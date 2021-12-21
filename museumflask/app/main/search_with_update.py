##
# @param file
#  
# This class implements the FLASK search view and the functionality needed to 
# retrieve the searched data. It receives a form with the parameters from the
# client: Column, comparator, filter and columns  to show. 
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import listman
from . import tree
from . import PTreeNode
from . import models
from . import definitions
from . import model_to_view
from . import Configuration
from . import showmuseumtypes

from PTreeNode import PTreeNode as PTreeNode


from flask import current_app as app
import pprint
import collections
import copy
import importlib

from altair import Chart, Color, Scale
import pandas as pd
import traceback
import sys
import pickle
import time
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class Search():
    
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

    conditionslist=None
##  List of comparators to use for specific datatype
    widgets=""
##  The widgets shown in the search menu for a datatype
    widgetcodes=""
##  The JS to use
    view_attributes=None
    
    ALL_COLUMNS='All attributes'
    
    
## Purpose:Processes model representations to view representations
# Arguments:
# 
# @param bindings keys
# @param res      results

    def createView(self,bindings,res):
        for d in bindings:
            dataname=definitions.DEFNAME+d
	    resdata=res[bindings[d]]
	    if (len(res[bindings[d]])>0):
		if (dataname in definitions.DATATYPEDICT):
		    datatype=definitions.DATATYPEDICT[dataname]
		    res[bindings[d]]=self.modeltoview.getViewForType(datatype,res[bindings[d]])
		else:
		    res[bindings[d]]=self.modeltoview.getView(d,res[bindings[d]])
	return res


    @staticmethod
## Purpose:Returns list of conditions
    def getConditionTypes():
	return Search.conditionslist

    @staticmethod
## Purpose:Returns all widgets
    def getWidgets():
	return Search.widgets

    @staticmethod
## Purpose:returns all JS
    def getWidgetCodes():
	return Search.widgetcodes


## Purpose:Converts list of model representations to view representations
# Arguments:
# 
# @param list model 
    def getViewAttributes(self,list):
	view_attributes=[]
	for item in list:
	    newitem=item.replace('_',' ')
	    view_attributes.append(newitem)
	return view_attributes

    
## Purpose:Build comparator list
    def getConditionTypesList(self):

	## Basic types
	Search.conditionslist=[]
	Search.conditionslist.append(" var conditiontypes= {")
	Search.conditionslist.append(" 'integer':[")
	Search.conditionslist.append("	'Before:LT',")
	Search.conditionslist.append("	'After:GT',")
	Search.conditionslist.append("	'Before and including:LTE',")
	Search.conditionslist.append("	'After and including:GTE',")
	Search.conditionslist.append("	'Specific year only:EQ',")
	Search.conditionslist.append("	'Apart from:NEQ'],")
	Search.conditionslist.append("")

	Search.conditionslist.append(" 'positiveInteger':[")
	Search.conditionslist.append("	'Before:LT',")
	Search.conditionslist.append("	'After:GT',")
	Search.conditionslist.append("	'Before and including:LTE',")
	Search.conditionslist.append("	'After and including:GTE',")
	Search.conditionslist.append("	'Specific year only:EQ',")
	Search.conditionslist.append("	'Apart from:NEQ'],")

	Search.conditionslist.append(" 'RangeType':[")
	Search.conditionslist.append("	'Before:LT',")
	Search.conditionslist.append("	'After:GT',")
	Search.conditionslist.append("	'Before and including:LTE',")
	Search.conditionslist.append("	'After and including:GTE',")
	Search.conditionslist.append("	'Specific year only:EQ',")
	Search.conditionslist.append("	'Apart from:NEQ',")
	Search.conditionslist.append("	'Possibly Before:PLT',")
	Search.conditionslist.append("	'Possibly After:PGT',")
	Search.conditionslist.append("	'Possibly Before and including:PLTE',")
	Search.conditionslist.append("	'Possibly After and including:PGTE',")
	Search.conditionslist.append("	'Possibly Specific year only:PEQ',")
	Search.conditionslist.append("	'Possibly Apart from:PNEQ'],")


	Search.conditionslist.append("")
	Search.conditionslist.append(" 'decimal':[")
	Search.conditionslist.append("	'Before:LT',")
	Search.conditionslist.append("	'After:GT',")
	Search.conditionslist.append("	'Before and including:LTE',")
	Search.conditionslist.append("	'After and including:GTE',")
	Search.conditionslist.append("	'Specific year only:EQ',")
	Search.conditionslist.append("	'Apart from:NEQ'],")
	Search.conditionslist.append("")
	Search.conditionslist.append(" 'date'   :['Before:DLT','After:DGT',")
	Search.conditionslist.append("            'Before and including:DLTE',")
	Search.conditionslist.append("	    'After and including:DGTE',")
	Search.conditionslist.append("	    'Specific year only:DEQ',")
	Search.conditionslist.append("	    'Apart from:DNEQ'],")
	Search.conditionslist.append("'boolean':['True:True','False:False'],")
	Search.conditionslist.append("")
	Search.conditionslist.append("'other':['Matches:match','Not Match:notmatch'],")

	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		clist=instance.getGUIConditions()
		Search.conditionslist.append("'"+dkey+"':[")
		clist=instance.getGUIConditions()
		for c in clist:
		    parts=c.split(":")
		    Search.conditionslist.append("'"+parts[0]+":"+parts[1]+"',")
		
		Search.conditionslist[-1]=Search.conditionslist[-1].replace("',","'")
		Search.conditionslist.append("],")
		    
	Search.conditionslist[-1]=Search.conditionslist[-1].replace("],","]")
	Search.conditionslist.append("	}; ")

	return Search.conditionslist


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Initialise widgets from datatype implementations
    def initWidgets(self):

	## Basic types
	Search.widgets+=" var widgets= { \n"
	Search.widgetcodes+=" var widgetcode= { \n"
	
	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		widget=instance.getWidget()
		Search.widgets+="'"+dkey+"':'"+widget+"',\n"
		code=instance.getWidgetCode().replace("\n",'#')
		Search.widgetcodes+='"'+dkey+'":"'+code+'",\n'
		
	Search.widgets+="};"
	Search.widgets=Search.widgets.replace(",\n};","};").encode('ascii','ignore')
	Search.widgetcodes+="};"
	Search.widgetcodes=Search.widgetcodes.replace(",\n};","};").encode('ascii','ignore')

	return 


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Check for malicious queries
    def checkInjection(self,matchstring):
	for word in matchstring:
	    for key in definitions.SPARQL_KEYWORDS:
		if (word.upper().find(key) > -1):
		    return key
	return None
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    

