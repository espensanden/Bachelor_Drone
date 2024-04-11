import logging
from websocket_server import WebsocketServer
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
while True:
    try:
        server = WebsocketServer(host='192.168.1.169', port=8765, loglevel=logging.INFO)
        server.set_fn_new_client(new_client)
        server.set_fn_message_received(message_received)
        server.run_forever()
    except KeyboardInterrupt:
        server.server_close()
        server.server_close()
        break