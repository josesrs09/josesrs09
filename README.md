# Blueprint de Implementación Empresarial
## Sistema Web de Facturación Electrónica (DGII, República Dominicana)

> Stack objetivo: **Angular + PHP 7.3 + MySQL + API REST JSON**.
>
> En todo tema fiscal/DGII, aplicar: **"validar con normativa vigente DGII y/o contador fiscal"**.

---

## Implementación base incluida en este repositorio

Además del blueprint, este repositorio ahora incluye una base inicial de implementación:

- `backend/`: API REST en PHP 7.3 con rutas funcionales de `auth`, `customers` y `ecf`.
- `frontend/`: estructura Angular-style modular con servicios para consumir la API.

### Ejecución rápida backend

```bash
php -S 0.0.0.0:8080 -t backend/public
```


## 1) Resumen ejecutivo

Este documento define un diseño completo para construir una plataforma empresarial modular orientada a operación continua:

- Facturación Electrónica (e-CF 31, 32, 33, 34, 46, 47)
- Contabilidad
- Bancos
- Ventas
- Cuentas por Cobrar (CxC)
- Cuentas por Pagar (CxP)
- Inventarios
- Portal de clientes
- Reportes fiscales 606, 607 y 608
- Asistentes inteligentes + wizard de configuración

### Capacidad operativa inicial requerida

- 2 almacenes
- 2 usuarios internos + usuario de contador por Red ACSN
- 500 transacciones mensuales
- listas de precios ilimitadas
- multimoneda ilimitada
- portal de clientes
- reportes 606, 607, 608

### Objetivo de negocio

Maximizar productividad y control documental con trazabilidad integral (funcional, técnica y fiscal), reduciendo errores operativos y de cumplimiento.

---

## 2) Arquitectura general

## 2.1 Estilo arquitectónico

- **Frontend (Angular)**: SPA modular, lazy loading, guards, interceptors, formularios reactivos.
- **Backend (PHP 7.3)**: arquitectura por capas (`Controller -> Service -> Repository`), validación centralizada, manejo uniforme de errores.
- **MySQL**: modelo normalizado, índices para consultas críticas, control transaccional y auditoría.
- **Integración DGII**: orquestador de validación, envío, consulta de estatus y reintentos.

## 2.2 Componentes transversales

- Seguridad RBAC + JWT access/refresh
- Auditoría de cambios y acciones
- Motor de validación (técnica / negocio / fiscal / estructural)
- Cola de procesos (reintentos DGII, notificaciones)
- Observabilidad (logs técnicos + funcionales)

## 2.3 Flujo macro de documento fiscal

1. Captura documento (ventas/compras)
2. Validación de formulario y negocio
3. Validación fiscal previa
4. Construcción payload e-CF
5. Validación estructural (XSD / reglas)
6. Envío a DGII
7. Recepción de respuesta / polling de estado
8. Actualización estado + trazabilidad + impactos contables

---

## 3) Mapa de módulos

1. Seguridad, acceso y administración  
2. Empresas, sucursales y parámetros generales  
3. Clientes y portal de clientes  
4. Proveedores y compras  
5. Productos, servicios e inventarios  
6. Ventas y facturación  
7. Facturación Electrónica DGII  
8. Guías integradas y asistente normativo  
9. Asistente de Configuración Inteligente  
10. Wizard de primera configuración  
11. Contabilidad  
12. Bancos  
13. Cuentas por Cobrar  
14. Cuentas por Pagar  
15. Reportes fiscales 606, 607 y 608  
16. Dashboard inteligente  
17. Logs, auditoría y monitoreo

---

## 4) Modelo general de datos

## 4.1 Maestros

- `companies`, `branches`, `warehouses`
- `users`, `roles`, `permissions`, `user_roles`, `role_permissions`
- `customers`, `suppliers`
- `products`, `services`, `product_categories`, `units`
- `price_lists`, `price_list_details`
- `currencies`, `exchange_rates`
- `taxes`, `tax_groups`
- `fiscal_sequences`, `fiscal_parameters`
- `chart_of_accounts`

## 4.2 Transaccionales

- Ventas: `quotes`, `orders`, `sales_invoices`, `sales_invoice_items`, `credit_notes`, `debit_notes`
- Compras: `purchase_invoices`, `purchase_invoice_items`
- Inventario: `inventory_moves`, `inventory_balances`, `kardex`
- CxC/CxP: `ar_documents`, `ar_receipts`, `ap_documents`, `ap_payments`
- Bancos: `bank_accounts`, `bank_transactions`, `bank_reconciliations`
- Contabilidad: `journal_entries`, `journal_lines`

## 4.3 Fiscal/e-CF y auditoría

- `ecf_documents`, `ecf_versions`, `ecf_validation_runs`, `ecf_submissions`, `ecf_responses`
- `fiscal_606_runs`, `fiscal_607_runs`, `fiscal_608_runs`
- `audit_logs`, `access_logs`, `error_logs`, `integration_logs`

---

## 5) Convenciones API REST

- Base path: `/api/v1`
- Formato estándar:

```json
{
  "success": true,
  "data": {},
  "errors": [],
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-03-12T10:00:00Z"
  }
}
```

- HTTP status recomendado: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `422`, `500`
- Idempotencia para POST críticos: encabezado `Idempotency-Key`

---

# 6) Desarrollo completo por módulos

## Módulo 1. Seguridad, acceso y administración

### Objetivo
Asegurar acceso controlado, sesión segura y administración de identidad con trazabilidad.

### Alcance
Login, recuperación de acceso, sesiones, roles, permisos, perfiles, bloqueo por intentos, control por menú/acción, acceso contador por Red ACSN.

### Submódulos
- Autenticación
- Autorización RBAC
- Usuarios y perfiles
- Políticas de sesión
- Auditoría de acceso

