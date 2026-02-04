# TESTS FUNCIONALES ESTRICTOS - SISTEMA DE TRANSACCIONES

## MÓDULO: Gestión de Transacciones Financieras

### FUNCIONALIDADES DEL SISTEMA:
- Creación de transacciones con validación estricta
- Gestión de estados de transacciones (pendiente, completada, cancelada, fallida)
- Asociación de transacciones con clientes
- Validación de montos, monedas y fechas
- Persistencia y recuperación de datos
- Protección de integridad referencial

---

## TESTS FUNCIONALES

### 1. Creación de Transacción Válida Completa
**Funcionalidad evaluada:** Creación de transacción con todos los campos válidos
**Precondiciones:** Cliente existente en base de datos con id válido
**Pasos de ejecución:**
1. Crear instancia de Transaccion con id_cliente válido, monto=100.00, moneda='MXN', fecha=datetime actual, estado='pendiente'
2. Ejecutar save()
3. Recuperar transacción de base de datos por id_transaccion
4. Verificar todos los campos guardados
**Resultado esperado:** Transacción creada con id_transaccion UUID único, todos los campos persisten correctamente, created_at y updated_at establecidos, estado='pendiente', moneda='MXN'
**Condición de fallo:** Cualquier campo no persiste, id_transaccion no se genera, timestamps no se establecen, ValidationError lanzado
**Severidad:** Crítica

### 2. Creación de Transacción sin Cliente
**Funcionalidad evaluada:** Validación de campo requerido id_cliente
**Precondiciones:** Ninguna
**Pasos de ejecución:**
1. Crear instancia de Transaccion sin especificar id_cliente
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado con mensaje indicando que id_cliente es requerido, transacción no se crea en base de datos
**Condición de fallo:** Transacción se crea sin cliente, error no se lanza, mensaje de error incorrecto
**Severidad:** Crítica

### 3. Creación de Transacción con Monto Negativo
**Funcionalidad evaluada:** Validación de monto positivo
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con monto=-50.00
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado con mensaje 'El monto debe ser mayor a 0', transacción no se crea
**Condición de fallo:** Transacción se crea con monto negativo, error no se lanza, constraint de base de datos no funciona
**Severidad:** Crítica

### 4. Creación de Transacción con Monto Cero
**Funcionalidad evaluada:** Validación de monto mínimo 0.01
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con monto=0.00
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, transacción no se crea
**Condición de fallo:** Transacción se crea con monto cero, validación MinValueValidator no funciona
**Severidad:** Crítica

### 5. Creación de Transacción con Monto Mínimo Válido
**Funcionalidad evaluada:** Aceptación de monto mínimo permitido
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con monto=0.01
2. Ejecutar save()
3. Recuperar transacción de base de datos
**Resultado esperado:** Transacción creada exitosamente, monto persiste como Decimal('0.01')
**Condición de fallo:** ValidationError lanzado incorrectamente, monto no persiste correctamente
**Severidad:** Alta

### 6. Creación de Transacción con Monto Máximo Válido
**Funcionalidad evaluada:** Aceptación de monto máximo permitido (9999999999999.99)
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con monto=9999999999999.99
2. Ejecutar save()
3. Recuperar transacción de base de datos
**Resultado esperado:** Transacción creada exitosamente, monto persiste correctamente
**Condición de fallo:** ValidationError lanzado, monto truncado o modificado, overflow de DecimalField
**Severidad:** Alta

### 7. Creación de Transacción con Moneda Inválida
**Funcionalidad evaluada:** Validación de moneda ISO 4217 válida
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con moneda='XXX'
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado con mensaje indicando monedas válidas, transacción no se crea
**Condición de fallo:** Transacción se crea con moneda inválida, error no se lanza, constraint de choices no funciona
**Severidad:** Crítica

### 8. Creación de Transacción con Moneda en Minúsculas
**Funcionalidad evaluada:** Validación de formato de moneda (mayúsculas)
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con moneda='mxn'
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, transacción no se crea
**Condición de fallo:** Transacción se crea con moneda en minúsculas, validación de choices permite minúsculas
**Severidad:** Alta

### 9. Creación de Transacción con Todas las Monedas Válidas
**Funcionalidad evaluada:** Aceptación de todas las monedas permitidas
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Para cada moneda en ['MXN', 'USD', 'EUR', 'GBP', 'CAD', 'ARS', 'BRL', 'CLP', 'COP', 'PEN']:
   - Crear instancia de Transaccion con moneda=moneda_actual
   - Ejecutar save()
   - Verificar persistencia
**Resultado esperado:** Todas las transacciones se crean exitosamente, cada moneda persiste correctamente
**Condición de fallo:** Alguna moneda válida es rechazada, moneda no persiste correctamente
**Severidad:** Alta

