from db_config import get_connection

try:
    conn = get_connection()
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)