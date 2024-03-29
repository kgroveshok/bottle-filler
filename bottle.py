#!/usr/bin/python
#

# Bottle filling machine
# ----------------------

# I have a need to automate the filling of perfume bottles and to help with 
# my sanity during COVID lock down I thought this little project will help.
#
# Aug 2022 - Revisiting via the use of a peristaltic pump which provides easir
# separation of solvents and no internal pump contamination. Also simplying
# parts, so only moving part is the pump.

# (c) 2021 Kevin Groves
# Feel free to reuse but please do credit

#from enum import Enum
import piconzero as pz, time
#import hcsr04, time
from gpiozero import LED
import os


# sensor flags

senseButSelection = 0
senseButStartStop = 0

senseButSelection = 0
senseButStartStop = 0
#senseCaddyIn = 0
#senseCaddyOut = 0
senseBottleMark = 0
senseButAdjustPreset = 0
senseBottlePresent = 0

senseButSelection = 0
senseButStartStop = 0
senseButAdjustPreset = 0
#senseCaddyIn = 0
#senseCaddyOut = 0
senseBottleMark = 0
senseBottlePresent = 0

# Machine processing stages

class stage:
    Selection = 1
#    LoadCaddy = 2
    FindingBottleMark = 3
#    BottlePresentScan =4
#    FillInsert = 5
#    FillPause = 6
    Filling = 4
    Stop = 8
    Init = 9
    Learn = 10




pz.init()
#hcsr04.init()

# machine pin out
# * CHANGE HERE *

#pinCaddyIn = 0
#pinCaddyOut = 0
pinBottleMark = 1
pinButSelection = 1
pinButStartStop = 3
pinButAdjustPreset = 2

#pinFillInsert = 1

#pinCaddyDrive = 0

#pinLED1 = 17
#pinLED2 = 18
#pinLED3 = 27

pinLED1 = 3
pinLED2 = 4
pinLED3 = 5

pinPump = 1

# max distance a bottle can be away to detect it is present
# * CHANGE HERE *
threshBottlePresent = 2





dispLED1 = 0
dispLED2 = 0
dispLED3 = 0
dispLED4 = 0
dispLED5 = 0

# HEF4051B configuration for the LED display

displayLED = [ [ 0, False, False, False ], \
    [ 0, False, False, True ],
    [ 0, False, True, False ],
    [ 0, False, True, True ],
    [ 0, True, False, False ],
    [ 0, True, False, True ],
    [ 0, True, True, False ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ],
    [ 0, True, True, True ] ]

# Piconzero pin to HEF mapping
# * CHANGE HERE *

pin1=LED(18)
pin2=LED(27)
pin3=LED(22)

def setLED():
   # set led states

    for p in range(0,8):
        if displayLED[p][0]:
            #            print( "LED %d on" % (p))
            if displayLED[p][3]:
                pin1.on()
            else:
                pin1.off()
            if displayLED[p][2]:
                pin2.on()
            else:
                pin2.off()
            if displayLED[p][1]:
                pin3.on()
            else:
                pin3.off()

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


# Preset fill programs (can be over ridden at control panel)

fillPrograms = [ 1, 5, 10, 15, 20, 40, 300, 1, 0, 0 ]
fillStage = 0



#def hcsr04Max():
#    # Take find the max from an avg of the samples to discount spurious readings
#    # v2 Or see if the presence threshold is counted significantly
#    m=0
#    t=0
#    for r in range(0,10):
#        sample =  int( hcsr04.getDistance() )
#        if sample <= threshBottlePresent :
#            t = t + 1
#        if sample > m :
#            m = sample
#        print( "Sample %d: %d t %d max %d" %  (r, sample, t,m) )
#
#        time.sleep(0.05)
#
#    print( "Final Sample %d t %d max %d" %  (sample, t,m) )
#    if t >= 8 :
#        print( "Mostly present" )
#        # 80% present
#        return  threshBottlePresent
#    return m

# Save and loading of the presets and user adjustments

def savePrograms():
    print( "Saving program settings to bottle.settings.")
    f = open( "bottle.settings","w" )
    for p in range(0,10):
        f.write("%d " % ( fillPrograms[p] ))
    f.close()

def loadPrograms():
    try:
        f = open( "bottle.settings","r" )
        print( "Loading programs from bottle.settings")
        p = f.read()
        fill = p.split(" ")
        f.close()
        for p in range(0, 10):
            fillPrograms[p]=int(fill[p])
    except:
        print( "No bottle.settings file found. Using code defaults and saving them.")
        savePrograms()

    print( "Current Programs")
    for p in range(0,6):
        fillPrograms[p]=int(fillPrograms[p])
        print("Program %d = %d" % ( p, fillPrograms[p]))

