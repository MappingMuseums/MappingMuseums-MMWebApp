##
# @file
# This class implements the map page view 
#  
# Returns the map data (lat/lon/subject) for a property to show to Leaflet
# and the menu of properties
#  
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

from altair import Chart, Color, Scale
import pandas as pd
import traceback
import sys
import pickle

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

class MapChart():

#-  -  -  -  -  -  -
    t=None
    boundaries={}
    boundaries['England']=['Region','County','Local auth']
    boundaries['Scotland']=['County','Local auth']
    boundaries['Northern Ireland']=['County','Local auth']
    boundaries['Wales']=['County','Local auth']
    locations=['Country','Region','County','Comb auth','Local auth']

    countries=['England','Scotland','Northern Ireland','Wales']
    time_range=[definitions.YEAR_OPENED,definitions.YEAR_CLOSED]
    modeltoview=model_to_view.Model_To_View()

#-  -  -  -  -  -  -


## Purpose:Return menu
    def getConfiguration(self):
	if (not MapChart.t):
	    MapChart.t=self.getConfiguration_work()
	return MapChart.t

## Purpose:Create menu
    def getConfiguration_work(self):
	fields=[
	    definitions.HASNAME+definitions.ACCREDITATION,
	    definitions.HASNAME+definitions.GOVERNANCE
	    ]
	first=True

        t = tree.Tree("Museums",False,False,"menu")
	t.addLeaf('<a href="{}" target="restable">{}</a>'.format("/map/all",'All'))
	b=fields[0]
	t.addNodeAndLevel('{}'.format(b.replace('_',' ').replace(definitions.HASNAME,'')),False,False)


	subprops=listman.getList(b.replace(definitions.HASNAME,'')+definitions.LISTNAME)
	if (len(subprops) > 0):
	    for s in subprops:
		t.addLeaf('<a href="{}" target="restable">{}</a>'.format("/map/"+b+"/"+s,s.replace('_',' ')))

	t.addNodeAtCurrentLevel("Date",False,False)

	b="Year_open"
	t.addLeaf('<a href="{}" target="restable">{} </a>'.format("/timerange/"+b.replace(' ','').replace(definitions.HASNAME,''),b.replace('_',' ').replace(definitions.HASNAME,'')))
	b="Year_closed"
	t.addLeaf('<a href="{}" target="restable">{} </a>'.format("/timerange/"+b.replace(' ','').replace(definitions.HASNAME,''),b.replace('_',' ').replace(definitions.HASNAME,'')))
	b=definitions.YEAR_OF_FOUNDATION
	t.addLeaf('<a href="{}" target="restable">{} </a>'.format("/timerange/"+b.replace(' ','').replace(definitions.HASNAME,''),b.replace('_',' ').replace(definitions.HASNAME,'')))
	t.closeLevel()


	t.addNodeAndLevel("Locations",False,False)
	for b in self.locations:
	    t.addLeaf('<a href="{}" target="restable">{} </a>'.format("/chloro/"+b.replace(' ',''),b))
	t.closeLevel()

	b=definitions.HASNAME+definitions.SUBJECT_MATTER
 	t.addNodeAtCurrentLevel('{}'.format(b.replace('_',' ').replace(definitions.HASNAME,'')),False,False)

 	subprops=listman.getList(b.replace(definitions.HASNAME,'')+definitions.LISTNAME)
	print "?#?#? views.py at line: 325 Dbg-out variable \subprops [",str(subprops),"]\n";
 	if (len(subprops) > 0):
 	    subtree=self.modeltoview.getTreeView(subprops,definitions.DEFINED_HIERTYPE,"subjectMatterAction",definitions.SUBJECT_MATTER)
	    print "?#?#? views.py at line: 328 Dbg-out variable \subtree [",str(subtree),"]\n";
 	    t.addSubTree(subtree,1)
			
	# add domus to subject matter
	domus=definitions.HASNAME+definitions.DOMUS_SUBJECTCLASSIFICATION
	t.addNodeAndLevel('{}'.format(domus.replace('_',' ').replace(definitions.HASNAME,'')),False,False)
	subprops=listman.getList(domus.replace(definitions.HASNAME,'')+definitions.LISTNAME)
	if (len(subprops) > 0):
	    for s in subprops:
		t.addLeaf('<a href="{}" target="restable">{}</a>'.format("/map/"+domus+"/"+s,s.replace('_',' ')))
			


        t.addNodeAtCurrentLevel("Visitor numbers",True,False)
	t.addLeaf('<a href="{}" target="restable">{}</a>'.format("/map/all",'Yet to come'))
	    




	t.closeLevel()
        t.closeTree()
        

        return t.getTree()

