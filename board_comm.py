#!/usr/bin/env python
from constants import TARGET_IP, TARGET_PORT
from messages import *
import pycstruct
from payload_parser import TinyFrame

definitions = pycstruct.parse_file('messages.h')
MCU_TIMEOUT = 3.0

class BoardComm():
    def __init__(self, message_queue, sock=None):
        self._tf = TinyFrame()
        self._tf.ID_BYTES = 1
        self._tf.LEN_BYTES = 2
        self._tf.TYPE_BYTES = 1
        self._tf.CKSUM_TYPE = 'crc16'
        self._tf.SOF_BYTE = 0xAA
        self._tf.write = self.serialWrite

        self.message_queue = message_queue
        self.sock = sock
        
        self._tf.add_type_listener(MSG_ID_OPERATION_MODE_CMD, self.operationModeCallback)
        self._tf.add_type_listener(MSG_ID_VARIANT_GET, self.variantCallback)
        self._tf.add_type_listener(MSG_ID_APPLICATION_VERSION_GET, self.applicationVersionCallback)

    def operationModeCallback(self, frame, data):
        self.message_queue.put(MSG_ID_OPERATION_MODE_TRANSMIT)

    def variantCallback(self, frame, data):
        self.message_queue.put(MSG_ID_VARIANT_GET)

    def applicationVersionCallback(self, frame, data):
        self.message_queue.put(MSG_ID_APPLICATION_VERSION_GET)

    def sendOperationMode(self):
        output = {}
        output["mode"] = 5
        self._tf.send(MSG_ID_OPERATION_MODE_TRANSMIT, definitions["retOperationMode_t"].serialize(output))

    def sendVariant(self):
        output = {}
        output["fpga_variant"] = 187     
        output["mcu_variant"] = 1 
        self._tf.send(MSG_ID_VARIANT_GET, definitions["variantData_t"].serialize(output))

    def sendApplicationVersion(self):
        output = {}

        output["mcu_ver"] = {}
        output["mcu_ver"]["major"] = 1  
        output["mcu_ver"]["minor"] = 2  
        output["mcu_ver"]["patch"] = 5  


        output["fpga_ver"] = {}
        output["fpga_ver"]["major"] = 3  
        output["fpga_ver"]["minor"] = 0  
        output["fpga_ver"]["patch"] = 0  


        output["bootloader_ver"] = {}
        output["bootloader_ver"]["major"] = 0  
        output["bootloader_ver"]["minor"] = 9  
        output["bootloader_ver"]["patch"] = 1

        print(output)

        self._tf.send(MSG_ID_APPLICATION_VERSION_GET, definitions["versionData_t"].serialize(output))

    def serialWrite(self, buf):
        if self.sock:
            try:
                self.sock.sendto(buf, (TARGET_IP, TARGET_PORT))
            except Exception as e:
                print(f"Error sending data: {e}")
        else:
            print("No socket provided to send data")