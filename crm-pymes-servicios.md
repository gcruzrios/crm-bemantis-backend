

# CRM Simplificado para PYMES de Servicios
> Esquema de entidades mínimas para empresas de hasta 10 empleados con ventas entre $50k–$100k USD anuales. Sin módulo de facturación — el flujo termina en **Cotización**.

---

## 1. Contexto y Alcance

| Parámetro | Valor |
|---|---|
| Tamaño de empresa | 1–10 empleados |
| Volumen de ventas anual | $50,000 – $100,000 USD |
| Tipo de negocio | Servicios (consultoría, marketing, IT, diseño, etc.) |
| Documento comercial final | Cotización (Quote) — sin facturación electrónica |
| Modelo de datos | Relacional simplificado |

---

## 2. Principios de Diseño

- **Mínimo viable:** solo las entidades que generan valor operativo real.
- **Sin sobrecarga:** sin módulos de inventario, cuentas por cobrar ni RRHH.
- **Foco en el ciclo de venta:** Prospecto → Contacto → Negocio → Cotización.
- **Extensible:** estructura que permite agregar facturación o soporte en el futuro.

---

## 3. Entidades del Modelo

### 3.1 `Company` — Empresa cliente

Representa a la organización con la que se tiene o se busca una relación comercial.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `name` | VARCHAR(200) | Nombre de la empresa |
| `industry` | VARCHAR(100) | Sector (ej. salud, retail, legal) |
| `website` | VARCHAR(255) | Sitio web |
| `country` | VARCHAR(100) | País |
| `city` | VARCHAR(100) | Ciudad |
| `source` | ENUM | Origen (referido, web, evento, etc.) |
| `created_at` | TIMESTAMP | Fecha de registro |
| `notes` | TEXT | Notas libres |

---

### 3.2 `Contact` — Persona de contacto

Individuo dentro de la empresa cliente. Un `Company` puede tener múltiples contactos.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `company_id` | FK → Company | Empresa a la que pertenece |
| `first_name` | VARCHAR(100) | Nombre |
| `last_name` | VARCHAR(100) | Apellido |
| `email` | VARCHAR(200) | Correo electrónico |
| `phone` | VARCHAR(50) | Teléfono / WhatsApp |
| `role` | VARCHAR(100) | Cargo (ej. Gerente, Dueño) |
| `is_primary` | BOOLEAN | ¿Es el contacto principal? |
| `created_at` | TIMESTAMP | Fecha de registro |

---

### 3.3 `Deal` — Negocio / Oportunidad

Representa una oportunidad de venta activa. Es el centro del pipeline comercial.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `company_id` | FK → Company | Cliente asociado |
| `contact_id` | FK → Contact | Contacto responsable |
| `owner_id` | FK → User | Vendedor asignado |
| `title` | VARCHAR(200) | Nombre del negocio |
| `stage` | ENUM | Etapa del pipeline (ver §4) |
| `estimated_value` | DECIMAL(12,2) | Valor estimado en USD |
| `probability` | INT (0-100) | % de cierre estimado |
| `expected_close_date` | DATE | Fecha esperada de cierre |
| `created_at` | TIMESTAMP | Fecha de creación |
| `updated_at` | TIMESTAMP | Última actualización |
| `notes` | TEXT | Notas del negocio |

---

### 3.4 `Quote` — Cotización

Documento comercial enviado al cliente. Puede haber varias versiones por negocio.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `deal_id` | FK → Deal | Negocio al que pertenece |
| `quote_number` | VARCHAR(50) | Número de cotización (ej. COT-2025-001) |
| `status` | ENUM | Estado: borrador, enviada, aceptada, rechazada, expirada |
| `valid_until` | DATE | Fecha de vencimiento |
| `subtotal` | DECIMAL(12,2) | Subtotal sin impuestos |
| `tax_rate` | DECIMAL(5,2) | % impuesto aplicable |
| `total` | DECIMAL(12,2) | Total con impuestos |
| `currency` | CHAR(3) | Moneda (USD, CRC, etc.) |
| `notes` | TEXT | Términos, condiciones, notas |
| `created_at` | TIMESTAMP | Fecha de creación |
| `sent_at` | TIMESTAMP | Fecha de envío al cliente |

---

### 3.5 `QuoteItem` — Línea de cotización

Cada servicio o ítem dentro de una cotización.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `quote_id` | FK → Quote | Cotización padre |
| `service_id` | FK → Service (opcional) | Servicio del catálogo |
| `description` | TEXT | Descripción del ítem |
| `quantity` | DECIMAL(10,2) | Cantidad (horas, unidades, etc.) |
| `unit_price` | DECIMAL(12,2) | Precio unitario |
| `line_total` | DECIMAL(12,2) | `quantity × unit_price` |

---

### 3.6 `Service` — Catálogo de servicios

