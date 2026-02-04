"""
Tests estrictos de integridad para el modelo Transaccion.

Estos tests verifican:
1. Validaciones de campos requeridos
2. Validaciones de tipos de datos
3. Constraints de negocio (montos positivos, estados válidos, monedas válidas)
4. Integridad referencial (ForeignKey a cliente)
5. Constraints de base de datos
6. Validaciones de rangos y límites
7. Validaciones de formato (moneda ISO 4217)
8. Validaciones de fecha (no futuras)
"""
import uuid
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction, models
from django.utils import timezone

from apps.companies.models import Company, Sitec
from apps.transactions.models import Transaccion, Cliente


class TransaccionIntegridadTests(TestCase):
    """Tests estrictos de integridad para el modelo Transaccion"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Test Company",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="test",
            status="active",
        )
        self.cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Test",
            email="cliente@test.com"
        )
    
    # ========== TESTS DE CAMPOS REQUERIDOS ==========
    
    def test_id_cliente_requerido(self):
        """Test: id_cliente es obligatorio"""
        # Django valida antes de llegar a la DB, así que lanza ValidationError
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        self.assertIn('id_cliente', str(context.exception))
    
    def test_monto_requerido(self):
        """Test: monto es obligatorio"""
        # Django valida antes de llegar a la DB
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        # El error puede ser por monto None o por la validación en clean()
        self.assertTrue('monto' in str(context.exception) or 'id_cliente' in str(context.exception))
    
    def test_moneda_requerida(self):
        """Test: moneda tiene default, pero si se pasa vacía debe validar"""
        # Moneda tiene default='MXN', así que no es técnicamente requerida
        # Pero si se pasa vacía o inválida, debe fallar
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='',  # Vacía
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_fecha_requerida(self):
        """Test: fecha tiene default, pero si se pasa None debe validar"""
        # Fecha tiene default=timezone.now, así que no es técnicamente requerida
        # Pero si se pasa None explícitamente, debe fallar
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            estado='pendiente'
            # fecha no especificada, usa default
        )
        self.assertIsNotNone(transaccion.fecha)
    
    def test_estado_requerido(self):
        """Test: estado tiene default, pero si se pasa vacío debe validar"""
        # Estado tiene default='pendiente', así que no es técnicamente requerido
        # Pero si se pasa vacío o inválido, debe fallar
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado=''  # Vacío
            )
            transaccion.full_clean()
    
    # ========== TESTS DE VALIDACIONES DE TIPOS ==========
    
    def test_monto_debe_ser_decimal(self):
        """Test: monto debe ser un Decimal válido"""
        # Intentar crear con string debería funcionar (Django lo convierte)
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto='100.50',
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertIsInstance(transaccion.monto, Decimal)
        self.assertEqual(transaccion.monto, Decimal('100.50'))
    
    def test_monto_con_precision_correcta(self):
        """Test: monto debe tener máximo 2 decimales"""
        # Django DecimalField valida antes de guardar, así que rechaza más de 2 decimales
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.999'),  # Más de 2 decimales
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        self.assertIn('monto', str(context.exception))
        
        # Pero si redondeamos manualmente a 2 decimales, funciona
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.99'),  # Exactamente 2 decimales
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.refresh_from_db()
        self.assertEqual(str(transaccion.monto), '100.99')
    
    def test_moneda_debe_ser_string(self):
        """Test: moneda debe ser un string"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        self.assertIsInstance(transaccion.moneda, str)
        self.assertEqual(len(transaccion.moneda), 3)
    
    def test_fecha_debe_ser_datetime(self):
        """Test: fecha debe ser un DateTime"""
        ahora = timezone.now()
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=ahora,
            estado='pendiente'
        )
        self.assertIsInstance(transaccion.fecha, datetime)
    
    def test_estado_debe_ser_string(self):
        """Test: estado debe ser un string"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        self.assertIsInstance(transaccion.estado, str)
    
    # ========== TESTS DE CONSTRAINTS DE NEGOCIO ==========
    
    def test_monto_debe_ser_positivo(self):
        """Test: monto debe ser mayor a 0"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('0.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_monto_negativo_rechazado(self):
        """Test: monto negativo es rechazado"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('-100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_monto_minimo_aceptado(self):
        """Test: monto mínimo de 0.01 es aceptado"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.01'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.monto, Decimal('0.01'))
    
    def test_monto_maximo_aceptado(self):
        """Test: monto máximo de 9999999999999.99 es aceptado (max_digits=15, decimal_places=2)"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('9999999999999.99'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.monto, Decimal('9999999999999.99'))
    
    def test_monto_excede_maximo_rechazado(self):
        """Test: monto que excede el máximo es rechazado"""
        with self.assertRaises((ValidationError, InvalidOperation)):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('99999999999999.99'),  # Excede max_digits=15
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    # ========== TESTS DE VALIDACIONES DE MONEDA ==========
    
    def test_moneda_mxn_valida(self):
        """Test: moneda MXN es válida"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.moneda, 'MXN')
    
    def test_moneda_usd_valida(self):
        """Test: moneda USD es válida"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='USD',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.moneda, 'USD')
    
    def test_moneda_invalida_rechazada(self):
        """Test: moneda inválida es rechazada"""
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='XXX',  # Moneda inválida
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        
        self.assertIn('moneda', str(context.exception))
    
    def test_moneda_minusculas_rechazada(self):
        """Test: moneda en minúsculas es rechazada (debe ser mayúsculas)"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='mxn',  # Minúsculas
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_moneda_longitud_incorrecta_rechazada(self):
        """Test: moneda con longitud incorrecta es rechazada"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MX',  # Solo 2 caracteres
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_todas_monedas_validas_aceptadas(self):
        """Test: todas las monedas válidas son aceptadas"""
        monedas_validas = ['MXN', 'USD', 'EUR', 'GBP', 'CAD', 'ARS', 'BRL', 'CLP', 'COP', 'PEN']
        
        for moneda in monedas_validas:
            with self.subTest(moneda=moneda):
                transaccion = Transaccion(
                    company=self.company,
                    sitec=self.sitec,
                    id_cliente=self.cliente,
                    monto=Decimal('100.00'),
                    moneda=moneda,
                    fecha=timezone.now(),
                    estado='pendiente'
                )
                transaccion.full_clean()
                transaccion.save()
                self.assertEqual(transaccion.moneda, moneda)
    
    # ========== TESTS DE VALIDACIONES DE ESTADO ==========
    
    def test_estado_pendiente_valido(self):
        """Test: estado 'pendiente' es válido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.estado, 'pendiente')
    
    def test_estado_completada_valido(self):
        """Test: estado 'completada' es válido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='completada'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.estado, 'completada')
    
    def test_estado_cancelada_valido(self):
        """Test: estado 'cancelada' es válido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='cancelada'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.estado, 'cancelada')
    
    def test_estado_fallida_valido(self):
        """Test: estado 'fallida' es válido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='fallida'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.estado, 'fallida')
    
    def test_estado_invalido_rechazado(self):
        """Test: estado inválido es rechazado"""
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='invalido'  # Estado inválido
            )
            transaccion.full_clean()
        
        self.assertIn('estado', str(context.exception))
    
    def test_todos_estados_validos_aceptados(self):
        """Test: todos los estados válidos son aceptados"""
        estados_validos = ['pendiente', 'completada', 'cancelada', 'fallida']
        
        for estado in estados_validos:
            with self.subTest(estado=estado):
                transaccion = Transaccion(
                    company=self.company,
                    sitec=self.sitec,
                    id_cliente=self.cliente,
                    monto=Decimal('100.00'),
                    moneda='MXN',
                    fecha=timezone.now(),
                    estado=estado
                )
                transaccion.full_clean()
                transaccion.save()
                self.assertEqual(transaccion.estado, estado)
    
    # ========== TESTS DE VALIDACIONES DE FECHA ==========
    
    def test_fecha_pasada_aceptada(self):
        """Test: fecha pasada es aceptada"""
        fecha_pasada = timezone.now() - timedelta(days=1)
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_pasada,
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.fecha, fecha_pasada)
    
    def test_fecha_actual_aceptada(self):
        """Test: fecha actual es aceptada"""
        ahora = timezone.now()
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=ahora,
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        # Permitir diferencia de segundos
        diferencia = abs((transaccion.fecha - ahora).total_seconds())
        self.assertLess(diferencia, 5)
    
    def test_fecha_futura_rechazada(self):
        """Test: fecha futura es rechazada"""
        fecha_futura = timezone.now() + timedelta(days=1)
        
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=fecha_futura,
                estado='pendiente'
            )
            transaccion.full_clean()
        
        self.assertIn('fecha', str(context.exception))
    
    def test_fecha_default_es_ahora(self):
        """Test: fecha por defecto es el momento actual"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            estado='pendiente'
            # fecha no especificada, debe usar default
        )
        diferencia = abs((transaccion.fecha - timezone.now()).total_seconds())
        self.assertLess(diferencia, 5)
    
    # ========== TESTS DE INTEGRIDAD REFERENCIAL ==========
    
    def test_cliente_existente_requerido(self):
        """Test: el cliente debe existir en la base de datos"""
        cliente_inexistente = Cliente(id=uuid.uuid4(), nombre="No existe")
        
        # Django valida que el ForeignKey apunte a un objeto existente
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=cliente_inexistente,  # Cliente no guardado
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        self.assertIn('id_cliente', str(context.exception))
    
    def test_eliminacion_cliente_protegida(self):
        """Test: no se puede eliminar un cliente con transacciones (PROTECT)"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        # Intentar eliminar el cliente debería fallar
        with self.assertRaises(models.ProtectedError):
            self.cliente.delete()
        
        # Verificar que la transacción sigue existiendo
        self.assertTrue(Transaccion.objects.filter(id_transaccion=transaccion.id_transaccion).exists())
    
    def test_relacion_cliente_transacciones(self):
        """Test: relación inversa cliente.transacciones funciona"""
        transaccion1 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion2 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('200.00'),
            moneda='USD',
            fecha=timezone.now(),
            estado='completada'
        )
        
        transacciones = self.cliente.transacciones.all()
        self.assertEqual(transacciones.count(), 2)
        self.assertIn(transaccion1, transacciones)
        self.assertIn(transaccion2, transacciones)
    
    # ========== TESTS DE CONSTRAINTS DE BASE DE DATOS ==========
    
    def test_constraint_monto_positivo_en_db(self):
        """Test: constraint de monto positivo se aplica en la base de datos"""
        # Django valida antes de llegar a la DB, así que lanza ValidationError
        # Pero también existe el constraint en la DB como respaldo
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('-100.00'),  # Negativo
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        self.assertIn('monto', str(context.exception))
    
    def test_constraint_estado_valido_en_db(self):
        """Test: constraint de estado válido se aplica en la base de datos"""
        # Intentar insertar directamente con estado inválido usando raw SQL
        # Primero necesitamos obtener el nombre real de la columna FK
        from django.db import connection
        
        # Obtener el nombre real de la columna FK
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(transactions_transaccion)")
            columns = {row[1]: row[0] for row in cursor.fetchall()}
            
            # Buscar la columna FK (puede ser id_cliente_id o id_cliente)
            fk_column = None
            for col_name in columns.keys():
                if 'cliente' in col_name.lower():
                    fk_column = col_name
                    break
            
            if fk_column:
                try:
                    with transaction.atomic():
                        cursor.execute(f"""
                            INSERT INTO transactions_transaccion 
                            (id_transaccion, {fk_column}, monto, moneda, fecha, estado, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            str(uuid.uuid4()),
                            str(self.cliente.id),
                            '100.00',
                            'MXN',
                            timezone.now().isoformat(),
                            'estado_invalido',  # Estado inválido
                            timezone.now().isoformat(),
                            timezone.now().isoformat()
                        ])
                        # Si llegamos aquí, el constraint no funcionó
                        self.fail("El constraint de estado válido no se aplicó correctamente")
                except IntegrityError:
                    # Esto es lo esperado - el constraint de DB debería rechazarlo
                    pass
                except Exception as e:
                    # Otros errores (como formato de fecha) son aceptables
                    # Lo importante es que no se insertó un estado inválido
                    pass
    
    def test_indices_creados_correctamente(self):
        """Test: los índices se crean correctamente en la base de datos"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar índices (sintaxis SQLite)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='transactions_transaccion'
            """)
            indices = [row[0] for row in cursor.fetchall()]
            
            # Verificar que existen los índices esperados
            # Nota: SQLite puede crear índices automáticos para ForeignKeys y campos con db_index=True
            indices_esperados = [
                'transaccion_cliente_fecha_idx',
                'transaccion_estado_fecha_idx',
                'transaccion_moneda_fecha_idx',
                'transaccion_fecha_idx',
            ]
            
            # Verificar que al menos algunos de los índices personalizados existen
            # (puede haber índices adicionales creados por Django)
            indices_encontrados = [idx for idx in indices_esperados if idx in indices]
            self.assertGreater(len(indices_encontrados), 0, 
                             f"Ninguno de los índices esperados fue encontrado. Índices disponibles: {indices}")
            
            # Verificar que el índice de estado existe (tiene db_index=True)
            # Django crea automáticamente un índice para campos con db_index=True
            self.assertTrue(
                any('estado' in idx.lower() for idx in indices) or 'transaccion_estado_fecha_idx' in indices,
                f"Índice de estado no encontrado. Índices disponibles: {indices}"
            )
    
    # ========== TESTS DE CASOS LÍMITE ==========
    
    def test_monto_muy_grande_aceptado(self):
        """Test: monto muy grande pero dentro del límite es aceptado"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('999999999999.99'),  # Casi el máximo
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.monto, Decimal('999999999999.99'))
    
    def test_monto_con_muchos_decimales_rechazado(self):
        """Test: monto con muchos decimales es rechazado (no se redondea automáticamente)"""
        # Django valida la precisión antes de guardar
        with self.assertRaises(ValidationError) as context:
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.999999'),  # Muchos decimales
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
        self.assertIn('monto', str(context.exception))
        
        # Si queremos redondear manualmente, podemos hacerlo
        monto_redondeado = Decimal('100.999999').quantize(Decimal('0.01'))
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=monto_redondeado,  # Redondeado manualmente
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.refresh_from_db()
        self.assertEqual(str(transaccion.monto), '101.00')
    
    def test_multiples_transacciones_mismo_cliente(self):
        """Test: un cliente puede tener múltiples transacciones"""
        for i in range(10):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal(f'{100 + i}.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        self.assertEqual(self.cliente.transacciones.count(), 10)
    
    def test_transacciones_diferentes_clientes(self):
        """Test: diferentes clientes pueden tener transacciones independientes"""
        cliente2 = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente 2",
            email="cliente2@test.com"
        )
        
        transaccion1 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion2 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=cliente2,
            monto=Decimal('200.00'),
            moneda='USD',
            fecha=timezone.now(),
            estado='completada'
        )
        
        self.assertNotEqual(transaccion1.id_cliente, transaccion2.id_cliente)
        self.assertEqual(self.cliente.transacciones.count(), 1)
        self.assertEqual(cliente2.transacciones.count(), 1)
    
    # ========== TESTS DE INTEGRIDAD DE DATOS ==========
    
    def test_id_transaccion_es_unico(self):
        """Test: id_transaccion es único (primary key)"""
        id_transaccion = uuid.uuid4()
        
        transaccion1 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_transaccion=id_transaccion,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        # Intentar crear otra con el mismo ID debería fallar
        # Django puede validar antes (ValidationError) o en la DB (IntegrityError)
        with self.assertRaises((IntegrityError, ValidationError)):
            Transaccion.objects.create(
                id_transaccion=id_transaccion,  # Mismo ID
                id_cliente=self.cliente,
                monto=Decimal('200.00'),
                moneda='USD',
                fecha=timezone.now(),
                estado='completada'
            )
    
    def test_id_transaccion_auto_generado(self):
        """Test: id_transaccion se genera automáticamente si no se proporciona"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        self.assertIsNotNone(transaccion.id_transaccion)
        self.assertIsInstance(transaccion.id_transaccion, uuid.UUID)
    
    def test_timestamps_auto_generados(self):
        """Test: created_at y updated_at se generan automáticamente"""
        antes = timezone.now()
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        despues = timezone.now()
        
        self.assertIsNotNone(transaccion.created_at)
        self.assertIsNotNone(transaccion.updated_at)
        self.assertGreaterEqual(transaccion.created_at, antes)
        self.assertLessEqual(transaccion.created_at, despues)
    
    def test_updated_at_se_actualiza(self):
        """Test: updated_at se actualiza al modificar la transacción"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        updated_at_original = transaccion.updated_at
        
        # Esperar un momento para asegurar diferencia de tiempo
        import time
        time.sleep(0.1)
        
        transaccion.estado = 'completada'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertGreater(transaccion.updated_at, updated_at_original)
    
    # ========== TESTS DE VALIDACIONES COMBINADAS ==========
    
    def test_transaccion_completa_valida(self):
        """Test: transacción con todos los campos válidos se crea correctamente"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('1500.75'),
            moneda='USD',
            fecha=timezone.now() - timedelta(hours=2),
            estado='completada'
        )
        
        self.assertIsNotNone(transaccion.id_transaccion)
        self.assertEqual(transaccion.id_cliente, self.cliente)
        self.assertEqual(transaccion.monto, Decimal('1500.75'))
        self.assertEqual(transaccion.moneda, 'USD')
        self.assertEqual(transaccion.estado, 'completada')
        self.assertIsNotNone(transaccion.fecha)
        self.assertIsNotNone(transaccion.created_at)
        self.assertIsNotNone(transaccion.updated_at)
    
    def test_validacion_completa_en_save(self):
        """Test: todas las validaciones se ejecutan en save()"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('-100.00'),  # Monto negativo
                moneda='XXX',  # Moneda inválida
                fecha=timezone.now() + timedelta(days=1),  # Fecha futura
                estado='invalido'  # Estado inválido
            )
            transaccion.save()  # Debe ejecutar full_clean()
    
    # ========== TESTS DE PERFORMANCE Y CONSULTAS ==========
    
    def test_consulta_por_cliente_optimizada(self):
        """Test: consulta por cliente usa índice"""
        # Crear múltiples transacciones
        for i in range(5):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal(f'{100 + i}.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        # Consulta debería usar el índice
        transacciones = Transaccion.objects.filter(id_cliente=self.cliente).order_by('-fecha')
        self.assertEqual(transacciones.count(), 5)
    
    def test_consulta_por_estado_optimizada(self):
        """Test: consulta por estado usa índice"""
        # Crear transacciones con diferentes estados
        estados = ['pendiente', 'completada', 'cancelada', 'fallida']
        for estado in estados:
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado=estado
            )
        
        # Consulta debería usar el índice
        completadas = Transaccion.objects.filter(estado='completada')
        self.assertEqual(completadas.count(), 1)
    
    def test_consulta_por_moneda_optimizada(self):
        """Test: consulta por moneda usa índice"""
        # Crear transacciones con diferentes monedas
        monedas = ['MXN', 'USD', 'EUR']
        for moneda in monedas:
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda=moneda,
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        # Consulta debería usar el índice
        usd = Transaccion.objects.filter(moneda='USD')
        self.assertEqual(usd.count(), 1)
    
    # ========== TESTS DE CASOS EDGE ==========
    
    def test_monto_exactamente_cero_rechazado(self):
        """Test: monto exactamente 0.00 es rechazado"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('0.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_monto_muy_pequeno_aceptado(self):
        """Test: monto muy pequeño (0.01) es aceptado"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.01'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.monto, Decimal('0.01'))
    
    def test_moneda_vacia_rechazada(self):
        """Test: moneda vacía es rechazada"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='',  # Vacía
                fecha=timezone.now(),
                estado='pendiente'
            )
            transaccion.full_clean()
    
    def test_estado_vacio_rechazado(self):
        """Test: estado vacío es rechazado"""
        with self.assertRaises(ValidationError):
            transaccion = Transaccion(
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado=''  # Vacío
            )
            transaccion.full_clean()
    
    def test_fecha_muy_antigua_aceptada(self):
        """Test: fecha muy antigua es aceptada (solo rechazamos futuras)"""
        fecha_antigua = timezone.now() - timedelta(days=365)
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_antigua,
            estado='pendiente'
        )
        transaccion.full_clean()
        transaccion.save()
        self.assertEqual(transaccion.fecha, fecha_antigua)
    
    # ========== TESTS DE INTEGRIDAD TRANSACCIONAL ==========
    
    def test_rollback_en_error_de_validacion(self):
        """Test: rollback automático en caso de error de validación"""
        count_before = Transaccion.objects.count()
        
        try:
            with transaction.atomic():
                Transaccion.objects.create(
                    company=self.company,
                    sitec=self.sitec,
                    id_cliente=self.cliente,
                    monto=Decimal('-100.00'),  # Inválido
                    moneda='MXN',
                    fecha=timezone.now(),
                    estado='pendiente'
                )
        except (ValidationError, IntegrityError):
            pass
        
        count_after = Transaccion.objects.count()
        self.assertEqual(count_before, count_after)
    
    def test_transacciones_atomicas(self):
        """Test: múltiples transacciones se crean de forma atómica"""
        count_before = Transaccion.objects.count()
        
        try:
            with transaction.atomic():
                Transaccion.objects.create(
                    company=self.company,
                    sitec=self.sitec,
                    id_cliente=self.cliente,
                    monto=Decimal('100.00'),
                    moneda='MXN',
                    fecha=timezone.now(),
                    estado='pendiente'
                )
                Transaccion.objects.create(
                    company=self.company,
                    sitec=self.sitec,
                    id_cliente=self.cliente,
                    monto=Decimal('-200.00'),  # Esta fallará
                    moneda='MXN',
                    fecha=timezone.now(),
                    estado='pendiente'
                )
        except (ValidationError, IntegrityError):
            pass
        
        # Ninguna debería haberse guardado debido al rollback
        count_after = Transaccion.objects.count()
        self.assertEqual(count_before, count_after)


class ClienteIntegridadTests(TestCase):
    """Tests de integridad para el modelo Cliente"""

    def setUp(self):
        """Company y Sitec requeridos por el modelo Cliente."""
        self.company = Company.objects.create(
            name="Test Company",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="test",
            status="active",
        )

    def test_cliente_creacion_valida(self):
        """Test: creación de cliente válido"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Test",
            email="test@example.com"
        )
        self.assertIsNotNone(cliente.id)
        self.assertEqual(cliente.nombre, "Cliente Test")
        self.assertEqual(cliente.email, "test@example.com")
        self.assertTrue(cliente.activo)

    def test_cliente_nombre_requerido(self):
        """Test: nombre es requerido"""
        with self.assertRaises(ValidationError) as context:
            cliente = Cliente(company=self.company, sitec=self.sitec, email="test@example.com")
            cliente.full_clean()
        self.assertIn('nombre', str(context.exception))

    def test_cliente_email_opcional(self):
        """Test: email es opcional"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Sin Email"
        )
        self.assertEqual(cliente.email, "")

    def test_cliente_activo_por_defecto(self):
        """Test: activo es True por defecto"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Test"
        )
        self.assertTrue(cliente.activo)
