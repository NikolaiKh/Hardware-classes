import pyvisa
import re


class DelayGenerator:
    def __init__(self, gpibport):
        rm = pyvisa.ResourceManager()
        self.device = rm.open_resource(f'GPIB0::{gpibport}::INSTR')
        # # get SR name and model (830 / 844). It is important for aux_out !!!!
        self.name = self.device.query("*IDN?")
        match = re.search(r"DG(\d{3})", self.name)
        self.model = int(match.group(1))
#         self.model = 830
        self.state = f'Delay generator is connected. Model DG{self.model}'
        print(self.state)


    def send_trigger(self):
        self.device.write("*TRG")
        print("Trigger sent to DG645")
        return


    def get_all_set_trigger_sources(self):
        return (
        "Internal", "External rising edges", "External falling edges", "Single shot external rising edges",
        "Single shot external falling edges", "Single shot", "Line")


    def set_trigger_source(self, val=0):
        # 0 Internal
        # 1 External rising edges
        # 2 External falling edges
        # 3 Single shot external rising edges
        # 4 Single shot external falling edges
        # 5 Single shot
        # 6 Line
        self.device.write(f"TSRC{val}")
        trg_list = self.get_all_set_trigger_sources()
        print(f"Trigger source: {trg_list[val]}")
        return


    def set_delay2channel(self, channel="A", delay=0.0):
        # set time parameters of the "channel"
        # delay = time delay (s) to T0 (for simplicity)
        # Value Channel
        # 0 T0
        # 1 T1
        # 2 A
        # 3 B
        # 4 C
        # 5 D
        # 6 E
        # 7 F
        # 8 G
        # 9 H
        #convert the name to number
        chnls = ('T0', 'T1', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        indx = chnls.index(channel)  # use this value, not name of the port
        #examples:
        #DLAY 2, 0, 10e-6 : Set channel A delay to equal channel T0 plus 10 µs.
        self.device.write(f"DLAY{indx},0,{delay}")
        return


    def set_level_amplitude(self, bnc="AB", ampl=3.5):
        # set voltage of the BNC output "bnc"
        # An output BNC:
        # Value Output
        # 0 T0
        # 1 AB
        # 2 CD
        # 3 EF
        # 4 GH
        # convert the name to number
        chnls = ('T0', 'AB', 'CD', 'EF', 'GH')
        indx = chnls.index(bnc)
        # examples:
        # LAMP 2,3.5<CR> Set the CD output amplitude to 3.5 V
        self.device.write(f"LAMP{indx},{ampl}")
        print(f"Amplitude of {bnc} set to {ampl} V")
        return


    def set_polatity(self, bnc="AB", polarity="pos"):
        # polarity="pos" / "neg"
        # An output BNC:
        # Value Output
        # 0 T0
        # 1 AB
        # 2 CD
        # 3 EF
        # 4 GH
        # convert the name to number
        chnls = ('T0', 'AB', 'CD', 'EF', 'GH')
        indx = chnls.index(bnc)
        # convert polarity to index
        polrt = ('neg', 'pos')
        polind = polrt.index(polarity)
        # examples: LPOL 1,0<CR> Configure the AB output as negative polarity.
        self.device.write(f"LPOL{indx},{polind}")
        print(f"Polarity of {bnc} set to {polarity}")
        return


    def get_error(self):
        err = self.device.query("LERR?")
        print(f"Last error of DG645: {err}")
        return err


    def set_trigger_level(self, val=0.3):
        self.device.write(f"TLVL{val}")
        print(f"Trigger level setted to {val} V")
        return


    def set_shutter_on_seq(self):
        # AB pulse for camera
        # set amplitude of AB to trigger the camera
        self.set_level_amplitude(bnc="AB", ampl=3.5)
        # set A to 0.099915 s and camerat Exp = 0.01 ms
        self.set_delay2channel(channel="A", delay=0.0999)
        # set B to 0.09998 s
        self.set_delay2channel(channel="B", delay=0.09998)
        # CD pulse to open the shutter for second probe (1 pump)
        # set delay C to 0 s
        self.set_delay2channel(channel="C", delay=0.0)
        # set D to 110 ms
        self.set_delay2channel(channel="D", delay=0.11)
        # set amplitude of CD to open shutter
        self.set_level_amplitude(bnc="CD", ampl=5)
        # set CD polarity to positive
        self.set_polatity(bnc="CD", polarity="pos")
        # set D to 110 ms
        # self.set_delay2channel(channel="D", delay=0.11)
        # set external single-shot trigger
        self.set_trigger_source(val=4)
        # set trigger level
        self.set_trigger_level(0.3)
        # set single-shot ready
        self.send_trigger()
        print("Shutter ON seq set")


    def set_shutter_off_seq(self):
        # AB pulse for camera
        # set A to 99 ms
        self.set_delay2channel(channel="A", delay=0.0999)
        # set B to +2 ms
        self.set_delay2channel(channel="B", delay=0.09998)
        # set amplitude of AB to trigger the camera
        self.set_level_amplitude(bnc="AB", ampl=3.5)
        # CD pulse to do not open the shutter for second probe (1 pump)
        # set delay C to 0 s
        self.set_delay2channel(channel="C", delay=0.0)
        # set D to 110 ms
        self.set_delay2channel(channel="D", delay=0.11)
        # set amplitude of CD to keep shutter closed
        self.set_level_amplitude(bnc="CD", ampl=0.5)
        # set CD polarity to positive
        self.set_polatity(bnc="CD", polarity="pos")
        # set external single-shot trigger
        self.set_trigger_source(val=4)
        # set trigger level
        self.set_trigger_level(0.3)
        # set single-shot ready
        self.send_trigger()
        print("Shutter OFF seq set")
        return


if __name__ == "__main__":
    dg = DelayGenerator(17)
    # dg.set_trigger_source(5)
    # dg.send_trigger()
    dg.set_shutter_off_seq()
    # dg.set_shutter_off_seq()
    dg.get_error()


