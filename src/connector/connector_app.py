from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

from src.connector.connector import Connector
from src.connector.structures.component_connection_static import ComponentConnectionStatic
from src.detector.exceptions.update_capture_error import UpdateCaptureError

app = FastAPI()

connector = Connector(serial_identifier="SlicerConnector")

class ConnectionStaticModel(BaseModel):
    label: str
    role: str
    ip_address: str
    port: int

class ConnectionDynamicModel(BaseModel):
    status: str
    attempt_count: int
    next_attempt_timestamp_utc: Optional[str] = None
    socket: Optional[str] = None

@app.post("/add_connection")
def add_connection(connection_static: ConnectionStaticModel):
    connection_static = ComponentConnectionStatic(
        label=connection_static.label,
        role=connection_static.role,
        ip_address=connection_static.ip_address,
        port=connection_static.port
    )
    try:
        connector.add_connection(connection_static)
        return {"message": "Connection added successfully"}
    except ConnectionError as e:
        message: str = f"Unable to add connection \"{connection_static.label}\" \
            with role {connection_static.role} \
            at {connection_static.ip_address}:{connection_static.port}"
        connector.add_status_message(
            severity="error",
            message=message)
        return

@app.post("/begin_connecting/{label}")
def begin_connecting(label: str):
    connector.begin_connecting(label)
    return {"message": f"Started connecting to {label}"}

@app.post("/begin_disconnecting/{label}")
def begin_disconnecting(label: str):
    connector.begin_disconnecting(label)
    return {"message": f"Started disconnecting from {label}"}

@app.get("/get_status")
def get_status():
    return {"status": connector.get_status().name}

@app.get("/get_live_detector_frame/{detector_label}")
def get_live_detector_frame(detector_label: str):
    frame = connector.get_live_detector_frame(detector_label)
    if frame is None:
        raise UpdateCaptureError(severity="error", message="Could not get live detector frame")
    return frame

@app.post("/start_tracking")
def start_tracking(mode: str = Connector.StartupMode.DETECTING_AND_SOLVING):
    connector.start_tracking(mode=mode)
    return {"message": "Tracking started"}

@app.post("/stop_tracking")
def stop_tracking():
    connector.stop_tracking()
    return {"message": "Tracking stopped"}
