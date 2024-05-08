import logging
from websocket_server import WebsocketServer
import time
import ADS1x15 #https://github.com/chandrawi/ADS1x15-ADC/blob/main/examples/ADS_read.py

ADS = ADS1x15.ADS1115(1, 0x48)

ADS.setGain(ADS.PGA_4_096V)
ads_to_voltage0 = 0.0006192
ads_to_voltage1 = 0.000625
ads_to_voltage2 = 0.000625
ads_to_voltage3 = 0.0006225
def adc_read_voltage():
    val_0 = ADS.readADC(0)
    val_1 = ADS.readADC(1)
    val_2 = ADS.readADC(2)
    val_3 = ADS.readADC(3)

    analog_voltage = {
        "BATTERY_VOLTAGE_CELL0:": round(val_0*ads_to_voltage0, 2),
        "BATTERY_VOLTAGE_CELL1:": round(val_1*ads_to_voltage1, 2),
        "BATTERY_VOLTAGE_CELL2:": round(val_2*ads_to_voltage2, 2),
        "BATTERY_VOLTAGE_CELL3:": round(val_3*ads_to_voltage3, 2)
    }
    return analog_voltage

def new_client(client, server):
    server.send_message_to_all("Hey all, a new client has joined us")

def message_received(client, server, message):
    print("Received message from client {}: {}".format(client['id'], message))
    # Gjør ønsket behandling av den mottatte meldingen her
    if message == "CHARGING_PLATE_ON":
        print ("plate is on")
    elif message == 'BATTERY_STATS':
        server.send_message_to_all("rasbat")
        analog_voltage = adc_read_voltage()
        for key, i in analog_voltage.items():
            server.send_message_to_all(key + str(i)) 
 

    elif message == "CHARGING_PLATE_OFF":
        server.send_message_to_all("ras_say_the_plate_is_off")
        print ("plate is off")

def send_message(server, message):
    server.send_message_to_all(message)


def run_server():
    server = WebsocketServer(host='192.168.0.166', port=8765, loglevel=logging.INFO) #raspberry pi 3 = 192.168.1.169
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(message_received)
    server.run_forever()

server = run_server()