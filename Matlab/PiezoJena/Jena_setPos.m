function Jena_setPos(nv40multi,channel,loopQ,position)
%Use it
%loop = nv40multi.GetClosedLoopControlled(channel);
%nv40multi.SetRemoteControlled(channel,true);
if loopQ==true
    %nv40multi.SetClosedLoopControlled(channel,true);
    nv40multi.SetDesiredOutput(channel,position);  % if (loop) 10 µm else 10 Volt
else
    %nv40multi.SetClosedLoopControlled(channel,false);
    nv40multi.SetDesiredOutput(channel,15*position/8 - 20);  % if (loop) 10 µm else 10 Volt
    %nv40multi.SetClosedLoopControlled(channel,false);
end

end