### Casos de uso
- Iniciar/cerrar sesión
- Restablecer contraseña
- Crear usuario y asignar rol
- Bloquear/desbloquear usuario
- Permitir acceso por rango IP ACSN para contador

### Roles involucrados
- Superadmin
- Administrador
- Facturador
- Contador
- Auditor

### Flujo funcional paso a paso
1. Usuario envía credenciales.
2. API valida identidad y estado.
3. Se emite JWT access + refresh.
4. Frontend guarda token seguro.
5. Guards habilitan rutas según permisos.

### Reglas de negocio
- **Regla interna:** 5 intentos fallidos => bloqueo 15 min.
- **Regla interna:** contraseña debe cambiarse cada 90 días (parametrizable).

### Validaciones
- **Validación técnica:** formato usuario/email, hash de contraseña, expiración token.
- **Validación fiscal:** N/A.
- **Validación de permisos:** endpoint + acción de UI.

### Diseño UI/UX
- Pantalla login simple con mensajes claros.
- Gestión de usuarios con tabla filtrable, estado visible y acciones rápidas.
- Matriz de permisos por módulo/acción.

### Componentes Angular
- `login-page`, `forgot-password-page`, `users-page`, `roles-page`, `permissions-matrix`

### Servicios Angular
- `auth.service.ts`, `user-admin.service.ts`, `rbac.service.ts`

### Rutas Angular
- `/auth/login`
- `/admin/users`
- `/admin/roles`

### Controladores PHP
- `AuthController`
- `UserController`
- `RoleController`

### Servicios/capa lógica PHP
- `AuthService`, `SessionService`, `RbacService`, `PasswordPolicyService`

### Modelo MySQL
- `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `sessions`, `access_logs`

### Relación entidades
- `users` N:M `roles`
- `roles` N:M `permissions`

### Endpoints REST
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /users`, `POST /users`, `PUT /users/{id}`

### JSON de ejemplo
```json
{
  "request": {"username": "admin@empresa.com", "password": "<SECRET>"},
  "response_ok": {"success": true, "data": {"access_token": "jwt", "refresh_token": "rjwt", "expires_in": 900}},
  "response_error": {"success": false, "errors": [{"type": "technical", "code": "AUTH_INVALID", "message": "Credenciales inválidas"}]},
  "campos": "username: correo o usuario; password: credencial"
}
```

### Manejo de errores
- Errores autenticación: `AUTH_INVALID`, `ACCOUNT_LOCKED`
- Errores autorización: `FORBIDDEN_ACTION`

### Permisos y seguridad
- JWT + refresh rotativo
- Contraseña con bcrypt
- Restricción IP ACSN para perfil contador (opcional por política)

### Auditoría
- Log de login, logout, cambios de contraseña, cambios de rol

### Pruebas sugeridas
- Unit test `AuthService`
- Integración login/refresh
- Prueba fuerza bruta

### Riesgos
- Exceso de privilegios
- Configuración débil de sesiones

### Buenas prácticas
- Principio de mínimo privilegio
- Deshabilitar usuarios inactivos

### Posibles mejoras futuras
- MFA obligatorio por rol
- SSO empresarial

---

## Módulo 2. Empresas, sucursales y parámetros generales

### Objetivo
Consolidar configuración base operativa y fiscal por empresa/sucursal.

### Alcance
Datos empresa, sucursales, información fiscal, secuencias, impuestos, monedas, tasas, listas de precios, formatos, parámetros e-CF.

### Submódulos
- Empresa y sucursales
- Fiscal y secuencias
- Catálogos financieros
- Parámetros por sucursal

### Casos de uso
- Crear empresa y sucursal
- Configurar secuencia por tipo e-CF
- Definir monedas y tipos de cambio

### Roles involucrados
- Administrador
- Contador

### Flujo funcional
1. Registrar datos de empresa
2. Crear sucursales
3. Configurar fiscalidad y secuencias
4. Publicar parámetros globales

### Reglas de negocio
- **Regla interna:** secuencia única por sucursal + tipo e-CF.

### Validaciones
- **Técnica:** RNC único, tasa de cambio > 0, moneda válida.
- **Fiscal:** secuencia autorizada y vigente (validar con normativa vigente DGII y/o contador fiscal).

### UI/UX
- Pantalla tipo tabs: Empresa, Fiscal, Monedas, Impuestos, Secuencias.

### Angular
- Componentes: `company-form`, `branches-grid`, `tax-setup`, `currency-rate-form`, `sequence-form`
- Servicio: `settings.service.ts`
- Rutas: `/settings/company`, `/settings/fiscal`

### PHP
- `CompanyController`, `BranchController`, `FiscalConfigController`
- `CompanyService`, `FiscalService`

### MySQL
- `companies`, `branches`, `taxes`, `currencies`, `exchange_rates`, `fiscal_sequences`, `price_lists`

### API REST
- `POST /companies`
- `POST /branches`
- `POST /fiscal/sequences`

### JSON ejemplo
```json
{
  "request": {"company_name": "Mi Empresa SRL", "rnc": "101010101", "base_currency": "DOP"},
  "response_ok": {"success": true, "data": {"company_id": 1}},
  "response_error": {"success": false, "errors": [{"type": "business", "code": "RNC_DUPLICATE", "message": "RNC ya existe"}]},
  "campos": "rnc: identificación fiscal; base_currency: moneda base"
}
```

### Seguridad/Auditoría/Pruebas/Riesgos/Mejoras
Permisos admin/contador, auditoría de parámetros críticos, pruebas de secuencias, riesgo de parametrización incorrecta, mejoras con versionado de configuración.

---

## Módulo 3. Clientes y portal de clientes

### Objetivo
Administrar clientes y habilitar autoservicio documental y financiero.

### Alcance
Ficha fiscal, crédito, condiciones de pago, historial, portal, descarga de facturas, consulta de balances.

### Submódulos
- Maestro clientes
- Crédito y cobranza comercial
- Portal de clientes

