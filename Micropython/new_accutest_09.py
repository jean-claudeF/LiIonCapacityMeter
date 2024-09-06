'''
Discharge 1-3 LiIon accus and log the voltage values
Begin discharging at button push
Switch off discharging for individual cell when the voltage drops below threshold
Values are written to the internal storage: filename = 'LiIon.dat'
and output through USB serial and UART(0)_TX
'''
import os
import time
from machine import Pin, I2C, ADC, Timer, UART
from ssd1306 import SSD1306_I2C
from mosfet import *
#-------------------------------------------------------------------
filename = 'LiIon.dat'
baudrate_TX = 38400
threshold = 3
Rload = [3.336, 3.376988, 3.373832]
header = '# t/s \t U0/V \t U1/V \t U2/V \t I0/A \t \I1/A \t I2/A \n'
#-------------------------------------------------------------------------
continue_running = [0, 0, 0]

seconds = 0

WIDTH  = 128                                            # oled display width
HEIGHT = 32                                             # oled display height

adc2 = Pin(28, Pin.IN)                  # this is needed to turn input to high impedance    
adc1 = Pin(27, Pin.IN)                  # this is needed to turn input to high impedance
adc0 = Pin(26, Pin.IN)                  # this is needed to turn input to high impedance    
adc0 = ADC(0)        # Pin 31
adc1 = ADC(1)        # Pin 32
adc2 = ADC(2)        # Pin 28
adc = [adc0, adc1, adc2]



Q_As = [0,0,0]
Q_mAh = [0, 0, 0]

uart = UART(0, baudrate=baudrate_TX)

btn_on = Pin(14, Pin.IN, Pin.PULL_UP)

i2c = I2C(0)                                            # Init I2C using I2C0 defaults, SCL=Pin(GP9), SDA=Pin(GP8), freq=400000
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display

tim = Timer()
#--------------------------------------------------
def say_hello():
    print("LIon TEST")
    print("# I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("# I2C Configuration: "+str(i2c))                   # Display I2C config
    oled.fill(0)
    oled.text("ACCU TEST",5,5)
    oled.text("withPico",5,15)
    oled.show()
    time.sleep(1)

   
#----------------------------------------------------
def display(s):
    ''' display 4 substrings separated by \t on OLED'''
    s = s.split('\t')
    oled.fill(0)
    oled.text(str(s[0]), 0, 0)
    oled.text(str(s[1]), 0, 8)
    oled.text(str(s[2]), 0, 16)
    oled.text(str(s[3]), 0, 24)
    oled.show()    
    
def display_result(sq):
    oled.fill(0)
    oled.text("CHARGES:", 0, 0)
    y = 8
    for s in sq:
        oled.text(s + "mAh", 0, y)
        y += 8
    oled.show()       
#-------------------------------------------------------    
def get_adc012(n_samples):
    '''return 3 voltages as array'''
    v0 = 0
    v1 = 0
    v2 = 0
    for i in range(0, n_samples):
        v0 += adc0.read_u16()
        v1 += adc1.read_u16()
        v2 += adc2.read_u16()
        time.sleep_us(950)
    v0 = v0/n_samples
    v1 = v1/n_samples
    v2 = v2/n_samples  
    v0 = v0 * 5.041299648886 / 65535 - 0.016
    v1 = v1 * 5.031866583 /65535 - 0.016
    v2 = v2 * 5.0291789788 /65535 - 0.016
    return [v0, v1, v2]
#----------------------------------------------------
def calculate_currents(voltages):
    '''calculate currents from voltages array'''
    curr = [0, 0, 0]
    i=0
    for v in voltages:
       if continue_running[i]: 
           curr[i] = voltages[i] / Rload[i]
       else:
           curr[i] = 0
       i += 1
    return curr
#--------------------------------------------------
def calculate_Q(currents):
    i=0
    for curr in currents:
       Q_As[i] += curr
       Q_mAh[i] += curr/3.6
       i += 1
    return Q_As, Q_mAh    
#----------------------------------------------------
def tick(timer):
    '''execute every second via timer interrupt'''
    global seconds
    s, currents = measure_display_store()
    Q = calculate_Q 
    seconds +=1
#-------------------------------------------------------    
def measure_display_store():
    voltages = get_adc012(20)
    vs = ["%.3f" %(v) for v in voltages]
    s = str(seconds) + '\t' + vs[0] + '\t' + vs[1] + '\t' + vs[2]   ## +'\t'
    
    # if at least one channel is running, print + store voltages + currents
    if get_nb_running(continue_running):
        currents = calculate_currents(voltages)
        si = ["%.3f" %(i) for i in currents]
        s += '\t' + si[0] + '\t' + si[1] + '\t' + si[2]     ##+ '\t'
        ## store(s)
        
        Q_As, Q_mAh = calculate_Q(currents)
        si = ["%.2f" %(i) for i in Q_mAh]
        s += '\t' + si[0] + '\t' + si[1] + '\t' + si[2]
        
        store(s)
        print(s)
        uart.write(s)
        
    # before start, print only voltages all in one line (overwriting line before)
    else:    
        print(s, end = '\r')
        currents = [0, 0, 0]
    
    display(s)
    return s, currents    
#------------------------------------------------------    
def get_nb_running(continue_running):
    sumr = 0
    for r in continue_running:
        sumr += r
    return sumr

#-------------------------------------------------------


def delete_old_file():
    try:
        os.remove(filename)
        print("Remove old " + filename)
    except:
        print("Could not delete " + filename)
        print(os.listdir())


def createfile():
    f = open(filename, 'w')
    f.write('LiIon measure capacity\n')
    f.write(header)       
    f.close()
    

def store(s):
    if ( seconds <= 60 ) or (seconds % 10 ==0): 
        f = open(filename, 'a')
        f.write(s + '\n')
        f.close()
    
#-------------------------------------------------------    

# *****   MAIN   *********

switch_all_off()
say_hello()

print (header)
measure_display_store()

# wait for button
while btn_on.value():
    measure_display_store()
    time.sleep_ms(100)
    

# ---------------------------
# start
delete_old_file()
createfile()
tim.init(freq=1, mode=Timer.PERIODIC, callback=tick)
continue_running = [1, 1, 1]
switch_all_on()

while True:
    
    v = get_adc012(20)
    time.sleep_ms(100)
    
    # check threshold:
    for i in [0, 1, 2]:
        if v[i] < threshold:
            switch_off(i)
            continue_running[i] = 0
            print("#", i, " switched off @ ", v[i], "V")
        
    # stop only when all are off:
    sumr = get_nb_running(continue_running)
    if sumr == 0:
        break
    

tim.deinit()
print('# CHARGES:')
sq = (["%.2f" %(q) for q in Q_mAh])
for s in sq:
    print("#  ", s , "mAh")
display_result(sq)
    
