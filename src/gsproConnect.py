import socket
import logging
import json
import sys
from time import sleep
from shot_data import BallData, ClubHeadData

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

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._shot_number = 2

    def init_socket(self, ip_address, port):
        self._socket.connect((ip_address, port))
        self._socket.settimeout(2)

    # def handleResponse(self, msg):
    #     # TODO handle

    def send_msg(self, payload):
        print('payload')
        print(json.dumps(payload))
        self._socket.sendall(json.dumps(payload).encode("utf-8"))
        _logger.info("sending message to GSPro Connect...")
        
        while True:
            try:
                msg = self._socket.recv(8096)
            except socket.timeout as e:
                err = e.args[0]
                # this next if/else is a bit redundant, but illustrates how the
                # timeout exception is setup
                if err == 'timed out':
                    sleep(1)
                    print('recv timed out, retry later')
                    continue
                else:
                    print('other timeout error:')
                    print(e)
                    sys.exit(1)
            except socket.error as e:
                # Something else happened, handle error, exit, etc.
                print('non timeout error:')
                print(e)
                sys.exit(1)
            else:
                if len(msg) == 0:
                    print('orderly shutdown on server end')
                    sys.exit(0)
                else:
                    print("response from GSPro Connect")
                    print(msg)
                    # self.handleResponse(msg)
                    break

    def send_test_signal(self):
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
        self.send_msg(payload)
        print('GSPro Connected...')

    def launch_ball(self, ball_data: BallData, club_data: ClubHeadData = None) -> None:
        _logger.info("Sending launch data")

        api_data = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "BallData": {
                "Speed": ball_data.ballspeed,
                "SpinAxis": ball_data.spinaxis,
                "TotalSpin": ball_data.totalspin,
                "HLA": ball_data.hla,
                "VLA": ball_data.vla,
            },
            "ShotDataOptions": {
                "ContainsBallData": True, 
                "ContainsClubData": False
            },
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

        self.send_msg(api_data)

        self._shot_number += 1

    def terminate_session(self):
        if(self._socket):
            self._socket.close()
            # self._socket.shutdown(socket.SHUT_RDWR)
