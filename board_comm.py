#!/usr/bin/env python
import random
import time
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

        self._last_ui_keep_alive = time.time()
        self.message_queue = message_queue
        self.sock = sock
        
        # Listeners
        self._tf.add_type_listener(MSG_ID_OPERATION_MODE_CMD, self.operationModeCallback)
        self._tf.add_type_listener(MSG_ID_VARIANT_GET, self.variantCallback)
        self._tf.add_type_listener(MSG_ID_APPLICATION_VERSION_GET, self.applicationVersionCallback)
        self._tf.add_type_listener(MSG_ID_UI_KEEP_ALIVE, self.keepAliveCallback)
        self._tf.add_type_listener(MSG_ID_WHITE_LOG_REQUEST,self.whiteLogCallback)
        self._tf.add_type_listener(MSG_ID_ENERGY_CALCULATION_GET,self.energyCalculationCallback)

    # Callback
    def operationModeCallback(self, frame, data):
        self.message_queue.put(MSG_ID_OPERATION_MODE_TRANSMIT)

    def variantCallback(self, frame, data):
        self.message_queue.put(MSG_ID_VARIANT_GET)

    def applicationVersionCallback(self, frame, data):
        self.message_queue.put(MSG_ID_APPLICATION_VERSION_GET)

    def keepAliveCallback(self, frame, data):
        self.message_queue.put(MSG_ID_UI_KEEP_ALIVE)

    def whiteLogCallback(self, frame, data):
        self.message_queue.put(MSG_ID_WHITE_LOG_RESPONSE)

    def energyCalculationCallback(self, frame, data):
        self.message_queue.put(MSG_ID_ENERGY_CALCULATION_GET)

    # Send
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
        
        self._tf.send(MSG_ID_APPLICATION_VERSION_GET, definitions["versionData_t"].serialize(output))

    def sendKeepAlive(self):
        output = {}
        output["val"] = 1
        self._tf.send(MSG_ID_UI_KEEP_ALIVE, definitions["StandardCmd_t"].serialize(output))

    def sendWhiteLog(self):
        options = ["[**EXAMPLE**]Monitor to DISCHARGE - low IHV[**EXAMPLE**]", "[**EXAMPLE**]Transiet to discharge monitor[**EXAMPLE**]", "[**EXAMPLE**]Active monitor[**EXAMPLE**]"]
        dummy_data = random.choice(options) + "\n"

        output = {}
        output['frame_id'] = 1
        output["len"] = 1000
        output["type"] = MSG_ID_WHITE_LOG_RESPONSE
        output["data"] = bytes(dummy_data, "utf-8")  # Ensure it's a bytes object
        print(output)
        self._tf.send(MSG_ID_WHITE_LOG_RESPONSE, definitions["DebugNotificationResponse_t"].serialize(output))

    def sendEnergyCalculation(self):
        output = {}
        output["vlv"] = 360 + random.randint(-100, 100)
        output["vlv_timestamp"] = 167253 + random.randint(-167253, 167253)
        output["ilv"] = 100 + random.randint(-20, 20)
        output["ilv_timestamp"] = 167253 + random.randint(-167253, 167253)
        output["health_status"] = 1
        output["state_machine_mode_state"] = 1
        output["state_machine_current_state"] = 1
        self._tf.send(MSG_ID_ENERGY_CALCULATION_GET, definitions["retEnergyCalculation_t"].serialize(output))

    # Socket send
    def serialWrite(self, buf):
        if self.sock:
            try:
                self.sock.sendto(buf, (TARGET_IP, TARGET_PORT))
            except Exception as e:
                print(f"Error sending data: {e}")
        else:
            print("No socket provided to send data")