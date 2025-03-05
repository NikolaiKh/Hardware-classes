function Jena_setLoop (nv40multi,channel,loopQ)

%Use it
%loop = nv40multi.GetClosedLoopControlled(channel);
%nv40multi.SetRemoteControlled(channel,true);

if loopQ==true
    nv40multi.SetClosedLoopControlled(channel,true);
else
    nv40multi.SetClosedLoopControlled(channel,false);
end

end