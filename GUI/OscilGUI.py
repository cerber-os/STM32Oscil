#!/usr/bin/env python3
import sys
from log import logInfo, logError
from GUITools import GUI
from serialCom import SerialCom
import pygame
from time import sleep
import serial

expectingData = False


################################
# Main program
################################
def processUserInput(gui, serial):
    global expectingData
    scaleGraphLUT = {pygame.K_UP: (0, 0.1), pygame.K_DOWN: (0, -0.1), pygame.K_LEFT: (-0.1, 0),
                     pygame.K_RIGHT: (0.1, 0)}
    posGraphLUT = {pygame.K_a: (10, 0), pygame.K_d: (-10, 0)}
    scaleTriggerLUT = {pygame.K_i: 0.1, pygame.K_j: -0.1}
    freqLUT = {pygame.K_z: 10000, pygame.K_x: -10000}
    samplesLUT = {pygame.K_n: -100, pygame.K_m: 100}
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logInfo('Exiting...')
            pygame.quit()
            exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key in scaleGraphLUT:
                gui.graph.incScale(scaleGraphLUT[event.key])
                return True
            elif event.key in scaleTriggerLUT:
                gui.trigger.incTriggerLevel(scaleTriggerLUT[event.key])
                serial.setTriggerLevel(gui.trigger.triggerLevel)
                return True
            elif event.key in posGraphLUT:
                gui.graph.incPos(posGraphLUT[event.key])
                return True
            elif event.key in freqLUT:
                gui.graph.incFreq(freqLUT[event.key])
                serial.setPrecision(gui.graph.freq)
                return True
            elif event.key in samplesLUT:
                gui.graph.incNumberOfSamples(samplesLUT[event.key])
                if serial.setNumberOfSamples(gui.graph.numberOfSamples):
                    gui.graph.incNumberOfSamples(samplesLUT[event.key] * (-1))
                return True
            elif event.key == pygame.K_SPACE:
                if serial.triggerNow() == 0:
                    expectingData = True
                return True
            elif event.key == pygame.K_o:
                serial.turnOff()
                return True
            elif event.key == pygame.K_p:
                if serial.trigMode() == 0:
                    expectingData = True
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                gui.graph.incScale((0.5, 0))
                return True
            elif event.button == 5:
                gui.graph.incScale((-0.5, 0))
                return True
    return False


def main():
    global expectingData, serialCom
    if len(sys.argv) != 2:
        logError('Please provide serial port as first argument')
        exit(1)

    try:
        serialCom = SerialCom(sys.argv[1])
    except serial.serialutil.SerialException as e:
        logError('Could not open serial port: {}'.format(e.args[1]))
        exit(1)

    gui = GUI()
    gui.draw([], 'Looking for device')
    while serialCom.ping() != 0:
        gui.draw([], 'Device is not responding to\nPING command\nCheck connection\n\nRetrying...')
        sleep(1)

    gui.draw([], 'Device is connected\n\nSending initial configuration')
    actions = [{'job': serialCom.setTriggerLevel, 'name': 'Setting trigger level', 'value': 1},
               {'job': serialCom.setMode, 'name': 'Setting mode', 'value': 0},
               {'job': serialCom.setNumberOfSamples, 'name': 'Setting number of samples', 'value': gui.graph.numberOfSamples},
               {'job': serialCom.setPrecision, 'name': 'Setting frequency', 'value': gui.graph.freq}]
    for action in actions:
        gui.draw([], 'Device is connected\n\nSending initial configuration\n\n' + action['name'])
        while action['job'](action['value']) != 0:
            sleep(3)
            gui.draw([], 'Device is connected\n\nSending initial configuration\n\nRetrying: ' + action['name'])

    gui.draw([])
    exData = []
    while True:
        message = None
        while not (expectingData and serialCom.isDataAvail()) and not processUserInput(gui, serialCom):
            sleep(0.3)

        if expectingData and serialCom.isDataAvail():
            (status, exData) = serialCom.downloadData()
            if status:
                expectingData = False
            else:
                message = 'Downloading samples failed\nCommunication error\noccurred\n\nPress any key'

        gui.draw(exData, message)


if __name__ == '__main__':
    main()
