function Jena_setPos_OpenClosePort (channel,loop,position)
asm1 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Protocols.dll');
asm2 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Ftd2xx.dll');
asm3 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Visa.dll');
asm4 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Protocols.Nv40Multi.dll');

%call Constructor
service = Piezojena.Protocols.Nv40Multi.Nv40MultiServices;

%Connect device
nv40multi = service.ConnectNv40MultiToSerialPort('COM4');

nv40multi.SetRemoteControlled(channel,true);
nv40multi.SetClosedLoopControlled(channel,loop);
if loop
    nv40multi.SetDesiredOutput(channel,position);  % if (loop) 10 µm else 10 Volt
else
    nv40multi.SetDesiredOutput(channel,15*position/8 - 20);  % if (loop) 10 µm else 10 Volt
    %nv40multi.SetClosedLoopControlled(channel,false);
end
%Close Port
nv40multi.Dispose();
end