### 10. Creación de Transacción con Fecha Futura
**Funcionalidad evaluada:** Validación de fecha no futura
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con fecha=timezone.now() + timedelta(days=1)
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado con mensaje 'La fecha de la transacción no puede ser futura', transacción no se crea
**Condición de fallo:** Transacción se crea con fecha futura, validación en clean() no funciona
**Severidad:** Crítica

### 11. Creación de Transacción sin Especificar Fecha
**Funcionalidad evaluada:** Aplicación de default para fecha
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion sin especificar fecha
2. Ejecutar save()
3. Recuperar transacción de base de datos
**Resultado esperado:** Transacción creada con fecha establecida automáticamente a timezone.now(), diferencia menor a 5 segundos
**Condición de fallo:** Fecha es None, fecha incorrecta, default no funciona
**Severidad:** Alta

### 12. Creación de Transacción con Estado Inválido
**Funcionalidad evaluada:** Validación de estado válido
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion con estado='invalido'
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado con mensaje indicando estados válidos, transacción no se crea
**Condición de fallo:** Transacción se crea con estado inválido, constraint de base de datos no funciona
**Severidad:** Crítica

### 13. Creación de Transacción sin Especificar Estado
**Funcionalidad evaluada:** Aplicación de default para estado
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion sin especificar estado
2. Ejecutar save()
3. Recuperar transacción de base de datos
**Resultado esperado:** Transacción creada con estado='pendiente' por defecto
**Condición de fallo:** Estado es None o diferente a 'pendiente', default no funciona
**Severidad:** Alta

### 14. Creación de Transacción sin Especificar Moneda
**Funcionalidad evaluada:** Aplicación de default para moneda
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear instancia de Transaccion sin especificar moneda
2. Ejecutar save()
3. Recuperar transacción de base de datos
**Resultado esperado:** Transacción creada con moneda='MXN' por defecto
**Condición de fallo:** Moneda es None o diferente a 'MXN', default no funciona
**Severidad:** Alta

### 15. Actualización de Estado de Transacción Pendiente a Completada
**Funcionalidad evaluada:** Transición de estado válida
**Precondiciones:** Transacción existente con estado='pendiente'
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar estado a 'completada'
3. Ejecutar save()
4. Recuperar transacción actualizada
**Resultado esperado:** Estado actualizado a 'completada', updated_at modificado, created_at sin cambios
**Condición de fallo:** Estado no se actualiza, updated_at no cambia, created_at se modifica, ValidationError lanzado incorrectamente
**Severidad:** Crítica

### 16. Actualización de Estado de Transacción Completada a Pendiente
**Funcionalidad evaluada:** Transición de estado inversa
**Precondiciones:** Transacción existente con estado='completada'
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar estado a 'pendiente'
3. Ejecutar save()
4. Recuperar transacción actualizada
**Resultado esperado:** Estado actualizado a 'pendiente', operación permitida sin restricciones
**Condición de fallo:** Transición bloqueada incorrectamente, ValidationError lanzado
**Severidad:** Media

### 17. Actualización de Monto de Transacción Existente
**Funcionalidad evaluada:** Modificación de monto después de creación
**Precondiciones:** Transacción existente con monto=100.00
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar monto a 200.00
3. Ejecutar save()
4. Recuperar transacción actualizada
**Resultado esperado:** Monto actualizado a 200.00, updated_at modificado, validaciones aplicadas
**Condición de fallo:** Monto no se actualiza, validación de monto positivo no se ejecuta en actualización
**Severidad:** Crítica

### 18. Actualización de Monto a Valor Negativo
**Funcionalidad evaluada:** Validación de monto positivo en actualización
**Precondiciones:** Transacción existente con monto=100.00
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar monto a -50.00
3. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, monto no se actualiza, transacción mantiene valor original
**Condición de fallo:** Monto se actualiza a negativo, validación no se ejecuta en actualización
**Severidad:** Crítica

### 19. Actualización de Moneda de Transacción Existente
**Funcionalidad evaluada:** Modificación de moneda después de creación
**Precondiciones:** Transacción existente con moneda='MXN'
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar moneda a 'USD'
3. Ejecutar save()
4. Recuperar transacción actualizada
**Resultado esperado:** Moneda actualizada a 'USD', validación de moneda válida aplicada
**Condición de fallo:** Moneda no se actualiza, validación no se ejecuta
**Severidad:** Alta

