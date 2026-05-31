"""OPC-UA client stub for real-time sensor ingestion (FR-06)."""

import logging

from backend.app.config import Settings

logger = logging.getLogger(__name__)


class OPCUAClient:
    """Async OPC-UA client wrapper using asyncua library."""

    def __init__(self, settings: Settings):
        self.endpoint = settings.opcua_endpoint
        self._client = None
        self._connected = False

    async def connect(self) -> None:
        try:
            from asyncua import Client

            self._client = Client(url=self.endpoint)
            await self._client.connect()
            self._connected = True
            logger.info("Connected to OPC-UA server at %s", self.endpoint)
        except Exception as exc:
            logger.warning("OPC-UA connection failed: %s", exc)
            self._connected = False

    async def disconnect(self) -> None:
        if self._client and self._connected:
            await self._client.disconnect()
            self._connected = False

    async def read_sensor_nodes(self, node_ids: list[str]) -> dict[str, float]:
        if not self._connected or not self._client:
            raise ConnectionError("OPC-UA client not connected")

        values = {}
        for node_id in node_ids:
            node = self._client.get_node(node_id)
            values[node_id] = await node.read_value()
        return values
