# Import micromanager classes
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
        self.param = {}
        self.name = self.get_camera_name()
        print(f"Camera {self.name} is connected")
        self.show = show
        self.method_get = 'get_params'
        self.method_set = 'set_params'
        self.method_det = 'get_image_1D'

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}  {message}')

    def get_camera_name(self):
        name = self.instr.get_property("Camera", "Description")
        self.param["Name"] = name
        return name

    def get_image(self):
        self.instr.snap_image()
        tagged_image = self.instr.get_tagged_image()
        h = tagged_image.tags['Height']
        w = tagged_image.tags['Width']
        img = np.reshape(tagged_image.pix[0:h * w], newshape=[h, w])
        self.param['Height'] = h
        self.param['Width'] = w
        return img

    def plot_img(self):
        img = self.get_image()
        plt.imshow(img, cmap='gray')
        plt.colorbar(orientation='vertical')
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

    def get_exposure_time(self):
        exp_time = self.instr.get_property("Camera", "Exposure")
        self.param["Exp time"] = exp_time
        return exp_time

    def set_exposure(self, val):
        # if val <= 8000:
        #     self.instr.set_exposure(val)
        # else:
        #     self.log(f'Value exceeds maximum. \n\
        #             Setting to maximum acquisition time: 8 000 ms.')
        #     self.instr.set_exposure(8000)
        if "Hamamatsu" in self.name:
            scan_mode = int(self.get_scan_mode())
            if scan_mode == 2:
                exp_step = float(self.instr.get_property("Camera", "INTERNAL LINE INTERVAL"))
            else:
                exp_step = 0.03394 + 0.0001 / 11  # step for Ultra Quiet mode
            # exp_step = float(self.instr.get_property_lower_limit("Camera", "Exposure"))
            ratio = -(-val // exp_step)  # in ms, round up to integer
            val = exp_step * ratio  # calculation of the new exposure value
        self.instr.set_exposure(val)
        exp_time = self.instr.get_property("Camera", "Exposure")
        self.param["Exp time"] = exp_time

    def set_shortest_exposure(self):
        if "Hamamatsu" in self.name:
            if self.get_scan_mode() == "2":
                # exp_step = float(self.instr.get_property("Camera", "INTERNAL LINE INTERVAL"))
                val = self.instr.get_property_lower_limit("Camera", "Exposure")
                self.set_exposure(val * 1.1)  # lower limit freezes MM with Hamamatsu cam
            else:
                self.set_exposure(0.05)
        else:
            self.set_exposure(0.02)
        print(f"Exposure time: {self.get_exposure_time()} ms")
        exp_time = self.instr.get_property("Camera", "Exposure")
        self.param["Exp time"] = exp_time

    def set_binning(self, binning=1):
        if isinstance(binning, int):
            val = f"{binning}x{binning}"
        else:
            val = binning
        self.instr.set_property("Camera", "Binning", val)
        binning = self.instr.get_property("Camera", "Binning")
        self.param["Binning"] = binning

    def get_binning(self):
        binning = self.instr.get_property("Camera", "Binning")
        self.param["Binning"] = binning
        return binning

    def get_PMode(self):
        if "Hamamatsu" in self.name:
            mode = self.instr.get_property("Camera", "SENSOR MODE")
        elif self.instr.has_property("Camera", "PMode"):
            mode = self.instr.get_property("Camera", "PMode")
        else:
            mode = None
        self.param["PMode"] = mode
        return mode

    def set_PMode(self, mode="Normal"):
        if "Hamamatsu" in self.name:
            self.instr.set_property("Camera", "SENSOR MODE", mode)
        elif self.instr.has_property("Camera", "PMode"):
            self.instr.set_property("Camera", "PMode", mode)
        self.get_PMode()

    def get_allPModevalues(self):
        if "Hamamatsu" in self.name:
            javalist = self.instr.get_allowed_property_values("Camera", "SENSOR MODE")
        elif self.instr.has_property("Camera", "PMode"):
            javalist = self.instr.get_allowed_property_values("Camera", "PMode")
        else:
            return
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def set_PixelType(self, val):
        if self.instr.has_property("Camera", "PixelType"):
            self.instr.set_property("Camera", "PixelType", val)
        self.get_PixelType()

    def get_PixelType(self):
        if self.instr.has_property("Camera", "PixelType"):
            px_type =  self.instr.get_property("Camera", "PixelType")
        else:
            px_type = None
        self.param["PixelType"] = px_type
        return px_type

    def set_gain(self, val=1):
        if "Hamamatsu" in self.name:
            return
        else:
            self.instr.set_property("Camera", "Gain", str(val))
        # self.get_params()

    def get_gain(self):
        if self.instr.has_property("Camera", "Gain"):
            gain = self.instr.get_property("Camera", "Gain")
        else:
            gain = 1
        self.param["Gain"] = gain
        return gain

    def get_allGainvalues(self):
        if self.instr.has_property("Camera", "Gain"):
            javalist = self.instr.get_allowed_property_values("Camera", "Gain")
            allowed = []
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
            return allowed
        else:
            return 1

    def get_BitDepth(self):
        if "Hamamatsu" in self.name:
            bit_depth =  self.instr.get_property("Camera", "Bits per Channel")
        elif self.instr.has_property("Camera", "BitDepth"):
            bit_depth =  self.instr.get_property("Camera", "BitDepth")
        else:
            bit_depth = None
        self.param["BitDepth"] = bit_depth
        return bit_depth

    def set_MaxSens(self, binning=4, mode="PHOTON NUMBER RESOLVING"):
        self.set_binning(binning)
        if "Hamamatsu" in self.name:
            self.set_PMode(mode)
        else:
            # for PVCAM cameras
            self.set_PMode("Alternate Normal")
            self.set_gain(2)

    def get_allBinningvalues(self):
        javalist = self.instr.get_allowed_property_values("Camera", "Binning")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_allReadoutRates(self):
        allowed = []
        if self.instr.has_property("Camera", "ReadoutRate"):
            javalist = self.instr.get_allowed_property_values("Camera", "ReadoutRate")
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
        return allowed

    def set_ReadoutRate(self, val):
        if self.instr.has_property("Camera", "ReadoutRate"):
            self.instr.set_property("Camera", "ReadoutRate", str(val))
        self.get_ReadoutRate()

    def get_ReadoutRate(self):
        if self.instr.has_property("Camera", "ReadoutRate"):
            ro_rate = self.instr.get_property("Camera", "ReadoutRate")
        else:
            ro_rate = None
        self.param["ReadoutRate"] = ro_rate
        return ro_rate

    def get_allTriggerModes(self):
        if "Hamamatsu" not in self.name:
            if self.instr.has_property("Camera", "TriggerMode"):
                javalist = self.instr.get_allowed_property_values("Camera", "TriggerMode")
            else:
                return "Camera has no TriggerMode"
        else:
            if self.instr.has_property("Camera", "TRIGGER SOURCE"):
                javalist = self.instr.get_allowed_property_values("Camera", "TRIGGER SOURCE")
            else:
                return "Camera has no TriggerMode"
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_TriggerMode(self):
        if self.instr.has_property("Camera", "TriggerMode"):
            trg_mode = self.instr.get_property("Camera", "TriggerMode")
        elif "Hamamatsu" in self.name:
            trg_mode = self.instr.get_property("Camera", "TRIGGER SOURCE")
        else:
            trg_mode = None
        self.param["TriggerMode"] = trg_mode
        return trg_mode

    def set_TriggerMode(self, val="Timed"):
        # Options we used in experiments (for Teledyne cameras):
        # Timed - internal trigger
        # Strobed - external trigger / internal exposure time
        # Bulb - external trigger / external exposure time
        if "Hamamatsu" not in self.name:
            self.instr.set_property("Camera", "TriggerMode", str(val))
        else:  # adaptation for Hamamatsu Quest v1
            if val == "Timed":
                val = "INTERNAL"
            elif val == "Strobed":
                val = "EXTERNAL"
                self.instr.set_property("Camera", "TRIGGER GLOBAL EXPOSURE", "GLOBAL RESET")
                self.set_trigger_polarity("POSITIVE")
            self.instr.set_property("Camera", "TRIGGER SOURCE", str(val))
            mode = self.instr.get_property("Camera", "TRIGGER SOURCE")
            print(f"Trigger mode: {mode}")
        self.get_TriggerMode()

    def set_trigger_polarity(self, val="POSITIVE"):
        # if "Hamamatsu" in self.name:
        if self.instr.has_property("Camera", "TriggerPolarity"):
            self.instr.set_property("Camera", "TriggerPolarity", str(val))
        self.get_TriggerPolarity()

    def get_TriggerPolarity(self):
        if self.instr.has_property("Camera", "TriggerPolarity"):
            trg_polarity = self.instr.get_property("Camera", "TriggerPolarity")
        else:
            trg_polarity = None
        self.param["TriggerPolarity"] = trg_polarity
        return trg_polarity

    def get_allTriggerPolarities(self):
        if self.instr.has_property("Camera", "TriggerPolarity"):
            javalist = self.instr.get_allowed_property_values("Camera", "TriggerPolarity")
            allowed = []
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
            return allowed
        else:
            return "Camera has no TriggerPolarity"

    def get_allExposureTimes(self):
        javalist = self.instr.get_allowed_property_values("Camera", "Exposure")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_scan_mode(self):  # for Hamamatsu cam
        if "Hamamatsu" in self.name:
            result = self.instr.get_property("Camera", "ScanMode")
        else:
            result = "Global shutter"
        self.param["ScanMode"] = result
        return result

    def set_scan_mode(self, val):  # for Hamamatsu cam
        # 1 = low nise mode
        # 2 = fast mode
        if "Hamamatsu" in self.name:
            self.instr.set_property("Camera", "ScanMode", val)
        else:
            # for Teledyne camera
            match val:
                case 1:
                    self.instr.set_property("Camera", "PMode", "Alternate Normal")
                    ro_rates = self.get_allReadoutRates()
                    self.set_ReadoutRate(ro_rates[0])
                case _:
                    self.instr.set_property("Camera", "PMode", "Normal")
        self.get_scan_mode()

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
    # camera.set_exposure(100)
    # camera.set_shortest_exposure()
    print(f"Exposure time: {camera.get_exposure_time()} ms")
    # print(f"All allowed Exposure times: {camera.get_allExposureTimes()}")
    # print(f"Result of test: {camera.get_test()}")
    # camera.setMaxSens("8x8")
    # camera.set_MaxSens(4)
    # camera.set_gain(2)

    print(f"All allowed binning options: {camera.get_allBinningvalues()}")
    # camera.set_binning(4)
    print(f"Binning {camera.get_binning()}")
    print(f"Pixel type {camera.get_PixelType()}")

    print(f"Trigger mode: {camera.get_TriggerMode()}")
    # camera.set_TriggerMode("Timed")
    print(f"Trigger mode: {camera.get_TriggerMode()}")
    print(f"All trigger polarities: {camera.get_allTriggerPolarities()}")
    print(f"Current trigger polarity: {camera.get_TriggerPolarity()}")
    # camera.set_trigger_polarity("POSITIVE")
    print(f"Current trigger polarity: {camera.get_TriggerPolarity()}")

    # camera.set_PMode("Alternate Normal")
    # print(f"PMode {camera.get_PMode()}")
    print(f"All PMode options: {camera.get_allPModevalues()}")
    # camera.set_PMode("AREA")
    print(f"PMode {camera.get_PMode()}")

    print(f"Scan mode: {camera.get_scan_mode()}")
    # camera.set_scan_mode(2)
    print(f"Scan mode: {camera.get_scan_mode()}")

    print(f"Gain: {camera.get_gain()}")
    readout_rates = camera.get_allReadoutRates()
    print(f"All ReadoutRates options: {readout_rates}")
    # camera.set_ReadoutRate(readout_rates[1])
    print(f"Set ReadoutRate: {camera.get_ReadoutRate()}")
    # print(f"Bytes per pixel {camera.getBytesPerPixel()}")
    # img = camera.get_image()
    # camera.set_exposure(0.05)
    # camera.set_MaxSens(4)
    print(f"PMode {camera.get_PMode()}")
    print(f"Scan mode: {camera.get_scan_mode()}")
    # camera.set_shortest_exposure()
    print(f"Exposure time: {camera.get_exposure_time()} ms")

    # camera.set_TriggerMode(val="Strobed")
    print(f"Trigger mode: {camera.get_TriggerMode()}")
    camera.plot_img()
    print(camera.param)
