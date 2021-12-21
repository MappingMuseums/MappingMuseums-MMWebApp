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
class Bench():

###### NEED TO CHANGE REWRITE IF YOU CHANGE THE URI, MAYBE BOTH IN CONFIG AND DEFINTIONS ###

    dates=[
	definitions.HASNAME+definitions.YEAR_OPENED,
	definitions.HASNAME+definitions.YEAR_CLOSED
	   ]

    # Fields no longer used in configuration but needed in dispatch to select on
    fields=[
        definitions.HASNAME+definitions.YEAR_OPENED,
        definitions.HASNAME+definitions.YEAR_CLOSED,
        definitions.HASNAME+definitions.GOVERNANCE,
        definitions.HASNAME+definitions.COUNTY,
        definitions.HASNAME+definitions.ACCREDITATION,
	definitions.HASNAME+definitions.SUBJECT_MATTER
        ]
    ptrsdict={}
    ptr=0
    for b in fields:
	ptrsdict[b]=ptr
	ptr+=1

    ShowMuseumTypes = showmuseumtypes.ShowMuseumTypes()
    optlist=[
	definitions.YEAR_OPENED,
	definitions.YEAR_CLOSED,
	"Exists",
	"All"
	
	]

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def benchView(self,propertytodisplay):

	mapdata=[]
	mapindex=0
	mapdata.append("var museums=[")
	idtoindexmap={}
	
	dictdata=[]
	dictdata.append("museumdict={")
	treedict=self.ShowMuseumTypes.treedict
	for key, val in treedict.iteritems():
	    arrs=""
	    vallen=len(val)-1
	    icount=0
	    for item in val:
		count,url,name,sub,lat,lon=(item)
		parts=url.split("/")
		plen=len(parts)-1
		href=parts[plen]
		if (len(sub) == 0):
		    sub="Unknown"
		if (href not in idtoindexmap):
		    idtoindexmap[href]=mapindex
		    thisindex=mapindex
		    mapindex+=1
		    mapdata.append('["{}","{}","{}",{},{}],'.format(href,name,sub,lat,lon))
		else:
		    thisindex=idtoindexmap[href]
		    
		# print str(icount)+":"+str(vallen)
		if (icount==vallen):
		    alist='[{},{}]'.format(count,thisindex)
		    #print "alist:"+alist
		    arrs=arrs+alist
		else:
		    alist='[{},{}],'.format(count,thisindex)
		    #print "alist:"+alist
		    arrs=arrs+alist
		    icount=icount+1

	    dictdata.append('"'+key+'":['+arrs+"],")
	dictdata[-1]=dictdata[-1].replace("]],","]]")
	dictdata.append("};")


	mapdata[-1]=mapdata[-1].replace("],","]")
	mapdata.append("];")

#   	for dc in dictdata:
#   	    print "-----------------------------------------------------------"
#   	    print str(dc)
#   	    print "-----------------------------------------------------------"

        if (request.method == 'GET' and propertytodisplay != None):
            
            columns=""
            count=0
            ordercolumn="?"+str(propertytodisplay)
            if ( propertytodisplay == self.fields[self.ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.YEAR_CLOSED]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+definitions.YEAR_CLOSED)
                except Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error Y detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
            
                treetext=self.delegate_foundationyear(definitions.YEAR_CLOSED,results)
            elif (propertytodisplay == self.fields[self.ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.YEAR_OPENED]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+definitions.YEAR_OPENED)
                except  Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error Z detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
            
                treetext=self.delegate_foundationyear(definitions.YEAR_OPENED,results)
            elif (propertytodisplay == self.fields[self.ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.COUNTY]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+propertytodisplay)
                except    Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error A-II detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
                
                treetext=self.delegate_countyproperty(definitions.COUNTY,results)
            #else:

	    
            return render_template('bench.html',
				   results=treetext,
				   trees=self.ShowMuseumTypes.getConfiguration(),
				   dicts=dictdata,
				   options=self.optlist,
				   mapdata=mapdata,
				   property=propertytodisplay)
        else:
	    dim=self.ShowMuseumTypes.getDimensionTree()
	    print "?#?#? bench.py at line: 158 Dbg-out variable \dim [",dim,"]\n";
	    
            return render_template('bench.html',
				   dim=dim,
				   loc=self.ShowMuseumTypes.getLocationTree(),
				   dicts=dictdata,
				   options=self.optlist,
				   mapdata=mapdata,
				   results=None)



