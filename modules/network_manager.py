import socket
import json
import logging
from typing import Dict, Any, Optional

# Configure module-level logger (Best Practice: Don't use print() in modules)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class NetworkBridge:
    """
    A robust, non-blocking UDP Client designed for high-frequency telemetry.

    Usage:
        with NetworkBridge("127.0.0.1", 5005) as net:
            net.send({"roll": 0.5})
    """

    # Optimization: __slots__ saves RAM by preventing the creation of __dict__
    __slots__ = ('ip', 'port', '_socket', '_address')

    def __init__(self, ip: str, port: int):
        """
        Initialize the Network Bridge.

        :param ip: Target IP Address (e.g., "127.0.0.1")
        :param port: Target Port (1-65535)
        :raises ValueError: If parameters are invalid.
        """
        if not (1 <= port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535. Got: {port}")

        self.ip = ip
        self.port = port
        self._address = (self.ip, self.port)
        self._socket: Optional[socket.socket] = None

        # Initialize immediately
        self._setup_socket()

    def _setup_socket(self) -> None:
        """Internal method to configure the raw UDP socket."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setblocking(False)  # Critical for real-time loops
            logger.info(f"UDP Bridge initialized targeting {self.ip}:{self.port}")
        except socket.error as e:
            logger.critical(f"Failed to create socket: {e}")
            raise

    def send_telemetry(self, data: Dict[str, Any]) -> None:
        """
        Serializes and transmits a dictionary as a JSON packet.

        :param data: Dictionary containing flight data (e.g., {'roll': 0.5})
        """
        if self._socket is None:
            return

        try:
            # High-speed serialization
            json_payload = json.dumps(data, default=str)
            encoded_bytes = json_payload.encode('utf-8')

            self._socket.sendto(encoded_bytes, self._address)

        except BlockingIOError:
            # Expected behavior in non-blocking mode if buffer is full.
            # We ignore this to keep the game loop smooth.
            pass
        except TypeError as e:
            logger.error(f"Serialization failed. Data must be JSON-serializable. Error: {e}")
        except socket.error as e:
            logger.warning(f"Transmission error: {e}")

    def close(self) -> None:
        """Manually close the connection."""
        if self._socket:
            try:
                self._socket.close()
            except socket.error:
                pass
            finally:
                self._socket = None
                logger.info("UDP Socket closed.")

    # --- Context Manager Support (The "Senior Dev" Touch) ---
    def __enter__(self):
        """Allows usage in 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically closes socket when exiting 'with' block."""
        self.close()