### 20. Actualización de Fecha de Transacción Existente
**Funcionalidad evaluada:** Modificación de fecha después de creación
**Precondiciones:** Transacción existente con fecha pasada
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar fecha a otra fecha pasada válida
3. Ejecutar save()
4. Recuperar transacción actualizada
**Resultado esperado:** Fecha actualizada correctamente, validación de fecha no futura aplicada
**Condición de fallo:** Fecha no se actualiza, validación no se ejecuta
**Severidad:** Alta

### 21. Actualización de Fecha a Futura en Transacción Existente
**Funcionalidad evaluada:** Validación de fecha no futura en actualización
**Precondiciones:** Transacción existente con fecha pasada
**Pasos de ejecución:**
1. Recuperar transacción de base de datos
2. Modificar fecha a timezone.now() + timedelta(days=1)
3. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, fecha no se actualiza, transacción mantiene fecha original
**Condición de fallo:** Fecha se actualiza a futura, validación no se ejecuta en actualización
**Severidad:** Crítica

### 22. Eliminación de Cliente sin Transacciones
**Funcionalidad evaluada:** Eliminación permitida de cliente sin dependencias
**Precondiciones:** Cliente existente sin transacciones asociadas
**Pasos de ejecución:**
1. Recuperar cliente de base de datos
2. Ejecutar delete()
3. Verificar eliminación
**Resultado esperado:** Cliente eliminado exitosamente, registro no existe en base de datos
**Condición de fallo:** Cliente no se elimina, error lanzado incorrectamente
**Severidad:** Media

### 23. Eliminación de Cliente con Transacciones Asociadas
**Funcionalidad evaluada:** Protección de integridad referencial (PROTECT)
**Precondiciones:** Cliente existente con al menos una transacción asociada
**Pasos de ejecución:**
1. Crear transacción asociada al cliente
2. Intentar eliminar cliente
3. Ejecutar delete()
**Resultado esperado:** ProtectedError lanzado, cliente no se elimina, transacciones permanecen intactas
**Condición de fallo:** Cliente se elimina, transacciones quedan huérfanas, error no se lanza
**Severidad:** Crítica

### 24. Recuperación de Transacción por ID
**Funcionalidad evaluada:** Consulta de transacción por identificador único
**Precondiciones:** Transacción existente con id_transaccion conocido
**Pasos de ejecución:**
1. Crear transacción y guardar id_transaccion
2. Ejecutar Transaccion.objects.get(id_transaccion=id_guardado)
3. Verificar campos recuperados
**Resultado esperado:** Transacción recuperada correctamente, todos los campos coinciden con valores originales
**Condición de fallo:** Transacción no se encuentra, campos incorrectos, DoesNotExist lanzado incorrectamente
**Severidad:** Crítica

### 25. Recuperación de Transacciones por Cliente
**Funcionalidad evaluada:** Consulta de transacciones asociadas a un cliente
**Precondiciones:** Cliente existente con múltiples transacciones asociadas
**Pasos de ejecución:**
1. Crear cliente
2. Crear 5 transacciones asociadas al cliente
3. Ejecutar cliente.transacciones.all()
4. Verificar cantidad y contenido
**Resultado esperado:** 5 transacciones recuperadas, todas asociadas al cliente correcto, relación inversa funciona
**Condición de fallo:** Cantidad incorrecta, transacciones de otros clientes incluidas, relación inversa no funciona
**Severidad:** Crítica

### 26. Recuperación de Transacciones por Estado
**Funcionalidad evaluada:** Filtrado de transacciones por estado
**Precondiciones:** Múltiples transacciones con diferentes estados
**Pasos de ejecución:**
1. Crear 3 transacciones con estado='pendiente'
2. Crear 2 transacciones con estado='completada'
3. Ejecutar Transaccion.objects.filter(estado='pendiente')
4. Verificar resultados
**Resultado esperado:** 3 transacciones con estado='pendiente' recuperadas, índice utilizado para optimización
**Condición de fallo:** Cantidad incorrecta, transacciones con otros estados incluidas, filtro no funciona
**Severidad:** Alta

### 27. Recuperación de Transacciones por Moneda
**Funcionalidad evaluada:** Filtrado de transacciones por moneda
**Precondiciones:** Múltiples transacciones con diferentes monedas
**Pasos de ejecución:**
1. Crear 4 transacciones con moneda='USD'
2. Crear 3 transacciones con moneda='MXN'
3. Ejecutar Transaccion.objects.filter(moneda='USD')
4. Verificar resultados
**Resultado esperado:** 4 transacciones con moneda='USD' recuperadas, índice utilizado
**Condición de fallo:** Cantidad incorrecta, transacciones con otras monedas incluidas
**Severidad:** Alta