#-  -  -  -  -  -  -  

## Purpose:Implements the FLASK view
# Arguments:
# @prop    the property to show
# @subprop the possible subproperty to show

    def mapchartView(self,prop,subprop):

	
        if (request.method == 'GET'):
            mapdata=[]
            mapdata.append("var museums=[")

	    if (prop == "all"):
		props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,definitions.PROJECT_ID]
		    
		try:
		    results=apputils.getMarkerData(props)
		except    Exception, e:
		    print str(e)
		    return render_template('message.html', title="Internal application error",message="Internal Application Error G-II detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
	    
		rlen=len(results["results"]["bindings"])
		for result in results["results"]["bindings"]:
		    name=result[definitions.NAME_OF_MUSEUM]["value"]
		    href="Error_no_id"
		    if (definitions.PROJECT_ID in result):
			mid=result[definitions.PROJECT_ID]["value"]
			if (len(mid) > 0):
			    href="http://"+app.config['URLREWRITEPATTERN']+"Museum/nid/n0/"+mid
			    if (definitions.DOMUS_SUBJECTCLASSIFICATION in result):
				sub=result[definitions.DOMUS_SUBJECTCLASSIFICATION]["value"]
			    else:
				sub="Unknown"
			    lat=result[definitions.LATITUDE]["value"]
			    lon=result[definitions.LONGITUDE]["value"]
			    if (len(lat) > 0 and len(lon) >0):
				mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},"{}"],'.format(name,sub,lat,lon,href))
                        
		mapdata[-1]=mapdata[-1].replace("],","]")
		mapdata.append("];")
		
		return render_template('nakedmap.html',
				       alert=None,
				       heading="All",
				       mapdata=mapdata,
				       trees=self.getConfiguration(),
				       title="Map")
		
	    elif (not prop):
            
                return render_template('map.html',
				       alert=None,
				       heading='',
				       mapdata=None,
				       trees=self.getConfiguration(),
				       title="Map")
                
		
	    else:
		qprop=prop.replace(definitions.HASNAME,'')
		if (qprop == definitions.DOMUS_SUBJECTCLASSIFICATION):
		    props=[definitions.NAME_OF_MUSEUM,qprop,definitions.PROJECT_ID]
		else:
		    props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,qprop,definitions.PROJECT_ID]
		    
		try:
		    results=apputils.getMarkerData(props)
		except    Exception, e:
		    print str(e)
		    return render_template('message.html', title="Internal application error",message="Internal Application Error H-II detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
	    
		rlen=len(results["results"]["bindings"])
		for result in results["results"]["bindings"]:
		    name=result[definitions.NAME_OF_MUSEUM]["value"]
		    href="Error_no_id"
		    if (definitions.PROJECT_ID in result):
			mid=result[definitions.PROJECT_ID]["value"]
			if (len(mid) > 0):
			    href="http://"+app.config['URLREWRITEPATTERN']+"Museum/nid/n0/"+mid
			    
		    if (qprop in result and result[qprop]["value"] == subprop):
			if (definitions.DOMUS_SUBJECTCLASSIFICATION in result):
			    sub=result[definitions.DOMUS_SUBJECTCLASSIFICATION]["value"]
			else:
			    sub="Unknown"
			lat=result[definitions.LATITUDE]["value"]
			lon=result[definitions.LONGITUDE]["value"]
			if (len(lat) > 0 and len(lon) >0):
			    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},"{}"],'.format(name,sub,lat,lon,href))
                        
		mapdata[-1]=mapdata[-1].replace("],","]")
		mapdata.append("];")
		
		return render_template('nakedmap.html',
				       alert=None,
				       heading=subprop,
				       mapdata=mapdata,
				       trees=self.getConfiguration(),
				       title="Map")
        else:
	    return render_template('message.html',
				   title="Method not supported",
				   message="Only GET is supported")
	