# Cycle through all the LEDS for a main transition indication

def cycleLEDS():
    for f in range(0,8):
        for s in range(0,8):
            displayLED[s][0]=0

        displayLED[f+1][0]=1
        setLED()
        time.sleep(0.25)




# init

# selection options
currentStage = stage.Init

l = 0

prevStage = stage.Selection
stageSetup = True
learnBlink = 0
#caddyPos = 0
#pipeStateIn = False

flashFlipFlop = 0
flashCt = 0

# handle selection and button bounce

fillSelection = 0
pressedSelection = False
pressedStartStop = False
pressedAdjust = False


# setup I/O

pz.setInputConfig( pinButSelection, 0, True )
pz.setInputConfig( pinButStartStop, 0, True )
#pz.setInputConfig( pinCaddyIn, 0, True )
#pz.setInputConfig( pinCaddyOut, 0, True )
pz.setInputConfig( pinBottleMark, 0, True )
pz.setInputConfig( pinButAdjustPreset, 0, True )

pz.setOutputConfig( pinLED1, 0 )
pz.setOutputConfig( pinLED2, 0 )
pz.setOutputConfig( pinLED3, 0 )

#pz.setOutputConfig( pinCaddyDrive, 2 )
#pz.setOutputConfig( pinFillInsert, 2 )

#pz.setOutput( pinCaddyDrive, caddySpeedStop )
#pz.setOutput( pinCaddyDrive, caddySpeedStop )
#pz.setOutputConfig( pinFillInsert, fillPipeOut )


# main loop

cycleLEDS()
cycleLEDS()
cycleLEDS()

# load presaved programs if present
loadPrograms()

stopBottle = False

while not stopBottle:
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
#        readSensors()
    #( senseButSelection, senseButStartStop, senseCaddyIn, senseBottlePresent ) = readSensors()

#def readSensors():
    senseButSelection = not pz.readInput( pinButSelection)
    senseButStartStop = not pz.readInput( pinButStartStop)
 #   senseCaddyIn = not pz.readInput( pinCaddyIn)
 #   senseCaddyOut = not pz.readInput( pinCaddyOut)
    senseBottleMark = not pz.readInput( pinBottleMark)
    senseButAdjustPreset = not pz.readInput( pinButAdjustPreset)

 #   senseBottlePresent = int( hcsr04.getDistance() )

#    print(" select %d" % ( senseButSelection ))
#return 
#        print( ": sel %d selbut %d ex %d start %d sel %d stage %d pres %d mrk %d in/out %d "        % ( fillSelection, senseButSelection, senseButAdjustPreset,  senseButStartStop,  pressedSelection,  currentStage,        senseBottlePresent, senseBottleMark, senseCaddyIn +  senseCaddyOut) )

#    if senseButSelection :
#        print "DIAG: Selection button pressed"

#    if senseButStartStop :
#        print "DIAG: Start/Stop button pressed"

    #if senseCaddyIn or senseCaddyOut :
    #    print "DIAG: Caddy in/out tripped"

#    if senseBottleMark :
#        print( "DIAG: Bottle mark tripped")

#    if senseButAdjustPreset :
#        print( "DIAG: Adjust preset button pressed")


#    if senseBottlePresent :
#        print( "DIAG: Bottle present sensor %d" % senseBottlePresent)
#        if senseBottlePresent < threshBottlePresent :
#            print( "DIAG: Bottle present sensor tripped %d" % senseBottlePresent)


    if currentStage != stage.Selection and currentStage != stage.Learn:
       # As process is running set the display to
       # be the current stage number
       for s in range(0,8):
            displayLED[s][0]=0
       displayLED[currentStage+1][0]=1


    if senseButStartStop and ( currentStage != stage.Selection and currentStage != stage.Learn ):
       # emergency stop if start button is pressed when running
#       if senseButStartStop :
            print(" emergency stop!")
            currentStage = stage.Selection
            stageSetup = True
            # stop pump
            pz.stop()
            # stop servo
#            pz.setOutput(pinCaddyDrive,caddySpeedStop )
            # take fill pipe out
#            pz.setOutput( pinFillInsert, fillPipeOut)
            cycleLEDS()
            cycleLEDS()


