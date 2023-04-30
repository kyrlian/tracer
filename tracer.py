#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# TRACER v1.7 - Kyrlian 2013-2018
# python 3 compatible

# Changelog
# 1.0: basic drawing
# 1.1: stress-based colors
# 1.2: input/display random seed
# 1.3: new method to find locks : contour
# 1.4: findpath is no longer recursive
# 1.5: tweaked rewind
# 1.6: using nested functions for more clarity, and added high level recursivity (grid in grid)
# 1.7: more color settings
# 1.73 : rewriten for python 3

import random, time, turtle

################################
# CONFIG

#   GRID
gridSizeW = 32  # W : x : rows : dont go up too fast, can be really long to complete depending on your hardware - up to 16 is easy, up to 27 is ok, 28/29 never work, 30 ok (seed 1682156647)
# Size : Seed
# 30 : 1682156647
gridSizeH = gridSizeW  # H : y : cols
gridLevels = 1  # 1-n #KEEP THIS LOW : FINAL GRID SIZE WILL BE GRIDSIZEW^GRIDLEVEL*GRIDSIZEH^GRIDLEVEL
#   REWIND
allowRewind = True  # Allow rewind, set to False to test all possible solutions, True is more efficient
rewindMoreSteps = 5  # Number of steps to rewind if I am blocked, 1-10 gives good results
#   STRESS - USED FOR COLOR CHANGE
colorSpeed = 0.1#0 for not color change
stressUp = 10  # 0-10 gives good results
stressDown = stressUp
#   DRAWING
drawSpeed = 1000 # print one move in N, 1-1000 is good
drawFence = False #draw the grid external fence, useless
bgColor = "black"#background
fgColor = "white"#forground
colorMode = "len" #stress, len, fgColor
################################
      
def intersect(a, b):
    return list(set(a).intersection(set(b)))

def exclude(a, b):
    return list(set(a).difference(set(b)))
   
