import datetime
# Import PI libraries
from pipython import GCSDevice, pitools


class Pi:
    def __init__(self, serial_number, stage, controller, refmodes='FNL', unit={'str': 'mm', 'scale': 1},
                 show=False):
        self.SN = serial_number
        self.stage = stage
        self.controller = controller
        self.refmodes = refmodes
        self.type = 'PI_linear'
        self.unit = unit
        self.method_set = 'set_absolute_position'
        self.method_get = 'get_current_position'
        self.show = show

    def connect(self):
        self.instr = GCSDevice(self.controller)
        self.instr.ConnectUSB(self.SN)
        print(self.instr.qIDN())
        pitools.startup(self.instr, stages=self.stage, refmodes=self.refmodes)
        rangemin = self.instr.qTMN()
        rangemax = self.instr.qTMX()
        self.axes = self.instr.axes[0]
        self.limits = (rangemin[self.axes], rangemax[self.axes])
        self.ready = True
        self.get_current_position()

    def disconnect(self):
        self.instr.CloseConnection()
        message = 'Device closed'
        self.log(message)
        self.ready = False

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}  {message}')

    def check_limits(self, target):
        within_limits = self.limits[0] <= target <= self.limits[1]
        if within_limits is False:
            message = f'Motion out of limits!!\nAxis {self.axes} limits (mm): ({self.limits[0]}, {self.limits[1]})'
            self.log(message)
        return (within_limits)

    def get_current_position(self):
        x_dict = self.instr.qPOS()
        x = x_dict[self.axes]
        if self.show:
            message = f'current position: {x:.2f} mm'
            self.log(message)
        x = round(x, 3)
        return (x)

    # def get_velocity(self):
    #     x_dict = self.instr.qVMX()
    #     x = x_dict[self.axes]
    #     if self.show:
    #         message = f'max velocity: {x:.2f} mm'
    #         self.log(message)
    #     x = round(x, 3)
    #     return (x)

    def set_velocity(self, velocity):
        # currVel = self.instr.qVEL()
        self.instr.VEL(self.axes[0], velocity)
        if self.show:
            message = f'velocity changed to {velocity:.2f} mm/s'
            self.log(message)

    def set_absolute_position(self, target):
        within_limits = self.check_limits(target)
        if within_limits:
            self.ready = False
            self.instr.MOV(self.axes, target)
            pitools.waitontarget(self.instr)
            x = self.get_current_position()
        self.ready = True
        return (x)

    def set_relative_position(self, dx):
        x = self.get_current_position()
        target = x + dx
        self.set_absolute_position(target)


if __name__ == "__main__":
    # test of stage
    pi_stage = Pi(serial_number='0195500405', stage='M-126.CG1', controller='C-863', refmodes='FNL', show=True)
    pi_stage.connect()
    pi_stage.log('Stage connected')
    pi_stage.set_absolute_position(10)
    pi_stage.set_velocity(0.6)
    pi_stage.set_absolute_position(12)
    pi_stage.disconnect()
