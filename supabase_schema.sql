-- ============================================================
-- SISTEMA DE CONTROL DE STOCK AGRÍCOLA
-- Schema para Supabase / PostgreSQL
-- ============================================================

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA: establecimientos
-- ============================================================
CREATE TABLE establecimientos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO establecimientos (nombre) VALUES
  ('La Sonia'),
  ('San Guillermo'),
  ('Camba Pora');

-- ============================================================
-- TABLA: usuarios (extiende Supabase Auth)
-- ============================================================
CREATE TABLE usuarios (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  rol TEXT NOT NULL CHECK (rol IN ('admin', 'establecimiento')),
  establecimiento_id UUID REFERENCES establecimientos(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLA: categorias
-- ============================================================
CREATE TABLE categorias (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre TEXT NOT NULL UNIQUE
);

INSERT INTO categorias (nombre) VALUES
  ('Semillas'),
  ('Agroquímicos'),
  ('Fertilizantes');

-- ============================================================
-- TABLA: productos (subitems)
-- ============================================================
CREATE TABLE productos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  categoria_id UUID NOT NULL REFERENCES categorias(id),
  nombre TEXT NOT NULL,
  activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(categoria_id, nombre)
);

-- ---- SEMILLAS ----
WITH cat AS (SELECT id FROM categorias WHERE nombre = 'Semillas')
INSERT INTO productos (categoria_id, nombre) VALUES
  ((SELECT id FROM cat), 'Sorgo p/silo - Tobin 62T'),
  ((SELECT id FROM cat), 'Sorgo Granífero Ciclo Largo'),
  ((SELECT id FROM cat), 'Sorgo Silero Padrillo - Tobin curado Concept+Cruiser'),
  ((SELECT id FROM cat), 'Tobin Facon'),
  ((SELECT id FROM cat), 'Barluz barenbrug (fotosensitivo)'),
  ((SELECT id FROM cat), 'Sorgo Forrajero - BMeRre FotoS. SAC500/700 SIN CURAR'),
  ((SELECT id FROM cat), 'Sorgo Forrajero - Talero Tobin SIN CURAR'),
  ((SELECT id FROM cat), 'Maíz 1era BOLSA - DK 73-10 VT3 X 80M (BANDA 1)'),
  ((SELECT id FROM cat), 'Maíz Tardío BOLSA - DK 77-100 VT3 X 60M'),
  ((SELECT id FROM cat), 'Maíz REFUGIO - DK 77-10 RR2 X 60M'),
  ((SELECT id FROM cat), 'Maíz HIJO de RR p/PASTOREO - BOLSA'),
  ((SELECT id FROM cat), 'Soja DM 61I61 IPRO STS curada + fungicida'),
  ((SELECT id FROM cat), 'Avena Strigosa - Kg.'),
  ((SELECT id FROM cat), 'Avena Strigosa Goujon - Kg.'),
  ((SELECT id FROM cat), 'Avena Negra Económica - Kg.'),
  ((SELECT id FROM cat), 'Avena Mana-Inta - Kg.'),
  ((SELECT id FROM cat), 'Melilotus Albus - Kg.'),
  ((SELECT id FROM cat), 'Vicia Villosa - Kg.'),
  ((SELECT id FROM cat), 'Rye Grass Diploide - LE284 - Kg.'),
  ((SELECT id FROM cat), 'Rye Grass Diploide - LE284 No fiscalizado - Kg.'),
  ((SELECT id FROM cat), 'Rye Grass Tetraploide - Inta - Kg.'),
  ((SELECT id FROM cat), 'Rye Grass Tetraploide - Don Gianni - Kg.'),
  ((SELECT id FROM cat), 'Rye Grass Tetraploide - Jumbo - Kg.'),
  ((SELECT id FROM cat), 'Alfalfa RR BOLSA BLANCA - Kg.'),
  ((SELECT id FROM cat), 'Alfalfa WL922 HVX.RR - Kg.'),
  ((SELECT id FROM cat), 'Alfalfa WL919 - Kg.'),
  ((SELECT id FROM cat), 'Gatton Panic - Kg.'),
  ((SELECT id FROM cat), 'Pasto Siam - Kg.'),
  ((SELECT id FROM cat), 'Brachiaria Brizanta Toledo - Kg.'),
  ((SELECT id FROM cat), 'Brachiaria Mulato II - Kg.'),
  ((SELECT id FROM cat), 'Brachiaria Hibrida Mavuno - Kg.'),
  ((SELECT id FROM cat), 'Brachiaria Humidícola - Kg.'),
  ((SELECT id FROM cat), 'Brachiaria Marandú - Kg.'),
  ((SELECT id FROM cat), 'Gramma Rhodes Katambora - Kg.'),
  ((SELECT id FROM cat), 'Gramma Rhodes Épica - Kg.'),
  ((SELECT id FROM cat), 'Gramma Rhodes Reclaimer - Kg.'),
  ((SELECT id FROM cat), 'Gramma Rhodes Callide - Kg.'),
  ((SELECT id FROM cat), 'Dicantium Rastrero - Kg.'),
  ((SELECT id FROM cat), 'Setaria Narok - Kg.'),
  ((SELECT id FROM cat), 'Curasemilla c/inocul x kg.'),
  ((SELECT id FROM cat), 'Funguicida - Litro');

-- ---- AGROQUÍMICOS ----
WITH cat AS (SELECT id FROM categorias WHERE nombre = 'Agroquímicos')
INSERT INTO productos (categoria_id, nombre) VALUES
  ((SELECT id FROM cat), 'Glifosato al 60% (Panzer Gold) - Litro'),
  ((SELECT id FROM cat), 'Glifosato al 66% - Litro (Round Up Full II)'),
  ((SELECT id FROM cat), 'Glifosato al 74% - Kg.'),
  ((SELECT id FROM cat), 'Tordon D30 (Picloran + 2.4D)'),
  ((SELECT id FROM cat), 'Picloran - Tordon 24K'),
  ((SELECT id FROM cat), 'Tocon'),
  ((SELECT id FROM cat), 'Pastar'),
  ((SELECT id FROM cat), 'Sendero'),
  ((SELECT id FROM cat), 'Sulfato de Amonio - Kg./Litro'),
  ((SELECT id FROM cat), 'Flumioxazin 48% Litro'),
  ((SELECT id FROM cat), 'Atrazina Líquida al 50% - Lts.'),
  ((SELECT id FROM cat), 'Dicamba'),
  ((SELECT id FROM cat), '2,4 D Amina 48% - litro'),
  ((SELECT id FROM cat), '2,4 D Amina 60% - litro'),
  ((SELECT id FROM cat), '2,4 DB - (para Alfalfa)'),
  ((SELECT id FROM cat), 'Trifluarlina - Premerge ADAMA'),
  ((SELECT id FROM cat), 'Flumetsulam - Preside (Alfalfa)'),
  ((SELECT id FROM cat), 'Imazetapir - Pivot Basf'),
  ((SELECT id FROM cat), 'Fluoxipir - Starane Xtra Dow'),
  ((SELECT id FROM cat), 'Acetoclor'),
  ((SELECT id FROM cat), 'Sempra'),
  ((SELECT id FROM cat), 'Metsulfuron - Kg.'),
  ((SELECT id FROM cat), 'Basagran'),
  ((SELECT id FROM cat), 'Galant HL - Haloxyfop'),
  ((SELECT id FROM cat), 'Latium o Select (Cletodim)'),
  ((SELECT id FROM cat), 'Concep'),
  ((SELECT id FROM cat), 'Paraquat (secador de soja)'),
  ((SELECT id FROM cat), 'S-Metolacloro (Control de Gramíneas) - CURAR'),
  ((SELECT id FROM cat), 'Cruiser'),
  ((SELECT id FROM cat), 'Acefato'),
  ((SELECT id FROM cat), 'Bronco - Tiodicarb (Cura semilla)'),
  ((SELECT id FROM cat), 'Cipermetrina 25%'),
  ((SELECT id FROM cat), 'Ampligo (Lamda+clorantniliprole) - Insecticida'),
  ((SELECT id FROM cat), 'Cilambda - Lambdacialotrina 25% - Insecticida'),
  ((SELECT id FROM cat), 'Timerol Plus o ESUS - Insecticida'),
  ((SELECT id FROM cat), 'Abacmetina'),
  ((SELECT id FROM cat), 'Nomolt (IGR) TEFLUBENZURON'),
  ((SELECT id FROM cat), 'Intrepid (IGR) - Metoxifenocide'),
  ((SELECT id FROM cat), 'Clorpirifos (Lorsban)'),
  ((SELECT id FROM cat), 'Gloster (Dimetoato 37,6%)'),
  ((SELECT id FROM cat), 'Imidacloprid - Insecticida'),
  ((SELECT id FROM cat), 'Patton Flow (Pirimicarb 50%) - Insecticida (Control Pulgones)'),
  ((SELECT id FROM cat), 'Opera - Fungicida'),
  ((SELECT id FROM cat), 'Tebuzim - Fungicida (Soja)'),
  ((SELECT id FROM cat), 'Amistar Extra Gold - Fungicida'),
  ((SELECT id FROM cat), 'Alcohol etoxilado'),
  ((SELECT id FROM cat), 'Corrector de PH'),
  ((SELECT id FROM cat), 'Emultec'),
  ((SELECT id FROM cat), 'Aceite Mineral - Caddet - Litro'),
  ((SELECT id FROM cat), 'Aceite Mineral YPF - Litro'),
  ((SELECT id FROM cat), 'Aceite Vegetal - Litro');

-- ---- FERTILIZANTES ----
WITH cat AS (SELECT id FROM categorias WHERE nombre = 'Fertilizantes')
INSERT INTO productos (categoria_id, nombre) VALUES
  ((SELECT id FROM cat), 'Urea - Kg.'),
  ((SELECT id FROM cat), 'Sulfan (YARA - reempl. Urea o nitro doble) Kg.'),
  ((SELECT id FROM cat), 'Cloruro de potasio Kg.'),
  ((SELECT id FROM cat), 'DAP - Kg. (18N - 46P)'),
  ((SELECT id FROM cat), 'Nitro Complex (YARA - reempl. DAP) Kg.'),
  ((SELECT id FROM cat), 'MAP - Kg. (12N - 52P)'),
  ((SELECT id FROM cat), 'Sulfato de Potasio y Magnesio'),
  ((SELECT id FROM cat), 'Super fosfato simple (0N - 21P - 12S)'),
  ((SELECT id FROM cat), 'NPS (7N-40P-0+5S+10Ca)'),
  ((SELECT id FROM cat), 'Superfosfato triple de calcio SFT - Kg. (0N - 46P - 14Ca)');

-- ============================================================
-- TABLA: proveedores
-- ============================================================
CREATE TABLE proveedores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre TEXT NOT NULL UNIQUE,
  activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLA: stock
-- Stock actual por producto + establecimiento + lote (fecha vto.)
-- ============================================================
CREATE TABLE stock (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  producto_id UUID NOT NULL REFERENCES productos(id),
  establecimiento_id UUID NOT NULL REFERENCES establecimientos(id),
  cantidad NUMERIC(12,3) NOT NULL DEFAULT 0,
  presentacion TEXT,
  marca TEXT,
  concentracion TEXT,
  fecha_vencimiento DATE,
  stock_minimo NUMERIC(12,3) DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLA: movimientos
-- Registro de todos los ingresos y egresos
-- ============================================================
CREATE TABLE movimientos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tipo TEXT NOT NULL CHECK (tipo IN ('ingreso', 'egreso')),
  producto_id UUID NOT NULL REFERENCES productos(id),
  establecimiento_id UUID NOT NULL REFERENCES establecimientos(id),
  cantidad NUMERIC(12,3) NOT NULL,
  presentacion TEXT,
  marca TEXT,
  concentracion TEXT,
  fecha_vencimiento DATE,

  -- Campos de ingreso
  origen_tipo TEXT CHECK (origen_tipo IN ('proveedor', 'traslado', NULL)),
  proveedor_id UUID REFERENCES proveedores(id),
  origen_establecimiento_id UUID REFERENCES establecimientos(id),
  numero_factura TEXT,
  fecha_factura DATE,

  -- Campos de egreso
  destino_tipo TEXT CHECK (destino_tipo IN ('uso', 'traslado', NULL)),
  destino_establecimiento_id UUID REFERENCES establecimientos(id),
  numero_remito TEXT,
  observaciones TEXT,

  -- Metadatos
  fecha DATE NOT NULL DEFAULT CURRENT_DATE,
  usuario_id UUID REFERENCES usuarios(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- FUNCIÓN: actualizar stock automáticamente al insertar movimiento
-- ============================================================
CREATE OR REPLACE FUNCTION actualizar_stock()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.tipo = 'ingreso' THEN
    INSERT INTO stock (producto_id, establecimiento_id, cantidad, presentacion, marca, concentracion, fecha_vencimiento)
    VALUES (NEW.producto_id, NEW.establecimiento_id, NEW.cantidad, NEW.presentacion, NEW.marca, NEW.concentracion, NEW.fecha_vencimiento)
    ON CONFLICT (producto_id, establecimiento_id)
    DO UPDATE SET
      cantidad = stock.cantidad + NEW.cantidad,
      updated_at = NOW();
  ELSIF NEW.tipo = 'egreso' THEN
    UPDATE stock
    SET cantidad = GREATEST(0, cantidad - NEW.cantidad),
        updated_at = NOW()
    WHERE producto_id = NEW.producto_id
      AND establecimiento_id = NEW.establecimiento_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_stock
AFTER INSERT ON movimientos
FOR EACH ROW EXECUTE FUNCTION actualizar_stock();

-- Constraint único para stock por producto+establecimiento
ALTER TABLE stock ADD CONSTRAINT uq_stock_producto_estab
  UNIQUE (producto_id, establecimiento_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS) — Supabase
-- ============================================================
ALTER TABLE movimientos ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Admin ve todo
CREATE POLICY "admin_all_movimientos" ON movimientos
  FOR ALL USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND rol = 'admin')
  );

CREATE POLICY "admin_all_stock" ON stock
  FOR ALL USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND rol = 'admin')
  );

