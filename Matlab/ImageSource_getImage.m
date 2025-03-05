function pic = ImageSource_getImage(varargin)
if ~isempty(varargin)
    Nframes = varargin{1};
else
    Nframes = 10;
end;
if length(varargin)>1
    Exp = varargin{2};
else
    Exp = 0.01;
end;
if length(varargin)>2
    Gain = varargin{3};
else
    Gain = 0;
end;
vid = videoinput('tisimaq_r2013_64', 1, 'Y16 (1216x1024) [Binning 2x]');
src = getselectedsource(vid);
vid.FramesPerTrigger = Nframes;
src.FrameRate = 150;
src.ExposureAuto = 'Off';
src.Exposure = Exp;
src.ToneMapping = 'Disable';
src.ToneMappingAuto = 'Off';
src.Gain = Gain;
src.GainAuto = 'Off';
src.Denoise = 0;
get(src);
% inspect(vid);
% imaqhelp(vid);
tic
start(vid);
while vid.FramesAcquired < Nframes
    pause(0.01);
end;
vv = getdata(vid);
stop(vid);
delete(vid);
toc
data = squeeze(vv);
pic = mean(data,3);
surf(pic, 'linestyle', 'none');
colorbar;
view(0, -90);
end