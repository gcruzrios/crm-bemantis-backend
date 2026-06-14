# Backend Specification — CRM PYMES Servicios
> FastAPI + PostgreSQL · SQLAlchemy Async · Pydantic v2 · JWT Auth

---

## 1. Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Framework | FastAPI | 0.115+ |
| Base de datos | PostgreSQL | 16+ |
| ORM | SQLAlchemy (async) | 2.0+ |
| Migraciones | Alembic | 1.13+ |
| Validación | Pydantic v2 | 2.6+ |
| Autenticación | python-jose + passlib | JWT HS256 |
| Servidor | Uvicorn + Gunicorn | — |
| Contenedor | Docker + Docker Compose | — |
| Testing | Pytest + httpx | — |

---

## 2. Estructura del Proyecto

```
crm-backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, routers
│   ├── core/
│   │   ├── config.py            # Settings (Pydantic BaseSettings)
│   │   ├── security.py          # JWT, password hashing
│   │   └── deps.py              # Dependencias comunes (get_db, get_current_user)
│   ├── db/
│   │   ├── base.py              # Base declarativa + imports de modelos
│   │   ├── session.py           # AsyncEngine + AsyncSessionLocal
│   │   └── init_db.py           # Seed inicial (admin user)
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── contact.py
│   │   ├── deal.py
│   │   ├── quote.py
│   │   ├── quote_item.py
│   │   ├── service.py
│   │   └── activity.py
│   ├── schemas/                 # Pydantic v2 schemas
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── contact.py
│   │   ├── deal.py
│   │   ├── quote.py
│   │   ├── quote_item.py
│   │   ├── service.py
│   │   ├── activity.py
│   │   └── auth.py
│   ├── crud/                    # Operaciones DB reutilizables
│   │   ├── base.py              # CRUDBase genérico
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── contact.py
│   │   ├── deal.py
│   │   ├── quote.py
│   │   └── activity.py
│   ├── routers/                 # Endpoints agrupados por entidad
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── companies.py
│   │   ├── contacts.py
│   │   ├── deals.py
│   │   ├── quotes.py
│   │   ├── services.py
│   │   ├── activities.py
│   │   └── dashboard.py
│   └── utils/
│       ├── quote_pdf.py         # Generación PDF de cotización
│       └── quote_number.py      # Auto-generación COT-YYYY-NNN
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 3. Configuración Base (`core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CRM PYMES"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 horas

    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db

    MAX_ACTIVE_USERS: int = 10
    DEFAULT_CURRENCY: str = "USD"
    DEFAULT_TAX_RATE: float = 13.0  # % IVA Costa Rica

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 4. Modelos SQLAlchemy

### 4.1 User
```python
class User(Base):
    __tablename__ = "users"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name       = Column(String(150), nullable=False)
    email      = Column(String(200), unique=True, index=True, nullable=False)
    hashed_pw  = Column(String, nullable=False)
    role       = Column(Enum("admin","vendedor","visualizador"), default="vendedor")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deals      = relationship("Deal", back_populates="owner")
    activities = relationship("Activity", back_populates="owner")
```

### 4.2 Company
```python
class Company(Base):
    __tablename__ = "companies"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name       = Column(String(200), nullable=False, index=True)
    industry   = Column(String(100))
    website    = Column(String(255))
    country    = Column(String(100))
    city       = Column(String(100))
    source     = Column(Enum("referido","web","evento","llamada","otro"))
    notes      = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contacts   = relationship("Contact", back_populates="company", cascade="all, delete")
    deals      = relationship("Deal", back_populates="company")
```

### 4.3 Contact
```python
class Contact(Base):
    __tablename__ = "contacts"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    email      = Column(String(200), index=True)
    phone      = Column(String(50))
    role       = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company    = relationship("Company", back_populates="contacts")
```

### 4.4 Deal
```python
class Deal(Base):
    __tablename__ = "deals"
    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id          = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    contact_id          = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    owner_id            = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title               = Column(String(200), nullable=False)
    stage               = Column(Enum("prospecto","calificado","propuesta",
                                      "negociacion","ganado","perdido"),
                                 default="prospecto")
    estimated_value     = Column(Numeric(12,2), default=0)
    probability         = Column(Integer, default=10)
    expected_close_date = Column(Date)
    notes               = Column(Text)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    company    = relationship("Company", back_populates="deals")
    owner      = relationship("User", back_populates="deals")
    quotes     = relationship("Quote", back_populates="deal", cascade="all, delete")
    activities = relationship("Activity", back_populates="deal")
```

