function status = Jena_init(COM_N)

%Load Assembly
asm1 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Protocols.dll');
asm2 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Ftd2xx.dll');
asm3 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Visa.dll');
asm4 = NET.addAssembly('D:\Pump-probe_setup\Matlab Control\Jena\piezojena-NV40Multi_Net_Framework_library\piezojena NV40Multi\Piezojena.Protocols.Nv40Multi.dll');

%call Constructor
service = Piezojena.Protocols.Nv40Multi.Nv40MultiServices;

try
    %Connect device
    nv40multi = service.ConnectNv40MultiToSerialPort(COM_N);
    
    %Set remote control
    nv40multi.SetRemoteControlled(0,true);
    nv40multi.SetRemoteControlled(1,true);
    nv40multi.SetRemoteControlled(2,true);
    %Close Port
    nv40multi.Dispose();
    status = true;
catch
    warning('PiezoJena is not initilized');
    status = false;
end
end