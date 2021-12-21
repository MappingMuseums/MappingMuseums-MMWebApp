from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.models import HoverTool, ColumnDataSource,Title
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
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.plotting import figure 
from bokeh.palettes import brewer 
import datetime
from bokeh.models import DatetimeTickFormatter
from bokeh.models.glyphs import Rect as rect
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
)
from bokeh.models.widgets import DateSlider,RangeSlider, DateRangeSlider,Slider, Div
from bokeh.models.layouts import Row, Column, WidgetBox
from bokeh.models.widgets import DateSlider,RangeSlider, DateRangeSlider,Slider, Div
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import gridplot,row,widgetbox


from . import bokutils

from app.main import apputils
from app.main import definitions
from app.main import listman

from flask import render_template, redirect, url_for, abort, flash, request, make_response
import copy
from . import bokutils,bokehtimeandcategory
#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
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


class BokehHeatmap():
    TIME="Time"
    YEAR_EXISTS='Year_exists'
    LOCATION='Location'

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @namelist
# @results

    def getDataParts(namelist,results):
        ddict={}
	name=namelist[0]
	

        if (name == bokutils.PLOT_GLOCATION_KEY):
            for res in results["results"]["bindings"]:
                if (bokutils.PLOT_GLOCATION_KEY in res):
		    aname=bokutils.getSubFromLocation(res,bokutils.PLOT_GLOCATION_KEY,None)
                    if (not aname[0] in ddict):
                        ddict[aname[0]]=0
        elif (name == BokehHeatmap.LOCATION):
            for res in results["results"]["bindings"]:
                if (definitions.GEOADMNAME  in res):
                    aname=res[definitions.GEOADMNAME]["value"]
                    if (not aname in ddict):
                        ddict[aname]=0
        else:
            ntype=apputils.getDefinedType(name)
            dtype=definitions.DATATYPEDICT[ntype]
            if (dtype == definitions.DEFINED_HIERTYPE):
                subprops=listman.getList("defClass"+name+definitions.LISTNAME)
                sortedsubprops=sorted(subprops)
    
		if (len(namelist) > 1):
		    jname="-".join(namelist[1:])
		    jname=jname+"-"
		    classcount=bokutils.getOccurances(definitions.HIER_SUBCLASS_SEPARATOR,jname)
		    subclasses=[]
		    newprops=[]
		    for sub in sortedsubprops:
			thisclasscount=bokutils.getOccurances(definitions.HIER_SUBCLASS_SEPARATOR,sub)
			if (thisclasscount > classcount):
			    baseclass=bokutils.getStrToOccurance(definitions.HIER_SUBCLASS_SEPARATOR,thisclasscount,sub)
			elif (sub.startswith(jname)):
			    newprops.append(sub)

		    sortedsubprops=newprops
		    

		    for sub in sortedsubprops:
			if (sub.startswith(jname)):
			    ddict[sub]=0

		else:
		    for sub in sortedsubprops:
			parts=sub.split("-")
			if ( parts[0] not in ddict ):
			    ddict[parts[0]]=0
            
            elif (dtype == definitions.DEFINED_LISTTYPE):
                subprops=listman.getList(name+definitions.LISTNAME)
                sortedsubprops=sorted(subprops)
		if (len(namelist) > 1):
		    jname="-".join(namelist[1:])
		    for sub in sortedsubprops:
			if (sub.startswith(jname)):
			    ddict[sub]=0
		else:
		    for sub in sortedsubprops:
			ddict[sub]=0
    
            elif (dtype == "xsd:positiveInteger"):
		sortedsubprops=apputils.getIntegerAsList(name)
		if (len(namelist) > 1):
		    jname="-".join(namelist[1:])
		    for sub in sortedsubprops:
			if (sub.startswith(jname)):
			    ddict[sub]=0
		else:
		    for sub in sortedsubprops:
			ddict[sub]=0
	
	print ddict		
	return ddict
            
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @res
# @topic
# @topictype
# @flag=None

    def getSubValue(res,topic,topictype,flag=None):
        if (topictype == definitions.DEFINED_LISTTYPE):
	    tlen=len(topic)
	    if (topic[0] in res):
		sub=res[topic[0]]["value"]
		if (tlen > 1):
		    if (sub == topic[1]):
			return sub
			#return sub.replace("_"," ")
		    else:
			return ""
		else:
		    return sub
		    #return sub.replace("_"," ")
	    else:
		return ""
        elif (topictype == definitions.DEFINED_HIERTYPE):
	    if (topic[0] in res):
		sub=res[topic[0]]["value"]
		parts=sub.split("/")
		plen=len(parts)-1
		sub=parts[plen]
		return BokehHeatmap.comparesubhier(sub,topic)
	    else:
		return ""
	elif (topic[0] == bokutils.PLOT_GLOCATION_KEY):
            sub=res[bokutils.PLOT_GLOCATION_KEY]["value"]
	    return bokutils.getSubFromLocationAtomic(res,bokutils.PLOT_GLOCATION_KEY)
	elif (topic == definitions.GEOADMNAME):
            sub=res[topic]["value"]
	    return sub
	    #return sub.replace("_"," ")

        elif (topic[0] in res):
            sub=res[topic[0]]["value"]
	    return sub
        else:

            return None
        
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @dbname
# @topic

    def comparesubhier(dbname,topic):
	# If topic is 1 there is no subspec for the hier, matches all, but dictionary is only on first level so
	# only return the first level
	if (len(topic) == 1):
	    dbparts=dbname.split("-")
	    return dbparts[0]
	else:
	    # We check hierarchy match
	    tlen=len(topic)
	    topstart=1
	    dbparts=dbname.split("-")
	    dlen=len(dbparts)
	    found=True
	    while (topstart < tlen and topstart-1 < dlen):
		if (dbparts[topstart-1] != topic[topstart]):
		    found=False
		topstart=topstart+1
	    if (found):
		jname="-".join(dbparts[:topstart])
		return jname
	    
	    else:
		return ""
		
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @ n
    def create_n_dimensional_matrix( n):
        dimensions = len(n)
        if (dimensions == 1): 
            return [0 for i in range(n[0])]

        if (dimensions == 2): 
            return [[0 for i in range(n[0])] for j in range(n[1])]

        if (dimensions == 3): 
            return [[[0 for i in range(n[0])] for j in range(n[1])] for k in range(n[2])]

        if (dimensions == 4): 
            return [[[[0 for i in range(n[0])] for j in range(n[1])] for k in range(n[2])] for l in range(n[3])]

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @Xname
# @Yname
# @factorsx
# @factorsy
# @results
# @firstyear
# @lastyear

    def getCountMatrix(Xname,Yname,factorsx,factorsy,results,firstyear,lastyear):
	
	observations=0
	if (str(type(Xname)) == "<type 'list'>"):
	    DXname=Xname[0]
	else:
	    DXname=Xname
	if (str(type(Yname)) == "<type 'list'>"):
	    DYname=Yname[0]
	else:
	    DYname=Yname

	    
	
        rowlen=len(factorsx)
        collen=len(factorsy)

	if (Xname ==  BokehHeatmap.LOCATION):
	    Xname=definitions.GEOADMNAME
	    Xtype="xsd:string"
	elif (Xname[0] ==  bokutils.PLOT_GLOCATION_KEY):
	    Xtype="xsd:string"
	elif (Xname ==  bokutils.PLOT_GLOCATION_KEY):
	    Xtype="xsd:string"
	else:
	    ntype=apputils.getDefinedType(Xname[0])
	    Xtype=definitions.DATATYPEDICT[ ntype ]

	    
	    
	if (Yname ==  BokehHeatmap.LOCATION):
	    Yname=definitions.GEOADMNAME
	    Ytype="xsd:string"
	elif (Yname[0] ==  bokutils.PLOT_GLOCATION_KEY):
	    Ytype="xsd:string"
	else:
	    ntype=apputils.getDefinedType(Yname[0])
	    Ytype=definitions.DATATYPEDICT[ntype]

	    
        ylen=lastyear-firstyear+1
        countmatrix=BokehHeatmap.create_n_dimensional_matrix([rowlen,collen,ylen])
        maxval=-1
	xycount=0
	xycount=0

        for res in results["results"]["bindings"]:
            pid=res["museum"]["value"]
            xval=""
            yval=""
            if (Xname[0] in res):
                xval=BokehHeatmap.getSubValue(res,Xname,Xtype,flag=True)
		
	    if (Yname[0] in res):
                yval=BokehHeatmap.getSubValue(res,Yname,Ytype)

	    if  (xval != "" and yval != ""):
		xycount=xycount+1
                xind=-1
                yind=-1
                if (xval in factorsx):
                    xind=factorsx.index(xval)
                if (yval in factorsy):
                    yind=factorsy.index(yval)


                if (xind > -1 and yind > -1):
                    if (definitions.YEAR_OPENED in res):
                        openyear=res[definitions.YEAR_OPENED]["value"]
                        parts=openyear.split(":")
                        startrange=int(parts[0])
                        endrange=int(parts[1])
			if (endrange > bokutils.LAST_YEAR):
			    endrange=bokutils.LAST_YEAR
			if (startrange > bokutils.LAST_YEAR):
			    startrange=bokutils.LAST_YEAR


			if (endrange < bokutils.FIRST_YEAR):
			    endrange=bokutils.FIRST_YEAR
			if (startrange < bokutils.FIRST_YEAR):
			    startrange=bokutils.FIRST_YEAR


                        loopstart=startrange-firstyear
                        loopend=endrange-firstyear+1
                        rlen=(loopend-loopstart)
                        ##frac=float(1)/float(rlen) ##Nick's Original line 
                        for t in range(loopstart,loopend):
                            ##Corrected logic conforming to Logic 1
                            frac=float(t-loopstart+1)/float(rlen)
                            countmatrix[t][yind][xind]=countmatrix[t][yind][xind] + frac
                            if (countmatrix[t][yind][xind] > maxval):
                                maxval=countmatrix[t][yind][xind]
                            
                            print frac
                        ##print 'loopend'
                        periodstart=loopend
                    if (definitions.YEAR_CLOSED in res):
                        openyear=res[definitions.YEAR_CLOSED]["value"]
                        parts=openyear.split(":")
                        startrange=int(parts[0])
                        endrange=int(parts[1])
			if (endrange > bokutils.LAST_YEAR):
			    endrange=bokutils.LAST_YEAR
			if (startrange > bokutils.LAST_YEAR):
			    startrange=bokutils.LAST_YEAR
			if (endrange < bokutils.FIRST_YEAR):
			    endrange=bokutils.FIRST_YEAR
			if (startrange < bokutils.FIRST_YEAR):
			    startrange=bokutils.FIRST_YEAR
                        loopstart=startrange-firstyear
                        loopend=endrange-firstyear+1
                        rlen=(loopend-loopstart)
                        ##frac=float(1)/float(rlen) ##Nick's original line
                        for t in range(loopstart,loopend):
                            ##Corrected logic conforming to Logic 1
                            frac=float(loopend-t)/float(rlen) 
                            countmatrix[t][yind][xind]=countmatrix[t][yind][xind] + frac
                            if (countmatrix[t][yind][xind] > maxval):
                                maxval=countmatrix[t][yind][xind]
                            
                            print frac
                        periodend=loopstart
                        print 'loopend2'
                    if (definitions.YEAR_CLOSED in res and definitions.YEAR_OPENED in res):
			observations=observations+1
                        for t in range(periodstart,periodend):
                            countmatrix[t][yind][xind]=countmatrix[t][yind][xind] + float(1)
                            if (countmatrix[t][yind][xind] > maxval):
                                maxval=countmatrix[t][yind][xind]

                                
        print "Found "+str(xycount)+" number of matching museums"  
        print countmatrix        
        return countmatrix,maxval,observations
    
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @parameters
# @bgcolor
# @contextdict

    def getHeatMap(results,parameters,bgcolor,contextdict):      
        
	
        Yname=parameters[2]
        Xname=parameters[3]
        
        Xdict=BokehHeatmap.getDataParts(Xname,results)
        Ydict=BokehHeatmap.getDataParts(Yname,results)
	
        #colours row wise
        factorsx = sorted(list(Xdict))
        factorsy = sorted(list(Ydict),reverse=True)

	
        rowlen=len(factorsx)
        collen=len(factorsy)
	
        countmatrix,maxval,observations=BokehHeatmap.getCountMatrix(Xname,Yname,factorsx,factorsy,results,bokutils.FIRST_YEAR,bokutils.LAST_YEAR)
        print 'countmatrix'
        print countmatrix
        print 'maxval'
        print maxval
        print 'observations'
        print observations
        rate=[]
	LOWVALUE=1
	HIGHVALUE=int(float(maxval)+float(0.5))-1
	COLOURBAR=True
	hcolors=bokutils.generateColorGradientHex(bokutils.hex_to_rgb(bgcolor), (255,204,204), 4)
	hcolors=["#0C7D03","#489D42","#85BE81","#C2DEC0"]
	textcolors=hcolors[::-1]
	
        for i,items in enumerate(factorsx):
	    factorsx[i]=bokutils.makeLegendKey(items)
	for i,items in enumerate(factorsy):
	    factorsy[i]=bokutils.makeLegendKey(items)
        x=[]
        y=[]
        totcount=0
        # Initialise with last year as base
        for col in range(collen):
            for row in range(rowlen):
                print countmatrix[-1][col][row]
                x.append(factorsx[row])
                y.append(factorsy[col])
                count=int(countmatrix[-1][col][row]+float(0.5))
                print count
                rate.append(count)
                totcount=totcount+count


	
	if (totcount == 0):
	    COLOURBAR=False
	    HIGHVALUE=float(2)
	    LOWVALUE=float(0.8)
	elif (HIGHVALUE == -1):
	    COLOURBAR=False
	    HIGHVALUE=1
	elif (HIGHVALUE == 0):
	    COLOURBAR=False
	    HIGHVALUE=float(0.9)
	    LOWVALUE=float(0.8)
	elif (HIGHVALUE == 1):
	    HIGHVALUE=float(1.9)
	    LOWVALUE=float(0.8)
	    textcolors=["#C2DEC0"]
	    hcolors=["#0C7D03"]
	elif (HIGHVALUE <= LOWVALUE):
            HIGHVALUE=float(HIGHVALUE) - 0.1
	    LOWVALUE=float(HIGHVALUE - 0.1)
	    COLOURBAR=False
	

        mapper = LinearColorMapper(palette=textcolors, high=float(HIGHVALUE),low=float(LOWVALUE),low_color="white",high_color="#45334C")
        source = ColumnDataSource(
            data=dict(
                x=x,
                y=y,
                rate=rate
                )
            )
        print 'count matrix again'
        print countmatrix
        allsource = ColumnDataSource(data=dict(ratebyyear=countmatrix))
        print 'allsource'
        print allsource

        textmapper = LinearColorMapper(palette=hcolors[:],  high=maxval)

        TOOLS = "hover,save"

	if (str(type(Xname)) == "<type 'str'>"):
	    DXname=Xname
	else:
	    DXname=Xname[0]
	if (str(type(Yname)) == "<type 'str'>"):
	    DYname=Yname
	else:
	    DYname=Yname[0]


	if (DXname == bokutils.PLOT_GLOCATION_KEY or DXname == bokutils.PLOT_GLOCATION_KEY):
	    location=parameters[5]
	    title="Visualisations/Plot/X = "+location[1:]+" Y = "+"/".join(Yname).replace("_"," ")
	else:
	    location=", location="+str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	    title="Visualisations/Plot/X = "+"/".join(Xname).replace("_"," ")+" Y = "+"/".join(Yname).replace("_"," ")

	#Visualisations/Plot/X = Governance/Independent Y = Classification 2018 

	
	
        p = figure(title=title,
                   x_range=factorsx, y_range=factorsy,
                   x_axis_location="above", plot_width=900, plot_height=900,
                   tools=TOOLS, toolbar_location='below')