### Casos de uso
- Crear cliente
- Consultar documentos
- Descargar e-CF/PDF

### Reglas de negocio
- **Regla interna:** no facturar crédito si excede límite.

### Validaciones
- **Técnica:** email/teléfono/RNC
- **Fiscal:** datos requeridos para e-CF según tipo

### UI/UX
- Ficha 360 con tabs: generales, fiscal, crédito, historial, documentos.

### Angular/PHP/MySQL/API
- Angular: `customers.module`, `portal.module`
- PHP: `CustomerController`, `PortalController`
- MySQL: `customers`, `customer_contacts`, `customer_portal_users`
- API: `POST /customers`, `GET /portal/documents`

### JSON
```json
{
  "request": {"name": "Cliente A", "tax_id": "131313131", "credit_limit": 150000, "currency_codes": ["DOP", "USD"]},
  "response_ok": {"success": true, "data": {"customer_id": 25}},
  "response_error": {"success": false, "errors": [{"type": "technical", "code": "TAX_ID_INVALID", "message": "Documento fiscal inválido"}]},
  "campos": "tax_id: RNC/Cédula"
}
```

### Seguridad
Portal con contraseña robusta y MFA opcional.

### Auditoría
Descargas y consultas registradas por usuario/IP.

### Pruebas
Acceso a portal, seguridad horizontal, límites de crédito.

### Riesgos / Mejores prácticas / Futuro
Riesgo de datos fiscales incompletos; usar validadores en tiempo real; mejora con notificaciones por WhatsApp/email.

---

## Módulo 4. Proveedores y compras

### Objetivo
Gestionar ciclo de compras y obligaciones asociadas.

### Alcance
Proveedores, facturas de compra, impuestos, integración CxP y contabilidad, soporte e-CF 46.

### Submódulos
- Maestro proveedores
- Registro de compras
- Impuestos de compra

### Casos de uso
- Crear proveedor
- Registrar factura de compra
- Aplicar impuestos y cuentas contables

### Reglas de negocio
- **Regla interna:** compra contabilizada genera CxP.

### Validaciones
- **Técnica:** no duplicar número factura proveedor
- **Fiscal:** tipo de comprobante permitido (validar con normativa vigente DGII y/o contador fiscal)

### UI/UX
- Formulario de compra con panel de impuestos y previsualización de impacto contable.

### Angular/PHP/MySQL/API/JSON
- Angular: `suppliers-page`, `purchase-invoice-form`
- PHP: `SupplierController`, `PurchaseController`
- MySQL: `suppliers`, `purchase_invoices`, `purchase_items`, `purchase_taxes`
- API: `POST /suppliers`, `POST /purchases`

```json
{
  "request": {"supplier_id": 9, "invoice_number": "B0100001234", "date": "2026-03-01", "items": [{"product_id": 3, "qty": 10, "cost": 120}]},
  "response_ok": {"success": true, "data": {"purchase_id": 90, "status": "POSTED"}},
  "response_error": {"success": false, "errors": [{"type": "business", "code": "SUPPLIER_DOC_DUPLICATE", "message": "Documento duplicado"}]},
  "campos": "invoice_number: comprobante del proveedor"
}
```

### Seguridad/Auditoría/Pruebas/Riesgos/Mejoras
Permiso por aprobación, auditoría de cambios de totales, pruebas de duplicidad, riesgo de registro fiscal erróneo, mejora con OCR de facturas.

---

## Módulo 5. Productos, servicios e inventarios

### Objetivo
Control integral de catálogo, costos, movimientos y disponibilidad por almacén.

### Alcance
Productos/servicios, categorías, unidades, costos, impuestos, precios, existencias, kardex, ajustes, transferencias entre 2 almacenes.

### Submódulos
- Catálogo
- Costeo
- Movimientos
- Kardex/transferencias

### Casos de uso
- Crear producto
- Registrar entrada
- Registrar ajuste
- Transferir entre almacenes

### Reglas de negocio
- **Regla interna:** no permitir stock negativo sin permiso especial.
- **Regla interna:** toda transferencia genera 2 movimientos en transacción atómica.

### Validaciones
- **Técnica:** SKU único, unidad existente.
- **Negocio:** disponibilidad por almacén.

### UI/UX
- Vista kardex por producto/almacén/fecha.
- Alertas visuales por stock mínimo.

### Angular/PHP/MySQL/API
- Angular: `products-page`, `inventory-move-form`, `kardex-page`, `transfer-form`
- PHP: `ProductController`, `InventoryController`
- MySQL: `products`, `inventory_balances`, `inventory_moves`, `kardex`
- API: `POST /products`, `POST /warehouses`, `POST /inventory/entries`, `POST /inventory/adjustments`

### JSON
```json
{
  "request": {"warehouse_id": 1, "product_id": 3, "move_type": "ENTRY", "qty": 50, "unit_cost": 100},
  "response_ok": {"success": true, "data": {"move_id": 210, "new_balance": 140}},
  "response_error": {"success": false, "errors": [{"type": "technical", "code": "WAREHOUSE_NOT_FOUND", "message": "Almacén no existe"}]},
  "campos": "move_type: ENTRY|EXIT|ADJUST|TRANSFER"
}
```

### Seguridad/Auditoría/Pruebas/Riesgos/Mejoras
Bitácora por movimiento, pruebas de concurrencia, riesgo por inventario desfasado, mejora con conteo cíclico móvil.

---

## Módulo 6. Ventas y facturación

### Objetivo
Gestionar ciclo comercial completo y emisión de documentos internos previos al e-CF.

### Alcance
Cotizaciones, pedidos, facturas, devoluciones, notas de crédito, descuentos, impuestos, integración inventario/CxC/contabilidad.

### Submódulos
- Preventa (cotización/pedido)
- Facturación
- Devoluciones y NC

### Casos de uso
- Convertir cotización a pedido/factura
- Facturar y afectar inventario
- Emitir nota de crédito

