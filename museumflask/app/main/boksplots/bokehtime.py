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

from . import bokutils

from app.main import apputils
from app.main import definitions
from flask import render_template, redirect, url_for, abort, flash, request, make_response
import copy
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


class BokehTime():
    TIME="Time"
    YEAR_EXISTS='Year_exists'


## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


# Logics 4 and 5 called only for All (Openings and closings over time)
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @timedict
# @topic

    def getTimeDataset(results,timedict,topic):
	firstyear=bokutils.FIRST_YEAR
	lastyear=bokutils.LAST_YEAR
	
        countobs=0
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
		countobs=countobs+1
		openyear=res[topic]["value"]
		parts=openyear.split(":")
		##print parts
        # Fixed
		for t in range(firstyear,lastyear+1):
		    if (topic == definitions.YEAR_OPENED):
			fo=int(parts[0])
			to=int(parts[1])

                        if (t < fo or to < t):
                            nop=0
                        else:
                            idx=t-firstyear
                            if (t >= fo and t <= to):
                                if (t not in timedict):
                                    propdict={}
                                    propdict[topic]=0
                                    timedict[t]=propdict
                                propdict=timedict[t]
                                frac=float(1)/float(to-fo+1)
                                propdict[topic]=propdict[topic]+frac
		    else:
			fc=int(parts[0])
			tc=int(parts[1])
			
                        if (t < fc or tc < t):
                            nop=0
                        else:
                            idx=t-firstyear
                            if (t >= fc and t <= tc):
                                if (t not in timedict):
                                    propdict={}
                                    propdict[topic]=0
                                    timedict[t]=propdict
                                propdict=timedict[t]
                                frac=float(1)/float(tc-fc+1)
				if (topic not in propdict):
				    propdict[topic]=0
                                propdict[topic]=propdict[topic]+frac

			    
        for skey, sval in timedict.iteritems():
	    for pkey, pval in sval.iteritems():
 		sval[pkey]=int(sval[pkey]+float(0.5))

                    
    
        return timedict

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @timedict
# @topic
# @firstyear
# @lastyear

    def getOpenOverTimeDataSet(results,timedict,topic,firstyear,lastyear):
	
        musdict={}
        inyear=definitions.YEAR_OPENED
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            sub=""
            if (topic  in res):
		sub=res[topic]["value"]
            openyear=""
            closeyear=""
            if (definitions.YEAR_OPENED in res):
                openyear=res[definitions.YEAR_OPENED]["value"]
            if (definitions.YEAR_CLOSED in res):
                closeyear=res[definitions.YEAR_CLOSED]["value"]
            if (openyear == "" or closeyear == "" or sub == ""):
                nop=0
            else:
                musdict[uri]=(openyear,closeyear,sub)
                        

        countobs=0
        for key, val in musdict.iteritems():
	    countobs=countobs+1
            openyear,closeyear,sub=val
            parts=openyear.split(":")
            fo=int(parts[0])
            to=int(parts[1])

            parts=closeyear.split(":")
            fc=int(parts[0])
            tc=int(parts[1])
	    # changed
	    for t in range(firstyear,lastyear+1):
		if (t < fo or t > tc):
		    nop=0
		else:
		    idx=t-firstyear
		    if (t > to and t < fc):
			buckets[idx]=buckets[idx]+float(1)
		    else:
			if (t >= fo and t <= to):
			    frac=float(t - fo + 1)/float(to - fo + 1)
			    buckets[idx]=buckets[idx]+frac
			if (t >= fc and t <= tc):
			    frac=float(tc - t+1)/float(tc - fc + 1) 
			    buckets[idx]=buckets[idx]+frac



        for i in range(firstyear,lastyear):
	    y=i-firstyear
	    timedict[i]={topic:int(buckets[y]+float(0.5))}
        
        return timedict

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @parameters
# @contextdict

    def showTimePlot(results,parameters,contextdict):      
	
        colors = {'Year opened minus closed':'Orange',
                  'Ag':'Silver',
                  'Au':'Yellow',
                  'Year_opened':'Green',
                  'Year_closed':'Red',
                  'Rh':'Blue',
                  BokehTime.YEAR_EXISTS:'Purple'}
    
        timedict={}
	if (definitions.YEAR_CLOSED in parameters and definitions.YEAR_OPENED in parameters):
	    ##print 'if'
	    timedict=BokehTime.getOpenOverTimeDataSet(results,
						      timedict,
						      definitions.YEAR_OPENED,
						      bokutils.FIRST_YEAR,
						      bokutils.LAST_YEAR)
	elif (definitions.YEAR_OPENED in parameters):
	    ##print 'elif'
	    timedict=BokehTime.getTimeDataset(results,timedict,definitions.YEAR_OPENED)
	elif (definitions.YEAR_CLOSED in parameters):
	    ##print 'elifant'
	    timedict=BokehTime.getTimeDataset(results,timedict,definitions.YEAR_CLOSED)
        openseries=[]
        closedseries=[]
	existseries=[]
        timeseries=[]
        openminusclosed=[]
        print timedict
        for key in sorted(timedict.keys()):
	    val=timedict[key]
            opened=0
            closed=0
	    exists=0
            propdict=val
            timeseries.append(key)
            if (definitions.YEAR_OPENED in propdict):
                opened=propdict[definitions.YEAR_OPENED]
            openseries.append(opened)
                
            if (definitions.YEAR_CLOSED in propdict):
                closed=propdict[definitions.YEAR_CLOSED]
            closedseries.append(closed)
	    if (definitions.YEAR_CLOSED in parameters and definitions.YEAR_OPENED in parameters):
                exists=propdict[definitions.YEAR_OPENED]
            existseries.append(exists)
		
	    openminusclosed.append(opened-closed)
    
	title=contextdict[bokutils.SERVER_PATH][len("/visualisations"):].replace("_"," ")
	
        valuedict={BokehTime.TIME:timeseries}
	if (definitions.YEAR_CLOSED in parameters and definitions.YEAR_OPENED in parameters):
	    valuedict[BokehTime.YEAR_EXISTS]=existseries
	elif (definitions.YEAR_OPENED in parameters):
	    valuedict[definitions.YEAR_OPENED]=openseries
	elif (definitions.YEAR_CLOSED in parameters):
	    valuedict[definitions.YEAR_CLOSED]=closedseries

        p=BokehTime.getTimePlot(valuedict,colors,
				title,"Year","Count")
        
        
        return p


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @valuedict
# @colors
# @title
# @xtitle
# @ytitle

    def getTimePlot(valuedict,colors,title,xtitle,ytitle):
    
    
        x_time=[]
        
        for i, year in enumerate(valuedict["Time"]):
            dyear=datetime.datetime(int(year), 1, 1, 0, 0)
            x_time.append(dyear)
    
        hover =HoverTool(
        tooltips=[
                ("Year", "@x{%Y}"),
                ("Value", "@y{int}"),
                ],
        formatters={
                'x'      : 'datetime', # use 'datetime' formatter for 'date' field
                },
    
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline',
        point_policy="snap_to_data"
            
        )
    
    
    
        p = figure(plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, x_axis_type='datetime',title=title, tools=[hover,"crosshair","box_zoom","reset","pan"])
        p.xaxis.formatter = DatetimeTickFormatter(years = ['%Y'])
    
        p.xaxis.axis_label = xtitle
        p.yaxis.axis_label = ytitle
        p.xaxis.major_label_orientation = 'vertical'
    
        kcount=0
	litems=[]
        for key in sorted(valuedict.iterkeys()):
	    val=valuedict[key]
            if (key != BokehTime.TIME):
                
                desc=[]
                for i in range(0,len(valuedict[BokehTime.TIME])):
                    desc.append(key)
                source = ColumnDataSource(data=dict(
                    x=x_time,
                    y=valuedict[key],
                    desc=desc))
                circ=p.circle('x', 'y', size=5, source=source,color=colors[key])
                litems.append(LegendItem(label=bokutils.makeLegendKey(key), renderers=[circ]))
                p.line(x_time, valuedict[key],color=colors[key])
                kcount=kcount+1
                if (kcount > bokutils.MAX_CATEGORY_LINES):
                    break
                
	p.add_layout(Legend(items=litems,
			    glyph_height=bokutils.LEGEND_GLYPH_HEIGHT,
			    glyph_width=bokutils.LEGEND_GLYPH_WIDTH,),
		     'right')


        return p

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createPlot(self,me,parameters,contextdict):
	location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	
	try:
	    props=[definitions.NAME_OF_MUSEUM,
		   definitions.PROJECT_ID,
		   me]
	    markerdict=None
	    filters=[]
	    for p in parameters:
		props.append(p)

	    if (location != bokutils.PLOT_LOCATION_UK):
		markerdict={}
		markerdict['${GEOENTITY}']=location
		props.append(definitions.GEOCOL)

	    
	    results=apputils.getMarkerData(props,filters,markerdict)
 	except Exception, e:
 	    print str(e)
 	    return render_template('message.html', title="Internal application error",message="Internal Application Error C detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
	


        parameters.append(me.replace('_',' '))
        p = BokehTime.showTimePlot(results,parameters,contextdict)
               
        return p

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @valuedict
# @colors
# @title
# @xtitle
# @ytitle

    def getTimePlotAll(valuedict,colors,title,xtitle,ytitle):
        x_time=[]
        
        for i, year in enumerate(valuedict["Time"]):
            dyear=datetime.datetime(int(year), 1, 1, 0, 0)
            x_time.append(dyear)
    
        hover =HoverTool(
        tooltips=[
                ("Year", "@x{%Y}"),
                ("Value", "@y{int}"),
                ],
        formatters={
                'x'      : 'datetime', # use 'datetime' formatter for 'date' field
                },
    
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline',
        point_policy="snap_to_data"
            
        )
    
        p = figure(plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, x_axis_type='datetime',title=title, tools=[hover,"crosshair","box_zoom","reset","pan"])
        p.xaxis.formatter = DatetimeTickFormatter(years = ['%Y'])
    
        p.xaxis.axis_label = xtitle
        p.yaxis.axis_label = ytitle
        p.xaxis.major_label_orientation = 'vertical'
    
        band_x = np.append(x_time, x_time[::-1])
        band_y = np.append(valuedict[definitions.YEAR_CLOSED], valuedict[definitions.YEAR_OPENED][::-1])
    
        
        # a line works fine with time objects
        kcount=0
	litems=[]
        for key in sorted(valuedict.iterkeys()):
	    val=valuedict[key]
            if (key != BokehTime.TIME):
                
                desc=[]
                for i in range(0,len(valuedict[BokehTime.TIME])):
                    desc.append(key)
                source = ColumnDataSource(data=dict(
                    x=x_time,
                    y=valuedict[key],
                    desc=desc))
                circ=p.circle('x', 'y', size=5, source=source,color=colors[key])
                litems.append(LegendItem(label=bokutils.makeLegendKey(key), renderers=[circ]))
                p.line(x_time, valuedict[key],color=colors[key])
                kcount=kcount+1
                if (kcount > bokutils.MAX_CATEGORY_LINES):
                    break
                
        p.patch(band_x, band_y, color='#7570B3', fill_alpha=0.2)
	p.add_layout(Legend(items=litems,
			    glyph_height=bokutils.LEGEND_GLYPH_HEIGHT,
			    glyph_width=bokutils.LEGEND_GLYPH_WIDTH,),
		     'right')

        return p

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @parameters
# @contextdict

    def showTimePlotAll(results,parameters,contextdict):      
	
        colors = {'Year opened minus closed':'Orange',
                  'Ag':'Silver',
                  'Au':'Yellow',
                  'Year_opened':'Green',
                  'Year_closed':'Red',
                  'Rh':'Blue',
                  BokehTime.YEAR_EXISTS:'Purple'}
    
        timedict={}
	timedict=BokehTime.getTimeDataset(results,timedict,definitions.YEAR_OPENED)
	timedict=BokehTime.getTimeDataset(results,timedict,definitions.YEAR_CLOSED)
        openseries=[]
        closedseries=[]
        timeseries=[]
        openminusclosed=[]

        for key in sorted(timedict.keys()):
	    val=timedict[key]
            opened=0
            closed=0
	    exists=0
            propdict=val
            timeseries.append(key)
            if (definitions.YEAR_OPENED in propdict):
                opened=propdict[definitions.YEAR_OPENED]
            openseries.append(opened)
                
            if (definitions.YEAR_CLOSED in propdict):
                closed=propdict[definitions.YEAR_CLOSED]
            closedseries.append(closed)
	    openminusclosed.append(opened-closed)
    
	
        valuedict={BokehTime.TIME:timeseries}
	location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	title="Opening and closing at location "+location

	valuedict[definitions.YEAR_OPENED]=openseries
	valuedict[definitions.YEAR_CLOSED]=closedseries
        p=BokehTime.getTimePlotAll(valuedict,colors,
				title,"Year","Count")
        
        
        return p

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createPlotAll(self,me,parameters,contextdict):
	location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	

	try:
	    props=[definitions.NAME_OF_MUSEUM,
		   definitions.PROJECT_ID,
		   me]
	    filters=[]
	    for p in parameters:
		props.append(p)


	    markerdict={}
	    if (location != bokutils.PLOT_LOCATION_UK):
		markerdict['${GEOENTITY}']=location
		props.append(definitions.GEOCOL)
	    
	    results=apputils.getMarkerData(props,filters,markerdict)
	except Exception, e:
 	    print str(e)
 	    return render_template('message.html', title="Internal application error",message="Internal Application Error D detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
	


        parameters.append(me.replace('_',' '))
        p = BokehTime.showTimePlotAll(results,parameters,contextdict)

               
        return p
        
    
