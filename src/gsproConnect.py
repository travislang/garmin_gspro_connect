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
        self._shot_number = 1

    def init_socket(self, ip_address, port):
        self._socket.connect((ip_address, port))
        self._socket.settimeout(2)

    def send_msg(self, payload, attempts=10):
        for attempt in range(attempts):
            try:
                _logger.info("sending message to GSPro...")
                self._socket.sendall(json.dumps(payload).encode("utf-8"))
                msg = self._socket.recv(8096)
            except socket.timeout as e:
                print('timed out...')
                sleep(1)
                continue
            except socket.error as e:
                print('Error waiting for GSPro response:')
                print(e)
                raise
                # sys.exit(1)
            else:
                if len(msg) == 0:
                    print('GS Pro closed connection')
                    return False
                else:
                    print("response from GSPro: ")
                    print(msg)
                    return True
        return False
            

    def send_test_signal(self):
        payload = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "ShotDataOptions": {
                "ContainsBallData": False,
                "ContainsClubData": False,
            },
        }
        self.send_msg(payload)
        print('GSPro Connected...')

    def launch_ball(self, ball_data: BallData, club_data: ClubHeadData = None) -> None:
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
            api_data["ShotDataOptions"]["ContainsClubData"] = True
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
