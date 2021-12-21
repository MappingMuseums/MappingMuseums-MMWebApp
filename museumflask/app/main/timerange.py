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

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class TimeRange():

    mapchart= mapchart.MapChart()

#-  -  -  -  -  -  -

    def getConfiguration(self):
	return mapchart.MapChart.t

#-  -  -  -  -  -  -  

    def timerangeView(self,prop):
	timeprop=prop
	mapdata=[]
	mapdata.append("var museums=[")

        if (request.method == 'GET'):
	    if (prop == definitions.YEAR_OF_FOUNDATION):
		props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,definitions.YEAR_OF_FOUNDATION]
	    elif (prop == 'Year_open'):
		props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,definitions.YEAR_OPENED]
	    else:
		props=[definitions.NAME_OF_MUSEUM,definitions.DOMUS_SUBJECTCLASSIFICATION,definitions.YEAR_CLOSED]
		
	    try:
		results=apputils.getMarkerData(props)
	    except       Exception, e:
		print str(e)
		return render_template('message.html', title="Internal application error",message="Internal Application Error B-II detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

	    #pp = pprint.PrettyPrinter(indent=4)
	    #pp.pprint(results)


	    # THIS CAN BE COMMENTED IN WHEN COLUMNS CONTAIN 2 VALUES LATER
# 	    if (prop == "Year_open"):

# 		# This column contains 2 values so we re-package and do one at the time
# 		for res in results["results"]["bindings"]:
# 		    year=res[definitions.YEAR_OPENED_AND_CLOSED]["value"]
# 		    if (year.find(":") > -1):
# 			parts=year.split(":")
# 			openval=parts[0].strip()
# 			closedval=parts[1].strip()
# 			if (len(openval) < 4):
# 			    openval="9999"
# 		    res[definitions.YEAR_OPENED_AND_CLOSED]["value"]=openval
		

# 	    elif(prop == "Year_closed"):
# 		for res in results["results"]["bindings"]:
# 		    if (definitions.YEAR_OPENED_AND_CLOSED in res):
# 			year=res[definitions.YEAR_OPENED_AND_CLOSED]["value"]
# 			if (year.find(":") > -1):
# 			    parts=year.split(":")
# 			    closedval=parts[1].strip()
# 			    if (len(closedval) < 4):
# 				closedval="9999"
# 			res[definitions.YEAR_OPENED_AND_CLOSED]["value"]=closedval
		

		
	    rlen=len(results["results"]["bindings"])
	    for result in results["results"]["bindings"]:
		lat=result[definitions.LATITUDE]["value"]
		lon=result[definitions.LONGITUDE]["value"]
		if (len(lat) > 0 and len(lon) >0):
		    name=result[definitions.NAME_OF_MUSEUM]["value"]
		    if (definitions.DOMUS_SUBJECTCLASSIFICATION in result):
			sub=result[definitions.DOMUS_SUBJECTCLASSIFICATION]["value"]
		    else:
			sub="Unknown topic"
		    uri=result["museum"]["value"]
		    href='"'+'/Museum/nid/n0'+uri[50:]+'"'
		    if (prop == definitions.YEAR_OF_FOUNDATION):
			if (definitions.YEAR_OF_FOUNDATION in result):
			    yof=result[definitions.YEAR_OF_FOUNDATION]["value"]
			    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},{},{}],'.format(name,sub,lat,lon,href,yof))

		    elif (prop == 'Year_open'):
			if (definitions.YEAR_OPENED in result):
			    yof=result[definitions.YEAR_OPENED]["value"]
			    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},{},{}],'.format(name,sub,lat,lon,href,yof))

		    elif (prop == definitions.YEAR_CLOSED):
			if (definitions.YEAR_CLOSED in result):
			    yof=result[definitions.YEAR_CLOSED]["value"]
			    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},{},{}],'.format(name,sub,lat,lon,href,yof))


# 		    else:
# 			year=result[definitions.YEAR_OPENED_AND_CLOSED]["value"]
# 			if (year != "9999" ):
# 			    mapdata.append('["<b>{}<b><br/>Subject:{}",{},{},{},{}],'.format(name,sub,lat,lon,href,year))
		    
                
                        
	    mapdata[-1]=mapdata[-1].replace("],","]")
	    mapdata.append("];")

            
	    return render_template('nakedtimerange.html',
				   alert=None,
				   heading=prop.replace("_"," "),
				   mapdata=mapdata,
				   trees=self.getConfiguration(),
				   title="Map",
				   prop=prop)
                




