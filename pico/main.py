#!/usr/bin/python
#

# Bottle filling machine v3 (Pico)
# --------------------------------

# I have a need to automate the filling of perfume bottles and to help with 
# my sanity during COVID lock down I thought this little project will help.
#
# Aug 2022 - Revisiting via the use of a peristaltic pump which provides easir
# separation of solvents and no internal pump contamination. Also simplying
# parts, so only moving part is the pump.
#
# Oct 2022 - Now a better solution it is time to shrink everything down
# and produce a neat little package that takes up less space.
# Perhaps even get to a point where I could mass produce them for others!

# (c) 2022 Kevin Groves
# Feel free to reuse but please do credit

from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from time import sleep
import framebuf,sys
import os

pix_res_x  = 128 # SSD1306 horizontal resolution
pix_res_y = 64   # SSD1306 vertical resolution

# sensor flags


senseButSelection = False
senseButStartStop = False
senseButAdjustPreset = False
#learnStep = 0
labelNew=""
# Machine processing stages

class stage:
    Selection = 1
    FindingBottleMark = 3
    Filling = 4
    Stop = 8
    Init = 9
    LearnDirection = 10
    LearnIncr = 11
    LearnLabel = 12
    LearnDone = 13
    
    Settings = 20
    

maxProgram = 10


def pumpStop():
    # stop the pump
    pumpActive.low()
    pumpIN1.low()
    pumpIN2.low()

def pumpPulse():
    # run the pump for a single pulse
    pumpIN1.high()
    pumpIN2.low()
    pumpActive.high()
    sleep(fillPulse)
    pumpStop()

def pumpPulseRev():
    # run the pump for a single pulse in the other direction
    pumpIN1.low()
    pumpIN2.high()
    pumpActive.high()
    sleep(fillPulse)
    pumpStop()

def setLED():
   # set led states

   # display current state
   buttonContext = [ "", "", ""]

   oled.fill(0)

   if currentStage == stage.Selection  :
        # display the current fill program setting
        #oled.text( "Prog: " + str(fillSelection), 25, 12 )
        oled.text( labelPrograms[fillSelection], 25, 25 )

        buttonContext = [ "Go", "Sel", "Adj" ]
        # start button, selection, and adjust bittons available

   elif currentStage == stage.LearnDirection :
        # display the current fill program setting
        #print( "Adjusting current state" )
        #print( currentStage )
#        oled.text( "Change Prog: " + str(fillSelection), 25, 12 )
        oled.text( labelPrograms[fillSelection], 25, 12 )
#        print( fillSelection ) 
        # first button ok, second button reduce, third increase. hold first to cancel adjustment
        
        
            # pump direction
            
        oled.text( directionPrograms[fillSelection] and "Fwd" or   "Rev", 25, 25)
        buttonContext = [ "Next", "Rev", "Fwd" ]
   elif currentStage == stage.LearnIncr :
        
    
            oled.text( str(fillPrograms[fillSelection]), 25, 25)
            buttonContext = [ "Next", "-", "+" ]
   elif currentStage == stage.LearnLabel :
        
    
       oled.text( labelPrograms[fillSelection], 25, 12 )
       
       buttonContext = [ "Done", ">", "^" ]
            
   elif currentStage == stage.Settings:
        print( "Settings")
        # adjust pulse length
        # adjust motor speed
        # select foot trigger
        # adjust oled contrast
        # adjust auto switch off
        # battery monitor???
        # stepper or motor
   elif currentStage == stage.Filling:
        #print( "Display Filling pulse %d of %d" % ( fillStage, fillPrograms[fillSelection] ))
        oled.text( "Filling", 25, 12 )
        oled.text( str(fillStage), 25, 25 )
        oled.text( str(fillPrograms[fillSelection]), 75, 25 )
        # TODO display bar graph of progress
        buttonContext = [ "Stop", "", "" ]
   #else:
   #     # Program must be running so display progress
   #     #print( "Program running" )
   #     oled.text( "Running Prog: " + str(fillSelection), 25, 12 )
   #     oled.text( labelPrograms[fillSelection], 25, 25 )
   #     buttonContext = [ "Stop", "Fill", "" ]
        #print( currentStage )
        #print( fillSelection ) 
        # anny button to stop


   # Display the button context along the bottom
   oled.text( buttonContext[0], 0, 48)
   oled.text( buttonContext[1], 40, 48)
   oled.text( buttonContext[2], 85, 48)
   oled.show()

 #   for p in range(0,8):
 #       if displayLED[p][0]:
 #           #            print( "LED %d on" % (p))
 #           if displayLED[p][3]:
 #               pin1.on()
 #           else:
 #               pin1.off()
 #           if displayLED[p][2]:
 #               pin2.on()
 #           else:
 #               pin2.off()
 #           if displayLED[p][1]:
 #               pin3.on()
 #           else:
 #               pin3.off()

