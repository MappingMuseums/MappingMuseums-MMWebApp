from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource,LabelSet
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
from datetime import datetime
from bokeh.layouts import layout 
from bokeh.models import ( 
  HoverTool, ColumnDataSource, Legend, LegendItem 
) 
from bokeh.plotting import figure 
from bokeh.palettes import brewer 
import datetime
from bokeh.models import DatetimeTickFormatter
from bokeh.models.glyphs import Rect as rect
from bokeh.models import Text
from bokeh.models.ranges import Range1d
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.models.widgets import Panel, Tabs


import jinja2
from bokeh.embed import components
from app.main.boksplots import bokehcategorypie
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, OpenURL, TapTool
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.plotting import figure, output_file, show
from bokeh.events import Tap
from bokeh.models.layouts import Row, Column, WidgetBox
from bokeh.models.widgets import DateSlider,RangeSlider, DateRangeSlider,Slider, Div
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import gridplot,row,widgetbox

from app.main import apputils
from app.main import definitions

from . import bokutils,bokehtimeandcategory,custompie

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
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BokehCategoryBar():

    REST=23



    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @title
# @plotdict
# @classification
# @parameters
# @contextdict
# @maxval

    def getPlotByYear(title,plotdict,classification,parameters,contextdict,maxval):

	category=str(contextdict["name"][0]).replace("'","").encode('ascii','ignore').decode("utf-8")
	classification=sorted(classification)

	if (category == 'All'):
	    hover = HoverTool(tooltips="""
	    <div style=" opacity: .8; padding: 5px; background-color: @type_color;color: @font_color;>
			      <h1 style="margin: 0; font-size: 12px;"> All museums:</h1>
			      <h1 style="margin: 0; font-size: 24px;"><strong> @counts </strong></h1>
			      </div>
			      """
			      )

	else:
	    hover = HoverTool(tooltips="""
	    <div style=" opacity: .8; padding: 5px; background-color: @type_color;color: @font_color;>
			      <h1 style="margin: 0; font-size: 12px;"> @classification</h1>
			      <h1 style="margin: 0; font-size: 24px;"><strong> @counts </strong></h1>
			      </div>
			      """
			      )

	bucketlen=0
	if ("Time" in classification):
	    bucketlen=len(plotdict["Time"])
	    classification.remove("Time")
        classlen=len(classification)

	for i, l in enumerate(classification):
	    classification[i]=bokutils.makeLegendKey(l)

	shortkeydict={}
        for key,val in plotdict.iteritems():
            shortkeydict[bokutils.makeLegendKey(key)]=plotdict[key]

	plotdict=shortkeydict
	
	    

			  
        my_palette=bokutils.getColors(classlen,True,False)
        
        colordict={}
        for i, val in enumerate(my_palette):
            colordict[i]=val

        
	valuearr=[]
	for year in range(0,bucketlen):
	    counts=[]
	    for c in classification:
	        if (c in plotdict):
		    counts.append(int(plotdict[c][year]+float(0.5)))
		else:
		    counts.append(0)
            valuearr.append(counts)

        plotdict=None

	labellist=[]
	for l in counts:
	    labellist.append(str(l))
	
        

        source = ColumnDataSource(data=dict(classification=classification,
					    counts=counts,
					    labellist=labellist,
                                            type_color=[colordict[x] for x in colordict],
                                            font_color=[bokutils.contrasting_text_color(colordict[x]) for x in colordict]))
        
        allsource = ColumnDataSource(data=dict(plotlist=valuearr))
	if (bokutils.ACCUMULATE_TRUE in parameters):
	    acc=True
	if (bokutils.ACCUMULATE_FALSE in parameters):
	    acc=False
	    
        paramsource = ColumnDataSource(data=dict(params=[acc,False,"Time"]))

	plotwidth=bokutils.PLOT_WIDTH



        p = figure(x_range=classification, plot_height=bokutils.PLOT_HEIGHT,
	           plot_width=plotwidth,
		   tools=[hover],
		   toolbar_location=None,
		   title=title)

        # set fixed padding for small numbers, but could also be percentage
	if (len(classification) < 6):
	   p.x_range.range_padding = 0.7

        p.vbar(x='classification', top='counts',width=0.9,line_width=5.9 , source=source, legend="classification",
               line_color='white', fill_color=factor_cmap('classification', palette=my_palette, factors=classification))
        
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
	#p.x_range.factors = classification[::-1]
	#p.y_range = Range1d(start=0,end=4000,bounds='auto')
        p.y_range.end = maxval+int(0.05*float(maxval))

	blabel = LabelSet(x='classification', y='counts', text='labellist', level='glyph',
			  x_offset=-11, y_offset=2, source=source, render_mode='canvas')

	p.add_layout(blabel)


        p.legend.orientation = "vertical"
        p.xaxis.major_label_orientation = 1.2
	new_legend = p.legend[0]
	p.legend[0].plot = None
	p.add_layout(new_legend, 'right')

	slider = Slider(start=bokutils.FIRST_YEAR,
	                end=bokutils.LAST_YEAR,
                        value=bokutils.LAST_YEAR,
                        step=1,
                        title='Year',
			bar_color="#b3cccc")

	


	
	callback = CustomJS(args=dict(source=source,slider=slider,plot=p,window=None,source2=allsource,source3=paramsource),
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
	  
	  var arr = source.data["counts"];
	  var labels = source.data["labellist"];
	  var allcounts=source2.data["plotlist"];
	  var al = arr.length;
	  //console.log(al);
	  var i =0;
	    while (i < al)
	      {
	        arr[i] = 0;
	        i = i + 1;
	      }
	    i =0;
	   var startidx=slider.value - 1960;
	   //console.log("START"+startidx);

	    // No accumulation
	    i=0;
	    while (i < al)
	      {
	        arr[i] = arr[i] = allcounts[startidx][i];
		labels[i]=arr[i]+"";
	        i = i + 1;
	      }
	  	    

	source.change.emit();

	return null;
	};
	cb(source, slider, plot,window,source2,source3);

	""")

	slider.js_on_change('value', callback)


        wb=widgetbox(children=[slider], sizing_mode='scale_width')
        thisrow=Column(children=[p, wb],sizing_mode='scale_both')

        return thisrow



#- - - - - - - - - - - - -


    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @score
# @allscore
# @classification
# @counts
# @rest
# @tabledict
# @title
# @maxval

    def getPlot(score,allscore,classification,counts,rest,tabledict,title,maxval):

	classification=sorted(classification)
	legendlist=[]
	for l in classification:
	    legendlist.append(bokutils.makeLegendKey(l))
	
	labellist=[]
	for l in counts:
	    labellist.append(str(l))
	

        hover = HoverTool(tooltips="""
        <div style=" opacity: .8; padding: 5px; background-color: @type_color;color: @font_color;>
                          <h1 style="margin: 0; font-size: 12px;"> @legendlist</h1>
                          <h1 style="margin: 0; font-size: 24px;"><strong> @counts </strong></h1>
                          <table>
                          @subgroups{safe}
                          </table>
                          </div>
                          """
                          )

                          

        subdict={}
        for i, val in enumerate(classification):
            subdict[i]=tabledict[val]

                          
        
        ## Left diagram
        classlen=len(classification)
        my_palette=bokutils.getColors(classlen,True,False)
        
        colordict={}
        for i, val in enumerate(my_palette):
            colordict[i]=val
        
        source = ColumnDataSource(data=dict(classification=classification, counts=counts,
					    legendlist=legendlist,
					    labellist=labellist,
                                            type_color=[colordict[x] for x in colordict],
                                            font_color=[bokutils.contrasting_text_color(colordict[x]) for x in colordict],
                                            subgroups=[subdict[x] for x in subdict]))
        

        p = figure(x_range=classification, plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, tools=[hover],toolbar_location=None, title=title)
        p.vbar(x='classification', top='counts', width=0.9, source=source, legend="legendlist",
               line_color='white', fill_color=factor_cmap('classification', palette=my_palette, factors=classification))
        
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = maxval
        p.legend.orientation = "vertical"
        #p.legend.location = "top_right"
        text_source = ColumnDataSource({'year': ['%s' % 1968]})
        text= Text(x=1, y=35, text='year',
                   text_font_size='80pt',
                   text_color='#EEEEEE'
                   )
        p.add_glyph(text_source, text)
        p.xaxis.major_label_orientation = 1.2

	blabel = LabelSet(x='classification', y='counts', text='labellist', level='glyph',
			  x_offset=5, y_offset=5, source=source, render_mode='canvas')

	p.add_layout(blabel)

	new_legend = p.legend[0]
	p.legend[0].plot = None
	p.add_layout(new_legend, 'right')

	blabel = LabelSet(x='classification', y='counts', text='labellist', level='glyph',
			  x_offset=5, y_offset=5, source=source, render_mode='canvas')

	p.add_layout(blabel)
		      
        slider = RangeSlider(
                              start=bokutils.FIRST_YEAR,
                              end=bokutils.LAST_YEAR,
                              value=[bokutils.LAST_YEAR, bokutils.LAST_YEAR],
                              step=1,
                              title='Year',
			      bar_color="#b3cccc")



        def slider_update(source=source, slider=slider, plot=p,window=None):
            year0 = slider.value[0]
            year1 = slider.value[1]
            return

        
        slider.js_on_change('value', bokutils.translatepy2js(slider_update))

        wb=widgetbox(children=[slider], sizing_mode='scale_width')
        thisrow=Column(children=[p, wb],
                       sizing_mode='scale_both')
        return thisrow


    
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results

    def getHierCategoryCountDataSet(topic,results):      
    
        score={}
        allscore={}
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
                sub=res[topic]["value"]
                parts=sub.split("/")
                plen=len(parts)-1
                sub=parts[plen]
                parts=sub.split("-")
                compokey=str(parts[0])
                
                
                if (compokey in score):
                    score[compokey]=score[compokey]+1
                else:
                    score[compokey]=score[compokey]=1
                if (sub in allscore):
                    allscore[sub]=allscore[sub]+1
                else:
                    allscore[sub]=allscore[sub]=1
                        
        
        
        classification = []
        counts = []
        
        r_class= []
        r_counts = []
        
        tuples=[]
        
        
        for key,val in score.iteritems():
            tup=(key,val)
            tuples.append(tup)
        
        stups=sorted(tuples,key=lambda x: x[1])
        c=0
        rest=0
        tl=len(stups)-1
        
        while (tl > 0):
            key,val=stups[tl]
            if (c < BokehCategoryBar.REST):
                classification.append(key)
                counts.append(val)
            else:
                r_class.append(key)
                r_counts.append(val)
                rest=rest+val
            c=c+1
            tl=tl-1
        
        if (rest > 0):
            classification.append("Rest")
            counts.append(rest)
        
        
        tabledict={}
        for key,val in score.iteritems():
            keylist=[]
            for akey,aval in allscore.iteritems():
                parts=akey.split("-")
                if (parts[0] == key):
                    tup=(akey,aval)
                    keylist.append(tup)
            for item in sorted(keylist,key=lambda x: x[1],reverse=True):
                akey,aval=(item)
                if (not key in tabledict):
                    tabledict[key]=""
                tabledict[key]=tabledict[key]+'<tr><td><h4>'+akey+'</h4></td><td>'+str(aval)+'</td></tr>'
        if (rest):
            tabledict["Rest"]="See graph on right"
        
        subdict={}
        for i, val in enumerate(classification):
            subdict[i]=tabledict[val]
    
        return score,allscore,classification,counts,r_class,r_counts,(rest > 0),tabledict
    
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @valuedict)
    def getMaxVal(valuedict):
	maxval=-99999
	for k in valuedict.keys():
	    if (k != "Time"):
		vlist=valuedict[k]
		for v in vlist:
		    if (v > maxval):
			maxval=v
	return maxval
	
    
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @topic
# @parameters
# @contextdict

    def showPlot(results,topic,parameters,contextdict):    
	
	defcol=definitions.DEFNAME+topic
	itype=None
	if (defcol in definitions.DATATYPEDICT ):
	    itype=definitions.DATATYPEDICT[defcol]
	elif (topic in definitions.DATATYPEDICT ):
	    itype=definitions.DATATYPEDICT[topic]
	elif (topic in ['All','location'] ):
	    itype=topic # Type is not used
	else:
	    print "WARNING **** No handler for :"+topic


	if (topic == "All"):
	    if (parameters[0]==definitions.YEAR_OPENED):
		valuedict=bokehtimeandcategory.BokehTimeAndCategory.getOpenedDictionaryAllTopics(topic,
												 results,
												 bokutils.FIRST_YEAR,
												 bokutils.LAST_YEAR,
												 itype,
												 parameters)
	    else:

		#THIS is the next routine to make into accepting closed.
		#CHeck what is in param 0 to find out what the difference is for logic 2 and 4
		
		valuedict=bokehtimeandcategory.BokehTimeAndCategory.getOpenedUpToGivenTimeAllTopics(topic,
												    results,
												    bokutils.FIRST_YEAR,
												    bokutils.LAST_YEAR,
												    itype,
												    parameters)
		
	elif (parameters[0] == definitions.YEAR_OPENED ):
            valuedict=bokehtimeandcategory.BokehTimeAndCategory.getOpenedDictionaryPerTopic(topic,
											    results,
											    bokutils.FIRST_YEAR,
											    bokutils.LAST_YEAR,
											    itype,
											    parameters)
	elif (parameters[0] == definitions.YEAR_CLOSED ):
            valuedict=bokehtimeandcategory.BokehTimeAndCategory.getClosedDictionaryPerTopicL6(topic,
											      results,
											      bokutils.FIRST_YEAR,
											      bokutils.LAST_YEAR,
											      itype,
											      parameters)
	elif (parameters[0] == definitions.YEAR_EXISTS ):
            valuedict=bokehtimeandcategory.BokehTimeAndCategory.getOpenedUpToGivenTimePerTopic(topic,
											       results,
											       bokutils.FIRST_YEAR,
											       bokutils.LAST_YEAR,
											       itype,
											       parameters)
	    

	title=contextdict[bokutils.SERVER_PATH][len("/visualisations"):].replace("_"," ")

	newparameters=None
	maxval=BokehCategoryBar.getMaxVal(valuedict)
        p=BokehCategoryBar.getPlotByYear(title,valuedict,list(valuedict.keys()),parameters,contextdict,maxval)

        # Not working    p=getStackedPlot(score,allscore,classification,counts,isrest,tabledict,topic,int(maxval))
        #p=getStackedLinePlot(score,allscore,classification,counts,isrest,tabledict,topic,int(maxval))
        
	return p
        
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createPlot(self,me,parameters,contextdict):
	location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))
	

        try:
	    if (me == "All"):
		props=[definitions.NAME_OF_MUSEUM,
		       definitions.PROJECT_ID,
		       definitions.YEAR_OPENED,
		       definitions.YEAR_CLOSED]
	    else:
		props=[definitions.NAME_OF_MUSEUM,
		       definitions.PROJECT_ID,
		       definitions.YEAR_OPENED,
		       definitions.YEAR_CLOSED,
		       me]

	    markerdict={}
	    if (location != bokutils.PLOT_LOCATION_UK):
		markerdict['${GEOENTITY}']=location
		props.append(definitions.GEOCOL)
	
	    results=apputils.getMarkerData(props,vardict=markerdict)
        except Exception, e:
            print str(e)
            return render_template('message.html', title="Internal application error",message="Internal Application Error B detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
        
        return BokehCategoryBar.showPlot(results,me,parameters,contextdict)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createLocationPlot(self,me,parameters,contextdict):

	results=apputils.getVizLocationData(parameters,bokutils.FIRST_YEAR,bokutils.LAST_YEAR)
        return BokehCategoryBar.showPlot(results,me,parameters,contextdict)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
