import asyncio
import logging
import time as t
from ipaddress import IPv4Address
from pydantic import BaseModel

from src.connector.connector import Connector
from src.connector.structures.component_connection_static import ComponentConnectionStatic

from src.common.structures import \
    COMPONENT_ROLE_LABEL_DETECTOR, \
    COMPONENT_ROLE_LABEL_POSE_SOLVER

class ConnectionStaticModel(BaseModel):
    label: str
    role: str
    ip_address: str
    port: int

# TODO: find better way to do this
started = False

async def connector_frame_repeat(connector: Connector,started):
    # noinspection PyBroadException
    try:
        await connector.do_update_frames_for_connections()
    except Exception as e:
        connector.add_status_message(
            severity="error",
            message=f"Exception occurred in connector loop: {str(e)}")
    connector.update_loop()
    if started == False:
        connector.start_tracking()
        connector.update_loop()
        started = True
    frame = connector.get_live_detector_frame("d102")
    event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    event_loop.create_task(connector_frame_repeat(connector=connector,started=started))


async def main():
    logging.basicConfig(level=logging.INFO)

    connector = Connector(
        serial_identifier="connector",
        send_status_messages_to_logger=True)

    # Add detector -- running on raspberry pi
    connector.add_connection(ComponentConnectionStatic(
            label="d102",
            role=COMPONENT_ROLE_LABEL_DETECTOR,
            ip_address=IPv4Address("192.168.0.102"),
            port=8001
        ))

    # Add pose solver -- running on same computer
    connector.add_connection(ComponentConnectionStatic(
            label="ps",
            role=COMPONENT_ROLE_LABEL_POSE_SOLVER,
            ip_address=IPv4Address("127.0.0.1"),
            port=8000
        ))

    connector.begin_connecting("d102")
    connector.begin_connecting("ps")

    event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    event_loop.create_task(connector_frame_repeat(connector=connector,started=started))

    while True:
        await asyncio.sleep(1)

# To use: start pose solver on same computer, and connect to LAN with detector
if __name__ == "__main__":
    asyncio.run(main())