-- Usuario de establecimiento: solo su establecimiento
CREATE POLICY "estab_own_movimientos" ON movimientos
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM usuarios
      WHERE id = auth.uid()
        AND rol = 'establecimiento'
        AND establecimiento_id = movimientos.establecimiento_id
    )
  );

CREATE POLICY "estab_own_stock" ON stock
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios
      WHERE id = auth.uid()
        AND rol = 'establecimiento'
        AND establecimiento_id = stock.establecimiento_id
    )
  );

-- Tablas de referencia: lectura pública autenticada
ALTER TABLE productos ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE establecimientos ENABLE ROW LEVEL SECURITY;
ALTER TABLE proveedores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "read_productos" ON productos FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "read_categorias" ON categorias FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "read_establecimientos" ON establecimientos FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "read_proveedores" ON proveedores FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "admin_write_productos" ON productos FOR ALL USING (
  EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND rol = 'admin')
);
CREATE POLICY "admin_write_proveedores" ON proveedores FOR ALL USING (
  EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND rol = 'admin')
);

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: stock con nombres legibles + alerta de vencimiento
CREATE VIEW v_stock_completo AS
SELECT
  s.id,
  e.nombre AS establecimiento,
  c.nombre AS categoria,
  p.nombre AS producto,
  s.cantidad,
  s.presentacion,
  s.marca,
  s.concentracion,
  s.fecha_vencimiento,
  s.stock_minimo,
  CASE
    WHEN s.fecha_vencimiento IS NOT NULL AND s.fecha_vencimiento <= CURRENT_DATE + 30 THEN 'vence_pronto'
    WHEN s.fecha_vencimiento IS NOT NULL AND s.fecha_vencimiento <= CURRENT_DATE THEN 'vencido'
    WHEN s.cantidad <= s.stock_minimo THEN 'stock_bajo'
    ELSE 'ok'
  END AS alerta,
  s.updated_at