### Reglas de negocio
- **Regla interna:** factura confirmada descuenta inventario y genera CxC.
- **Regla interna:** NC requiere documento de referencia.

### Validaciones
- **Técnica:** cliente, moneda, impuestos válidos
- **Negocio:** stock y límite crédito
- **Fiscal:** tipo comprobante correcto (validar con normativa vigente DGII y/o contador fiscal)

### UI/UX / Angular / PHP / DB / API
- Componentes: `quote-form`, `order-form`, `invoice-form`, `credit-note-form`
- Servicios: `sales.service.ts`, `pricing.service.ts`
- Controllers: `SalesController`, `CreditNoteController`
- Tablas: `sales_invoices`, `sales_invoice_items`, `credit_notes`
- API: `POST /sales/invoices`, `POST /sales/credit-notes`

### JSON
```json
{
  "request": {"customer_id": 25, "currency": "DOP", "items": [{"product_id": 3, "qty": 2, "price": 1500, "discount_pct": 5}]},
  "response_ok": {"success": true, "data": {"invoice_id": 880, "total": 3015}},
  "response_error": {"success": false, "errors": [{"type": "business", "code": "INSUFFICIENT_STOCK", "message": "Inventario insuficiente"}]},
  "campos": "items: detalle de línea"
}
```

### Seguridad/Auditoría/Pruebas/Riesgos/Mejoras
Control por permiso de descuento máximo, auditoría de anulaciones, pruebas de impuestos/rounding, riesgo de precios incorrectos, mejora con reglas dinámicas por cliente.

---

## Módulo 7. Facturación Electrónica DGII (detallado)

### Objetivo
Emitir, validar, enviar y monitorear e-CF con trazabilidad 100%.

### Alcance
e-CF 31/32/33/34/46/47, validación previa, secuencias, envío DGII, respuesta, reintentos, monitor de errores, historial.

### Submódulos
- Generador e-CF
- Validador estructural/fiscal
- Integrador DGII
- Monitor y reintentos
- Trazabilidad y evidencias

### Casos de uso
- Emitir e-CF desde factura interna
- Validar antes de envío
- Enviar/consultar estatus
- Corregir y reenviar tras rechazo

### Roles involucrados
Facturador, Contador, Administrador fiscal, Auditor.

### Flujo funcional paso a paso
1. Documento interno aprobado.
2. Selección tipo e-CF.
3. Construcción payload fiscal.
4. Validación técnica + negocio + fiscal + estructura.
5. Firma digital.
6. Envío DGII.
7. Registro de track_id y estado.
8. Reintentos automáticos/manuales.
9. Cierre con estado final y notificación.

### Tipos e-CF soportados

#### e-CF 31
- **Definición:** Factura de Crédito Fiscal.
- **Cuándo aplica:** operaciones B2B con derecho a crédito fiscal.
- **Cuándo no aplica:** consumidor final.
- **Datos obligatorios:** datos emisor/receptor fiscal, detalle ITBIS, totales.
- **Validaciones:** RNC receptor, totales y secuencia.
- **Impacto contable:** Dr CxC / Cr ingresos + Cr ITBIS.
- **Impacto fiscal:** reporte 607.
- **Errores comunes:** RNC inválido, ITBIS inconsistente.

#### e-CF 32
- **Definición:** Factura de Consumo.
- **Aplica:** venta a consumidor final.
- **No aplica:** operaciones que requieran crédito fiscal comprador.
- **Impacto contable/fiscal:** ingreso + ITBIS; reporte 607.

#### e-CF 33
- **Definición:** Nota de Débito.
- **Aplica:** incrementos posteriores a documento emitido.
- **No aplica:** devoluciones o descuentos.
- **Obligatorio:** referencia del e-CF origen + motivo.

#### e-CF 34
- **Definición:** Nota de Crédito.
- **Aplica:** devoluciones/bonificaciones/descuentos posteriores.
- **No aplica:** incremento de valor.
- **Impacto contable:** reverso parcial/total del ingreso/impuesto.

#### e-CF 46
- **Definición:** Comprobante de Compras Electrónico.
- **Aplica:** soporte de compras/gastos según tratamiento fiscal.
- **No aplica:** cuando corresponda otro tipo regulado.

#### e-CF 47
- **Definición:** Gastos Menores Electrónico.
- **Aplica:** gastos menores bajo límites/reglas permitidas.
- **No aplica:** operación de mayor formalidad fiscal.

> Para todos los tipos, parámetros y criterios exactos de aceptación/rechazo: **validar con normativa vigente DGII y/o contador fiscal**.

### Diseño UI/UX
- Formulario inteligente por tipo e-CF (campos dinámicos)
- Semáforo de validaciones: técnica, negocio, fiscal, estructura
- Panel de estatus DGII con timeline

### Estructura Angular
- `ecf.module.ts`
- Componentes: `ecf-form`, `ecf-validator-panel`, `ecf-monitor`, `ecf-history`
- Servicios: `ecf.service.ts`, `dgii.service.ts`, `ecf-validation.service.ts`
- Rutas: `/ecf/emit`, `/ecf/monitor`, `/ecf/{id}`

### Estructura PHP 7.3
- `EcfController`, `EcfValidationController`, `DgiiController`
- Servicios: `EcfBuilderService`, `EcfValidationService`, `DgiiGatewayService`, `RetryService`

### Tablas MySQL
- `ecf_documents`, `ecf_versions`, `ecf_validation_runs`, `ecf_submissions`, `ecf_responses`, `ecf_errors`

### API REST
- `POST /ecf/validate`
- `POST /ecf/emit`
- `POST /ecf/send`
- `GET /ecf/{id}/status`
- `POST /ecf/{id}/register-response`
- `POST /ecf/{id}/retry`