#????    if not senseButStartStop and pressedStartStop :
#            pressedStartStop = False


    elif currentStage == stage.Learn:
        if stageSetup : 
            print( "Entering learn mode for %d" % ( fillSelection ))
            displayLED[fillSelection][0]=0
            learnBlink = 0
            # set current pump count
            fillStage = 0
            pressedAdjust = False
            pressSelection = False

        if senseButAdjustPreset and not pressedAdjust :
            # selection button pressed
            pressedAdjust = True
            print( "Holding down adjust button in learn")

        if senseButSelection and not pressedSelection:
            # selection button pressed
            pressedSelection = True
            print( "Holding down selection button in learn")

        if senseButStartStop and not pressedStartStop:
            # selection button pressed
            pressedStartStop = True
            print( "Holding down start button in learn")

        if not senseButStartStop and pressedStartStop :
            # cancel adjustment
            print( "Cancel setting program %d" % ( fillSelection ))
            currentStage = stage.Selection
            time.sleep(3)

        elif not senseButAdjustPreset and pressedAdjust :
            print( "Exit adjustment for %d set at %d from %d" % ( fillSelection,  fillStage,fillPrograms[fillSelection]))
            # set and save the adjustments
            fillPrograms[fillSelection]=fillStage
            savePrograms()
            currentStage = stage.Selection
            pressedAdjust=False
            time.sleep(3)

        elif not senseButSelection and pressedSelection :
            fillStage = fillStage + 1
            print( "Do pump %d" % fillStage )
            pressedSelection = False
            pz.forward( fillSpeed)
            time.sleep(fillPulse)
            pz.stop()

#            print( "Blink state %d at %d " % ( displayLED[fillSelection][0], learnBlink ))
        # blink the current selection LED
        if learnBlink == 0 :
#                print ( "Blink led %d " %( displayLED[fillSelection][0]))
            if displayLED[fillSelection][0]:
                displayLED[fillSelection][0] = 0
                displayLED[7][0] = 1
            else:
                displayLED[7][0] = 0
                displayLED[fillSelection][0] = 1
            learnBlink = 50
            
        setLED()
            
        learnBlink = learnBlink - 1

    elif currentStage == stage.Selection:
        if stageSetup :
#            pz.setOutput( pinFillInsert, fillPipeOut)
            fillStage = 0
 #           pipeStateIn = False
            pressedAdjust = False
            pressedSelection = False

        for p in range(0,8):
            if fillSelection == p:
                displayLED[p][0]=1
            else:
                displayLED[p][0]=0

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
            currentStage = stage.Learn

        elif not senseButSelection and pressedSelection :
            # selection button has been released



            pressedSelection = False
            fillStage = 0
            
            # Cycle selection
            fillSelection = fillSelection + 1
            if fillSelection > 7:
                fillSelection = 0
            print( "Fill selection %d" % fillSelection )

        elif senseButSelection and senseButStartStop :
            pressedSelection = False
            fillStage = fillStage + 1
            print( "Run pump pulse %d counted %d " % ( fillPulse, fillStage ) )
            pz.forward( fillSpeed)
            time.sleep(fillPulse)
            pz.stop()

        elif not senseButAdjustPreset and pressedAdjust and senseButSelection :
            pressedAdjust = False
            pressedStartStop = False
#            print "Toggle fill pipe in and out"
#                pressedAdjust = False
#                senseButStartStop = False
            # toggle fill pipe in and out
#            if pipeStateIn:
#                pipeStateIn = False
#                pz.setOutput( pinFillInsert, fillPipeOut)
#            else:
#                pipeStateIn = True
#                pz.setOutput( pinFillInsert, fillPipeIn)
#            time.sleep(0.5)

        #    dispLED1 = True
        #    dispLED2 = True
        #    dispLED3 = True
        #    dispLED4 = True
        #    dispLED5 = True

        elif senseButStartStop and not senseButSelection and not pressedStartStop and not senseButAdjustPreset:
            # start the system
#                displayLED[0][0]=1
#                dispLED1 = True
#                dispLED2 = False
#                dispLED3 = False
#                dispLED4 = False
#                dispLED5 = False
#            if fillSelection == 6 :
#                print("Flush system program starting")
#                currentStage = stage.Filling
#                senseButStartStop = False
#            else:
                #print( "Start fill process")
            print( "Start fill bottle using program %d" % (fillSelection) )
            currentStage = stage.FindingBottleMark 

            time.sleep(1)
            cycleLEDS()

            if fillSelection == 7:
                print ("Power off")
                currentStage = stage.Selection
                stopBottle = True

