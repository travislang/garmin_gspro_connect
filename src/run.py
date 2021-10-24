# Initial test file to send data payload to gspro.
import logging
import yaml
import socket

# from golf_shot import BallData, ClubHeadData
from gsproConnect import GSProConnect
from garminConnect import GarminConnect
import pathlib


# configure log.
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
_logger = logging.getLogger(__file__)


def load_base_config():
    import os

    print(os.listdir())
    config_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "config.yml")
    with open(config_path, "r") as f:
        try:
            _logger.info("Attempting to read configuration file")
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            _logger.exception("Error loading config file. {e}")
            raise e


def main():
    try:
        # read base config file:
        _cfg = load_base_config()
        print(_cfg)

        # create GSPro Connect class for specific LM.
        gsProConnect = GSProConnect(
            _cfg["device_id"],
            _cfg["units"],
            _cfg["gspro"]["api_version"],
            _cfg["club_data"],
        )


        _logger.info("Connecting to GSPro...")
        # open tcp connection from config.
        # gsProConnect.init_socket(
        #     _cfg["gspro"]["ip_address"], _cfg["gspro"]["port"])
        # # send a heartbeat?
        # r10Connect.send_heartbeat()

        _logger.info("Connecting to garmin...")
        garminConnect = GarminConnect(
            _cfg["garmin"]["ip_address"], _cfg["garmin"]["port"])
        garminConnect.init_handshake()
        _logger.info("garmin connected")

        # r10Socket.listen()

        garminConnect.listenForShots(gsProConnect)

        
    finally:
        # #  Close this socket port.
        gsProConnect.terminate_session()
        garminConnect.terminate_session()


if __name__ == "__main__":
    main()
