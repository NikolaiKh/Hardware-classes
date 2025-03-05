# Hardware classes
 Last version of Python and Matlab classes for different devices I used in the lab. Other projects (e.g. pump-probe-gui) could use old versions. I used a few basic functions only. Thus, if you need full-functionality, you can update classes based on hardware manuals, or check, for expample, [pymeasure](https://pymeasure.readthedocs.io/en/latest/index.html). It contains a lot of ready-to-use python implementations of a number of devices.

## List of supported hardware:
### Python:
- Stanford Research Lock-in amplifier SR830 / SR844. Based on [PyVISA](https://pyvisa.readthedocs.io/en/latest/#)
- NewPort XPS controller
- Physics Instrument (PI) motion controller. Bases 
- pycromanager class -- to use cameras with [MicroManager](https://micro-manager.org/). Based on [pycromanager](https://pycro-manager.readthedocs.io/en/latest/index.html). Tested with Teledyne Reriga R3, Teledyne CollSnap HQ, Hamamatsu Quest, pco.2000, Teledyne Kinetix22, Hamamatsu ORCA-Fusion BT, Andor Sona
- Stanford Research delay generator DG645. Based on [PyVISA](https://pyvisa.readthedocs.io/en/latest/#)
- Thorlabs Kinetix motion control. Tested with linear stages DDS600/M and DDS220/M. Based on [PyLabLib](https://pylablib.readthedocs.io/en/latest/)
- Zurich Instruments Lock-in amplifier MFLI
