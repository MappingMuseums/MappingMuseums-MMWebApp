from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral10
from bokeh.palettes import Category20_20
from bokeh import palettes
from numpy import pi
from random import shuffle
import colorsys
from bokeh.layouts import layout 
from bokeh.models import ( 
  HoverTool, ColumnDataSource, Legend, LegendItem 
) 
from bokeh.plotting import figure 
from bokeh.palettes import brewer 
from bokeh.core.properties import value
import numpy as np
from numpy import pi
from random import shuffle
from math import sin,cos
from bokeh.plotting import ColumnDataSource,output_notebook,figure
from bokeh.models import HoverTool,Text
from bokeh import palettes
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.palettes import brewer

# Thanks to Alex Fung 

from SPARQLWrapper import SPARQLWrapper, JSON


# !@!!!   [musenv][/home/nlarsson/bbk/python/webdev/museumflask]python -m app.main.boktest

__name__ ="app.main.bokradar"
__package__ = "app.main"


# ## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, LabelSet

num_vars = 9

theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
# rotate theta such that the first axis is at the top
theta += np.pi/2

def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.
    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

def radar_patch(r, theta):
    yt = (r + 0.01) * np.sin(theta) + 0.5
    xt = (r + 0.01) * np.cos(theta) + 0.5
    return xt, yt

verts = unit_poly_verts(theta)
x = [v[0] for v in verts] 
y = [v[1] for v in verts] 

p = figure(title="Radar")
text = ['Sulfate', 'Nitrate', 'EC', 'OC1', 'OC2', 'OC3', 'OP', 'CO', 'O3']
source = ColumnDataSource({'x':x+ [0.5],'y':y+ [1],'text':text})

p.line(x="x", y="y", source=source)

labels = LabelSet(x="x",y="y",text="text",source=source)

p.add_layout(labels)

# example factor:
f1 = np.array([0.88, 0.01, 0.03, 0.03, 0.00, 0.06, 0.01, 0.00, 0.00]) * 0.5
f2 = np.array([0.07, 0.95, 0.04, 0.05, 0.00, 0.02, 0.01, 0.00, 0.00]) * 0.5
f3 = np.array([0.01, 0.02, 0.85, 0.19, 0.05, 0.10, 0.00, 0.00, 0.00]) * 0.5
f4 = np.array([0.02, 0.01, 0.07, 0.01, 0.21, 0.12, 0.98, 0.00, 0.00]) * 0.5
f5 = np.array([0.01, 0.01, 0.02, 0.71, 0.74, 0.70, 0.00, 0.00, 0.00]) * 0.5
#xt = np.array(x)
flist = [f1,f2,f3,f4,f5]
colors = ['blue','green','red', 'orange','purple']
for i in range(len(flist)):
    xt, yt = radar_patch(flist[i], theta)
    p.patch(x=xt, y=yt, fill_alpha=0.15, fill_color=colors[i])
show(p)

