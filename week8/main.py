import asyncio
import json
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, log_anomaly_if_needed, get_recent_anomalies
from monitor import SystemTelemetryEngine, terminate_process_by_pid

telemetry = SystemTelemetryEngine()
active_clients: Set[WebSocket] = set()

# 預設告警門檻 (%)
cpu_alert_threshold: float = 80.0
mem_alert_threshold: float = 85.0


async def broadcast(payload: dict):
    if not active_clients:
        return
    text = json.dumps(payload)
    disconnected = set()
    for ws in active_clients:
        try:
            await ws.send_text(text)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        active_clients.discard(ws)


async def telemetry_loop():
    """常駐背景迴圈：每秒採樣硬體數據並檢查是否觸發異常紀錄"""
    while True:
        try:
            snap = telemetry.collect_snapshot()
            top_proc = snap["top_processes"][0] if snap["top_processes"] else {}

            anomaly_event = None
            if snap["cpu"]["total"] >= cpu_alert_threshold and top_proc:
                anomaly_event = await log_anomaly_if_needed("CPU 飆高", snap["cpu"]["total"], top_proc)
            elif snap["memory"]["percent"] >= mem_alert_threshold and top_proc:
                anomaly_event = await log_anomaly_if_needed("RAM 滿載", snap["memory"]["percent"], top_proc)

            await broadcast({
                "type": "telemetry",
                "data": snap,
                "new_anomaly": anomaly_event
            })
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Telemetry Error] {e}")

        await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(telemetry_loop())
    yield
    task.cancel()


app = FastAPI(title="SysPulse & NetGuard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/kill/{pid}")
async def kill_process(pid: int):
    """終止指定 PID 的程序"""
    return terminate_process_by_pid(pid)


@app.post("/api/thresholds")
async def set_thresholds(
    cpu: float = Query(80.0, ge=10.0, le=99.0),
    mem: float = Query(85.0, ge=10.0, le=99.0)
):
    """動態調整異常抓包門檻"""
    global cpu_alert_threshold, mem_alert_threshold
    cpu_alert_threshold = cpu
    mem_alert_threshold = mem
    return {"ok": True, "cpu_threshold": cpu_alert_threshold, "mem_threshold": mem_alert_threshold}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    active_clients.add(ws)
    try:
        # 初次連線發送歷史異常紀錄與當前門檻設定
        history = await get_recent_anomalies(30)
        await ws.send_text(json.dumps({
            "type": "init",
            "cpu_threshold": cpu_alert_threshold,
            "mem_threshold": mem_alert_threshold,
            "anomalies": history
        }))
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        active_clients.discard(ws)