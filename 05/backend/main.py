import os
import time
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Docker Microservices API")

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres123")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.on_event("startup")
def init_db():
    retries = 10
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visit_logs (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            break
        except Exception:
            retries -= 1
            time.sleep(2)

@app.get("/api/health")
def health_check():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        db_status = "Connected"
    except Exception as e:
        db_status = f"Disconnected: {str(e)}"

    return {
        "status": "online",
        "service": "Python FastAPI Backend",
        "database": db_status
    }

@app.get("/api/logs")
def get_logs():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, message, created_at FROM visit_logs ORDER BY created_at DESC LIMIT 10;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records

@app.post("/api/logs")
def add_log(payload: dict):
    msg = payload.get("message", "無訊息")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO visit_logs (message) VALUES (%s) RETURNING id;", (msg,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "id": new_id, "message": msg}
