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
      print("Connected" )
      print("PicoW IP: ", wlan.ifconfig())
           
   else:
      print('No WiFi')
      

def test():
    
      addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
      s = socket.socket()
      s.connect(addr)
      s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
      data = s.recv(1000)
      print(data[:80])
      s.close()         # don't forget to close the socket
      wlan.disconnect()  # and disconnect from WiFi
      
wlan = start_wlan()   
connect( wlan, ssid, pwd)
test()
