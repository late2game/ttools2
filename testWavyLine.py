######################
# Python Boilerplate #
######################

### Modules
import drawingFunctions
reload(drawingFunctions)
from drawingFunctions import calcWavyLine

### Constants

### Function & procedures
def drawWavyLine(wavyPoints):
    newPath()
    moveTo(wavyPoints[0])
    for eachBcpOut, eachBcpIn, eachPt in wavyPoints[1:]:
        curveTo(eachBcpOut, eachBcpIn, eachPt)
    drawPath()

### Variables
pt1 = 100, 200
pt2 = 400, 500

oval(pt1[0]-2, pt1[1]-2, 4, 4)
oval(pt2[0]-2, pt2[1]-2, 4, 4)

waveLength = 10
waveHeight = 8

fill(None)
stroke(0)

wavyPoints = calcWavyLine(pt1, pt2, waveLength, waveHeight, pseudoSquaring=.7)
drawWavyLine(wavyPoints)

pt1 = 300, 100
pt2 = 100, 500

fill(0)
stroke(None)
oval(pt1[0]-2, pt1[1]-2, 4, 4)
oval(pt2[0]-2, pt2[1]-2, 4, 4)

fill(None)
stroke(0)
wavyPoints = calcWavyLine(pt1, pt2, waveLength, waveHeight, pseudoSquaring=.7)
drawWavyLine(wavyPoints)









