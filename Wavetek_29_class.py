# made by Nikolai Khokhlov
# version: 2026.11.10.1

import time
from datetime import datetime
import pyvisa
import re


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Wave generator [{timestamp}]: {message}")


class WaveGenerator:
    """Control class for the Wavetek Model 29 DDS Function Generator."""

    def __init__(self, gpibport):
        rm = pyvisa.ResourceManager()

        if isinstance(gpibport, int):
            self.device = rm.open_resource(f"GPIB0::{gpibport}::INSTR")
        elif isinstance(gpibport, str):
            self.device = rm.open_resource(gpibport)
        else:
            self.state = "NOT connected!"
            log(self.state)
            return

        self.device.timeout = 5000
        self.device.write_termination = "\n"
        self.device.read_termination = "\n"

        self.name = self.device.query("*IDN?").strip()
        self.model = 29
        self.state = f"Wavetek Model {self.model} connected: {self.name}"
        log(self.state)

        self.minimum_voltage = 0.0025
        self.maximum_voltage = 10.0
        # Read actual physical settings from the Wavetek.
        self.target_voltage = self.get_voltage()
        self.output_state = self.get_output_state()

        print(
            f"Wavetek initial state: "
            f"MAIN OUT = {'ON' if self.output_state else 'OFF'}, "
            f"voltage = {self.target_voltage:g} Vpp"
        )


    def close(self):
        self.device.close()
        self.state = "Wavetek Model 29 disconnected"
        log(self.state)
        return

    def reset(self):
        """Reset the generator to the factory default settings."""
        self.device.write("*RST")
        print("Wavetek Model 29 reset to defaults")
        return

    def set_sine(self):
        """Select the sine waveform."""
        self.device.write("SINE")
        print("Wavetek waveform set to sine")
        return

    def get_output_state(self):
        """
        Read the physical MAIN OUT state from the Wavetek *LRN? response.

        Returns
        -------
        bool
            True  -> MAIN OUT ON
            False -> MAIN OUT OFF
        """

        response = self.device.query("*LRN?").strip()

        if not response.startswith("LRN #H"):
            raise RuntimeError(
                f"Unexpected *LRN? response: {response[:30]}"
            )

        # The first state word changes reproducibly with MAIN OUT:
        #
        # OFF: 000020812...
        # ON : 0000A081A...
        #
        state_word = response[6:15]

        if state_word.startswith("0000A081A"):
            return True

        if state_word.startswith("000020812"):
            return False

        raise RuntimeError(
            f"Unknown Wavetek MAIN OUT state: {state_word}"
        )


    def set_output(self, state=True, ramp_time=1.0, steps=20):
        """
        Enable or disable MAIN OUT with a smooth voltage ramp.

        ON:
            1. Set amplitude to minimum.
            2. Enable MAIN OUT.
            3. Ramp to self.target_voltage.

        OFF:
            1. Ramp from self.target_voltage to minimum.
            2. Disable MAIN OUT.

        The OFF ramp is always performed because the physical output
        may have been enabled manually from the front panel.
        """

        if not isinstance(state, bool):
            raise TypeError("state must be True or False")

        ramp_time = float(ramp_time)
        steps = int(steps)

        if ramp_time < 0:
            raise ValueError("ramp_time cannot be negative")

        if steps < 1:
            raise ValueError("steps must be at least 1")

        if state:

            if self.target_voltage is None:
                raise RuntimeError(
                    "Output voltage is unknown. "
                    "Use set_voltage() before enabling MAIN OUT."
                )

            # Start from minimum amplitude.
            self.device.write(
                f"PDPP {self.minimum_voltage:.12g}"
            )

            # Enable MAIN OUT at minimum amplitude.
            self.device.write("OUTPUT ON")
            self.output_state = True

            try:
                self._ramp_voltage(
                    start_voltage=self.minimum_voltage,
                    stop_voltage=self.target_voltage,
                    ramp_time=ramp_time,
                    steps=steps
                )

            except Exception:
                self.device.write("OUTPUT OFF")
                self.output_state = False
                raise

            print(
                f"Wavetek output set to ON at "
                f"{self.target_voltage:g} Vpp"
            )


        else:

            # Read actual physical MAIN OUT state.
            self.output_state = self.get_output_state()

            # If MAIN OUT is already OFF, there is nothing to ramp.
            if not self.output_state:
                print("Wavetek output is already OFF")
                return

            # MAIN OUT is physically ON.
            # Read the actual physical voltage before starting the ramp.
            current_voltage = self.get_voltage()

            # Check that the starting voltage is valid.
            self._validate_voltage(current_voltage)

            # Remember this voltage so that it can be restored
            # the next time MAIN OUT is switched ON.
            self.target_voltage = current_voltage

            # Ramp physical voltage to minimum.
            self._ramp_voltage(
                start_voltage=current_voltage,
                stop_voltage=self.minimum_voltage,
                ramp_time=ramp_time,
                steps=steps
            )

            # Switch MAIN OUT OFF only after the ramp is complete.
            self.device.write("OUTPUT OFF")
            self.output_state = False

            print(
                f"Wavetek output set to OFF; "
                f"stored voltage is {self.target_voltage:g} Vpp"
            )

        return


    def output_on(self, ramp_time=1.0, steps=20):
        """Enable MAIN OUT and ramp to the stored voltage."""

        self.set_output(
            state=True,
            ramp_time=ramp_time,
            steps=steps
        )

        return

    def output_off(self, ramp_time=1.0, steps=20):
        """Ramp to minimum voltage and disable MAIN OUT."""

        self.set_output(
            state=False,
            ramp_time=ramp_time,
            steps=steps
        )

        return

    def ramp_to_voltage(self, voltage, ramp_time=1.0, steps=20):
        """
        Smoothly change from the stored voltage to a new voltage.

        If MAIN OUT is off, only program and store the requested voltage.
        """

        voltage = float(voltage)

        if not self.minimum_voltage <= voltage <= self.maximum_voltage:
            raise ValueError(
                f"voltage must be between "
                f"{self.minimum_voltage:g} and "
                f"{self.maximum_voltage:g} Vpp"
            )

        old_voltage = self.target_voltage

        if self.output_state:
            self._ramp_voltage(
                start_voltage=old_voltage,
                stop_voltage=voltage,
                ramp_time=ramp_time,
                steps=steps
            )
        else:
            self.device.write(f"PDPP {voltage:.12g}")

        self.target_voltage = voltage

        print(
            f"Wavetek voltage changed from "
            f"{old_voltage:g} to {voltage:g} Vpp"
        )

        return

    def _validate_voltage(self, voltage):
        """
        Validate PDPP voltage into a matched load.
        """

        voltage = float(voltage)

        if not self.minimum_voltage <= voltage <= self.maximum_voltage:
            raise ValueError(
                f"voltage must be between "
                f"{self.minimum_voltage:g} and "
                f"{self.maximum_voltage:g} Vpp"
            )

        return


    def _ramp_voltage(
            self,
            start_voltage,
            stop_voltage,
            ramp_time=1.0,
            steps=20):
        """
        Ramp physical amplitude using PDPP.

        This method does not change self.target_voltage.
        """

        start_voltage = float(start_voltage)
        stop_voltage = float(stop_voltage)
        ramp_time = float(ramp_time)
        steps = int(steps)

        self._validate_voltage(start_voltage)
        self._validate_voltage(stop_voltage)

        if ramp_time < 0:
            raise ValueError("ramp_time cannot be negative")

        if steps < 1:
            raise ValueError("steps must be at least 1")

        if ramp_time == 0 or steps == 1:
            self.device.write(
                f"PDPP {stop_voltage:.12g}"
            )
            return

        # There are steps - 1 intervals between steps.
        delay = ramp_time / (steps - 1)

        for step in range(steps):
            fraction = step / (steps - 1)

            voltage = (
                    start_voltage
                    + fraction * (stop_voltage - start_voltage)
            )

            voltage = min(
                max(voltage, self.minimum_voltage),
                self.maximum_voltage
            )

            self.device.write(f"PDPP {voltage:.12g}")

            if step < steps - 1:
                time.sleep(delay)

        # Explicitly set the exact final amplitude.
        self.device.write(f"PDPP {stop_voltage:.12g}")

        return


    def set_frequency(self, frequency=1000.0):
        """
        Set the main-generator frequency in Hz.

        For a sine wave, the Model 29 range is 100 uHz to 10 MHz.
        """
        frequency = float(frequency)
        if not 100e-6 <= frequency <= 10e6:
            raise ValueError("Sine frequency must be between 100e-6 and 10e6 Hz")

        self.device.write(f"FREQ {frequency:.12g}")
        print(f"Wavetek frequency set to {frequency:g} Hz")
        return

    def set_phase(self, phase=0.0):
        """
        Set the sine/burst start-stop phase in degrees.

        The instrument accepts signed phase values. The setting also defines
        the phase relationship between MAIN OUT and AUX OUT.
        """
        phase = float(phase)
        if not -360.0 <= phase <= 360.0:
            raise ValueError("phase must be between -360 and +360 degrees")

        self.device.write(f"PHASE {phase:.12g}")
        print(f"Wavetek phase set to {phase:g} degrees")
        return

    def set_voltage(self, voltage=1.0):
        """
        Set and remember the output amplitude in Vpp into a matched load.
        """

        voltage = float(voltage)

        self._validate_voltage(voltage)

        self.device.write(f"PDPP {voltage:.12g}")

        self.target_voltage = voltage

        print(
            f"Wavetek output voltage set to "
            f"{voltage:g} Vpp"
        )

        return

    def get_voltage(self):
        """
        Read the currently programmed PDPP voltage from the Wavetek.

        Returns
        -------
        float
            MAIN output amplitude in Vpp into a matched load.
        """

        response = self.device.query("*LRN?").strip()

        if not response.startswith("LRN #H"):
            raise RuntimeError(
                f"Unexpected *LRN? response: {response[:30]}"
            )

        hex_data = response[6:]

        try:
            data = bytes.fromhex(hex_data)
        except ValueError as exc:
            raise RuntimeError(
                "Could not decode Wavetek *LRN? response"
            ) from exc

        # In the observed Model 29 LRN block, the MAIN amplitude
        # display field starts around byte 59.
        #
        # Examples:
        #     +50.0mV
        #     +100.0mV
        #     +1.000 V
        #
        amplitude_field = data[55:75]

        match = re.search(
            rb'([+-]?\d+(?:\.\d+)?)\s*(uV|mV|V)',
            amplitude_field
        )

        if match is None:
            raise RuntimeError(
                "Could not decode MAIN output voltage. "
                f"Amplitude field: {amplitude_field!r}"
            )

        value = float(match.group(1))
        unit = match.group(2).decode("ascii")

        if unit == "uV":
            value /= 1_000_000.0
        elif unit == "mV":
            value /= 1000.0
        elif unit == "V":
            pass
        else:
            raise RuntimeError(
                f"Unknown voltage unit in *LRN? response: {unit}"
            )

        return value


    def get_all_trigger_sources(self):
        return ("External", "Manual/Remote", "Internal trigger generator")

    def set_trigger_source(self, source="EXT"):
        """
        Set the triggered-burst source.

        source:
            'EXT'  - rising edge at EXT TRIG
            'MAN'  - front-panel MAN/SYNC key or remote *TRG command
            'TGEN' - internal trigger generator
        """
        source = str(source).upper()
        allowed = {
            "EXT": "External",
            "MAN": "Manual/Remote",
            "TGEN": "Internal trigger generator",
        }
        if source not in allowed:
            raise ValueError("source must be 'EXT', 'MAN', or 'TGEN'")

        self.device.write(f"TRIGSRC {source}")
        print(f"Wavetek trigger source: {allowed[source]}")
        return

    def set_internal_trigger_period(self, period=1e-3):
        """
        Set the internal trigger-generator period in seconds.

        Valid range: 20 us to 200 s, corresponding to 50 kHz to 5 mHz.
        """
        period = float(period)
        if not 20e-6 <= period <= 200.0:
            raise ValueError("trigger period must be between 20e-6 and 200 s")

        self.device.write(f"TGEN {period:.12g}")
        print(f"Wavetek internal trigger period set to {period:g} s")
        return

    def set_burst_count(self, cycles=1):
        """
        Set the number of cycles in each triggered burst.

        The Model 29 permits integer counts from 1 to 1023. It also permits
        half-cycle counts from 0.5 to 511.5.
        """
        cycles = float(cycles)
        is_integer = cycles.is_integer()
        is_half_step = (cycles * 2).is_integer()

        valid_integer = is_integer and 1 <= cycles <= 1023
        valid_half_cycle = is_half_step and 0.5 <= cycles <= 511.5

        if not (valid_integer or valid_half_cycle):
            raise ValueError(
                "cycles must be an integer from 1 to 1023, or a 0.5-cycle "
                "increment from 0.5 to 511.5"
            )

        cycles_text = str(int(cycles)) if is_integer else f"{cycles:.1f}"
        self.device.write(f"BCNT {cycles_text}")
        print(f"Wavetek burst count set to {cycles_text} cycles")
        return

    def set_burst(self, cycles=1, phase=0.0, source="EXT", trigger_period=None):
        """Configure and enable triggered-burst mode."""
        self.set_sine()
        self.set_burst_count(cycles)
        self.set_phase(phase)
        self.set_trigger_source(source)

        if str(source).upper() == "TGEN":
            if trigger_period is None:
                trigger_period = 1e-3
            self.set_internal_trigger_period(trigger_period)

        self.device.write("TRIG ON")
        print("Wavetek triggered-burst mode ON")
        return

    def set_continuous(self):
        """Disable triggered-burst mode and return to continuous output."""
        self.device.write("TRIG OFF")
        print("Wavetek continuous mode ON")
        return

    def send_trigger(self):
        """Send a remote trigger. TRIGSRC MAN must be selected first."""
        self.device.write("*TRG")
        print("Trigger sent to Wavetek Model 29")
        return

    def get_error(self):
        """Read and clear the execution error register. Zero means no error."""
        err = self.device.query("EER?").strip()
        print(f"Last execution error of Wavetek Model 29: {err}")
        return err

    def wait_for_voltage(
        self,
        target_voltage=None,
        tolerance=0.01,
        timeout=5.0,
        poll_interval=0.05,
        settle_time=0.2):
        """
        Wait until the physical programmed voltage reaches the target.

        Parameters
        ----------
        target_voltage : float or None
            Target voltage in Vpp. If None, self.target_voltage is used.

        tolerance : float
            Maximum allowed absolute difference in Vpp.

        timeout : float
            Maximum waiting time in seconds.

        poll_interval : float
            Delay between voltage queries in seconds.

        settle_time : float
            Additional delay after reaching the target.

        Returns
        -------
        float
            Last voltage read from the Wavetek.
        """

        if target_voltage is None:
            target_voltage = self.target_voltage

        if target_voltage is None:
            raise RuntimeError(
                "Target voltage is unknown. "
                "Use set_voltage() before wait_for_voltage()."
            )

        target_voltage = float(target_voltage)
        tolerance = float(tolerance)
        timeout = float(timeout)
        poll_interval = float(poll_interval)
        settle_time = float(settle_time)

        self._validate_voltage(target_voltage)

        if tolerance <= 0:
            raise ValueError("tolerance must be positive")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")

        if settle_time < 0:
            raise ValueError("settle_time cannot be negative")

        start_time = time.monotonic()
        last_voltage = None

        while time.monotonic() - start_time < timeout:

            last_voltage = self.get_voltage()

            if abs(last_voltage - target_voltage) <= tolerance:

                if settle_time > 0:
                    time.sleep(settle_time)

                print(
                    f"Wavetek voltage reached "
                    f"{last_voltage:g} Vpp"
                )

                return last_voltage

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Wavetek did not reach {target_voltage:g} Vpp "
            f"within {timeout:g} s. "
            f"Last reported voltage: {last_voltage!r} Vpp"
        )


if __name__ == "__main__":
    # Integer address and full VISA address are both supported:
    wg = WaveGenerator(3)
    # wg = WaveGenerator("GPIB0::3::INSTR")

    # wg.set_sine()
    # wg.set_frequency(4001)
    # wg.set_output(True)
    # print(wg.get_voltage())
    wg.set_output(False)
    # time.sleep(0.5)

    wg.set_voltage(4)
    wg.set_burst(cycles=4, phase=40, source="EXT")

    time.sleep(0.5)
    # wg.set_output(True)
    # wg.send_trigger()

    # wg.device.write("OUTPUT OFF")
    # time.sleep(0.5)
    #
    # print(wg.get_output_state())

    # setup = wg.device.query("*LRN?")
    # print(type(setup))
    # print(len(setup))
    # print(repr(setup))
    #
    # time.sleep(0.5)
    # wg.set_voltage(0.05)
    # setup2 = wg.device.query("*LRN?")
    # print(type(setup2))
    # print(len(setup2))
    # print(repr(setup2))

    # print("Execution error:", wg.get_error())
    wg.close()
