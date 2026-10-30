import time
import aiosqlite
from typing import List, Dict, Any

DB_PATH = "syspulse.db"
_last_logged_time: float = 0.0
LOG_COOLDOWN_SEC: float = 15.0  # 至少間隔 15 秒才記錄下一筆異常峰值


async def init_db():
    """初始化異常監控資料表"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                culprit_pid INTEGER NOT NULL,
                culprit_name TEXT NOT NULL,
                culprit_cpu REAL NOT NULL,
                culprit_mem_mb REAL NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)
        await db.commit()


async def log_anomaly_if_needed(
    metric_type: str,
    metric_value: float,
    top_proc: Dict[str, Any]
) -> Dict[str, Any] | None:
    """當 CPU 或記憶體超標時，記錄造成負載的頭號程序（含冷卻機制）"""
    global _last_logged_time
    now = time.time()
    if now - _last_logged_time < LOG_COOLDOWN_SEC:
        return None

    _last_logged_time = now
    record = {
        "metric_type": metric_type,
        "metric_value": round(metric_value, 1),
        "culprit_pid": top_proc.get("pid", 0),
        "culprit_name": top_proc.get("name", "Unknown"),
        "culprit_cpu": round(top_proc.get("cpu_percent", 0.0), 1),
        "culprit_mem_mb": round(top_proc.get("memory_mb", 0.0), 1),
        "timestamp": int(now * 1000)
    }

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO anomaly_logs
               (metric_type, metric_value, culprit_pid, culprit_name, culprit_cpu, culprit_mem_mb, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record["metric_type"],
                record["metric_value"],
                record["culprit_pid"],
                record["culprit_name"],
                record["culprit_cpu"],
                record["culprit_mem_mb"],
                record["timestamp"]
            )
        )
        await db.commit()
    return record


async def get_recent_anomalies(limit: int = 30) -> List[Dict[str, Any]]:
    """取得最近 N 筆系統異常峰值紀錄"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM anomaly_logs ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]