#    elif currentStage == stage.LoadCaddy:
#        if stageSetup:
##                dispLED2 = True
#            # wait for liquid drips to clear
#            time.sleep(2)
#            pz.setOutput( pinFillInsert, fillPipeOut)
##                caddyPos = 0
##            time.sleep(2)
#        # TODO add sensor check and remove counter
#            pz.setOutput( pinCaddyDrive, caddySpeedOut )
#            print( "Roll caddy out")
#            # TODO sensor debounce
#            time.sleep(0.25)
#        else:
#            if senseCaddyOut:
#                print( "Caddy is out")
#                pz.setOutput( pinCaddyDrive, caddySpeedStop )
#                time.sleep(1)
#                pz.setOutput( pinCaddyDrive, caddySpeedStop )
#                pz.setOutput( pinCaddyDrive, caddySpeedIn )
#                # TODO sensor debounce
#                time.sleep(0.25)
#                currentStage = stage.FindingBottleMark
#        setLED()
        
    elif currentStage == stage.FindingBottleMark:

        if stageSetup:
#            pz.setOutput( pinFillInsert, fillPipeOut)
#            dispLED3 = True
#            dispLED4 = False
#            dispLED5 = False


 #           pz.setOutput( pinCaddyDrive, caddySpeedIn )
            print( "Finding bottle marker" )
            # TODO sensor debounce
            time.sleep(0.25)
        else:

            if senseBottleMark:
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
                time.sleep(1)
                currentStage = stage.Filling
  #              pz.setOutput( pinCaddyDrive, caddySpeedStop )

#            if senseCaddyIn :
#                print("At end of filling. Stop")
#                currentStage = stage.Selection
#                pz.setOutput( pinCaddyDrive, caddySpeedStop )
 #               time.sleep(1)
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
 #               pz.setOutput( pinFillInsert, fillPipeOut)
 #               cycleLEDS()
        setLED()
#    elif currentStage == stage.BottlePresentScan:
#        if stageSetup:
#            dispLED4 = True
#            dispLED5 = False
#            setLED()
#            # TODO sensor debounce
#            print( "Bottle present at this slot?" )
#            time.sleep(2)
#        else:
#            senseBottlePresent = hcsr04Max()
#            if senseBottlePresent <= threshBottlePresent :
#                # Bottle is present so fill it
#                currentStage = stage.FillInsert
#                print( "Yes" )
#            else:
#                # No bottle is present so find the next one
#                currentStage = stage.FindingBottleMark
#                print( "No" )
#    elif currentStage == stage.FillInsert:
#        setLED()
#        print( "Insert fill pipe" )
#        pz.setOutput( pinFillInsert, fillPipeIn)
#        time.sleep(2)
#        currentStage = stage.FillPause

#    elif currentStage == stage.FillPause:
#        if stageSetup:
#            dispLED4 = True
#            dispLED5 = False
#            setLED()
#            print( "Waiting before filling..." )
#            fillStage = 50
#            flashFlipFlop = 0
#            flashCt = 10
#        else:
#            flashCt = flashCt - 1
#            if flashCt == 0 :
#                if flashFlipFlop == 0:
#                        dispLED4 = True
#                        dispLED5 = False
#                        flashCt = 10
#                        flashFlipFlop = 1
#                else:
#                        dispLED4 = False
#                        dispLED5 = True
#                        flashCt = 10
#                        flashFlipFlop = 0
#
#            setLED()
#            if fillStage == 0 :
#                currentStage = stage.Filling
#            else:
#                time.sleep(0.5)
#                fillStage = fillStage - 1


    elif currentStage == stage.Filling:
        if stageSetup:
            dispLED5 = True
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
#                    time.sleep(1)
#                else:
#                    currentStage = stage.FindingBottleMark
#                    print "Reverse and pause to avoid drips after stopping pump"
#                    pz.forward( fillReverse)
#                    time.sleep(2)
                pz.stop()
#                    time.sleep(2)
#                    print "Withdraw filling pipe"
#                    pz.setOutput( pinFillInsert, fillPipeOut)
#                    time.sleep(0.5)
            else:
                print( "Filling pulse %d" % ( fillStage ))
                pz.forward(fillSpeed)
                time.sleep(fillPulse)
                pz.stop()
                fillStage = fillStage - 1

    elif currentStage == stage.Init:
        if stageSetup:
            #                dispLED2 = True
            pz.stop()
            cycleLEDS()
#            pz.setOutput( pinFillInsert, fillPipeOut)
#            caddyPos = 0
#            time.sleep(2)
        # TODO add sensor check and remove counter
 #           pz.setOutput( pinCaddyDrive, caddySpeedIn )
 #           print( "Roll caddy in")
            # TODO sensor debounce
            time.sleep(0.25)
 #       else:
 #           if senseCaddyIn:
 #               print( "Caddy is in")
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
 #               time.sleep(1)
 #               pz.setOutput( pinCaddyDrive, caddySpeedStop )
            currentStage = stage.Selection
        setLED()
        

#hcsr04.cleanup()

pz.cleanup()
os.system("sudo halt -p")
