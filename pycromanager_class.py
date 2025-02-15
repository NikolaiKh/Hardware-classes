#Import micromanager classes
from pycromanager import Core
# from pycromanager import Bridge
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


class MMcamera():
    def __init__(self, show=False):
        self.instr = Core()
        # self.instr.set_property('Core', 'AutoShutter', 0)
        self.mmdir = "C:\Program Files\Micro-Manager-2.0.3"
        self.configfile = "MMConfig_pvcam_simple_1.cfg"
        self.name = self.get_camera_name()
        print(f"Camera {self.name } is connected")
        self.show = show
        self.param = {}
        self.method_get = 'get_params'
        self.method_set = 'set_params'
        self.method_det = 'get_image_1D'

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}  {message}')

    def get_camera_name(self):
        return self.instr.get_property("Camera", "Description")

    def get_image(self):
        self.instr.snap_image()
        tagged_image = self.instr.get_tagged_image()
        img = np.reshape(tagged_image.pix, \
                         newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']]).astype(int)
        self.param['Height'] = tagged_image.tags['Height']
        self.param['Width'] = tagged_image.tags['Width']
        return img

    def plot_img(self):
        img = self.get_image()
        plt.imshow(img, cmap='gray')
        plt.show()

    def get_image_1D(self):
        self.instr.snap_image()
        tagged_image = self.instr.get_tagged_image()
        img = tagged_image.pix.astype(int)
        self.param['Height'] = tagged_image.tags['Height']
        self.param['Width'] = tagged_image.tags['Width']
        return img

    def get_params(self):
        self.param["exposure"] = f'{self.instr.get_exposure()} ms'
        self.param["binning"] = self.instr.get_property("Camera", "Binning")
        self.param["pMode"] = self.instr.get_property("Camera", "PMode")
        self.param["pixelType"] = self.instr.get_property("Camera", "PixelType")
        self.param["gain"] = self.instr.get_property("Camera", "Gain")
        if self.show:
            for key in self.param:
                message = f'{key}: {self.param[key]}'
                self.log(message)
        return self.param

    def set_exposure(self, val):
        # if val <= 8000:
        #     self.instr.set_exposure(val)
        # else:
        #     self.log(f'Value exceeds maximum. \n\
        #             Setting to maximum acquisition time: 8 000 ms.')
        #     self.instr.set_exposure(8000)
        self.instr.set_exposure(val)
        # self.instr.set_property("Camera", "Exposure", val)
        # self.get_params()

    def set_binning(self, binning=1):
        if isinstance(binning, int):
            val = f"{binning}x{binning}"
        else:
            val = binning
        self.instr.set_property("Camera", "Binning", val)
        # self.get_params()

    def get_binning(self):
        return self.instr.get_property("Camera", "Binning")

    def get_PMode(self):
        return self.instr.get_property("Camera", "PMode")

    def set_PMode(self, mode="Normal"):
        self.instr.set_property("Camera", "PMode", mode)
        # self.get_params()

    def set_PixelType(self, val):
        self.instr.set_property("Camera", "PixelType", val)
        # self.get_params()

    def set_gain(self, val=1):
        self.instr.set_property("Camera", "Gain", str(val))
        # self.get_params()

    def get_gain(self):
        if "Hamamatsu" in self.name:
            return 1
        else:
            return self.instr.get_property("Camera", "Gain")
    
    def get_BitDepth(self):
        return self.instr.get_property("Camera", "BitDepth")

    def set_MaxSens(self, binning=4):  # for PVCAM cameras
        self.set_binning(binning)
        self.set_PMode("Alternate Normal")
        self.set_gain(2)

    def get_allBinningvalues(self):
        javalist = self.instr.get_allowed_property_values("Camera", "Binning")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_allPModevalues(self):
        javalist = self.instr.get_allowed_property_values("Camera", "PMode")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_allGainvalues(self):
        javalist = self.instr.get_allowed_property_values("Camera", "Gain")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_allReadoutRates(self):
        javalist = self.instr.get_allowed_property_values("Camera", "ReadoutRate")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def set_ReadoutRate(self, val):
        self.instr.set_property("Camera", "ReadoutRate", str(val))

    def get_ReadoutRate(self):
        if "Hamamatsu" in self.name:
            return
        else:
            return self.instr.get_property("Camera", "ReadoutRate")

    def get_allTriggerModes(self):
        javalist = self.instr.get_allowed_property_values("Camera", "TriggerMode")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_TriggerMode(self):
        return self.instr.get_property("Camera", "TriggerMode")

    def set_TriggerMode(self, val="Timed"):
        self.instr.set_property("Camera", "TriggerMode", str(val))

    def get_exposure_time(self):
        return self.instr.get_property("Camera", "Exposure")

    def get_allExposureTimes(self):
        javalist = self.instr.get_allowed_property_values("Camera", "Exposure")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_test(self):
        low_limit = self.instr.get_property_lower_limit("Camera", "Exposure")
        upper_limit = self.instr.get_property_upper_limit("Camera", "Exposure")
        print(f"Lower limit: {low_limit}")
        print(f"Upper limit: {upper_limit}")
        javalist = self.instr.get_allowed_property_values("Camera", "Exposure")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        print(f"Allowed: {allowed}")
        is_limited = self.instr.has_property_limits("Camera", "Exposure")
        print(f"Are limits?: {is_limited}")
        javalist2 = self.instr.get_device_property_names("Camera")
        property_names = []
        for index in range(javalist.capacity()):
            property_names.append(javalist.get(index))
        exp_type = self.instr.get_property_type("Camera", "Exposure")
        print(f"Type: {exp_type}")
        return



if __name__ == "__main__":
    camera = MMcamera()
    # camera.set_exposure(0.1)
    print(f"Explosure time {camera.get_exposure_time()} ms")
    print(f"All allowed Exposure times: {camera.get_allExposureTimes()}")
    print(f"Result of test: {camera.get_test()}")
    # camera.setMaxSens("8x8")
    # camera.set_MaxSens(4)
    # camera.set_gain(2)
    print(f"Binning {camera.get_binning()}")
    print(f"All allowed binning options: {camera.get_allBinningvalues()}")
    # print(f"Pixel type {camera.getPixelType()}")
    # camera.setPMode("Alternate Normal")
    # print(f"PMode {camera.getPMode()}")
    print(f"All PMode options: {camera.get_allPModevalues()}")
    # camera.setGain(2)
    print(f"Gain: {camera.get_gain()}")
    readout_rates = camera.get_allReadoutRates()
    print(f"All ReadoutRates options: {readout_rates}")
    # camera.set_ReadoutRate(readout_rates[1])
    print(f"Setted ReadoutRate: {camera.get_ReadoutRate()}")
    # print(f"Bytes per pixel {camera.getBytesPerPixel()}")
    # img = camera.get_image()
    camera.plot_img()
