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
        self.params = {}
        self.img_metadata = {}
        self.device_label = "Camera"
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
        name = self.instr.get_property(self.device_label, "Description")
        self.params["Description"] = name
        return name


    def get_image(self):
        if "Hamamatsu" in self.params["Description"]:
            self.set_scan_mode(1)   # Hamamatsu gives unknown error at long exposure times. The line helps
        self.instr.snap_image()
        tagged_image = self.instr.get_tagged_image()
        h = tagged_image.tags['Height']
        w = tagged_image.tags['Width']
        img = np.reshape(tagged_image.pix[0:h * w], newshape=[h, w])
        self.params['Height'] = h
        self.params['Width'] = w
        # save image metadata not about camera
        for key in tagged_image.tags:
            if "Camera-" not in key:
                self.img_metadata[key] = tagged_image.tags[key]
        # save parameters of the camera only 
        for key in tagged_image.tags.keys():
            if "Camera-" in key:
                self.params[key.split("-")[1]] = tagged_image.tags[key]
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
        self.params['Height'] = tagged_image.tags['Height']
        self.params['Width'] = tagged_image.tags['Width']
        self.img_metadata = tagged_image.tags
        return img

    def get_params(self):
        self.params["Exposure"] = f'{self.instr.get_exposure()} ms'
        self.params["Binning"] = self.instr.get_property(self.device_label, "Binning")
        self.params["PMode"] = self.instr.get_property(self.device_label, "PMode")
        self.params["PixelType"] = self.instr.get_property(self.device_label, "PixelType")
        self.params["Gain"] = self.instr.get_property(self.device_label, "Gain")
        if self.show:
            for key in self.params:
                message = f'{key}: {self.params[key]}'
                self.log(message)
        return self.params

    def get_exposure_time(self):
        exp_time = self.instr.get_property(self.device_label, "Exposure")
        self.params["Exposure"] = exp_time
        return exp_time

    def set_exposure(self, val):
        # if val <= 8000:
        #     self.instr.set_exposure(val)
        # else:
        #     self.log(f'Value exceeds maximum. \n\
        #             Setting to maximum acquisition time: 8 000 ms.')
        #     self.instr.set_exposure(8000)
        if "Hamamatsu" in self.name:
            # if val > 1000:
            #     self.instr.set_property(self.device_label, "EXPOSURE TIME UNITS", 'SECONDS')
            scan_mode = int(self.get_scan_mode())
            if scan_mode == 2:
                exp_step = float(self.instr.get_property(self.device_label, "INTERNAL LINE INTERVAL"))
            else:
                exp_step = 0.03394 + 0.0001 / 11  # step for Ultra Quiet mode
            # exp_step = float(self.instr.get_property_lower_limit(self.device_label, "Exposure"))
            ratio = -(-val // exp_step)  # in ms, round up to integer
            val = exp_step * ratio  # calculation of the new exposure value
        self.instr.set_exposure(val)
        # exp_time = self.instr.get_property(self.device_label, "Exposure")
        self.params["Exposure"] = val

    def set_shortest_exposure(self):
        if "Hamamatsu" in self.name:
            if self.get_scan_mode() == "2":
                # exp_step = float(self.instr.get_property(self.device_label, "INTERNAL LINE INTERVAL"))
                val = self.instr.get_property_lower_limit(self.device_label, "Exposure")
                self.set_exposure(val * 1.1)  # lower limit freezes MM with Hamamatsu cam
            else:
                self.set_exposure(0.05)
        else:
            self.set_exposure(0.02)
        print(f"Exposure time: {self.get_exposure_time()} ms")
        exp_time = self.instr.get_property(self.device_label, "Exposure")
        self.params["Exposure"] = exp_time

    def set_binning(self, binning=1):
        if isinstance(binning, int):
            val = f"{binning}x{binning}"
        else:
            val = binning
        self.instr.set_property(self.device_label, "Binning", val)
        binning = self.instr.get_property(self.device_label, "Binning")
        self.params["Binning"] = binning

    def get_binning(self):
        binning = self.instr.get_property(self.device_label, "Binning")
        self.params["Binning"] = binning
        return binning

    def get_PMode(self):
        if "Hamamatsu" in self.name:
            mode = self.instr.get_property(self.device_label, "SENSOR MODE")
        elif self.instr.has_property(self.device_label, "PMode"):
            mode = self.instr.get_property(self.device_label, "PMode")
        else:
            mode = None
        self.params["PMode"] = mode
        return mode

    def set_PMode(self, mode="Normal"):
        if "Hamamatsu" in self.name:
            self.instr.set_property(self.device_label, "SENSOR MODE", mode)
        elif self.instr.has_property(self.device_label, "PMode"):
            self.instr.set_property(self.device_label, "PMode", mode)
        self.get_PMode()

    def get_allPModevalues(self):
        if "Hamamatsu" in self.name:
            javalist = self.instr.get_allowed_property_values(self.device_label, "SENSOR MODE")
        elif self.instr.has_property(self.device_label, "PMode"):
            javalist = self.instr.get_allowed_property_values(self.device_label, "PMode")
        else:
            return
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def set_PixelType(self, val):
        if self.instr.has_property(self.device_label, "PixelType"):
            self.instr.set_property(self.device_label, "PixelType", val)
        self.get_PixelType()

    def get_PixelType(self):
        if self.instr.has_property(self.device_label, "PixelType"):
            px_type =  self.instr.get_property(self.device_label, "PixelType")
        else:
            px_type = None
        self.params["PixelType"] = px_type
        return px_type

    def set_gain(self, val=1):
        if "Hamamatsu" in self.name:
            return
        else:
            self.instr.set_property(self.device_label, "Gain", str(val))
        # self.get_params()

    def get_gain(self):
        if self.instr.has_property(self.device_label, "Gain"):
            gain = self.instr.get_property(self.device_label, "Gain")
        else:
            gain = 1
        self.params["Gain"] = gain
        return gain

    def get_allGainvalues(self):
        if self.instr.has_property(self.device_label, "Gain"):
            javalist = self.instr.get_allowed_property_values(self.device_label, "Gain")
            allowed = []
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
            return allowed
        else:
            return 1

    def get_BitDepth(self):
        if "Hamamatsu" in self.name:
            bit_depth =  self.instr.get_property(self.device_label, "Bits per Channel")
        elif self.instr.has_property(self.device_label, "BitDepth"):
            bit_depth =  self.instr.get_property(self.device_label, "BitDepth")
        else:
            bit_depth = None
        self.params["BitDepth"] = bit_depth
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
        javalist = self.instr.get_allowed_property_values(self.device_label, "Binning")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_allReadoutRates(self):
        allowed = []
        if self.instr.has_property(self.device_label, "ReadoutRate"):
            javalist = self.instr.get_allowed_property_values(self.device_label, "ReadoutRate")
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
        return allowed

    def set_ReadoutRate(self, val):
        if self.instr.has_property(self.device_label, "ReadoutRate"):
            self.instr.set_property(self.device_label, "ReadoutRate", str(val))
        self.get_ReadoutRate()

    def get_ReadoutRate(self):
        if self.instr.has_property(self.device_label, "ReadoutRate"):
            ro_rate = self.instr.get_property(self.device_label, "ReadoutRate")
        else:
            ro_rate = None
        self.params["ReadoutRate"] = ro_rate
        return ro_rate

    def get_allTriggerModes(self):
        if "Hamamatsu" not in self.name:
            if self.instr.has_property(self.device_label, "TriggerMode"):
                javalist = self.instr.get_allowed_property_values(self.device_label, "TriggerMode")
            else:
                return "Camera has no TriggerMode"
        else:
            if self.instr.has_property(self.device_label, "TRIGGER SOURCE"):
                javalist = self.instr.get_allowed_property_values(self.device_label, "TRIGGER SOURCE")
            else:
                return "Camera has no TriggerMode"
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_TriggerMode(self):
        if self.instr.has_property(self.device_label, "TriggerMode"):
            trg_mode = self.instr.get_property(self.device_label, "TriggerMode")
        elif "Hamamatsu" in self.name:
            trg_mode = self.instr.get_property(self.device_label, "TRIGGER SOURCE")
        else:
            trg_mode = None
        self.params["TriggerMode"] = trg_mode
        return trg_mode

    def set_TriggerMode(self, val="Timed"):
        # Options we used in experiments (for Teledyne cameras):
        # Timed - internal trigger
        # Strobed - external trigger / internal exposure time
        # Bulb - external trigger / external exposure time
        if "Hamamatsu" not in self.name:
            self.instr.set_property(self.device_label, "TriggerMode", str(val))
        else:  # adaptation for Hamamatsu Quest v1
            if val == "Timed":
                val = "INTERNAL"
            elif val == "Strobed":
                val = "EXTERNAL"
                self.instr.set_property(self.device_label, "TRIGGER GLOBAL EXPOSURE", "GLOBAL RESET")
                self.set_trigger_polarity("POSITIVE")
            self.instr.set_property(self.device_label, "TRIGGER SOURCE", str(val))
            mode = self.instr.get_property(self.device_label, "TRIGGER SOURCE")
            print(f"Trigger mode: {mode}")
        self.get_TriggerMode()

    def set_trigger_polarity(self, val="POSITIVE"):
        # if "Hamamatsu" in self.name:
        if self.instr.has_property(self.device_label, "TriggerPolarity"):
            self.instr.set_property(self.device_label, "TriggerPolarity", str(val))
        self.get_TriggerPolarity()

    def get_TriggerPolarity(self):
        if self.instr.has_property(self.device_label, "TriggerPolarity"):
            trg_polarity = self.instr.get_property(self.device_label, "TriggerPolarity")
        else:
            trg_polarity = None
        self.params["TriggerPolarity"] = trg_polarity
        return trg_polarity

    def get_allTriggerPolarities(self):
        if self.instr.has_property(self.device_label, "TriggerPolarity"):
            javalist = self.instr.get_allowed_property_values(self.device_label, "TriggerPolarity")
            allowed = []
            for index in range(javalist.capacity()):
                allowed.append(javalist.get(index))
            return allowed
        else:
            return "Camera has no TriggerPolarity"

    def get_allExposureTimes(self):
        javalist = self.instr.get_allowed_property_values(self.device_label, "Exposure")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        return allowed

    def get_scan_mode(self):  # for Hamamatsu cam
        if "Hamamatsu" in self.name:
            result = self.instr.get_property(self.device_label, "ScanMode")
        else:
            result = "Global shutter"
        self.params["ScanMode"] = result
        return result

    def set_scan_mode(self, val):  # for Hamamatsu cam
        # 1 = low nise mode
        # 2 = fast mode
        if "Hamamatsu" in self.name:
            self.instr.set_property(self.device_label, "ScanMode", 1)   # we will work in most sensitive mode always
        else:
            # for Teledyne camera
            match val:
                case 1:
                    self.instr.set_property(self.device_label, "PMode", "Alternate Normal")
                    ro_rates = self.get_allReadoutRates()
                    self.set_ReadoutRate(ro_rates[0])
                case _:
                    self.instr.set_property(self.device_label, "PMode", "Normal")
        self.get_scan_mode()


    def set_property(self, prorerty, value):
        if self.instr.has_property(self.device_label, prorerty):
            self.instr.set_property(self.device_label, prorerty, value)


    def get_test(self):
        low_limit = self.instr.get_property_lower_limit(self.device_label, "Exposure")
        upper_limit = self.instr.get_property_upper_limit(self.device_label, "Exposure")
        print(f"Lower limit: {low_limit}")
        print(f"Upper limit: {upper_limit}")
        javalist = self.instr.get_allowed_property_values(self.device_label, "Exposure")
        allowed = []
        for index in range(javalist.capacity()):
            allowed.append(javalist.get(index))
        print(f"Allowed: {allowed}")
        is_limited = self.instr.has_property_limits(self.device_label, "Exposure")
        print(f"Are limits?: {is_limited}")
        javalist2 = self.instr.get_device_property_names(self.device_label)
        property_names = []
        for index in range(javalist.capacity()):
            property_names.append(javalist.get(index))
        exp_type = self.instr.get_property_type(self.device_label, "Exposure")
        print(f"Type: {exp_type}")
        return


if __name__ == "__main__":
    camera = MMcamera()
    camera.set_exposure(5575)
    # camera.set_shortest_exposure()
    print(f"Exposure time: {camera.get_exposure_time()} ms")
    # print(f"All allowed Exposure times: {camera.get_allExposureTimes()}")
    # print(f"Result of test: {camera.get_test()}")
    # camera.setMaxSens("8x8")
    # camera.set_MaxSens(4)
    # camera.set_gain(2)

    print(f"All allowed binning options: {camera.get_allBinningvalues()}")
    camera.set_binning(4)
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
    camera.set_scan_mode(1)
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
    # camera.set_scan_mode(1)
    camera.plot_img()
    print(camera.params)
    np.save('cam_settings.npy', camera.params)
