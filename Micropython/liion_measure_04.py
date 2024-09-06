# Switchoff voltage:
threshold = 3.0
Idischarge = 1.0
filename = 'LiIon.dat'
header = '# t/s \t U/V \t I/A \t Q/As \t Q/mAh\n'

Q_As = 0
Q_mAh = 0

from machine import Pin, ADC, Timer, I2C, PWM
import time
import os, sys

timer = Timer()

btn_start = Pin(15, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(14, Pin.IN, Pin.PULL_UP)
#led = Pin(25, Pin.OUT)
led = Pin('LED', Pin.OUT)

# OLED
from ssd1306 import SSD1306_I2C
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

# DAC via PWM for current setting:
pwm = PWM(Pin(3))
pwm.duty_u16(32767)
pwm.freq(100000)

def set_dac(v):
    duty = int(65535 * v / 3.3)
    pwm.duty_u16(duty)


#--------------------------------------------------------------------
seconds = 0
voltage = 0
current = 0
nbval = 0

# ADC
a0 = Pin(26, Pin.IN) # his is needed to turn input to high impedance
a1 = Pin(27, Pin.IN) # this is needed to turn input to high impedance 
a2 = Pin(28, Pin.IN)
adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)


class LinCalc():
    # y = k0 + k1 * x
    def __init__(self, k0 = 0, k1 = 1):
        self.k0 = k0
        self.k1 = k1
        
    def calc(self, x):
        y = self.k0  + self.k1 * x
        return y
    
def readADC(adc, n = 10):
    # adc = adc0, adc1, adc2
    # n = nb of vallues for mean
    vm = 0
    for i in range(0, n):
        v = adc.read_u16()
        vm += v
    v = vm / n    
    v = v * 3.3 / 65535
    return v
   

clin0 = LinCalc(k0 = -0.02, k1 = 2.00926177)
clin1 = LinCalc(k0 = -0.02, k1 = 0.955)
clin2 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)

def get_adc():
    v0 = readADC(adc0)
    v0 = clin0.calc(v0)
    
    v1 = readADC(adc1)
    v1 = clin1.calc(v1)
    
    v2 = readADC(adc2)
    v2 = clin2.calc(v2)
    return v0, v1, v2

#----------------------------------------------------

def say_hello():
    print("LIon TEST")
    print("# I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("# I2C Configuration: "+str(i2c))                   # Display I2C config
    print("# Waiting for start button")
    
    time.sleep(1)



def print_values():
    s = "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (seconds, voltage, current, Q_As, Q_mAh)
    print(s)
    
    
def oled_waiting():
    oled.fill(0)
    oled.text("%.3f V" % voltage, 0, 12)
    oled.text("WAITING",0,36)
    oled.show()

def oled_running():
    oled.fill(0)
    oled.text(str(seconds) +"s", 0, 0)
    oled.text("%.3f V" % voltage, 0, 12)
    oled.text("%.3f A" % current, 0, 24)
    oled.text("%i mAh" % Q_mAh, 0, 36)
    oled.text("RUNNING", 0, 48)
    oled.show()
    
def oled_stopped():
    oled.fill(0)
    oled.text(str(seconds) + "s", 0, 0)
    oled.text("%.3f V" % voltage, 0, 12)
    oled.text("%.3f A" % current, 0, 24)
    oled.text("%i mAh" % Q_mAh, 0, 36)
    oled.text("STOPPED", 0, 48)
    oled.show()

def oled_sentdata(l):
    oled.fill(0)
    oled.text("SENT DATA", 0, 12)
    oled.text(str(l) + " chars", 0, 24)
    oled.text("RESET TO START", 0, 48)
    oled.show()

def oled_error(e):
    oled.fill(0)
    oled.text("ERROR !", 0, 12)
    oled.text(e, 0, 24)
    oled.text("RESET TO START", 0, 48)
    oled.show()

def set_current(I):
    set_dac(I)

def measure():
    global voltage, current
    v0, v1, v2 = get_adc()
    voltage = v0
    current = v1
    

#-------------------------------------------------------------
# Timer callback function
# This is wher it happens!
def timer_callback(void):
    # This is called via timer interrupt every second
    global seconds, voltage, Q_As, Q_mAh
    led.on()
    measure()
    print_values()
    oled_running()
    if ( seconds <= 60 ) or (seconds % 10 ==0):
        store()
    led.off()
    seconds += 1
    Q_As += current
    Q_mAh = Q_As / 3.6
    
#------------------------------------------------------------------------
def delete_old_file():
    try:
        os.remove(filename)
        print("Remove old " + filename)
    except:
        print("Could not delete " + filename)
        print(os.listdir())


def create_file():
    try:
        f = open(filename, 'w')
        f.write('# LiIon measure capacity\n')
        f.write(header)       
        f.close()
    except:
        print("Error creating " + filename)

def store():
    s = "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (seconds, voltage, current, Q_As, Q_mAh)
    f = open(filename, "a") 
    f.write(s + '\n')
    f.close()    

def send_data():
    
    try:
        f = open(filename, 'r')
        t = f.read()
        f.close()
        print(t)
        oled_sentdata(len(t))
    except:
        print("Could not read " + filename)
        oled_error("Error sending data")
     
    
#--------------------------------------------------------------------------------------
##   MAIN



set_current(0)
say_hello()

# Wait for button start
while btn_start.value():
    if btn_stop.value() ==0:
        send_data()
        sys.exit()
    measure()
    print("##   %.3fV" % voltage, end = '\r')
    oled_waiting()
    time.sleep(0.05)

# START
# Init timer and set discharge current
timer.init(period = 1000, callback = timer_callback)      # in ms!
print("\n # Start")
print(header)
delete_old_file()
create_file()
set_current(Idischarge)


# The measurement, display and stoe is done in the timer_callback function

# Wait for voltage < threshold or stop button
while btn_stop.value():
    measure()
    
    if voltage < threshold:
        set_current(0)
        break
    time.sleep(0.05)
timer.deinit()
set_current(0)
print("# STOPPED at %.3fV" % voltage)
print("# Q = ", Q_mAh, "mAh")
oled_stopped()


#---------------------------------------------------------------------------------------
# Callback function must be defined before init timer!
    

#timer.init(freq = 1, mode = timer.PERIODIC, callback = do_it)       # in Hz!