### 4.5 Quote
```python
class Quote(Base):
    __tablename__ = "quotes"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    deal_id      = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    quote_number = Column(String(50), unique=True, index=True)
    status       = Column(Enum("borrador","enviada","aceptada","rechazada","expirada"),
                          default="borrador")
    valid_until  = Column(Date)
    subtotal     = Column(Numeric(12,2), default=0)
    tax_rate     = Column(Numeric(5,2), default=13.0)
    total        = Column(Numeric(12,2), default=0)
    currency     = Column(String(3), default="USD")
    notes        = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    sent_at      = Column(DateTime(timezone=True))

    deal  = relationship("Deal", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete")
```

### 4.6 QuoteItem
```python
class QuoteItem(Base):
    __tablename__ = "quote_items"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    quote_id    = Column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=False)
    service_id  = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True)
    description = Column(Text, nullable=False)
    quantity    = Column(Numeric(10,2), default=1)
    unit_price  = Column(Numeric(12,2), nullable=False)
    line_total  = Column(Numeric(12,2), nullable=False)  # computed on save

    quote   = relationship("Quote", back_populates="items")
    service = relationship("Service")
```

### 4.7 Service
```python
class Service(Base):
    __tablename__ = "services"
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name          = Column(String(200), nullable=False)
    description   = Column(Text)
    default_price = Column(Numeric(12,2), nullable=False)
    unit          = Column(String(50), default="proyecto")
    is_active     = Column(Boolean, default=True)
```

### 4.8 Activity
```python
class Activity(Base):
    __tablename__ = "activities"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    deal_id      = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True)
    contact_id   = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)
    owner_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type         = Column(Enum("llamada","email","reunion","tarea","nota"), nullable=False)
    subject      = Column(String(200), nullable=False)
    description  = Column(Text)
    due_date     = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    deal    = relationship("Deal", back_populates="activities")
    owner   = relationship("User", back_populates="activities")
```

---

## 5. Esquemas Pydantic v2 (ejemplo: Quote)

```python
from pydantic import BaseModel, computed_field
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum

class QuoteStatus(str, Enum):
    borrador   = "borrador"
    enviada    = "enviada"
    aceptada   = "aceptada"
    rechazada  = "rechazada"
    expirada   = "expirada"

class QuoteItemCreate(BaseModel):
    service_id:  Optional[UUID] = None
    description: str
    quantity:    Decimal
    unit_price:  Decimal

class QuoteCreate(BaseModel):
    deal_id:     UUID
    valid_until: date
    tax_rate:    Decimal = Decimal("13.0")
    currency:    str = "USD"
    notes:       Optional[str] = None
    items:       List[QuoteItemCreate]

class QuoteRead(BaseModel):
    id:           UUID
    quote_number: str
    status:       QuoteStatus
    subtotal:     Decimal
    tax_rate:     Decimal
    total:        Decimal
    currency:     str
    valid_until:  date
    created_at:   datetime
    sent_at:      Optional[datetime]
    items:        List[QuoteItemRead]

    model_config = {"from_attributes": True}
```

---

## 6. Endpoints por Router

### Auth — `/api/v1/auth`
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/login` | Login → devuelve JWT access token |
| POST | `/refresh` | Refresca token activo |
| GET | `/me` | Perfil del usuario autenticado |

### Users — `/api/v1/users`
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/` | admin | Listar usuarios activos |
| POST | `/` | admin | Crear usuario (valida MAX_ACTIVE_USERS) |
| GET | `/{id}` | admin | Obtener usuario |
| PATCH | `/{id}` | admin | Actualizar usuario |
| DELETE | `/{id}` | admin | Desactivar usuario (soft delete) |

### Companies — `/api/v1/companies`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar con paginación y búsqueda |
| POST | `/` | Crear empresa |
| GET | `/{id}` | Detalle + contactos + deals |
| PATCH | `/{id}` | Actualizar |
| DELETE | `/{id}` | Eliminar (soft delete) |

### Contacts — `/api/v1/contacts`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar (filtro por company_id) |
| POST | `/` | Crear contacto |
| GET | `/{id}` | Detalle |
| PATCH | `/{id}` | Actualizar |
| DELETE | `/{id}` | Eliminar |

