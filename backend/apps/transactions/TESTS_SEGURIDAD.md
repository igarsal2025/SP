# TESTS DE SEGURIDAD ESTRICTOS - SISTEMA DE TRANSACCIONES

## MÓDULO: Gestión de Transacciones Financieras

### FUNCIONALIDADES DEL SISTEMA:
- Creación, lectura, actualización de transacciones financieras
- Control de acceso basado en roles (admin_empresa, pm, tecnico, supervisor, cliente)
- Sistema ABAC (Attribute-Based Access Control) con AccessPolicyPermission
- Multi-tenancy por Company/Sitec
- Autenticación mediante sesiones Django
- MFA (Multi-Factor Authentication) opcional

### ROLES Y PERFILES:
- **admin_empresa**: Acceso completo a todas las transacciones de su empresa
- **pm**: Project Manager - acceso limitado según políticas
- **tecnico**: Técnico - acceso limitado según políticas
- **supervisor**: Supervisor - acceso limitado según políticas
- **cliente**: Cliente - acceso de solo lectura limitado
- **anonymous**: Usuario no autenticado

---

## TESTS DE SEGURIDAD

### 1. Acceso No Autenticado a Creación de Transacción
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/transactions/transacciones/
**Vector de ataque:** Request HTTP sin cookies de sesión, sin header Authorization
**Regla de seguridad evaluada:** IsAuthenticated debe rechazar acceso no autenticado
**Condición de fallo:** Status code 201 o 200, transacción creada, respuesta contiene datos de transacción
**Severidad:** Crítica

### 2. Acceso No Autenticado a Listado de Transacciones
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/
**Vector de ataque:** Request HTTP sin autenticación
**Regla de seguridad evaluada:** IsAuthenticated debe rechazar acceso no autenticado
**Condición de fallo:** Status code 200, lista de transacciones retornada, datos sensibles expuestos
**Severidad:** Crítica

### 3. Acceso No Autenticado a Detalle de Transacción
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Request HTTP sin autenticación con UUID válido
**Regla de seguridad evaluada:** IsAuthenticated debe rechazar acceso no autenticado
**Condición de fallo:** Status code 200, datos de transacción retornados, información financiera expuesta
**Severidad:** Crítica

### 4. Acceso No Autenticado a Actualización de Transacción
**Rol involucrado:** anonymous
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Request HTTP sin autenticación con payload de modificación
**Regla de seguridad evaluada:** IsAuthenticated debe rechazar acceso no autenticado
**Condición de fallo:** Status code 200, transacción modificada, cambios persistidos
**Severidad:** Crítica

### 5. Acceso No Autenticado a Eliminación de Transacción
**Rol involucrado:** anonymous
**Recurso objetivo:** DELETE /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Request HTTP sin autenticación
**Regla de seguridad evaluada:** IsAuthenticated debe rechazar acceso no autenticado
**Condición de fallo:** Status code 204 o 200, transacción eliminada
**Severidad:** Crítica

### 6. Acceso de Cliente a Creación de Transacción
**Rol involucrado:** cliente
**Recurso objetivo:** POST /api/transactions/transacciones/
**Vector de ataque:** Usuario con rol cliente autenticado intenta crear transacción
**Regla de seguridad evaluada:** AccessPolicyPermission debe evaluar políticas ABAC y rechazar según rol
**Condición de fallo:** Status code 201, transacción creada, política de acceso no aplicada
**Severidad:** Crítica

### 7. Acceso de Cliente a Actualización de Transacción
**Rol involucrado:** cliente
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Usuario cliente intenta modificar transacción existente
**Regla de seguridad evaluada:** AccessPolicyPermission debe rechazar escritura para rol cliente
**Condición de fallo:** Status code 200, transacción modificada, escalamiento de privilegios exitoso
**Severidad:** Crítica

### 8. Acceso de Cliente a Eliminación de Transacción
**Rol involucrado:** cliente
**Recurso objetivo:** DELETE /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Usuario cliente intenta eliminar transacción
**Regla de seguridad evaluada:** AccessPolicyPermission debe rechazar eliminación para rol cliente
**Condición de fallo:** Status code 204, transacción eliminada, operación destructiva permitida
**Severidad:** Crítica

### 9. Acceso Cruzado Entre Empresas - Lectura
**Rol involucrado:** tecnico de Empresa A
**Recurso objetivo:** GET /api/transactions/transacciones/{id_transaccion_empresa_b}/
**Vector de ataque:** Usuario de Empresa A intenta acceder a transacción de Empresa B usando UUID válido
**Regla de seguridad evaluada:** Filtrado por Company debe prevenir acceso cross-tenant
**Condición de fallo:** Status code 200, datos de transacción de otra empresa retornados, fuga de información
**Severidad:** Crítica

### 10. Acceso Cruzado Entre Empresas - Actualización
**Rol involucrado:** pm de Empresa A
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion_empresa_b}/
**Vector de ataque:** Usuario de Empresa A modifica transacción de Empresa B
**Regla de seguridad evaluada:** Filtrado por Company debe prevenir modificación cross-tenant
**Condición de fallo:** Status code 200, transacción de otra empresa modificada, integridad violada
**Severidad:** Crítica

### 11. Acceso Cruzado Entre Empresas - Eliminación
**Rol involucrado:** admin_empresa de Empresa A
**Recurso objetivo:** DELETE /api/transactions/transacciones/{id_transaccion_empresa_b}/
**Vector de ataque:** Admin de Empresa A elimina transacción de Empresa B
**Regla de seguridad evaluada:** Filtrado por Company debe prevenir eliminación cross-tenant
**Condición de fallo:** Status code 204, transacción de otra empresa eliminada, pérdida de datos
**Severidad:** Crítica