### JSON de ejemplo
```json
{
  "request": {"type": "31", "customer": {"tax_id": "101010101"}, "items": [{"description": "Servicio", "qty": 1, "price": 1000, "tax": 180}]},
  "response_ok": {"success": true, "data": {"ecf_id": 500, "status": "READY_TO_SEND"}},
  "response_error": {"success": false, "errors": [{"type": "fiscal", "code": "RNC_INVALID", "message": "RNC receptor inválido"}]},
  "campos": "type: tipo e-CF; items: detalle fiscal"
}
```

### Manejo de errores
- `DGII_TIMEOUT` (técnico)
- `DGII_SCHEMA_ERROR` (estructura)
- `DGII_FISCAL_RULE` (fiscal)
- `BUSINESS_RULE_FAILED` (negocio)

### Permisos y seguridad
- Solo perfiles autorizados pueden enviar/corregir/reintentar.
- Cifrado de payload sensible en reposo.

### Auditoría
- Registro completo de versión, intento, respuesta, usuario y timestamp.

### Pruebas sugeridas
- Unit: mapeo payload por tipo e-CF
- Integración: validación + envío + consulta
- E2E: rechazo, corrección y reenvío

### Riesgos
- Cambios en normativa/formato DGII
- Certificados vencidos

### Buenas prácticas
- Versionar reglas por fecha efectiva
- Reintentos exponenciales

### Posibles mejoras futuras
- Simulador fiscal de prevalidación masiva
- Motor de reglas configurable sin despliegue

---

## Módulo 8. Guías integradas y asistente normativo

### Objetivo
Reducir errores con ayuda contextual operativa y fiscal dentro del sistema.

### Alcance
Guías por tipo e-CF, ayuda por campo, glosario, recomendaciones, ejemplos correctos/incorrectos, explicación de errores DGII, FAQ.

### Submódulos
- Centro de ayuda
- Asistencia contextual
- Base de conocimiento fiscal

### API
- `GET /help/topics`
- `GET /help/context/{screen}/{field}`

### Reglas/validaciones
- **Regla interna:** contenido versionado por vigencia.
- **Validación técnica:** cache de contenido + fallback local.

### Resto (UI/seguridad/auditoría/pruebas/riesgos)
Ayuda en side-panel, permisos de edición para administrador, auditoría de cambios de contenido, pruebas de contexto por pantalla, riesgo de desactualización normativa, mejora con IA semántica.

---

## Módulo 9. Asistente de Configuración Inteligente

### Objetivo
Diagnosticar configuración y recomendar/corregir faltantes críticos.

### Alcance
Tipo de comprobante sugerido, datos faltantes, credenciales/certificados, secuencias, moneda/impuestos/inventario, corrección en 1 clic.

### API
- `POST /setup-assistant/analyze`
- `POST /setup-assistant/apply-fix`

### Reglas
- **Regla interna:** no permite envío DGII si checklist crítico incompleto.

### Validaciones
- **Técnica:** consistencia de configuración
- **Fiscal:** parámetros obligatorios de e-CF

### Mejoras
motor de recomendaciones por histórico de errores.

---

## Módulo 10. Wizard de primera configuración

### Objetivo
Guiar instalación desde cero hasta primera factura de prueba.

### Alcance (pasos)
Bienvenida -> Empresa -> Sucursal -> Usuarios -> Fiscal -> Monedas -> Impuestos -> Almacenes -> Productos base -> Certificados -> Credenciales DGII -> Secuencias -> Prueba conexión -> Validación final -> Primera factura de prueba.

### Campos/validaciones/mensajes
- Cada paso con validación bloqueante.
- Mensaje de error accionable y ayuda contextual.

### Angular/PHP/API
- Angular: `wizard.module`, componente `stepper`
- PHP: `SetupWizardController`
- API: `POST /wizard/step/{n}`, `POST /wizard/complete`

---

## Módulo 11. Contabilidad

### Objetivo
Registrar y reportar impacto financiero de operaciones.

### Alcance
Catálogo de cuentas, asientos automáticos/manuales, auxiliares, balances, integración ventas/compras/bancos.

### Reglas
- **Regla interna:** todo asiento debe cuadrar (debe = haber).
- **Regla interna:** operación fiscal impacta contabilidad según plantilla parametrizada.

### Validaciones
- **Técnica:** cuentas activas y período abierto
- **Fiscal:** clasificación tributaria coherente (validar con normativa vigente DGII y/o contador fiscal)

### API
- `POST /accounting/journal-entries`
- `GET /accounting/trial-balance`

---

## Módulo 12. Bancos

### Objetivo
Administrar tesorería y conciliación bancaria.

### Alcance
Cuentas, ingresos, egresos, transferencias, conciliaciones, integración CxC/CxP/contabilidad.

### API
- `POST /banks/accounts`
- `POST /banks/transactions`
- `POST /banks/reconciliations`

### Validaciones
- **Técnica:** cuenta activa, saldo suficiente
- **Negocio:** no duplicar referencia bancaria

---

## Módulo 13. Cuentas por Cobrar

### Objetivo
Controlar cartera de clientes y gestión de cobro.

### Alcance
Balances, antigüedad, cobros, recibos, aplicación de pagos, notas de crédito, estados de cuenta, alertas.

### API
- `GET /ar/aging`
- `POST /ar/receipts`
- `POST /ar/applications`

### Reglas
- **Regla interna:** no aplicar cobro por encima del saldo documento.

---

## Módulo 14. Cuentas por Pagar

### Objetivo
Gestionar obligaciones con proveedores y pagos.

### Alcance
Balances, programación, pagos parciales, vencimientos, integración compras/contabilidad.

### API
- `GET /ap/aging`
- `POST /ap/payments`

### Reglas
- **Regla interna:** toda salida de pago debe generar movimiento bancario + asiento.

---

## Módulo 15. Reportes fiscales 606, 607 y 608

### Objetivo
Generar reportes fiscales por período con control de calidad de datos.

### Alcance
Filtros, validaciones, estructura de salida, conciliación compras/ventas, inconsistencias, exportación.

