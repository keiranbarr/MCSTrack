import abc
from src.common import \
    EmptyResponse, \
    ErrorResponse, \
    MCastResponse, \
    MCastComponent
from src.detector.api import \
    GetCaptureDeviceResponse, \
    GetCapturePropertiesResponse, \
    GetCaptureImageResponse
from src.common.structures.capture_status import CaptureStatus

import datetime

class AbstractCameraInterface(abc.ABC):

    _captured_timestamp_utc: datetime.datetime
    _capture_status: CaptureStatus  # internal bookkeeping

    def __del__(self):
        pass

    def set_capture_device(self, **kwargs) -> EmptyResponse | ErrorResponse:
        pass
        
    def set_capture_properties(self, **kwargs) -> EmptyResponse:
        pass

    def get_capture_device(self, **_kwargs) -> GetCaptureDeviceResponse:
        pass

    def get_capture_properties(self, **_kwargs) -> GetCapturePropertiesResponse | ErrorResponse:
        pass

    def get_capture_image(self, **kwargs) -> GetCaptureImageResponse:
        pass

    def start_capture(self, **kwargs) -> MCastResponse:
        pass

    def stop_capture(self, **kwargs) -> MCastResponse:
        pass