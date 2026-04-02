-- ============================================================
-- SkiRent Manager — Schema para Supabase (PostgreSQL)
-- Ejecutar en: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- 1. OFICINAS
CREATE TABLE IF NOT EXISTS oficinas (
    id     SERIAL PRIMARY KEY,
    nombre TEXT   UNIQUE NOT NULL,
    ciudad TEXT   NOT NULL
);

-- 2. CATEGORÍAS (gestionadas desde la app)
CREATE TABLE IF NOT EXISTS categorias (
    id     SERIAL PRIMARY KEY,
    nombre TEXT   UNIQUE NOT NULL
);

-- 3. INVENTARIO
CREATE TABLE IF NOT EXISTS inventario (
    id             SERIAL PRIMARY KEY,
    categoria      TEXT    NOT NULL,
    talle          TEXT    NOT NULL,
    color          TEXT    NOT NULL,
    oficina_actual INTEGER NOT NULL REFERENCES oficinas(id),
    estado         TEXT    NOT NULL DEFAULT 'Disponible'
                           CHECK (estado IN ('Disponible','Alquilado','Mantenimiento')),
    fecha_registro TEXT    NOT NULL
);

-- 4. MOVIMIENTOS (historial)
CREATE TABLE IF NOT EXISTS movimientos (
    id           SERIAL PRIMARY KEY,
    item_id      INTEGER NOT NULL REFERENCES inventario(id),
    tipo         TEXT    NOT NULL,
    oficina_orig INTEGER REFERENCES oficinas(id),
    oficina_dest INTEGER REFERENCES oficinas(id),
    fecha        TEXT    NOT NULL,
    notas        TEXT
);

-- ============================================================
-- DATOS SEMILLA
-- ============================================================

-- Oficinas iniciales
INSERT INTO oficinas (nombre, ciudad) VALUES
    ('Rios Andinos Aristides', 'Mendoza'),
    ('Rios Andinos Italia',    'Mendoza')
ON CONFLICT (nombre) DO NOTHING;

-- Categorías por defecto (pueden editarse/borrarse desde la app)
INSERT INTO categorias (nombre) VALUES
    ('Campera'),
    ('Pantalón'),
    ('Enterito'),
    ('Zapatos')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================
-- ÍNDICES para mejor performance en filtros frecuentes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_inventario_estado    ON inventario(estado);
CREATE INDEX IF NOT EXISTS idx_inventario_oficina   ON inventario(oficina_actual);
CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario(categoria);
CREATE INDEX IF NOT EXISTS idx_movimientos_fecha    ON movimientos(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_movimientos_item     ON movimientos(item_id);

-- ============================================================
-- ROW LEVEL SECURITY — habilitar si usás autenticación
-- (Opcional: comentar si querés acceso libre por ahora)
-- ============================================================
-- ALTER TABLE oficinas   ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE inventario ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE movimientos ENABLE ROW LEVEL SECURITY;
