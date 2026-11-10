# adapted by Nikolai Khokhlov
# from https://labdrivers.readthedocs.io/en/latest/_modules/labdrivers/oxford/itc503.html
# version 2026.06.22

import pyvisa
import time
import re


class TemControlDevice:
    """
    Module to connect to an ITC 503.
    Modes supported: GPIB
    :param gpib_addr: GPIB address of the ITC 503
    """
    # def __init__(self, gpib_addr=24):
    #     resource_manager = pyvisa.ResourceManager()
    #     self.TController = resource_manager.open_resource(f"GPIB::{gpib_addr}::INSTR")
    #     self.TController.read_termination = '\r'
    #     self.status = ('ITC503 Connected')
    #     self.model = "ITC503"
    #     self.state = f'Lakeshore is connected. Model {self.model}'
    def __init__(self):
        self.lakeshore = None
        self.model = None
        self.name = None
        self.state = None
        self.rm = pyvisa.ResourceManager()
        self.all_instruments = self.rm.list_resources()
        print(f'Connected instruments: {self.all_instruments}')

    def init_controller(self, device_name='24'):
        if 'GPIB0::' in str(device_name):
            self.TController = self.rm.open_resource(device_name)
        else:
            self.TController = self.rm.open_resource(f'GPIB0::{device_name}::INSTR')
        self.TController.read_termination = '\r'
        self.status = ('ITC503 Connected')
        self.model = "ITC503"
        self.state = f'ITC503 is connected. Model {self.model}'
        print(self.status)

    def query_temp(self): # get current temperature
        return self.getValue(1)

    def query_setpoint(self): # get current set point
        return self.getValue(0)

    def set_setpoint(self, temperature=0.010): #set new setpoint
        self.setTemperature(float(temperature))

    def setControl(self, unlocked=1, remote=1):
        """Set the LOCAL / REMOTE control state of the ITC 503

        :param unlocked (int): 0 to lock, 1 to unlock
        :param remote (int): 0 for local, 1 for remote
        :return: None
        """
        state_bit = str(remote) + str(unlocked)
        state = int(state_bit, 2)

        self.TController.write("$C{}".format(state))

    def setTemperature(self, temperature=0.010):
        """Change the temperature set point.

        :param temperature (float): Temperature set point in Kelvin (default: 0.010)
        """
        assert type(temperature) in [int, float], 'argument must be a number'

        self.setControl(1, 1)
        command = '$T' + str(int(100 * temperature)/100)
        self.TController.write(command)
        self.setControl(0, 0)

    def setAutoControl(self, auto_manual=0):
        """Sets automatic control for heater/gas(needle valve).

        Value:Status map
            0: heater manual, gas manual
            1: heater auto  , gas manual
            2: heater manual, gas auto
            3: heater auto  , gas auto

        Args:
            auto_manual: Index for gas/manual.
        """
        self.TController.write('$A{}'.format(auto_manual))
       

    def setHeaterOutput(self, heater_output=0):
        """Sets the heater output level.
    
        Args:
            heater_output: Sets the percent of the maximum
                        heater output in units of 0.1%.
                        Min: 0. Max: 999.
        """
    
        self._visa_resource.write('$O{}'.format(heater_output))
        return None
    
    def query_heater_power(self):
        return temp_controller.getValue(5)

    def getValue(self, variable=0):
        """Read the variable defined by the index.
    
        The possible inputs are::
    
            0: SET TEMPERATURE
            1: SENSOR 1 TEMPERATURE
            2: SENSOR 2 TEMPERATURE
            3: SENSOR 3 TEMPERATURE
            4: TEMPERATURE ERROR
            5: HEATER O/P (as %)
            6: HEATER O/P (as V)
            7: GAS FLOW O/P (a.u.)
            8: PROPORTIONAL BAND
            9: INTEGRAL ACTION TIME
            10: DERIVATIVE ACTION TIME
    
        :param variable (int): Index of variable to read.
        """
        assert type(variable) == int, 'Argument must be an integer.'
        assert variable in range(0, 11), 'Argument is not a valid number.'

        # Clear stale data
        # self.TController.clear()
        # self.TController.flush(pyvisa.constants.VI_READ_BUF_DISCARD)

        time.sleep(0.05)  # optional but helps stability
        value = self.TController.query('R{}'.format(variable))

        return float(value.strip('R+'))

if __name__ == "__main__":
    # temp_controller = TemControlDevice(24)# use your GPIB port
    temp_controller = TemControlDevice() #use your GPIB port
    temp_controller.init_controller('GPIB0::24::INSTR')
    print(temp_controller.state)
    # print('SensorTemp:', temp_controller.query_temp())
    # print('SetTemp:', temp_controller.query_setpoint())
    # temp_controller.setControl(1,1)
    temp_controller.set_setpoint(310)
    temp_controller.setAutoControl(3)
    temp_controller.setControl(0, 0)
    temp_controller.getValue(1)
    print('SensorTemp:', temp_controller.getValue(1))
    print('SetTemp:', temp_controller.getValue(0))
    print('Heater pwr:', temp_controller.getValue(5), '%')
