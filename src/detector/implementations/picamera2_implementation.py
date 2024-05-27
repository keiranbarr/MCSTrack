from src.detector.api import \
    GetCaptureDeviceResponse, \
    GetCaptureImageRequest, \
    GetCaptureImageResponse, \
    GetCapturePropertiesResponse, \
    SetCaptureDeviceRequest, \
    SetCapturePropertiesRequest
from src.common import \
    EmptyResponse, \
    ErrorResponse, \
    get_kwarg, \
    MCastResponse
from src.common.structures.capture_status import CaptureStatus

from src.detector.implementations import AbstractCameraInterface

from picamera2 import Picamera2, Preview

import base64
import cv2
import datetime
import logging
import time
import numpy
import os
from typing import Any, Callable

logger = logging.getLogger(__name__)

class PiCamera(AbstractCameraInterface):

    _capture: numpy.ndarray | None
    _captured_image: numpy.ndarray | None

    def __init__(self):
        self._capture = None
        self._captured_image = None
        self._captured_timestamp_utc = datetime.datetime.min

        self._capture_status = CaptureStatus
        self._capture_status.status = CaptureStatus.Status.STOPPED

        self._captured_timestamp_utc = datetime.datetime.min

        self._capture_status = CaptureStatus
        self._capture_status.status = CaptureStatus.Status.STOPPED

        # TODO: DEBUGGING
        self._capture_status.status = CaptureStatus.Status.RUNNING

        self._camera = Picamera2()
        self._camera.start()

    def __del__(self):
        if self._capture is not None:
            self._capture = numpy.empty

    def _detect_os_and_open_video(self):
        return self._camera.capture_array()

    def internal_update_capture(self):
        self._captured_image = self._camera.capture_array()

        if self._captured_image is None:
            message: str = "Failed to grab frame."
            self._status.capture_errors.append(message)
            self._capture_status.status = CaptureStatus.Status.FAILURE
            return ("error", message)

        self._captured_timestamp_utc = datetime.datetime.utcnow()

    def set_capture_device(self, **kwargs) -> EmptyResponse | ErrorResponse:
        
        self._capture = self._detect_os_and_open_video()
        if self._capture is None:
            return ErrorResponse(message=f"Failed to open capture device")
        
        default_brightness = self._camera.camera_controls['Brightness'][2]
        default_contrast = self._camera.camera_controls['Contrast'][2]
        default_sharpness = self._camera.camera_controls['Sharpness'][2]
        default_auto_exposure = self._camera.camera_controls['AeEnable'][2]
        default_exposure = self._camera.camera_controls['ExposureValue'][2]

        self._camera.controls.Brightness = default_brightness
        self._camera.controls.Contrast = default_contrast
        self._camera.controls.Sharpness = default_sharpness
        self._camera.controls.AeEnable = default_auto_exposure
        self._camera.controls.ExposureValue = default_exposure
        
        return EmptyResponse()

    # noinspection DuplicatedCode
    def set_capture_properties(self, **kwargs) -> EmptyResponse:
        """
        :key request: SetCapturePropertiesRequest
        """

        request: SetCapturePropertiesRequest = get_kwarg(
            kwargs=kwargs,
            key="request",
            arg_type=SetCapturePropertiesRequest)

        if self._capture is not None:

            # FPS and resolution change require the camera be off
            # While other settings require the camera be on
            self._camera.stop()
            if request.resolution_x_px is not None and request.resolution_y_px is not None:
                self._camera.video_configuration.size = (request.resolution_x_px,request.resolution_y_px)
            if request.fps is not None:
                self._camera.video_configuration.controls.FrameRate = request.fps
            self._camera.configure("video")
            self._camera.start()

            if request.auto_exposure is not None:
                self._camera.controls.AeEnable = request.auto_exposure
            # TODO: how to enforce values be entered in the proper range?
            if request.exposure is not None:
                self._camera.controls.ExposureValue = request.exposure
            if request.brightness is not None:
                self._camera.controls.Brightness = request.brightness
            if request.contrast is not None:
                self._camera.controls.Contrast = request.contrast
            if request.sharpness is not None:
                self._camera.controls.Sharpness = request.sharpness
            # no gamma
        return EmptyResponse()

    def get_capture_device(self, **_kwargs) -> GetCaptureDeviceResponse:
        return GetCaptureDeviceResponse(capture_device_id=str("N/A"))

    def get_capture_properties(self, **_kwargs) -> GetCapturePropertiesResponse | ErrorResponse:
        if self._capture is None:
            return ErrorResponse(
                message="The capture is not active, and properties cannot be retrieved.")
        else:
            ret = GetCapturePropertiesResponse(
                resolution_x_px=int(self._camera.video_configuration.size[0]),
                resolution_y_px=int(self._camera.video_configuration.size[1]),
                fps=int(round(self._camera.video_configuration.controls.FrameRate)),
                auto_exposure=bool(self._camera.controls.AeEnable),
                exposure=int(self._camera.controls.ExposureValue),
                brightness=self._camera.controls.Brightness,
                contrast=self._camera.controls.Contrast,
                sharpness=self._camera.controls.Sharpness)
            return ret
        # TODO: Get powerline_frequency_hz and backlight_compensation

    def get_capture_image(self, **kwargs) -> GetCaptureImageResponse:
        """
        :key request: GetCaptureImageRequest
        """

        request: GetCaptureImageRequest = get_kwarg(
            kwargs=kwargs,
            key="request",
            arg_type=GetCaptureImageRequest)

        encoded_frame: bool
        encoded_image_rgb_single_row: numpy.array
        encoded, encoded_image_rgb_single_row = cv2.imencode(request.format, self._captured_image)
        encoded_image_rgb_bytes: bytes = encoded_image_rgb_single_row.tobytes()
        encoded_image_rgb_base64 = base64.b64encode(encoded_image_rgb_bytes)
        return GetCaptureImageResponse(
            format=request.format,
            image_base64=encoded_image_rgb_base64)

    def start_capture(self, **kwargs) -> MCastResponse:
        if self._capture is not None:
            return EmptyResponse()

        self._capture = self._detect_os_and_open_video()

        self._capture_status.status = CaptureStatus.Status.RUNNING
        return EmptyResponse()

    def stop_capture(self, **kwargs) -> MCastResponse:
        if self._capture is not None:
            self._capture = None
        self._capture_status.status = CaptureStatus.Status.STOPPED
        return EmptyResponse()
