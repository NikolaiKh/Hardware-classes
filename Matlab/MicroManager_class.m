classdef MicroManager_class
    properties
        camera
        mmc % MoicroManager core      
        width
        height
    end

    methods
        function obj = MicroManager_class(varargin)
            %____Instructions_____
            %connect to micromanager
            %first install PV cam including PV cam test, see if its finds
            %the camera, then install micro manager and see if it finds the
            %camera, then follow instructions on 
            % https://micro-manager.org/Matlab_Configuration to connect to matalb
            %to micromanager, when trying to change classpath and
            %librarypath.txt you will encounter an acess denied error,
            %close matlab, open programme files/MATLAB/R2023a (your matlab
            %version)/toolbox/local and replace the files manually with the
            %modified ones. 
            config_file = 'C:\Program Files\Micro-Manager-2.0\MMConfig_demo.cfg';
%             config_file(1:nargin) = varargin;
            import mmcorej.*; 
            app.mmc = CMMCore; 
            app.mmc.unloadAllDevices();
            app.mmc.loadSystemConfiguration(config_file);
            disp('Camera is loaded');
        end

        function img = getImage(app)
        %________ protocol from https://micro-manager.org/Matlab_Configuration
            app.mmc.snapImage();
            img = app.mmc.getImage(); % returned as a 1D array of signed integers in row-major order
            app.width = app.mmc.getImageWidth(); 
            app.height = app.mmc.getImageHeight(); 
            pixelType = app.getPixelType();
            img = typecast(img, pixelType);
            img = reshape(img, [app.width, app.height]); % image should be interpreted as a 2D array
            img = transpose(img);                % make column-major order for MATLAB
        end

        function pixelType = getPixelType(app)
            if app.mmc.getBytesPerPixel == 2
                pixelType = 'uint16';
            else
                pixelType = 'uint8';
            end
        end

        function result = getExptime(app)
            result = app.mmc.getExposure();
        end

        function result = setExptime(app, time)
            result = app.mmc.setExposure(time);
        end

        function result = getBinning(app)
            result = app.mmc.getProperty("Camera", "Binning");
        end

        function setBinning(app, binning)
            app.mmc.setProperty("Camera", "Binning", binning);
        end

        function result = getAllBinningvalues(app)
            result =  app.mmc.getAllowedPropertyValues("Camera", "Binning");
        end

    end
end