### 28. Recuperación de Transacciones Ordenadas por Fecha Descendente
**Funcionalidad evaluada:** Ordenamiento según Meta.ordering
**Precondiciones:** Múltiples transacciones con fechas diferentes
**Pasos de ejecución:**
1. Crear transacciones con fechas: hoy, ayer, hace 2 días
2. Ejecutar Transaccion.objects.all()
3. Verificar orden
**Resultado esperado:** Transacciones ordenadas por fecha descendente (más reciente primero), luego por created_at descendente
**Condición de fallo:** Orden incorrecto, ordenamiento no funciona, Meta.ordering ignorado
**Severidad:** Media

### 29. Creación Múltiple de Transacciones para Mismo Cliente
**Funcionalidad evaluada:** Múltiples transacciones asociadas a un cliente
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear 10 transacciones asociadas al mismo cliente con diferentes montos y estados
2. Ejecutar cliente.transacciones.count()
3. Verificar todas las transacciones
**Resultado esperado:** 10 transacciones creadas, todas asociadas al cliente, count() retorna 10
**Condición de fallo:** Cantidad incorrecta, alguna transacción no asociada correctamente
**Severidad:** Alta

### 30. Creación de Transacciones para Diferentes Clientes
**Funcionalidad evaluada:** Aislamiento de transacciones entre clientes
**Precondiciones:** Múltiples clientes existentes
**Pasos de ejecución:**
1. Crear cliente A y cliente B
2. Crear 3 transacciones para cliente A
3. Crear 2 transacciones para cliente B
4. Verificar transacciones de cada cliente
**Resultado esperado:** Cliente A tiene 3 transacciones, Cliente B tiene 2 transacciones, no hay mezcla
**Condición de fallo:** Transacciones mezcladas entre clientes, aislamiento no funciona
**Severidad:** Crítica

### 31. Idempotencia de Creación de Transacción
**Funcionalidad evaluada:** Creación repetida con mismos datos produce resultados consistentes
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con datos específicos
2. Guardar y obtener id_transaccion_1
3. Crear otra transacción con mismos datos (excepto id_transaccion)
4. Guardar y obtener id_transaccion_2
5. Verificar que son diferentes
**Resultado esperado:** Dos transacciones creadas con id_transaccion diferentes, resto de campos idénticos
**Condición de fallo:** id_transaccion duplicado, unicidad violada
**Severidad:** Crítica

### 32. Persistencia de Transacción después de Reinicio de Base de Datos
**Funcionalidad evaluada:** Persistencia permanente de datos
**Precondiciones:** Transacción creada y guardada
**Pasos de ejecución:**
1. Crear y guardar transacción
2. Cerrar conexión de base de datos
3. Abrir nueva conexión
4. Recuperar transacción por id_transaccion
**Resultado esperado:** Transacción recuperada con todos los campos intactos, persistencia garantizada
**Condición de fallo:** Transacción no se encuentra, datos corruptos, persistencia falla
**Severidad:** Crítica

### 33. Actualización de updated_at en Modificación
**Funcionalidad evaluada:** Actualización automática de timestamp updated_at
**Precondiciones:** Transacción existente
**Pasos de ejecución:**
1. Recuperar transacción y guardar updated_at_original
2. Esperar 1 segundo
3. Modificar cualquier campo
4. Ejecutar save()
5. Recuperar transacción y verificar updated_at
**Resultado esperado:** updated_at modificado y mayor que updated_at_original, created_at sin cambios
**Condición de fallo:** updated_at no se actualiza, created_at se modifica, auto_now no funciona
**Severidad:** Alta

### 34. Inmutabilidad de created_at después de Actualización
**Funcionalidad evaluada:** created_at no se modifica en actualizaciones
**Precondiciones:** Transacción existente
**Pasos de ejecución:**
1. Recuperar transacción y guardar created_at_original
2. Modificar campos múltiples veces
3. Ejecutar save() múltiples veces
4. Recuperar transacción y verificar created_at
**Resultado esperado:** created_at permanece igual a created_at_original, auto_now_add funciona correctamente
**Condición de fallo:** created_at se modifica, inmutabilidad violada
**Severidad:** Crítica

### 35. Validación de Precisión Decimal de Monto
**Funcionalidad evaluada:** Precisión de 2 decimales en campo monto
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con monto=100.999
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado indicando máximo 2 decimales, transacción no se crea
**Condición de fallo:** Transacción se crea con más de 2 decimales, precisión no se valida
**Severidad:** Alta

### 36. Creación de Transacción con Monto Exactamente en Límite de Precisión
**Funcionalidad evaluada:** Aceptación de monto con exactamente 2 decimales
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con monto=123.45
2. Ejecutar save()
3. Recuperar transacción
**Resultado esperado:** Transacción creada, monto persiste como Decimal('123.45')
**Condición de fallo:** ValidationError lanzado incorrectamente, monto modificado
**Severidad:** Media

