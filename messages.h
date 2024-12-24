#include <stdint.h>

typedef struct {
	uint16_t sample_interval;
	int16_t OD;
	int16_t UD;
	int16_t OLO;
	int16_t ULO;
	uint8_t debounce;
	int16_t allowed_tries;
	uint16_t time_interval;
	int16_t timeout;
	uint8_t active_states;
}SensorConfig_t;

typedef struct {
	int32_t value;
	uint8_t status;
	uint8_t peripheral_state;
	uint8_t group_id;
	uint8_t sensor_id;
	uint8_t retry_cnt;
	uint8_t active_in_state;
}SensorDataShortOut_t;

typedef struct {
	SensorConfig_t config;
	int32_t value;
	uint8_t status;
	uint8_t peripheral_state;
	uint8_t group_id;
	uint8_t sensor_id;
	uint8_t retry_cnt;
	uint8_t active_in_state;
}SensorDataLongOut_t;

typedef struct {
	uint8_t group_id;
	uint8_t sensor_id;
	uint8_t status;
	uint16_t bit;
	uint8_t tries;
	int32_t time_interval;
}FPGAProtectBitDataOut_t;

//FPGA Register Config
typedef struct {
	uint16_t id;
}ReqFPGAConfig_t;

typedef struct {
	uint16_t id;
	uint16_t reg;
	uint16_t value;
}RetFPGAConfig_t;

//Sensor Register Config
typedef struct {
	uint8_t group_id;
	uint8_t sensor_id;
}ReqSensorConfig_t;

typedef struct {
	SensorConfig_t config;
	uint8_t group_id;
	uint8_t sensor_id;
}RetSensorConfig_t;

typedef struct {
	SensorConfig_t NIBB_SENSORS[25];
	SensorConfig_t INVERTER_SENSORS[7];
	SensorConfig_t RESONATOR_SENSORS[2];
	SensorConfig_t RECTIFIER_SENSORS[8];
	SensorConfig_t MB_SENSORS[9];
	SensorConfig_t DEBUG_SENSORS[9];
}SensorsConfiguration_t;

typedef struct {
	uint16_t V_ref;			//Target voltage
	uint16_t V_target;		//Intermediate reference voltage to create ramp up
	uint16_t DV;			//Voltage Step
	uint16_t V_supply;		//NIBB supply voltage
	uint16_t V_load;		//NIBB load voltage
}NibbConfiguration_t;

typedef struct {
	uint8_t group_id;
	uint8_t sensor_id;
	uint16_t id;
	int32_t value;
}sensorCommand_t;

//System
typedef struct {
	uint8_t major;
	uint8_t minor;
	uint8_t patch;
}SWVersion_t;

typedef struct {
	SWVersion_t mcu_ver;
	SWVersion_t fpga_ver;
	SWVersion_t bootloader_ver;
}versionData_t;

typedef struct {
	uint8_t fpga_variant;
	uint8_t mcu_variant;
}variantData_t;

typedef struct {
	uint16_t mode_state;
	uint16_t work_state;
	uint16_t developer_state;
}stateMachineInfo_t;

typedef struct {
	uint16_t type;
	uint16_t event;
}stateMachineEvent_t;

typedef struct {
	uint8_t cmd;
	uint8_t group_id;
}reqSensorStream_t;

typedef struct {
	uint8_t group_id;
	uint8_t sensor_id;
	uint16_t status;
	int32_t value;
}SensorFault_t;

typedef struct {
	uint8_t val;
}StandardCmd_t;

//System UI
typedef struct {
	uint16_t id;
	uint16_t type;
}ACKCmd_t;

typedef struct {
	uint8_t id;
}TaskWarning_t;

typedef struct {
	uint8_t id;
}DebugNotification_t;

