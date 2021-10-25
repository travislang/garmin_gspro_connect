import socket
import sys
import json
import logging
from shot_data import BallData, ClubHeadData
from time import sleep
import threading


# s.close()

def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.shutdown(socket.SHUT_RDWR)
        return ip


class GarminConnect:
    def __init__(self, port) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client = None
        self._listening = True
        self._ballData = BallData
        self._clubData = ClubHeadData
        self._ip_address = get_ip_address()
        self._port = port

        print('Starting Garmin Server...')

        print('Open the E6 option within the garmin app.  Make sure these settings match: \n')
        print("IP Address: " + self._ip_address)
        print("Port: " + str(self._port) + '\n')

        try:
            self._server.bind((self._ip_address, self._port))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            print(msg)
            sys.exit()

        # self._server.settimeout(1)
        self._server.listen(5)
    
        
    def handle_handshake(self, step=1):
        print('Trying handshake with R10...')

        step1 = '{"Challenge": "gQW3om37uK4OOU4FXQH9GWgljxOrNcL5MvubVHAtQC0x6Z1AwJTgAIKyamJJMzm9", "E6Version": "2, 0, 0, 0", "ProtocolVersion": "1.0.0.5", "RequiredProtocolVersion": "1.0.0.0", "Type": "Handshake"}'
        step2 = '{"Success":"true","Type":"Authentication"}'

        self._client.sendall(step1.encode('UTF-8'))
        data = self._client.recv(8096)
        if data:
            dataObj = json.loads(data.decode('UTF-8'))
            print('handshake data recieved: ')
            print(dataObj)

            if(dataObj['Type'] == 'Disconnect'):
                self.disconnect()
                return
            elif(dataObj['Hash']):
                self._client.sendall(step2.encode('UTF-8'))
                print('handshake successful')
                return
        else:
            print('no response data')
            return

    def sendPong(self):
        self._client.sendall('{"Type":"Pong"}'.encode('UTF-8'))

    def sendFakeShot(self,gsProConnect):
           # # simulate a :BOMB:
        self._ballData = BallData(
            ballspeed=126.8,
            spinaxis=-13.2,
            totalspin=2350.2,
            backspin=2350.2,
            sidespin=0.0,
            hla=0.0,
            vla=13.5,
            carry=300.0,
        )

        # not supported yet
        self._clubData = ClubHeadData()

        gsProConnect.launch_ball(self._ballData, self._clubData)


    def sendBallData(self, ballData, gsProConnect):
        self._ballData = BallData(
            ballspeed=ballData['BallSpeed'],
            spinaxis=ballData['SpinAxis'],
            totalspin=ballData['TotalSpin'],
            backspin=ballData['BackSpin'],
            sidespin=ballData['SideSpin'],
            hla=ballData['LaunchDirection'],
            vla=ballData['LaunchAngle'],
            # carry=ballData['CarryDistance'],
        )

        self._clubData = ClubHeadData()

        gsProConnect.launch_ball(self._ballData, self._clubData)

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None

    def stopListening(self):
        self._listening = False

    def start_server(self, gsProConnect):
        print('Waiting for connection from R10...')
        conn, addr = self._server.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        self._client = conn

        self.listen(gsProConnect)

    def listen(self, gsProConnect):
        while self._listening and self._client:
            try:
                data = self._client.recv(10000)
            except socket.error as e:
                # Something else happened, handle error, exit, etc.
                print('non timeout error:')
                print(e)
                sys.exit(1)
            else:
                if len(data) == 0:
                    print('orderly shutdown on server end')
                    sys.exit(0)
                else:
                    dataObj = json.loads(data.decode('UTF-8'))
                    print('garminConnect data recieved')
                    print(dataObj['Type'])

                    if(dataObj['Type'] == 'Handshake'):
                        self.handle_handshake()
                    elif(dataObj['Type'] == 'Disconnect'):
                        self.disconnect()
                    elif(dataObj['Type'] == 'SimCommand'):
                        if(dataObj['SubType'] == 'Ping'):
                            self.sendPong()
                        elif(dataObj['SubType'] == 'ShotComplete'):
                            self.sendBallData(
                                dataObj['Details']['BallData'], gsProConnect)
                    elif(dataObj['Type'] == 'SetClubType'):
                        self.sendFakeShot(gsProConnect)
                    # elif(dataObj['Type'] == 'SetBallData'):
                    #     self.setBallData(dataObj['Type'])
                    continue

    def terminate_session(self):
        if(self._socket):
            self._socket.close()

