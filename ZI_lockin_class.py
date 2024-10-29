import time
import numpy as np
import zhinst.utils
from zhinst.core import ziListEnum

class Lockin:
    def __init__(self):
        self.device_id = "dev5041"  # Device serial number available on its rear panel.
        server_host = "localhost"
        server_port = 8004
        api_level = 6  # Maximum API level supported for all instruments except HF2LI.

        (self.daq, self.device, _) = zhinst.utils.create_api_session(
            self.device_id, api_level, server_host=server_host, server_port=server_port
        )

        zhinst.utils.api_server_version_check(self.daq)
        self.daq.set(f"/{self.device}/demods/0/enable", 1)
        # get X Y R signals from demod0
        # The list of signal paths that we would like to record in the module.
        demod_path = f"/{self.device}/demods/0/sample"
        self.signal_paths = []
        self.signal_paths.append(demod_path + ".x")  # The demodulator X output.
        self.signal_paths.append(demod_path + ".y")  # The demodulator Y output.
        self.signal_paths.append(demod_path + ".r")  # The demodulator R output.
        # It's also possible to add signals from other node paths:
        # signal_paths.append('/%s/demods/1/sample.r' % (device))

        # Check the device has demodulators.
        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = self.daq.listNodes(f"/{self.device}", flags)
        if demod_path not in (node.lower() for node in streaming_nodes):
            print(
                f"Device {self.device} does not have demodulators. Please modify the example to specify",
                "a valid signal_path based on one or more of the following streaming nodes: ",
                "\n".join(streaming_nodes),
            )
            raise Exception(
                "Demodulator streaming nodes unavailable - see the message above for more information."
            )

        # Defined the total time we would like to record data for and its sampling rate.
        # total_duration: Time in seconds: This examples stores all the acquired data in the `data`
        # dict - remove this continuous storing in read_data_update_plot before increasing the size
        # of total_duration!
        time_c = self.get_time_constant()
        total_duration = time_c
        module_sampling_rate = 30000  # Number of points/second
        burst_duration = time_c  # Time in seconds for each data burst/segment.
        num_cols = int(np.ceil(module_sampling_rate * burst_duration))
        num_bursts = int(np.ceil(total_duration / burst_duration))

        # Create an instance of the Data Acquisition Module.
        self.daq_module = self.daq.dataAcquisitionModule()

        # Configure the Data Acquisition Module.
        # Set the device that will be used for the trigger - this parameter must be set.
        self.daq_module.set("device", self.device)

        # Specify continuous acquisition (type=0).
        self.daq_module.set("type", 0)

        # 'grid/mode' - Specify the interpolation method of
        #   the returned data samples.
        #
        # 1 = Nearest. If the interval between samples on the grid does not match
        #     the interval between samples sent from the device exactly, the nearest
        #     sample (in time) is taken.
        #
        # 2 = Linear interpolation. If the interval between samples on the grid does
        #     not match the interval between samples sent from the device exactly,
        #     linear interpolation is performed between the two neighbouring
        #     samples.
        #
        # 4 = Exact. The subscribed signal with the highest sampling rate (as sent
        #     from the device) defines the interval between samples on the DAQ
        #     Module's grid. If multiple signals are subscribed, these are
        #     interpolated onto the grid (defined by the signal with the highest
        #     rate, "highest_rate"). In this mode, duration is
        #     read-only and is defined as num_cols/highest_rate.
        self.daq_module.set("grid/mode", 2)
        # 'count' - Specify the number of bursts of data the
        #   module should return (if endless=0). The
        #   total duration of data returned by the module will be
        #   count*duration.
        self.daq_module.set("count", num_bursts)
        # 'duration' - Burst duration in seconds.
        #   If the data is interpolated linearly or using nearest neighbout, specify
        #   the duration of each burst of data that is returned by the DAQ Module.
        self.daq_module.set("duration", burst_duration)
        # 'grid/cols' - The number of points within each duration.
        #   This parameter specifies the number of points to return within each
        #   burst (duration seconds worth of data) that is
        #   returned by the DAQ Module.
        self.daq_module.set("grid/cols", num_cols)

        # A dictionary to store all the acquired data.
        for signal_path in self.signal_paths:
            print("Subscribing to ", signal_path)
            self.daq_module.subscribe(signal_path)

        """
        Read the acquired data out from the module. Raise an
        AssertionError if no data is returned.
        """
        # Start recording data.
        self.daq_module.execute()
        time.sleep(1) #wait for some data to be equared

    def getXYR(self):
        data_read = self.daq_module.read(True)
        returned_signal_paths = [
            signal_path.lower() for signal_path in data_read.keys()
        ]

        signal = []
        # Loop over all the subscribed signals:
        for ind, signal_path in enumerate(self.signal_paths):
            if signal_path.lower() in returned_signal_paths:
                # Loop over all the bursts for the subscribed signal. More than
                # one burst may be returned at a time, in particular if we call
                # read() less frequently than the burst_duration.
                for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                    value = signal_burst["value"][0, :]

            else:
                # Note: If we read before the next burst has finished, there may be no new data.
                # No action required.
                pass
            signal.append(np.mean(value))

        return [signal[0], signal[1], signal[2]]


    def get_time_constant(self):
        return self.daq.getDouble(f"/{self.device}/demods/0/timeconstant")


if __name__ == "__main__":
    lia = Lockin()
    print(lia.getXYR())
    print(lia.get_time_constant())
