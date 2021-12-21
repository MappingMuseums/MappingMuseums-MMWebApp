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
from random import shuffle
from numpy import pi 
import numpy as np 
import pandas as pd
import colorsys
from bokeh.layouts import layout 
from bokeh.models import ( 
  HoverTool, ColumnDataSource, Legend, LegendItem 
) 
from bokeh.plotting import figure 
from bokeh.palettes import brewer 
import datetime
from bokeh.models import DatetimeTickFormatter
from bokeh.models.glyphs import Rect as rect
from bokeh.models import CustomJS
from app.main import definitions
#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#   $$Author2$:Valeri Katerinchuk, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:valery.katerinchuk@gmail.com, License:GNU GPLv3
#
#We acknowledge the use of the following software under the terms of the specified licences:
#
#Python Flask - https://flask.palletsprojects.com/en/0.12.x/license/
#
#Bokeh - https://github.com/bokeh/bokeh/blob/master/LICENSE.txt
#
#
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LAST_YEAR=None
## Static init
today=datetime.datetime.today()
LAST_YEAR=today.year
#if (LAST_YEAR > 2020):
    #LAST_YEAR=2020
FIRST_YEAR=1960
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

PLOT_HEIGHT=850
PLOT_WIDTH=800
PLOT_WIDTH_SINGLE_CAT=180

LEGEND_GLYPH_HEIGHT=30
LEGEND_GLYPH_WIDTH=40


YEAR_FILTER="FILTER ((STRDT(?lv_Year_opened_3,xsd:positiveInteger) >  "+str(int(FIRST_YEAR - 1))+" ) && (STRDT(?lv_Year_closed_4,xsd:positiveInteger) <  "+str(LAST_YEAR)+"  ) )"
YEAR_FILTER4_OPEN="FILTER ((STRDT(?lv_Year_opened_4,xsd:positiveInteger) >  "+str(int(FIRST_YEAR - 1))+" ) && (STRDT(?uv_Year_opened_4,xsd:positiveInteger) <  "+str(LAST_YEAR)+" ) )"
##YEAR_FILTER3_OPEN="FILTER ((STRDT(?lv_Year_opened_3,xsd:positiveInteger) >  "+str(int(FIRST_YEAR - 1))+" ) && (STRDT(?uv_Year_opened_3,xsd:positiveInteger) <  "+str(LAST_YEAR)+" ) )"
##The above line was replaced with the below line to ensure heatmaps displayed museums open before 1960
YEAR_FILTER3_OPEN="FILTER ((STRDT(?uv_Year_opened_3,xsd:positiveInteger) <  "+str(LAST_YEAR)+" ) )"

YEAR_FILTER4_CLOSED="FILTER ((STRDT(?lv_Year_closed_4,xsd:positiveInteger) >  "+str(int(FIRST_YEAR - 1))+" )  )"
YEAR_FILTER5_CLOSED="FILTER ((STRDT(?lv_Year_closed_5,xsd:positiveInteger) >  "+str(int(FIRST_YEAR - 1))+" )  )"


MAX_CATEGORY_LINES=100
OPTIONS_KEY="#"
ACCUMULATE_TRUE=OPTIONS_KEY+"ACCUMULATE_TRUE"
ACCUMULATE_FALSE=OPTIONS_KEY+"ACCUMULATE_FALSE"

PLOT_LOCATION_KEY="location"   # Decorator
PLOT_GLOCATION_KEY="glocation" # as X/Y
PLOT_LOCATION_UK="UK"

SERVER_PATH="urlpath"

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @function
def translatepy2js(function):
    cs=CustomJS.from_py_func(function)
    cbtext=cs.code
    cbtext=cbtext.replace("return null;","source.change.emit();\n return null;")
    cs.code=cbtext
    return cs
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @N=5
def get_N_HexCol(N=5):

    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in xrange(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x*255),colorsys.hsv_to_rgb(*rgb))
        hex_out.append("#"+"".join(map(lambda x: chr(x).encode('hex'),rgb)))
    return hex_out

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 



## Purpose:Removes type info from name
# Arguments:
# 
# @N=5
# @random_color_order=True
# @reverse_color=False

def getColors(N=5,random_color_order=True,reverse_color=False):
    reverse_color = -1 if reverse_color else 1
    colors = palettes.viridis(N)[::reverse_color]
    if random_color_order:
	shuffle(colors)
    return colors

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @RGB1
# @ RGB2
# @n

def generateColorGradient(RGB1, RGB2, n):
    dRGB = [float(x2-x1)/(n-1) for x1, x2 in zip(RGB1, RGB2)]
    gradient = [tuple([int(x+k*dx) for x, dx in zip(RGB1, dRGB)]) for k in range(n)]
    return gradient


## Purpose:Removes type info from name
# Arguments:
# 
# @RGB1
# @RGB2
# @n

def generateColorGradientHex(RGB1, RGB2, n):
    dRGB = [float(x2-x1)/(n-1) for x1, x2 in zip(RGB1, RGB2)]
    gradient = [tuple([int(x+k*dx) for x, dx in zip(RGB1, dRGB)]) for k in range(n)]
    hex_out=[]
    for rgb in gradient:
        hex_out.append("#"+"".join(map(lambda x: chr(x).encode('hex'),rgb)))
	
    return hex_out

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

'''
Input a string without hash sign of RGB hex digits to compute
complementary contrasting color such as for fonts
'''
    

