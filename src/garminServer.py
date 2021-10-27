import socket
import sys
import json
from shot_data import BallData, ClubHeadData
from time import sleep

from simMessages import simMessages


# s.close()

def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.shutdown(socket.SHUT_RDWR)
        return ip


class GarminConnect:
    def __init__(self, gsProConnect, port) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client = None
        self._listening = True
        self._ballData = BallData
        self._clubData = ClubHeadData
        self._clubType = '7Iron'
        self._ip_address = get_ip_address()
        self._port = port
        self._simMessages = simMessages()
        self._gsProConnect = gsProConnect

        print('Starting Garmin Server...')

        print('\nOpen the E6 option within the garmin app.  Make sure these settings match: \n')
        print("IP Address: " + self._ip_address)
        print("Port: " + str(self._port) + '\n')

        try:
            self._server.bind((self._ip_address, self._port))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            print(msg)
            sys.exit()

        self._server.settimeout(3)
        self._server.listen(5)

    def listen_for_response(self):
        try:
            msg = self._client.recv(8096)
        except socket.timeout as e:
            print('Timed out waiting for R10 response')
            raise
        except socket.error as e:
            print('Error occured waiting for R10 response:')
            print(e)
            raise
        else:
            if len(msg) == 0:
                print('Garmin R10 has closed connection')
                sys.exit()
            else:
                print("response from GSPro Connect")
                print(msg.decode('UTF-8'))
                return msg

    def wait_for_message(self):
        while True:
            try:
                print('Waiting for message from R10...')
                msg = self._client.recv(10000)
            except socket.timeout as e:
                continue
            except socket.error as e:
                print('Error occured waiting for message:')
                print(e)
                self.disconnect()
            else:
                if len(msg) == 0:
                    print('Garmin R10 has closed connection')
                    self.disconnect()
                else:
                    return msg
            
    
    def handle_handshake(self):
        print('Trying handshake with R10...')

        self._client.sendall(self._simMessages.get_handshake_message(1))
        data = self.listen_for_response()
        
        try:
            dataObj = json.loads(data.decode('UTF-8'))
        except ValueError:
            print('unable to parse handshake data:')
            print(data.decode('UTF-8'))
            return False

        if(dataObj['Type'] == 'Disconnect'):
            self.disconnect()
        elif(dataObj['Hash']):
            self._client.sendall(self._simMessages.get_handshake_message(2))
            # self.listen_for_response()
            print('handshake successful')
            
            return True

    def sendPing(self):
        self._client.sendall(self._simMessages.get_sim_command('Ping'))

    def updateClubType(self, clubType):
        self._clubType = clubType

        self._client.sendall(self._simMessages.get_success_message('SetClubType'))

        if(clubType == 'SandWedge'):
            self.sendTestShot()

    def sendTestShot(self, ballSpeed=128.5):
        self._ballData = BallData(
            ballspeed=ballSpeed,
            spinaxis=-13.2,
            totalspin=2350.2,
            hla=0.0,
            vla=13.5,
        )
        self._clubData = ClubHeadData()

        self.sendShot()

    def setBallData(self, ballData):
        self._ballData = BallData(
            ballspeed=ballData['BallSpeed'],
            spinaxis=ballData['SpinAxis'],
            totalspin=ballData['TotalSpin'],
            hla=ballData['LaunchDirection'],
            vla=ballData['LaunchAngle'],
        )

        self._client.sendall(self._simMessages.get_success_message('SetBallData'))

    def setClubData(self, clubData):
        self._clubData = ClubHeadData(
            speed=clubData['ClubHeadSpeed'],
        )

        self._client.sendall(self._simMessages.get_success_message('SetClubData'))

    def sendShot(self):
        self._gsProConnect.launch_ball(self._ballData, self._clubData)

        self._client.sendall(self._simMessages.get_success_message('SendShot'))

        self._client.sendall(self._simMessages.get_shot_response_message())

        self._client.sendall(self._simMessages.get_sim_command('Disarm'))

        print('R10 is ready for next shot...')

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None

    def stopListening(self):
        self._listening = False

    def start_server(self):
        while True:
            try:
                print('Waiting for connection from R10...')
                conn, addr = self._server.accept()
                print('Connected with ' + addr[0] + ':' + str(addr[1]))
                self._client = conn
                self._client.settimeout(2)

                self.listen()
            except KeyboardInterrupt:
                raise

    def listen(self):
        while self._listening and self._client:
            data = self.wait_for_message()

            try:
                dataObj = json.loads(data.decode('UTF-8'))
            except ValueError:
                print('unable to parse data:')
                print(data.decode('UTF-8'))
                continue

            if(dataObj['Type'] == 'Handshake'):
                for i in range(3):
                    if(i == 2):
                        raise Exception
                    else:
                        resp = self.handle_handshake()
                        if(resp == True):
                            self._client.sendall(self._simMessages.get_sim_command('Arm'))
                            break
                        else:
                            continue
            elif(dataObj['Type'] == 'SetClubType'):
                self.updateClubType(dataObj['ClubType'])
            elif(dataObj['Type'] == 'SetBallData'):
                self.setBallData(dataObj['BallData'])
            elif(dataObj['Type'] == 'SetClubData'):
                self.setClubData(dataObj['ClubData'])
            elif(dataObj['Type'] == 'SendShot'):
                self.sendShot()
            # elif(dataObj['Type'] == 'Pong'):
            #     self.resetTimer()

    def terminate_session(self):
        if(self._server):
            self._server.close()

