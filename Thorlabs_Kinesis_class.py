from pylablib.devices import Thorlabs
import time
from datetime import datetime


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}  {message}')


class LinearStage:
    def __init__(self, channel=1, sn="103399144", is_rack_system=True, scale=1e6/50):
        self.stage = None #no connection still
        self.position = None
        self.channel = channel
        self.sn = sn
        self.is_rack_system = is_rack_system
        self.scale = scale
        self.init()  # Stage initialization

    def init(self):
        # Stage initialization
        log(f"List of Thorlabs devices: {Thorlabs.list_kinesis_devices()}")
        self.stage = Thorlabs.KinesisMotor(self.sn, is_rack_system=self.is_rack_system, scale=self.scale, default_channel=self.channel)  # connect to the stage
        status = self.stage.get_status()
        log(status)
        if not 'enabled' in status:
            self.stage._enable_channel() # enable if nedeed
        self.stage.home(sync=True, force=False)  # home the stage, if nedeed, and wait until homing is done
        log(f"Stage status: {self.stage.get_status()}")
        self.position = self.get_position()

    def move_to(self, position):
        self.position = position
        try:
            self.stage.move_to(position * self.scale)
            self.stage.wait_move()  # wait until moving is done
        except:  # if XPS controller crashed
            while True:
                time.sleep(20)
                try:
                    log("Reconnecting to stage controller")
                    self.init()
                    self.stage.move_to(position * self.scale)
                    log(f"Channel #{self.channel} reconnected")
                    break
                except:
                    log(f"Reconnecting Thorlabs channel #{self.channel} again")
        # self.get_position()

    def get_position(self):
        try:
            pos = round(self.stage.get_position()/self.scale, 5)
        except:  # if controller crashed
            while True:
                time.sleep(20)
                try:
                    log("Reconnecting to stage controller")
                    self.init()
                    self.move_to(self.position)
                    pos = round(self.stage.get_position()/self.scale, 5)
                    log(f"Channel #{self.channel} reconnected")
                    break
                except:
                    log(f"Reconnecting Thorlabs channel #{self.channel} again")
        log(f"Stage position: {pos:.5f}mm")
        return pos


if __name__ == "__main__":

    delay_stage = LinearStage(channel=3)
    delay_stage.move_to(80)

    # print(Thorlabs.list_kinesis_devices())
    # scale = 1e6 / 50
    # stage = Thorlabs.KinesisMotor("103399144", is_rack_system=True)  # connect to the stage
    # status = stage.get_status(channel=1)
    # if not 'enabled' in status:
    #     stage._enable_channel(enabled=True, channel=1)
    # stage.home(sync=True, force=False, channel=1)  # home the stage, if nedeed, and wait until homing is done
    # print(stage.get_status(channel=1))
    # stage.move_by(10*scale, channel=1)  # move by 1e6 steps = 50 mm
    # stage.wait_move()  # wait until moving is done
    # # stage.jog("+")  # initiate jog (continuous move) in the positive direction
    # # time.sleep(1.)  # wait for 1 second
    # # stage.stop()  # stop the motion
    # print(stage.get_status(channel=1))
    # stage.close()
