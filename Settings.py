from tkinter import *
import tkinter.simpledialog
import configparser
import os, sys

#Required to get the ports available
import serial.tools.list_ports


class Settings():

    #Settings file storage info
    SETTINGS_FNAME="config.ini"

    def __init__(self):
        self.load()

    def openGUI(self, master):
        self.load()
        settingsGUI = settingsDialogBox(parent=master, settings=self)
        self.save()
        settingsGUI.destroy()

    def load(self):

        def getValWithDefault(cfg_in, section_str, val_str, default):
            try:
                section = cfg_in[section_str]
                return section.get(val_str)
            except:
                print(sys.exc_info())
                return default


        config = configparser.ConfigParser()

        #Open file if exists, or create a blank one if not.
        if(os.path.exists(self.SETTINGS_FNAME)):
            config.read(self.SETTINGS_FNAME)
        else:
            config['V7CAN_DEVICE'] = {}
            with open(self.SETTINGS_FNAME, 'w') as cfgfile:
                config.write(cfgfile)


        #This defines what gets read out of the .ini file. "fallback" values define the defaults
        self.can_baud_rate = getValWithDefault(config, 'V7CAN_DEVICE', 'can_baud_rate', 1024)
        self.can_use_extended_frame = getValWithDefault(config,'V7CAN_DEVICE','can_use_extended_frame', True)
        self.can_serial_baud = getValWithDefault(config,'V7CAN_DEVICE', 'can_serial_baud', 115200)
        self.can_serial_comport = getValWithDefault(config,'V7CAN_DEVICE', 'can_serial_comport', "COM5")

    def save(self):
        config = configparser.ConfigParser()

        config['V7CAN_DEVICE'] = {}
        config['V7CAN_DEVICE']['can_baud_rate'] = str(self.can_baud_rate)
        config['V7CAN_DEVICE']['can_use_extended_frame'] = str(self.can_use_extended_frame)
        config['V7CAN_DEVICE']['can_serial_baud'] = str(self.can_serial_baud)
        config['V7CAN_DEVICE']['can_serial_comport'] = str(self.can_serial_comport)

        with open(self.SETTINGS_FNAME, 'w') as cfgfile:
            config.write(cfgfile)



class settingsDialogBox(tkinter.simpledialog.Dialog):

    can_baud_rate_options_str = ['5','10','20','50','100','125','200','250','400','500','800','1024']
    can_extended_frame_options_str = ['False', 'True']
    can_serial_baudrate_options_str = ['115200','2000000']
    can_serial_port_available_options_str = serial.tools.list_ports.comports()

    def __init__(self, parent, settings):
        self.settings = settings
        tkinter.simpledialog.Dialog.__init__(self, parent = parent)

    def body(self, master):

        def pickInitOption(setting, options, val):
            if(str(setting) in options):
                val.set(str(setting))
            else:
                val.set(list(options)[0])

        Label(master, text="CAN Baud Rate Kbps").grid(row=0)
        Label(master, text="CAN Frame Size").grid(row=1)
        Label(master, text="CAN Serial Baudrate").grid(row=2)
        Label(master, text="CAN Serial Comport").grid(row=3)

        self.can_baud_rate_options_sel_val = StringVar(master)
        self.can_extended_frame_options_sel_val = StringVar(master)
        self.can_serial_baudrate_options_sel_val = StringVar(master)
        self.can_serial_port_available_options_sel_val = StringVar(master)

        self.e1 = OptionMenu(master, self.can_baud_rate_options_sel_val, *self.can_baud_rate_options_str)
        self.e2 = OptionMenu(master, self.can_extended_frame_options_sel_val, *self.can_extended_frame_options_str)
        self.e3 = OptionMenu(master, self.can_serial_baudrate_options_sel_val, *self.can_serial_baudrate_options_str)
        self.e4 = OptionMenu(master, self.can_serial_port_available_options_sel_val, *self.can_serial_port_available_options_str)

        pickInitOption(self.settings.can_baud_rate,  self.can_baud_rate_options_str, self.can_baud_rate_options_sel_val)
        pickInitOption(self.settings.can_use_extended_frame,  self.can_extended_frame_options_str,  self.can_extended_frame_options_sel_val)
        pickInitOption(self.settings.can_serial_baud,  self.can_serial_baudrate_options_str,  self.can_serial_baudrate_options_sel_val)
        pickInitOption(self.settings.can_serial_comport,  self.can_serial_port_available_options_str,  self.can_serial_port_available_options_sel_val)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        return self.e1 # initial focus

    def apply(self):

        self.settings.can_baud_rate = int(self.can_baud_rate_options_sel_val.get())
        self.settings.can_use_extended_frame = bool(self.can_extended_frame_options_sel_val.get())
        self.settings.can_serial_baud = int(self.can_serial_baudrate_options_sel_val.get())
        self.settings.can_serial_comport = str(self.can_serial_port_available_options_sel_val.get())



