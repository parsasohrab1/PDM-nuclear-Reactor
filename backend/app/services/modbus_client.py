"""Modbus TCP client stub (SRS Section 5.3)."""

import logging

from backend.app.config import Settings

logger = logging.getLogger(__name__)


class ModbusClient:
    """Modbus TCP client wrapper using pymodbus."""

    def __init__(self, settings: Settings):
        self.host = settings.modbus_host
        self.port = settings.modbus_port
        self._client = None

    def connect(self) -> bool:
        try:
            from pymodbus.client import ModbusTcpClient

            self._client = ModbusTcpClient(host=self.host, port=self.port)
            return self._client.connect()
        except Exception as exc:
            logger.warning("Modbus connection failed: %s", exc)
            return False

    def read_holding_registers(self, address: int, count: int = 4) -> list[int] | None:
        if not self._client:
            return None
        result = self._client.read_holding_registers(address, count)
        if result.isError():
            return None
        return result.registers