typedef struct {
	uint16_t PILOT_VHV_REF;
	uint16_t NOMINAL_VHV_REF;
	uint16_t MIN_IHV_CLIENT;
	uint16_t SHUTDOWN_IHV;
	uint16_t PILOT_TIMEOUT;
	uint16_t RAMP_UP_TIMEOUT;
	uint16_t CLOSE_PHASE_TIMEOUT;
	uint16_t INV_VHV_POWEROFF;
	uint16_t CLOSE_PHASE_THRESH;
	uint16_t NOMINAL_THRESH;
	uint16_t HGH_PWR_IHV;
	uint16_t ENTRY_STANDBY_DELAY;
	uint16_t ENTRY_PILOT_DELAY;
	uint16_t ENTRY_RAMP_UP_DELAY;
	uint16_t ENTRY_CLOSE_PHASE_DELAY;
	uint16_t ENTRY_NOMINAL_DELAY;
	uint16_t DBNC_NOMINAL;
	uint16_t DBNC_PILOT;
	uint16_t SEARCH_INTERVAL;
	uint16_t AUTO_WORK;
	uint32_t DBNC_BADLOAD;
	uint16_t BADLOAD_IHV;
	uint16_t ENTRY_BADLOAD_DELAY;
	uint32_t BADLOAD_TIMEOUT;
	uint16_t TIMEOUT_RECOVER;
	uint16_t NO_BADLOAD_IHV;
	uint8_t FAN1_FEEDBACK_EN;
	uint8_t FAN2_FEEDBACK_EN;
	int16_t FAN_RETRIES;
	uint16_t FAN_RETRY_INTERVAL;
	uint16_t CLOSE_PHASE_DBNC;
	uint16_t RAMP_UP_DBNC;
	uint32_t NOMINAL_2_BADLOAD_DBNC;
	int16_t FPGA_NIBB_IL_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_IL_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_IHV_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_IHV_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_ILV_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_ILV_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_VHV_Overvoltage_RETRIES;
	int16_t FPGA_NIBB_VHV_Undervoltage_RETRIES;
	int16_t FPGA_NIBB_VLV_Overvoltage_RETRIES;
	int16_t FPGA_NIBB_VLV_Undervoltage_RETRIES;
	int16_t FPGA_NIBB_IL_OCP_POS_RETRIES;
	int16_t FPGA_NIBB_IL_OCP_NEG_RETRIES;
	int16_t FPGA_NIBB_HW_RETRIES;
	uint16_t FPGA_NIBB_IL_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_IL_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_IHV_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_IHV_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_ILV_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_ILV_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_VHV_Overvoltage_INTERVAL;
	uint16_t FPGA_NIBB_VHV_Undervoltage_INTERVAL;
	uint16_t FPGA_NIBB_VLV_Overvoltage_INTERVAL;
	uint16_t FPGA_NIBB_VLV_Undervoltage_INTERVAL;
	uint16_t FPGA_NIBB_IL_OCP_POS_INTERVAL;
	uint16_t FPGA_NIBB_IL_OCP_NEG_INTERVAL;
	uint16_t FPGA_NIBB_HW_INTERVAL;
	int16_t FPGA_INV_OCP_RETRIES;
	uint16_t FPGA_INV_OCP_INTERVAL;
	int16_t FPGA_INV_EXT_FREQ_RETRIES;
	uint16_t FPGA_INV_EXT_FREQ_INTERVAL;
	int16_t FPGA_INV_FORCE_SHUTDOWN_RETRIES;
	uint16_t FPGA_INV_FORCE_SHUTDOWN_INTERVAL;
	int16_t FPGA_INV_HW_RETRIES;
	uint16_t FPGA_INV_HW_INTERVAL;
	int16_t FPGA_PD_HARD_SWITCH_RETRIES;
	uint16_t FPGA_PD_HARD_SWITCH_INTERVAL;
	int16_t FPGA_PD_SOFT_SWITCH_RETRIES;
	uint16_t FPGA_PD_SOFT_SWITCH_INTERVAL;
	int16_t FPGA_PD_BIAS_FORCE_SHUTDOWN_RETRIES;
	uint16_t FPGA_PD_BIAS_FORCE_SHUTDOWN_INTERVAL;
	uint16_t PILOT_T2D_MIN;
	uint16_t PILOT_T2D_MAX;
	uint16_t T2D_MIN;
	uint16_t T2D_MAX;
	uint16_t T2D_DBNC;
}VariantTXConfiguration_t;

