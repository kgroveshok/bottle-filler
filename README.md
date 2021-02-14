Bottle filling machine
----------------------

I have a need to automate the filling of perfume bottles and to help with 
my sanity during COVID lock down I thought this little project will help.


(c) 2021 Kevin Groves
Feel free to reuse but please do credit

* Parts Needed

    * Any Raspberry Pi, I'm using a Zero. At some point might convert to ESP.
    * Piconzero control board (just so its all compact).
    * HCSR04 ultasonic detector (for bottle presence detection) 
    * 3 x Microswitches (Caddy ends and bottle marker)
    * 1 x Continuous rotation servo to drive the caddy
    * 1 x Micro 180 servo to control filling pipe insertion 
    * 1 x Micro pump of choice. Using a 12v but works well under 5v
      it's a chemical grade so I can use with alcohol based perfumes
    * 1 x HEF4581 octal multiplexer to drive the 8 LEDS from 3 pins
    * 4 x Push buttons for the control panel
    * 8 x LEDs 
    * Any breadboard or vero to stick it all on
    * Various bits of wood, metal, whatever to build
    * 1 x Draw runner with bearings (wonderful smooth glide motion)
    * Food grade tubing for the pump

* Wiring

  * The pump is connected to either of the motor outputs on the Piconzero
  * HCSR04 ultrasonic connects to the supplied socket for it on the Piconzero
  * The HEF requires three I/O pins to drive and these are mapped from S0-S2
    on the HEF to pins 18, 27 and 22 on the GPIO header on the Piconzero
  * The HEF is then wired up to sink each of the LEDs as:

          Pin             Where to
          1
          2
          3
          4
          5
          6
          7
          8
          9
          10
          11
          12
          13
          14
          15
          16

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

* Construction

  The videos/pictures should show how I threw it together from the various prototypes.

* Usage

The idea is that the caddy platform provides for a replaceble jig which has custom bottle holes for
the particular bottle sizes along with a marker for where the fill point for that bottle should be.
This means that various bottle shapes and sizes can be accomodated and that they are held safely and
won't tip while in motion.

The fill pipe too provides flexiblity to position depending on size and shape.

TODO youtube videos and some pictures

* Control Panel Features

TODO
Program selection button - goes through six programs, though all eight leds are lit. LED 8 selection
provides a system shutdown.


Program adjustment

Start and emergency stop button - starts the fill process




