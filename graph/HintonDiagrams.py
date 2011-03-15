# Got from:
# http://www.scipy.org/Cookbook/Matplotlib/HintonDiagrams
#
import numpy as N
import pylab as P

def _blob(x,y,area,colour):
    """
    Draws a square-shaped blob with the given area (< 1) at
    the given coordinates.
    """
    hs = N.sqrt(area) / 2
    xcorners = N.array([x - hs, x + hs, x + hs, x - hs])
    ycorners = N.array([y - hs, y - hs, y + hs, y + hs])
    P.fill(xcorners, ycorners, colour, edgecolor=colour)

def hinton(W, maxWeight=None, title=None, vlabels=None, hlabels=None):
    """
    Draws a Hinton diagram for visualizing a weight matrix. 
    Temporarily disables matplotlib interactive mode if it is on, 
    otherwise this takes forever.
    """
    P.figure()
    height, width = W.shape
    if not maxWeight:
        maxWeight = 2**N.ceil(N.log(N.max(N.abs(W)))/N.log(2))
    
    P.fill(N.array([0,width,width,0]),N.array([0,0,height,height]),'gray')
    if not vlabels and not hlabels: P.axis('off')
    P.axis('equal')
    for x in xrange(width):
        for y in xrange(height):
            _x = x+1
            _y = y+1
            w = W[y,x]
            if w > 0:
                _blob(_x - 0.5, height - _y + 0.5, min(1,w/maxWeight),'white')
            elif w < 0:
                _blob(_x - 0.5, height - _y + 0.5, min(1,-w/maxWeight),'black')
            P.text(_x-0.5, height - _y + 0.5, "%d" % w, horizontalalignment='center', verticalalignment='center', color='r')
    
    if vlabels: P.yticks(N.array(range(height))+0.5, list(reversed(hlabels)))
    if hlabels: P.xticks(N.array(range(width)) +0.5, hlabels)
    if title: P.title(title)
    
    P.gca().get_xaxis().tick_bottom()
    P.gca().get_yaxis().tick_left()

