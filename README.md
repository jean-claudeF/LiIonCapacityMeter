# LiIon Capacity Meter
Measure the remaining capacity of recycled 18650 cells

![Picture](measure_liion_01.png)

I have collected a lot of 18650 cells that I want to use for new projects.
To do this, measuring the remaining capacity is essential.

It seems trivial to do this, but there are some things to care about, especially the need for good low ohm connections to the battery.
I use a Kelvin connection (4 wire connection) to be sure that I measure the battery voltage and not some voltage including voltage drops on conductors. Even at 1A only these can lead to unreproducible results.

The project uses a Raspi Pico and a constant current sink (1A) that is switched off at a threshold voltage (3V).

## Usage
- Upon start, the cell voltage is displayed.
- By pushing the start button (bottom right) the discharge is started
- When the stop button (bottom left) is pushed or
- when the threshold voltage is reached, the discharge is stopped.
- The discharge in mAh is displayed
- A new measuring cycle can be started with the reset button (top)

The measured values of time, voltage, current and charge in As and mAh are stored in a file LiIon.dat, in tab separated CSV format.
This can be read in Thonny, or via USB serial.
After reset the LiIon.dat can be output to USB serial by pushing the STOP / READ button and read in any serial terminal.

