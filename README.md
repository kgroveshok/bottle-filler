Bottle filling machine (C) 2021 Kevin Groves
============================================

I have a need to automate the filling of perfume bottles, and to help with 
my sanity during COVID lock down I thought this little project will help both.

Feel free to reuse but please do credit, hey, and if you want me to build you one
drop me a message (once lockdown is over will have better material selection). :-)

[![Now on Hackaday](https://hackaday.io/project/179928-raspberry-pi-zero-bottle-filler)](https://hackaday.io/project/179928-raspberry-pi-zero-bottle-filler)

# Introduction Video

[![Introduction](https://img.youtube.com/vi/9glj0tt7VoQ/0.jpg)](https://www.youtube.com/watch?v=9glj0tt7VoQ)


# Construction Version 1

## Parts Needed

* Any Raspberry Pi, I'm using a Zero. At some point might convert to ESP.
* Piconzero control board (just so its all compact). https://4tronix.co.uk/blog/?p=1224
* HCSR04 ultasonic detector (for bottle presence detection) 
* 3 x Microswitches (Caddy ends and bottle marker)
* 1 x Continuous rotation servo to drive the caddy
* 1 x Micro 180 servo to control filling pipe insertion 
* 1 x Micro pump of choice. Using a 12v but works well under 5v it's a chemical grade 
so I can use with alcohol based perfumes
* 1 x HEF4051B octal multiplexer to drive the 8 LEDS from 3 pins
* 4 x Push buttons for the control panel
* 8 x LEDs 
* Any breadboard or vero to stick it all on
* Various bits of wood, metal, whatever to build
* 1 x Draw runner with bearings (wonderful smooth glide motion)
* Food grade tubing for the pump

## Wiring

* The pump is connected to either of the motor outputs on the Piconzero
* HCSR04 ultrasonic connects to the supplied socket for it on the Piconzero
* The HEF requires three I/O pins to drive and these are mapped from S0-S2
on the HEF to pins 18, 27 and 22 on the GPIO header on the Piconzero
* The HEF is then wired up to sink each of the LEDs as:

          Pin             Where to
          1              LED 5
          2              LED 7
          3              +5V from Pi
          4              LED 8
          5              LED 6
          6              GND on Pi
          7              +5V from Pi
          8              GND on Pi
          9              GPIO 18 
          10             GPIO 27
          11             GPIO 22
          12             LED 4
          13             LED 1
          14             LED 2
          15             LED 3
          16             +5V from Pi


All LEDs have a common ground which is connected to the Pi ground.
5v is supplied from the Pi

* Piconzero output pin wiring:

        0 - Caddy servo
        1 - Fill pipe servo

* Piconzero input pin wiring:

        0 - Caddy in and Caddy out microswitches, Control panel button (unused)
        1 - Control panel button for program adjustment
        2 - Control panel program selection button
        3 - Control panel start program/emergency stop button


## Building

The videos/pictures should show how I threw it together from the various prototypes.

Here are some early prototype videos and pictures: 

[![Video 1](https://img.youtube.com/vi/vrkxeWaGT0Y/0.jpg)](https://www.youtube.com/watch?v=vrkxeWaGT0Y)

[![Video 2](https://img.youtube.com/vi/BeN0tJPjiZY/0.jpg)](https://www.youtube.com/watch?v=BeN0tJPjiZY)

[![Video 3](https://img.youtube.com/vi/YHZAN4LFCxw/0.jpg)](https://www.youtube.com/watch?v=YHZAN4LFCxw)


![](media/20210214_165817.jpg)
![](media/20210214_165822.jpg)  
![](media/20210215_085208.jpg)  




# Usage

The idea is that the caddy platform provides for a replaceble jig which has custom bottle holes for
the particular bottle sizes along with a marker for where the fill point for that bottle should be.
This means that various bottle shapes and sizes can be accomodated and that they are held safely and
won't tip while in motion.

The flexible fill pipe too provides flexiblity to position depending on size and shape.


## Feature Overview

[![Feature Overview](https://img.youtube.com/vi/HLgK549O6gQ/0.jpg)](https://www.youtube.com/watch?v=HLgK549O6gQ)

## Dry Run Tests

[![Dry Run 1](https://img.youtube.com/vi/8gWB_FIZPl4/0.jpg)](https://www.youtube.com/watch?v=8gWB_FIZPl4)

[![Dry Run 2](https://img.youtube.com/vi/HOjA3XgUOuc/0.jpg)](https://www.youtube.com/watch?v=HOjA3XgUOuc)

## Live Run 

[![Live Run](https://img.youtube.com/vi/7t0mo8SHLEQ/0.jpg)](https://www.youtube.com/watch?v=7t0mo8SHLEQ)


## Final Build Photos

Now some final build photos. OK, the wood quality wasn't great, due to COVID lock down I could only use materials I had at hand which was some off cut worktop and some rough ply. Annoyingly I couldn't find my decent white primer so had to use art white acryilic which didn't work so well. Oh well. Its for my 
use anyway. :-)

![](media/20210217_112518.jpg)  
![](media/20210217_112634.jpg)
![](media/20210217_112545.jpg)  
![](media/20210217_112656.jpg)
![](media/20210217_112554.jpg)  
![](media/20210217_112706.jpg)
![](media/20210217_112507.jpg) 
![](media/20210217_112601.jpg)
![](media/20210217_112512.jpg)  
![](media/20210217_112618.jpg)


# Control Panel Features

## Program 'Selection' button
This goes through six normal programs, the flush program (7th) that won't move the caddy and 
can be used to clean the tubing, and the 8th LED which is a system shutdown feature.

## Program Adjustment

* Select a program to change
* Press the 'Adjustment' button
* The 8th and selected program LEDs will blink alternately
* Pressing and releasing the program select button will fire the pump for one unit
* Repeat until the desired number of presses are made
* Pressing 'Adjustment' button will save that setting
* Pressing 'Start' will cancel the adjustment
* All settings are saved to 'bottle.settings' file. You can either edit it later, or 
deletion will revert to the predefined settings in the code.


## 'Start' and emergency stop button
Starts the fill process. If at any time you need to stop before the end of program hold this button down.

* Press 'Selection' button until the desired program is found
* Press 'Start' button
* LEDs cycle
* Caddy will eject all the bottles until the microswitch is tripped.
* Caddy will reverse and begin to search for a bottle marker being tripped by a micro switch
* Caddy drive servo will stop
* Ultrasonic dector will make sure there is a bottle actually at that bottle marker
* If a bottle is sensed then the pipe fill servo will insert the fill tube
* Pump will start up for the required number of units
* Pipe fill servo will remove tube
* Caddy will then continue to look for another bottle marker unless the end caddy micro switch is
tripped.

## Prime Pump
If the tube is empty you need to fill the tubing with liquid so that you don't get empty bottles on the fill process. 

* Hold down the program 'Selection' button
* Press and hold the 'Start' button and the pump will run until you release both

## Calibrate Pipe Insert
To make sure the pipe inserts into the bottle at the right point, you can hold down the 'Selection' 
button and tap the 'Adjustment' button to toggle the position of the filling servo either in or out.
     
## Flush Program
Starting the 7th program will run the pump in whatever position it is in for a long (can be adjusted) 
cycle and this can be used to flush through any water and/or cleaning fluid.





# Construction Version 2 - Aug 2022

The previous version was just a little too complex (yeah, it filled in the time tbh), and counldn't 
handle the larger and heavier perfume bottles I eventually went with. Now I'm revisiting the
design to speed things up. A major concern was the pump too, each perfume change would require
the pipes to be fully flushed to prevent cross contamination. Theere would be material losses
which wouldn't be ideal. I really needed a better pump solution.

Then I found a peristaltic dosing pump. This type of pump that has no physical contact with the
pipe contents and it's ideal. All I would need to do to change perfume would be to change the pipe. 
No large amounts of flushing required (except at the end for any left overs).

I chose to also simply filling with removal of all moving parts excepting the pump. Removed most of
the sensors except one which helps with bottle fill trigger.

Much easier now.



## Building

* Stripped down the original device.
* Removed moveable platform
* Remove platform end sensors
* Remove filling tube arm
* Removed platform servo
* Kept the bottle mark sensor for reuse as a switch to trigger filling of the bottle
* Kept the control panel
* Replaced the pump with a peristaltic pump and provided means for the pipe to be focused


## Trial Run

And yes, obivously recording the trial run was a bad move as things didn't quite work right,
nothing serious, just over flowing bottle.

[![V2 Live Run](https://img.youtube.com/vi/VE5aFr9dA/0.jpg)](https://www.youtube.com/watch?v=VE5aFr9dA)


I've since corrected the filling settings and have ordered a Raspberry Pico. Once I've met the filling
demands for this current perfume batch I will be rebuilding for that platform along a redesigned 
control panel and a smaller box. Perhaps making it a box I can clamp to a lab retort or put on the wall.







# Construction Version 3 - Sep/Oct 2022


New code for a Pico version using OLED 1.3 panel and three buttons.

Have added L298N motor/stepper board to provide scope for using the 
existing pump as well as replacing at some point with a much more 
precise (and expensive) stepper motor.


## Photos and drawings


![](pico/Schematic_Bottle_Filler_v3_2022-10-01.png)
![(Drawing)](pico/Schematic_Bottle_Filler_v3_2022-10-01.pdf)

![](pico/20221001_164701.jpg)
![](pico/20221001_165718.jpg)

## Extra Features

The replacement of the LEDs with an OLED panel, a better UI can be presented.
At this stage I have the ability of make adjustments to the programs with
selection of the pump direction, increment and decrement of the pulse count
and then the ability to change the label on the program display.

The OLED also provides context button labels on the bottom row of the display 
which is helpful.

## Todo

* Add a settings screan where I can adjust the pump pulse timing and select
either the motor or more accurate stepper motor.
* Provide a 6mm jack socket so I can use my drum machine pedal to trigger the 
fill process hands free!
* Reformat the OLED display so it looks neater and perhaps include images/animations. Slick.



