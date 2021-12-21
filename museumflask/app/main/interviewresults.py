##
# @param file
#  
# This class implements the FLASK interviewresults view and the functionality needed to
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
import os.path

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





class Interviewresults():
    ##global gotpost
   ## gotpost = "false"
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

    conditionslist=None
##  List of comparators to use for specific datatype
    widgets=""
##  The widgets shown in the interviewresults menu for a datatype
    widgetcodes=""
    
    ##havepost ="false"
	 
	
##  The JS to use
    view_attributes=None
    
    ALL_COLUMNS='All attributes'
	

    @staticmethod
## Purpose:Returns list of conditions
    def getConditionTypes():
	return Interviewresults.conditionslist

   ## @staticmethod
   ## def gotpost():
       ## return Interviewresults.havepost
    @staticmethod
## Purpose:Returns all widgets
    def getWidgets():
	return Interviewresults.widgets

    @staticmethod
## Purpose:returns all JS
    def getWidgetCodes():
	return Interviewresults.widgetcodes

    
    def getViewAttributes(self,list):
	view_attributes=[]
	for item in list:
	    newitem=item.replace('_',' ')
	    view_attributes.append(newitem)
	return view_attributes
	
    def getConditionTypesList(self):

	## Basic types
	Interviewresults.conditionslist=[]
	Interviewresults.conditionslist.append(" var conditiontypes= {")
	Interviewresults.conditionslist.append(" 'integer':[")
	Interviewresults.conditionslist.append("	'Before:LT',")
	Interviewresults.conditionslist.append("	'After:GT',")
	Interviewresults.conditionslist.append("	'Before and including:LTE',")
	Interviewresults.conditionslist.append("	'After and including:GTE',")
	Interviewresults.conditionslist.append("	'Specific year only:EQ',")
	Interviewresults.conditionslist.append("	'Apart from:NEQ'],")
	Interviewresults.conditionslist.append("")

	Interviewresults.conditionslist.append(" 'positiveInteger':[")
	Interviewresults.conditionslist.append("	'Before:LT',")
	Interviewresults.conditionslist.append("	'After:GT',")
	Interviewresults.conditionslist.append("	'Before and including:LTE',")
	Interviewresults.conditionslist.append("	'After and including:GTE',")
	Interviewresults.conditionslist.append("	'Specific year only:EQ',")
	Interviewresults.conditionslist.append("	'Apart from:NEQ'],")

	Interviewresults.conditionslist.append(" 'RangeType':[")
	Interviewresults.conditionslist.append("	'Before:LT',")
	Interviewresults.conditionslist.append("	'After:GT',")
	Interviewresults.conditionslist.append("	'Before and including:LTE',")
	Interviewresults.conditionslist.append("	'After and including:GTE',")
	Interviewresults.conditionslist.append("	'Specific year only:EQ',")
	Interviewresults.conditionslist.append("	'Apart from:NEQ',")
	Interviewresults.conditionslist.append("	'Possibly Before:PLT',")
	Interviewresults.conditionslist.append("	'Possibly After:PGT',")
	Interviewresults.conditionslist.append("	'Possibly Before and including:PLTE',")
	Interviewresults.conditionslist.append("	'Possibly After and including:PGTE',")
	Interviewresults.conditionslist.append("	'Possibly Specific year only:PEQ',")
	Interviewresults.conditionslist.append("	'Possibly Apart from:PNEQ'],")


	Interviewresults.conditionslist.append("")
	Interviewresults.conditionslist.append(" 'decimal':[")
	Interviewresults.conditionslist.append("	'Before:LT',")
	Interviewresults.conditionslist.append("	'After:GT',")
	Interviewresults.conditionslist.append("	'Before and including:LTE',")
	Interviewresults.conditionslist.append("	'After and including:GTE',")
	Interviewresults.conditionslist.append("	'Specific year only:EQ',")
	Interviewresults.conditionslist.append("	'Apart from:NEQ'],")
	Interviewresults.conditionslist.append("")
	Interviewresults.conditionslist.append(" 'date'   :['Before:DLT','After:DGT',")
	Interviewresults.conditionslist.append("            'Before and including:DLTE',")
	Interviewresults.conditionslist.append("	    'After and including:DGTE',")
	Interviewresults.conditionslist.append("	    'Specific year only:DEQ',")
	Interviewresults.conditionslist.append("	    'Apart from:DNEQ'],")
	Interviewresults.conditionslist.append("'boolean':['True:True','False:False'],")
	Interviewresults.conditionslist.append("")
	Interviewresults.conditionslist.append("'other':['Matches:match','Not Match:notmatch'],")

	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		clist=instance.getGUIConditions()
		Interviewresults.conditionslist.append("'"+dkey+"':[")
		clist=instance.getGUIConditions()
		for c in clist:
		    parts=c.split(":")
		    Interviewresults.conditionslist.append("'"+parts[0]+":"+parts[1]+"',")
		
		Interviewresults.conditionslist[-1]=Interviewresults.conditionslist[-1].replace("',","'")
		Interviewresults.conditionslist.append("],")
		    
	Interviewresults.conditionslist[-1]=Interviewresults.conditionslist[-1].replace("],","]")
	Interviewresults.conditionslist.append("	}; ")

	return Interviewresults.conditionslist
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Initialise widgets from datatype implementations
    def initWidgets(self):

	## Basic types
	Interviewresults.widgets+=" var widgets= { \n"
	Interviewresults.widgetcodes+=" var widgetcode= { \n"
	
	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		widget=instance.getWidget()
		Interviewresults.widgets+="'"+dkey+"':'"+widget+"',\n"
		code=instance.getWidgetCode().replace("\n",'#')
		Interviewresults.widgetcodes+='"'+dkey+'":"'+code+'",\n'
		
	Interviewresults.widgets+="};"
	Interviewresults.widgets=Interviewresults.widgets.replace(",\n};","};").encode('ascii','ignore')
	Interviewresults.widgetcodes+="};"
	Interviewresults.widgetcodes=Interviewresults.widgetcodes.replace(",\n};","};").encode('ascii','ignore')

	return

    def interviewresultsView(self):
	



	##print "datadict"
	##print definitions.DATATYPEDICT
	##print "conditiontypes"
	##print self.getConditionTypes()
	##print "widgets"
	##print Interviewresults.widgets
	##print "gotposet"
     ##print(Interviewresults.gotpost)
     ##print(os.path.dirname(os.path.realpath(__file__)))
     dircsv = os.path.dirname(os.path.realpath(__file__))

     ##print "attributes"
     ##print definitions.DEFAULT_SEARCH_FILTER_COLUMNS
     ##print "attrtypes"
     ##print definitions.ATTRITYPES
     ##print"datagroups"
     ##print definitions.DATAGROUPS
     ##print type(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)
     summary=[]
     location=[]
     display=[]
     interview=[]
     fee=[]
     newdefs = []



     if (request.method == 'POST'):


		piccount=[]
		picnum=0
		for filename in os.listdir(dircsv + "/../static/interviews/"+request.form["foldername"]+"/Pictures"):
			picnum=picnum+1
			piccount.append(picnum)
		with io.open(dircsv+"/../static/interviews/"+request.form["foldername"]+"/public.txt", mode="r", encoding='utf-8') as f:
		 # use readlines to read all lines in the file
		 # The variable "lines" is a list containing all lines in the file
		 lines = f.readlines()
		 stage =0
		 musname = request.form["foldername"].split(",")[1]+","+request.form["foldername"].split(",")[2]
		 for line in lines:
			print("newline")
			#print(line)
			if(line=="Summary of museum:\n"):
				stage=1
			elif(line=="Description of museum building and location:\n"):
				stage=2
			elif(line=="Description of the display:\n"):
				stage=3
			elif(line=="Summary of interview:\n"):
				stage=4
			elif(line=="Entrance fee:\n"):
				stage=5
			else:
				if(stage==1):
					summary.append(line)
				if (stage == 2):
					location.append(line)
				if (stage == 3):
					display.append(line)
				if (stage == 4):
					interview.append(line)
				if (stage == 5):
					fee.append(line)

		 #print(summary)
		postrec="false"
		filepath=os.path.dirname(os.path.realpath(__file__))
		transcript2exists="false";
		if os.path.isfile(filepath+"/../static/interviews/"+request.form["foldername"]+"/transcript_2.pdf"):
		  print('true')
		  transcript2exists='true'
		else:
		  print(os.path.isfile(filepath+"/../static/interviews/"+request.form["foldername"]+"/transcript_2.pdf"))
		  print(filepath+"/../static/interviews/"+request.form["foldername"]+"/transcript2.pdf")
		  print('false')
		return render_template('interviewresults.html',
								   picdir = "static/interviews/"+request.form["foldername"]+"/Pictures",
								   transcript ="static/interviews/"+request.form["foldername"]+"/transcript.pdf",
                                   transcript2="static/interviews/"+request.form["foldername"]+"/transcript_2.pdf",
                                   transcript2exists=transcript2exists,
								   piccount = piccount,
								   musname=musname,
								   summary=summary,
							   location=location,
							   display=display,
							   interview=interview,
							   fee=fee)
     ##print(request.form['Governance'])
     ##\\sprint(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)




     postrec = "true"
     return render_template('interviewresults.html',
				   attributes=zip(newdefs,Interviewresults.view_attributes),
				   attritypes=attritypes,
				   datagroups=definitions.DATAGROUPS,
				   datadict=definitions.DATATYPEDICT,
				   conditiontypes=self.getConditionTypes(),
				   widgets=Interviewresults.widgets,
				   widgetcodes=Interviewresults.widgetcodes)
				   

