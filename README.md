# Hardware classes
 Last version of Python and Matlab classes for different devices I used in the lab. Other projects (e.g. pump-probe-gui) could use old versions. I used a few basic functions only. Thus, if you need full-functionality, you can update classes based on hardware manuals, or check, for expample, [pymeasure](https://pymeasure.readthedocs.io/en/latest/index.html). It contains a lot of ready-to-use python implementations of a number of devices.

Every class file contains "__main__" function for testing the device communication.

## List of supported hardware:
### Python
- Stanford Research Lock-in amplifier SR830 / SR844. Based on [PyVISA](https://pyvisa.readthedocs.io/en/latest/#)
- NewPort XPS controller
- Lakeshore 340 temperature controller. Based on [PyVISA](https://pyvisa.readthedocs.io/en/latest/#) and [RickyZiegahn github]([RickyZiegahn/Lakeshore-Cryostat-Controller](https://github.com/RickyZiegahn/Lakeshore-Cryostat-Controller). Should work with models 330, 336, 340. But I tested it with 340 only
- Physics Instrument (PI) motion controller. Based on [pipython](https://pipython.physikinstrumente.com/)
- pycromanager class -- to use cameras with [MicroManager](https://micro-manager.org/). Based on [pycromanager](https://pycro-manager.readthedocs.io/en/latest/index.html). Tested with Teledyne Reriga R3, Teledyne CollSnap HQ, Hamamatsu Quest, pco.2000, Teledyne Kinetix22, Hamamatsu ORCA-Fusion BT, Andor Sona
- Stanford Research delay generator DG645. Based on [PyVISA](https://pyvisa.readthedocs.io/en/latest/#)
- [Thorlabs](https://www.thorlabs.de/) Kinetix motion control. Based on [PyLabLib](https://pylablib.readthedocs.io/en/latest/). Tested with linear stages DDS600/M and DDS220/M
- [Zurich Instruments](https://www.zhinst.com/) Lock-in amplifier MFLI

### Matlab
- [Thorlabs](https://www.thorlabs.de/) camera
- [ImageSource](https://www.theimagingsource.com/en-us/) camera
- [Piezosystem Jena](https://www.piezosystem.com/)
- (APT Software Thorlabs](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9019) for translation stages
- [Standa](https://www.standa.lt/) motion control. Based on [XIMC software](https://files.xisupport.com/Software.en.html)
- [Zurich Instruments](https://www.zhinst.com/) lock-in amplifier. Tested with MFLI and HF2LI