Servicios predefinidos reutilizables en las cotizaciones.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `name` | VARCHAR(200) | Nombre del servicio |
| `description` | TEXT | Descripción |
| `default_price` | DECIMAL(12,2) | Precio base |
| `unit` | VARCHAR(50) | Unidad (hora, proyecto, mes) |
| `is_active` | BOOLEAN | ¿Disponible para cotizar? |

---

### 3.7 `Activity` — Actividades y seguimiento

Registro de interacciones con clientes: llamadas, emails, reuniones, tareas.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `deal_id` | FK → Deal (opcional) | Negocio relacionado |
| `contact_id` | FK → Contact (opcional) | Contacto relacionado |
| `owner_id` | FK → User | Usuario responsable |
| `type` | ENUM | llamada, email, reunión, tarea, nota |
| `subject` | VARCHAR(200) | Asunto |
| `description` | TEXT | Detalle |
| `due_date` | TIMESTAMP | Fecha/hora programada |
| `completed_at` | TIMESTAMP | Fecha de completado |
| `created_at` | TIMESTAMP | Fecha de registro |

---

### 3.8 `User` — Usuarios del CRM

Empleados con acceso al sistema (máx. 10).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID / INT | Identificador único |
| `name` | VARCHAR(150) | Nombre completo |
| `email` | VARCHAR(200) | Correo (login) |
| `role` | ENUM | admin, vendedor, visualizador |
| `is_active` | BOOLEAN | Estado de la cuenta |
| `created_at` | TIMESTAMP | Fecha de registro |

---

## 4. Pipeline de Ventas (Deal Stages)

```
PROSPECTO → CALIFICADO → PROPUESTA → NEGOCIACIÓN → GANADO / PERDIDO
```

| Etapa | Descripción | Prob. típica |
|---|---|---|
| `prospecto` | Empresa identificada, sin contacto formal | 10% |
| `calificado` | Necesidad confirmada, presupuesto validado | 25% |
| `propuesta` | Cotización enviada o en preparación | 50% |
| `negociacion` | Cliente evaluando, con feedback activo | 75% |
| `ganado` | Cotización aceptada, listo para servicio | 100% |
| `perdido` | Oportunidad descartada | 0% |

---

## 5. Diagrama de Relaciones (ERD Simplificado)

```
User
 └─ owns → Deal
 └─ executes → Activity

Company
 ├─ has many → Contact
 └─ has many → Deal

Contact
 └─ associated with → Deal
 └─ associated with → Activity

Deal
 ├─ has many → Quote
 └─ has many → Activity

Quote
 └─ has many → QuoteItem

QuoteItem
 └─ references → Service (optional)

Service
 └─ referenced by → QuoteItem
```

---

## 6. Flujo Operativo Principal

```
1. Registrar Company + Contact
        ↓
2. Crear Deal (negocio/oportunidad)
        ↓
3. Registrar Activities (llamadas, reuniones, seguimientos)
        ↓
4. Crear Quote con QuoteItems (desde catálogo o ad hoc)
        ↓
5. Enviar Quote al cliente
        ↓
6. Marcar Deal como GANADO o PERDIDO
        ↓
   [Fin del ciclo CRM — facturación externa]
```

---

## 7. Entidades NO incluidas (por decisión de alcance)

| Entidad | Razón de exclusión |
|---|---|
| Invoice / Factura | La empresa usa sistema externo de facturación |
| Payment | Sin gestión de cobros en el CRM |
| Contract | Volumen y complejidad no lo justifican |
| Support Ticket | Fuera del alcance de ventas |
| Product / Inventory | Empresa de servicios, sin inventario físico |
| Campaign / Marketing | Para una segunda fase del CRM |

---

## 8. Métricas Clave Soportadas

Con este modelo se pueden calcular directamente:

- **Pipeline total** = suma de `estimated_value` de deals activos
- **Tasa de cierre** = deals ganados / deals cerrados (%)
- **Valor promedio de cotización** = promedio de `Quote.total`
- **Tiempo de ciclo de venta** = días entre `Deal.created_at` y cierre
- **Actividad por vendedor** = conteo de `Activity` por `owner_id`
- **Cotizaciones por etapa** = distribución de `Quote.status`

---

## 9. Recomendaciones de Implementación

1. **Stack sugerido:** FastAPI + PostgreSQL (backend) / React + shadcn/ui (frontend)
2. **Autenticación:** JWT con roles (admin, vendedor, visualizador)
3. **Número de cotización:** generado automáticamente con formato `COT-YYYY-NNN`
4. **Export de cotización:** PDF generado desde plantilla HTML (ReportLab o WeasyPrint)
5. **Límite de usuarios:** validar en backend que `User.is_active` no supere 10
6. **Moneda base:** configurar a nivel de sistema, con opción por cotización

---

*Esquema diseñado para Bemantis CRM — versión PYME Servicios*
*Revisión: junio 2025*
