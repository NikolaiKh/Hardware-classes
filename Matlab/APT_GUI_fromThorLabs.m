clear; close all; clc;
global h delayStart; % make h a global variable so it can be used outside the main
          % function. Useful when you do event handling and sequential           move
%% Create Matlab Figure Container
% fpos    = get(0,'DefaultFigurePosition'); % figure default position
% fpos(1) = 50; % figure position X
% fpos(2) = 50; % figure position Y
% fpos(3) = 1200; % figure window size;Width
% fpos(4) = 900; % Height
 
% f = figure('Position', fpos,...           
%            'Name','APT GUI');
f = open('GUI_start_test.fig');       
%% Create ActiveX Controller
h = actxcontrol('MGMOTOR.MGMotorCtrl.1',[20 20 300 200], f);
 
%% Initialize
% Start Control
h.StartCtrl;
 
% Set the Serial Number
SN = 94864141; % put in the serial number of the hardware
set(h,'HWSerialNum', SN);
 
% Indentify the device
h.Identify;
 
pause(5); % waiting for the GUI to load up;
%% Controlling the Hardware
%h.MoveHome(0,0); % Home the stage. First 0 is the channel ID (channel 1)
                 % second 0 is to move immediately
%% Event Handling
h.registerevent({'MoveComplete' 'MoveCompleteHandler'});
 
% %% Sending Moving Commands
% timeout = 10; % timeout for waiting the move to be completed
% %h.MoveJog(0,1); % Jog
%  
% % Move a absolute distance
% h.SetAbsMovePos(0,7);
% h.MoveAbsolute(0,1==0);
%  
% t1 = clock; % current time
% while(etime(clock,t1)<timeout) 
% % wait while the motor is active; timeout to avoid dead loop
%     s = h.GetStatusBits_Bits(0);
%     if (IsMoving(s) == 0)
%       pause(2); % pause 2 seconds;
%       h.MoveHome(0,0);
%       disp('Home Started!');
%       break;
%     end
% end
