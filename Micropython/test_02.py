
from machine import Pin, ADC, Timer
import time

btn_start = Pin(15, Pin.IN, Pin.PULL_UP)
#led = Pin(25, Pin.OUT)
led = Pin('LED', Pin.OUT)

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
   

clin0 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)
clin1 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)
clin2 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)

def print_ADC():
    v0 = readADC(adc0)
    v0 = clin0.calc(v0)
    
    v1 = readADC(adc1)
    v1 = clin1.calc(v1)
    
    v2 = readADC(adc2)
    v2 = clin2.calc(v2)
    
    s = "%.3f\t%.3f\t%.3f" % (v0, v1, v2)
    print(s +'\t' + str(time.time()))


'''
# Waiting loop
starttime = time.time()
while True:

    #v0 = adc0.read_u16() * 3.3 / (65535)
    if time.time() - starttime >= 1.0:
        led.on()
        print_ADC()
        starttime = time.time()
        led.off()
        
    if btn_start.value() == 0:
        break
    
    time.sleep_ms(50)
'''

def do_it(void):
    led.on()
    print_ADC()
    led.off()

# Callback function must be defined before init timer!
    
timer = Timer()
#timer.init(freq = 1, mode = timer.PERIODIC, callback = do_it)       # in Hz!
timer.init(period = 2000, callback = do_it)      # in ms!

