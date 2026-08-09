from __future__ import annotations

import threading


class JobTracker:
    """Controla o número de conversões ativas no servidor.

    Protege CPU/memória limitando: (1) o total de jobs ativos no mundo todo e
    (2) o total de jobs ativos por IP. Usa threading.Lock porque a rota (event
    loop) e o background task (thread pool) podem tocar o tracker em paralelo.
    """

    def __init__(self, max_concurrent: int, max_per_ip: int) -> None:
        self.max_concurrent = max_concurrent
        self.max_per_ip = max_per_ip
        self._lock = threading.Lock()
        self._active = 0
        self._per_ip: dict[str, int] = {}

    def try_acquire(self, client_ip: str) -> bool:
        with self._lock:
            if self._active >= self.max_concurrent:
                return False
            if self._per_ip.get(client_ip, 0) >= self.max_per_ip:
                return False
            self._active += 1
            self._per_ip[client_ip] = self._per_ip.get(client_ip, 0) + 1
            return True

    def release(self, client_ip: str) -> None:
        with self._lock:
            self._active = max(0, self._active - 1)
            remaining = self._per_ip.get(client_ip, 0) - 1
            if remaining <= 0:
                self._per_ip.pop(client_ip, None)
            else:
                self._per_ip[client_ip] = remaining

    def active_count(self) -> int:
        with self._lock:
            return self._active
