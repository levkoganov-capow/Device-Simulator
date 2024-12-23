#!/usr/bin/env python
from payload_parser import TF_Msg, TF
from sensors_name import *
from messages import *
import pycstruct

definitions = pycstruct.parse_file('messages.h')
MCU_TIMEOUT = 3.0
RETRY_CNT = 50

class CommFlashLoggerAPI():
    def __init__(self, comm_layer, logger_gui = None):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui
        self._last_chunk = {}
        self._sd_last_chunk = {}
        self._sd_num_of_chunks = 0

    def logger_chunk_callback(self, tf: TF, msg: TF_Msg):
        self._last_chunk = definitions["FlashLoggerChunk_t"].deserialize(msg.data)

    def get_last_chunk(self):
        return self._last_chunk

    def sd_logger_num_of_chunks_callback(self, tf: TF, msg: TF_Msg):
        self._sd_num_of_chunks = definitions["reqSdLoggerNumOfChunks_t"].deserialize(msg.data)

    def sd_logger_get_num_of_chunk(self):
        return self._sd_num_of_chunks

    def sd_logger_chunk_callback(self, tf: TF, msg: TF_Msg):
        self._sd_last_chunk = definitions["SdLoggerChunk_t"].deserialize(msg.data)

    def sd_logger_get_chunk(self):
        return self._sd_last_chunk
   
