import pygame
import math
from log import logError, logInfo


class Point:
    """Class representing 2D point"""
    def __init__(self, point=(0, 0)):
        if type(point) == Point:
            self.x = point.x
            self.y = point.y
        else:
            self.x = round(point[0])
            self.y = round(point[1])

    def __add__(self, pt):
        if type(pt) == Point:
            return Point((self.x + pt.x, self.y + pt.y))
        else:
            return Point((self.x + pt[0], self.y + pt[1]))

    def __sub__(self, pt):
        if type(pt) == Point:
            return Point((self.x - pt.x, self.y - pt.y))
        else:
            return Point((self.x - pt[0], self.y - pt[1]))

    def __mul__(self, other):
        return Point((self.x * other, self.y * other))

    def __truediv__(self, other):
        return Point((self.x / other, self.y / other))

    def __len__(self):
        return round(math.sqrt(self.x ** 2 + self.y ** 2))

    def get(self):
        """Converts Point class to tuple"""
        return self.x, self.y

    def min(self, other):
        """Returns point with x and y value greater than provided"""
        if type(other) == Point:
            return Point((min(self.x, other.x), min(self.y, other.y)))
        else:
            return Point((min(self.x, other[0]), min(self.y, other[1])))

    def max(self, other):
        if type(other) == Point:
            return Point((max(self.x, other.x), max(self.y, other.y)))
        else:
            return Point((max(self.x, other[0]), max(self.y, other[1])))


