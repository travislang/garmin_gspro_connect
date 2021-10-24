import socket
import sys
import json
from shot_data import BallData, ClubHeadData


# s.close()


class GarminConnect:
    def __init__(self, ip_address, port) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client = ''
        self._handshake_step = 1
        self._listening = 'false'
        self._ballData = BallData
        self._clubData = ClubHeadData

        print('GarminConnect socket created')
        #Bind socket to local host and port
        try:
            self._socket.bind((ip_address, port))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            print(msg)
            sys.exit()

        self._socket.listen(10)

    def spoof_handshake(self):
        step1 = '{"Challenge": "gQW3om37uK4OOU4FXQH9GWgljxOrNcL5MvubVHAtQC0x6Z1AwJTgAIKyamJJMzm9", "E6Version": "2, 0, 0, 0", "ProtocolVersion": "1.0.0.5", "RequiredProtocolVersion": "1.0.0.0", "Type": "Handshake"}'
        step2 = '{"Success":"true","Type":"Authentication"}'

        if(self._handshake_step == 1):
            return step1.encode('UTF-8')
        if(self._handshake_step == 2):
            return step2.encode('UTF-8')

        
    def init_handshake(self):
        while not self._client:
            conn, addr = self._socket.accept()
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
            self._client = conn

        while self._client and self._handshake_step < 3:
            data = self._client.recv(10000)
            if data:
                print('garminConnect handshake data recieved')
                print(data.decode('UTF-8'))

                self._client.sendall(self.spoof_handshake())

                self._handshake_step += 1

        return

    def listen(self):
        while self._listening:
            data = self._client.recv(10000)
            if data:
                print('garminConnect data recieved')
                print(data.decode('UTF-8'))

        return

    def sendPong(self):
        self._client.sendall('{"Type":"Pong"}'.encode('UTF-8'))

    def sendBallData(self, ballData, gsProConnect):
        self._ballData = BallData(
            ballspeed=ballData['BallSpeed'],
            spinaxis=ballData['SpinAxis'],
            totalspin=ballData['TotalSpin'],
            backspin=ballData['BackSpin'],
            sidespin=ballData['SideSpin'],
            hla=ballData['LaunchDirection'],
            vla=ballData['LaunchAngle'],
            carry=ballData['CarryDistance'],
        )

        # # simulate a :BOMB:
        # ball_data = BallData(
        #     ballspeed=166.8,
        #     spinaxis=-13.2,
        #     totalspin=2350.2,
        #     backspin=2350.2,
        #     sidespin=0.0,
        #     hla=0.0,
        #     vla=13.5,
        #     carry=300.0,
        # )

        # not supported yet
        self._clubData = ClubHeadData()

        gsProConnect.launch_ball(self._ballData, self._clubData)

    # XËRËW×ýÞEØ)@À¨{À¨{â	³¹øªÌ*lõ¼nPýy{"Details": {"ClubType": "7Iron", "Handedness": "Right", "PlayerName": "Guest.1", "UserID": "992e8dd3-10fb-4142-98c3-646e490e5711"}, "SubType": "PlayerDataModified", "Type": "SimCommand"}

    # {"BallData": {"BallSpeed": 103.35501, "LaunchAngle": 17.773596, "LaunchDirection": -5.006505, "SpinAxis": 353.39822, "TotalSpin": 4721.594}, "Type": "SetBallData"}

    # //send as resp {"Details": "Success.", "SubType": "SetBallData", "Type": "ACK"}

    # {{"Details":{"Apex":62.2087860107422,"BallData":{"BackSpin":4690.28662109375,"BallSpeed":151.587356567383,"LaunchAngle":17.7735958099365,"LaunchDirection":-5.00650501251221,"SideSpin":-542.832092285156,"SpinAxis":353.398223876953,"TotalSpin":4721.59423828125},"BallInHole":false,"BallLocation":"Fringe","CarryDeviationAngle":357.429321289063,"CarryDeviationFeet":-19.5566101074219,"CarryDistance":436.027191162109,"ClubData":{"ClubAngleFace":-2.42121529579163,"ClubAnglePath":-10.2835702896118,"ClubHeadSpeed":110.317367553711,"ClubHeadSpeedMPH":75.2163848876953,"ClubType":"7Iron","SmashFactor":1.37410235404968},"DistanceToPin":122.404106140137,"TotalDeviationAngle":356.053466796875,"TotalDeviationFeet":-32.0723648071289,"TotalDistance":465.995697021484},"SubType":"ShotComplete","Type":"SimCommand"}

    def listenForShots(self, gsProConnect):
        while self._listening:
            data = self._client.recv(10000)
            if data:
                dataObj = json.loads(data.decode('UTF-8'))
                print('garminConnect data recieved')
                print(dataObj['Type'])

                if(dataObj['Type'] == 'SimCommand'):
                    if(dataObj['SubType'] == 'Ping'):
                        self.sendPong()
                    elif(dataObj['SubType'] == 'ShotComplete'):
                        self.sendBallData(
                            dataObj['Details']['BallData'], gsProConnect)
                # elif(dataObj['Type'] == 'SetBallData'):
                #     self.setBallData(dataObj['Type'])

        return

    def terminate_session(self):
        if(self._socket):
            self._socket.shutdown()




    # def send_heartbeat(self):
    #     payload = {
    #         "DeviceID": self._device_id,
    #         "Units": self._units,
    #         "ShotNumber": self._shot_number,
    #         "APIversion": self._api_version,
    #         "ShotDataOptions": {
    #             "ContainsBallData": False,
    #             "ContainsClubData": False,
    #             "LaunchMonitorIsReady": True,
    #             "LaunchMonitorBallDetected": True,
    #             "IsHeartBeat": True,
    #         },
    #     }
    #     self._socket.sendall(json.dumps(payload).encode("utf-8"))
    #     _logger.info("sent a payload for a heartbeat")
