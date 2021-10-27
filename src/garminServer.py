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

    def sendPing(self):
        self._client.sendall('{"SubType":"Ping","Type":"SimCommand"}'.encode('UTF-8'))

    def sendFakeShot(self,gsProConnect):
           # # simulate a :BOMB:
        self._ballData = BallData(
            ballspeed=126.8,
            spinaxis=-13.2,
            totalspin=2350.2,
            hla=0.0,
            vla=13.5,
        )

        # not supported yet
        self._clubData = ClubHeadData()

        gsProConnect.launch_ball(self._ballData, self._clubData)

    def setBallData(self, ballData):
        # from garmin
        # {"BallData":{"BallSpeed":103.35501,"LaunchAngle":17.773596,
        # "LaunchDirection":-5.006505,"SpinAxis":353.39822,"TotalSpin":4721.594},"Type":"SetBallData"} 
 
        self._ballData = BallData(
            ballspeed=ballData['BallSpeed'],
            spinaxis=ballData['SpinAxis'],
            totalspin=ballData['TotalSpin'],
            hla=ballData['LaunchDirection'],
            vla=ballData['LaunchAngle'],
            # backspin=ballData['BackSpin'],
            # sidespin=ballData['SideSpin'],
            # carry=ballData['CarryDistance'],
        )

        self._client.sendall('{"Details":"Success.","SubType":"SetBallData","Type":"ACK"}'.encode('UTF-8'))

    def setClubData(self, clubData):
        self._clubData = ClubHeadData(
            speed=clubData['ClubHeadSpeed'],
        )

        self._client.sendall('{"Details":"Success.","SubType":"SetClubData","Type":"ACK"}'.encode('UTF-8'))


    def sendShot(self, gsProConnect):
        self._client.sendall('{"Details":"Success.","SubType":"SendShot","Type":"ACK"}'.encode('UTF-8'))

        gsProConnect.launch_ball(self._ballData, self._clubData)

        data = self._client.recv(1096)
        if data:
            self._client.sendall('{"Details":{"Apex":62.2087860107422,"BallData":{"BackSpin":4690.28662109375,"BallSpeed":151.587356567383,"LaunchAngle":17.7735958099365,"LaunchDirection":-5.00650501251221,"SideSpin":-542.832092285156,"SpinAxis":353.398223876953,"TotalSpin":4721.59423828125},"BallInHole":false,"BallLocation":"Fringe","CarryDeviationAngle":357.429321289063,"CarryDeviationFeet":-19.5566101074219,"CarryDistance":436.027191162109,"ClubData":{"ClubAngleFace":-2.42121529579163,"ClubAnglePath":-10.2835702896118,"ClubHeadSpeed":110.317367553711,"ClubHeadSpeedMPH":75.2163848876953,"ClubType":"7Iron","SmashFactor":1.37410235404968},"DistanceToPin":122.404106140137,"TotalDeviationAngle":356.053466796875,"TotalDeviationFeet":-32.0723648071289,"TotalDistance":465.995697021484},"SubType":"ShotComplete","Type":"SimCommand"}'.encode('UTF-8'))
            
            resp = self._client.recv(1096)

            if(resp):
                self._client.sendall('{"SubType":"Disarm","Type":"SimCommand"}'.encode('UTF-8'))

                print('Garmin ready for next shot...')
                return
        else:
            print('shot corrupted from garmin.  Try another shot...')
            self._client.sendall('{"SubType":"Disarm","Type":"SimCommand"}'.encode('UTF-8'))

            return

           

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
                data = self._client.recv(12000)
            except socket.error as e:
                print('non timeout error:')
                print(e)
                sys.exit(1)
            else:
                if len(data) == 0:
                    print('orderly shutdown on server end')
                    sys.exit(0)
                else:
                    print('garminConnect data recieved')
                    try:
                        dataObj = json.loads(data.decode('UTF-8'))
                    except ValueError:
                        print('unable to parse data:')
                        print(data.decode('UTF-8'))
                        continue
                    
                    print(dataObj['Type'])

                    if(dataObj['Type'] == 'Handshake'):
                        self.handle_handshake()
                    elif(dataObj['Type'] == 'SetClubType'):
                        self.sendFakeShot(gsProConnect)
                    elif(dataObj['Type'] == 'SetBallData'):
                        self.setBallData(dataObj['BallData'])
                    elif(dataObj['Type'] == 'SetClubData'):
                        self.setClubData(dataObj['ClubData'])
                    elif(dataObj['Type'] == 'SendShot'):
                        self.sendShot(gsProConnect)
                    # elif(dataObj['Type'] == 'Pong'):
                    #     self.resetTimer()
                    continue

    def terminate_session(self):
        if(self._socket):
            self._socket.close()