### 12. Manipulación de ID de Transacción en URL
**Rol involucrado:** tecnico
**Recurso objetivo:** GET /api/transactions/transacciones/{id_transaccion_manipulado}/
**Vector de ataque:** Usuario modifica UUID en URL para acceder a transacción no autorizada
**Regla de seguridad evaluada:** Validación de pertenencia a Company debe rechazar IDs no autorizados
**Condición de fallo:** Status code 200, transacción no autorizada retornada, IDOR (Insecure Direct Object Reference)
**Severidad:** Crítica

### 13. Manipulación de ID de Cliente en Creación
**Rol involucrado:** tecnico
**Recurso objetivo:** POST /api/transactions/transacciones/ con id_cliente de otra empresa
**Vector de ataque:** Usuario especifica id_cliente de cliente de otra empresa en payload
**Regla de seguridad evaluada:** Validación de ForeignKey debe verificar pertenencia a misma Company
**Condición de fallo:** Status code 201, transacción creada con cliente de otra empresa, integridad referencial violada
**Severidad:** Crítica

### 14. Manipulación de Monto en Actualización
**Rol involucrado:** tecnico
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion}/ con monto negativo
**Vector de ataque:** Usuario intenta establecer monto negativo mediante manipulación de request
**Regla de seguridad evaluada:** Validación de modelo debe rechazar montos negativos
**Condición de fallo:** Status code 200, monto negativo persistido, constraint de negocio violado
**Severidad:** Crítica

### 15. Manipulación de Estado en Actualización
**Rol involucrado:** tecnico
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion}/ con estado inválido
**Vector de ataque:** Usuario envía estado no permitido en choices mediante manipulación de payload
**Regla de seguridad evaluada:** Validación de choices debe rechazar estados inválidos
**Condición de fallo:** Status code 200, estado inválido persistido, constraint violado
**Severidad:** Alta

### 16. Manipulación de Moneda en Actualización
**Rol involucrado:** tecnico
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id_transaccion}/ con moneda inválida
**Vector de ataque:** Usuario envía moneda no permitida mediante manipulación de request
**Regla de seguridad evaluada:** Validación de choices debe rechazar monedas inválidas
**Condición de fallo:** Status code 200, moneda inválida persistida, validación bypassed
**Severidad:** Alta

### 17. Escalamiento de Privilegios mediante Manipulación de Rol
**Rol involucrado:** tecnico
**Recurso objetivo:** POST /api/transactions/transacciones/ con header X-Role: admin_empresa
**Vector de ataque:** Usuario modifica header HTTP para simular rol superior
**Regla de seguridad evaluada:** Rol debe obtenerse de UserProfile, no de headers del request
**Condición de fallo:** Acceso concedido como admin_empresa, privilegios escalados
**Severidad:** Crítica

### 18. Escalamiento de Privilegios mediante Manipulación de Company ID
**Rol involucrado:** tecnico de Empresa A
**Recurso objetivo:** GET /api/transactions/transacciones/ con header X-Company-Id: {id_empresa_b}
**Vector de ataque:** Usuario modifica header para acceder como otra empresa
**Regla de seguridad evaluada:** Company debe obtenerse de UserProfile, no de headers manipulables
**Condición de fallo:** Acceso a datos de otra empresa, multi-tenancy violado
**Severidad:** Crítica

### 19. Bypass de Autenticación mediante Token Manipulado
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/ con sessionid inválido
**Vector de ataque:** Usuario envía cookie sessionid con valor aleatorio o de otro usuario
**Regla de seguridad evaluada:** Django debe validar sesión y rechazar tokens inválidos
**Condición de fallo:** Status code 200, acceso concedido con token inválido, autenticación bypassed
**Severidad:** Crítica

### 20. Bypass de Autenticación mediante Session Fixation
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/ con sessionid fijado antes de login
**Vector de ataque:** Atacante fija sessionid y fuerza víctima a autenticarse con esa sesión
**Regla de seguridad evaluada:** Django debe regenerar sessionid después de login
**Condición de fallo:** Acceso con sessionid fijado, sesión no regenerada
**Severidad:** Alta

### 21. Acceso con Sesión Expirada
**Rol involucrado:** tecnico
**Recurso objetivo:** GET /api/transactions/transacciones/ con sessionid expirado
**Vector de ataque:** Usuario intenta acceder con sesión que excedió SESSION_COOKIE_AGE
**Regla de seguridad evaluada:** Django debe invalidar sesiones expiradas
**Condición de fallo:** Status code 200, acceso concedido con sesión expirada, expiración no aplicada
**Severidad:** Alta

### 22. Acceso con Sesión de Otro Usuario
**Rol involucrado:** tecnico
**Recurso objetivo:** GET /api/transactions/transacciones/ con sessionid de usuario diferente
**Vector de ataque:** Usuario A utiliza sessionid de Usuario B obtenido por robo o leak
**Regla de seguridad evaluada:** Django debe validar que sessionid corresponde al usuario autenticado
**Condición de fallo:** Status code 200, acceso como otro usuario, identidad suplantada
**Severidad:** Crítica

### 23. Acceso sin CSRF Token en Request POST
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin header X-CSRFToken
**Vector de ataque:** Request POST sin token CSRF válido
**Regla de seguridad evaluada:** CsrfViewMiddleware debe rechazar requests sin CSRF token
**Condición de fallo:** Status code 201, transacción creada sin CSRF, protección CSRF bypassed
**Severidad:** Crítica

