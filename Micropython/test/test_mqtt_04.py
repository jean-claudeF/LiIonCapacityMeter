''' This seems to work fine!
Not always though!!!'''

import time, network, socket


ssid = "Katastrophenballungszentrum" 
pwd = "sylvie49.jean-claude56"

def start_wlan():
    # Disable AP!
    ap = network.WLAN(network.AP_IF)
    ap.active(False)    
    
    # Make wlan object
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan_mac = wlan.config('mac')
    print("MAC Address:", wlan_mac)

    return wlan


def connect(wlan, ssid, pwd):
   # Connect wlan to existing WiFi 
   wlan.connect(ssid, pwd)
   cnt =0
   while cnt<10:
     if not wlan.isconnected():
        print("Connecting to ", ssid ,cnt)
        time.sleep(2)
        cnt+=1
     else:
        break
    
   if wlan.isconnected():
      print("Connected to WLAN" )
      print("PicoW IP: ", wlan.ifconfig())
      return True     
   else:
      print('No WiFi')
      return False
#-------------------------------------------------
# Connect to Homeassistant MQTT broker

user = 'jc_mqtt'              # Homeassistant: Settings - People - Users
pwd = "rolasilimqtt"          # Homeassistant: Settings - People - Users

#mqtt_server = '192.168.0.154'  # Homeassistant IP address
mqtt_server = '192.168.0.173'  # PC lab IP address
client_id = 'jc-x'             # May be any string
topic = b'JC'                  # Used in Homeassistant configuration to filter out these messages
port = 1883

def mqtt_connect():
    try:
        client = MQTTClient(client_id, mqtt_server,  user = user, port = port, password = pwd)
        client.connect()
        print('Connected to %s MQTT Broker'%(mqtt_server))
    except:
        print("Could not connect to broker")
        client = None
    return client

def reconnect():
    # Only reconnects if this script is imported from main.py
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def send_messages(client):
    # Send example messages to Homeassistant:
    i=0    
    while True:
        msg = "HELLO JC " + str(i)
        client.publish(topic, msg)
        time.sleep(1)
        print(i)
        i+=1
      
wlan = start_wlan()   
if connect( wlan, ssid, pwd):
    try:
        client = mqtt_connect()
        if client:
            send_messages(client)
    except OSError as e:
        print ("ERROR ", e)
        
    

