#!/usr/bin/env python
import serial
# from sensors_name import *
from messages import *
# import pycstruct
import threading
import time
from payload_parser import TinyFrame, TF_Msg, TF

# API Modules
from comm_api.udp_comm_api import CommUDPAPI
# from comm_api.config_api import CommConfigAPI
# from comm_api.fpga_api import CommFPGAAPI
# from comm_api.state_machine_api import CommStateMachineAPI
# from comm_api.system_api import CommSystemModuleAPI
# from comm_api.sensor_api import CommSensorAPI
# from comm_api.flash_logger_api import CommFlashLoggerAPI
# from comm_api.firmware_api import FirmwareAPI

__author__ = "Itamar Eliakim / CaPow Technologies LTD"
__maintainer__ = "Itamar Eliakim"
# __email__ = "itamar@rootiebot.com"

# definitions = pycstruct.parse_file('messages.h')
MCU_TIMEOUT = 3.0

class DebugNotification():
    def __init__(self) -> None:
        self.stamp = 0
        self.chunk = -1

class BoardComm():
    UART = 0
    UDP = 1
    NUM_OF_FAULT_SENSORS = 4
    COMM_RETRY_CNT = 50
    UI_KEEP_ALIVE_TIMEOUT = 5.0

    def __init__(self, mode, esp32_id = None, esp32_ip = None, serial_port = None, baudrate = None, logger_gui = None, esp32_variant = None) -> None:
        # self._logger_gui = logger_gui

        # Initialize Modules
        # self.configAPI = CommConfigAPI(self, logger_gui)
        # self.systemAPI = CommSystemModuleAPI(self, logger_gui)
        # self.fpgaAPI = CommFPGAAPI(self, logger_gui)
        # self.stateMachineAPI = CommStateMachineAPI(self, logger_gui)
        # self.sensorAPI = CommSensorAPI(self, logger_gui)
        # self.flashLoggerAPI = CommFlashLoggerAPI(self, logger_gui)
        # self.firmwareUpgradeAPI = FirmwareAPI(self, logger_gui)

        # Initialize the serial/udp communication
        self.result = None
        self._mode = mode
        self._get_info_cnt = 0
        # self._last_ui_keep_alive = time.time()
        # self._last_debug_notification = DebugNotification()

        # Data for retrying failed messages
        # self._retry_on_failure = True
        self._last_ack = {"id": -1, "type": -1}
        self._last_msg = {"id": 0, "type": 0, "data": ""}
        self._exit_event = threading.Event()
        
        # if (mode == self.UART):
        #     self._in_pairing = False
        #     self._serial_port = serial_port
        #     self._ser = serial.Serial(serial_port, baudrate, timeout = 5)

        # elif (mode == self.UDP):
        self.udpAPI = CommUDPAPI(self, esp32_id, esp32_ip, esp32_variant)
        
        # Communication Parser
        self._tf = TinyFrame()
        self._tf.ID_BYTES = 1
        self._tf.LEN_BYTES = 2
        self._tf.TYPE_BYTES = 1
        self._tf.CKSUM_TYPE = 'crc16'
        self._tf.SOF_BYTE = 0xAA
        self._tf.write = self.serialWrite
        
        # Stop Stream
        # self.sensorAPI.stop_sensor_stream()

        # Add the listeners
        # self._tf.add_fallback_listener(self.fallback_cb)

        # System
        # self._tf.add_type_listener(MSG_ID_APPLICATION_VERSION_GET, self.systemAPI.app_version_callback)
        # self._tf.add_type_listener(MSG_ID_VARIANT_GET, self.systemAPI.variant_callback)
        # self._tf.add_type_listener(MSG_ID_OPERATION_MODE_TRANSMIT, self.systemAPI.operation_mode_callback)

    # def fallback_cb(self, frame, b):
    #     # Fallback callback for messages who aren't handled
    #     print(frame)
    #     print("Fallback listener")
        
    #     if (OPERATION_MODES[self.systemAPI.operation_mode] == "APPLICATION_RUN"):
    #         self._tf.send(MSG_ID_UI_KEEP_ALIVE, b"1")
    #         if (all([self.systemAPI.app_version, self.systemAPI.bl_version]) and (self._last_ui_keep_alive is not None)):
    #             if (not self.is_alive()):
    #                 self._logger_gui.log(f"UI<>MCU Timeout! {(time.time() - self._last_ui_keep_alive)}")
    #                 if (self._mode == self.UDP):
    #                     self._logger_gui.log(f"Trying Reconnect ESP")
    #                     if (self.udpAPI.udp_pairing()):
    #                         self._last_ui_keep_alive = time.time()

    def is_alive(self):
        return ((time.time() - self._last_ui_keep_alive) < self.UI_KEEP_ALIVE_TIMEOUT)
    
    def check_keep_alive(self):
        while not self._exit_event.is_set():
            # self.send_ui_keep_alive()
            time.sleep(0.2)

    # def ack_callback(self, tf: TF, msg: TF_Msg):
    #     # Callback for ack
    #     self._last_ack = definitions["ACKCmd_t"].deserialize(msg.data)

    def set_exit_event(self):
        # Set the exit event
        self._exit_event.set()
        if (self._mode == self.UDP):
            self.udpAPI.udp_client.close()
            self.udpAPI.udp_server.close()

    def serialWrite(self, buf):
        # Write to the serial/udp port
        if (self._mode == self.UART):
            try:
                self._ser.write(buf)
            except:
                pass
        elif (self._mode == self.UDP):
            if (not self.udpAPI.is_pairing()):
                self.udpAPI.udp_client.sendto(buf, (self.udpAPI.esp32_ip, self.udpAPI.UDP_ESP32_PORT))

    def start_comm(self):
        # Read from the serial/udp port
        while not self._exit_event.is_set():
            if (self._mode == self.UART):
                line = self._ser.read()
                self._tf.accept(line)
            if (self._mode == self.UDP):
                line = self.udpAPI.read()
                self._tf.accept(line)

    def send(self, type, data):
        # Send a message to the MCU, and store message on last
        self.result = None
        # self.stateMachineAPI.current_state = ""
        # self.sensorAPI.last_sensor_transmit = ""
        self._tf.send(type, data)
        self._last_msg["type"] = type
        self._last_msg["data"] = data
        self._last_msg["id"] = data

    def sendWithACK(self, type, data):
        # Send a message to the MCU, and store message on last
        self.result = None
        self.stateMachineAPI.current_state = ""
        self.sensorAPI.last_sensor_transmit = ""

        for i in range(0, self.COMM_RETRY_CNT):
            id = self._tf.send(type, data)
            self._last_msg["type"] = type
            self._last_msg["data"] = data
            self._last_msg["id"] = id
            if ((self._last_msg["id"] == (self._last_ack["id"] + 1)) and (self._last_msg["type"] == self._last_ack["type"])):
                print("ACK Recieved!")
                break
            time.sleep(0.01)

    def resend(self):
        # Resend a message to the MCU, and store message on last
        self.result = None
        self._tf.send(self._last_msg["type"], self._last_msg["data"])

    def receive(self):
        # Wait for a response from the MCU
        start_time = time.time()
        while ((self.result is None)):
            # Retry if MCU doesn't respond
            if ((time.time() - start_time > MCU_TIMEOUT/2) and self._retry_on_failure):
                self.resend()

            if (time.time() - start_time > MCU_TIMEOUT):
                break

            time.sleep(0.1)

        if (self.result is None):
            print("MCU Timeout")

        return self.result

    def get_mode(self):
        # Get mode
        return self._mode
    
    def is_ready(self):
        #if all([self.systemAPI.fpga_variant, self.systemAPI.mcu_variant, self.systemAPI.app_version, self.systemAPI.fpga_version]):
        if all([self.systemAPI.bl_version, self.systemAPI.app_version, self.systemAPI.fpga_version]):
            self._tf.send(MSG_ID_FAULTY_SENSOR, b"1")       #Get Faulty Sensors
            return True
        
        if (self._mode == self.UDP and self._get_info_cnt > 5):
            print("Retry pairing ESP")
            self.udpAPI.udp_pairing()

        #Get Operation Mode: Bootloader / Application
        if not all([self.systemAPI.operation_mode]):
            print("Getting Board Operation Mode..")
            self.send(MSG_ID_OPERATION_MODE_CMD, b"1")
            return False

        #Get Variant only On Application
        if (OPERATION_MODES[self.systemAPI.operation_mode] == "APPLICATION_RUN"):
            #Get MCU and FPGA Variants
            if not all([self.systemAPI.fpga_variant, self.systemAPI.mcu_variant]):
                print("Getting Board Variant...")
                self.send(MSG_ID_VARIANT_GET, b"1")
                return False
            
        #Get MCU and FPGA Application Version
        if not all([self.systemAPI.app_version, self.systemAPI.fpga_version,self.systemAPI.bl_version]):
            print("Getting Board Version...")
            self.send(MSG_ID_APPLICATION_VERSION_GET, b"1")
            return False
    
        fpga_version_str = f"FPGA Version: {self.systemAPI.fpga_version}"
        app_version_str = f"App Version: {self.systemAPI.app_version}"
        bl_version_str = f"BL Version: {self.systemAPI.bl_version}"
        self._logger_gui.log(f"{fpga_version_str} {app_version_str} {bl_version_str}")

        self._get_info_cnt += 1
        return False

    def get_serial_port(self):
        # Get serial port
        return self._serial_port

    # def sys_health(self, tf: TF, msg: TF_Msg):
    #     self.result = msg.data
    #     return TF.STAY
