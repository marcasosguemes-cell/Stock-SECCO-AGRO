"""
PRUEBA DE CONEXIÓN CON SUPABASE
Ejecutar este archivo para verificar la conexión
"""

import streamlit as st
from supabase import create_client
import os

# Configuración de la página
st.set_page_config(page_title="Test Supabase", page_icon="🔌")

st.title("🔌 Prueba de Conexión con Supabase")

# Cargar secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
    st.success("✅ Secrets cargados correctamente")
    st.write(f"URL: {SUPABASE_URL}")
except Exception as e:
    st.error(f"❌ Error cargando secrets: {e}")
    st.stop()

# Crear cliente
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    st.success("✅ Cliente Supabase creado correctamente")
except Exception as e:
    st.error(f"❌ Error creando cliente: {e}")
    st.stop()

st.markdown("---")

# PRUEBA 1: Leer la tabla usuarios
st.subheader("📋 PRUEBA 1: Leer tabla 'usuarios'")

try:
    usuarios = supabase.table("usuarios").select("*").execute()
    st.success(f"✅ Conexión exitosa! Se encontraron {len(usuarios.data)} usuarios")
    
    if usuarios.data:
        st.write("Usuarios encontrados:")
        for user in usuarios.data:
            st.write(f"  - ID: {user['id']}")
            st.write(f"    Nombre: {user.get('nombre', 'Sin nombre')}")
            st.write(f"    Rol: {user.get('rol', 'Sin rol')}")
            st.write("---")
    else:
        st.warning("⚠️ No hay usuarios en la tabla 'usuarios'")
        
except Exception as e:
    st.error(f"❌ Error leyendo tabla usuarios: {e}")

st.markdown("---")

# PRUEBA 2: Listar tablas disponibles
st.subheader("📁 PRUEBA 2: Verificar tablas disponibles")

tablas_a_verificar = ["usuarios", "establecimientos", "categorias", "productos", "proveedores", "movimientos"]

for tabla in tablas_a_verificar:
    try:
        result = supabase.table(tabla).select("*").limit(1).execute()
        st.success(f"✅ Tabla '{tabla}' existe")
    except Exception as e:
        st.error(f"❌ Tabla '{tabla}' no existe o error: {e}")

st.markdown("---")

# PRUEBA 3: Autenticación con usuario específico
st.subheader("🔐 PRUEBA 3: Probar autenticación")

with st.form("test_login"):
    email = st.text_input("Email", placeholder="usuario@ejemplo.com")
    password = st.text_input("Contraseña", type="password")
    submitted = st.form_submit_button("Probar Login")
    
    if submitted:
        st.write(f"Intentando login con: {email}")
        
        try:
            # Intentar login
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            st.success(f"✅ Login exitoso!")
            st.write(f"User ID: {auth_response.user.id}")
            st.write(f"Email: {auth_response.user.email}")
            
            # Buscar en tabla usuarios
            st.write("---")
            st.write("Buscando en tabla 'usuarios'...")
            
            perfil = supabase.table("usuarios").select("*").eq("id", auth_response.user.id).execute()
            
            if perfil.data:
                st.success(f"✅ Usuario encontrado en tabla 'usuarios'!")
                st.write(f"Datos: {perfil.data[0]}")
            else:
                st.error(f"❌ Usuario NO encontrado en tabla 'usuarios'")
                st.write(f"Buscando con ID: {auth_response.user.id}")
                
                # Mostrar todos los IDs disponibles
                todos = supabase.table("usuarios").select("id, nombre").execute()
                st.write("IDs disponibles en tabla usuarios:")
                for u in todos.data:
                    st.write(f"  - {u['id']} → {u.get('nombre', 'Sin nombre')}")
                    
        except Exception as e:
            st.error(f"❌ Error en login: {e}")
            
            # Si el error es de credenciales
            if "Invalid login credentials" in str(e):
                st.error("Credenciales incorrectas. Verifica email y contraseña.")
            elif "Email not confirmed" in str(e):
                st.error("Email no confirmado. Revisa tu bandeja de entrada.")
            else:
                st.write(f"Detalle del error: {e}")

st.markdown("---")

# PRUEBA 4: Verificar usuarios de autenticación
st.subheader("👥 PRUEBA 4: Usuarios en Authentication")

st.info("""
Para ver los usuarios de autenticación, ve al panel de Supabase:
1. Ve a Authentication → Users
2. Allí verás los emails registrados
3. Compara los IDs con los de la tabla 'usuarios'
""")

st.write("**Usuarios que deberías tener en Authentication:**")
st.write("- admin@seccoagro.com.ar")
st.write("- emanino@seccoagro.com.ar")
st.write("- gdefagot@seccoagro.com.ar")

st.write("**En la tabla 'usuarios' necesitas tener registros con los mismos IDs**")