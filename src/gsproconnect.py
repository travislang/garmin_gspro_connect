import socket
import logging
import json
from shot_data import BallData, ClubHeadData

# configure log.
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
_logger = logging.getLogger(__file__)


class GSProConnect:
    def __init__(self, device_id, units, api_version, club_data=False) -> None:
        self._device_id = device_id
        self._units = units
        self._api_version = api_version
        self._send_club_data = club_data

        self._socket = None
        self._shot_number = 0

    def init_socket(self, ip_address, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_address, port))

    def send_heartbeat(self):
        payload = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "ShotDataOptions": {
                "ContainsBallData": False,
                "ContainsClubData": False,
                "LaunchMonitorIsReady": True,
                "LaunchMonitorBallDetected": True,
                "IsHeartBeat": True,
            },
        }
        self._socket.sendall(json.dumps(payload).encode("utf-8"))
        _logger.info("sent a payload for a heartbeat")

    # TODO: Handle the response from GSPRO
    def launch_ball(self, ball_data: BallData, club_data: ClubHeadData = None) -> None:
        _logger.info("Sending data to GSPRO to launch ball")
        self._shot_number += 1
        _logger.info(f"Session Shot Number: {self._shot_number}")

        api_data = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "BallData": {
                "Speed": ball_data.ballspeed,
                "SpinAxis": ball_data.spinaxis,
                # "TotalSpin": ball_data.totalspin,
                "BackSpin": ball_data.backspin,
                "SideSpin": ball_data.sidespin,
                "HLA": ball_data.hla,
                "VLA": ball_data.vla,
                "CarryDistance": ball_data.carry,
            },
            "ShotDataOptions": {"ContainsBallData": True, "ContainsClubData": False, },
        }

        if self._send_club_data:
            api_data["ShotDataOptions"]["ContainsClubData"] = "true"
            api_data["ClubData"] = {
                "Speed": club_data.speed,
                "AngleOfAttack": club_data.angleofattack,
                "FaceToTarget": club_data.facetotarget,
                "Lie": club_data.lie,
                "Loft": club_data.loft,
                "Path": club_data.path,
                "SpeedAtImpact": club_data.speedatimpact,
                "VerticalFaceImpact": club_data.verticalfaceimpact,
                "HorizontalFaceImpact": club_data.horizontalfaceimpact,
                "ClosureRate": club_data.closurerate,
            }

        print(json.dumps(api_data, indent=4))

        self._socket.sendall(json.dumps(api_data).encode("utf-8"))
        response = self._socket.recv(8192)
        print("response from socket")
        print(response)

    # TODO: When script ends does socket auto close :shrug:
    def terminate_session(self):
        if(self._socket):
            self._socket.shutdown()
