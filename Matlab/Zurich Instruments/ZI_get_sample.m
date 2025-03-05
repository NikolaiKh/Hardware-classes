function [x,y] = ZI_get_sample(device_id, varargin)

% EXAMPLE_POLL Record demodulator data using ziDAQServer's synchronous poll function
%
% USAGE DATA = EXAMPLE_POLL(DEVICE_ID)
%
% Poll demodulator sample data from the device specified by DEVICE_ID using
% ziDAQServer's poll method. DEVICE_ID should be a string, e.g., 'dev2006' or
% 'uhf-dev2006'.
%
% ziDAQServer's poll method allows the user to obtain ('poll') demodulator
% data. Data can be obtained continuously in a loop. If asynchronous data
% recording is necessary please see example_record_async.m which uses the
% ziDAQRecord module.
%
% NOTE Additional configuration: Connect signal output 1 to signal input 1
% with a BNC cable.
%
% NOTE Please ensure that the ziDAQ folders 'Driver' and 'Utils' are in your
% Matlab path. To do this (temporarily) for one Matlab session please navigate
% to the ziDAQ base folder containing the 'Driver', 'Examples' and 'Utils'
% subfolders and run the Matlab function ziAddPath().
% >>> ziAddPath;
%
% Use either of the commands:
% >>> help ziDAQ
% >>> doc ziDAQ
% in the Matlab command window to obtain help on all available ziDAQ commands.
%
% Copyright 2008-2018 Zurich Instruments AG

clear ziDAQ;

if ~exist('device_id', 'var')
    error(['No value for device_id specified. The first argument to the ' ...
           'example should be the device ID on which to run the example, ' ...
           'e.g. ''dev2006'' or ''uhf-dev2006''.'])
end

% Check the ziDAQ MEX (DLL) and Utility functions can be found in Matlab's path.
if ~(exist('ziDAQ') == 3) && ~(exist('ziCreateAPISession', 'file') == 2)
    fprintf('Failed to either find the ziDAQ mex file or ziDevices() utility.\n')
    fprintf('Please configure your path using the ziDAQ function ziAddPath().\n')
    fprintf('This can be found in the API subfolder of your LabOne installation.\n');
    fprintf('On Windows this is typically:\n');
    fprintf('C:\\Program Files\\Zurich Instruments\\LabOne\\API\\MATLAB2012\\\n');
    return
end

% The API level supported by this example.
apilevel_example = 6;
% Create an API session; connect to the correct Data Server for the device.
[device, props] = ziCreateAPISession(device_id, apilevel_example);
ziApiServerVersionCheck();

branches = ziDAQ('listNodes', ['/' device ], 0);
if ~any(strcmp([branches], 'DEMODS'))
  sample = [];
  fprintf('\nThis example requires lock-in functionality which is not available on %s.\n', device);
  return
end

%% Define some other helper parameters.
demod_c = '0'; % Demod channel, 0-based indexing for paths on the device.
time_constant = 0.001; % [s]
demod_idx = str2double(demod_c) + 1; % 1-based indexing, to access the data.

% Unsubscribe all streaming data.
ziDAQ('unsubscribe', '*');

% Pause to get a settled lowpass filter.
%pause(10*time_constant);

% Perform a global synchronisation between the device and the data server:
% Ensure that the settings have taken effect on the device before issuing the
% ``poll`` command and clear the API's data buffers to remove any old
% data. Note: ``sync`` must be issued after waiting for the demodulator filter
% to settle above.
ziDAQ('sync');

% Subscribe to the demodulator sample.
ziDAQ('subscribe', ['/' device '/demods/' demod_c '/sample']);

% Poll data for poll_duration seconds.
poll_timeout = 100;
poll_duration = 0.1;
data = ziDAQ('poll', poll_duration, poll_timeout);

if ziCheckPathInData(data, ['/' device '/demods/' demod_c '/sample'])
    sample = data.(device).demods(demod_idx).sample;
else
    sample = [];
end

x=sample.x;
y=sample.y;

% Unsubscribe from all paths.
ziDAQ('unsubscribe', '*');

end