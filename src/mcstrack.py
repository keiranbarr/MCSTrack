from multiprocessing import Process
from src.common import MCastConfiguration
from src.common.api.mcast_request_series import MCastRequestSeries
from src.common.api.mcast_response_series import MCastResponseSeries
from src.common.structures import \
    COMPONENT_ROLE_LABEL_CALIBRATOR, \
    COMPONENT_ROLE_LABEL_DETECTOR, \
    COMPONENT_ROLE_LABEL_POSE_SOLVER, \
    ComponentConnectionStatic
from src.connector import Connector
from src.detector import \
    Detector, \
    DetectorConfiguration
from src.detector.api.get_capture_device_request import GetCaptureDeviceRequest
from src.detector.api.get_capture_properties_request import GetCapturePropertiesRequest
from src.detector.api.set_capture_device_request import SetCaptureDeviceRequest
from src.detector.api.start_capture_request import StartCaptureRequest
from src.detector.implementations import \
    AbstractCameraInterface, \
    AbstractMarkerInterface, \
    ArucoMarker, \
    USBWebcamWithOpenCV, \
    PiCamera
from src.pose_solver.structures import PoseData
import os
import hjson

class MCSTrack():

    _internal_loop : Process

    def __init__(self):
        _connector : Connector
        _detectors : list[Detector]

        self._connector = Connector(
        serial_identifier="connector",
        send_status_messages_to_logger=True)

    def start_up(self, MCastConfiguration) -> None:
        for num, IP in enumerate(MCastConfiguration.detector_addresses):
            # # initiate detectors
            # detector = Detector(detector_configuration=MCastConfiguration.detector_configuration,\
            #                     marker_interface=MCastConfiguration.marker_interface,\
            #                         camera_interface=MCastConfiguration.camera_interface)
            # _detectors.append(detector)

            # # add detector, pose solver to connector

            # # apply settings
            # detector.start_capture()
            # detector.set_capture_properties(MCastConfiguration.detector_settings)
        
            # while True:
            #     detector.get_capture_image()

            self._connector.add_connection(ComponentConnectionStatic(label=num, \
                                                                    role=COMPONENT_ROLE_LABEL_DETECTOR, \
                                                                    ip_address=IP, \
                                                                    port=8001))

        self._internal_loop = Process(target = self.controller_loop(MCastConfiguration))
        self._internal_loop.start()

    def get_poses(self) -> PoseData:
        pass

    def shutdown(self) -> None:
        self._internal_loop.join()

    def controller_loop(self, MCastConfiguration) -> None:
        print("test")
        request_series: MCastRequestSeries = MCastRequestSeries(
            series=[
                StartCaptureRequest(),
                GetCapturePropertiesRequest()])
        _capture_start_request_id = self._connector.request_series_push(
            connection_label="N/A",
            request_series=request_series)
        
        response_series: MCastResponseSeries | None = self._connector.response_series_pop(
            request_series_id=_capture_start_request_id)
        if response_series is not None:
            print(response_series.series)

        















test = MCSTrack()

# marker_interface: AbstractMarkerInterface

# detector_configuration_filepath: str = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")
# detector_configuration: DetectorConfiguration
# camera_interface: AbstractCameraInterface
# marker_interface: AbstractMarkerInterface

# with open(detector_configuration_filepath, 'r') as infile:
#     detector_configuration_file_contents: str = infile.read()
#     detector_configuration_dict = hjson.loads(detector_configuration_file_contents)
#     detector_configuration = DetectorConfiguration(**detector_configuration_dict)

# # camera_interface = PiCamera()
# camera_interface = USBWebcamWithOpenCV(detector_configuration.camera_connection.usb_id)
# marker_interface = ArucoMarker()

config = MCastConfiguration(detector_addresses=["192.168.0.103"], \
                            detector_settings = [])

test.start_up(config)