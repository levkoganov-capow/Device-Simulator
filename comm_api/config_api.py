#!/usr/bin/env python
from payload_parser import TF_Msg, TF
# from sensors_name import *
from messages import *
import pycstruct
import time
import pandas as pd

definitions = pycstruct.parse_file('messages.h')
MCU_TIMEOUT = 3.0
RETRY_CNT = 50

class CommConfigAPI():
    def __init__(self, comm_layer, logger_gui = None):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui

    #####################################################
    ##                  FPGA Registers                 ##
    #####################################################
    def erase_fpga_flash_configuration(self):
        if (self._comm_layer is None):
            return
        
        #Retry on erase
        for i in range(0, RETRY_CNT):
            config_to_flash = {
                "id": 0xFFFF,
                "reg": 0xFFFF,
                "value": 0xFFFF
            }
            self._comm_layer.send(MSG_ID_CONFIG_FPGA_SET_SINGLE, definitions["RetFPGAConfig_t"].serialize(config_to_flash))
            time.sleep(0.1)

            #Validate result
            req_fpga_id = {
                "id": 0
            }
            self._comm_layer.send(MSG_ID_CONFIG_FPGA_READ_SINGLE, definitions["RetFPGAConfig_t"].serialize(req_fpga_id))
            time.sleep(0.1)

            config_from_flash = self._comm_layer.result

            if (config_from_flash is None):
                continue

            if (config_from_flash["reg"] == 0xFFFF):
                break

        self._comm_layer.sendWithACK(MSG_ID_CONFIG_SAVE, b"1")
        return 1
    
    def load_fpga_flash_configuration(self, variant, filename):
        df = pd.read_excel(filename, sheet_name = variant.capitalize() + 'FPGA')
        id_values = df['id']
        reg_values = df['reg']
        value_values = df['value']

        for i in range(len(id_values)):
            id_val = id_values[i]
            reg_val = reg_values[i]
            value_val = value_values[i]
            
            if pd.notna(value_val):
                config_to_flash = {
                    "id": int(id_val),
                    "reg": int(reg_val),
                    "value": int(value_val)
                }
                
                for retry in range(0, RETRY_CNT):
                    self._comm_layer.send(MSG_ID_CONFIG_FPGA_SET_SINGLE, definitions["RetFPGAConfig_t"].serialize(config_to_flash))
                    time.sleep(0.1)

                    #Validate result
                    req_fpga_id = {
                        "id": int(id_val)
                    }

                    self._comm_layer.send(MSG_ID_CONFIG_FPGA_READ_SINGLE, definitions["ReqFPGAConfig_t"].serialize(req_fpga_id))
                    time.sleep(0.1)
                    config_from_flash = self._comm_layer.result

                    if (config_from_flash == config_to_flash):
                        print(f"ID: {int(id_val)}, Reg: {int(reg_val)}, Value: {int(value_val)}")
                        break
                else:
                    print("ERROR! Load FPGA Registers from Flash")
                    print("Possible reasons: communication fault, MCU halt")

        self._comm_layer.sendWithACK(MSG_ID_CONFIG_SAVE, b"1")
        return 1
    
    def dump_fpga_flash_configuration(self):
        fpga_register_list = []
        for i in range(0, 200):
            output = {
                "id": i
            }
            for j in range(0, 10): #Allow 10 retry for each cell
                self._comm_layer.send(MSG_ID_CONFIG_FPGA_READ_SINGLE, definitions["RetFPGAConfig_t"].serialize(output))
                time.sleep(0.1)
                if (self._comm_layer.result is not None):
                    break
                
            if (self._comm_layer.result["reg"] == 0xFFFF):
                #print("Done")
                break
            
            if (self._comm_layer.result["id"] == i):
                fpga_register_list.append(self._comm_layer.result)

        return fpga_register_list
    
    ###############################################
    ##                  Variant                  ##
    ###############################################
    def dump_variant_flash_configuration(self):
        self._comm_layer.send(MSG_ID_CONFIG_VARIANT_READ_SINGLE, b"1")
        time.sleep(0.05)
        return self._comm_layer.receive()
    
    def check_input_ouput_dict(self, input, output):
        common_keys = input.keys() & output.keys()
        for key in common_keys:
            if input[key] != output[key]:
                return False
        return True
    
    def load_variant_flash_configuration(self, variant, file_path):
        print("Saving Config to MCU RAM")

        df = pd.read_excel(file_path, sheet_name = variant.capitalize() + 'MCU')
        data_dict = df.set_index('Key').to_dict()['Value']
        for i in range(0, 10):
            if (self._comm_layer.systemAPI.mcu_variant == "TX"):
                self._comm_layer.send(MSG_ID_CONFIG_VARIANT_SET_SINGLE, definitions["VariantTXConfiguration_t"].serialize(data_dict))
            elif (self._comm_layer.systemAPI.mcu_variant == "RX"):
                self._comm_layer.send(MSG_ID_CONFIG_VARIANT_SET_SINGLE, definitions["VariantRXConfiguration_t"].serialize(data_dict))

            time.sleep(0.05)
            self._comm_layer.send(MSG_ID_CONFIG_VARIANT_READ_SINGLE, b"1")
            time.sleep(0.05)
            ret = self._comm_layer.receive()
            if (ret is not None and self.check_input_ouput_dict(data_dict, ret)):
                break

        print("Saving RAM to Flash")
        self._comm_layer.sendWithACK(MSG_ID_CONFIG_SAVE, b"1")

    def variant_config_callback(self, tf: TF, msg: TF_Msg):
        # Callback for single fpga config
        if (self._comm_layer.systemAPI.mcu_variant == "TX"):
            self._comm_layer.result = definitions["VariantTXConfiguration_t"].deserialize(msg.data)
        elif (self._comm_layer.systemAPI.mcu_variant == "RX"):
            self._comm_layer.result = definitions["VariantRXConfiguration_t"].deserialize(msg.data)
        return TF.STAY

    ###############################################
    ##                  Sensors                  ##
    ###############################################
    def dump_sensors_flash_configuration(self):
        sensor_register_list = []
        for group_id in range(0, len(SensorName)):
            output = {
                "group_id": group_id
            }

            # Support TX/RX Sensor Names
            if ((group_id == 0) or (group_id == 5)): #NIBB
                sensor_len = len(SensorName[group_id][self._comm_layer.systemAPI.get_mcu_variant()])
            else:
                sensor_len = len(SensorName[group_id])

            for sensor_id in range(0, sensor_len - 1):
                output["sensor_id"] = sensor_id

                # Retry on configuration
                config = None
                for retry in range(0, RETRY_CNT):
                    self._comm_layer.send(MSG_ID_CONFIG_SENSOR_READ_SINGLE, definitions["ReqSensorConfig_t"].serialize(output))
                    time.sleep(0.02)
                    config = self._comm_layer.receive()
                    if ((config["group_id"] == group_id) and (config["sensor_id"] == sensor_id)):
                        break

                if config is None:
                    print("Couldn't get Group ID and Sensor ID")

                # If recieved configuration
                # Support TX/RX Sensor Names
                if ((config["group_id"] == 0) or (config["group_id"] == 5)): #NIBB or Debug
                    sensor_name = SensorName[config["group_id"]][self._comm_layer.systemAPI.get_mcu_variant()][config["sensor_id"]]
                else:
                    sensor_name = SensorName[config["group_id"]][config["sensor_id"]]

                config_data = [GROUP_ID[config["group_id"]],sensor_name, config["config"]["sample_interval"],
                               config["config"]["OD"], config["config"]["UD"], config["config"]["OLO"], config["config"]["ULO"], config["config"]["debounce"], 
                               config["config"]["allowed_tries"], config["config"]["time_interval"], config["config"]["timeout"], config["config"]["active_states"]]
                sensor_register_list.append(config_data)
    
        return sensor_register_list
    
    def load_sensors_flash_configuration(self, variant, file_path):
        df = pd.read_excel(file_path, sheet_name = variant.capitalize() + 'SensorsReady')
        print(f"Loading Variant: {variant.capitalize()}")
        print("Loading Config to MCU RAM")
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            output = {
                "group_id": row_dict["group_id"],
                "sensor_id": row_dict["sensor_id"],
                "config": {k: v for k, v in row_dict.items() if k not in ["group_id", "sensor_id"]}
            }

            for retry in range(0, RETRY_CNT):
                self._comm_layer.send(MSG_ID_CONFIG_SENSOR_SET_SINGLE, definitions["RetSensorConfig_t"].serialize(output))
                time.sleep(0.1)

                #Validate Config
                get_config = {
                    "group_id": output["group_id"],
                    "sensor_id": output["sensor_id"]
                }
                self._comm_layer.send(MSG_ID_CONFIG_SENSOR_READ_SINGLE, definitions["ReqSensorConfig_t"].serialize(get_config))
                time.sleep(0.01)

                read_config = self._comm_layer.receive()
                if (read_config == output):
                    print(f"Group ID: {row_dict['group_id']}, Sensor ID: {row_dict['sensor_id']} - Success")
                    break

        print("Saving RAM to Flash")
        self._comm_layer.sendWithACK(MSG_ID_CONFIG_SAVE, b"1")

    def set_config_callback(self, tf: TF, msg: TF_Msg):
        # Callback for setting config
        self._comm_layer.result = definitions["RetFPGAConfig_t"].deserialize(msg.data)
        
    def single_fpga_config_callback(self, tf: TF, msg: TF_Msg):
        # Callback for single sensor config
        self._comm_layer.result = definitions["RetFPGAConfig_t"].deserialize(msg.data)
        return TF.STAY
    
    def single_sensor_config_callback(self, tf: TF, msg: TF_Msg):
        # Callback for single fpga config
        self._comm_layer.result = definitions["RetSensorConfig_t"].deserialize(msg.data)
        return TF.STAY

    def set_flash_configuration(self):
        # Set flash configuration
        self._comm_layer.send(MSG_ID_CONFIG_SET, b"1")
