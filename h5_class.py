import h5py
from datetime import datetime
import time
import sys
import os
import numpy as np


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}  {message}')


class H5Loader():
    def __init__(self, datapath, date, user):
        # Initializes the folder (YEAR\\mm\\dd-User) from which data is read
        Y = date['Y']
        m = date['m']
        d = date['d']
        self.folderpath = f'{datapath}{Y}\\{m}\\{d}-{user}'

    def load_data(self, foldername, filename):
        # This function loads all h5 groups and datasets into one dictionary
        self.datapath = f'{self.folderpath}\\{foldername}'
        self.filename = filename + '.h5'
        data_dict = {}
        with h5py.File(os.path.join(self.datapath, self.filename), 'r') as file:
            for group_name, group in file.items():
                dummy = {}
                for dataset_name, dataset in group.items():
                    dummy[dataset_name] = dataset[()]
                data_dict[group_name] = dummy
        self.data_dict = data_dict

    def process_camera(self):
        data = self.data_dict['Data']
        scan_param = self.data_dict['Scan']
        static_param = self.data_dict['Static']
        det_param = self.data_dict['Detector']
        height = det_param['Det0_Height']
        width = det_param['Det0_Width']
        DS = {}
        dat = data['data']
        axes = data['axes']
        rl = data['rangelim']
        img = []
        for i in range(dat.shape[0]):
            img_dummy = dat[i, :]
            img_dummy = np.reshape(img_dummy, newshape=[height, width])
            img.append(img_dummy)
        img = np.array(img)
        DS['image'] = img
        i = 0
        for key in enumerate(scan_param):
            keystr = 'ax' + str(i)
            DS[keystr] = np.reshape(axes[:, i], rl)
            i = i + 1
        self.dataset = DS
        self.param = scan_param
        self.static = static_param
        self.detector = det_param
        return (DS, scan_param, static_param, det_param)


class H5File2Save:
    def __init__(self, folderpath, filename, user):
        self.date = None
        self.folderpath = folderpath
        self.filename = filename
        self.user = user

    def save_scan(self, axes_list, data_list):
        # get time of saving
        now = datetime.now()
        Y = now.strftime('%Y')
        m = now.strftime('%m')
        d = now.strftime('%d')
        H = now.strftime('%H')
        M = now.strftime('%M')
        date = f'{Y}-{m}-{d}, {H}:{M}'
        self.date = date
        # turn data into numpy array 
        axes_save = np.array(axes_list)
        data_save = np.array(data_list)

        # check if folder exists and create folder
        if not os.path.exists(self.folderpath):
            os.makedirs(self.folderpath)

        # check if filename exists and create filename
        if os.path.exists(os.path.join(self.folderpath, self.filename + '.h5')):
            self.log(f'The file {self.filename} exists. Redefining filename as {self.filename}_new.h5')
            self.filename = self.filename + '_new'
        filename = f'{self.filename}.h5'
        self.currentfile = filename

        with h5py.File(os.path.join(self.folderpath, filename), 'w') as file:
            # Save data
            group = file.create_group('Data')
            group.create_dataset('axes', data=axes_save, maxshape=(None, axes_save.shape[1]), chunks=True)
            group.create_dataset('data', data=data_save, maxshape=(None, data_save.shape[1]), chunks=True)
            # group.create_dataset('rangelim', data=self.range_lim)
            # Save scan parameters
            # group2 = file.create_group('Scan')
            # for i in range(len(self.device)):
            #     group2.create_dataset(self.type[str(i)], data=f'{self.val[str(i)]} ({self.unit[str(i)]})')
            # # Save static parameters
            # group3 = file.create_group('Static')
            # group3.create_dataset('datetime', data=date)
            # for i in range(len(self.static)):
            #     instr = self.static[str(i)]
            #     getparam = getattr(instr, instr.method_get)
            #     param = getparam()
            #     group3.create_dataset(instr.type, data=param)
            # # Save detector parameters
            # group4 = file.create_group('Detector')
            # for i in range(len(self.detector)):
            #     instr = self.detector[str(i)]
            #     param = instr.param
            #     for key in param:
            #         group4.create_dataset(f'Det{i}_{key}', data=param[key])

    def update_scan(self, axes_list, data_list):
        data_a = np.array(data_list)
        axes_a = np.array(axes_list)
        with h5py.File(os.path.join(self.folderpath, self.currentfile), 'a') as file:
            group = file['Data']
            data = group['data']
            axes = group['axes']
            size_data = data.shape[0]+data_a.shape[0]
            size_axes = axes.shape[0]+axes_a.shape[0]
            axes.resize((size_axes, axes.shape[1]))
            data.resize((size_data, data.shape[1]))
            axes[-axes_a.shape[0]:, :] = axes_a
            data[-data_a.shape[0]:, :] = data_a
        # with h5py.File(os.path.join(self.folderpath, self.currentfile), 'r+') as file:
        #     group = file['Data']
            # rangelim = group['rangelim']
            # rangelim[...] = self.range_lim

    def make_read_me(self):
        # check if folder exists and create folder
        if not os.path.exists(self.folderpath):
            os.makedirs(self.folderpath)

        # check if filename exists and create filename
        if os.path.exists(os.path.join(self.folderpath, self.filename+'.h5')):
            self.log(f'The file {self.filename} exists. Redefining filename as {self.filename}_new.h5')
            self.filename = self.filename +'_new'

        with open(os.path.join(self.folderpath, f'readme_{self.filename}.txt'),'w') as file:
            file.write(f'User: {self.user}\n')
            file.write(f'Date time: {self.date} \n')
            file.write('\n')
            file.write(f'Scan parameters: \n')
            # for i in range(len(self.device)):
            #     priority = str(i)
            #     start = self.val[priority][0]
            #     end = self.val[priority][-1]
            #     step = self.val[priority][1]-self.val[priority][0]
            #     file.write(f'Priority {priority}: {self.type[priority]} from {start} to {end} in steps of {step}. \n')
            # file.write('\n')
            # file.write(f'Static parameters: \n')
            # for i in range(len(self.static)):
            #     instr = self.static[str(i)]
            #     getparam = getattr(instr, instr.method_get)
            #     param = getparam()
            #     file.write(f'{instr.type}: {param} {instr.unit['str']}\n')
            # file.write('\n')
            # file.write(f'Detector parameters: \n')
            # for i in range(len(self.detector)):
            #     instr = self.detector[str(i)]
            #     param = instr.param
            #     file.write(f'{self.type}\n')
            #     for key in param:
            #         file.write(f'{key}: {param[key]}\n')


