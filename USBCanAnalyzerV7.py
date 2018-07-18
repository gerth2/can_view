# Interface for talking over can to the mystical "V7.00" boxes that come from SEEEDstudio or ebay
#  They're the ones like https://www.seeedstudio.com/USB-CAN-Analyzer-p-2888.html , based on a 
#  QinHeng CH340 USB2 serial to USB adapter.
#
# I purchased one and tested with it against a smattering of CAN devices (mostly for FRC robotics).
# Protocol was snooped by "Viking Star" - a very special thanks to this individual and his blog post:
# http://arduinoalternatorregulator.blogspot.com/2018/03/a-look-at-seedstudio-usb-can-analyzer.html

import serial #Requires pySerial.
import datetime

class CanPacket:

    def __init__(self, starttime, prevtime):
        self.id = bytearray()
        self.data = bytearray()
        self.rx_time = datetime.datetime.now()
        self.start_time = starttime
        self.prev_time = prevtime

    def id_prepend(self, byte_in):
        self.id.insert(0, byte_in)

    def data_prepend(self, byte_in):
        self.data.insert(0, byte_in)

    def get_id_string(self):
        ret_str = str()
        ret_str += format(int.from_bytes(self.id, byteorder='little'), '#10X')
        return ret_str

    def get_data_string(self):
        ret_str = str()
        for byte in self.data :
            ret_str +=" "
            ret_str +=format(byte, '02X')
        return ret_str

    def get_rx_time(self):
        return self.rx_time

    def get_rx_time_delta_start(self):
        return self.rx_time - self.start_time

    def get_rx_time_delta_prev(self):
        return self.rx_time - self.prev_time

    def __str__(self):
        return self.get_id_string() + " " + self.get_data_string()


