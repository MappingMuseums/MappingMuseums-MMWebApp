##
# @param file
#  
# This class implements the FLASK interviews view and the functionality needed to
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

import os
import io
import csv
from flask import current_app as app
import pprint
import collections
import copy
import importlib
import requests
from altair import Chart, Color, Scale
import pandas as pd
import traceback
import sys
import pickle
import time
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 





class Interviews():
    ##global gotpost
   ## gotpost = "false"
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

    conditionslist=None
##  List of comparators to use for specific datatype
    widgets=""
##  The widgets shown in the interviews menu for a datatype
    widgetcodes=""
    
    ##havepost ="false"
	 
	
##  The JS to use
    view_attributes=None
    
    ALL_COLUMNS='All attributes'
	

    @staticmethod
## Purpose:Returns list of conditions
    def getConditionTypes():
	return Interviews.conditionslist

   ## @staticmethod
   ## def gotpost():
       ## return Interviews.havepost
    @staticmethod
## Purpose:Returns all widgets
    def getWidgets():
	return Interviews.widgets

    @staticmethod
## Purpose:returns all JS
    def getWidgetCodes():
	return Interviews.widgetcodes

    
    def getViewAttributes(self,list):
	view_attributes=[]
	for item in list:
	    newitem=item.replace('_',' ')
	    view_attributes.append(newitem)
	return view_attributes
	
    def getConditionTypesList(self):

	## Basic types
	Interviews.conditionslist=[]
	Interviews.conditionslist.append(" var conditiontypes= {")
	Interviews.conditionslist.append(" 'integer':[")
	Interviews.conditionslist.append("	'Before:LT',")
	Interviews.conditionslist.append("	'After:GT',")
	Interviews.conditionslist.append("	'Before and including:LTE',")
	Interviews.conditionslist.append("	'After and including:GTE',")
	Interviews.conditionslist.append("	'Specific year only:EQ',")
	Interviews.conditionslist.append("	'Apart from:NEQ'],")
	Interviews.conditionslist.append("")

	Interviews.conditionslist.append(" 'positiveInteger':[")
	Interviews.conditionslist.append("	'Before:LT',")
	Interviews.conditionslist.append("	'After:GT',")
	Interviews.conditionslist.append("	'Before and including:LTE',")
	Interviews.conditionslist.append("	'After and including:GTE',")
	Interviews.conditionslist.append("	'Specific year only:EQ',")
	Interviews.conditionslist.append("	'Apart from:NEQ'],")

	Interviews.conditionslist.append(" 'RangeType':[")
	Interviews.conditionslist.append("	'Before:LT',")
	Interviews.conditionslist.append("	'After:GT',")
	Interviews.conditionslist.append("	'Before and including:LTE',")
	Interviews.conditionslist.append("	'After and including:GTE',")
	Interviews.conditionslist.append("	'Specific year only:EQ',")
	Interviews.conditionslist.append("	'Apart from:NEQ',")
	Interviews.conditionslist.append("	'Possibly Before:PLT',")
	Interviews.conditionslist.append("	'Possibly After:PGT',")
	Interviews.conditionslist.append("	'Possibly Before and including:PLTE',")
	Interviews.conditionslist.append("	'Possibly After and including:PGTE',")
	Interviews.conditionslist.append("	'Possibly Specific year only:PEQ',")
	Interviews.conditionslist.append("	'Possibly Apart from:PNEQ'],")


	Interviews.conditionslist.append("")
	Interviews.conditionslist.append(" 'decimal':[")
	Interviews.conditionslist.append("	'Before:LT',")
	Interviews.conditionslist.append("	'After:GT',")
	Interviews.conditionslist.append("	'Before and including:LTE',")
	Interviews.conditionslist.append("	'After and including:GTE',")
	Interviews.conditionslist.append("	'Specific year only:EQ',")
	Interviews.conditionslist.append("	'Apart from:NEQ'],")
	Interviews.conditionslist.append("")
	Interviews.conditionslist.append(" 'date'   :['Before:DLT','After:DGT',")
	Interviews.conditionslist.append("            'Before and including:DLTE',")
	Interviews.conditionslist.append("	    'After and including:DGTE',")
	Interviews.conditionslist.append("	    'Specific year only:DEQ',")
	Interviews.conditionslist.append("	    'Apart from:DNEQ'],")
	Interviews.conditionslist.append("'boolean':['True:True','False:False'],")
	Interviews.conditionslist.append("")
	Interviews.conditionslist.append("'other':['Matches:match','Not Match:notmatch'],")

	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		clist=instance.getGUIConditions()
		Interviews.conditionslist.append("'"+dkey+"':[")
		clist=instance.getGUIConditions()
		for c in clist:
		    parts=c.split(":")
		    Interviews.conditionslist.append("'"+parts[0]+":"+parts[1]+"',")
		
		Interviews.conditionslist[-1]=Interviews.conditionslist[-1].replace("',","'")
		Interviews.conditionslist.append("],")
		    
	Interviews.conditionslist[-1]=Interviews.conditionslist[-1].replace("],","]")
	Interviews.conditionslist.append("	}; ")

	return Interviews.conditionslist
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Initialise widgets from datatype implementations
    def initWidgets(self):

	## Basic types
	Interviews.widgets+=" var widgets= { \n"
	Interviews.widgetcodes+=" var widgetcode= { \n"
	
	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		widget=instance.getWidget()
		Interviews.widgets+="'"+dkey+"':'"+widget+"',\n"
		code=instance.getWidgetCode().replace("\n",'#')
		Interviews.widgetcodes+='"'+dkey+'":"'+code+'",\n'
		
	Interviews.widgets+="};"
	Interviews.widgets=Interviews.widgets.replace(",\n};","};").encode('ascii','ignore')
	Interviews.widgetcodes+="};"
	Interviews.widgetcodes=Interviews.widgetcodes.replace(",\n};","};").encode('ascii','ignore')

	return

    def interviewsView(self):
	



	##print "datadict"
	##print definitions.DATATYPEDICT
	##print "conditiontypes"
	##print self.getConditionTypes()
	##print "widgets"
	##print Interviews.widgets
	##print "gotposet"
     ##print(Interviews.gotpost)
     ##print(os.path.dirname(os.path.realpath(__file__)))
     dircsv = os.path.dirname(os.path.realpath(__file__))

     ##print "attributes"
     ##print definitions.DEFAULT_SEARCH_FILTER_COLUMNS
     ##print "attrtypes"
     ##print definitions.ATTRITYPES
     ##print"datagroups"
     ##print definitions.DATAGROUPS
     ##print type(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)
     interlist=[]
     newdefs = []


     for filename in os.listdir (dircsv+"/../static/interviews"):
		 code = filename.split(",")[0]
		 name=filename.split(",")[1]+","+filename.split(",")[2]

		 with io.open(dircsv+"/../static/interviews/"+filename+"/summary.txt", mode="r", encoding='latin-1') as file:
			 summary = file.read().replace('\n', '')

		 interlist.append([code,name,summary])

		 print(filename)

     interlist=sorted(interlist, key=lambda x: x[1])
     print(interlist)
     if (request.method == 'GET'):
            postrec="false"
            return render_template('interviews.html',
								   interlist=interlist)
     ##print(request.form['Governance'])
     ##\\sprint(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)


     return render_template('interviews.html',
				   attributes=zip(newdefs,Interviews.view_attributes),
				   attritypes=attritypes,
				   datagroups=definitions.DATAGROUPS,
				   datadict=definitions.DATATYPEDICT,
				   conditiontypes=self.getConditionTypes(),
				   widgets=Interviews.widgets,
				   widgetcodes=Interviews.widgetcodes)
				   