def findPath(startPosition, destinationPosition, zeroPosition, initialStress, bDraw):  
    # Functions
    def translate(position):
        return (position[0] + zeroPosition[0], position[1] + zeroPosition[1])
        
    def initGrid():
        for y in range(gridSizeH):
            row = []
            for x in range(gridSizeW):
                row.append(0)
            grid.append(row)
    
    def isInGrid(position):
        x, y = position
        return x > -1 and y > -1 and x < gridSizeW and y < gridSizeH
    
    def getGrid(position):
        x, y = position
        return grid[y][x]
    
    def setGrid(position, val):
        #nonlocal is python 3 only
        nonlocal grid
        x, y = position
        grid[y][x] = val
    
    def printGrid():
        print("========")
        for y in range(gridSizeH):
            line = ''
            for x in range(gridSizeW):
                v = getGrid((x, y))
                if(v > 0):
                    line = line + str(v)
                else:
                    line = line + "."
            print(line)
        
    def goto(gridPos):
        screenPos = translate(gridPos)
        turtle.setposition(screenPos)

    def drawMove(gridPos, stress):
            def hueToRGB(H, S, V):  # Convert HUE (0-360) to RGB values
                #http://en.wikipedia.org/wiki/Hue
                # S=1#Saturation : 0=black, 1=Color
                M = int(255 * V)
                m = int(M * (1 - S))
                z = int((M - m) * (1 - abs((H / 60) % 2 - 1)))
                if H < 60:
                    R = M
                    G = z + m
                    B = m
                    return (R, G, B)
                if H < 120:
                    R = z + m
                    G = M
                    B = m
                    return (R, G, B)
                if H < 180:
                    R = m
                    G = M
                    B = z + m
                    return (R, G, B)
                if H < 240:
                    R = m
                    G = z + m
                    B = M
                    return (R, G, B)
                if H < 300:
                    R = z + m
                    G = m
                    B = M
                    return (R, G, B)
                else:
                    R = M
                    G = m
                    B = z + m
                    return (R, G, B)
                
            def stressToRGB(stress):
                H = 360 - ((len(path) + stress)*colorSpeed) % 360
                # H = 360 - stress%360
                V = 1  # len(path)/(gridSizeH*gridSizeW)#0-1
                S = 1
                return hueToRGB(H, S, V)

            def lenToRGB():
                H = 360 - (len(path)*colorSpeed) % 360  # 0-360
                V = 1  # len(path)/(gridSizeH*gridSizeW)#0-1
                S = 1
                return hueToRGB(H, S, V)

            turtle.color(stressToRGB(stress))
            if colorMode == "fgColor":
                turtle.color(fgColor)                    
            if colorMode == "len":
                turtle.color(lenToRGB())
            goto(gridPos)
            # print("drawMove:",gridPos,stress)
      
    def goForward(gridPos, stress, remainingPositions):
        nonlocal path, pathRemainingPositions, pathStress
        path.append(gridPos)
        pathRemainingPositions.append(remainingPositions)
        pathStress.append(stress)
        setGrid(gridPos, 1)
        if bDraw:
            drawMove(gridPos, stress)
        
    def rewind():
        nonlocal path, pathRemainingPositions, pathStress
        def eraseMove(gridPos):
            turtle.color(bgColor)
            goto(gridPos)
            # print("eraseMove:",position(),screenPos)
            
        erasePos = path.pop(len(path) - 1)
        # eraseChoices = pathRemainingPositions.pop(len(pathRemainingPositions)-1)
        stress = pathStress.pop(len(pathStress) - 1)
        if bDraw:
            eraseMove(path[len(path) - 1])
        setGrid(erasePos, 0)
        if(len(path) < len(pathRemainingPositions)):
            remainingPositions = pathRemainingPositions.pop(len(pathRemainingPositions) - 1)      
        return (stress, erasePos)

    def getvalidPositionsUsingContour(currPos):  # Check that I dont block the deck, and returns the valid positions around me
        nonlocal lastContourSize
        
        def getNearPositionsUsing(currPos, usingMoves):
            nearPositions = []
            for move in usingMoves:
                newPos = (currPos[0] + move[0], currPos[1] + move[1])
                if isInGrid(newPos) and getGrid(newPos) == 0:
                    nearPositions.append(newPos)
            return nearPositions

        def doContour():  # Starts from destination, runs with towerMoves around the white area
            def getClockWiseDir(position, currentDir):  # go left or forward or right or back
                i = towerMoves.index(currentDir)
                for j in range(len(towerMoves)):
                    newDir = towerMoves[(i - j + 1) % len(towerMoves)]
                    newPos = (position[0] + newDir[0], position[1] + newDir[1])
                    if isInGrid(newPos) and getGrid(newPos) == 0:
                        # print("getClockWiseDir:newPos:",newPos,"newDir:",newDir)
                        return newDir
            
            alertPosition = (0, 0)
            alert = False
            checkedList = []
            currPos = destinationPosition
            
            firstMove = towerMoves[0]#First move should go OUTSIDE the grid
            for move in towerMoves:
                testP = (destinationPosition[0]+move[0],destinationPosition[1]+move[1])
                if isInGrid(testP)==False:
                    firstMove = move
                    break                    
            
            currentDir = getClockWiseDir(destinationPosition, firstMove)
            if currentDir == None:
                return (alert, alertPosition, [destinationPosition])   
            testPosition = (currPos[0] + currentDir[0], currPos[1] + currentDir[1]) 
            while testPosition != destinationPosition:
                # print("doContour:testPosition",testPosition)
                checkedList.append(testPosition)
                currentDir = getClockWiseDir(testPosition, currentDir)
                testPosition = (testPosition[0] + currentDir[0], testPosition[1] + currentDir[1])
                if testPosition in checkedList and alert == False:  # if finds itself again : alert : potential deadlock
                    alertPosition = testPosition
                    alert = True
            # print("doContour:",alert,alertPosition,checkedList)
            return (alert, alertPosition, checkedList)

        def getPriorityPositions(currPos):  # If among the near positions, one has only 1 exit (adjacent free cell), I want to go there
            nearPositions = getNearPositionsUsing(currPos, towerMoves)
            potentialDeadEnds = []
            for position in nearPositions:
                if position != destinationPosition:  # Target is a normal dead end
                    # setGrid(position,2)
                    exits = len(getNearPositionsUsing(position, towerMoves))
                    if exits == 0:  # One of the cells has 0 exits : KO
                        return []
                    if exits == 1:  # One of the cells has 1 exit: should go there
                        potentialDeadEnds.append(position)
                    # setGrid(position,0)
            if len(potentialDeadEnds) == 1:
                # if potentialDeadEnds[0] != destinationPosition:
                return potentialDeadEnds
            if len(potentialDeadEnds) > 1:  # more that one dead end : no solution                
                return []
            return nearPositions

        def tryPosition(possiblePosition):  # Check if filling this cell would block/split the deck
            setGrid(possiblePosition, 2)
            res = doContour()
            setGrid(possiblePosition, 0)
            # print("tryPosition",possiblePosition,":",res)
            return res

        (alert, alertPosition, checkedList) = doContour()  # Check that I am not blocking the deck AND do early detection  
        newLen = len(checkedList)
        # print("getvalidPositionsUsingContour:lastContourSize:",lastContourSize,"newLen:",newLen)
        if newLen < (lastContourSize - 2):  # when returning to destination, the count should be stable : not decrease by more than 2
            return ([])  # We have blocked, return nothing so we rewind
        else:
            lastContourSize = newLen
            # validPositions = getNearPositionsUsing(currPos,towerMoves)
            validPositions = getPriorityPositions(currPos)
            if len(path) < (gridSizeW * gridSizeH) - 1:
                validPositions = exclude(validPositions, [destinationPosition])  # Destination should only be reached on full deck !
            if alert == True:  # Alerte : detection de l'impasse
                (alert, alertPosition, checkedList) = tryPosition(alertPosition)  # bloquer l'endroit du croisement et faire un checkLock(contour? bucket?) pour savoir ou any
                validPositions = exclude(validPositions, alertPosition)
                validPositions = exclude(validPositions, checkedList)
        # print("getvalidPositionsUsingContour:",validPositions)
        return validPositions


    # Globals
    towerMoves = ((1, 0), (0, -1), (-1, 0), (0, 1))  # Must be clockwise or counter clockwize
    # bishopMoves=((1,1),(-1,-1),(-1,1),(1,-1))
    # allMoves = list(set(towerMoves).union(set(bishopMoves)))
    # Init
    def init():
        nonlocal path, grid, pathRemainingPositions, pathStress, lastContourSize, stress
        path = []   
        path.append(startPosition)
        grid = []
        initGrid()
        setGrid(startPosition, 1)    
        pathRemainingPositions = []
        pathStress = []
        lastContourSize = 2 * (gridSizeW + gridSizeH - 2)
        stress = initialStress
            
    # Loop
    def traceLoop():
        nonlocal stress
        deadEndsCache = []
        status = "Continue"
        maxPathLen = 0
        rewindedSteps = 0
        while len(path) > 0:        
            currPos = path[len(path) - 1]
            # print("currPos:",currPos,",status:",status,",stress:",stress,"path:",len(path),"pathRemainingPositions:",len(pathRemainingPositions))
            # print("path(",len(path),"):",path)
            # print("pathRemainingPositions(",len(pathRemainingPositions),"):",pathRemainingPositions)        
            # Success conditions
            if len(path) == (gridSizeW * gridSizeH):
                #print("findPath:Done!")
                return "OK"
            if currPos == destinationPosition:
                #print("Arrived at destination!")
                return "OK"
    
            # Going forward
            if status == "Continue":  # and len(path) > 1:
                # Get or compute positions
                if(len(path) > len(pathRemainingPositions)):  # First time
                    remainingPositions = getvalidPositionsUsingContour(currPos)
                    random.shuffle(remainingPositions)
                    # print("firstTime:remainingPositions:",remainingPositions)
                else:  # Returning (after a rollback)
                    # remainingPositions = pathRemainingPositions[len(pathRemainingPositions)-1]
                    remainingPositions = pathRemainingPositions.pop(len(pathRemainingPositions) - 1)
                    # print("returning:remainingPositions:",remainingPositions)      
                stress += (3 - len(remainingPositions))
                if stress < 0:
                    stress = 0
    
                if len(remainingPositions) > 0:  # still some positions to test - go forward
                    position = remainingPositions.pop(0)  # get test position and remove it from remaining positions
                    goForward(position, stress, remainingPositions)  # go forward and store remaining positions
                    # print("pathRemainingPositions(",len(pathRemainingPositions),"):",pathRemainingPositions)  
                    status = "Continue"
                    # print("Going Forward")
                    if allowRewind and len(path) > maxPathLen:  # I went farther : clear the deadEnds cache
                        maxPathLen = len(path)
                        if(len(deadEndsCache) > 0):
                            # print("Farther:Clearing deadEndsCache")    
                            deadEndsCache = []
                else:  # no more positions to test : rewind                
                    status = "Rewind"
            # Going backward
            else:  # I hit a dead end - or I am rewinding
                    if len(path) == 1:  # its time to restart
                        return "KO"
                    # print("Dead End!")
                    (stress, erasePos) = rewind()              
                    if allowRewind:
                        if status == "Rewind More":  # I am rewinding, should I continue ?
                            rewindedSteps += 1
                            if rewindedSteps > rewindMoreSteps:  # Stop rewinding
                                rewindedSteps = 0
                                # print("StopRewind:Clearing deadEndsCache")    
                                # deadEndsCache = []
                                # print("StopRewind:pathRemainingPositions:",pathRemainingPositions)   
                                status = "Continue"
                        else:  # not rewinding yet - should we start to rewind ?
                            if (erasePos in deadEndsCache):  # If I was stuck in the same place:yes
                                status = "Rewind More"
                                # print("Rewind More")
                            else:
                                deadEndsCache.append(erasePos)
                                # if len(deadEndsCache)>20:
                                    # deadEndsCache.pop(0)                                
                                status = "Continue"
                    else:
                        status = "Continue"
        return "KO"

    path = []
    grid = []
    pathRemainingPositions = []
    pathStress = []
    lastContourSize = 2 * (gridSizeW + gridSizeH - 2)
    stress = initialStress     
    init()
    if bDraw:
        drawMove(startPosition, initialStress)
    while traceLoop() != "OK":
        #print("findPath:Restarting!")
        init()
        turtle.update()
    turtle.update()

    if bDraw:
        return len(path) + stress
    else:
        return path