### 37. Transición de Estado Pendiente a Cancelada
**Funcionalidad evaluada:** Cambio de estado válido
**Precondiciones:** Transacción con estado='pendiente'
**Pasos de ejecución:**
1. Recuperar transacción
2. Modificar estado a 'cancelada'
3. Ejecutar save()
4. Verificar estado
**Resultado esperado:** Estado actualizado a 'cancelada', transición permitida
**Condición de fallo:** Estado no se actualiza, transición bloqueada incorrectamente
**Severidad:** Alta

### 38. Transición de Estado Pendiente a Fallida
**Funcionalidad evaluada:** Cambio de estado válido
**Precondiciones:** Transacción con estado='pendiente'
**Pasos de ejecución:**
1. Recuperar transacción
2. Modificar estado a 'fallida'
3. Ejecutar save()
4. Verificar estado
**Resultado esperado:** Estado actualizado a 'fallida', transición permitida
**Condición de fallo:** Estado no se actualiza, transición bloqueada
**Severidad:** Alta

### 39. Consulta de Transacciones por Rango de Fechas
**Funcionalidad evaluada:** Filtrado por rango temporal
**Precondiciones:** Transacciones con fechas distribuidas en diferentes días
**Pasos de ejecución:**
1. Crear transacciones con fechas: hoy, ayer, hace 3 días
2. Ejecutar Transaccion.objects.filter(fecha__gte=ayer, fecha__lte=hoy)
3. Verificar resultados
**Resultado esperado:** Transacciones dentro del rango recuperadas correctamente, índice utilizado
**Condición de fallo:** Transacciones fuera del rango incluidas, filtro no funciona correctamente
**Severidad:** Media

### 40. Consulta de Transacciones por Cliente y Estado
**Funcionalidad evaluada:** Filtrado combinado por múltiples campos
**Precondiciones:** Cliente con transacciones en diferentes estados
**Pasos de ejecución:**
1. Crear cliente
2. Crear transacciones: 2 pendientes, 3 completadas
3. Ejecutar Transaccion.objects.filter(id_cliente=cliente, estado='pendiente')
4. Verificar resultados
**Resultado esperado:** 2 transacciones pendientes del cliente recuperadas, filtro combinado funciona
**Condición de fallo:** Cantidad incorrecta, transacciones de otros clientes o estados incluidas
**Severidad:** Alta

### 41. Consulta de Transacciones por Cliente y Moneda
**Funcionalidad evaluada:** Filtrado combinado por cliente y moneda
**Precondiciones:** Cliente con transacciones en diferentes monedas
**Pasos de ejecución:**
1. Crear cliente
2. Crear transacciones: 3 en USD, 2 en MXN
3. Ejecutar Transaccion.objects.filter(id_cliente=cliente, moneda='USD')
4. Verificar resultados
**Resultado esperado:** 3 transacciones en USD del cliente recuperadas
**Condición de fallo:** Cantidad incorrecta, filtro combinado no funciona
**Severidad:** Media

### 42. Verificación de Índice en Consulta por Cliente y Fecha
**Funcionalidad evaluada:** Optimización mediante índices compuestos
**Precondiciones:** Múltiples transacciones de diferentes clientes y fechas
**Pasos de ejecución:**
1. Crear múltiples transacciones
2. Ejecutar Transaccion.objects.filter(id_cliente=cliente).order_by('-fecha')
3. Verificar uso de índice transaccion_cliente_fecha_idx
**Resultado esperado:** Consulta optimizada usando índice compuesto, rendimiento adecuado
**Condición de fallo:** Índice no se utiliza, consulta lenta, optimización falla
**Severidad:** Baja

### 43. Verificación de Índice en Consulta por Estado y Fecha
**Funcionalidad evaluada:** Optimización mediante índices compuestos
**Precondiciones:** Múltiples transacciones con diferentes estados y fechas
**Pasos de ejecución:**
1. Crear múltiples transacciones
2. Ejecutar Transaccion.objects.filter(estado='pendiente').order_by('-fecha')
3. Verificar uso de índice transaccion_estado_fecha_idx
**Resultado esperado:** Consulta optimizada usando índice compuesto
**Condición de fallo:** Índice no se utiliza, optimización falla
**Severidad:** Baja

### 44. Verificación de Constraint de Monto Positivo en Base de Datos
**Funcionalidad evaluada:** Constraint de base de datos como respaldo
**Precondiciones:** Acceso directo a base de datos
**Pasos de ejecución:**
1. Intentar insertar registro directamente en base de datos con monto negativo usando SQL raw
2. Verificar rechazo
**Resultado esperado:** IntegrityError o rechazo por constraint transaccion_monto_positivo
**Condición de fallo:** Inserción exitosa con monto negativo, constraint no funciona
**Severidad:** Crítica

