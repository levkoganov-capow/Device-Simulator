#!/usr/bin/env python
# from sensors_name import *
from messages import *
# import pycstruct
import socket
import psutil
import time

__author__ = "Itamar Eliakim / CaPow Technologies LTD"
__maintainer__ = "Itamar Eliakim"
__email__ = "itamar@rootiebot.com"

# definitions = pycstruct.parse_file('messages.h')

class CommUDPAPI():

    def __init__(self, comm_layer, esp32_id = None, esp32_ip = None, esp32_variant = None) -> None:
        self._comm_layer = comm_layer

        if (esp32_variant == "RX"):
            self.UDP_BROADCAST_PORT = 8080
            self.UDP_ESP32_PORT = 8081
            self.UDP_PYTHON_PORT = 8082
        elif (esp32_variant == "TX"):
            self.UDP_BROADCAST_PORT = 9080
            self.UDP_ESP32_PORT = 9081
            self.UDP_PYTHON_PORT = 9082

        self.esp32_id = esp32_id
        self.esp32_ip = esp32_ip
        self.esp32_variant = esp32_variant

        self.close_port(self.UDP_BROADCAST_PORT)
        self.close_port(self.UDP_ESP32_PORT)
        self.close_port(self.UDP_PYTHON_PORT)

        self.in_pairing = True

        self.initUDPClient()
        self.initUDPServer()

        if (self.esp32_ip is None):
            print("Please Put ESP in Pairing Mode")
            self.udp_pairing()
        else:
            exit_pairing_start_time = time.time()
            self.udp_client.sendto(str(self.esp32_id).encode(), (self.esp32_ip, self.UDP_ESP32_PORT))
            
             # check if esp exit from pairing mode
            counter = 0
            data = {}

            while True:
                line = self.parse_udp_data()
                if line:
                    split_line = line.split('|')
                    if (int(split_line[1], 16) == self.esp32_id):
                        counter += 1

                    if(counter > 3):
                        #Tell ESP32 to exit from pairing mode
                        self.udp_client.sendto(str(self.esp32_id).encode(), (self.esp32_ip, self.UDP_ESP32_PORT))
                        print("Retry to send ESP exit paring mode")
                        counter = 0
                        exit_pairing_start_time = time.time()

                if (time.time() - exit_pairing_start_time > 3):
                    break
                
            self.in_pairing = False

    def read(self):
        try:
            data = self.udp_server.recvfrom(1024)
            return data[0]
        except socket.timeout:
            # self._comm_layer._logger_gui.log("UDP Socket Timeout! Restart UDP Socket")
            self.initUDPServer()
        return b''
    
    def initUDPClient(self , timeout = 5):
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_client.setblocking(1)
        self.udp_client.settimeout(timeout)
        self.udp_client.bind(('192.168.90.8', self.UDP_BROADCAST_PORT))
        
        print(f"Listening for responses on {'192.168.90.8'}:{self.UDP_BROADCAST_PORT}...")
        self.initBroadcast(self.udp_client)
    
    def initUDPServer(self):
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server.settimeout(10.0)
        self.udp_server.bind(("0.0.0.0", self.UDP_PYTHON_PORT))

    # Modify
    def initBroadcast(self, client):
        message = f"CaPow|0x45|192.168.90.5"
        client.sendto(message.encode(), ("255.255.255.255", 8080))
        print("Broadcast message sent to 255.255.255.255:8080")

    def reconnect_udp(self):
        self.udp_client.sendto(str(self.esp32_id).encode(), (self.esp32_ip, self.UDP_ESP32_PORT))

    def close_port(self, port_number):
        for proc in psutil.process_iter():
            try:
                connections = proc.connections(kind='inet')
                for conn in connections:
                    if conn.laddr.port == port_number:
                        proc.kill()
                        print(f"Process with PID {proc.pid} closed the port {port_number}.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                 
    def parse_udp_data(self):
        try:
            data, addr = self.udp_client.recvfrom(1024)
            print("parse_udp_data")
            return data.decode()
        except socket.error:
            return None
        
    def udp_pairing(self):
        data = {}
        while True:
            #TODO: Timeout?
            line = self.parse_udp_data()
            if line:
                split_line = line.split('|')
                if (int(split_line[1], 16) == self.esp32_id):
                    data["id"] = split_line[1]
                    data["ip"] = split_line[2]
                    break

        #Tell ESP32 to exit from pairing mode
        exit_pairing_start_time = time.time()
        self.udp_client.sendto(data["id"].encode(), (data["ip"], self.UDP_ESP32_PORT))
        print("Try to Pairing ESP")


        # check if esp exit from pairing mode
        counter = 0
        while True:
            line = self.parse_udp_data()
            if line:
                split_line = line.split('|')
                if (int(split_line[1], 16) == self.esp32_id):
                    counter += 1

                if(counter > 3):
                    #Tell ESP32 to exit from pairing mode
                    self.udp_client.sendto(data["id"].encode(), (data["ip"], self.UDP_ESP32_PORT))
                    print("Retry to pairing ESP")
                    counter = 0
                    exit_pairing_start_time = time.time()

            if (time.time() - exit_pairing_start_time > 3):
                break
        
        self.esp32_ip = data["ip"]
        self.in_pairing = False
        print(f"Done Pairing! IP: {data['ip']} ID: {data['id']}")
        self._comm_layer._logger_gui.log(f"Done Pairing! IP: {data['ip']} ID: {data['id']}")
        return True
    
    def is_pairing(self):
        return self.in_pairing
    
    def get_esp32_ip(self):
        # Get IP address
        return self.esp32_ip

    def get_esp32_id(self):
        # Get IP address
        return self.esp32_id
