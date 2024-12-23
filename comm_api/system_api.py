from payload_parser import TF_Msg, TF
from sensors_name import *
from messages import *
import pycstruct

__author__ = "Itamar Eliakim / CaPow Technologies LTD"
__maintainer__ = "Itamar Eliakim"
__email__ = "itamar@rootiebot.com"

definitions = pycstruct.parse_file('messages.h')

class CommSystemModuleAPI():
    def __init__(self, comm_layer, logger_gui):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui

        self.mcu_variant = "TX"
        self.app_version = None
        self.bl_version = None

        self.fpga_variant = None
        self.fpga_version = None

        self.operation_mode = None

    def app_version_callback(self, tf: TF, msg: TF_Msg):
        # Callback for version
        result = definitions["versionData_t"].deserialize(msg.data)
        self.fpga_version = f"{(result['fpga_ver']['major'])}"
        self.app_version = f"{result['mcu_ver']['major']}.{result['mcu_ver']['minor']}.{result['mcu_ver']['patch']}"
        self.bl_version = f"{result['bootloader_ver']['major']}.{result['bootloader_ver']['minor']}.{result['bootloader_ver']['patch']}"

        fpga_version_str = f"FPGA Version: {self.fpga_version}"
        app_version_str = f"MCU Version: {self.app_version}"
        bl_version_str = f"BL Version: {self.bl_version}"

        self._comm_layer.result = fpga_version_str + "\n" + app_version_str + "\n" +bl_version_str
        self._logger_gui.log(fpga_version_str + ", " + app_version_str + ", " + bl_version_str)
        return TF.STAY

    def variant_callback(self, tf: TF, msg: TF_Msg):
        # Callback for variant
        result = definitions["variantData_t"].deserialize(msg.data)

        # If no response
        if (result['fpga_variant'] == 0):
            return TF.STAY
        
        self.fpga_variant = FPGA_VARIANT[result['fpga_variant']]
        self.mcu_variant = MCU_VARIANT[result['mcu_variant']]

        fpga_variant_str = f"FPGA Variant: {self.fpga_variant}"
        mcu_variant_str = f"MCU Variant: {self.mcu_variant}"
        self._comm_layer.result = fpga_variant_str + "\n" + mcu_variant_str
        self._logger_gui.log(fpga_variant_str + ", " + mcu_variant_str)
        return TF.STAY

    def operation_mode_callback(self, tf: TF, msg: TF_Msg):
        # Callback for Operation Mode
        result = definitions["retOperationMode_t"].deserialize(msg.data)
        self.operation_mode = result["mode"]
        self._logger_gui.log(f"Operation Mode: {OPERATION_MODES[self.operation_mode]}")
        return TF.STAY
    
    def get_mcu_variant(self):
        # Get Variant
        if (self.mcu_variant is None):
            return ""
        
        return self.mcu_variant
    
    def get_app_version(self):
        # Get MCU Version
        return self.app_version
    
    def get_fpga_variant(self):
        if (self.fpga_variant is None):
            return ""

        return self.fpga_variant
    
    def get_fpga_version(self):
        # Get FPGA Version
        return self.fpga_version
    
    def get_operation_mode(self):
        # Get Operation Mode
        return self.operation_mode
    
    def get_bl_version(self):
        # Get Bootloader Version
        return self.bl_version
