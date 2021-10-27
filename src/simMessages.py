import json

class simMessages:
    
    def get_success_message(self, type):
        message = {
            "Details":"Success.",
            "SubType":type,
            "Type":"ACK"
        }
        return json.dumps(message).encode('UTF-8')

    def get_sim_command(self, type):
        message = {
            "SubType":type,
            "Type":"SimCommand"
        }
        return json.dumps(message).encode('UTF-8')

    def get_handshake_message(self, step):
        if(step == 1):
            message = {
                "Challenge": "gQW3om37uK4OOU4FXQH9GWgljxOrNcL5MvubVHAtQC0x6Z1AwJTgAIKyamJJMzm9", "E6Version": "2, 0, 0, 0",
                "ProtocolVersion": "1.0.0.5",
                "RequiredProtocolVersion": "1.0.0.0",
                "Type": "Handshake"
            }
        elif(step == 2):
            message = {
                "Success":"true",
                "Type":"Authentication"
            }
        else:
            message = {
                "Success":"true",
                "Type":"Authentication"
            }
            
        return json.dumps(message).encode('UTF-8')

    def get_shot_complete_message(self):
        message = {
            "Details":{
                "Apex":62.2087860107422,
                "BallData":{
                    "BackSpin":4690.28662109375,
                    "BallSpeed":151.587356567383,
                    "LaunchAngle":17.7735958099365,
                    "LaunchDirection":-5.00650501251221,
                    "SideSpin":-542.832092285156,
                    "SpinAxis":353.398223876953,
                    "TotalSpin":4721.59423828125
                },
                "BallInHole":False,
                "BallLocation":"Fringe",
                "CarryDeviationAngle":357.429321289063,"CarryDeviationFeet":-19.5566101074219,
                "CarryDistance":436.027191162109,
                "ClubData":{
                    "ClubAngleFace":-2.42121529579163,
                    "ClubAnglePath":-10.2835702896118,
                    "ClubHeadSpeed":110.317367553711,
                    "ClubHeadSpeedMPH":75.2163848876953,
                    "ClubType":"7Iron",
                    "SmashFactor":1.37410235404968
                },
                "DistanceToPin":122.404106140137,
                "TotalDeviationAngle":356.053466796875,"TotalDeviationFeet":-32.0723648071289,
                "TotalDistance":465.995697021484
            },
            "SubType":"ShotComplete",
            "Type":"SimCommand"
        }
        return json.dumps(message, indent=4).encode('UTF-8')