### Deals — `/api/v1/deals`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar (filtros: stage, owner, empresa) |
| POST | `/` | Crear negocio |
| GET | `/{id}` | Detalle + quotes + activities |
| PATCH | `/{id}` | Actualizar (incluyendo cambio de stage) |
| DELETE | `/{id}` | Eliminar |
| PATCH | `/{id}/stage` | Cambiar etapa del pipeline |

### Quotes — `/api/v1/quotes`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar (filtro por deal_id, status) |
| POST | `/` | Crear cotización (auto-genera quote_number) |
| GET | `/{id}` | Detalle completo con items |
| PATCH | `/{id}` | Actualizar borrador |
| POST | `/{id}/send` | Marcar como enviada + registra sent_at |
| PATCH | `/{id}/status` | Cambiar status (aceptada/rechazada) |
| GET | `/{id}/pdf` | Descargar PDF de la cotización |
| DELETE | `/{id}` | Eliminar (solo borradores) |

### Services — `/api/v1/services`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar servicios activos |
| POST | `/` | Crear servicio (admin) |
| PATCH | `/{id}` | Actualizar |
| DELETE | `/{id}` | Desactivar |

### Activities — `/api/v1/activities`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar (filtro: deal_id, owner, tipo) |
| POST | `/` | Registrar actividad |
| PATCH | `/{id}` | Actualizar |
| PATCH | `/{id}/complete` | Marcar como completada |
| DELETE | `/{id}` | Eliminar |

### Dashboard — `/api/v1/dashboard`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/summary` | KPIs: pipeline total, tasa cierre, deals por etapa |
| GET | `/pipeline` | Deals agrupados por stage con valor total |
| GET | `/activities/pending` | Actividades pendientes del usuario |
| GET | `/quotes/recent` | Últimas 10 cotizaciones |

---

## 7. Autenticación y Autorización

```python
# core/security.py
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# core/deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    ...  # decode JWT → buscar user → validar is_active

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return current_user
```

**Reglas por rol:**

| Acción | admin | vendedor | visualizador |
|---|---|---|---|
| Ver todo | ✅ | ✅ (propio) | ✅ (lectura) |
| Crear/Editar | ✅ | ✅ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ |
| Eliminar registros | ✅ | ❌ | ❌ |

---

## 8. Lógica de Negocio Clave

### Auto-generación de número de cotización
```python
# utils/quote_number.py
async def generate_quote_number(db: AsyncSession) -> str:
    year = datetime.now().year
    result = await db.execute(
        select(func.count(Quote.id)).where(
            extract("year", Quote.created_at) == year
        )
    )
    count = result.scalar() + 1
    return f"COT-{year}-{count:03d}"
```

### Cálculo automático de totales
```python
def recalculate_quote_totals(quote: Quote) -> None:
    subtotal = sum(item.quantity * item.unit_price for item in quote.items)
    for item in quote.items:
        item.line_total = item.quantity * item.unit_price
    quote.subtotal = subtotal
    quote.total = subtotal * (1 + quote.tax_rate / 100)
```

### Validación de límite de usuarios
```python
async def validate_user_limit(db: AsyncSession) -> None:
    count = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    if count >= settings.MAX_ACTIVE_USERS:
        raise HTTPException(400, "Limite de 10 usuarios activos alcanzado")
```

---

## 9. Docker Compose

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: crm
      POSTGRES_PASSWORD: crm_secret
      POSTGRES_DB: crm_db
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      DATABASE_URL: postgresql+asyncpg://crm:crm_secret@db/crm_db
      SECRET_KEY: supersecretkey
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  pg_data:
```

---

## 10. Variables de Entorno (`.env`)

```env
DATABASE_URL=postgresql+asyncpg://crm:crm_secret@localhost:5432/crm_db
SECRET_KEY=cambia_esto_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
MAX_ACTIVE_USERS=10
DEFAULT_CURRENCY=USD
DEFAULT_TAX_RATE=13.0
```

---

## 11. Convenciones y Estándares

- **UUID v4** como primary key en todas las tablas
- **Soft delete** en User y Company (campo `is_active`)
- **Timestamps** en UTC con timezone
- **Paginación** estándar: `?skip=0&limit=20`
- **Búsqueda** vía `?q=texto` en listados de Company, Contact y Deal
- **Respuestas de error** estandarizadas: `{"detail": "mensaje"}`
- **CORS** habilitado para `http://localhost:5173` (Vite dev) y dominio de producción

---

*CRM PYMES Servicios — Backend Spec v1.0 · Bemantis CRM*
