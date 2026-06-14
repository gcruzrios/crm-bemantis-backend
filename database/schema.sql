-- ============================================================
-- Bemantis CRM — Esquema PostgreSQL
-- PYME Servicios · Flujo: Prospecto → Cotización
-- ============================================================

-- Extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TIPOS ENUM
-- ============================================================

CREATE TYPE company_source AS ENUM (
    'referido',
    'web',
    'evento',
    'redes_sociales',
    'publicidad',
    'otro'
);

CREATE TYPE user_role AS ENUM (
    'admin',
    'vendedor',
    'visualizador'
);

CREATE TYPE deal_stage AS ENUM (
    'prospecto',
    'calificado',
    'propuesta',
    'negociacion',
    'ganado',
    'perdido'
);

CREATE TYPE quote_status AS ENUM (
    'borrador',
    'enviada',
    'aceptada',
    'rechazada',
    'expirada'
);

CREATE TYPE activity_type AS ENUM (
    'llamada',
    'email',
    'reunion',
    'tarea',
    'nota'
);

-- ============================================================
-- TABLAS
-- ============================================================

-- 3.8 Users — Usuarios del CRM (máx. 10 activos)
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(150)  NOT NULL,
    email       VARCHAR(200)  NOT NULL UNIQUE,
    role        user_role     NOT NULL DEFAULT 'vendedor',
    is_active   BOOLEAN       NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- 3.1 Companies — Empresa cliente
CREATE TABLE companies (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(200)  NOT NULL,
    industry    VARCHAR(100),
    website     VARCHAR(255),
    country     VARCHAR(100),
    city        VARCHAR(100),
    source      company_source,
    notes       TEXT,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- 3.2 Contacts — Persona de contacto
CREATE TABLE contacts (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id  UUID          NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    first_name  VARCHAR(100)  NOT NULL,
    last_name   VARCHAR(100)  NOT NULL,
    email       VARCHAR(200),
    phone       VARCHAR(50),
    role        VARCHAR(100),
    is_primary  BOOLEAN       NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- 3.3 Deals — Negocio / Oportunidad
CREATE TABLE deals (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id          UUID            NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    contact_id          UUID            REFERENCES contacts(id) ON DELETE SET NULL,
    owner_id            UUID            NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title               VARCHAR(200)    NOT NULL,
    stage               deal_stage      NOT NULL DEFAULT 'prospecto',
    estimated_value     DECIMAL(12,2),
    probability         SMALLINT        CHECK (probability BETWEEN 0 AND 100),
    expected_close_date DATE,
    notes               TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 3.6 Services — Catálogo de servicios
CREATE TABLE services (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(200)  NOT NULL,
    description   TEXT,
    default_price DECIMAL(12,2),
    unit          VARCHAR(50),
    is_active     BOOLEAN       NOT NULL DEFAULT true
);

-- 3.4 Quotes — Cotización
CREATE TABLE quotes (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id      UUID          NOT NULL REFERENCES deals(id) ON DELETE RESTRICT,
    quote_number VARCHAR(50)   NOT NULL UNIQUE,
    status       quote_status  NOT NULL DEFAULT 'borrador',
    valid_until  DATE,
    subtotal     DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_rate     DECIMAL(5,2)  NOT NULL DEFAULT 0,
    total        DECIMAL(12,2) NOT NULL DEFAULT 0,
    currency     CHAR(3)       NOT NULL DEFAULT 'USD',
    notes        TEXT,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    sent_at      TIMESTAMPTZ
);

-- 3.5 QuoteItems — Líneas de cotización
CREATE TABLE quote_items (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quote_id    UUID            NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    service_id  UUID            REFERENCES services(id) ON DELETE SET NULL,
    description TEXT            NOT NULL,
    quantity    DECIMAL(10,2)   NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price  DECIMAL(12,2)   NOT NULL CHECK (unit_price >= 0),
    line_total  DECIMAL(12,2)   GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 3.7 Activities — Actividades y seguimiento
CREATE TABLE activities (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id      UUID          REFERENCES deals(id) ON DELETE SET NULL,
    contact_id   UUID          REFERENCES contacts(id) ON DELETE SET NULL,
    owner_id     UUID          NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    type         activity_type NOT NULL,
    subject      VARCHAR(200)  NOT NULL,
    description  TEXT,
    due_date     TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE INDEX idx_contacts_company_id    ON contacts(company_id);
CREATE INDEX idx_deals_company_id       ON deals(company_id);
CREATE INDEX idx_deals_contact_id       ON deals(contact_id);
CREATE INDEX idx_deals_owner_id         ON deals(owner_id);
CREATE INDEX idx_deals_stage            ON deals(stage);
CREATE INDEX idx_quotes_deal_id         ON quotes(deal_id);
CREATE INDEX idx_quotes_status          ON quotes(status);
CREATE INDEX idx_quote_items_quote_id   ON quote_items(quote_id);
CREATE INDEX idx_activities_deal_id     ON activities(deal_id);
CREATE INDEX idx_activities_contact_id  ON activities(contact_id);
CREATE INDEX idx_activities_owner_id    ON activities(owner_id);
CREATE INDEX idx_activities_due_date    ON activities(due_date) WHERE completed_at IS NULL;

-- ============================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================

-- Auto-actualiza updated_at en deals
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_deals_updated_at
    BEFORE UPDATE ON deals
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

-- Secuencia para numeración de cotizaciones
CREATE SEQUENCE quote_seq START 1;

-- Genera quote_number automáticamente si se omite (COT-YYYY-NNN)
CREATE OR REPLACE FUNCTION fn_generate_quote_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quote_number IS NULL OR NEW.quote_number = '' THEN
        NEW.quote_number := 'COT-' || TO_CHAR(NOW(), 'YYYY') || '-' ||
                            LPAD(NEXTVAL('quote_seq')::TEXT, 3, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_quotes_number
    BEFORE INSERT ON quotes
    FOR EACH ROW
    EXECUTE FUNCTION fn_generate_quote_number();

-- Límite de 10 usuarios activos
CREATE OR REPLACE FUNCTION fn_check_max_active_users()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_active = true AND (
        SELECT COUNT(*) FROM users WHERE is_active = true AND id <> COALESCE(OLD.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) >= 10 THEN
        RAISE EXCEPTION 'Límite alcanzado: no se permiten más de 10 usuarios activos.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_max_active
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION fn_check_max_active_users();