### 24. Acceso con CSRF Token Inválido
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con X-CSRFToken: valor_aleatorio
**Vector de ataque:** Usuario envía token CSRF con valor incorrecto
**Regla de seguridad evaluada:** CsrfViewMiddleware debe validar token CSRF
**Condición de fallo:** Status code 201, transacción creada con token inválido, validación CSRF fallida
**Severidad:** Crítica

### 25. Acceso con CSRF Token de Otra Sesión
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con X-CSRFToken de sesión diferente
**Vector de ataque:** Usuario utiliza token CSRF de otra sesión activa
**Regla de seguridad evaluada:** CSRF token debe estar asociado a la sesión actual
**Condición de fallo:** Status code 201, token de otra sesión aceptado, protección CSRF violada
**Severidad:** Crítica

### 26. Rate Limiting Bypass mediante IP Spoofing
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/transactions/transacciones/ con múltiples requests y X-Forwarded-For rotado
**Vector de ataque:** Atacante modifica header X-Forwarded-For para evadir rate limiting
**Regla de seguridad evaluada:** RateLimitMiddleware debe validar IP real y no confiar solo en headers
**Condición de fallo:** Rate limit evadido, múltiples requests exitosos, DoS potencial
**Severidad:** Alta

### 27. Rate Limiting Bypass mediante Distribución de Requests
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/transactions/transacciones/ desde múltiples IPs coordinadas
**Vector de ataque:** Ataque distribuido desde múltiples direcciones IP
**Regla de seguridad evaluada:** Rate limiting debe considerar autenticación además de IP
**Condición de fallo:** Rate limit evadido mediante distribución, protección insuficiente
**Severidad:** Media

### 28. Acceso a Transacciones mediante SQL Injection en Filtros
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?id_cliente=1' OR '1'='1
**Vector de ataque:** Inyección SQL en parámetros de query string
**Regla de seguridad evaluada:** Django ORM debe prevenir SQL injection mediante parametrización
**Condición de fallo:** SQL ejecutado, datos no autorizados retornados, inyección exitosa
**Severidad:** Crítica

### 29. Acceso a Transacciones mediante NoSQL Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?estado[$ne]=pendiente
**Vector de ataque:** Inyección NoSQL en parámetros de filtro
**Regla de seguridad evaluada:** Serializers deben sanitizar parámetros antes de construir queries
**Condición de fallo:** Query malicioso ejecutado, datos filtrados incorrectamente
**Severidad:** Alta

### 30. Acceso mediante Path Traversal en ID
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/../../../admin/
**Vector de ataque:** Path traversal en parámetro de ruta
**Regla de seguridad evaluada:** Django URL routing debe validar formato de UUID
**Condición de fallo:** Acceso a ruta no autorizada, path traversal exitoso
**Severidad:** Alta

### 31. Acceso mediante Header Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/ con header X-Forwarded-Host: evil.com
**Vector de ataque:** Inyección de headers maliciosos para redirección o cache poisoning
**Regla de seguridad evaluada:** Aplicación debe validar y sanitizar headers
**Condición de fallo:** Redirección a dominio malicioso, headers inyectados procesados
**Severidad:** Media

### 32. Acceso mediante Parameter Pollution
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?id_cliente=1&id_cliente=2
**Vector de ataque:** Múltiples parámetros con mismo nombre para confundir lógica
**Regla de seguridad evaluada:** Serializers deben manejar parámetros duplicados correctamente
**Condición de fallo:** Comportamiento inesperado, lógica de filtrado comprometida
**Severidad:** Media

### 33. Acceso mediante Mass Assignment
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con campos no permitidos en payload
**Vector de ataque:** Usuario incluye campos como created_at, updated_at, id_transaccion en request
**Regla de seguridad evaluada:** Serializers deben usar Meta.fields explícito y rechazar campos extra
**Condición de fallo:** Campos protegidos modificados, mass assignment exitoso
**Severidad:** Alta

### 34. Acceso mediante JSON Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con payload JSON malicioso
**Vector de ataque:** Payload con caracteres de escape o estructuras JSON anidadas maliciosas
**Regla de seguridad evaluada:** Parsers JSON deben validar estructura y rechazar payloads maliciosos
**Condición de fallo:** JSON malicioso procesado, comportamiento inesperado
**Severidad:** Media

### 35. Acceso mediante XML External Entity (XXE)
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con Content-Type: application/xml y entidades externas
**Vector de ataque:** Payload XML con referencia a entidad externa para leer archivos del servidor
**Regla de seguridad evaluada:** Si XML está soportado, parser debe deshabilitar entidades externas
**Condición de fallo:** Archivos del servidor leídos, XXE exitoso
**Severidad:** Crítica

### 36. Acceso mediante Deserialización Insegura
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con payload pickle serializado
**Vector de ataque:** Payload con objeto pickle malicioso para ejecución de código
**Regla de seguridad evaluada:** Serializers deben usar formatos seguros y rechazar pickle
**Condición de fallo:** Código ejecutado en servidor, RCE (Remote Code Execution)
**Severidad:** Crítica

### 37. Acceso mediante Timing Attack en Validación de UUID
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/{uuid_válido} vs {uuid_inválido}
**Vector de ataque:** Medición de tiempo de respuesta para determinar existencia de transacciones
**Regla de seguridad evaluada:** Respuestas deben tener tiempos consistentes independiente de existencia
**Condición de fallo:** Tiempos diferentes revelan existencia, información leak mediante timing
**Severidad:** Media

