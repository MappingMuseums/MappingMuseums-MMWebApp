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

from app.main import apputils
from app.main import definitions

from app.main.boksplots import custompie
from . import bokutils
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
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BokehCategoryPie():


       
#- - - - - - - - - - - - -

    @staticmethod
    def getHierDataSet(topic,results):      
    
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
                #print "?#?#? plot.py at line: 127 Dbg-out variable \sub [",sub,"]\n";
                
                
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
            if (c < 9):
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
        print classification
        print counts
        
        if (rest > 0):
            print "Rest:"+str(len(r_class))
            print r_class
            print r_counts
        
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
    
#- - - - - - - - - - - - - - - - - -

    @staticmethod
    def showPiePlot(topic,results): 
    
    
        score,allscore,classification,counts,r_class,r_counts,isrest,tabledict=BokehCategoryPie.getHierDataSet(topic,results)
        maxval=float(max(counts))*(1.1)
        
        p=BokehCategoryPie.getPiePlot(score,allscore,classification,counts,isrest,tabledict,topic,int(maxval),"Governance")
        
        
        
        return p

#- - - - - - - - - - - - - - - - - -

    @staticmethod
    def getPiePlot(score,allscore,classification,counts,rest,tabledict,title,maxval,hovertext):
    
    
        d = {'posa': classification,
             'values': counts}
        df = pd.DataFrame(d)
    
        p = custompie.build_plot(
            df,
            'posa',
            'values',
            tooltips=[('percentage', '@percentage{0.00%}'), (hovertext, '@posa'), ('count','@values')],
            title='Governance',
            reverse_color=True,
            random_color_order=True,
            plot_height=700,
            plot_width=700)
        
        return p
    
            
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def createPlot(self,me,parameters):
# 	try:
        props=[definitions.NAME_OF_MUSEUM,
        definitions.PROJECT_ID,
	definitions.YEAR_OPENED,
        me]
 	results=apputils.getMarkerData(props,[bokutils.YEAR_FILTER3_OPEN])
 #	except Exception, e:
 	#    print str(e)
 	 #   return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 525   \n <br/><p><pre>"+str(e)+"</pre></p>")
	
	
        return BokehCategoryPie.showPiePlot(me,results)
    