# Piconzero servo caddy loading speeds
# * CHANGE HERE *

#caddySpeedStop=87
##caddySpeedStop=90
##too fast caddySpeedIn=98
#caddySpeedIn=93
#caddySpeedOut=50

# Piconzero servo pipe bottle insertion angles
# * CHANGE HERE *
#fillPipeIn=135
#fillPipeOut=150

# Piconzero pump motor speed and direction 
# * CHANGE HERE *
fillSpeed = -100
fillReverse = 100

# Piconzero pump duration (s) for a single unit 
# * CHANGE HERE *
fillPulse = 0.05
contrast = 10
useJack = 0
pumpType = 0

# Preset fill programs (can be over ridden at control panel)

settings = [ 1, fillPulse, contrast, useJack, maxProgram, pumpType ]
fillPrograms = [ 1, 5, 10, 15, 20, 40, 300, 1, 0, 0, 0 ]
directionPrograms = [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
labelPrograms = [ "Prg1      ", "Prg2      ", "Prg3      ", "Prg4      ", "Prg5      ", "Prg6      ", "Prg7      ", "Prg8      ", "Prg9      ", "Prg10     ","l            "]
fillStage = 0

labelSeq = "ABCDEFGHIKLNOPQRSTUVWZYZ 0123456789<>"
labelSel = 0
labelChar = 0


# Save and loading of the presets and user adjustments

def savePrograms():
    print( "Saving program settings to bottle.settings.")
    f = open( "bottle.settings","w" )
    for p in range(len(settings)):
        f.write("%d " % ( settings[p] ))
    for p in range(0,maxProgram):
        f.write("%d " % ( fillPrograms[p] ))
    for p in range(0,maxProgram):
        f.write("%d " % ( directionPrograms[p] ))
    for p in range(0,maxProgram):
        f.write("%s~" % ( labelPrograms[p] ))
    f.close()

def loadPrograms():
    try:
        f = open( "bottle.settings","r" )
        print( "Loading programs from bottle.settings")
        p = f.read()
        settings = p.split(" ")
        # TODO first value is settings version number
        fillPulse = settings[1]
        contrast = settings[2]
        useJack = settings[3]
        maxProgram = settings[4]
        pumpType = settings[5]

        p = f.read()
        fill = p.split(" ")
        for p in range(0,maxProgram):
            fillPrograms[p]=int(fill[p])
        p = f.read()
        fill = p.split(" ")
        for p in range(0,maxProgram):
            directionPrograms[p]=int(fill[p])
        p = f.read()
        fill = p.split("~")
        for p in range(0,maxProgram):
            labelPrograms[p]=fill[p]
        f.close()
    except:
        print( "No bottle.settings file found. Using code defaults and saving them.")
        savePrograms()

#    print( "Current Programs")
#    for p in range(0,6):
#        fillPrograms[p]=int(fillPrograms[p])
#        print("Program %d = %d" % ( p, fillPrograms[p]))

# Cycle through all the LEDS for a main transition indication

def cycleLEDS():
    print( "in cycleled" )
    # TODO display a logo or some other graphic
#    for f in range(0,8):
#        for s in range(0,8):
#            displayLED[s][0]=0
#
#        displayLED[f+1][0]=1
#        setLED()
#        sleep(0.25)




# init

# selection options
currentStage = stage.Init

l = 0

prevStage = stage.Selection
stageSetup = True


flashFlipFlop = 0
flashCt = 0

# handle selection and button bounce

fillSelection = 0
pressedSelection = False
pressedStartStop = False
pressedAdjust = False

i2c_dev = I2C(1,scl=Pin(27),sda=Pin(26),freq=50000)  # start I2C on I2C1 (GPIO 26/27)
#i2c_dev = I2C(1,scl=Pin(27),sda=Pin(26),freq=200000)  # start I2C on I2C1 (GPIO 26/27)
i2c_addr = [hex(ii) for ii in i2c_dev.scan()] # get I2C address in hex format
if i2c_addr==[]:
    print('No I2C Display Found') 
    sys.exit() # exit routine if no dev found
else:
    print("I2C Address      : {}".format(i2c_addr[0])) # I2C device address
    print("I2C Configuration: {}".format(i2c_dev)) # print I2C params


oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev) # oled controller

#fb = framebuf.FrameBuffer(buffer, img_res[0], img_res[1], framebuf.MONO_HMSB) # MONO_HLSB, MONO_VLSB, MONO_HMSB

oled.fill(0) # clear the OLED
#oled.blit(fb, 0, 0) # show the image at location (x=0,y=0)

# setup I/O

button1PIN=18
button2PIN=19
button3PIN=21

