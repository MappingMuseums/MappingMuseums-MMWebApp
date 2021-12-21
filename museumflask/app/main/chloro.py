##
# @file
#  This class implements the choropleths used for the various regions.
#  It provides the menu for the page and the data and boundary for leaflet
#  as well as the legend for the colours used.
#  
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

from . import mapchart

class Chloro():
    mapchart= mapchart.MapChart()

#-  -  -  -  -  -  -

## Purpose:Removes type info from name
    def getConfiguration(self):
	return mapchart.MapChart.t

#-  -  -  -  -  -  -  

## Purpose:Removes type info from name
# Arguments:
# @param prop = area to show

    def chloroView(self,prop):
	if (len(prop) < 1):
	    prop='county'
	boundary=prop.lower()
	grades='[0, 1, 5, 15, 20, 35, 50, 100]'

        if (request.method == 'GET'):
	    latomuseumsdict={}
            mapdata=[]
            mapdata.append("var museums=[")
	    mcount=0
            props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,definitions.POSTCODE]
	    try:
		results=apputils.getMarkerData(props)
	    except         Exception, e:
		print str(e)
		return render_template('message.html', title="Internal application error",message="Internal Application Error C-II detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

            rlen=len(results["results"]["bindings"])
            for result in results["results"]["bindings"]:
		postcode=""
		if (definitions.POSTCODE in result):
		    postcode=result[definitions.POSTCODE]["value"].replace(" ","")
		
                name=result[definitions.NAME_OF_MUSEUM]["value"]
                if (definitions.DOMUS_SUBJECTCLASSIFICATION in result):
                    sub=result[definitions.DOMUS_SUBJECTCLASSIFICATION]["value"]
                else:
                    sub="Unknown topic"
                lat=result[definitions.LATITUDE]["value"]
                lon=result[definitions.LONGITUDE]["value"]
                if (len(lat) > 0 and len(lon) >0):
                    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{}],'.format(name,sub,lat,lon))

		#postcode=result[definitions.POSTCODE]["value"].replace(" ","")
		if(boundary == 'localauth'):
		    if (postcode in definitions.POSTCODE2_LA_DICT):
			la=definitions.POSTCODE2_LA_DICT[postcode].replace('"','')
			if (la in latomuseumsdict):
			    latomuseumsdict[la].append(mcount)
			else:
			    latomuseumsdict[la]=[]
			    latomuseumsdict[la].append(mcount)
			    
		elif(boundary == 'county'):
		    if (postcode in definitions.POSTCODE2_COUNTY_DICT):
			la=definitions.POSTCODE2_COUNTY_DICT[postcode].replace('"','')
			if (la in latomuseumsdict):
			    latomuseumsdict[la].append(mcount)
			else:
			    latomuseumsdict[la]=[]
			    latomuseumsdict[la].append(mcount)
		    
		elif(boundary == 'region'):
		    if (postcode in definitions.POSTCODE2_REGION_DICT):
			la=definitions.POSTCODE2_REGION_DICT[postcode].replace('"','')
			if (la in latomuseumsdict):
			    latomuseumsdict[la].append(mcount)
			else:
			    latomuseumsdict[la]=[]
			    latomuseumsdict[la].append(mcount)
		    
		    
		elif(boundary == 'country'):
		    if (postcode in definitions.POSTCODE2_COUNTRY_DICT):
			la=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
			if (la in latomuseumsdict):
			    latomuseumsdict[la].append(mcount)
			else:
			    latomuseumsdict[la]=[]
			    latomuseumsdict[la].append(mcount)

		elif(boundary == 'combauth'):
		    if (postcode in definitions.POSTCODE2_LA_DICT):
			la=definitions.POSTCODE2_LA_DICT[postcode].replace('"','')
			if (la in apputils.LA_TO_CA_NAMES_TABLE):
			    caname=apputils.LA_TO_CA_NAMES_TABLE[la]

			    if (caname in latomuseumsdict):
				latomuseumsdict[caname].append(mcount)
			    else:
				latomuseumsdict[caname]=[]
				latomuseumsdict[caname].append(mcount)
		
		    
		mcount+=1

	    if(boundary == 'localauth'):
		grades='[0, 1, 5, 15, 20, 35, 50, 100]'
	    elif(boundary == 'county'):
		grades='[20, 30, 40, 50, 75, 100, 150, 200]'
	    elif(boundary == 'region'):
		grades='[100, 150, 200, 250, 300, 350, 400, 500]'
	    elif(boundary == 'comb auth'):
		grades='[100, 150, 200, 250, 300, 350, 400, 500]'
	    elif(boundary == 'country'):
		grades='[200, 150, 200, 250, 600, 700, 900, 1000]'
		

		
#	    print latomuseumsdict
            mapdata[-1]=mapdata[-1].replace("],","]")
            mapdata.append("];")
	    mapdata.append("district2museums={")
	    # iterating, always use iteritems !
	    for key, val in latomuseumsdict.iteritems():
		mapdata.append('"'+key.replace(" CA","")+'":'+str(val)+",")

            mapdata[-1]=mapdata[-1].replace("],","]")
            mapdata.append("};")
	    
	    return render_template('nakedchloro.html',
                                   alert=None,
                                   heading=boundary,
                                   mapdata=mapdata,
				   grades=grades,
				   boundarydata=definitions.JSONDATA[boundary],
                                   trees=self.getConfiguration(),
                                   title="Chloro")
                




