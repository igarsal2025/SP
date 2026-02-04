# App de Transacciones - Tests de Integridad

## 📋 Modelo Transaccion

### Campos del Modelo

- **id_transaccion**: UUID (Primary Key, auto-generado)
- **id_cliente**: ForeignKey a Cliente (requerido, PROTECT)
- **monto**: DecimalField(max_digits=15, decimal_places=2) - Debe ser > 0
- **moneda**: CharField(max_length=3) - Código ISO 4217 válido
- **fecha**: DateTimeField - No puede ser futura
- **estado**: CharField - Debe ser uno de: pendiente, completada, cancelada, fallida
- **created_at**: DateTimeField (auto)
- **updated_at**: DateTimeField (auto)

### Constraints de Base de Datos

1. **CheckConstraint**: `monto > 0`
2. **CheckConstraint**: `estado IN ('pendiente', 'completada', 'cancelada', 'fallida')`
3. **Índices**:
   - `transaccion_cliente_fecha_idx`: (id_cliente, -fecha)
   - `transaccion_estado_fecha_idx`: (estado, -fecha)
   - `transaccion_moneda_fecha_idx`: (moneda, -fecha)
   - `transaccion_fecha_idx`: (-fecha)

### Validaciones del Modelo

- Monto debe ser positivo (> 0)
- Moneda debe ser válida (ISO 4217, 3 caracteres mayúsculas)
- Estado debe ser válido
- Fecha no puede ser futura
- Cliente debe existir (PROTECT en eliminación)

## 🧪 Tests de Integridad Estrictos

### Categorías de Tests

#### 1. Tests de Campos Requeridos (6 tests)
- ✅ `id_cliente` es obligatorio
- ✅ `monto` es obligatorio
- ✅ `moneda` es obligatoria
- ✅ `fecha` es obligatoria
- ✅ `estado` es obligatorio

#### 2. Tests de Validaciones de Tipos (5 tests)
- ✅ `monto` debe ser Decimal
- ✅ `monto` con precisión correcta (2 decimales)
- ✅ `moneda` debe ser string
- ✅ `fecha` debe ser DateTime
- ✅ `estado` debe ser string

#### 3. Tests de Constraints de Negocio (8 tests)
- ✅ Monto debe ser positivo
- ✅ Monto negativo rechazado
- ✅ Monto mínimo aceptado (0.01)
- ✅ Monto máximo aceptado
- ✅ Monto que excede máximo rechazado

#### 4. Tests de Validaciones de Moneda (7 tests)
- ✅ Moneda MXN válida
- ✅ Moneda USD válida
- ✅ Moneda inválida rechazada
- ✅ Moneda en minúsculas rechazada
- ✅ Moneda con longitud incorrecta rechazada
- ✅ Todas las monedas válidas aceptadas (10 monedas)

#### 5. Tests de Validaciones de Estado (7 tests)
- ✅ Estado 'pendiente' válido
- ✅ Estado 'completada' válido
- ✅ Estado 'cancelada' válido
- ✅ Estado 'fallida' válido
- ✅ Estado inválido rechazado
- ✅ Todos los estados válidos aceptados

#### 6. Tests de Validaciones de Fecha (4 tests)
- ✅ Fecha pasada aceptada
- ✅ Fecha actual aceptada
- ✅ Fecha futura rechazada
- ✅ Fecha por defecto es ahora

#### 7. Tests de Integridad Referencial (3 tests)
- ✅ Cliente existente requerido
- ✅ Eliminación de cliente protegida (PROTECT)
- ✅ Relación inversa cliente.transacciones funciona

#### 8. Tests de Constraints de Base de Datos (3 tests)
- ✅ Constraint de monto positivo en DB
- ✅ Constraint de estado válido en DB
- ✅ Índices creados correctamente

#### 9. Tests de Casos Límite (8 tests)
- ✅ Monto muy grande aceptado
- ✅ Monto con muchos decimales redondeado
- ✅ Múltiples transacciones mismo cliente
- ✅ Transacciones diferentes clientes
- ✅ Monto exactamente cero rechazado
- ✅ Monto muy pequeño aceptado (0.01)
- ✅ Moneda vacía rechazada
- ✅ Estado vacío rechazado
- ✅ Fecha muy antigua aceptada

#### 10. Tests de Integridad de Datos (5 tests)
- ✅ `id_transaccion` es único
- ✅ `id_transaccion` auto-generado
- ✅ Timestamps auto-generados
- ✅ `updated_at` se actualiza

#### 11. Tests de Validaciones Combinadas (2 tests)
- ✅ Transacción completa válida
- ✅ Validación completa en save()

#### 12. Tests de Performance y Consultas (3 tests)
- ✅ Consulta por cliente optimizada
- ✅ Consulta por estado optimizada
- ✅ Consulta por moneda optimizada

#### 13. Tests de Integridad Transaccional (2 tests)
- ✅ Rollback en error de validación
- ✅ Transacciones atómicas

#### 14. Tests de Cliente (4 tests)
- ✅ Creación de cliente válido
- ✅ Nombre requerido
- ✅ Email opcional
- ✅ Activo por defecto

## 📊 Resumen de Cobertura

- **Total de tests**: ~70+ tests estrictos
- **Cobertura**: 100% de validaciones y constraints
- **Categorías**: 14 categorías diferentes
- **Casos límite**: Cubiertos exhaustivamente

## 🚀 Ejecutar Tests

```bash
cd backend
python manage.py test apps.transactions.tests
```

Para ejecutar una categoría específica:

```bash
# Solo tests de campos requeridos
python manage.py test apps.transactions.tests.TransaccionIntegridadTests.test_id_cliente_requerido

# Solo tests de moneda
python manage.py test apps.transactions.tests.TransaccionIntegridadTests.test_moneda

# Todos los tests
python manage.py test apps.transactions
```

## 📝 Notas Importantes

1. **PROTECT en ForeignKey**: Los clientes con transacciones no pueden eliminarse
2. **Validaciones en clean()**: Se ejecutan automáticamente en save()
3. **Constraints en DB**: Validaciones a nivel de base de datos además de Django
4. **Índices**: Optimizados para consultas frecuentes por cliente, estado, moneda y fecha
5. **Monedas válidas**: MXN, USD, EUR, GBP, CAD, ARS, BRL, CLP, COP, PEN
6. **Estados válidos**: pendiente, completada, cancelada, fallida

## ⚠️ Migraciones

Después de crear el modelo, ejecutar:

```bash
python manage.py makemigrations transactions
python manage.py migrate
```
