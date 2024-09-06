from machine import Pin
import time

ch0 = Pin(10, Pin.OUT)
ch1 = Pin(11, Pin.OUT)
ch2 = Pin(12, Pin.OUT)
channels = [ch0, ch1, ch2]

def switch_on(i):
    channels[i].value(1)
    
def switch_off(i):
    channels[i].value(0)    

def switch_all_off():
    for i in [0, 1, 2]:
        switch_off(i)
        
def switch_all_on():
    for i in [0, 1, 2]:
        switch_on(i)
    
