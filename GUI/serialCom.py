import serial
import struct


class SerialCom:
    """Class providing support for communication with MCU over serial port"""

    """Dict representing ids of available commands"""
    commandCodes = {'SET_TRIGGER':    0,
                    'SET_MODE':       1,
                    'PING':           2,
                    'SET_SAMPLES':    3,
                    'TRIG_NOW':       9,
                    'IS_DATA_AVAIL':  5,
                    'DOWNLOAD_DATA':  6,
                    'TURN_OFF':       7,
                    'TRIG_MODE':      8,
                    'SET_PRECISION':  4}

    def __init__(self, devicePath):
        self.serial = serial.Serial(devicePath, 38400, timeout=3)

    def sendPacket(self, cmd='PING', payload=b''):
        """Sends command and its payload to MCU"""
        data = struct.pack('B', self.commandCodes[cmd]) + payload
        self.serial.write(data)
        self.serial.flush()

    def getResponseStatus(self):
        """Gets status report from MCU. Returns -1 if timeout occurres"""
        resp = self.serial.read(1)
        if len(resp) != 1:
            return -1
        return struct.unpack('B', resp)[0]

    def ping(self):
        """Wrappers for sending commands"""
        self.sendPacket(cmd='PING', payload=b'')
        return self.getResponseStatus()

    def setTriggerLevel(self, triggerLevel):
        self.sendPacket(cmd='SET_TRIGGER', payload=struct.pack('I', round(triggerLevel * 1000)))
        return self.getResponseStatus()

    def setMode(self, mode):
        self.sendPacket(cmd='SET_MODE', payload=struct.pack('B', mode))
        return self.getResponseStatus()

    def setNumberOfSamples(self, count):
        self.sendPacket(cmd='SET_SAMPLES', payload=struct.pack('I', count))
        return self.getResponseStatus()

    def setPrecision(self, prec):
        self.sendPacket(cmd='SET_PRECISION', payload=struct.pack('I', prec))
        return self.getResponseStatus()

    def triggerNow(self):
        self.sendPacket(cmd='TRIG_NOW')
        return self.getResponseStatus()

    def isDataAvail(self):
        self.sendPacket(cmd='IS_DATA_AVAIL')
        return self.getResponseStatus() != 0

    def turnOff(self):
        self.sendPacket(cmd='TURN_OFF')
        return self.getResponseStatus()

    def trigMode(self):
        self.sendPacket(cmd='TRIG_MODE')
        return self.getResponseStatus()

    def downloadData(self):
        """Tries to download samples from device
                Returns tuple consisting of: (state, data), where
                    state = True | False  -  indicated if operation succedded
                    data  = list of tuples - samples sent by MCU in form (no, sample)"""
        self.sendPacket(cmd='DOWNLOAD_DATA')

        resp = self.getResponseStatus()
        if resp != 0:
            return False, []

        # Downloading data
        samples = []
        length = struct.unpack("I", self.serial.read(4))[0]
        for i in range(length):
            sample = (i, struct.unpack("H", self.serial.read(2))[0]/1000)
            samples.append(sample)

        endBlock = struct.unpack("B", self.serial.read(1))[0]
        if endBlock != 0xff:
            return False, []
        return True, samples
