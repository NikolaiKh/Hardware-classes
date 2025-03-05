function [x, y] = ZI_getXY(device, poll_duration)

% Unsubscribe all streaming data.
ziDAQ('unsubscribe', '*');

% Perform a global synchronisation between the device and the data server:
% Ensure that the settings have taken effect on the device before issuing the
% ``poll`` command and clear the API's data buffers to remove any old
% data. Note: ``sync`` must be issued after waiting for the demodulator filter
% to settle above.
ziDAQ('sync');

%% Define some other helper parameters.
demod_c = '0'; % Demod channel, 0-based indexing for paths on the device.
% time_constant = 0.001; % [s]
demod_idx = str2double(demod_c) + 1; % 1-based indexing, to access the data.
% Subscribe to the demodulator sample.
ziDAQ('subscribe', ['/' device '/demods/' demod_c '/sample']);

% Poll data for poll_duration seconds.
poll_timeout = 10;
%poll_duration = 0.1;
data = ziDAQ('poll', poll_duration, poll_timeout);

if ziCheckPathInData(data, ['/' device '/demods/' demod_c '/sample'])
    sample = data.(device).demods(demod_idx).sample;
else
    sample = [];
end

x=mean(sample.x);
y=mean(sample.y);

% Unsubscribe from all paths.
ziDAQ('unsubscribe', '*');

end