### 45. Verificación de Constraint de Estado Válido en Base de Datos
**Funcionalidad evaluada:** Constraint de base de datos como respaldo
**Precondiciones:** Acceso directo a base de datos
**Pasos de ejecución:**
1. Intentar insertar registro directamente con estado inválido usando SQL raw
2. Verificar rechazo
**Resultado esperado:** IntegrityError o rechazo por constraint transaccion_estado_valido
**Condición de fallo:** Inserción exitosa con estado inválido, constraint no funciona
**Severidad:** Crítica

### 46. Creación de Transacción con Cliente Inexistente
**Funcionalidad evaluada:** Validación de ForeignKey existente
**Precondiciones:** Cliente no guardado en base de datos
**Pasos de ejecución:**
1. Crear instancia de Cliente sin guardar
2. Crear Transaccion con id_cliente=cliente_no_guardado
3. Ejecutar save()
**Resultado esperado:** IntegrityError o ValidationError lanzado, transacción no se crea
**Condición de fallo:** Transacción se crea con referencia a cliente inexistente, integridad referencial violada
**Severidad:** Crítica

### 47. Recuperación de Transacción después de Eliminación de Cliente (Protegida)
**Funcionalidad evaluada:** Transacciones permanecen después de intento de eliminación de cliente
**Precondiciones:** Cliente con transacciones asociadas
**Pasos de ejecución:**
1. Crear cliente y transacción asociada
2. Intentar eliminar cliente
3. Verificar que ProtectedError se lanza
4. Recuperar transacción
**Resultado esperado:** Transacción sigue existiendo y accesible, cliente no eliminado
**Condición de fallo:** Transacción eliminada o inaccesible, cliente eliminado incorrectamente
**Severidad:** Crítica

### 48. Flujo Completo: Creación, Actualización y Consulta
**Funcionalidad evaluada:** Flujo end-to-end completo
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con estado='pendiente', monto=100.00
2. Verificar creación
3. Actualizar estado a 'completada', monto a 150.00
4. Verificar actualización
5. Consultar transacción y verificar valores finales
**Resultado esperado:** Transacción creada, actualizada y recuperada correctamente, todos los cambios persisten
**Condición de fallo:** Cualquier paso del flujo falla, datos inconsistentes
**Severidad:** Crítica

### 49. Creación Concurrente de Transacciones para Mismo Cliente
**Funcionalidad evaluada:** Manejo de concurrencia
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear 10 transacciones simultáneamente para el mismo cliente
2. Verificar que todas se crean correctamente
3. Verificar que todas están asociadas al cliente
**Resultado esperado:** 10 transacciones creadas sin conflictos, todas asociadas correctamente
**Condición de fallo:** Transacciones perdidas, conflictos de concurrencia, datos inconsistentes
**Severidad:** Alta

### 50. Validación de Método __str__ de Transaccion
**Funcionalidad evaluada:** Representación de cadena del modelo
**Precondiciones:** Transacción existente con datos conocidos
**Pasos de ejecución:**
1. Crear transacción con id_transaccion conocido, cliente con nombre conocido, monto y moneda
2. Ejecutar str(transaccion)
3. Verificar formato
**Resultado esperado:** Cadena con formato "Transacción {id_transaccion} - Cliente: {nombre} - {monto} {moneda}"
**Condición de fallo:** Formato incorrecto, información faltante, TypeError lanzado
**Severidad:** Baja

### 51. Validación de Método __str__ de Cliente
**Funcionalidad evaluada:** Representación de cadena del modelo Cliente
**Precondiciones:** Cliente existente con nombre conocido
**Pasos de ejecución:**
1. Crear cliente con nombre conocido
2. Ejecutar str(cliente)
3. Verificar formato
**Resultado esperado:** Cadena igual al nombre del cliente
**Condición de fallo:** Formato incorrecto, nombre no coincide
**Severidad:** Baja

### 52. Verificación de Ordenamiento por Fecha y created_at
**Funcionalidad evaluada:** Ordenamiento múltiple según Meta.ordering
**Precondiciones:** Transacciones con misma fecha pero diferentes created_at
**Pasos de ejecución:**
1. Crear múltiples transacciones con misma fecha pero creadas en momentos diferentes
2. Ejecutar Transaccion.objects.all()
3. Verificar orden: primero por fecha descendente, luego por created_at descendente
**Resultado esperado:** Transacciones ordenadas correctamente según ambos criterios
**Condición de fallo:** Orden incorrecto, ordenamiento múltiple no funciona
**Severidad:** Media