## Purpose:Implements the FLASK view
# Provides all data for the search page.
# Processes the form
# Retrieves the data

    def searchView(self):


	if (Search.conditionslist is None):
	    Search.conditionslist = self.getConditionTypesList()
	    self.initWidgets()
	    Search.view_attributes=self.getViewAttributes(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)

        if (request.method == 'GET'):
            return render_template('search.html',
				   attributes=zip(definitions.DEFAULT_SEARCH_FILTER_COLUMNS,Search.view_attributes),
				   attritypes=definitions.ATTRITYPES,
				   datagroups=definitions.DATAGROUPS,
				   datadict=definitions.DATATYPEDICT,
				   conditiontypes=self.getConditionTypes(),
				   widgets=Search.widgets,
				   widgetcodes=Search.widgetcodes)
        
            
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(request.form)
        
        ms=request.form.getlist('multiselect[]')
        
        msl=len(ms)
        if (msl < 1):
            return render_template('message.html', title="Search",message=" No display columns selected")
        elif (ms[0] == 'Default'):
            ms=copy.deepcopy(definitions.DEFAULT_SEARCH_SHOW_COLUMNS)
            i=0
            mlen=len(ms)
            while (i < mlen):
                ms[i]=str(ms[i].replace(definitions.HASNAME,''))
                i+=1
        else :
            if (msl == 0):
                return render_template('message.html', title="Search",message=" No custom display columns selected")

        columns=""
        count=0
        
	start_time = time.time()
	ordercolumn="?museum"
        orderby=request.form.getlist('orderby')
        if (len(orderby) < 1):
            return render_template('message.html', title="Search",message=" No matching ordering selected")
	else:
	    ordercolumn="?"+str(orderby[0])
	    
        coltomatch=request.form.getlist('coltomatch')
        if (len(coltomatch) < 1):
            return render_template('message.html', title="Search",message=" No matching column selected")
            
        matchstring=request.form.getlist('matchstring')
        if (len(matchstring) < 1):
            return render_template('message.html', title="Search",message="No match string entered")
	isinjection=self.checkInjection(matchstring)
        if (isinjection != None):
            return render_template('message.html', title="Search",message="Search has detected a suspicious injection query which has been denied.["+isinjection+"]")
	
        conditions=request.form.getlist('condition')
        if (len(conditions) < 1):
            return render_template('message.html', title="Search",message="No filter criteria entered")
    
        if (ms[0] == Search.ALL_COLUMNS):
	    ms=copy.deepcopy(definitions.DEFAULT_VIEW_ALL_COLUMNS)
        else:
    #       Check if any condition needs to be added to the output columns
            for col in coltomatch:
                if (col not in ms):
                    ms.append(col)
	    # This is a special case and we need to make sure NAME is first in the list.
	    if definitions.NAME_OF_MUSEUM in ms:
		mn=ms.remove(definitions.NAME_OF_MUSEUM)
	    ms.insert(0,definitions.NAME_OF_MUSEUM)