### 38. Acceso mediante Error Message Information Disclosure
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/{uuid_inválido}/
**Vector de ataque:** Análisis de mensajes de error para obtener información del sistema
**Regla de seguridad evaluada:** Mensajes de error deben ser genéricos y no revelar detalles técnicos
**Condición de fallo:** Mensaje de error revela estructura de BD, versión de Django, queries SQL
**Severidad:** Media

### 39. Acceso mediante Stack Trace Information Disclosure
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con payload que causa excepción
**Vector de ataque:** Payload diseñado para generar excepción y exponer stack trace
**Regla de seguridad evaluada:** DEBUG=False debe ocultar stack traces en producción
**Condición de fallo:** Stack trace expuesto con rutas de archivos, código fuente, configuración
**Severidad:** Alta

### 40. Acceso mediante Verbose Error Messages
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/transactions/transacciones/ con datos inválidos
**Vector de ataque:** Análisis de mensajes de error detallados para mapear validaciones
**Regla de seguridad evaluada:** Mensajes de error deben ser genéricos para usuarios no autenticados
**Condición de fallo:** Mensajes detallados revelan estructura de modelo, campos requeridos, constraints
**Severidad:** Baja

### 41. Acceso mediante Session Hijacking mediante XSS
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Campo de transacción con payload XSS almacenado y ejecutado
**Vector de ataque:** Payload JavaScript en campo de texto que roba sessionid cuando se visualiza
**Regla de seguridad evaluada:** Output encoding debe prevenir ejecución de scripts, CSP debe bloquear inline scripts
**Condición de fallo:** JavaScript ejecutado, sessionid robado, sesión comprometida
**Severidad:** Crítica

### 42. Acceso mediante Stored XSS en Nombre de Cliente
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/clientes/ con nombre=<script>malicious</script>
**Vector de ataque:** Payload XSS almacenado en nombre de cliente y ejecutado en listados
**Regla de seguridad evaluada:** Sanitización de entrada y output encoding deben prevenir XSS
**Condición de fallo:** Script ejecutado al visualizar cliente, XSS persistente exitoso
**Severidad:** Alta

### 43. Acceso mediante Reflected XSS en Parámetros de Búsqueda
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?search=<script>alert(1)</script>
**Vector de ataque:** Payload XSS reflejado en respuesta sin sanitización
**Regla de seguridad evaluada:** Output encoding debe sanitizar parámetros reflejados en respuesta
**Condición de fallo:** Script ejecutado en respuesta, XSS reflejado exitoso
**Severidad:** Alta

### 44. Acceso mediante DOM-based XSS
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Frontend que procesa parámetros URL con JavaScript sin sanitización
**Vector de ataque:** Payload JavaScript en URL procesado por código del lado cliente
**Regla de seguridad evaluada:** Frontend debe sanitizar entrada antes de manipular DOM
**Condición de fallo:** Script ejecutado en contexto del usuario, DOM XSS exitoso
**Severidad:** Alta

### 45. Acceso mediante Clickjacking en Formularios de Transacción
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Página maliciosa con iframe transparente sobre formulario de transacción
**Vector de ataque:** Atacante superpone iframe transparente para hacer click en acciones no autorizadas
**Regla de seguridad evaluada:** X-Frame-Options: DENY debe prevenir embedding en iframes
**Condición de fallo:** Formulario embebido en iframe, clickjacking exitoso
**Severidad:** Media

### 46. Acceso mediante Open Redirect en Parámetros de URL
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?redirect=https://evil.com
**Vector de ataque:** Parámetro redirect usado para redirigir a dominio malicioso después de acción
**Regla de seguridad evaluada:** Redirecciones deben validar dominio y usar whitelist
**Condición de fallo:** Redirección a dominio malicioso, open redirect exitoso
**Severidad:** Media

### 47. Acceso mediante HTTP Parameter Pollution en Filtros
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?estado=pendiente&estado=completada
**Vector de ataque:** Múltiples valores para mismo parámetro para confundir lógica de filtrado
**Regla de seguridad evaluada:** Serializers deben manejar parámetros duplicados y usar último valor
**Condición de fallo:** Comportamiento inesperado, filtrado comprometido
**Severidad:** Baja

### 48. Acceso mediante Insecure Direct Object Reference (IDOR) en Cliente
**Rol involucrado:** tecnico de Empresa A
**Recurso objetivo:** GET /api/transactions/clientes/{id_cliente_empresa_b}/
**Vector de ataque:** Usuario accede directamente a recurso de otra empresa usando ID conocido
**Regla de seguridad evaluada:** Filtrado por Company debe prevenir acceso cross-tenant
**Condición de fallo:** Cliente de otra empresa retornado, IDOR exitoso
**Severidad:** Crítica

### 49. Acceso mediante Insecure Direct Object Reference (IDOR) en Transacción
**Rol involucrado:** tecnico
**Recurso objetivo:** GET /api/transactions/transacciones/{id_transaccion_no_autorizada}/
**Vector de ataque:** Usuario accede a transacción fuera de su scope usando ID conocido
**Regla de seguridad evaluada:** Validación de autorización debe verificar pertenencia antes de retornar
**Condición de fallo:** Transacción no autorizada retornada, IDOR exitoso
**Severidad:** Crítica

### 50. Acceso mediante Horizontal Privilege Escalation
**Rol involucrado:** tecnico A
**Recurso objetivo:** GET /api/transactions/transacciones/{id_transaccion_tecnico_b}/
**Vector de ataque:** Usuario accede a transacciones de otro usuario del mismo rol y empresa
**Regla de seguridad evaluada:** Filtrado debe restringir acceso a transacciones propias si aplica
**Condición de fallo:** Transacciones de otro usuario retornadas, escalamiento horizontal exitoso
**Severidad:** Alta