buttonStartStop = Pin(button1PIN, Pin.IN, Pin.PULL_UP)
buttonA = Pin(button2PIN, Pin.IN, Pin.PULL_UP)
buttonB = Pin(button3PIN, Pin.IN, Pin.PULL_UP)



pumpIN1 = Pin( 3, Pin.OUT)
pumpIN2 = Pin(2, Pin.OUT)

pumpActive = Pin(4, Pin.OUT)



# main loop

#cycleLEDS()

# load presaved programs if present
loadPrograms()

while True:
    if currentStage != prevStage :
        pressedSelection = False
        pressedStartStop = False
        pressedAdjust = False
        prevStage = currentStage
        stageSetup = True
        print( "Stage setup for %d" % ( currentStage ) )
    else:
        stageSetup = False

    setLED()

    senseButSelection = not buttonA.value()
    senseButStartStop = not buttonStartStop.value()
    senseButAdjustPreset = not buttonB.value()



    if senseButStartStop and ( currentStage != stage.Selection and currentStage != stage.LearnDirection and currentStage != stage.LearnIncr and currentStage != stage.LearnLabel):
       # emergency stop if start button is pressed when running
#       if senseButStartStop :
            print(" emergency stop!")
            currentStage = stage.Selection
            stageSetup = True
            # stop pump
            pumpStop()
            cycleLEDS()
            cycleLEDS()



    elif currentStage == stage.LearnDirection:
        if stageSetup : 
            print( "Entering learn mode for %d (direction)" % ( fillSelection ))
    #        displayLED[fillSelection][0]=0
    #        learnBlink = 0
            # set current pump count
            learnStep = 0
            pressedAdjust = False
            pressSelection = False
            pressedStartStop = False
            
            # handle pump direction
        if senseButSelection and not pressedSelection:
                    # pump direction reversed
                    print( "Pump rev" )
                    directionPrograms[fillSelection]=0
                    currentStage = stage.LearnIncr
                    
        if senseButAdjustPreset and not pressedAdjust:
                    # pump direction forward
                    print( "Pump forward" )
                    directionPrograms[fillSelection]=1
                    currentStage = stage.LearnIncr
                    
        if senseButStartStop and not pressedStartStop:
                    # move to next page
                    print( "Next page")
                    currentStage = stage.LearnIncr
                    
    elif currentStage == stage.LearnIncr:
        if stageSetup : 
            print( "Entering learn mode for %d (incr)" % ( fillSelection ))
    #        displayLED[fillSelection][0]=0
    #        learnBlink = 0
            # set current pump count
            
            pressedAdjust = False
            pressSelection = False
            pressedStartStop = False
    
    
        
                # handle increments
        if senseButSelection and not pressedSelection:
                    # pump direction reversed
                    print( "Pump -" )
                    fillPrograms[fillSelection]=fillPrograms[fillSelection] -1
                    if fillPrograms[fillSelection] < 0:
                        fillPrograms[fillSelection]=0
                    
                    
        if senseButAdjustPreset and not pressedAdjust:
                    # pump direction forward
                    print( "Pump +" )
                    fillPrograms[fillSelection]=fillPrograms[fillSelection]+1
                    
                    if directionPrograms[fillSelection] == 1:
                        pumpPulse()
                    else:
                        pumpPulseRev()
                    
                
        if senseButStartStop and not pressedStartStop:
                    # move to next page
                    print( "Next page")
                    currentStage = stage.LearnLabel



    elif currentStage == stage.LearnLabel:
        if stageSetup : 
            print( "Entering learn mode for %d (label)" % ( fillSelection ))
    #        displayLED[fillSelection][0]=0
    #        learnBlink = 0
            # set current pump count
            
            pressedAdjust = False
            pressSelection = False
            pressedStartStop = False
            labelSel = 0
            labelChar = 0
            # handle label
        curLabel = list(labelPrograms[fillSelection])
        curLabel[labelChar]=labelSeq[labelSel]
        print(curLabel)
        print(labelChar)
        print(labelSeq[labelSel])
        print(labelSel)
        labelPrograms[fillSelection]="".join(curLabel)
        
        if senseButSelection and not pressedSelection:
                    # pump direction reversed
                    print( "Move right" )
                    labelChar = labelChar + 1
                    if labelChar > 9 :
                        labelChar = 0
