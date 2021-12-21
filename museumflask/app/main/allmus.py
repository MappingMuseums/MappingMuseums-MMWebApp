##
# @param file
#  
# This class implements the FLASK Allmus view and the functionality needed to 
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





class Allmus():
    ##global gotpost
   ## gotpost = "false"
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

    conditionslist=None
##  List of comparators to use for specific datatype
    widgets=""
##  The widgets shown in the Allmus menu for a datatype
    widgetcodes=""
    
    ##havepost ="false"
	 
	
##  The JS to use
    view_attributes=None
    
    ALL_COLUMNS='All attributes'
	

    @staticmethod
## Purpose:Returns list of conditions
    def getConditionTypes():
	return Allmus.conditionslist

   ## @staticmethod
   ## def gotpost():
       ## return Allmus.havepost
    @staticmethod
## Purpose:Returns all widgets
    def getWidgets():
	return Allmus.widgets

    @staticmethod
## Purpose:returns all JS
    def getWidgetCodes():
	return Allmus.widgetcodes

    
    def getViewAttributes(self,list):
	view_attributes=[]
	for item in list:
	    newitem=item.replace('_',' ')
	    view_attributes.append(newitem)
	return view_attributes
	
    def getConditionTypesList(self):

	## Basic types
	Allmus.conditionslist=[]
	Allmus.muselist=[]
	Allmus.muslist=[]
	Allmus.conditionslist.append(" var conditiontypes= {")
	Allmus.conditionslist.append(" 'integer':[")
	Allmus.conditionslist.append("	'Before:LT',")
	Allmus.conditionslist.append("	'After:GT',")
	Allmus.conditionslist.append("	'Before and including:LTE',")
	Allmus.conditionslist.append("	'After and including:GTE',")
	Allmus.conditionslist.append("	'Specific year only:EQ',")
	Allmus.conditionslist.append("	'Apart from:NEQ'],")
	Allmus.conditionslist.append("")

	Allmus.conditionslist.append(" 'positiveInteger':[")
	Allmus.conditionslist.append("	'Before:LT',")
	Allmus.conditionslist.append("	'After:GT',")
	Allmus.conditionslist.append("	'Before and including:LTE',")
	Allmus.conditionslist.append("	'After and including:GTE',")
	Allmus.conditionslist.append("	'Specific year only:EQ',")
	Allmus.conditionslist.append("	'Apart from:NEQ'],")

	Allmus.conditionslist.append(" 'RangeType':[")
	Allmus.conditionslist.append("	'Before:LT',")
	Allmus.conditionslist.append("	'After:GT',")
	Allmus.conditionslist.append("	'Before and including:LTE',")
	Allmus.conditionslist.append("	'After and including:GTE',")
	Allmus.conditionslist.append("	'Specific year only:EQ',")
	Allmus.conditionslist.append("	'Apart from:NEQ',")
	Allmus.conditionslist.append("	'Possibly Before:PLT',")
	Allmus.conditionslist.append("	'Possibly After:PGT',")
	Allmus.conditionslist.append("	'Possibly Before and including:PLTE',")
	Allmus.conditionslist.append("	'Possibly After and including:PGTE',")
	Allmus.conditionslist.append("	'Possibly Specific year only:PEQ',")
	Allmus.conditionslist.append("	'Possibly Apart from:PNEQ'],")


	Allmus.conditionslist.append("")
	Allmus.conditionslist.append(" 'decimal':[")
	Allmus.conditionslist.append("	'Before:LT',")
	Allmus.conditionslist.append("	'After:GT',")
	Allmus.conditionslist.append("	'Before and including:LTE',")
	Allmus.conditionslist.append("	'After and including:GTE',")
	Allmus.conditionslist.append("	'Specific year only:EQ',")
	Allmus.conditionslist.append("	'Apart from:NEQ'],")
	Allmus.conditionslist.append("")
	Allmus.conditionslist.append(" 'date'   :['Before:DLT','After:DGT',")
	Allmus.conditionslist.append("            'Before and including:DLTE',")
	Allmus.conditionslist.append("	    'After and including:DGTE',")
	Allmus.conditionslist.append("	    'Specific year only:DEQ',")
	Allmus.conditionslist.append("	    'Apart from:DNEQ'],")
	Allmus.conditionslist.append("'boolean':['True:True','False:False'],")
	Allmus.conditionslist.append("")
	Allmus.conditionslist.append("'other':['Matches:match','Not Match:notmatch'],")

	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		clist=instance.getGUIConditions()
		Allmus.conditionslist.append("'"+dkey+"':[")
		clist=instance.getGUIConditions()
		for c in clist:
		    parts=c.split(":")
		    Allmus.conditionslist.append("'"+parts[0]+":"+parts[1]+"',")
		
		Allmus.conditionslist[-1]=Allmus.conditionslist[-1].replace("',","'")
		Allmus.conditionslist.append("],")
		    
	Allmus.conditionslist[-1]=Allmus.conditionslist[-1].replace("],","]")
	Allmus.conditionslist.append("	}; ")

	return Allmus.conditionslist
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Initialise widgets from datatype implementations
    def initWidgets(self):

	## Basic types
	Allmus.widgets+=" var widgets= { \n"
	Allmus.widgetcodes+=" var widgetcode= { \n"
	
	## Ontologytypes
	for dkey, dval in definitions.DATATYPEDICT.iteritems():
	    # We have a class
	    # FIXTHIS check against list,range etc defined types as well
	    if (apputils.isDataClass(definitions.DATATYPEDICT[dkey])):
		instance=apputils.getDataClassInstance(definitions.DATATYPEDICT[dkey])
		widget=instance.getWidget()
		Allmus.widgets+="'"+dkey+"':'"+widget+"',\n"
		code=instance.getWidgetCode().replace("\n",'#')
		Allmus.widgetcodes+='"'+dkey+'":"'+code+'",\n'
		
	Allmus.widgets+="};"
	Allmus.widgets=Allmus.widgets.replace(",\n};","};").encode('ascii','ignore')
	Allmus.widgetcodes+="};"
	Allmus.widgetcodes=Allmus.widgetcodes.replace(",\n};","};").encode('ascii','ignore')

	return

    def allmusView(self):
	



	##print "datadict"
	##print definitions.DATATYPEDICT
	##print "conditiontypes"
	##print self.getConditionTypes()
	##print "widgets"
	##print Allmus.widgets
	##print "gotposet"
     ##print(Allmus.gotpost)
     ##print(os.path.dirname(os.path.realpath(__file__)))
     dircsv = os.path.dirname(os.path.realpath(__file__))

     ##print "attributes"
     ##print definitions.DEFAULT_SEARCH_FILTER_COLUMNS
     ##print "attrtypes"
     ##print definitions.ATTRITYPES
     ##print"datagroups"
     ##print definitions.DATAGROUPS
     ##print type(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)
     newdefs = []

     print("before")
     with open(dircsv + '/newmuseum.csv', 'rb') as csvfile:
        linereader = csv.reader(csvfile, delimiter='$', quotechar='"')

        row2 = next(linereader)
        next(linereader)
        next(linereader)
        row4 = next(linereader)

        for x, y in zip(list(row2),list(row4)):
            ##print "this is x"+x+" this is y"+y
            if y == 'Visible':
                newdefs.append(x)
        ##print "newdefs "
        ##print  newdefs



        ##print inputrow
     if (Allmus.conditionslist is None):
	    Allmus.conditionslist = self.getConditionTypesList()
	    self.initWidgets()
	    Allmus.view_attributes=self.getViewAttributes(newdefs)
     ##print("here")
     idlist=apputils.getValuesForType("project_id","xsd:string")
     #print idlist
     
     #f = open("out.csv","wb",encoding='utf-8')
     with open('out.csv', 'wb') as csvfile:
      cr = csv.writer(csvfile, delimiter=',')
      #cr = csv.writer(f,delimiter=',')
      cr.writerow(["museum_id".encode('utf-8'),"Name_of_museum".encode('utf-8'),"Address_line_1".encode('utf-8'),"Address_line_2".encode('utf-8'),"Village,_Town_or_City".encode('utf-8'),"Postcode".encode('utf-8'),"Latitude".encode('utf-8'),"Longitude".encode('utf-8'),"Admin_area".encode('utf-8'),"Accreditation".encode('utf-8'),"Governance".encode('utf-8'),"Size".encode('utf-8'),"Size_provenance".encode('utf-8'),"Subject_Matter".encode('utf-8'),"Year_opened".encode('utf-8'),"Year_closed".encode('utf-8'),"DOMUS_Subject_Matter".encode('utf-8'),"DOMUS_identifier".encode('utf-8'),"Primary_provenance_of_data".encode('utf-8'),"Identifier_used_in_primary_data_source".encode('utf-8'),"Area_Deprivation_index".encode('utf-8'),"Area_Deprivation_index_crime".encode('utf-8'),"Area_Deprivation_index_education".encode('utf-8'),"Area_Deprivation_index_employment".encode('utf-8'),"Area_Deprivation_index_health".encode('utf-8'),"Area_Deprivation_index_housing".encode('utf-8'),"Area_Deprivation_index_income".encode('utf-8'),"Area_Deprivation_index_services".encode('utf-8'),"Area_Geodemographic_group".encode('utf-8'),"Area_Geodemographic_group_code".encode('utf-8'),"Area_Geodemographic_subgroup".encode('utf-8'),"Area_Geodemographic_subgroup_code".encode('utf-8'),"Area_Geodemographic_supergroup".encode('utf-8'),"Area_Geodemographic_supergroup_code".encode('utf-8'),"Notes".encode('utf-8')])
      if (Allmus.muslist ==[]):
       for id in idlist:
		  musname=apputils.getPropertyForMuseumID("Name_of_museum", id)
		  addl1=apputils.getPropertyForMuseumID("Address_line_1", id)
		  addl2=apputils.getPropertyForMuseumID("Address_line_2", id)
		  mustown=apputils.getPropertyForMuseumID("Town_or_City", id)
		  postcode=apputils.getPropertyForMuseumID("Postcode", id)
		  latitude=apputils.getPropertyForMuseumID("Latitude", id)
		  longitude=apputils.getPropertyForMuseumID("Longitude", id)
		  adminarea=apputils.getPropertyForMuseumID("Admin_hierarchy", id)
		  accreditation=apputils.getPropertyForMuseumID("Accreditation", id)
		  governance=apputils.getPropertyForMuseumID("Governance", id)
		  size = apputils.getPropertyForMuseumID("Size", id)
		  sizeprov = apputils.getPropertyForMuseumID("Size_prov", id)
		  subjectmatter = apputils.getPropertyForMuseumID("Subject_Matter", id)
		  yearopen = apputils.getPropertyForMuseumID("Year_opened", id)
		  yearclosed = apputils.getPropertyForMuseumID("Year_closed", id)
		  domus_subject_matter = apputils.getPropertyForMuseumID("DOMUS_Subject_Matter", id)
		  domus_identifier = apputils.getPropertyForMuseumID("DOMUS_identifier", id)
		  provenance = apputils.getPropertyForMuseumID("Primary_provenance_of_data", id)
		  prov_identifier = apputils.getPropertyForMuseumID("Identifier_used_in_source_database", id)
		  deprivindex = apputils.getPropertyForMuseumID("Deprivation_index", id)
		  deprivindex_crime = apputils.getPropertyForMuseumID("Deprivation_index_crime", id)
		  deprivindex_edu = apputils.getPropertyForMuseumID("Deprivation_index_education", id)
		  deprivindex_employ = apputils.getPropertyForMuseumID("Deprivation_index_employment", id)
		  deprivindex_health = apputils.getPropertyForMuseumID("Deprivation_index_health", id)
		  deprivindex_housing = apputils.getPropertyForMuseumID("Deprivation_index_housing", id)
		  deprivindex_income = apputils.getPropertyForMuseumID("Deprivation_index_income", id)
		  deprivindex_services = apputils.getPropertyForMuseumID("Deprivation_index_services", id)
		  Gepdemographic_group = apputils.getPropertyForMuseumID("Geodemographic_group", id)
		  Gepdemographic_group_code = apputils.getPropertyForMuseumID("Geodemographic_group_code", id)
		  Gepdemographic_subgroup = apputils.getPropertyForMuseumID("Geodemographic_subgroup", id)
		  Gepdemographic_subgroup_code = apputils.getPropertyForMuseumID("Geodemographic_subgroup_code", id)
		  Gepdemographic_supergroup = apputils.getPropertyForMuseumID("Geodemographic_supergroup", id)
		  Gepdemographic_supergroup_code = apputils.getPropertyForMuseumID("Geodemographic_supergroup_code", id)
		  Notes = apputils.getPropertyForMuseumID("Notes", id)
          
          
          
		  
		  
		  cr.writerow([id.encode('utf-8'),musname.encode('utf-8'),addl1.encode('utf-8'),addl2.encode('utf-8'),mustown.encode('utf-8'),postcode.encode('utf-8'),latitude.encode('utf-8'),longitude.encode('utf-8'),adminarea.encode('utf-8'),accreditation.encode('utf-8'),governance.encode('utf-8'),size.encode('utf-8'),sizeprov.encode('utf-8'),subjectmatter.encode('utf-8'),yearopen.encode('utf-8'),yearclosed.encode('utf-8'),domus_subject_matter.encode('utf-8'),domus_identifier.encode('utf-8'),provenance.encode('utf-8'),prov_identifier.encode('utf-8'),deprivindex.encode('utf-8'),deprivindex_crime.encode('utf-8'),deprivindex_edu.encode('utf-8'),deprivindex_employ.encode('utf-8'),deprivindex_health.encode('utf-8'),deprivindex_housing.encode('utf-8'),deprivindex_income.encode('utf-8'),deprivindex_services.encode('utf-8'),Gepdemographic_group.encode('utf-8'),Gepdemographic_group_code.encode('utf-8'),Gepdemographic_subgroup.encode('utf-8'),Gepdemographic_subgroup_code.encode('utf-8'),Gepdemographic_supergroup.encode('utf-8'),Gepdemographic_supergroup_code.encode('utf-8'),Notes.encode('utf-8')])
		 #print(musname +", " +id +", " +mustown)
		  Allmus.muselist.append(id)
		  Allmus.muslist.append(musname)
     ##print(muslist)
     #muslist=muselist
       csvfile.close();
     Allmus.muslist, Allmus.muselist = zip(*sorted(zip(Allmus.muslist, Allmus.muselist)))
       #Allmus.muslist.sort()
     if (request.method == 'GET'):
            postrec="false"
            return render_template('allmus.html',
				   attributes=zip(newdefs,Allmus.view_attributes),
				   attritypes=definitions.ATTRITYPES,
				   muslist=zip(Allmus.muslist, Allmus.muselist),
				   datagroups=definitions.DATAGROUPS,
				   datadict=definitions.DATATYPEDICT,
				   conditiontypes=self.getConditionTypes(),
				   widgets=Allmus.widgets,
				   widgetcodes=Allmus.widgetcodes,
                   gotpost=postrec)
     ##print(request.form['Governance'])
     ##\\sprint(definitions.DEFAULT_SEARCH_FILTER_COLUMNS)
     print("gotpastit")
     file = open(dircsv+'/editmusfiles/editfileindex.txt', 'r')
     editindex = pickle.load(file)
     inputrow = ''
     newdefs.append('Name_of_museum')
     namemuseum=request.form['Name_of_museum']
     if(namemuseum not in muslist):
         postrec='true'
         return render_template('allmus.html',
							attributes=zip(newdefs, Allmus.view_attributes),
							attritypes=definitions.ATTRITYPES,
							message = "Error: Museum name not among list of suggestions. Please select from the list of provided museum names (These are automatically suggested as you type).",
                            muslist=muslist,
							datagroups=definitions.DATAGROUPS,
							datadict=definitions.DATATYPEDICT,
							conditiontypes=self.getConditionTypes(),
							widgets=Allmus.widgets,
							widgetcodes=Allmus.widgetcodes,
							gotpost=postrec) 
     
     return render_template('allmus.html',
							attributes=zip(newdefs, Allmus.view_attributes),
							attritypes=definitions.ATTRITYPES,
							message = "Thank you for submitting a correction on our data about a museum. We will be in touch with you if we require additional information. The data will be reviewed before uploading to our database which may take a while.",
                            muslist=muslist,
							datagroups=definitions.DATAGROUPS,
							datadict=definitions.DATATYPEDICT,
							conditiontypes=self.getConditionTypes(),
							widgets=Allmus.widgets,
							widgetcodes=Allmus.widgetcodes,
							gotpost=postrec)
				   