def drawInit(startPosition, destinationPosition, randomSeed):
    def drawWorldLimit():
        if drawFence:
            turtle.penup()
            turtle.setposition(-.5, -.5)
            turtle.color(fgColor)
            turtle.pensize(1)
            turtle.pendown()
            turtle.setposition(-.5, screenSizeH - .5)
            turtle.setposition(screenSizeW - .5, screenSizeH - .5)
            turtle.setposition(screenSizeW - .5, -.5)
            turtle.setposition(-.5, -.5)
            turtle.penup()
    
    def drawDestinationPosition():
        turtle.penup()
        turtle.color(fgColor)
        turtle.pensize(penSize)
        turtle.setposition((destinationPosition[0] * (screenSizeW-1) / (gridSizeW-1), destinationPosition[1] * (screenSizeH-1) / (gridSizeH-1)))
        turtle.pendown()
        turtle.forward(0)
        turtle.penup()
    
    def drawSignature():
        turtle.penup()
        turtle.color(fgColor)
        #turtle.setposition(((1 - 3 / 20) * screenSizeW, -1 / 20 * screenSizeH))
        signW = 35/40*screenSizeW
        signH = min(-1/25*screenSizeH,-1)
        turtle.setposition((signW , signH))
        signature = "Path n�" + str(randomSeed)
        turtle.write(signature, False, "left", ("Arial", 10, "normal"))
    
    screenSizeW = pow(gridSizeW, gridLevels)
    screenSizeH = pow(gridSizeH, gridLevels)
    penSize = 400 / screenSizeW
    # getcanvas() #to resize canvas ?
    turtle.screensize(screenSizeW, screenSizeH, bgColor)
    turtle.setworldcoordinates(-1, -1, screenSizeW, screenSizeH)  # shift for better clarity    
    turtle.shape("turtle")
    turtle.tracer(drawSpeed)
    turtle.speed(0)
    turtle.colormode(255)
    turtle.hideturtle()
    drawWorldLimit()
    drawSignature()
    drawDestinationPosition()    
    turtle.penup()
    turtle.setposition(startPosition)
    turtle.pendown()
    turtle.pensize(penSize)
    