### API
- `POST /fiscal/606/generate`
- `POST /fiscal/607/generate`
- `POST /fiscal/608/generate`

### Validaciones
- **Técnica:** período válido y cerrado
- **Fiscal:** estructura y reglas del reporte (validar con normativa vigente DGII y/o contador fiscal)

---

## Módulo 16. Dashboard inteligente

### Objetivo
Visualización ejecutiva y operativa para toma de decisiones.

### Alcance
KPIs por estado documento, tipo e-CF, usuario, sucursal, período; alertas y acciones rápidas.

### API
- `GET /dashboard/kpis`
- `GET /dashboard/alerts`

### Buenas prácticas
- Widgets configurables por rol
- Cache de métricas no críticas

---

## Módulo 17. Logs, auditoría y monitoreo

### Objetivo
Trazabilidad integral técnica, funcional y fiscal.

### Alcance
Auditoría de usuarios/documentos/cambios, monitoreo DGII, clasificación de errores y observabilidad.

### Submódulos
- Auditoría funcional
- Observabilidad técnica
- Monitor de integración DGII

### Clasificación de error
- **Error técnico:** infraestructura/red/certificados/timeouts.
- **Error de estructura:** incumplimiento XSD o formato.
- **Error fiscal:** regla tributaria.
- **Error de negocio:** regla interna.

### API
- `GET /audit/logs`
- `GET /monitor/integrations`
- `GET /errors`

---

# 7) Catálogo de JSON obligatorios

> Cada ejemplo incluye: `request`, `response_ok`, `response_error`, `explicación de campos`.

## 7.1 login
```json
{
  "request": {"username": "admin@empresa.com", "password": "<SECRET>"},
  "response_ok": {"success": true, "data": {"access_token": "jwt", "refresh_token": "rjwt", "expires_in": 900}},
  "response_error": {"success": false, "errors": [{"code": "AUTH_INVALID", "message": "Credenciales inválidas"}]},
  "explicacion": "username: usuario de acceso; password: clave"
}
```

## 7.2 crear usuario
```json
{
  "request": {"name": "Operador", "email": "op@empresa.com", "role_ids": [2], "branch_ids": [1]},
  "response_ok": {"success": true, "data": {"user_id": 7}},
  "response_error": {"success": false, "errors": [{"code": "EMAIL_DUPLICATE", "message": "Email ya registrado"}]},
  "explicacion": "role_ids define acceso por rol"
}
```

## 7.3 crear cliente
```json
{
  "request": {"name": "Cliente A", "tax_id": "131313131", "credit_limit": 150000, "currency_codes": ["DOP", "USD"]},
  "response_ok": {"success": true, "data": {"customer_id": 25}},
  "response_error": {"success": false, "errors": [{"code": "TAX_ID_INVALID", "message": "RNC/Cédula inválido"}]},
  "explicacion": "tax_id es identificación fiscal del cliente"
}
```

## 7.4 crear proveedor
```json
{
  "request": {"name": "Proveedor SRL", "tax_id": "122222222", "payment_terms_days": 30},
  "response_ok": {"success": true, "data": {"supplier_id": 9}},
  "response_error": {"success": false, "errors": [{"code": "SUPPLIER_TAX_ID_INVALID", "message": "RNC inválido"}]},
  "explicacion": "payment_terms_days: plazo de pago"
}
```

## 7.5 crear producto
```json
{
  "request": {"sku": "P-100", "name": "Producto X", "unit_id": 1, "tax_ids": [1], "base_price": 1000},
  "response_ok": {"success": true, "data": {"product_id": 3}},
  "response_error": {"success": false, "errors": [{"code": "SKU_DUPLICATE", "message": "SKU ya existe"}]},
  "explicacion": "tax_ids: impuestos aplicables"
}
```

## 7.6 crear almacén
```json
{
  "request": {"code": "ALM-01", "name": "Almacén Principal", "branch_id": 1},
  "response_ok": {"success": true, "data": {"warehouse_id": 1}},
  "response_error": {"success": false, "errors": [{"code": "WAREHOUSE_CODE_DUPLICATE", "message": "Código ya existe"}]},
  "explicacion": "branch_id: sucursal dueña"
}
```

## 7.7 registrar entrada inventario
```json
{
  "request": {"warehouse_id": 1, "product_id": 3, "qty": 50, "unit_cost": 100},
  "response_ok": {"success": true, "data": {"move_id": 210, "new_balance": 140}},
  "response_error": {"success": false, "errors": [{"code": "WAREHOUSE_NOT_FOUND", "message": "Almacén inválido"}]},
  "explicacion": "qty: cantidad de entrada"
}
```

## 7.8 registrar ajuste
```json
{
  "request": {"warehouse_id": 1, "product_id": 3, "adjust_qty": -2, "reason": "Merma"},
  "response_ok": {"success": true, "data": {"move_id": 222, "balance": 138}},
  "response_error": {"success": false, "errors": [{"code": "NEGATIVE_STOCK_NOT_ALLOWED", "message": "Stock negativo no permitido"}]},
  "explicacion": "adjust_qty puede ser positivo o negativo"
}
```

## 7.9 crear factura
```json
{
  "request": {"customer_id": 25, "currency": "DOP", "items": [{"product_id": 3, "qty": 2, "price": 1500}]},
  "response_ok": {"success": true, "data": {"invoice_id": 880, "status": "ISSUED"}},
  "response_error": {"success": false, "errors": [{"code": "INSUFFICIENT_STOCK", "message": "Inventario insuficiente"}]},
  "explicacion": "items: detalle de líneas"
}
```

## 7.10 emitir e-CF 31
```json
{
  "request": {"type": "31", "invoice_id": 880, "receiver_tax_id": "101010101"},
  "response_ok": {"success": true, "data": {"ecf_id": 5001, "status": "READY_TO_SEND"}},
  "response_error": {"success": false, "errors": [{"code": "RNC_INVALID", "message": "RNC receptor inválido"}]},
  "explicacion": "type=31 crédito fiscal"
}
```

