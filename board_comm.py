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

    def operationModeCallback(self, frame, data):
        self.message_queue.put(MSG_ID_OPERATION_MODE_TRANSMIT)

    def variantCallback(self, frame, data):
        self.message_queue.put(MSG_ID_VARIANT_GET)

    def serialWrite(self, buf):
        if self.sock:
            try:
                self.sock.sendto(buf, (TARGET_IP, TARGET_PORT))
            except Exception as e:
                print(f"Error sending data: {e}")
        else:
            print("No socket provided to send data")

    def sendOperationMode(self):
        output = {}
        output["mode"] = 5
        self._tf.send(MSG_ID_OPERATION_MODE_TRANSMIT, definitions["retOperationMode_t"].serialize(output)) #  output = 5

    def sendVariant(self):
        output = {}
        output["fpga_variant"] = 187     
        output["mcu_variant"] = 187 
        self._tf.send(MSG_ID_VARIANT_GET, definitions["variantData_t"].serialize(output)) #  output = 5
