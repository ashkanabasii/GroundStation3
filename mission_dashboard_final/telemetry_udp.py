# telemetry_udp.py
# Improved UDP-based telemetry receiver with thread safety, error logging, and graceful shutdown

import socket
import threading
import time
from collections import deque, defaultdict

class Telemetry:
    def __init__(self, ip="127.0.0.1", port=5005, maxlen=1000):
        # Create and bind UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((ip, port))
        except Exception as e:
            raise RuntimeError(f"Failed to bind UDP socket to {ip}:{port}: {e}")
        self.sock.setblocking(False)

        # Thread-safety and control
        self._lock = threading.Lock()
        self._running = True

        # Telemetry storage (history limited by maxlen)
        self.data = defaultdict(lambda: deque(maxlen=maxlen))
        # Predefine known fields
        for field in ["time", "Yaw", "Pitch", "Roll", "Alt", "Lat", "Lon", "P", "T", "Accel", "Gyro"]:
            self.data[field]

        self.latest = None           # most recent packet
        self.event_log = deque(maxlen=100)  # error and status messages

        # Start background receive thread
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def _receive_loop(self):
        while self._running:
            try:
                raw, _ = self.sock.recvfrom(4096)
                recv_time = time.time()
                line = raw.decode("utf-8", errors="ignore").strip()

                # Parse key:value pairs
                pkt = {}
                for token in line.split(","):
                    if ":" not in token:
                        continue
                    key, val = token.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    try:
                        val_conv = float(val)
                    except ValueError:
                        val_conv = val
                    pkt[key] = val_conv

                # Store parsed data thread-safely
                with self._lock:
                    self.latest = {"recv_time": recv_time, **pkt}
                    for k, v in pkt.items():
                        self.data[k].append(v)
                    # Also record the receive timestamp
                    self.data["time"].append(recv_time)

            except BlockingIOError:
                # No data; yield CPU
                time.sleep(0.01)
            except Exception as e:
                # Log unexpected errors
                with self._lock:
                    self.event_log.append(f"Error in receive loop: {e}")
                time.sleep(0.1)

    def get_latest(self):
        """Return the most recent packet (including recv_time)."""
        with self._lock:
            return dict(self.latest) if self.latest else None

    def get_history(self, field):
        """Return the history list for a given field."""
        with self._lock:
            return list(self.data.get(field, []))

    def reset(self):
        """Clear all stored data and logs."""
        with self._lock:
            for dq in self.data.values():
                dq.clear()
            self.latest = None
            self.event_log.clear()

    def close(self):
        """Stop the receive loop and close the socket."""
        self._running = False
        self._thread.join(timeout=1)
        self.sock.close()