typedef struct {
	uint16_t MONITOR_VHV_REF;
	uint16_t ACTIVE_VHV_REF;
	uint16_t ILV_CURRENT_LIMIT;
	uint16_t DISCHARGE_VHV_REF;
	uint16_t DISCHARGE_VHV_THRESH;
	uint16_t MONITOR_VHV_THRESH;
	uint16_t DISCHARGE_TIMEOUT;
	uint16_t ACTIVE_IHV_THRESH;
	uint16_t DISCHARGE_IHV_THRESH;
	uint16_t MONITOR_2_DISCHARGE_DBNC;
	uint16_t MONITOR_2_ACTIVE_DBNC;
	uint16_t ACTIVE_DBNC;
	uint16_t DSCHRG_DBNC;
	uint16_t ENTRY_MONITOR_DELAY;
	uint16_t ENTRY_ACTIVE_DELAY;
	uint16_t ENTRY_DISCHARGE_DELAY;
	uint16_t AUTO_WORK;
	uint16_t TIMEOUT_RECOVER;
	uint8_t SPOOFER_ENABLE;
	int16_t SPOOFER_RETRIES;
	uint16_t SPOOFER_RETRY_INTERVAL;
	uint8_t FAN1_FEEDBACK_EN;
	uint8_t FAN2_FEEDBACK_EN;
	int16_t FAN_RETRIES;
	uint16_t FAN_RETRY_INTERVAL;
	uint16_t STANDBY_DISCHARGE_TIMEOUT;
	uint16_t DISABLED_DISCHARGE_TIMEOUT;
	int16_t FPGA_NIBB_IL_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_IL_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_IHV_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_IHV_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_ILV_Overcurrent_RETRIES;
	int16_t FPGA_NIBB_ILV_Undercurrent_RETRIES;
	int16_t FPGA_NIBB_VHV_Overvoltage_RETRIES;
	int16_t FPGA_NIBB_VHV_Undervoltage_RETRIES;
	int16_t FPGA_NIBB_VLV_Overvoltage_RETRIES;
	int16_t FPGA_NIBB_VLV_Undervoltage_RETRIES;
	int16_t FPGA_NIBB_IL_OCP_POS_RETRIES;
	int16_t FPGA_NIBB_IL_OCP_NEG_RETRIES;
	int16_t FPGA_NIBB_HW_RETRIES;
	uint16_t FPGA_NIBB_IL_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_IL_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_IHV_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_IHV_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_ILV_Overcurrent_INTERVAL;
	uint16_t FPGA_NIBB_ILV_Undercurrent_INTERVAL;
	uint16_t FPGA_NIBB_VHV_Overvoltage_INTERVAL;
	uint16_t FPGA_NIBB_VHV_Undervoltage_INTERVAL;
	uint16_t FPGA_NIBB_VLV_Overvoltage_INTERVAL;
	uint16_t FPGA_NIBB_VLV_Undervoltage_INTERVAL;
	uint16_t FPGA_NIBB_IL_OCP_POS_INTERVAL;
	uint16_t FPGA_NIBB_IL_OCP_NEG_INTERVAL;
	uint16_t FPGA_NIBB_HW_INTERVAL;
	int16_t FPGA_RECT_HW_SHUTDOWN_RETRIES;
	uint16_t FPGA_RECT_HW_SHUTDOWN_INTERVAL;
	int16_t FPGA_RECT_RELAY_SC_RETRIES;
	uint16_t FPGA_RECT_RELAY_SC_INTERVAL;
	int16_t FPGA_RECT_HW_RETRIES;
	uint16_t FPGA_RECT_HW_INTERVAL;
	int16_t FPGA_POWER_LIMITER_MAX_REACHED_RETRIES;
	uint16_t FPGA_POWER_LIMITER_MAX_REACHED_INTERVAL;
}VariantRXConfiguration_t;

//Flash Logger
typedef struct{
	uint16_t chunk;
	uint16_t tchunk;
	char data[100];
}FlashLoggerChunk_t;

typedef struct {
	uint16_t chunk;
	uint8_t state;
}reqFlashLoggerChunk_t;

//SD Logger
typedef struct{
	uint16_t chunk;
	char data[128];
}SdLoggerChunk_t;

typedef struct {
	uint16_t chunk;
	uint8_t state;
}reqSdLoggerChunk_t;

typedef struct {
	uint16_t num_of_chunks;
}reqSdLoggerNumOfChunks_t;

typedef struct {
	int32_t vlv;
	uint32_t vlv_timestamp;
	int32_t ilv;
	uint32_t ilv_timestamp;
	uint8_t health_status;
	uint16_t state_machine_mode_state;
	uint16_t state_machine_current_state;
}retEnergyCalculation_t;

//Firmware Over-the-Air (OTA)
typedef struct {
	uint16_t cmd;
}reqFirmwareInfo_t;

typedef struct {
	SWVersion_t version;
	uint16_t chunks_num;
	uint32_t size;
	uint16_t crc;
}FirmwareInfo_t;

typedef struct {
	uint16_t chunk_id;
}reqFirmwareChunk_t;

typedef struct {
	char data[200];
}FirmwareChunkData_t;

typedef struct {
	uint16_t chunk;
	uint16_t tchunk;
	uint16_t crc;
	uint8_t data[200];
}FirmwareChunk_t;

typedef struct {
	uint16_t mode;
}retOperationMode_t;