class DeviceInterface:

    #####################################################################
    # CONSTANTS
    #####################################################################

    #Device supported CAN bus speeds
    SUPPORTED_SPEEDS = {5:0x0C,10:0x0B,20:0x0A,50:0x09,100:0x08,125:0x07,200:0x06,250:0x05,400:0x04,500:0x03,800:0x02,1024:0x01}
    
    # Protocol tokens
    START_TOKEN=0xAA
    CMD_EXTENDED_MODE_TRANSFER = 0xF0
    CMD_STANDARD_MODE_TRANSFER = 0xC0
    CMD_CONFIGURE = 0x55
    CFG_EXTENDED_MODE = 0x02
    CFG_STANDARD_MODE = 0x01
    TX_MAGIC_BYTE_FINAL = 0x55

    MAX_BYTES_PER_UPDATE = 10000

    # RX State Machine variables
    RX_expectedIDBytes = 0
    RX_expectedDataBytes = 0
    RX_packetUnderConstruction = CanPacket(datetime.datetime.now(),datetime.datetime.now())
    RX_packetList = []


    #serial port object
    sp = None

    #####################################################################
    # PUBLIC API
    #####################################################################

    def __init__(self, speed_kbps=1024, use_extended_frame=True, comport="COM5" ):
        #So far:
        # --Filter unsupported
        # --Mask unsupported
        # --Mode hardcoded to "Normal"
        # --Frame type 

        if(use_extended_frame == False):
            # TODO: Test and support this
            raise NotImplementedError

        if(speed_kbps not in self.SUPPORTED_SPEEDS):
            print("Error: specified CAN speed " + speed_kbps + "kbps is not supported! Choose from " + str(self.SUPPORTED_SPEEDS.keys))
            return

        #Configure but do not open serial port
        if(self.sp is None):
            self.sp = serial.Serial()
            self.sp.baudrate=115200 #maybe?
            self.sp.port=comport
            self.speed = self.SUPPORTED_SPEEDS[speed_kbps]
            self.rx_packet_byte_idx = 0
            self.capture_start_time = datetime.datetime.now()
            self.prev_capture_time = self.capture_start_time
        return

    def open(self):
        if(self.sp is not None and not self.sp.is_open):
            self.sp.open()
            print("Serial port opened")
            self.sendConfigPacket()
            self.rx_packet_byte_idx = 0
            self.capture_start_time = datetime.datetime.now()
            print("Device configured")
        else:
            print("Port already open!")
        return

    def close(self):
        if(self.sp is not None and self.sp.is_open):
            self.sp.close()
            print("Serial port closed")
        else:
            print("Port already closed!")
        return

    def is_open(self):
        return self.sp.is_open


    def send(self, id, data):
        if(len(id) != 4):
            print("Err, Extended ID expected to be passed as a length 4 bytearray, MSB at index 0")
            return

        num_bytes = len(data)
        if(num_bytes > 8):
            print("Err, cannot send more than 8 bytes of data")
            return

        if(self.sp is not None and self.sp.is_open):
            # Init with required header
            send_buf = bytearray([self.START_TOKEN, 
                                  self.CMD_EXTENDED_MODE_TRANSFER|num_bytes,
                                 ])
            # Pack bytes LSB first
            for byte in reversed(id):
                send_buf.append(byte)
            for byte in reversed(data):
                send_buf.append(byte)

            # Yet another magic byte determined from reverse engineering the sample program's output
            send_buf.append(self.TX_MAGIC_BYTE_FINAL)

            # Send data
            print("Sending packet " + str(send_buf))
            self.sp.write(send_buf)
        return

    def receive(self):
        self.RX_packetList = []
        self.rx_state_machine_update()
        return self.RX_packetList



    #####################################################################
    #PRIVATE Methods
    #####################################################################

    def sendConfigPacket(self):
        if(self.sp is not None and self.sp.is_open):
            # Init with required header
            send_buf = bytearray()
            send_buf.append(self.START_TOKEN)
            send_buf.append(self.CMD_CONFIGURE)
            #Pack mystery byte
            send_buf.append(0x12)
            #Pack byte indicating CAN bus speed
            send_buf.append(self.speed)
            #Pack frame type byte
            send_buf.append(self.CFG_EXTENDED_MODE)
            #Filter not supported
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)
            #Mask not supported
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)
            #Hardcode mode to Normal? Set to 0x01 to get loopback mode
            send_buf.append(0x00)
            #Send magic byte (may have to be 0x01?)
            send_buf.append(0x01)
            #Send more magic bytes
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)
            send_buf.append(0x00)

            #Calculate checksum
            checksum = 0
            for idx in range(0,18):
                checksum += int(send_buf[idx])
            checksum = checksum % 255
            
            send_buf.append(checksum)

            # Send data
            print("Sending packet " + str(send_buf))
            self.sp.write(send_buf)

    def rx_state_machine_update(self):

        #Helper utility to check for a received byte matching the expected protocol
        def rx_check(actual, expected, reset_on_err=True):
            if(int(actual) == int(expected)):
                self.rx_packet_byte_idx += 1
                return True
            else:
                if(reset_on_err):
                    #print("Error in packet RX: Got " + format(actual, '#04X') + " but was expecting " + format(expected, '#04X'))
                    self.rx_packet_byte_idx = 0
                return False

        byte_counter = 0

        if(self.sp is not None and self.sp.is_open):
            #As long as we have at least one packet, read it.
            while(self.sp.in_waiting != 0 and byte_counter < self.MAX_BYTES_PER_UPDATE): 

                byte_counter += 1

                #Read exactly one byte out of the serial port buffer
                new_byte = int.from_bytes(self.sp.read(size=1), byteorder='little')
                #print(str(self.rx_packet_byte_idx) + " " + format(new_byte,'#04x'))

                # Handle this byte based on which byte we are currently on
                if(self.rx_packet_byte_idx == 0):
                    if(int(new_byte) != 0xAA):
                        #Discard bytes till the start marker 
                        continue

                if(self.rx_packet_byte_idx == 0):
                    rx_check(new_byte,0xAA)
                    continue
                elif(self.rx_packet_byte_idx == 1):
                    if(rx_check(new_byte&0xF0,0xC0,False)):
                        #Standard Packet incoming
                        self.RX_expectedIDBytes = 2
                        self.RX_expectedDataBytes = int(new_byte&0x0F)
                    elif(rx_check(new_byte&0xF0,0xE0,True)):
                        #Extended packet incoming
                        self.RX_expectedIDBytes = 4
                        self.RX_expectedDataBytes = int(new_byte&0x0F)

                    #print(" --Expecting " + str(self.RX_expectedIDBytes) + " ID Bytes")
                    #print(" --Expecting " + str(self.RX_expectedDataBytes) + " data bytes")
                    
                    self.RX_packetUnderConstruction = CanPacket(self.capture_start_time, self.prev_capture_time)
                    continue
                elif(self.rx_packet_byte_idx in range(2, 2 + self.RX_expectedIDBytes)):
                    #Receiving ID
                    self.RX_packetUnderConstruction.id_prepend(new_byte)
                    self.rx_packet_byte_idx += 1
                    continue
                elif(self.rx_packet_byte_idx in range(2 + self.RX_expectedIDBytes, 2 + self.RX_expectedIDBytes + self.RX_expectedDataBytes )):
                    #Receiving Data
                    self.RX_packetUnderConstruction.data_prepend(new_byte)
                    self.rx_packet_byte_idx += 1

                    if(self.rx_packet_byte_idx >= (2 + self.RX_expectedIDBytes + self.RX_expectedDataBytes)):
                        #Done receiving
                        self.RX_packetList.append(self.RX_packetUnderConstruction)
                        self.prev_capture_time = datetime.datetime.now()
                        self.rx_packet_byte_idx = 0
                        #print(self.RX_packetList)
                    continue
                else:
                    print("Developers goofed up???")
                    self.rx_packet_byte_idx = 0
                    continue

    def __del__(self):
        self.close()
        return

    def sendTestPacket(self):
        self.send(bytearray([0x01, 0x02, 0x03, 0x04]), bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x6, 0x07, 0x08]))