### 53. Creación de Transacción con Monto en Límite Inferior Exacto
**Funcionalidad evaluada:** Validación de límite mínimo estricto
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con monto=0.01
2. Ejecutar save()
3. Verificar creación
**Resultado esperado:** Transacción creada exitosamente, monto=0.01 aceptado
**Condición de fallo:** ValidationError lanzado incorrectamente, límite mínimo no funciona
**Severidad:** Alta

### 54. Creación de Transacción con Monto Justo Debajo del Mínimo
**Funcionalidad evaluada:** Rechazo de valores menores al mínimo
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con monto=0.009
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, monto menor a 0.01 rechazado
**Condición de fallo:** Transacción se crea con monto menor al mínimo, validación falla
**Severidad:** Crítica

### 55. Verificación de db_table Personalizado
**Funcionalidad evaluada:** Nombre de tabla personalizado en base de datos
**Precondiciones:** Acceso a esquema de base de datos
**Pasos de ejecución:**
1. Verificar existencia de tabla 'transactions_transaccion' en base de datos
2. Verificar existencia de tabla 'transactions_cliente' en base de datos
**Resultado esperado:** Tablas existen con nombres especificados en Meta.db_table
**Condición de fallo:** Tablas con nombres incorrectos, db_table no funciona
**Severidad:** Media

### 56. Verificación de Campos Readonly en Admin
**Funcionalidad evaluada:** Configuración de campos de solo lectura en Django Admin
**Precondiciones:** Acceso a Django Admin
**Pasos de ejecución:**
1. Acceder a formulario de creación de Transaccion en Admin
2. Verificar que id_transaccion, created_at, updated_at son readonly
3. Intentar modificar estos campos
**Resultado esperado:** Campos marcados como readonly, no editables en formulario
**Condición de fallo:** Campos editables, readonly_fields no funciona
**Severidad:** Baja

### 57. Verificación de Filtros en Admin
**Funcionalidad evaluada:** Configuración de filtros en Django Admin
**Precondiciones:** Acceso a Django Admin con transacciones existentes
**Pasos de ejecución:**
1. Acceder a lista de Transacciones en Admin
2. Verificar presencia de filtros: estado, moneda, fecha, created_at
3. Aplicar cada filtro y verificar resultados
**Resultado esperado:** Filtros disponibles y funcionales, resultados correctos
**Condición de fallo:** Filtros faltantes, resultados incorrectos, list_filter no funciona
**Severidad:** Baja

### 58. Verificación de Búsqueda en Admin
**Funcionalidad evaluada:** Configuración de búsqueda en Django Admin
**Precondiciones:** Acceso a Django Admin con transacciones existentes
**Pasos de ejecución:**
1. Acceder a lista de Transacciones en Admin
2. Buscar por id_transaccion
3. Buscar por nombre de cliente
**Resultado esperado:** Búsqueda funcional, resultados correctos para ambos criterios
**Condición de fallo:** Búsqueda no funciona, resultados incorrectos, search_fields no funciona
**Severidad:** Baja

### 59. Verificación de date_hierarchy en Admin
**Funcionalidad evaluada:** Jerarquía de fechas en Django Admin
**Precondiciones:** Acceso a Django Admin con transacciones de diferentes fechas
**Pasos de ejecución:**
1. Acceder a lista de Transacciones en Admin
2. Verificar presencia de jerarquía de fechas por campo 'fecha'
3. Navegar por la jerarquía
**Resultado esperado:** Jerarquía de fechas visible y funcional
**Condición de fallo:** Jerarquía no visible, date_hierarchy no funciona
**Severidad:** Baja

### 60. Verificación de Fieldsets en Admin
**Funcionalidad evaluada:** Agrupación de campos en Django Admin
**Precondiciones:** Acceso a Django Admin
**Pasos de ejecución:**
1. Acceder a formulario de Transaccion en Admin
2. Verificar presencia de fieldsets: 'Información de Transacción', 'Detalles Financieros', 'Metadatos'
3. Verificar campos en cada fieldset
**Resultado esperado:** Campos agrupados correctamente según fieldsets definidos
**Condición de fallo:** Campos agrupados incorrectamente, fieldsets no funciona
**Severidad:** Baja

### 61. Creación de Transacción con Todos los Campos Opcionales Usando Defaults
**Funcionalidad evaluada:** Funcionamiento de valores por defecto
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear Transaccion especificando solo id_cliente y monto
2. Ejecutar save()
3. Verificar valores de moneda, fecha y estado
**Resultado esperado:** Transacción creada con moneda='MXN', fecha=timezone.now(), estado='pendiente'
**Condición de fallo:** Valores por defecto no se aplican, campos None o incorrectos
**Severidad:** Alta

