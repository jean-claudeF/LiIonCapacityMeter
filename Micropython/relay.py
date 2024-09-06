from machine import Pin
import time

sw_on = Pin(13, Pin.OUT)
sw_off = [ Pin(12, Pin.OUT),  Pin(11, Pin.OUT), Pin(10, Pin.OUT)]

#--------------------------------------------------
def switch_all_off():
    for sw in sw_off:
        sw.value(1)
    time.sleep_ms(100)
    for sw in sw_off:
        sw.value (0)
    
    
def switch_off(channel):
    sw_off[channel].value(1)
    time.sleep_ms(100)
    sw_off[channel].value(0)

#..........................................
def switch_all_on():
    sw_on.value(1)
    time.sleep_ms(100)
    sw_on.value(0)