## 7.11 emitir e-CF 32
```json
{
  "request": {"type": "32", "invoice_id": 881, "customer_name": "Consumidor Final"},
  "response_ok": {"success": true, "data": {"ecf_id": 5002}},
  "response_error": {"success": false, "errors": [{"code": "CUSTOMER_REQUIRED", "message": "Cliente requerido"}]},
  "explicacion": "type=32 consumo"
}
```

## 7.12 emitir e-CF 33
```json
{
  "request": {"type": "33", "reference_ecf": "E310000001", "reason": "Cargo adicional"},
  "response_ok": {"success": true, "data": {"ecf_id": 5003}},
  "response_error": {"success": false, "errors": [{"code": "REF_ECF_NOT_FOUND", "message": "Documento referencia no existe"}]},
  "explicacion": "type=33 nota débito"
}
```

## 7.13 emitir e-CF 34
```json
{
  "request": {"type": "34", "reference_ecf": "E310000001", "reason": "Devolución"},
  "response_ok": {"success": true, "data": {"ecf_id": 5004}},
  "response_error": {"success": false, "errors": [{"code": "AMOUNT_EXCEEDS_REFERENCE", "message": "Monto excede documento origen"}]},
  "explicacion": "type=34 nota crédito"
}
```

## 7.14 emitir e-CF 46
```json
{
  "request": {"type": "46", "purchase_invoice_id": 90, "supplier_tax_id": "131313131"},
  "response_ok": {"success": true, "data": {"ecf_id": 5005}},
  "response_error": {"success": false, "errors": [{"code": "SUPPLIER_TAX_ID_INVALID", "message": "RNC proveedor inválido"}]},
  "explicacion": "type=46 comprobante compras"
}
```

## 7.15 emitir e-CF 47
```json
{
  "request": {"type": "47", "expense_type": "GASTO_MENOR", "amount": 300},
  "response_ok": {"success": true, "data": {"ecf_id": 5006}},
  "response_error": {"success": false, "errors": [{"code": "EXPENSE_TYPE_INVALID", "message": "Tipo de gasto inválido"}]},
  "explicacion": "type=47 gastos menores"
}
```

## 7.16 validar documento antes de envío
```json
{
  "request": {"document_id": 880, "checks": ["schema", "fiscal", "business"]},
  "response_ok": {"success": true, "data": {"valid": false, "errors": [{"type": "fiscal", "field": "receiver_tax_id", "code": "RNC_INVALID"}]}},
  "response_error": {"success": false, "errors": [{"code": "DOCUMENT_NOT_FOUND", "message": "Documento no encontrado"}]},
  "explicacion": "checks define validaciones requeridas"
}
```

## 7.17 enviar documento a DGII
```json
{
  "request": {"ecf_id": 5001, "signed_payload": "base64..."},
  "response_ok": {"success": true, "data": {"submission_id": 7001, "status": "SENT", "track_id": "DGII-123"}},
  "response_error": {"success": false, "errors": [{"code": "DGII_TIMEOUT", "message": "Tiempo de espera agotado"}]},
  "explicacion": "signed_payload es la estructura firmada"
}
```

## 7.18 consultar estatus DGII
```json
{
  "request": {"track_id": "DGII-123"},
  "response_ok": {"success": true, "data": {"status": "ACCEPTED", "status_date": "2026-03-10T10:30:00Z"}},
  "response_error": {"success": false, "errors": [{"code": "TRACK_ID_NOT_FOUND", "message": "No encontrado"}]},
  "explicacion": "track_id entregado por DGII"
}
```

## 7.19 registrar respuesta DGII
```json
{
  "request": {"ecf_id": 5001, "dgii_status": "REJECTED", "dgii_code": "E302", "dgii_message": "Totales inconsistentes"},
  "response_ok": {"success": true, "data": {"updated": true}},
  "response_error": {"success": false, "errors": [{"code": "INVALID_STATUS_TRANSITION", "message": "Transición inválida"}]},
  "explicacion": "dgii_code es código oficial recibido"
}
```

## 7.20 registrar rechazo
```json
{
  "request": {"ecf_id": 5001, "reason": "RNC inválido"},
  "response_ok": {"success": true, "data": {"status": "REJECTED_REGISTERED"}},
  "response_error": {"success": false, "errors": [{"code": "ECF_NOT_FOUND", "message": "e-CF no existe"}]},
  "explicacion": "reason: motivo operativo del rechazo"
}
```

## 7.21 corregir documento
```json
{
  "request": {"ecf_id": 5001, "patch": {"receiver_tax_id": "101010101"}},
  "response_ok": {"success": true, "data": {"new_version": 2, "status": "READY_TO_RESEND"}},
  "response_error": {"success": false, "errors": [{"code": "PATCH_NOT_ALLOWED", "message": "Campo no editable"}]},
  "explicacion": "patch contiene cambios permitidos"
}
```

## 7.22 generar nota de crédito
```json
{
  "request": {"reference_invoice_id": 880, "reason": "Devolución parcial", "items": [{"product_id": 3, "qty": 1, "amount": 1500}]},
  "response_ok": {"success": true, "data": {"credit_note_id": 901}},
  "response_error": {"success": false, "errors": [{"code": "REF_DOC_NOT_ELIGIBLE", "message": "Documento no elegible"}]},
  "explicacion": "reference_invoice_id: factura original"
}
```

## 7.23 registrar cobro
```json
{
  "request": {"customer_id": 25, "amount": 3000, "currency": "DOP", "applications": [{"invoice_id": 880, "amount": 3000}]},
  "response_ok": {"success": true, "data": {"receipt_id": 7001}},
  "response_error": {"success": false, "errors": [{"code": "OVERPAYMENT_NOT_ALLOWED", "message": "Monto excede saldo"}]},
  "explicacion": "applications distribuye el cobro"
}
```

