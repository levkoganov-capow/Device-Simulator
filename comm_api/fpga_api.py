#!/usr/bin/env python
from payload_parser import TF_Msg, TF
from sensors_name import *
from messages import *
import pycstruct

__author__ = "Itamar Eliakim / CaPow Technologies LTD"
__maintainer__ = "Itamar Eliakim"
__email__ = "itamar@rootiebot.com"

definitions = pycstruct.parse_file('messages.h')
MCU_TIMEOUT = 3.0

class CommFPGAAPI():
    def __init__(self, comm_layer, logger_gui):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui

        self._fpga_fault_stream = [[["-", "-", "-", "-"]] * (self._comm_layer.NUM_OF_FAULT_SENSORS)]                         # Fault FPGA
        self._fpga_fault_idx = 0
        
        self.reset_tables()

    ############################################
    ##              FPGA Section              ##                
    ############################################
    ##Callbacks
    def fpga_fault_callback(self, tf: TF, msg: TF_Msg):
        # Callback for sensor data
        result = definitions["SensorFault_t"].deserialize(msg.data)
        group_id = result["group_id"]
        sensor_id = result["sensor_id"]

        if (self._comm_layer.systemAPI.mcu_variant == "TX"):
            if ([GROUP_FPGA_TX_PROTECT_ID[group_id], sensor_id, 0, 0] not in self._fpga_fault_stream[0]):
                self._fpga_fault_stream[0][self._fpga_fault_idx % self._comm_layer.NUM_OF_FAULT_SENSORS] = [GROUP_FPGA_TX_PROTECT_ID[group_id], sensor_id, 0, 0]
                self._fpga_fault_idx += 1
                self._logger_gui.log(f"Error: FPGA Protect! Group ID: {GROUP_FPGA_TX_PROTECT_ID[group_id]} Bit ID: {sensor_id}", True)
        elif (self._comm_layer.systemAPI.mcu_variant == "RX"):
            if ([GROUP_FPGA_RX_PROTECT_ID[group_id], sensor_id, 0, 0] not in self._fpga_fault_stream[0]):
                self._fpga_fault_stream[0][self._fpga_fault_idx % self._comm_layer.NUM_OF_FAULT_SENSORS] = [GROUP_FPGA_RX_PROTECT_ID[group_id], sensor_id, 0, 0]
                self._fpga_fault_idx += 1
                self._logger_gui.log(f"Error: FPGA Protect! Group ID: {GROUP_FPGA_RX_PROTECT_ID[group_id]} Bit ID: {sensor_id}", True)
        return TF.STAY
    
    def fpga_protect_data_callback(self, tf: TF, msg: TF_Msg):
        # Callback for sensor data
        result = definitions["FPGAProtectBitDataOut_t"].deserialize(msg.data)
        group_id = result["group_id"]
        sensor_id = result["sensor_id"]
        status = SENSOR_STATUS[result["status"]]
        bit = result["bit"]
        tries = result["tries"]
        time_interval = result["time_interval"]

        if (self._comm_layer.systemAPI.mcu_variant == "TX"):
            sensor_info = [sensor_id, FPGA_TX_PROTECT_NAME[group_id][sensor_id], status, bit, tries, time_interval]
        elif (self._comm_layer.systemAPI.mcu_variant == "RX"):
            sensor_info = [sensor_id, FPGA_RX_PROTECT_NAME[group_id][sensor_id], status, bit, tries, time_interval]
        self._fpga_protect_stream[result["group_id"]][sensor_id] = sensor_info
        return TF.STAY
    
    ##Commands
    def start_fpga_protect_stream(self, group_id):
        # Start sensor stream
        output = {}
        output["cmd"] = 1
        output["group_id"] = group_id
        self._comm_layer.sendWithACK(MSG_ID_FPGA_PROTECT_STREAM_CMD, definitions["reqSensorStream_t"].serialize(output))
        self.reset_tables()

    def stop_fpga_protect_stream(self):
        # Stop sensor stream
        output = {}
        output["cmd"] = 0
        output["group_id"] = 0
        self._comm_layer.sendWithACK(MSG_ID_FPGA_PROTECT_STREAM_CMD, definitions["reqSensorStream_t"].serialize(output))
    
    ##Getters
    def get_fpga_protect_stream(self, id):
        # Get fpga protect stream
        return self._fpga_protect_stream[id]
    
    def get_fpga_fault(self):
        # Get FPGA fault
        return self._fpga_fault_stream[0]
    
    def reset_tables(self):
        if (self._comm_layer.systemAPI.mcu_variant == "TX"):
            self._fpga_protect_stream = [[[0, 0, 0, 0, 0, 0]] * (len(NibbProtectRegister)),                            # Nibb Protect
                                        [[0, 0, 0, 0, 0, 0]] * (len(InverterProtectRegister)),                         # Inverter Protect
                                        [[0, 0, 0, 0, 0, 0]] * (len(PhaseProtectRegister))]                            # Phase Protect
        elif (self._comm_layer.systemAPI.mcu_variant == "RX"):
            self._fpga_protect_stream = [[[0, 0, 0, 0, 0, 0]] * (len(NibbProtectRegister)),                            # Nibb Protect
                                         [[0, 0, 0, 0, 0, 0]] * (len(RectifierProtectRegister)),                       # Rectifier Protect
                                         [[0, 0, 0, 0, 0, 0]] * (len(DetuneProtectRegister))]                          # Detune Protect