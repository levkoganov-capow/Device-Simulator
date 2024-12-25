import threading
import socket
import time
import queue
from board_comm import BoardComm
from constants import *
from messages import *

message_queue = queue.Queue()
stop_event = threading.Event()

class MsgIDs:
    MSG_ID_OPERATION_MODE_TRANSMIT = MSG_ID_OPERATION_MODE_TRANSMIT
    MSG_ID_VARIANT_GET = MSG_ID_VARIANT_GET
    MSG_ID_APPLICATION_VERSION_GET = MSG_ID_APPLICATION_VERSION_GET
    MSG_ID_UI_KEEP_ALIVE = MSG_ID_UI_KEEP_ALIVE
    MSG_ID_WHITE_LOG_RESPONSE = MSG_ID_WHITE_LOG_RESPONSE
    MSG_ID_ENERGY_CALCULATION_GET = MSG_ID_ENERGY_CALCULATION_GET

# Create the UDP socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((LOCAL_IP, LOCAL_PORT))
    board_comm = BoardComm(message_queue, sock)
    device_msg = f"CaPow|0x45|{LOCAL_IP}"
    IsParing = True

    def send_broadcast(address, port):
        while not stop_event.is_set():            
            try:
                sock.sendto(device_msg.encode(), (address, port))
                print(f"Broadcast message sent to {address}:{port}")
                time.sleep(5)
            except Exception as e:
                print(f"Error in broadcast: {e}")

    def read_data_from_device(device_ip, port):
        global IsParing

        print(f"Listening on {device_ip}:{port}")

        while True:
            try:
                data, addr = sock.recvfrom(1024)

                if IsParing:
                    decoded_data = data.decode()
                    print(f"Data received from {addr}: {decoded_data}")                    
                    stop_event.set()  # Stop sending Broadcast
                    message_queue.put(decoded_data)

                else:
                    board_comm._tf.accept(data)

            except Exception as e:
                print(f"Error receiving data: {e}")

    def send_data_to_device(device_ip, port):
        global IsParing
        print(f"Preparing to send data to {device_ip}:{port}")

        while True:
            try:
                message = message_queue.get(timeout=1)  # Timeout avoids indefinite blocking

                if IsParing:
                    ack_msg = f"{device_msg}|ACK"
                    sock.sendto(ack_msg.encode(), (device_ip, port))
                    print(f"ACK message sent to {device_ip}:{port}")
                    IsParing = False

                else:

                    match message:
                        case MsgIDs.MSG_ID_OPERATION_MODE_TRANSMIT:
                            board_comm.sendOperationMode()
                            print("Case 1: Sending 201")
                        case MsgIDs.MSG_ID_VARIANT_GET:
                            board_comm.sendVariant()
                            print("Case 2: Sending 41")
                        case MsgIDs.MSG_ID_APPLICATION_VERSION_GET:
                            board_comm.sendApplicationVersion()
                            print("Case 3: Sending 42")
                        case MsgIDs.MSG_ID_UI_KEEP_ALIVE:
                            board_comm.sendKeepAlive()
                            print("Case 4: Sending 47")
                        case MsgIDs.MSG_ID_WHITE_LOG_RESPONSE:
                            board_comm.sendWhiteLog()
                            print("Case 5: Sending 53")
                        case MsgIDs.MSG_ID_ENERGY_CALCULATION_GET:
                            board_comm.sendEnergyCalculation()
                            print("Case 6: Sending 61")
                        case _:
                            print("Default case executed")

            except queue.Empty:
                pass  
            except Exception as e:
                print(f"Error sending data: {e}")

    def main():
        broadcast_thread = threading.Thread(target=send_broadcast, args=(BROADCAST_ADDRESS, BROADCAST_PORT), daemon=True)
        read_thread = threading.Thread(target=read_data_from_device, args=(LOCAL_IP, LOCAL_PORT), daemon=True)
        send_thread = threading.Thread(target=send_data_to_device, args=(TARGET_IP, TARGET_PORT), daemon=True)
        
        broadcast_thread.start()
        read_thread.start()
        send_thread.start()

        broadcast_thread.join()
        read_thread.join()
        send_thread.join()

    if __name__ == "__main__":
        main()