#labelSeq = "ABCDEFGHIKLNOPQRSTUVWZYZ 0123456789<>"
#labelSel = 0
#labelChar = 0
                    
                    
                    
        if senseButAdjustPreset and not pressedAdjust:
                    # pump direction forward
                    print( "next char" )
                    labelSel = labelSel + 1
                    if labelSel > len(labelSeq)-1:
                        labelSel = 0
                    
                
        if senseButStartStop and not pressedStartStop:
                    # move to next page
                    print( "Done")
                    currentStage = stage.LearnDone


    

    elif currentStage == stage.LearnDone:
    
                 

            # exit learn
            print( "Exit adjustment for %d set at %d from %d" % ( fillSelection,  fillStage,fillPrograms[fillSelection]))
            # set and save the adjustments
            #fillPrograms[fillSelection]=fillStage
            savePrograms()
            currentStage = stage.Selection
            pressedAdjust=False
            sleep(3)

    elif currentStage == stage.Selection:
        if stageSetup :
#            pz.setOutput( pinFillInsert, fillPipeOut)
            fillStage = 0
 #           pipeStateIn = False
            pressedAdjust = False
            pressedSelection = False

        # select mode
        if senseButSelection and not pressedSelection:
            # selection button pressed
            pressedSelection = True
            print("Holding down selection button selection stage")

        if senseButAdjustPreset and not pressedAdjust:
            # selection button pressed
            pressedAdjust = True
            print("Holding down adjust button selection stage")

        if not senseButAdjustPreset and pressedAdjust and not senseButSelection :
            currentStage = stage.LearnDirection

        elif not senseButSelection and pressedSelection :
            # selection button has been released



            pressedSelection = False
            fillStage = 0
            
            # Cycle selection
            fillSelection = fillSelection + 1
            if fillSelection > maxProgram:
                fillSelection = 0
            print( "Fill selection %d" % fillSelection )

        elif senseButSelection and senseButStartStop :
            pressedSelection = False
            fillStage = fillStage + 1
            print( "Run pump pulse %d counted %d " % ( fillPulse, fillStage ) )
            pumpPulse()
            
        elif not senseButAdjustPreset and pressedAdjust and senseButSelection :
            pressedAdjust = False
            pressedStartStop = False

        elif senseButStartStop and not senseButSelection and not pressedStartStop and not senseButAdjustPreset:
            # start the system
                #print( "Start fill process")
            print( "Start fill bottle using program %d" % (fillSelection) )
            currentStage = stage.FindingBottleMark 

            sleep(1)
            cycleLEDS()

        
    elif currentStage == stage.FindingBottleMark:

        if stageSetup:

            print( "Finding bottle marker" )
            # TODO sensor debounce
            sleep(0.25)
        else:

            if useJack:

                if senseBottleMark:
     #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
                    sleep(1)
                    currentStage = stage.Filling
  #              pz.setOutput( pinCaddyDrive, caddySpeedStop )
            else:
                if senseButSelection or senseButAdjustPreset:
                    sleep(1)
                    currentStage = stage.Filling

                if senseButStartStop :
                    print("At end of filling. Stop")
                    currentStage = stage.Selection
                    sleep(1)
                    cycleLEDS()

        setLED()


    elif currentStage == stage.Filling:
        if stageSetup:
            #dispLED5 = True
            setLED()
            fillStage = fillPrograms[fillSelection]
            print( "Fill bottle using program %d for %d pulses" % (fillSelection, fillStage) )
        else:
            if fillStage == 0 :
                print( "Filling completed")
                currentStage = stage.FindingBottleMark 
#                if fillSelection == 6:
#                    print( "Flush system program is over so return to selection")
#                    currentStage = stage.Selection
#                    sleep(1)
#                else:
#                    currentStage = stage.FindingBottleMark
#                    print "Reverse and pause to avoid drips after stopping pump"
#                    pz.forward( fillReverse)
#                    sleep(2)
 #               pz.stop()
#                    sleep(2)
#                    print "Withdraw filling pipe"
#                    pz.setOutput( pinFillInsert, fillPipeOut)
#                    sleep(0.5)
            else:
                print( "Filling pulse %d of %d" % ( fillStage, fillPrograms[fillSelection] ))

                if directionPrograms[fillSelection] == 1:
                    pumpPulse()
                else:
                    pumpPulseRev()

#                pz.forward(fillSpeed)
#                sleep(fillPulse)
#                pz.stop()
                fillStage = fillStage - 1

    elif currentStage == stage.Init:
        if stageSetup:
            #                dispLED2 = True
 #           pz.stop()
            cycleLEDS()
#            pz.setOutput( pinFillInsert, fillPipeOut)
#            caddyPos = 0
#            sleep(2)
        # TODO add sensor check and remove counter
 #           pz.setOutput( pinCaddyDrive, caddySpeedIn )
 #           print( "Roll caddy in")
            # TODO sensor debounce
            sleep(0.25)
 #       else:
 #           if senseCaddyIn:
 #               print( "Caddy is in")
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
 #               sleep(1)
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
            currentStage = stage.Selection
        setLED()
        

#hcsr04.cleanup()

#pz.cleanup()
#os.system("sudo halt -p")
