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

class CommStateMachineAPI():
    def __init__(self, comm_layer, logger_gui = None):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui

        self.current_state = ""
        self.energy_info = ""

    ############################################
    ##         State Machine Section          ##
    ############################################
    ##Callbacks
    def state_callback(self, tf: TF, msg: TF_Msg):
        # Callback for state
        result = definitions["stateMachineInfo_t"].deserialize(msg.data)
        mode_state = MODE_STATES[result["mode_state"]]
        work_state = WORK_STATES[self._comm_layer.systemAPI.get_mcu_variant()][result["work_state"]]
        developer_state = DEVELOPER_STATES[self._comm_layer.systemAPI.get_mcu_variant()][result["developer_state"]]
        self.current_state = f"Mode State: {mode_state}. Work State: {work_state}. Developer State: {developer_state}"
        # self._logger_gui.log(f"Mode State: {mode_state}")
        # self._logger_gui.log(f"Work State: {work_state}. Developer State: {developer_state}")
        return TF.STAY
    
    def energy_request_callback(self, tf: TF, msg: TF_Msg):
        result = definitions["retEnergyCalculation_t"].deserialize(msg.data)
        state_machine_mode_state = MODE_STATES[result["state_machine_mode_state"]]
        state_machine_current_state = WORK_STATES[self._comm_layer.systemAPI.get_mcu_variant()][result["state_machine_current_state"]]
        vlv = result["vlv"]
        vlv_timestamp = result["vlv_timestamp"]
        ilv = result["ilv"]
        ilv_timestamp = result["ilv_timestamp"]
        health_status = result["health_status"]
        self.energy_info = (f"State Machine Mode State: {state_machine_mode_state}. "
                            f"State Machine Current State: {state_machine_current_state}.\n"
                            f"Health Status: {health_status}. vlv: {vlv} timestamp: {vlv_timestamp}. "
                            f"ilv: {ilv} timestamp: {ilv_timestamp}")
        # self.energy_info = f"State Machine Mode State: {state_machine_mode_state}. State MachineCurrent State: {state_machine_current_state}. \n\+
        # f"Health Status {health_status}. vlv {vlv} timestamp {vlv_timestamp} . ilv {ilv} timestamp {ilv_timestamp}"

        return TF.STAY
    
    ##Getters
    def get_state(self):
        return self.current_state
    
    def get_energy_info(self):
        return self.energy_info
