import logging
import pathlib
import socket
import sys
import yaml
from time import sleep

from gsproConnect import GSProConnect
from garminServer import GarminConnect

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
            _logger.info("Reading configuration file")
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            _logger.exception("Error loading config file. {e}")
            raise e

def main():
    try:
        _config = load_base_config()

        def start_gspro():
            global gsProConnect
            # create GSPro Connect class
            gsProConnect = GSProConnect(
                _config["device_id"],
                _config["units"],
                _config["gspro"]["api_version"],
                _config["club_data"],
            )

            _logger.info("Connecting to GSPro...")

            gsProConnect.init_socket(
                _config["gspro"]["ip_address"], _config["gspro"]["port"])

        start_gspro()

        # create R10 class
        garminConnect = GarminConnect(gsProConnect, _config["garmin"]["port"])

        def check_gspro_status():
            for attempt in range(10):
                print('checking gs pro status')
                try:
                    gsProConnect.send_test_signal()
                    return
                except KeyboardInterrupt:
                    raise
                except:
                    start_gspro()
                    continue
            raise Exception

        check_gspro_status()
        
        while True:
            print('starting Garmin server')
            try:
                garminConnect.start_server()
            except socket.timeout as e:
                garminConnect.disconnect()
                print('Trying to reconnect...')
                sleep(2)
                continue
            except socket.error as e:
                print('Error occured waiting for R10 response:')
                sleep(2)
                garminConnect.terminate_session()
                check_gspro_status()
                garminConnect = GarminConnect(gsProConnect, _config["garmin"]["port"])
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                _logger.exception("General error: {e}")
                break

    finally:
        print('closing sockets')
        if(gsProConnect):
            gsProConnect.terminate_session()
        if(garminConnect):
            garminConnect.terminate_session()
        sys.exit()

if __name__ == "__main__":
    main()