FROM stock s
JOIN productos p ON p.id = s.producto_id
JOIN categorias c ON c.id = p.categoria_id
JOIN establecimientos e ON e.id = s.establecimiento_id
WHERE s.cantidad > 0;

-- Vista: movimientos con nombres legibles
CREATE VIEW v_movimientos_completo AS
SELECT
  m.id,
  m.tipo,
  m.fecha,
  e.nombre AS establecimiento,
  c.nombre AS categoria,
  p.nombre AS producto,
  m.cantidad,
  m.presentacion,
  m.marca,
  m.concentracion,
  m.fecha_vencimiento,
  m.origen_tipo,
  prov.nombre AS proveedor,
  eorig.nombre AS origen_establecimiento,
  m.numero_factura,
  m.fecha_factura,
  m.destino_tipo,
  edest.nombre AS destino_establecimiento,
  m.numero_remito,
  m.observaciones,
  u.nombre AS usuario,
  m.created_at
FROM movimientos m
JOIN productos p ON p.id = m.producto_id
JOIN categorias c ON c.id = p.categoria_id
JOIN establecimientos e ON e.id = m.establecimiento_id
LEFT JOIN proveedores prov ON prov.id = m.proveedor_id
LEFT JOIN establecimientos eorig ON eorig.id = m.origen_establecimiento_id
LEFT JOIN establecimientos edest ON edest.id = m.destino_establecimiento_id
LEFT JOIN usuarios u ON u.id = m.usuario_id
ORDER BY m.created_at DESC;