#		   border_fill_color=hcolors[0])

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "10pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi / 3

        labels = LabelSet(x='x', y='y', text='rate', level='glyph',text_color={'field': 'rate', 'transform': textmapper},
                          x_offset=-10, y_offset=-10, source=source, render_mode='canvas')
        p.rect(x="x", y="y", width=1, height=1,
               source=source,
               fill_color={'field': 'rate', 'transform': mapper},
               line_color="white")
       
	if (COLOURBAR):
	    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
				 ticker=BasicTicker(desired_num_ticks=len(hcolors)),
				 formatter=PrintfTickFormatter(format="%d"),
				 label_standoff=6, border_line_color=hcolors[0], location=(0, 0))
	    p.add_layout(color_bar, 'right')
	    
	p.add_layout(Title(text="X", align="center"), "below")
	p.add_layout(Title(text="Y", align="center"), "left")
	p.add_layout(Title(text="Colour to count legend", align="center"), "right")

        p.add_layout(labels)
        p.select_one(HoverTool).tooltips = [
            ('Point', '@y # @x'),
            ('Count', '@rate '),
            ]


        slider = Slider(start=bokutils.FIRST_YEAR,
                        end=bokutils.LAST_YEAR,
                        value=bokutils.LAST_YEAR,
                        step=1,
                        title='Year',
			bar_color=hcolors[0])
        

        paramsource = ColumnDataSource(data=dict(params=[rowlen,collen]))

        
        callback = CustomJS(args=dict(source=source,
                                      slider=slider,
                                      plot=p,
                                      window=None,
                                      source2=allsource,
                                      source3=paramsource),
        code="""
        var cb;
        cb = function (source,
                       slider,
                       plot,
                       window,
                       source2,
                       source3)
        {
          var al, arr, data, end, i;
          source = (source === undefined) ? source: source;
          //console.log("slider "+slider);
          slider = (slider === undefined) ? slider: slider;
          plot = (plot === undefined) ? p: plot;
          window = (window === undefined) ? null: window;
          data = source.data;
          
          var arr = source.data["rate"];
          //console.log("rate"+arr);
          var allcounts=source2.data["ratebyyear"];
          //console.log(allcounts);
          var params=source3.data["params"];
          var rowlen=params[0];
          var collen=params[1];
          //console.log("arrlen"+arr.length);
          //console.log("rowlen"+rowlen);
          //console.log("collen"+collen);

          var startidx=slider.value - 1960;
          //console.log("START"+startidx);
          var i=0;
          var j=0;
          var tot=0;

          while (j < collen)
            {
             while (i < rowlen)
              {
                arr[tot] = Math.round(allcounts[startidx][j][i]);
                i = i + 1;
                tot=tot+1;
              }
              j = j + 1;
              i=0;
            }




        //console.log("TOT="+tot);
        //console.log("rate"+arr);
        source.change.emit();

        return null;
        };
        cb(source, slider, plot,window,source2,source3);

        """)

        slider.js_on_change('value', callback)

        wb=widgetbox(children=[slider], sizing_mode='scale_width')
        thisrow=Column(children=[p, wb],sizing_mode='scale_both')

        return thisrow

    

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createPlot(self,me,parameters,contextdict):
	colorptr=len(parameters)-1
	incolor=parameters[colorptr]
	del parameters[colorptr]
	

	if (me == bokutils.PLOT_GLOCATION_KEY):
	    
	    columns=[]
	    columns.append(parameters[3][0])
	    results=apputils.getVizLocationData(parameters[4],
						bokutils.FIRST_YEAR,
						bokutils.LAST_YEAR,
						columns,
						locationname=me)
 	    locs=", "
 	    for l in parameters[4]:
 		locs=locs+str(l)+","
 	    parameters.append(locs[:len(locs)-1])
 	    parameters[2]=parameters[3]
 	    parameters[3]=[me]
	    locs=", "
	    for l in parameters[2]:
		locs=locs+str(l)+","
	    parameters.append(locs[:len(locs)-1])
	    plot = BokehHeatmap.getHeatMap(results,parameters,incolor,contextdict)
	    
	else:
	    location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	    props=[definitions.PROJECT_ID,
		   me[0]]
	    markerdict=None
	    filters=[]

	    if (location != bokutils.PLOT_LOCATION_UK):
		markerdict={}
		markerdict['${GEOENTITY}']=str(location)
		props.append(definitions.GEOCOL)

	    for p in parameters:
		if (str(type(p)) == "<type 'list'>"):
		    props.append(p[0])
		else:
		    props.append(p)

	    filters.append(bokutils.YEAR_FILTER3_OPEN)
	    filters.append(bokutils.YEAR_FILTER4_CLOSED)
            
	    results=apputils.getMarkerData(props,filters,markerdict)

	    parameters.append(me)
	    plot = BokehHeatmap.getHeatMap(results,parameters,incolor,contextdict)
               
        return plot

