#!/usr/bin/env python
from payload_parser import TF_Msg, TF
from sensors_name import *
from messages import *
import pycstruct
import os
import base64
from .crc16 import crc16_table

definitions = pycstruct.parse_file('messages.h')

class FirmwareInfo():
    def __init__(self, filename, size, chunks, chunk_size, crc) -> None:
        self.filename = filename
        self.size = size
        self.chunks = chunks
        self.chunk_size = chunk_size
        self.crc = crc

class FirmwareAPI():
    MAX_SIZE = 130000#122880
    CHUNK_SIZE = 200
    def __init__(self, comm_layer, logger_gui = None):
        self._comm_layer = comm_layer
        self._logger_gui = logger_gui
        self.chunk_id = 0
        self.num_of_chunks = None

        self._firmware_info = None

        self._in_firmware_upgrade = False
        

    def loadBin(self, filename):
        if os.path.exists(filename):
            file_type = os.path.splitext(filename)
            
            if file_type[1] != ".bin":
                print(f"{filename} should be .bin file")
                return False

            file_size = os.path.getsize(filename)
            with open(filename, 'rb') as file:
                data = file.read(file_size)
                crc = self.calculate_crc16_all(bytearray(data))
                chunks = int(file_size / self.CHUNK_SIZE)
                if ((file_size % self.CHUNK_SIZE) > 0):
                    chunks += 1

                if (file_size > self.MAX_SIZE):
                    print("Failed. FW Size is Too Large!")
                    self._logger_gui.log(f"Failed. FW Size is Too Large!")
                    return False
                
                self._firmware_info = FirmwareInfo(filename, file_size, chunks, self.CHUNK_SIZE, crc)
                self._logger_gui.log(f"The size of '{self._firmware_info.filename}' is {self._firmware_info.size} bytes.")
                print(f"The size of '{self._firmware_info.filename}' is {self._firmware_info.size} bytes.")
                self._logger_gui.log(f"Num of chunks: {self._firmware_info.chunks}. Checksum: {self._firmware_info.crc}")
                print(f"Num of chunks: {self._firmware_info.chunks}. Checksum: {self._firmware_info.crc}")
                self.num_of_chunks = self._firmware_info.chunks
                return True
            
        print(f"'{filename}' does not exist.")
        return False

    def calculate_crc16_all(self, data):
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ crc16_table[(crc ^ byte) & 0xFF]
        return crc
             
    def calculate_crc16(self, data):
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ crc16_table[(crc ^ byte) & 0xFF]
        return crc

    def chunk_request_callback(self, tf: TF, msg: TF_Msg):
        if (self._in_firmware_upgrade):
            self.chunk_id = definitions["reqFirmwareChunk_t"].deserialize(msg.data)["chunk_id"]
            # print(f"Request ChunkID: {self.chunk_id} | Total Chunks: {self._firmware_info.chunks}")

            chunk_data = self.get_firmware_chunk(self.chunk_id, self.CHUNK_SIZE)
            if (len(chunk_data) < self.CHUNK_SIZE):
                empty_byte_array = b'\x00' * 200
                chunk_data = (chunk_data + empty_byte_array[:200 - len(chunk_data)])[:200]

            #hex_array = [hex(byte) for byte in chunk_data]
            #print(hex_array)
            #print(len(chunk_data), chunk_data)
            output = {}
            output["chunk"] = self.chunk_id
            output["tchunk"] = self._firmware_info.chunks
            output["crc"] = self.calculate_crc16(bytearray(chunk_data))
            output["data"] = chunk_data
            self._comm_layer.send(MSG_ID_BOOTLOADER_CHUNK_DATA, definitions["FirmwareChunk_t"].serialize(output))
    
    def info_request_callback(self, tf: TF, msg: TF_Msg):
        if (self._in_firmware_upgrade):
            if os.path.exists(self._firmware_info.filename):
                output = {}
                version = self._firmware_info.filename.split("_")[-1].split(".")
                output["version"] = {"major": int(version[0]), "minor": int(version[1]), "patch": int(version[2])}
                output["chunks_num"] = self._firmware_info.chunks
                output["size"] = self._firmware_info.size
                output["crc"] = self._firmware_info.crc
                self._comm_layer.send(MSG_ID_BOOTLOADER_INFO_DATA, definitions["FirmwareInfo_t"].serialize(output))
            else:
                print(f"'{self._firmware_info.filename}' does not exist.")
                self._logger_gui.log(f"'{self._firmware_info.filename}' does not exist.")

    def start_firmware_upgrade(self, filename):
        if (self.loadBin(filename)):
            self._in_firmware_upgrade = True
            return True
        return False
    
    def get_firmware_chunk(self, chunk_id, chunk_size = 100):
        if (self._in_firmware_upgrade):
            if os.path.exists(self._firmware_info.filename):
                with open(self._firmware_info.filename, 'rb') as file:
                    file.seek(chunk_id * chunk_size)
                    data = file.read(chunk_size)
                    if data:
                        return data
                    else:
                        print(f"Chunk {chunk_id} does not exist.")
                        self._logger_gui.log(f"Chunk {chunk_id} does not exist.")
            else:
                print(f"'{self._firmware_info.filename}' does not exist.")
                self._logger_gui.log(f"'{self._firmware_info.filename}' does not exist.")