## 7.24 registrar pago
```json
{
  "request": {"supplier_id": 9, "amount": 5000, "bank_account_id": 2, "applications": [{"purchase_invoice_id": 90, "amount": 5000}]},
  "response_ok": {"success": true, "data": {"payment_id": 8001}},
  "response_error": {"success": false, "errors": [{"code": "BANK_BALANCE_INSUFFICIENT", "message": "Fondos insuficientes"}]},
  "explicacion": "bank_account_id: cuenta origen"
}
```

## 7.25 generar 606
```json
{
  "request": {"period": "2026-02", "branch_id": 1},
  "response_ok": {"success": true, "data": {"file": "606_202602.txt", "records": 120}},
  "response_error": {"success": false, "errors": [{"code": "INCONSISTENT_FISCAL_DATA", "message": "Datos inconsistentes"}]},
  "explicacion": "period en formato AAAA-MM"
}
```

## 7.26 generar 607
```json
{
  "request": {"period": "2026-02", "branch_id": 1},
  "response_ok": {"success": true, "data": {"file": "607_202602.txt", "records": 152}},
  "response_error": {"success": false, "errors": [{"code": "FISCAL_PERIOD_OPEN", "message": "Período no cerrado"}]},
  "explicacion": "incluye facturación del período"
}
```

## 7.27 generar 608
```json
{
  "request": {"period": "2026-02", "branch_id": 1},
  "response_ok": {"success": true, "data": {"file": "608_202602.txt", "records": 8}},
  "response_error": {"success": false, "errors": [{"code": "VOIDED_DOCS_NOT_FOUND", "message": "Sin anulaciones para el período"}]},
  "explicacion": "reporte de anulaciones"
}
```

---

# 8) Validaciones obligatorias (matriz)

1. **Validaciones de formulario**: requerido, tipo, rango, máscara.
2. **Validaciones de negocio**: stock, crédito, estados de flujo.
3. **Validaciones fiscales**: tipo e-CF, secuencia, datos fiscales.
4. **Validaciones técnicas**: autenticación, integridad JSON, referencial.
5. **Validaciones previas DGII**: estructura + fiscal + firma + credenciales.
6. **Validaciones de inventario**: disponibilidad por almacén.
7. **Validaciones de moneda**: tasa vigente y redondeo.
8. **Validaciones de impuestos**: base imponible y tasa aplicable.
9. **Validaciones de secuencias**: correlativo y agotamiento.
10. **Validaciones de permisos**: rol, acción y alcance.
11. **Validaciones de configuración**: checklist mínimo de operación.
12. **Validaciones de consistencia contable**: debe/haber balanceado.

---

# 9) Validación XSD/estructural enterprise

### Diseño del motor

- Repositorio de XSD por tipo e-CF y versión
- Caché de esquemas con checksum
- Validador multi-etapa:
  1. JSON/Payload mínimo
  2. Reglas de negocio
  3. Reglas fiscales
  4. XSD estructural

### Respuesta de error enriquecida

- Código
- Severidad
- Tipo (`technical|structure|fiscal|business`)
- Campo/ruta (`XPath` o `json.path`)
- Mensaje y sugerencia de corrección

### Trazabilidad

- Historial por intento
- Usuario/sistema que ejecutó validación
- Resultado completo persistido para auditoría

---

# 10) Riesgos generales

- Cambios regulatorios DGII
- Parámetros fiscales mal configurados
- Calidad deficiente de maestros
- Latencia/falla de integración externa
- Dependencia en personal clave

Mitigaciones: versionado de reglas, pruebas regresivas fiscales, observabilidad, capacitación operativa y runbooks.

---

# 11) Plan de implementación por fases

1. **Fase 0**: Base técnica (auth, RBAC, auditoría, error handling)
2. **Fase 1**: Maestros (empresa, sucursal, impuestos, moneda, productos, clientes, proveedores)
3. **Fase 2**: Inventario + ventas + CxC
4. **Fase 3**: Compras + CxP + bancos
5. **Fase 4**: Facturación electrónica DGII y monitor
6. **Fase 5**: Contabilidad integrada + 606/607/608
7. **Fase 6**: Portal clientes + dashboard + asistentes
8. **Fase 7**: Hardening producción + performance + continuidad

---

# 12) Checklist de salida a producción

- [ ] Certificado digital vigente
- [ ] Credenciales DGII validadas
- [ ] Secuencias e-CF habilitadas por sucursal
- [ ] Matriz de permisos aprobada
- [ ] Backups y restore probados
- [ ] Monitoreo y alertas activados
- [ ] Logs y auditoría operativos
- [ ] Pruebas funcionales/fiscales aprobadas
- [ ] Prueba de carga para 500 transacciones/mes
- [ ] Manual operativo + técnico publicados

---

# 13) Estructura sugerida de carpetas

## Frontend (Angular)

```text
frontend/src/app/
  core/
  shared/
  modules/
    security/
    settings/
    customers/
    suppliers/
    inventory/
    sales/
    ecf/
    help-center/
    setup-assistant/
    wizard/
    accounting/
    banks/
    ar/
    ap/
    fiscal-reports/
    dashboard/
    audit-monitor/
```

## Backend (PHP 7.3)

```text
backend/
  app/
    Controllers/
    Services/
    Repositories/
    Validators/
    Policies/
    DTO/
    Jobs/
    Helpers/
  routes/
  config/
  storage/
  tests/
```

---

# 14) Nota final de cumplimiento

Este documento sirve como **blueprint funcional + técnico** para implementación.

Antes de activar operación oficial:

1. Confirmar catálogos/estructuras vigentes de DGII.
2. Validar reglas fiscales y contables con contador.
3. Ejecutar pruebas de aceptación fiscal, técnica y operativa.

**Regla permanente**: “validar con normativa vigente DGII y/o contador fiscal”.
