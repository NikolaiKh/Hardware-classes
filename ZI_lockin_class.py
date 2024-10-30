import time
import numpy as np
import zhinst.utils

class Lockin:
    def __init__(self):
        self.device_id = "dev5041"  # Device serial number available on its rear panel.
        server_host = "localhost"
        server_port = 8004
        api_level = 6  # Maximum API level supported for all instruments except HF2LI.

        (self.daq, self.device, _) = zhinst.utils.create_api_session(
            self.device_id, api_level, server_host=server_host, server_port=server_port
        )

        self.daq.unsubscribe("*")
        self.daq.sync()
        self.daq.set(f"/{self.device}/demods/0/enable", 1)
        self.daq.setInt(f'/{self.device}/extrefs/0/demodselect', 0)
        self.daq.setInt(f'/{self.device}/extrefs/0/enable', 1)
        self.daq.setInt(f'/{self.device}/extrefs/1/demodselect', 2)
        self.daq.setInt(f'/{self.device}/extrefs/1/enable', 1)
        self.daq.setInt(f'/{self.device}/demods/2/oscselect', 2)
        self.daq.setInt(f'/{self.device}/demods/0/adcselect', 8)
        self.daq.setInt(f'/{self.device}/demods/2/adcselect', 9)

        path = f"/{self.device}/demods/0/sample"
        self.daq.subscribe(path)

        time_c = self.get_time_constant()
        while True:
            try:
                data_read = self.daq.poll(time_c, 1, 0, True)
                print(np.mean(data_read[f"/{self.device}/demods/0/sample"]["x"]))
                break
            except:
                pass
        self.state = f'ZI lock-in is connected. ID {self.device_id}'

    def getXYR(self):

        time_c = self.get_time_constant()
        while True:
            try:
                data_read = self.daq.poll(time_c, 1, 0, True)
                sigX = np.mean(data_read[f"/{self.device}/demods/0/sample"]["x"])
                sigY = np.mean(data_read[f"/{self.device}/demods/0/sample"]["y"])
                sigR = np.sqrt(sigX**2+sigY**2)
                break
            except:
                pass

        return [sigX, sigY, sigR]


    def get_time_constant(self):
        return self.daq.getDouble(f"/{self.device}/demods/0/timeconstant")


if __name__ == "__main__":
    lia = Lockin()
    print(lia.getXYR())
    print(lia.get_time_constant())
    print(lia.daq.getDouble(f"/{lia.device}/oscs/0/freq"))
    print(lia.daq.getDouble(f"/{lia.device}/oscs/2/freq"))
    lia.daq.unsubscribe("*")
