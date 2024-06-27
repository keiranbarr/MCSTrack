import asyncio
import logging
import time as t
from ipaddress import IPv4Address
from pydantic import BaseModel

from src.connector.connector import Connector
from src.connector.structures.component_address import ComponentAddress

from src.common.structures import \
    COMPONENT_ROLE_LABEL_DETECTOR, \
    COMPONENT_ROLE_LABEL_POSE_SOLVER

detector_label = "d102"

async def connector_frame_repeat(connector: Connector,started):
    await connector.update()
    frame = connector.get_live_detector_frame(detector_label)
    event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    event_loop.create_task(connector_frame_repeat(connector=connector,started=started))


async def main():
    logging.basicConfig(level=logging.INFO)

    connector = Connector(
        serial_identifier="connector",
        send_status_messages_to_logger=True)

    # Add detector -- running on raspberry pi
    connector.add_connection(ComponentAddress(
            label=detector_label,
            role=COMPONENT_ROLE_LABEL_DETECTOR,
            ip_address=IPv4Address("192.168.0.102"),
            port=8001
        ))

    # Add pose solver -- running on same computer
    connector.add_connection(ComponentAddress(
            label="ps",
            role=COMPONENT_ROLE_LABEL_POSE_SOLVER,
            ip_address=IPv4Address("127.0.0.1"),
            port=8000
        ))

    connector.start_up()

    event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    event_loop.create_task(connector_frame_repeat(connector=connector))

    while True:
        await asyncio.sleep(1)

# To use: start pose solver on same computer, and connect to LAN with detector
if __name__ == "__main__":
    asyncio.run(main())