### 62. Actualización Parcial de Transacción
**Funcionalidad evaluada:** Actualización de campos individuales
**Precondiciones:** Transacción existente con múltiples campos
**Pasos de ejecución:**
1. Recuperar transacción
2. Modificar solo el campo estado
3. Ejecutar save()
4. Verificar que solo estado se actualiza, otros campos sin cambios
**Resultado esperado:** Solo estado actualizado, resto de campos permanecen iguales
**Condición de fallo:** Otros campos modificados, actualización parcial no funciona
**Severidad:** Alta

### 63. Verificación de Unicidad de id_transaccion
**Funcionalidad evaluada:** Primary key único
**Precondiciones:** Transacción existente
**Pasos de ejecución:**
1. Crear transacción y obtener id_transaccion
2. Intentar crear otra transacción con mismo id_transaccion
3. Ejecutar save()
**Resultado esperado:** IntegrityError o ValidationError lanzado, segunda transacción no se crea
**Condición de fallo:** Dos transacciones con mismo id_transaccion, unicidad violada
**Severidad:** Crítica

### 64. Verificación de Generación Automática de UUID
**Funcionalidad evaluada:** Generación automática de id_transaccion
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear Transaccion sin especificar id_transaccion
2. Ejecutar save()
3. Verificar que id_transaccion es UUID válido
**Resultado esperado:** id_transaccion generado automáticamente, es instancia de UUID válida
**Condición de fallo:** id_transaccion no se genera, formato incorrecto, default no funciona
**Severidad:** Crítica

### 65. Verificación de Generación Automática de UUID de Cliente
**Funcionalidad evaluada:** Generación automática de id de Cliente
**Precondiciones:** Ninguna
**Pasos de ejecución:**
1. Crear Cliente sin especificar id
2. Ejecutar save()
3. Verificar que id es UUID válido
**Resultado esperado:** id generado automáticamente, es instancia de UUID válida
**Condición de fallo:** id no se genera, formato incorrecto
**Severidad:** Alta

### 66. Verificación de Inmutabilidad de id_transaccion
**Funcionalidad evaluada:** Primary key no editable después de creación
**Precondiciones:** Transacción existente
**Pasos de ejecución:**
1. Recuperar transacción y guardar id_transaccion_original
2. Intentar modificar id_transaccion
3. Ejecutar save()
4. Verificar que id_transaccion no cambia
**Resultado esperado:** id_transaccion permanece igual, editable=False funciona
**Condición de fallo:** id_transaccion se modifica, inmutabilidad violada
**Severidad:** Crítica

### 67. Verificación de Inmutabilidad de id de Cliente
**Funcionalidad evaluada:** Primary key no editable después de creación
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Recuperar cliente y guardar id_original
2. Intentar modificar id
3. Ejecutar save()
4. Verificar que id no cambia
**Resultado esperado:** id permanece igual, editable=False funciona
**Condición de fallo:** id se modifica
**Severidad:** Alta

### 68. Creación de Transacción con Monto que Excede max_digits
**Funcionalidad evaluada:** Validación de límite máximo de dígitos
**Precondiciones:** Cliente existente
**Pasos de ejecución:**
1. Crear transacción con monto que excede 15 dígitos totales
2. Ejecutar save()
**Resultado esperado:** ValidationError lanzado, monto rechazado por exceder max_digits
**Condición de fallo:** Transacción se crea con monto que excede límite, validación falla
**Severidad:** Alta

### 69. Verificación de Meta.verbose_name y verbose_name_plural
**Funcionalidad evaluada:** Nombres descriptivos del modelo
**Precondiciones:** Acceso a metadatos del modelo
**Pasos de ejecución:**
1. Verificar Transaccion._meta.verbose_name
2. Verificar Transaccion._meta.verbose_name_plural
**Resultado esperado:** verbose_name='Transacción', verbose_name_plural='Transacciones'
**Condición de fallo:** Nombres incorrectos, Meta no configurado
**Severidad:** Baja

### 70. Verificación de db_column Personalizado
**Funcionalidad evaluada:** Nombres de columnas personalizados en base de datos
**Precondiciones:** Acceso a esquema de base de datos
**Pasos de ejecución:**
1. Verificar nombre de columna para id_transaccion en tabla
2. Verificar nombre de columna para id_cliente en tabla
**Resultado esperado:** Columnas con nombres 'id_transaccion' y 'id_cliente' respectivamente
**Condición de fallo:** Nombres de columnas incorrectos, db_column no funciona
**Severidad:** Media