### 51. Acceso mediante Vertical Privilege Escalation
**Rol involucrado:** tecnico
**Recurso objetivo:** DELETE /api/transactions/transacciones/{id_transaccion}/
**Vector de ataque:** Usuario con rol limitado intenta operación restringida a roles superiores
**Regla de seguridad evaluada:** AccessPolicyPermission debe evaluar políticas y rechazar según rol
**Condición de fallo:** Operación restringida permitida, escalamiento vertical exitoso
**Severidad:** Crítica

### 52. Acceso mediante Bypass de Validación de Políticas ABAC
**Rol involucrado:** tecnico
**Recurso objetivo:** POST /api/transactions/transacciones/ con acción que requiere supervisor
**Vector de ataque:** Usuario intenta acción restringida cuando política ABAC debería rechazar
**Regla de seguridad evaluada:** evaluate_access_policy debe evaluar condiciones y aplicar efecto deny
**Condición de fallo:** Acción permitida cuando debería ser denegada, política ABAC bypassed
**Severidad:** Crítica

### 53. Acceso mediante Manipulación de Condiciones en AccessPolicy
**Rol involucrado:** admin_empresa
**Recurso objetivo:** PATCH /api/accounts/policies/{policy_id}/ modificando condiciones
**Vector de ataque:** Admin modifica condiciones de política para otorgar acceso indebido
**Regla de seguridad evaluada:** Validación de políticas debe prevenir condiciones que otorguen acceso excesivo
**Condición de fallo:** Política modificada con condiciones que otorgan acceso indebido, validación fallida
**Severidad:** Alta

### 54. Acceso mediante Prioridad de Políticas Manipulada
**Rol involucrado:** admin_empresa
**Recurso objetivo:** PATCH /api/accounts/policies/{policy_id}/ con priority muy alto
**Vector de ataque:** Admin establece prioridad alta en política deny para sobrescribir allow
**Regla de seguridad evaluada:** Sistema debe validar que políticas deny tengan prioridad sobre allow
**Condición de fallo:** Política deny con prioridad alta bloquea acceso legítimo, lógica de prioridad incorrecta
**Severidad:** Media

### 55. Acceso mediante Política Inactiva Reactivada
**Rol involucrado:** admin_empresa
**Recurso objetivo:** PATCH /api/accounts/policies/{policy_id}/ con is_active=True
**Vector de ataque:** Admin reactiva política que debería permanecer inactiva
**Regla de seguridad evaluada:** Reactivación de políticas debe requerir validación adicional
**Condición de fallo:** Política peligrosa reactivada sin validación, seguridad comprometida
**Severidad:** Media

### 56. Acceso mediante Bypass de MFA
**Rol involucrado:** tecnico con MFA requerido
**Recurso objetivo:** POST /api/transactions/transacciones/ sin completar MFA
**Vector de ataque:** Usuario intenta acceder a recurso protegido sin verificación MFA
**Regla de seguridad evaluada:** OTPMiddleware debe requerir MFA para usuarios configurados
**Condición de fallo:** Acceso concedido sin MFA, protección MFA bypassed
**Severidad:** Crítica

### 57. Acceso mediante MFA Token Reutilizado
**Rol involucrado:** tecnico con MFA
**Recurso objetivo:** POST /api/transactions/transacciones/ con mismo token OTP múltiples veces
**Vector de ataque:** Usuario reutiliza token OTP ya consumido
**Regla de seguridad evaluada:** Tokens OTP deben ser de un solo uso (one-time)
**Condición de fallo:** Token reutilizado exitosamente, MFA comprometido
**Severidad:** Crítica

### 58. Acceso mediante MFA Token de Otro Usuario
**Rol involucrado:** tecnico A
**Recurso objetivo:** POST /api/transactions/transacciones/ con token OTP de tecnico B
**Vector de ataque:** Usuario utiliza token OTP generado para otro usuario
**Regla de seguridad evaluada:** Tokens OTP deben estar vinculados al usuario específico
**Condición de fallo:** Token de otro usuario aceptado, autenticación comprometida
**Severidad:** Crítica

### 59. Acceso mediante MFA Token Expirado
**Rol involucrado:** tecnico con MFA
**Recurso objetivo:** POST /api/transactions/transacciones/ con token OTP que excedió tiempo de validez
**Vector de ataque:** Usuario utiliza token OTP después de ventana de tiempo permitida
**Regla de seguridad evaluada:** Tokens OTP deben tener expiración y validarse contra tiempo actual
**Condición de fallo:** Token expirado aceptado, expiración no aplicada
**Severidad:** Alta

### 60. Acceso mediante Brute Force de Credenciales
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/auth/login/ con múltiples combinaciones usuario/password
**Vector de ataque:** Ataque de fuerza bruta con diccionario de contraseñas comunes
**Regla de seguridad evaluada:** Rate limiting y bloqueo de cuenta después de intentos fallidos
**Condición de fallo:** Múltiples intentos permitidos sin bloqueo, cuenta comprometida
**Severidad:** Crítica

### 61. Acceso mediante Credential Stuffing
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/auth/login/ con credenciales de breach de otra plataforma
**Vector de ataque:** Uso de credenciales filtradas de otros servicios con mismo usuario/password
**Regla de seguridad evaluada:** Sistema debe detectar patrones de credential stuffing y bloquear
**Condición de fallo:** Credenciales reutilizadas aceptadas, cuenta comprometida
**Severidad:** Alta