def refinePath(startPosition, destinationPosition, zeroPosition, initialStress, recursionLevel):  
    if recursionLevel == 1:  # at lowest level : draw
        #print("refinePath:Drawing lowest level")
        newStress = findPath(startPosition, destinationPosition, zeroPosition, initialStress, True)
        return newStress
    else:  # not at lowest yet, recurse
        #print("refinePath:Refining at level:",recursionLevel)
        highPath = findPath(startPosition, destinationPosition, zeroPosition, initialStress, False)        
        endPx = 0  # for initialisation only
        endPy = 0  # for initialisation only
        stress = initialStress
        for iPath in range(len(highPath)):
            if iPath == 0:
                startPx = startPosition[0]
                startPy = startPosition[1]
            else:
                if highPath[iPath - 1][0] < highPath[iPath][0]:
                    startPx = 0
                if highPath[iPath - 1][0] > highPath[iPath][0]:
                    startPx = gridSizeW - 1
                if highPath[iPath - 1][0] == highPath[iPath][0]:
                    startPx = endPx#Previous end
                if highPath[iPath - 1][1] < highPath[iPath][1]:
                    startPy = 0
                if highPath[iPath - 1][1] > highPath[iPath][1]:
                    startPy = gridSizeH - 1
                if highPath[iPath - 1][1] == highPath[iPath][1]:
                    startPy = endPy#Previous end        
            startP = (startPx, startPy)
            
            if iPath == len(highPath) - 1:
                endPx = destinationPosition[0]
                endPy = destinationPosition[1]
            else:
                endPx = startPx
                endPy = startPy
                if highPath[iPath + 1][0] < highPath[iPath][0]:
                    endPx = 0
                if highPath[iPath + 1][0] > highPath[iPath][0]:
                    endPx = gridSizeW - 1
                if highPath[iPath + 1][1] < highPath[iPath][1]:
                    endPy = 0
                if highPath[iPath + 1][1] > highPath[iPath][1]:
                    endPy = gridSizeH - 1
                if highPath[iPath + 1][0] == highPath[iPath][0]:#I dont care where I end on x
                    if endPy == startPy:#but If I end on start for y, I want to have a different x
                        if startPx == 0:
                            endPx = gridSizeH - 1
                        else:
                            endPx = 0 
                if highPath[iPath + 1][1] == highPath[iPath][1]:#I dont care where I end on y
                    if endPx == startPx:#but If I end on start for x, I want to have a different y
                        if startPy == 0:
                            endPy = gridSizeH - 1
                        else:
                            endPy = 0                             
            endP = (endPx, endPy)
