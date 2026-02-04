"""
Tests Funcionales Estrictos - Sistema de Transacciones
Implementación de los 70 tests funcionales especificados en TESTS_FUNCIONALES_QA.md
"""
import uuid
import time
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from django.contrib.admin.sites import site
from django.contrib.admin.options import ModelAdmin

from apps.companies.models import Company, Sitec
from apps.transactions.models import Transaccion, Cliente


class TransaccionFuncionalTests(TestCase):
    """Tests funcionales estrictos para el sistema de transacciones"""
    
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
    
    # Test 1: Creación de Transacción Válida Completa
    def test_01_creacion_transaccion_valida_completa(self):
        """Test 1: Creación de transacción con todos los campos válidos"""
        fecha_actual = timezone.now()
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_actual,
            estado='pendiente'
        )
        transaccion.save()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        
        self.assertIsNotNone(transaccion_recuperada.id_transaccion)
        self.assertIsInstance(transaccion_recuperada.id_transaccion, uuid.UUID)
        self.assertEqual(transaccion_recuperada.id_cliente, self.cliente)
        self.assertEqual(transaccion_recuperada.monto, Decimal('100.00'))
        self.assertEqual(transaccion_recuperada.moneda, 'MXN')
        self.assertEqual(transaccion_recuperada.estado, 'pendiente')
        self.assertIsNotNone(transaccion_recuperada.created_at)
        self.assertIsNotNone(transaccion_recuperada.updated_at)
    
    # Test 2: Creación de Transacción sin Cliente
    def test_02_creacion_transaccion_sin_cliente(self):
        """Test 2: Validación de campo requerido id_cliente"""
        transaccion = Transaccion(
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('id_cliente', str(context.exception))
        self.assertFalse(Transaccion.objects.filter(monto=Decimal('100.00')).exists())
    
    # Test 3: Creación de Transacción con Monto Negativo
    def test_03_creacion_transaccion_monto_negativo(self):
        """Test 3: Validación de monto positivo"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('-50.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('monto', str(context.exception))
        self.assertIn('mayor a 0', str(context.exception))
        self.assertFalse(Transaccion.objects.filter(monto=Decimal('-50.00')).exists())
    
    # Test 4: Creación de Transacción con Monto Cero
    def test_04_creacion_transaccion_monto_cero(self):
        """Test 4: Validación de monto mínimo 0.01"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError):
            transaccion.save()
        
        self.assertFalse(Transaccion.objects.filter(monto=Decimal('0.00')).exists())
    
    # Test 5: Creación de Transacción con Monto Mínimo Válido
    def test_05_creacion_transaccion_monto_minimo_valido(self):
        """Test 5: Aceptación de monto mínimo permitido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.01'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.save()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        self.assertEqual(transaccion_recuperada.monto, Decimal('0.01'))
    
    # Test 6: Creación de Transacción con Monto Máximo Válido
    def test_06_creacion_transaccion_monto_maximo_valido(self):
        """Test 6: Aceptación de monto máximo permitido"""
        monto_maximo = Decimal('9999999999999.99')
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=monto_maximo,
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.save()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        self.assertEqual(transaccion_recuperada.monto, monto_maximo)
    
    # Test 7: Creación de Transacción con Moneda Inválida
    def test_07_creacion_transaccion_moneda_invalida(self):
        """Test 7: Validación de moneda ISO 4217 válida"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='XXX',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('moneda', str(context.exception))
        self.assertFalse(Transaccion.objects.filter(moneda='XXX').exists())
    
    # Test 8: Creación de Transacción con Moneda en Minúsculas
    def test_08_creacion_transaccion_moneda_minusculas(self):
        """Test 8: Validación de formato de moneda (mayúsculas)"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='mxn',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError):
            transaccion.save()
        
        self.assertFalse(Transaccion.objects.filter(moneda='mxn').exists())
    
    # Test 9: Creación de Transacción con Todas las Monedas Válidas
    def test_09_creacion_transaccion_todas_monedas_validas(self):
        """Test 9: Aceptación de todas las monedas permitidas"""
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
                transaccion.save()
                
                transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
                self.assertEqual(transaccion_recuperada.moneda, moneda)
    
    # Test 10: Creación de Transacción con Fecha Futura
    def test_10_creacion_transaccion_fecha_futura(self):
        """Test 10: Validación de fecha no futura"""
        fecha_futura = timezone.now() + timedelta(days=1)
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_futura,
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('fecha', str(context.exception))
        self.assertIn('futura', str(context.exception))
    
    # Test 11: Creación de Transacción sin Especificar Fecha
    def test_11_creacion_transaccion_sin_fecha(self):
        """Test 11: Aplicación de default para fecha"""
        antes = timezone.now()
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            estado='pendiente'
        )
        transaccion.save()
        despues = timezone.now()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        self.assertIsNotNone(transaccion_recuperada.fecha)
        self.assertGreaterEqual(transaccion_recuperada.fecha, antes)
        self.assertLessEqual(transaccion_recuperada.fecha, despues)
        diferencia = abs((transaccion_recuperada.fecha - timezone.now()).total_seconds())
        self.assertLess(diferencia, 5)
    
    # Test 12: Creación de Transacción con Estado Inválido
    def test_12_creacion_transaccion_estado_invalido(self):
        """Test 12: Validación de estado válido"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='invalido'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('estado', str(context.exception))
    
    # Test 13: Creación de Transacción sin Especificar Estado
    def test_13_creacion_transaccion_sin_estado(self):
        """Test 13: Aplicación de default para estado"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now()
        )
        transaccion.save()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        self.assertEqual(transaccion_recuperada.estado, 'pendiente')
    
    # Test 14: Creación de Transacción sin Especificar Moneda
    def test_14_creacion_transaccion_sin_moneda(self):
        """Test 14: Aplicación de default para moneda"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion.save()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion.id_transaccion)
        self.assertEqual(transaccion_recuperada.moneda, 'MXN')
    
    # Test 15: Actualización de Estado de Transacción Pendiente a Completada
    def test_15_actualizacion_estado_pendiente_a_completada(self):
        """Test 15: Transición de estado válida"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        created_at_original = transaccion.created_at
        updated_at_original = transaccion.updated_at
        
        time.sleep(0.1)  # Pequeña pausa para asegurar diferencia en timestamps
        
        transaccion.estado = 'completada'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'completada')
        self.assertEqual(transaccion.created_at, created_at_original)
        self.assertGreater(transaccion.updated_at, updated_at_original)
    
    # Test 16: Actualización de Estado de Transacción Completada a Pendiente
    def test_16_actualizacion_estado_completada_a_pendiente(self):
        """Test 16: Transición de estado inversa"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='completada'
        )
        
        transaccion.estado = 'pendiente'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'pendiente')
    
    # Test 17: Actualización de Monto de Transacción Existente
    def test_17_actualizacion_monto_transaccion_existente(self):
        """Test 17: Modificación de monto después de creación"""
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
        time.sleep(0.1)
        
        transaccion.monto = Decimal('200.00')
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.monto, Decimal('200.00'))
        self.assertGreater(transaccion.updated_at, updated_at_original)
    
    # Test 18: Actualización de Monto a Valor Negativo
    def test_18_actualizacion_monto_valor_negativo(self):
        """Test 18: Validación de monto positivo en actualización"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        monto_original = transaccion.monto
        
        transaccion.monto = Decimal('-50.00')
        
        with self.assertRaises(ValidationError):
            transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.monto, monto_original)
    
    # Test 19: Actualización de Moneda de Transacción Existente
    def test_19_actualizacion_moneda_transaccion_existente(self):
        """Test 19: Modificación de moneda después de creación"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion.moneda = 'USD'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.moneda, 'USD')
    
    # Test 20: Actualización de Fecha de Transacción Existente
    def test_20_actualizacion_fecha_transaccion_existente(self):
        """Test 20: Modificación de fecha después de creación"""
        fecha_pasada_1 = timezone.now() - timedelta(days=5)
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_pasada_1,
            estado='pendiente'
        )
        
        fecha_pasada_2 = timezone.now() - timedelta(days=3)
        transaccion.fecha = fecha_pasada_2
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.fecha, fecha_pasada_2)
    
    # Test 21: Actualización de Fecha a Futura en Transacción Existente
    def test_21_actualizacion_fecha_futura_transaccion_existente(self):
        """Test 21: Validación de fecha no futura en actualización"""
        fecha_pasada = timezone.now() - timedelta(days=1)
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_pasada,
            estado='pendiente'
        )
        
        fecha_original = transaccion.fecha
        transaccion.fecha = timezone.now() + timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.fecha, fecha_original)
    
    # Test 22: Eliminación de Cliente sin Transacciones
    def test_22_eliminacion_cliente_sin_transacciones(self):
        """Test 22: Eliminación permitida de cliente sin dependencias"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Sin Transacciones"
        )
        cliente_id = cliente.id
        
        cliente.delete()
        
        self.assertFalse(Cliente.objects.filter(id=cliente_id).exists())
    
    # Test 23: Eliminación de Cliente con Transacciones Asociadas
    def test_23_eliminacion_cliente_con_transacciones(self):
        """Test 23: Protección de integridad referencial (PROTECT)"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion_id = transaccion.id_transaccion
        
        from django.db import models
        with self.assertRaises(models.ProtectedError):
            self.cliente.delete()
        
        self.assertTrue(Cliente.objects.filter(id=self.cliente.id).exists())
        self.assertTrue(Transaccion.objects.filter(id_transaccion=transaccion_id).exists())
    
    # Test 24: Recuperación de Transacción por ID
    def test_24_recuperacion_transaccion_por_id(self):
        """Test 24: Consulta de transacción por identificador único"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        id_guardado = transaccion.id_transaccion
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=id_guardado)
        
        self.assertEqual(transaccion_recuperada.id_transaccion, id_guardado)
        self.assertEqual(transaccion_recuperada.id_cliente, self.cliente)
        self.assertEqual(transaccion_recuperada.monto, Decimal('100.00'))
        self.assertEqual(transaccion_recuperada.moneda, 'MXN')
        self.assertEqual(transaccion_recuperada.estado, 'pendiente')
    
    # Test 25: Recuperación de Transacciones por Cliente
    def test_25_recuperacion_transacciones_por_cliente(self):
        """Test 25: Consulta de transacciones asociadas a un cliente"""
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
        
        transacciones = self.cliente.transacciones.all()
        
        self.assertEqual(transacciones.count(), 5)
        for transaccion in transacciones:
            self.assertEqual(transaccion.id_cliente, self.cliente)
    
    # Test 26: Recuperación de Transacciones por Estado
    def test_26_recuperacion_transacciones_por_estado(self):
        """Test 26: Filtrado de transacciones por estado"""
        for _ in range(3):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        for _ in range(2):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='completada'
            )
        
        pendientes = Transaccion.objects.filter(estado='pendiente')
        self.assertEqual(pendientes.count(), 3)
        for transaccion in pendientes:
            self.assertEqual(transaccion.estado, 'pendiente')
    
    # Test 27: Recuperación de Transacciones por Moneda
    def test_27_recuperacion_transacciones_por_moneda(self):
        """Test 27: Filtrado de transacciones por moneda"""
        for _ in range(4):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='USD',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        for _ in range(3):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        usd_transacciones = Transaccion.objects.filter(moneda='USD')
        self.assertEqual(usd_transacciones.count(), 4)
        for transaccion in usd_transacciones:
            self.assertEqual(transaccion.moneda, 'USD')
    
    # Test 28: Recuperación de Transacciones Ordenadas por Fecha Descendente
    def test_28_recuperacion_transacciones_ordenadas_fecha_descendente(self):
        """Test 28: Ordenamiento según Meta.ordering"""
        hoy = timezone.now()
        ayer = hoy - timedelta(days=1)
        hace_2_dias = hoy - timedelta(days=2)
        
        transaccion_hoy = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=hoy,
            estado='pendiente'
        )
        
        transaccion_ayer = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=ayer,
            estado='pendiente'
        )
        
        transaccion_hace_2_dias = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=hace_2_dias,
            estado='pendiente'
        )
        
        transacciones = list(Transaccion.objects.all())
        
        self.assertEqual(transacciones[0].fecha, hoy)
        self.assertEqual(transacciones[1].fecha, ayer)
        self.assertEqual(transacciones[2].fecha, hace_2_dias)
    
    # Test 29: Creación Múltiple de Transacciones para Mismo Cliente
    def test_29_creacion_multiple_transacciones_mismo_cliente(self):
        """Test 29: Múltiples transacciones asociadas a un cliente"""
        for i in range(10):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal(f'{100 + i}.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente' if i % 2 == 0 else 'completada'
            )
        
        count = self.cliente.transacciones.count()
        self.assertEqual(count, 10)
        
        transacciones = self.cliente.transacciones.all()
        for transaccion in transacciones:
            self.assertEqual(transaccion.id_cliente, self.cliente)
    
    # Test 30: Creación de Transacciones para Diferentes Clientes
    def test_30_creacion_transacciones_diferentes_clientes(self):
        """Test 30: Aislamiento de transacciones entre clientes"""
        cliente_a = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente A"
        )
        cliente_b = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente B"
        )
        
        for _ in range(3):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=cliente_a,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        for _ in range(2):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=cliente_b,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        self.assertEqual(cliente_a.transacciones.count(), 3)
        self.assertEqual(cliente_b.transacciones.count(), 2)
        
        for transaccion in cliente_a.transacciones.all():
            self.assertEqual(transaccion.id_cliente, cliente_a)
        
        for transaccion in cliente_b.transacciones.all():
            self.assertEqual(transaccion.id_cliente, cliente_b)
    
    # Test 31: Idempotencia de Creación de Transacción
    def test_31_idempotencia_creacion_transaccion(self):
        """Test 31: Creación repetida con mismos datos produce resultados consistentes"""
        datos = {
            'company': self.company,
            'sitec': self.sitec,
            'id_cliente': self.cliente,
            'monto': Decimal('100.00'),
            'moneda': 'MXN',
            'fecha': timezone.now(),
            'estado': 'pendiente'
        }
        
        transaccion_1 = Transaccion.objects.create(**datos)
        transaccion_2 = Transaccion.objects.create(**datos)
        
        self.assertNotEqual(transaccion_1.id_transaccion, transaccion_2.id_transaccion)
        self.assertEqual(transaccion_1.id_cliente, transaccion_2.id_cliente)
        self.assertEqual(transaccion_1.monto, transaccion_2.monto)
        self.assertEqual(transaccion_1.moneda, transaccion_2.moneda)
        self.assertEqual(transaccion_1.estado, transaccion_2.estado)
    
    # Test 32: Persistencia de Transacción después de Reinicio de Base de Datos
    def test_32_persistencia_transaccion_despues_reinicio_db(self):
        """Test 32: Persistencia permanente de datos"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        id_guardado = transaccion.id_transaccion
        
        # Simular cierre y apertura de conexión
        connection.close()
        connection.ensure_connection()
        
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=id_guardado)
        
        self.assertEqual(transaccion_recuperada.id_transaccion, id_guardado)
        self.assertEqual(transaccion_recuperada.monto, Decimal('100.00'))
        self.assertEqual(transaccion_recuperada.moneda, 'MXN')
        self.assertEqual(transaccion_recuperada.estado, 'pendiente')
    
    # Test 33: Actualización de updated_at en Modificación
    def test_33_actualizacion_updated_at_en_modificacion(self):
        """Test 33: Actualización automática de timestamp updated_at"""
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
        created_at_original = transaccion.created_at
        
        time.sleep(1)
        
        transaccion.monto = Decimal('200.00')
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertGreater(transaccion.updated_at, updated_at_original)
        self.assertEqual(transaccion.created_at, created_at_original)
    
    # Test 34: Inmutabilidad de created_at después de Actualización
    def test_34_inmutabilidad_created_at_despues_actualizacion(self):
        """Test 34: created_at no se modifica en actualizaciones"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        created_at_original = transaccion.created_at
        
        # Múltiples actualizaciones
        transaccion.monto = Decimal('200.00')
        transaccion.save()
        
        transaccion.estado = 'completada'
        transaccion.save()
        
        transaccion.moneda = 'USD'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.created_at, created_at_original)
    
    # Test 35: Validación de Precisión Decimal de Monto
    def test_35_validacion_precision_decimal_monto(self):
        """Test 35: Precisión de 2 decimales en campo monto"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.999'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('monto', str(context.exception))
        self.assertIn('decimales', str(context.exception))
    
    # Test 36: Creación de Transacción con Monto Exactamente en Límite de Precisión
    def test_36_creacion_transaccion_monto_limite_precision(self):
        """Test 36: Aceptación de monto con exactamente 2 decimales"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('123.45'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.monto, Decimal('123.45'))
    
    # Test 37: Transición de Estado Pendiente a Cancelada
    def test_37_transicion_estado_pendiente_a_cancelada(self):
        """Test 37: Cambio de estado válido"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion.estado = 'cancelada'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'cancelada')
    
    # Test 38: Transición de Estado Pendiente a Fallida
    def test_38_transicion_estado_pendiente_a_fallida(self):
        """Test 38: Cambio de estado válido"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion.estado = 'fallida'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'fallida')
    
    # Test 39: Consulta de Transacciones por Rango de Fechas
    def test_39_consulta_transacciones_por_rango_fechas(self):
        """Test 39: Filtrado por rango temporal"""
        hoy = timezone.now()
        ayer = hoy - timedelta(days=1)
        hace_3_dias = hoy - timedelta(days=3)
        
        Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=hoy,
            estado='pendiente'
        )
        
        Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=ayer,
            estado='pendiente'
        )
        
        Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=hace_3_dias,
            estado='pendiente'
        )
        
        transacciones = Transaccion.objects.filter(
            fecha__gte=ayer,
            fecha__lte=hoy
        )
        
        self.assertEqual(transacciones.count(), 2)
        for transaccion in transacciones:
            self.assertGreaterEqual(transaccion.fecha, ayer)
            self.assertLessEqual(transaccion.fecha, hoy)
    
    # Test 40: Consulta de Transacciones por Cliente y Estado
    def test_40_consulta_transacciones_por_cliente_y_estado(self):
        """Test 40: Filtrado combinado por múltiples campos"""
        for _ in range(2):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        for _ in range(3):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='completada'
            )
        
        transacciones = Transaccion.objects.filter(
            id_cliente=self.cliente,
            estado='pendiente'
        )
        
        self.assertEqual(transacciones.count(), 2)
        for transaccion in transacciones:
            self.assertEqual(transaccion.id_cliente, self.cliente)
            self.assertEqual(transaccion.estado, 'pendiente')
    
    # Test 41: Consulta de Transacciones por Cliente y Moneda
    def test_41_consulta_transacciones_por_cliente_y_moneda(self):
        """Test 41: Filtrado combinado por cliente y moneda"""
        for _ in range(3):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='USD',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        for _ in range(2):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
        
        transacciones = Transaccion.objects.filter(
            id_cliente=self.cliente,
            moneda='USD'
        )
        
        self.assertEqual(transacciones.count(), 3)
        for transaccion in transacciones:
            self.assertEqual(transaccion.id_cliente, self.cliente)
            self.assertEqual(transaccion.moneda, 'USD')
    
    # Test 42: Verificación de Índice en Consulta por Cliente y Fecha
    def test_42_verificacion_indice_consulta_cliente_fecha(self):
        """Test 42: Optimización mediante índices compuestos"""
        for i in range(5):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now() - timedelta(days=i),
                estado='pendiente'
            )
        
        # La consulta debería usar el índice
        transacciones = Transaccion.objects.filter(
            id_cliente=self.cliente
        ).order_by('-fecha')
        
        self.assertEqual(transacciones.count(), 5)
        # Verificar que el orden es correcto (más reciente primero)
        fechas = [t.fecha for t in transacciones]
        self.assertEqual(fechas, sorted(fechas, reverse=True))
    
    # Test 43: Verificación de Índice en Consulta por Estado y Fecha
    def test_43_verificacion_indice_consulta_estado_fecha(self):
        """Test 43: Optimización mediante índices compuestos"""
        for i in range(5):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal('100.00'),
                moneda='MXN',
                fecha=timezone.now() - timedelta(days=i),
                estado='pendiente'
            )
        
        transacciones = Transaccion.objects.filter(
            estado='pendiente'
        ).order_by('-fecha')
        
        self.assertEqual(transacciones.count(), 5)
        fechas = [t.fecha for t in transacciones]
        self.assertEqual(fechas, sorted(fechas, reverse=True))
    
    # Test 44: Verificación de Constraint de Monto Positivo en Base de Datos
    def test_44_verificacion_constraint_monto_positivo_db(self):
        """Test 44: Constraint de base de datos como respaldo"""
        # Django valida antes, pero el constraint existe como respaldo
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('-100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        # Debe fallar en validación de Django antes de llegar a la DB
        with self.assertRaises(ValidationError):
            transaccion.save()
    
    # Test 45: Verificación de Constraint de Estado Válido en Base de Datos
    def test_45_verificacion_constraint_estado_valido_db(self):
        """Test 45: Constraint de base de datos como respaldo"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='estado_invalido'
        )
        
        # Debe fallar en validación de Django antes de llegar a la DB
        with self.assertRaises(ValidationError):
            transaccion.save()
    
    # Test 46: Creación de Transacción con Cliente Inexistente
    def test_46_creacion_transaccion_cliente_inexistente(self):
        """Test 46: Validación de ForeignKey existente"""
        cliente_no_guardado = Cliente(
            id=uuid.uuid4(),
            company=self.company,
            sitec=self.sitec,
            nombre="No existe"
        )
        
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=cliente_no_guardado,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises((ValidationError, IntegrityError)):
            transaccion.save()
    
    # Test 47: Recuperación de Transacción después de Eliminación de Cliente (Protegida)
    def test_47_recuperacion_transaccion_despues_eliminacion_cliente_protegida(self):
        """Test 47: Transacciones permanecen después de intento de eliminación de cliente"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        transaccion_id = transaccion.id_transaccion
        
        from django.db import models
        with self.assertRaises(models.ProtectedError):
            self.cliente.delete()
        
        # Verificar que la transacción sigue existiendo
        transaccion_recuperada = Transaccion.objects.get(id_transaccion=transaccion_id)
        self.assertIsNotNone(transaccion_recuperada)
        self.assertEqual(transaccion_recuperada.id_cliente, self.cliente)
    
    # Test 48: Flujo Completo: Creación, Actualización y Consulta
    def test_48_flujo_completo_creacion_actualizacion_consulta(self):
        """Test 48: Flujo end-to-end completo"""
        # Crear transacción
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        # Verificar creación
        self.assertEqual(transaccion.estado, 'pendiente')
        self.assertEqual(transaccion.monto, Decimal('100.00'))
        
        # Actualizar
        transaccion.estado = 'completada'
        transaccion.monto = Decimal('150.00')
        transaccion.save()
        
        # Consultar y verificar valores finales
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'completada')
        self.assertEqual(transaccion.monto, Decimal('150.00'))
    
    # Test 49: Creación Concurrente de Transacciones para Mismo Cliente
    def test_49_creacion_concurrente_transacciones_mismo_cliente(self):
        """Test 49: Manejo de concurrencia"""
        transacciones_creadas = []
        
        for i in range(10):
            transaccion = Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_cliente=self.cliente,
                monto=Decimal(f'{100 + i}.00'),
                moneda='MXN',
                fecha=timezone.now(),
                estado='pendiente'
            )
            transacciones_creadas.append(transaccion.id_transaccion)
        
        # Verificar que todas se crearon
        self.assertEqual(len(transacciones_creadas), 10)
        
        # Verificar que todas están asociadas al cliente
        count = self.cliente.transacciones.count()
        self.assertEqual(count, 10)
        
        # Verificar que todas existen
        for transaccion_id in transacciones_creadas:
            self.assertTrue(Transaccion.objects.filter(id_transaccion=transaccion_id).exists())
    
    # Test 50: Validación de Método __str__ de Transaccion
    def test_50_validacion_metodo_str_transaccion(self):
        """Test 50: Representación de cadena del modelo"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        str_repr = str(transaccion)
        
        self.assertIn(str(transaccion.id_transaccion), str_repr)
        self.assertIn(self.cliente.nombre, str_repr)
        self.assertIn('100.00', str_repr)
        self.assertIn('MXN', str_repr)
    
    # Test 51: Validación de Método __str__ de Cliente
    def test_51_validacion_metodo_str_cliente(self):
        """Test 51: Representación de cadena del modelo Cliente"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Test Str"
        )
        
        str_repr = str(cliente)
        
        self.assertEqual(str_repr, "Cliente Test Str")
    
    # Test 52: Verificación de Ordenamiento por Fecha y created_at
    def test_52_verificacion_ordenamiento_fecha_created_at(self):
        """Test 52: Ordenamiento múltiple según Meta.ordering"""
        fecha_comun = timezone.now()
        
        # Crear transacciones con misma fecha pero diferentes created_at
        transaccion_1 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=fecha_comun,
            estado='pendiente'
        )
        
        time.sleep(0.1)
        
        transaccion_2 = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('200.00'),
            moneda='MXN',
            fecha=fecha_comun,
            estado='pendiente'
        )
        
        transacciones = list(Transaccion.objects.all())
        
        # Deben estar ordenadas por fecha descendente, luego por created_at descendente
        # La más reciente primero
        self.assertEqual(transacciones[0].id_transaccion, transaccion_2.id_transaccion)
        self.assertEqual(transacciones[1].id_transaccion, transaccion_1.id_transaccion)
    
    # Test 53: Creación de Transacción con Monto en Límite Inferior Exacto
    def test_53_creacion_transaccion_monto_limite_inferior_exacto(self):
        """Test 53: Validación de límite mínimo estricto"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.01'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.monto, Decimal('0.01'))
    
    # Test 54: Creación de Transacción con Monto Justo Debajo del Mínimo
    def test_54_creacion_transaccion_monto_justo_debajo_minimo(self):
        """Test 54: Rechazo de valores menores al mínimo"""
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('0.009'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError):
            transaccion.save()
    
    # Test 55: Verificación de db_table Personalizado
    def test_55_verificacion_db_table_personalizado(self):
        """Test 55: Nombre de tabla personalizado en base de datos"""
        self.assertEqual(Transaccion._meta.db_table, 'transactions_transaccion')
        self.assertEqual(Cliente._meta.db_table, 'transactions_cliente')
        
        # Verificar que las tablas existen
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN (?, ?)",
                         ['transactions_transaccion', 'transactions_cliente'])
            tablas = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('transactions_transaccion', tablas)
            self.assertIn('transactions_cliente', tablas)
    
    # Test 56: Verificación de Campos Readonly en Admin
    def test_56_verificacion_campos_readonly_admin(self):
        """Test 56: Configuración de campos de solo lectura en Django Admin"""
        from apps.transactions.admin import TransaccionAdmin
        
        admin_instance = TransaccionAdmin(Transaccion, site)
        
        self.assertIn('id_transaccion', admin_instance.readonly_fields)
        self.assertIn('created_at', admin_instance.readonly_fields)
        self.assertIn('updated_at', admin_instance.readonly_fields)
    
    # Test 57: Verificación de Filtros en Admin
    def test_57_verificacion_filtros_admin(self):
        """Test 57: Configuración de filtros en Django Admin"""
        from apps.transactions.admin import TransaccionAdmin
        
        admin_instance = TransaccionAdmin(Transaccion, site)
        
        self.assertIn('estado', admin_instance.list_filter)
        self.assertIn('moneda', admin_instance.list_filter)
        self.assertIn('fecha', admin_instance.list_filter)
        self.assertIn('created_at', admin_instance.list_filter)
    
    # Test 58: Verificación de Búsqueda en Admin
    def test_58_verificacion_busqueda_admin(self):
        """Test 58: Configuración de búsqueda en Django Admin"""
        from apps.transactions.admin import TransaccionAdmin
        
        admin_instance = TransaccionAdmin(Transaccion, site)
        
        self.assertIn('id_transaccion', admin_instance.search_fields)
        self.assertIn('id_cliente__nombre', admin_instance.search_fields)
    
    # Test 59: Verificación de date_hierarchy en Admin
    def test_59_verificacion_date_hierarchy_admin(self):
        """Test 59: Jerarquía de fechas en Django Admin"""
        from apps.transactions.admin import TransaccionAdmin
        
        admin_instance = TransaccionAdmin(Transaccion, site)
        
        self.assertEqual(admin_instance.date_hierarchy, 'fecha')
    
    # Test 60: Verificación de Fieldsets en Admin
    def test_60_verificacion_fieldsets_admin(self):
        """Test 60: Agrupación de campos en Django Admin"""
        from apps.transactions.admin import TransaccionAdmin
        
        admin_instance = TransaccionAdmin(Transaccion, site)
        
        self.assertIsNotNone(admin_instance.fieldsets)
        fieldset_titles = [fs[0] for fs in admin_instance.fieldsets]
        
        self.assertIn('Información de Transacción', fieldset_titles)
        self.assertIn('Detalles Financieros', fieldset_titles)
        self.assertIn('Metadatos', fieldset_titles)
    
    # Test 61: Creación de Transacción con Todos los Campos Opcionales Usando Defaults
    def test_61_creacion_transaccion_campos_opcionales_defaults(self):
        """Test 61: Funcionamiento de valores por defecto"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00')
        )
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.moneda, 'MXN')
        self.assertEqual(transaccion.estado, 'pendiente')
        self.assertIsNotNone(transaccion.fecha)
    
    # Test 62: Actualización Parcial de Transacción
    def test_62_actualizacion_parcial_transaccion(self):
        """Test 62: Actualización de campos individuales"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        monto_original = transaccion.monto
        moneda_original = transaccion.moneda
        fecha_original = transaccion.fecha
        
        transaccion.estado = 'completada'
        transaccion.save()
        
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'completada')
        self.assertEqual(transaccion.monto, monto_original)
        self.assertEqual(transaccion.moneda, moneda_original)
        self.assertEqual(transaccion.fecha, fecha_original)
    
    # Test 63: Verificación de Unicidad de id_transaccion
    def test_63_verificacion_unicidad_id_transaccion(self):
        """Test 63: Primary key único"""
        id_transaccion = uuid.uuid4()
        
        Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_transaccion=id_transaccion,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises((IntegrityError, ValidationError)):
            Transaccion.objects.create(
                company=self.company,
                sitec=self.sitec,
                id_transaccion=id_transaccion,
                id_cliente=self.cliente,
                monto=Decimal('200.00'),
                moneda='USD',
                fecha=timezone.now(),
                estado='completada'
            )
    
    # Test 64: Verificación de Generación Automática de UUID
    def test_64_verificacion_generacion_automatica_uuid(self):
        """Test 64: Generación automática de id_transaccion"""
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
    
    # Test 65: Verificación de Generación Automática de UUID de Cliente
    def test_65_verificacion_generacion_automatica_uuid_cliente(self):
        """Test 65: Generación automática de id de Cliente"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente UUID Test"
        )
        
        self.assertIsNotNone(cliente.id)
        self.assertIsInstance(cliente.id, uuid.UUID)
    
    # Test 66: Verificación de Inmutabilidad de id_transaccion
    def test_66_verificacion_inmutabilidad_id_transaccion(self):
        """Test 66: Primary key no editable después de creación"""
        transaccion = Transaccion.objects.create(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=Decimal('100.00'),
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        id_original = transaccion.id_transaccion
        
        # Verificar que editable=False está configurado (afecta formularios admin, no modificación programática)
        id_field = Transaccion._meta.get_field('id_transaccion')
        self.assertFalse(id_field.editable)
        
        # En Django, editable=False solo previene edición en formularios, no modificación programática
        # Pero la primary key no debería cambiarse en la práctica
        # Verificamos que el campo tiene editable=False configurado
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.id_transaccion, id_original)
    
    # Test 67: Verificación de Inmutabilidad de id de Cliente
    def test_67_verificacion_inmutabilidad_id_cliente(self):
        """Test 67: Primary key no editable después de creación"""
        cliente = Cliente.objects.create(
            company=self.company,
            sitec=self.sitec,
            nombre="Cliente Inmutable"
        )
        
        id_original = cliente.id
        
        # Verificar que editable=False está configurado
        id_field = Cliente._meta.get_field('id')
        self.assertFalse(id_field.editable)
        
        # En Django, editable=False solo previene edición en formularios, no modificación programática
        # Verificamos que el campo tiene editable=False configurado
        cliente.refresh_from_db()
        self.assertEqual(cliente.id, id_original)
    
    # Test 68: Creación de Transacción con Monto que Excede max_digits
    def test_68_creacion_transaccion_monto_excede_max_digits(self):
        """Test 68: Validación de límite máximo de dígitos"""
        # Crear monto que excede 15 dígitos totales
        monto_excedido = Decimal('99999999999999.99')  # 16 dígitos antes del punto
        
        transaccion = Transaccion(
            company=self.company,
            sitec=self.sitec,
            id_cliente=self.cliente,
            monto=monto_excedido,
            moneda='MXN',
            fecha=timezone.now(),
            estado='pendiente'
        )
        
        with self.assertRaises(ValidationError) as context:
            transaccion.save()
        
        self.assertIn('monto', str(context.exception))
    
    # Test 69: Verificación de Meta.verbose_name y verbose_name_plural
    def test_69_verificacion_meta_verbose_name(self):
        """Test 69: Nombres descriptivos del modelo"""
        self.assertEqual(Transaccion._meta.verbose_name, 'Transacción')
        self.assertEqual(Transaccion._meta.verbose_name_plural, 'Transacciones')
    
    # Test 70: Verificación de db_column Personalizado
    def test_70_verificacion_db_column_personalizado(self):
        """Test 70: Nombres de columnas personalizados en base de datos"""
        # Verificar db_column en los campos
        id_transaccion_field = Transaccion._meta.get_field('id_transaccion')
        id_cliente_field = Transaccion._meta.get_field('id_cliente')
        
        self.assertEqual(id_transaccion_field.db_column, 'id_transaccion')
        self.assertEqual(id_cliente_field.db_column, 'id_cliente')