### 62. Acceso mediante Password en Texto Plano en Logs
**Rol involucrado:** tecnico
**Recurso objetivo:** POST /api/auth/login/ con password
**Vector de ataque:** Análisis de logs del servidor para encontrar passwords en texto plano
**Regla de seguridad evaluada:** Logs no deben contener passwords, solo hashes deben almacenarse
**Condición de fallo:** Password encontrado en logs, información sensible expuesta
**Severidad:** Crítica

### 63. Acceso mediante Hash de Password Débil
**Rol involucrado:** admin_empresa
**Recurso objetivo:** Creación de usuario con password débil
**Vector de ataque:** Password hashado con algoritmo débil susceptible a rainbow tables
**Regla de seguridad evaluada:** Django debe usar PBKDF2 o Argon2, no MD5 o SHA1
**Condición de fallo:** Hash débil almacenado, password recuperable mediante rainbow tables
**Severidad:** Crítica

### 64. Acceso mediante Password sin Salt
**Rol involucrado:** admin_empresa
**Recurso objetivo:** Creación de usuario con password
**Vector de ataque:** Passwords hashados sin salt único por usuario
**Regla de seguridad evaluada:** Django debe usar salt único por password
**Condición de fallo:** Hash sin salt almacenado, passwords idénticos tienen mismo hash
**Severidad:** Crítica

### 65. Acceso mediante Session Fixation en Logout
**Rol involucrado:** tecnico
**Recurso objetivo:** POST /api/auth/logout/ sin regenerar sessionid
**Vector de ataque:** Sessionid no se regenera después de logout, permitiendo reutilización
**Regla de seguridad evaluada:** Logout debe invalidar y regenerar sessionid
**Condición de fallo:** Sessionid reutilizable después de logout, sesión no invalidada completamente
**Severidad:** Alta

### 66. Acceso mediante Session no Invalidada en Cambio de Password
**Rol involucrado:** tecnico
**Recurso objetivo:** Cambio de password sin invalidar sesiones existentes
**Vector de ataque:** Sesiones activas permanecen válidas después de cambio de password
**Regla de seguridad evaluada:** Cambio de password debe invalidar todas las sesiones excepto la actual
**Condición de fallo:** Sesiones antiguas válidas después de cambio, seguridad comprometida
**Severidad:** Alta

### 67. Acceso mediante Session no Invalidada en Cambio de Rol
**Rol involucrado:** admin_empresa
**Recurso objetivo:** Cambio de rol de usuario sin invalidar sesiones existentes
**Vector de ataque:** Sesiones activas mantienen privilegios antiguos después de cambio de rol
**Regla de seguridad evaluada:** Cambio de rol debe invalidar sesiones para aplicar nuevos permisos
**Condición de fallo:** Sesiones con privilegios antiguos válidas, escalamiento de privilegios persistente
**Severidad:** Crítica

### 68. Acceso mediante Cookie sin HttpOnly
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Análisis de cookies de sesión
**Vector de ataque:** JavaScript accede a sessionid si cookie no tiene flag HttpOnly
**Regla de seguridad evaluada:** SESSION_COOKIE_HTTPONLY debe ser True para prevenir acceso vía JavaScript
**Condición de fallo:** JavaScript accede a sessionid, cookie comprometida mediante XSS
**Severidad:** Crítica

### 69. Acceso mediante Cookie sin Secure Flag en HTTPS
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Transmisión de cookies en canal no cifrado
**Vector de ataque:** Cookie sessionid transmitida en HTTP permitiendo interceptación
**Regla de seguridad evaluada:** SESSION_COOKIE_SECURE debe ser True en producción con HTTPS
**Condición de fallo:** Cookie transmitida en texto plano, sesión interceptable mediante MITM
**Severidad:** Crítica

### 70. Acceso mediante Cookie sin SameSite
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Request cross-site con cookies
**Vector de ataque:** CSRF mediante request desde dominio externo con cookies de sesión
**Regla de seguridad evaluada:** SESSION_COOKIE_SAMESITE debe ser Lax o Strict
**Condición de fallo:** Cookies enviadas en requests cross-site, CSRF facilitado
**Severidad:** Alta

### 71. Acceso mediante CORS Mal Configurado
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/ desde dominio externo
**Vector de ataque:** Request desde dominio malicioso con CORS permitido para cualquier origen
**Regla de seguridad evaluada:** CORS debe restringir orígenes permitidos, no usar Access-Control-Allow-Origin: *
**Condición de fallo:** Datos accesibles desde dominio externo, CORS mal configurado
**Severidad:** Crítica

### 72. Acceso mediante CORS con Credenciales desde Origen No Autorizado
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/ desde evil.com con credentials
**Vector de ataque:** Request cross-origin con cookies desde dominio no autorizado
**Regla de seguridad evaluada:** CORS debe validar origen antes de permitir credentials
**Condición de fallo:** Credenciales enviadas desde dominio no autorizado, sesión comprometida
**Severidad:** Crítica

### 73. Acceso mediante Missing Security Headers
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/ análisis de headers de respuesta
**Vector de ataque:** Análisis de headers de seguridad faltantes para identificar vulnerabilidades
**Regla de seguridad evaluada:** SecurityHeadersMiddleware debe incluir X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
**Condición de fallo:** Headers de seguridad faltantes, protección reducida
**Severidad:** Media

