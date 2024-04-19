import logging
from websocket_server import WebsocketServer
import time
import ADS1x15 #https://github.com/chandrawi/ADS1x15-ADC/blob/main/examples/ADS_read.py
import threading 

ADS = ADS1x15.ADS1115(1, 0x48)

ADS.setGain(ADS.PGA_4_096V)
ads_to_voltage = 0.000621

def new_client(client, server):
    server.send_message_to_all("Hey all, a new client has joined us")
def message_received(client, server, message):
    print("Received message from client {}: {}".format(client['id'], message))
    # Gjør ønsket behandling av den mottatte meldingen her
    if message == "CHARGING_PLATE_ON":
        print ("plate is on")
        
    elif message == "CHARGING_PLATE_OFF":
        server.send_message_to_all("ras_say_the_plate_is_off")
        print ("plate is off")
def send_message(server, message):
    server.send_message_to_all(message)

def adc_read_voltage():
    val_0 = ADS.readADC(0)
    val_1 = ADS.readADC(1)
    val_2 = ADS.readADC(2)
    val_3 = ADS.readADC(3)

    analog_voltage = {
        "Analog0:": round(val_0*ads_to_voltage, 1),
        "Analog1:": round(val_1*ads_to_voltage, 1),
        "Analog2:": round(val_2*ads_to_voltage, 1),
        "Analog3:": round(val_3*ads_to_voltage, 1)
    }
    return analog_voltage
 


def run_server():
    server = WebsocketServer(host='192.168.1.169', port=8765, loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(message_received)
    server.run_forever()
    return server

server = run_server()


#server_thread = threading.Thread(target = run_server)
#server_thread.daemon = True
#server_thread.start()

while True:
    
    #time.sleep(1)
    #analog_voltage = adc_read_voltage()
    #print(analog_voltage)
    #if time.time() % 10 == 0:
    send_message(server, "hi")
    print("hi")