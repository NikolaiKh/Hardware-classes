function [device, props] = ZI_init(device_id, varargin)

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

end