class UserInterface:
    """The base class for all elements of user interface
        Its aim is to provide methods for drawing which takes care of size and
        location of user interface segment.

    Attributes:
        screen: PyGame screen to be used
        loc: Point representing the location of upper-left corner
        size: Point representing size of segment
    """
    def __init__(self, screen, location, size):
        self.screen = screen
        self.loc = Point(location)
        self.size = Point(size)
        self.font = pygame.font.SysFont("monospace", 18)

    def inScreen(self, cords):
        """Cheks if provided Point is located inside segment"""
        assert (type(cords) == Point)
        return 0 <= cords.x <= self.size.x and 0 <= cords.y <= self.size.y

    def setPixel(self, cords, color):
        """Sets pixel to provided color if it is inside segment"""
        assert (type(cords) == Point)
        if self.inScreen(cords):
            self.screen.set_at((cords + self.loc).get(), color)
        else:
            logError('Point outside drawing area [X: {} Y: {}]'.format(cords.x, cords.y))

    def drawRect(self, cords, size, color, width=2):
        """Draws rectangle with provided cords, size, color and width"""
        pygame.draw.rect(self.screen, color, (self.loc + cords).get() + size.get(), width)

    def drawPolygon(self, points, color, width=0):
        pygame.draw.polygon(self.screen, color, [(p + self.loc).get() for p in points], width)

    def drawCircle(self, cords, radius, color):
        assert (type(cords) == Point)
        if self.inScreen(cords):
            pygame.draw.circle(self.screen, color, (cords + self.loc).get(), radius)
        else:
            logError('Circle outside drawing area [X: {} Y: {}]'.format(cords.x, cords.y))

    def drawLine(self, start, end, color):
        pygame.draw.line(self.screen, color, (start+self.loc).get(), (end+self.loc).get())

    def drawDashedLine(self, start, end, fillness, color):
        """Draws dashed line"""
        start = Point(start)
        end = Point(end)
        diff = end - start
        length = len(diff)
        pointsPerLine = fillness / length
        for dist in range(0, length // fillness, 2):
            p1 = start + diff * dist * pointsPerLine + self.loc
            p2 = start + diff * (dist + 1) * pointsPerLine + self.loc
            pygame.draw.line(self.screen, color, p1.get(), p2.get(), 1)

    def printText(self, text, pos, color):
        label = self.font.render(text, 1, color)
        self.screen.blit(label, (self.loc + pos).get())

    def printCenteredText(self, text, pos, size, color):
        """Prints text centered inside box with provided position and size"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            label = self.font.render(line, 1, color)
            offset = Point(((size.x - label.get_width()) // 2,
                            (size.y - (label.get_height() + 2) * len(lines)) // 2 + (label.get_height() + 2) * i))
            self.screen.blit(label, (self.loc + pos + offset).get())

    def clearView(self):
        """Fills segment with black color"""
        pygame.draw.rect(self.screen, (0, 0, 0), (self.loc.x, self.loc.y, self.size.x, self.size.y))


class UIGraph(UserInterface):
    """Class responsible of drawing chart with samples on it.

       Attributes:
           screen: PyGame screen to be used
           location: Point representing the location of upper-left corner
           size: Point representing size of segment
           division: Tuple containing information about number of divisions on graph
       """
    def __init__(self, screen, location, size, division=(16, 10)):
        super().__init__(screen, location, size)
        self.division = division
        self.divColor = (0, 90, 0)
        self.zeroDivs = (210, 210, 210)
        self.startOfCord = Point((0, self.size.y // 2))
        self.scale = [130, 0.5]
        self.freq = 10000
        self.numberOfSamples = 2000

    def drawBackground(self):
        """Clears segment and draws divisions"""
        self.clearView()
        for i in range(15):
            start = (self.size.x // 16 * (i + 1), 0)
            end = (start[0], self.size.y)
            color = self.zeroDivs if i == 7 else self.divColor
            self.drawDashedLine(start, end, 5, color)
        for i in range(9):
            start = (0, self.size.y // 10 * (i + 1))
            end = (self.size.x, start[1])
            color = self.zeroDivs if i == 4 else self.divColor
            self.drawDashedLine(start, end, 5, color)

    def setScale(self, scale=None):
        """Sets scale of graph"""
        if scale[0] <= 0 or scale[1] <= 0:
            raise ValueError("Can't set scale to value below 0")
        self.scale[0] = round(scale[0], 2)
        self.scale[1] = round(scale[1], 2)

    def incPos(self, scale):
        """Moves start of graph"""
        self.startOfCord += Point(scale)

    def incScale(self, scale):
        """Increases scale of graph"""
        self.scale[0] = round(max(self.scale[0] + scale[0], 0.1), 2)
        self.scale[1] = round(max(self.scale[1] + scale[1], 0.1), 2)

    def incFreq(self, freq):
        """Increses freqency of samples probing"""
        if self.freq < 500:
            freq //= 10
        self.freq = max(self.freq + freq, 1)

    def incNumberOfSamples(self, samples):
        """Increases number of samples"""
        self.numberOfSamples = max(self.numberOfSamples + samples, 1)

    def getParams(self):
        """Returns string containing information of current graph settings"""
        return str(round(self.scale[0] / self.freq * 1000, 1)) + 'ms/div', \
               str(self.scale[1]) + 'V/div', \
               str(round(9000 / self.freq, 1)) + 'kHz', \
               str(self.numberOfSamples)

    def scaleCords(self, cords):
        """Hepler method used to scale points before drawing them on screen"""
        assert (type(cords) == tuple)
        return Point((self.size.x / 16 * cords[0] / self.scale[0], (-1) * self.size.y / 10 * cords[1] / self.scale[1]))

    def draw(self, data=None):
        self.drawBackground()

        if type(data) != list:
            data = []
        lastPoint = None
        lastInterpolatedPoint = None
        for point in data:
            assert (type(point) == tuple)
            scaledPoint = self.scaleCords(point)
            interpolatedPoint = self.scaleCords((point[0], 3.3 if point[1] > 1.1 else 0))
            scaledPoint += self.startOfCord
            interpolatedPoint += self.startOfCord
            if self.inScreen(scaledPoint) and lastPoint is not None:
                self.drawLine(lastPoint, scaledPoint, (255, 126, 0))
            if self.inScreen(interpolatedPoint) and lastInterpolatedPoint is not None:
                self.drawLine(lastInterpolatedPoint, interpolatedPoint, (0, 166, 147))
            lastPoint = scaledPoint
            lastInterpolatedPoint = interpolatedPoint


class UIStatus(UserInterface):
    def __init__(self, screen, location, size):
        super().__init__(screen, location, size)

    def draw(self, graphParams=("None", "None"), triggerParams=""):
        self.clearView()
        pygame.draw.line(self.screen, (50, 50, 50), (self.loc.x, (self.loc + self.size).y),
                         (self.loc + self.size).get(), 1)

        self.printText('No: {4: <{w4}}     Trig: {0: <{w0}}    X: {1: <{w1}}    Y: {2: <{w2}}    F: {3: <{w3}}'
                       .format(triggerParams, graphParams[0], graphParams[1], graphParams[2], graphParams[3],
                               w0=max(10 - len(triggerParams), 0),
                               w1=max(10 - len(graphParams[0]), 0),
                               w2=max(10 - len(graphParams[1]), 0),
                               w3=max(10 - len(graphParams[2]), 0),
                               w4=max(10 - len(graphParams[3]), 0)),
                       Point((0, 0)), (255, 255, 255))


class UITrigger(UserInterface):
    def __init__(self, screen, location, size):
        super().__init__(screen, location, size)

        self.arrowHeight = 20
        self.arrowWidthRatio = 2 / 3
        self.triggerLevel = 1.2

    def setTriggerLevel(self, trigger):
        self.triggerLevel = trigger

    def incTriggerLevel(self, trigger):
        self.triggerLevel += trigger

    def scaleY(self, scale, y):
        return (-1) * self.size.y / 10 * y / scale[1]

    def getParams(self):
        return str(round(self.triggerLevel, 2)) + 'V'

    def drawArrow(self, color, text, scale):
        posOfMiddle = self.size / 2 + (0, self.scaleY(scale, self.triggerLevel))
        posOfMiddle = posOfMiddle.max((0, self.arrowHeight / 2)).min(self.size)
        self.drawRect(posOfMiddle - Point((posOfMiddle.x, self.arrowHeight / 2)),
                      Point((self.size.x * self.arrowWidthRatio, self.arrowHeight)),
                      color, 0)
        self.drawPolygon((
            Point((self.size.x * self.arrowWidthRatio, posOfMiddle.y - self.arrowHeight / 2)),
            Point((self.size.x * self.arrowWidthRatio, posOfMiddle.y + self.arrowHeight / 2 - 1)),
            Point((self.size.x, posOfMiddle.y))), color, 0)
        self.printText(text, Point((0, posOfMiddle.y - self.arrowHeight / 2)), (255, 255, 255))

    def draw(self, scale):
        self.clearView()
        pygame.draw.line(self.screen, (50, 50, 50), ((self.loc + self.size).x, self.loc.y),
                         (self.loc + self.size).get(), 1)
        self.drawArrow((110, 0, 40), '{0:.1f}'.format(self.triggerLevel), scale)


class MessageBox(UserInterface):
    BORDER_COLOR = (10, 90, 10)

    def __init__(self, screen, loc, size, message=''):
        super().__init__(screen, loc, size)
        self.message = message

    def draw(self):
        self.clearView()
        self.drawRect(Point((0, 0)), Point(self.size), self.BORDER_COLOR)
        self.drawRect(Point((10, 10)), Point(self.size) - Point((20, 20)), self.BORDER_COLOR)
        self.printCenteredText(self.message, (0, 0), self.size, (210, 210, 210))


class GUI:
    DFT_SCREEN_SIZE = (835, 620)
    DFT_MSGBOX_SIZE = (450, 200)
    DFT_MSGBOX_LOC = ((DFT_SCREEN_SIZE[0] - DFT_MSGBOX_SIZE[0]) // 2,
                      (DFT_SCREEN_SIZE[1] - DFT_MSGBOX_SIZE[1]) // 2)

    def __init__(self):
        logInfo('Starting pygame')
        pygame.init()

        self.screen = pygame.display.set_mode(self.DFT_SCREEN_SIZE)
        self.graph = UIGraph(self.screen, (35, 21), (800, 600))
        self.status = UIStatus(self.screen, (0, 0), (835, 20))
        self.trigger = UITrigger(self.screen, (0, 21), (35, 600))

    def draw(self, exData, msg=None):
        self.screen.fill((0, 0, 0))

        self.graph.draw(exData)
        self.status.draw(graphParams=self.graph.getParams(), triggerParams=self.trigger.getParams())
        self.trigger.draw(self.graph.scale)

        if msg is not None:
            MessageBox(self.screen, self.DFT_MSGBOX_LOC, self.DFT_MSGBOX_SIZE, msg).draw()
        pygame.display.update()