## Purpose:Removes type info from name
# Arguments:
# 
# @input_hex_str
def contrasting_text_color(input_hex_str):
    if (input_hex_str.find("#") > -1):
	hex_str=input_hex_str[1:]
    else:
	hex_str=input_hex_str
	
    (r, g, b) = (hex_str[:2], hex_str[2:4], hex_str[4:])
    rval='000' if 1 - (int(r, 16) * 0.299 + int(g, 16) * 0.587 + int(b, 16) * 0.114) / 255 < 0.5 else 'fff'
    if (input_hex_str.find("#") > -1):
	return "#"+str(rval)
    else:
	return rval


## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

## Purpose:Removes type info from name
# Arguments:
# 
# @whatwearelookingfor
# @str

def getOccurances(whatwearelookingfor,str):
	
    start = occ = 0
    while start >= 0:
	pos = str.find(whatwearelookingfor, start)
	if pos < 0:
	    break
	occ += 1
	start = pos + len(whatwearelookingfor)
    return occ
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

## Purpose:Removes type info from name
# Arguments:
# 
# @whatwearelookingfor
# @inocc
# @str

def getStrToOccurance(whatwearelookingfor,inocc,str):
	
    start =  0
    occ   =  0
    while start >= 0:
	pos = str.find(whatwearelookingfor, start)
	if pos < 0:
	    break
	occ += 1
	if (occ == inocc):
	    return str[0:pos]
	start = pos + len(whatwearelookingfor)
    return None

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @res
# @topic
# @topictype
# @subtarget

def getSubFromtimeandcat(res,topic,topictype,subtarget):
    if (topictype == definitions.DEFINED_LISTTYPE):
        sub=res[topic]["value"]
	if (subtarget.endswith("-")):
	    # no subcats
	    return [sub]
	compare=topic+"-"+sub.replace(" ","_")
	if (compare.startswith(subtarget)):
	    return [sub]
	else:
            return []
    elif (topictype == definitions.DEFINED_HIERTYPE):
	allsubs=[]
	sub=res[topic]["value"]
	parts=sub.split("/")
	plen=len(parts)-1
	if (subtarget.endswith("-")):
	    # Top level, show only next level
	    scat=parts[plen].split("-")
	    sub=topic+"-"+scat[0]
	else:
	    sub=topic+"-"+parts[plen]
	comparelen=len(subtarget)-1
	#if (sub.startswith(subtarget)):
	if (sub[0:comparelen] == subtarget[0:comparelen]):
	    # If sub is a subclass then we remove the subclasses, note the plus one to remove from +level of subclasses
	    classcount=getOccurances(definitions.HIER_SUBCLASS_SEPARATOR,subtarget)+1 
	    thisclasscount=getOccurances(definitions.HIER_SUBCLASS_SEPARATOR,sub)
	    if (thisclasscount > classcount):
		sub=getStrToOccurance(definitions.HIER_SUBCLASS_SEPARATOR,thisclasscount,sub)
	    allsubs.append(sub)
		
	return allsubs
    elif (topictype == "ALL"):
        return topictype

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @res
# @topic
# @topictype
# @subtarget

def getSubFromtimeandcatOLD(res,topic,topictype,subtarget):
    if (topictype == "LISTTYPE"):
        sub=res[topic]["value"]
	if (subtarget.endswith("-")):
	    # no subcats
	    return [sub]
	compare=topic+"-"+sub.replace(" ","_")
	if (compare.startswith(subtarget)):
	    return [sub]
	else:
            return []
    elif (topictype == "HIERTYPE"):
	allsubs=[]
	sub=res[topic]["value"]
	parts=sub.split("/")
	plen=len(parts)-1
	if (subtarget.endswith("-")):
	    # Top level, show only next level
	    scat=parts[plen].split("-")
	    sub=topic+"-"+scat[0]
	else:
	    sub=topic+"-"+parts[plen]
	comparelen=len(subtarget)-1
	if (sub[0:comparelen] == subtarget[0:comparelen]):
	    allsubs.append(sub)
		
	return allsubs
    elif (topictype == "ALL"):
        return topictype

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @res
# @topic
# @subtarget

def getSubFromLocation(res,topic,subtarget):
    sub=res[topic]["value"]
    parts=sub.split("/")
    
    return [ parts[-1] ]

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @res
# @topic

def getSubFromLocationAtomic(res,topic):
    sub=res[topic]["value"]
    parts=sub.split("/")
    
    return parts[-1]
#    return parts[-1].replace("_"," ") 

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

## Purpose:Removes type info from name
# Arguments:
# 
# @inpar
def remove_options(inpar):
    newparameters=[]
    for p in inpar:
	if (not p.startswith(OPTIONS_KEY)):
	    newparameters.append(p)
    return newparameters


## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

## Purpose:Removes type info from name
# Arguments:
# 
# @key
def makeLegendKey(key):
    newkey=key
    if ( key.find("-") > -1):
	parts=key.split("-")
	newkey=parts[-1]
    if (newkey == definitions.YEAR_EXISTS):
	newkey="All"
    return newkey.replace("_"," ")


## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

# convert RGB tuple to hexadecimal code

## Purpose:Removes type info from name
# Arguments:
# 
# @rgb
def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

# convert hexadecimal code to RGB tuple  

## Purpose:Removes type info from name
# Arguments:
# 
# @inhex
def hex_to_rgb(inhex):
    h=inhex.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

# convert hexadecimal to RGB tuple

## Purpose:Removes type info from name
# Arguments:
# 
# @hex
def hex_to_dec(hex):
    red = ''.join(hex.strip('#')[0:2])
    green = ''.join(hex.strip('#')[2:4])
    blue = ''.join(hex.strip('#')[4:6])
    return (int(red, 16), int(green, 16), int(blue,16))

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