# REVOIR CALCUL DECAL en CAS de RECURSION            
            decalW = (highPath[iPath][0] + zeroPosition[0]) * gridSizeW
            decalH = (highPath[iPath][1] + zeroPosition[1]) * gridSizeH
            zeroP = (decalW, decalH)
# REVOIR CALCUL STRESS en CAS de RECURSION            
            stress = refinePath(startP, endP, zeroP, stress, recursionLevel - 1)        
    #print("refinePath:Finished a level:",recursionLevel)
    return stress
     
#   RUN
def main():
    #   RANDOM
    def getRandomSeed():
        randomSeedPrompt = input("Random Seed?")
        if(len(randomSeedPrompt) == 0):
            randomSeed = str(int(time.time()))
        else:
            randomSeed = str(randomSeedPrompt)
        print("Random Seed:[", randomSeed, "]")
        random.seed(randomSeed)
        return randomSeed
    
    #   START - DESTINATION
    startPosition = (0, 0)  # Relative to high level grid - of gridSize
    # startPosition=(random.randint(0,gridSizeW-1) ,random.randint(0,gridSizeH-1))
    destinationPosition = (gridSizeW - 1, 0)  # Relative to high level grid - of gridSize
    # destinationPosition=(random.randint(0,gridSizeW-1) ,random.randint(0,gridSizeH-1))#NOTE:Some random positions are unreachable
    randomSeed = getRandomSeed()
    drawInit(startPosition, destinationPosition, randomSeed)
    zeroPosition = startPosition
    initialStress = 0
    recursionLevel = gridLevels
    refinePath(startPosition, destinationPosition, zeroPosition, initialStress, recursionLevel)
    turtle.update()
    print("Finished!")
    turtle.done()#Turtle will fait for input     

main()
# EOF