#################
	ms.append(definitions.PROJECT_ID)
		    
        try:
	    results=apputils.getSearchResults(ms,coltomatch,conditions,matchstring,ordercolumn)
	except Exception, e:
               print str(e)
	       return render_template('message.html',
				      title="Internal application error",
				      message="Internal Application Error M detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
                
        
        if (len(results) < 1):
            return render_template('message.html', title="Search",message="No results found.")
    


        mapdata=[]
        mapdata.append("var museums=[")
    
        headingdata=results[0]
    
        del results[0]
        bindings={}
        hlen=len(headingdata)
        
        # Fix heading
        i=0
        while (i < hlen):
            bindings[str(headingdata[i])]=i
            i+=1

	print("--- %s seconds ---" % (time.time() - start_time))
	start_time = time.time()
        print "LEN BIN -> "+str(len(bindings))
        print "LEN RES -> "+str(len(results))
        if (len(results) < 1):
            return render_template('message.html', title="Search",message="No results found.")
############################
	print results[0][17]
	print bindings
	print results[0][17]
	pid=str(results[0][17])
	print "?#?#? search.py at line: 344 Dbg-out variable \pid [",pid,"]\n";
	
        lonptr=bindings[definitions.LONGITUDE]
        latptr=bindings[definitions.LATITUDE]
        # We must delete from high to low in matrix
        order=[]
        if (definitions.LATITUDE not in ms and definitions.LONGITUDE not in ms):
            if (latptr > lonptr):
                order.append(latptr)
                order.append(lonptr)
            else:
                order.append(lonptr)
                order.append(latptr)
        elif (definitions.LATITUDE not in ms):
                order.append(latptr)
        elif ( definitions.LONGITUDE not in ms):
                order.append(lonptr)
            
	order.append(bindings["museum"])
        for res in results:
            name=res[bindings[definitions.NAME_OF_MUSEUM]]
            uri=res[bindings["museum"]]
            uri=uri[len(definitions.RDFDEFURI)+6:]
            href='<a href="#tab3" uri="'+uri+'" data-toggle="tab" onclick="tabResSelected(3);">'+name+'</a>'
            href=href.replace(definitions.RDFDATAURI,
                              app.config['URLREWRITEPATTERN']).replace("/id/","/nid/")
            res[bindings[definitions.NAME_OF_MUSEUM]]=href
            
            res = self.createView(bindings,res)

            # Map data
            if (definitions.SUBJECT_MATTER  in bindings):
                sub=res[bindings[definitions.SUBJECT_MATTER]]
            else:
                sub="Unknown topic"
            lat=res[bindings[definitions.LATITUDE]]
            lon=res[bindings[definitions.LONGITUDE]]
            if (len(lat) > 0 and len(lon) >0):
                mapdata.append('["#1{}#2{}",{},{}],'.format(name,sub,lat,lon))
    
            for ptr in order:
                del res[ptr]
                    
                            
        mapdata[-1]=mapdata[-1].replace("],","]")
        mapdata.append("];")
    
        for ptr in order:
            del bindings[headingdata[ptr]]
            del headingdata[ptr]
    
    
        hlen=hlen-len(order)
        # Fix heading
        i=0
        while (i < hlen):
            headingdata[i]=str(headingdata[i].replace(definitions.HASNAME,'').replace('_',' '))
	    headingdata[i]=apputils.snake2camel(headingdata[i])
            i+=1
	print("--- %s seconds ---" % (time.time() - start_time))
	#qq=apputils.getUpdateStatementForCol(definitions.POSTCODE,pid,"SUESSCODE") # data
	#apputils.executebypost(qq)

	#print "?#?#? search.py at line: 406 Dbg-out variable \qq [",qq,"]\n";
	

	print("--- %s seconds ---" % (time.time() - start_time))

	    
        return render_template('searchResults.html',
                               attributes=definitions.ATTRITYPES,
                               attritypes=definitions.ATTRITYPES,
			       conditiontypes=Search.getConditionTypes(),
                               headingdata=headingdata,
                               mapdata=mapdata,
                               results=results,
                               length=len(results))
    
    
