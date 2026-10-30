import os
import time
import psutil
from typing import Dict, Any, List


class SystemTelemetryEngine:
    def __init__(self):
        self.last_time = time.monotonic()
        self.last_net = psutil.net_io_counters()
        self.last_disk = psutil.disk_io_counters()
        self.cpu_count_logical = psutil.cpu_count(logical=True) or 1

        # 預熱 CPU 百分比計算
        psutil.cpu_percent(interval=None)
        for p in psutil.process_iter():
            try:
                p.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def collect_snapshot(self) -> Dict[str, Any]:
        now = time.monotonic()
        elapsed = max(0.1, now - self.last_time)
        self.last_time = now

        # 1. CPU 整體與各核心負載、時脈
        cpu_total = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        cpu_freq = psutil.cpu_freq()
        freq_mhz = round(cpu_freq.current, 0) if cpu_freq else 0

        # 2. 記憶體與 Swap 狀態
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # 3. 網路上下行即時速率 (KB/s)
        cur_net = psutil.net_io_counters()
        net_up_kbps = (cur_net.bytes_sent - self.last_net.bytes_sent) / elapsed / 1024.0
        net_down_kbps = (cur_net.bytes_recv - self.last_net.bytes_recv) / elapsed / 1024.0
        self.last_net = cur_net

        # 4. 磁碟 I/O 即時讀寫速率 (MB/s)
        cur_disk = psutil.disk_io_counters()
        if cur_disk and self.last_disk:
            disk_read_mbps = (cur_disk.read_bytes - self.last_disk.read_bytes) / elapsed / (1024 * 1024)
            disk_write_mbps = (cur_disk.write_bytes - self.last_disk.write_bytes) / elapsed / (1024 * 1024)
            self.last_disk = cur_disk
        else:
            disk_read_mbps, disk_write_mbps = 0.0, 0.0

        # 5. 掃描所有程序與建立 PID 名稱對照表
        processes: List[Dict[str, Any]] = []
        pid_name_map: Dict[int, str] = {}

        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'status']):
            try:
                info = proc.info
                pid = info['pid']
                name = info['name'] or f"PID-{pid}"
                pid_name_map[pid] = name

                # System Idle Process (PID 0) 不列入排名
                if pid == 0:
                    continue

                raw_cpu = proc.cpu_percent(interval=None)
                # 正規化為總體 CPU 佔用百分比 (0~100%)
                norm_cpu = round(raw_cpu / self.cpu_count_logical, 1)
                mem_bytes = info['memory_info'].rss if info.get('memory_info') else 0
                mem_mb = round(mem_bytes / (1024 * 1024), 1)

                processes.append({
                    "pid": pid,
                    "name": name,
                    "cpu_percent": norm_cpu,
                    "memory_mb": mem_mb,
                    "status": info.get('status', 'running')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # 依 CPU 與記憶體綜合排序取前 15 名
        processes.sort(key=lambda x: (x["cpu_percent"], x["memory_mb"]), reverse=True)
        top_processes = processes[:15]

        # 6. 掃描活躍的 TCP 網路連線 (Active Connections Audit)
        connections = self._scan_network_connections(pid_name_map)

        return {
            "timestamp": int(time.time() * 1000),
            "cpu": {
                "total": round(cpu_total, 1),
                "per_core": [round(c, 1) for c in cpu_per_core],
                "freq_mhz": freq_mhz
            },
            "memory": {
                "percent": round(mem.percent, 1),
                "used_gb": round(mem.used / (1024 ** 3), 2),
                "total_gb": round(mem.total / (1024 ** 3), 2),
                "swap_percent": round(swap.percent, 1)
            },
            "network": {
                "up_kbps": round(max(0.0, net_up_kbps), 1),
                "down_kbps": round(max(0.0, net_down_kbps), 1)
            },
            "disk": {
                "read_mbps": round(max(0.0, disk_read_mbps), 2),
                "write_mbps": round(max(0.0, disk_write_mbps), 2)
            },
            "top_processes": top_processes,
            "connections": connections
        }

    def _scan_network_connections(self, pid_name_map: Dict[int, str]) -> List[Dict[str, Any]]:
        """擷取本機 ESTABLISHED 與 LISTEN 的網路連線並反查程序名稱"""
        conns_list: List[Dict[str, Any]] = []
        try:
            raw_conns = psutil.net_connections(kind='tcp')
        except psutil.AccessDenied:
            return conns_list

        for c in raw_conns:
            if c.status not in ('ESTABLISHED', 'LISTEN'):
                continue
            laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
            raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "等待連線 (LISTEN)"
            pid = c.pid or 0
            proc_name = pid_name_map.get(pid, "System/Kernel")

            conns_list.append({
                "pid": pid,
                "name": proc_name,
                "local": laddr,
                "remote": raddr,
                "status": c.status
            })

        # 優先顯示有外部連線的 ESTABLISHED 狀態
        conns_list.sort(key=lambda x: (0 if x["status"] == "ESTABLISHED" else 1, x["name"]))
        return conns_list[:35]


def terminate_process_by_pid(target_pid: int) -> Dict[str, Any]:
    """安全終止指定 PID 的程序"""
    current_pid = os.getpid()
    if target_pid in (0, 4, current_pid):
        return {"ok": False, "message": "系統核心或監控伺服器本身不可終止！"}

    try:
        proc = psutil.Process(target_pid)
        proc_name = proc.name()
        proc.terminate()
        return {"ok": True, "message": f"已發送終止訊號給 {proc_name} (PID: {target_pid})"}
    except psutil.NoSuchProcess:
        return {"ok": False, "message": f"找不到 PID {target_pid}，該程序可能已結束。"}
    except psutil.AccessDenied:
        return {"ok": False, "message": "權限不足！請以系統管理員身分啟動 VS Code 再試。"}