### 74. Acceso mediante Content Security Policy (CSP) Débil
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Página con formulario de transacción
**Vector de ataque:** CSP con 'unsafe-inline' o 'unsafe-eval' permite ejecución de scripts
**Regla de seguridad evaluada:** CSP debe restringir scripts a sources específicos, no usar unsafe-*
**Condición de fallo:** Scripts inline ejecutados, CSP bypassed, XSS facilitado
**Severidad:** Alta

### 75. Acceso mediante Information Disclosure en Headers
**Rol involucrado:** anonymous
**Recurso objetivo:** GET /api/transactions/transacciones/ análisis de headers de respuesta
**Vector de ataque:** Headers como X-Powered-By, Server revelan información del stack tecnológico
**Regla de seguridad evaluada:** Headers no deben revelar versión de servidor, framework, o tecnología
**Condición de fallo:** Información técnica expuesta, fingerprinting facilitado
**Severidad:** Baja

### 76. Acceso mediante Missing Input Validation
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con monto excediendo max_digits
**Vector de ataque:** Input sin validación permite valores fuera de rango esperado
**Regla de seguridad evaluada:** Serializers deben validar formato, tipo, y rango de todos los campos
**Condición de fallo:** Valores inválidos aceptados, validación bypassed
**Severidad:** Alta

### 77. Acceso mediante Missing Output Encoding
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/ con datos sin encoding
**Vector de ataque:** Datos retornados sin encoding permiten XSS si renderizados en frontend
**Regla de seguridad evaluada:** Output debe ser encoded según contexto (HTML, JavaScript, URL)
**Condición de fallo:** Datos sin encoding retornados, XSS facilitado
**Severidad:** Alta

### 78. Acceso mediante Missing Authorization Check en Endpoint
**Rol involucrado:** tecnico
**Recurso objetivo:** GET /api/transactions/transacciones/{id}/ sin verificación de pertenencia
**Vector de ataque:** Endpoint retorna datos sin verificar que pertenecen al usuario/empresa
**Regla de seguridad evaluada:** Views deben verificar autorización a nivel de objeto además de permiso general
**Condición de fallo:** Datos no autorizados retornados, autorización insuficiente
**Severidad:** Crítica

### 79. Acceso mediante Missing Rate Limiting en Login
**Rol involucrado:** anonymous
**Recurso objetivo:** POST /api/auth/login/ con múltiples intentos sin límite
**Vector de ataque:** Ataque de fuerza bruta sin restricción de velocidad
**Regla de seguridad evaluada:** Rate limiting debe aplicarse a endpoints de autenticación
**Condición de fallo:** Múltiples intentos sin bloqueo, brute force facilitado
**Severidad:** Crítica

### 80. Acceso mediante Missing Rate Limiting en Creación de Transacciones
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ con múltiples requests simultáneos
**Vector de ataque:** Creación masiva de transacciones sin límite de velocidad
**Regla de seguridad evaluada:** Rate limiting debe prevenir abuso de recursos
**Condición de fallo:** Múltiples transacciones creadas rápidamente, DoS o abuso de recursos
**Severidad:** Media

### 81. Acceso mediante Missing Audit Logging
**Rol involucrado:** admin_empresa
**Recurso objetivo:** DELETE /api/transactions/transacciones/{id}/
**Vector de ataque:** Eliminación de transacciones sin registro en logs de auditoría
**Regla de seguridad evaluada:** Operaciones críticas deben registrarse en audit log
**Condición de fallo:** Eliminación no registrada, trazabilidad perdida
**Severidad:** Alta

### 82. Acceso mediante Audit Log Tampering
**Rol involucrado:** admin_empresa
**Recurso objetivo:** Modificación de registros en AuditLog después de acción
**Vector de ataque:** Usuario modifica logs de auditoría para ocultar acciones maliciosas
**Regla de seguridad evaluada:** Audit logs deben ser inmutables y solo append-only
**Condición de fallo:** Logs modificados o eliminados, evidencia de acciones comprometida
**Severidad:** Crítica

### 83. Acceso mediante Missing IP Logging en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de IP
**Vector de ataque:** Acciones maliciosas sin registro de origen IP
**Regla de seguridad evaluada:** Audit logs deben incluir IP address del cliente
**Condición de fallo:** IP no registrada, origen de acciones no trazable
**Severidad:** Alta

### 84. Acceso mediante Missing User Agent Logging
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de user agent
**Vector de ataque:** Acciones sin registro de dispositivo/navegador utilizado
**Regla de seguridad evaluada:** Audit logs deben incluir user agent para trazabilidad
**Condición de fallo:** User agent no registrado, contexto de acción perdido
**Severidad:** Media

### 85. Acceso mediante Missing Timestamp en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin timestamp preciso
**Vector de ataque:** Acciones sin registro de tiempo exacto de ejecución
**Regla de seguridad evaluada:** Audit logs deben incluir timestamp con precisión de milisegundos
**Condición de fallo:** Timestamp impreciso o faltante, secuencia de eventos no determinable
**Severidad:** Media

### 86. Acceso mediante Missing Before/After Values en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** PATCH /api/transactions/transacciones/{id}/ sin registro de valores anteriores
**Vector de ataque:** Modificaciones sin registro de estado anterior y nuevo
**Regla de seguridad evaluada:** Audit logs deben incluir valores before y after para cambios
**Condición de fallo:** Valores anteriores no registrados, cambios no auditables
**Severidad:** Alta

### 87. Acceso mediante Missing Entity ID en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de id_transaccion creado
**Vector de ataque:** Creación de recursos sin registro de identificador en audit log
**Regla de seguridad evaluada:** Audit logs deben incluir entity_id del recurso afectado
**Condición de fallo:** ID de recurso no registrado, correlación de eventos imposible
**Severidad:** Alta

