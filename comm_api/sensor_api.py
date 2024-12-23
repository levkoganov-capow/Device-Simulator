#!/usr/bin/env python
from payload_parser import TF_Msg, TF
from sensors_name import *
from messages import *
import pycstruct

__author__ = "Itamar Eliakim / CaPow Technologies LTD"
__maintainer__ = "Itamar Eliakim"
__email__ = "itamar@rootiebot.com"

definitions = pycstruct.parse_file('messages.h')

class CommSensorAPI():
    def __init__(self, comm_layer, logger_gui = None):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui

        self.last_sensor_transmit = ""

        self._faulty_sensor_list = [[], [], [], [], [], []]
        self._sensor_fault_stream = [[["-", "-", "-", "-"]] * (self._comm_layer.NUM_OF_FAULT_SENSORS)]            # Fault Sensors
        self._sensor_fault_idx = 0

        self.reset_tables()
        
    ############################################
    ##             Sensor Section             ##
    ############################################
    ##Callbacks
    def faulty_sensor_callback(self, tf: TF, msg: TF_Msg):
        result = definitions["SensorFault_t"].deserialize(msg.data)
        if (result['sensor_id'] not in self._faulty_sensor_list[result['group_id']]):
            self._logger_gui.log(f"Error: Faulty Sensor! Group ID: {GROUP_ID[result['group_id']]} Sensor ID: {result['sensor_id']}", True)
            self._faulty_sensor_list[result['group_id']].append(result['sensor_id'])

        output = {"group_id": result['group_id'], "sensor_id": result['sensor_id']}
        self._comm_layer.send(MSG_ID_FAULTY_SENSOR_ACK, definitions["ReqSensorConfig_t"].serialize(output))

    def sensor_transmit_callback(self, tf: TF, msg: TF_Msg):
        result = definitions["sensorCommand_t"].deserialize(msg.data)
        group_id = result["group_id"]
        id = result["id"]
        value = result["value"]
        
        if (group_id == 0):                 #FPGA
            ret_value = value
            if (id == 1):
                ret_value = str(value)
            self.last_sensor_transmit = f"Interface ID: {group_id}, Register: {id}, Value: {ret_value}"
        else:
            self.last_sensor_transmit = f"Interface ID: {group_id}, ID: {id}, Value: {value}"

    def sensor_fault_callback(self, tf: TF, msg: TF_Msg):
        # Callback for sensor data
        result = definitions["SensorFault_t"].deserialize(msg.data)
        group_id = result["group_id"]
        sensor_id = result["sensor_id"]
        sensor_value = result["value"]
        sensor_status = result["status"]

        if ([GROUP_ID[group_id], sensor_id, 0, 0] not in self._sensor_fault_stream[0]):
            self._sensor_fault_stream[0][self._sensor_fault_idx % self._comm_layer.NUM_OF_FAULT_SENSORS] = [GROUP_ID[group_id], sensor_id, 0, 0]
            self._sensor_fault_idx += 1
            self._logger_gui.log(f"Error: Sensor Group ID: {GROUP_ID[group_id]}, Sensor ID: {sensor_id}, Sensor value: {sensor_value}, Sensor Status: {sensor_status}", True)
        return TF.STAY
    
    def sensor_data_long_callback(self, tf: TF, msg: TF_Msg):
        # Callback for sensor data
        # TODO: Merge with short sequence
        result = definitions["SensorDataLongOut_t"].deserialize(msg.data)
        sensor_id = result["sensor_id"]
        group_id = result["group_id"]
        retry_cnt = result["retry_cnt"]
        active_in_state = result["active_in_state"]
        peripheral_state = SENSOR_PERIPHERAL_STATE[result["peripheral_state"]]
        sensor_status = SENSOR_STATUS[result["status"]]
        config_values = list(result["config"].values())  # Config from EEPROM

        #Support TX/RX Sensor Names
        if ((group_id == 0) or (group_id == 5)): #NIBB
            sensor_name = SensorName[group_id][self._comm_layer.systemAPI.get_mcu_variant()][sensor_id]
        else:
            sensor_name = SensorName[group_id][sensor_id]

        sensor_info = [sensor_id, sensor_name, sensor_status, peripheral_state, result["value"], retry_cnt, active_in_state] + config_values
        self._sensors_stream[result["group_id"]][sensor_id] = sensor_info
        return TF.STAY
    
    def sensor_data_short_callback(self, tf: TF, msg: TF_Msg):
        # Callback for sensor data
        result = definitions["SensorDataShortOut_t"].deserialize(msg.data)

        #Support TX/RX Sensor Names
        if ((result["group_id"] == 0) or (result["group_id"] == 5)): #NIBB
            sensor_name = SensorName[result["group_id"]][self._comm_layer.systemAPI.get_mcu_variant()][result["sensor_id"]]
        else:
            sensor_name = SensorName[result["group_id"]][result["sensor_id"]]

        retry_cnt = result["retry_cnt"]
        self._sensors_stream[result["group_id"]][result["sensor_id"]] =  [result["sensor_id"], sensor_name, SENSOR_STATUS[result["status"]], \
                                                                          SENSOR_PERIPHERAL_STATE[result["peripheral_state"]], \
                                                                          result["value"], retry_cnt, result["active_in_state"]]
        return TF.STAY

    ##Commands
    def start_sensor_stream(self, group_id):
        # Start sensor stream
        output = {}
        output["cmd"] = 1
        output["group_id"] = group_id
        self._comm_layer.sendWithACK(MSG_ID_SENSOR_STREAM_CMD, definitions["reqSensorStream_t"].serialize(output))
        self.reset_tables()
        
    def stop_sensor_stream(self):
        # Stop sensor stream
        output = {}
        output["cmd"] = 0
        output["group_id"] = 0
        self._comm_layer.sendWithACK(MSG_ID_SENSOR_STREAM_CMD, definitions["reqSensorStream_t"].serialize(output))

    ##Getters
    def get_sensor_stream(self, id):
        # Get sensor stream
        return self._sensors_stream[id]

    def get_sensor_fault(self):
        # Get sensor fault
        return self._sensor_fault_stream[0]
    
    def get_sensor_transmit(self):
        return self.last_sensor_transmit

    def reset_tables(self):
        #print(self._comm_layer.systemAPI.get_mcu_variant())
        self._sensors_stream = [[[0, "None", 0, 0, 0, 0, 0]] * (len(NibbSensorName[self._comm_layer.systemAPI.get_mcu_variant()]) - 1),                      # Nibb
                                [[0, "None", 0, 0, 0, 0, 0]] * (len(InverterSensorName) - 1),                                                                # Inverter
                                [[0, "None", 0, 0, 0, 0, 0]] * (len(ResonatorSensorName) - 1),                                                               # Resonator
                                [[0, "None", 0, 0, 0, 0, 0]] * (len(RectifierSensorName) - 1),                                                               # Rectifier
                                [[0, "None", 0, 0, 0, 0, 0]] * (len(MbSensorName) - 1),                                                                      # Motherboard
                                [[0, "None", 0, 0, 0, 0, 0]] * (len(DebugSensorName[self._comm_layer.systemAPI.get_mcu_variant()]) - 1)]                                                                   # Debug
