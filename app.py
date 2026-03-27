-- Crear tabla de movimientos si no existe
CREATE TABLE IF NOT EXISTS movimientos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (tipo IN ('ingreso', 'egreso')),
    producto_id UUID NOT NULL,
    establecimiento_id UUID NOT NULL,
    cantidad NUMERIC NOT NULL,
    fecha DATE NOT NULL,
    proveedor_id UUID,
    observaciones TEXT,
    usuario_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear tabla de proveedores si no existe
CREATE TABLE IF NOT EXISTS proveedores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear tabla de categorías si no existe
CREATE TABLE IF NOT EXISTS categorias (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear tabla de productos si no existe
CREATE TABLE IF NOT EXISTS productos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria_id UUID REFERENCES categorias(id),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crear tabla de establecimientos si no existe
CREATE TABLE IF NOT EXISTS establecimientos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