### 88. Acceso mediante Missing Action Type en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de tipo de acción
**Vector de ataque:** Acciones sin clasificación de tipo (create, update, delete)
**Regla de seguridad evaluada:** Audit logs deben incluir action type para categorización
**Condición de fallo:** Tipo de acción no registrado, análisis de auditoría dificultado
**Severidad:** Media

### 89. Acceso mediante Missing Company Context en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de company
**Vector de ataque:** Acciones sin registro de contexto de empresa en multi-tenancy
**Regla de seguridad evaluada:** Audit logs deben incluir company_id para trazabilidad multi-tenant
**Condición de fallo:** Company no registrada, contexto multi-tenant perdido
**Severidad:** Alta

### 90. Acceso mediante Missing Actor Information en Audit
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/transacciones/ sin registro de usuario ejecutor
**Vector de ataque:** Acciones sin registro de usuario que las ejecutó
**Regla de seguridad evaluada:** Audit logs deben incluir actor (user_id) para responsabilidad
**Condición de fallo:** Usuario no registrado, responsabilidad de acciones no asignable
**Severidad:** Crítica

### 91. Acceso mediante SQL Injection en Filtros de Búsqueda
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?search=1' UNION SELECT password FROM auth_user--
**Vector de ataque:** Inyección SQL en parámetro de búsqueda para extraer datos de otras tablas
**Regla de seguridad evaluada:** Django ORM debe usar parametrización, no concatenación de strings
**Condición de fallo:** SQL malicioso ejecutado, datos de otras tablas extraídos
**Severidad:** Crítica

### 92. Acceso mediante Command Injection en Campos de Texto
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** POST /api/transactions/clientes/ con nombre=test; rm -rf /
**Vector de ataque:** Inyección de comandos del sistema operativo en campos de texto
**Regla de seguridad evaluada:** Input debe ser sanitizado antes de uso en comandos del sistema
**Condición de fallo:** Comando del sistema ejecutado, RCE exitoso
**Severidad:** Crítica

### 93. Acceso mediante LDAP Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Búsqueda de usuarios con parámetros LDAP maliciosos
**Vector de ataque:** Inyección LDAP en parámetros de búsqueda si se usa LDAP para autenticación
**Regla de seguridad evaluada:** Parámetros LDAP deben ser escapados antes de construcción de query
**Condición de fallo:** Query LDAP maliciosa ejecutada, datos no autorizados retornados
**Severidad:** Alta

### 94. Acceso mediante XPath Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Búsqueda con parámetros XPath maliciosos si se usa XML
**Vector de ataque:** Inyección XPath en consultas XML para acceso no autorizado
**Regla de seguridad evaluada:** Parámetros XPath deben ser sanitizados antes de construcción de query
**Condición de fallo:** XPath malicioso ejecutado, datos filtrados incorrectamente
**Severidad:** Media

### 95. Acceso mediante Template Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Campo de texto con sintaxis de template engine
**Vector de ataque:** Inyección de código de template en campos que se renderizan
**Regla de seguridad evaluada:** Templates deben usar auto-escaping y no ejecutar código arbitrario
**Condición de fallo:** Código de template ejecutado, SSTI (Server-Side Template Injection) exitoso
**Severidad:** Crítica

### 96. Acceso mediante Expression Language Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** Campo con expresión de lenguaje de evaluación
**Vector de ataque:** Inyección de expresiones evaluables en campos procesados
**Regla de seguridad evaluada:** Evaluación de expresiones debe usar sandbox y whitelist de funciones
**Condición de fallo:** Expresión maliciosa evaluada, código ejecutado
**Severidad:** Crítica

### 97. Acceso mediante Insecure Random en Generación de UUID
**Rol involucrado:** sistema
**Recurso objetivo:** Generación de id_transaccion con generador predecible
**Vector de ataque:** UUIDs generados con algoritmo débil permiten predicción de IDs
**Regla de seguridad evaluada:** UUIDs deben usar uuid.uuid4() con generador criptográficamente seguro
**Condición de fallo:** UUIDs predecibles, enumeración de recursos facilitada
**Severidad:** Alta

### 98. Acceso mediante Enumeration de IDs Secuenciales
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/1, /2, /3...
**Vector de ataque:** IDs secuenciales permiten enumeración de todos los recursos
**Regla de seguridad evaluada:** IDs deben ser UUIDs no secuenciales para prevenir enumeración
**Condición de fallo:** IDs secuenciales permiten enumeración completa, recursos expuestos
**Severidad:** Alta

### 99. Acceso mediante Time-based Blind SQL Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?id=1' AND SLEEP(5)--
**Vector de ataque:** Inyección SQL que usa delays para extraer información sin respuesta visible
**Regla de seguridad evaluada:** Django ORM debe prevenir cualquier SQL injection mediante parametrización
**Condición de fallo:** Delay observado confirma inyección SQL, información extraída mediante timing
**Severidad:** Crítica

### 100. Acceso mediante Boolean-based Blind SQL Injection
**Rol involucrado:** tecnico autenticado
**Recurso objetivo:** GET /api/transactions/transacciones/?id=1' AND 1=1-- vs 1' AND 1=2--
**Vector de ataque:** Inyección SQL que usa diferencias en respuestas booleanas para extraer datos
**Regla de seguridad evaluada:** Django ORM debe prevenir SQL injection, respuestas deben ser consistentes
**Condición de fallo:** Respuestas diferentes revelan información, blind SQL injection exitoso
**Severidad:** Crítica
