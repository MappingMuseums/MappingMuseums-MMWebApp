##
# @file
#  
# This class implements the view to show a specific museum with ID  
# It has two views; view default or view all. A button toggles the two.
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

import pandas as pd
import traceback
import sys
import pickle
import time
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class NakedId():
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

## Purpose:Local getview for this view
# Arguments:
# 
# @prop  type
# @value value

    def getView(self,prop,value):
        dataname=definitions.DEFNAME+prop
        if (prop in definitions.DATATYPEDICT):
            return self.modeltoview.getView(prop,value)
	elif(dataname in definitions.DATATYPEDICT):
            datatype=definitions.DATATYPEDICT[dataname]
            return self.modeltoview.getViewForType(datatype,value)
        return value


    def visitorsort(self,prop):
	tups=[]
	for p in prop:
	    parr=p.split(":")
	    tup=(parr[0],parr[1],parr[2],parr[3])
	    tups.append(tup)
	tups=sorted(tups, key=lambda x: x[2])
	newprops=[]
	for p in tups:
	    newprops.append(':'.join(p))
	tups=None
	return newprops    
	    
	    
## Purpose:Implements the FLASK view
# Returns a dictionary to show in the table
# Arguments:
# 
# @nid Project id to view
# @mid ?? not used

    def nakedidView(self,nid,mid):

	
        if (request.method == 'GET'):
	    
	    start_time = time.time()

	    try:
 		properties=apputils.getMuseumPropertiesForId(mid)
 	    except Exception, e:
 		print str(e)
 		return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 196   \n <br/><p><pre>"+str(e)+"</pre></p>")
	
	    pkeys=properties["head"]["vars"]
            pdict={}
            count=0
            for pk in pkeys:
                pdict[pk]=count
                count=count+1
        
        
            fdict={}
            allprops=[]
            for res in properties["results"]["bindings"]:
                for f in res:
		    if (not f in fdict):
			fdict[f]=[]
		    found=False
		    for di in fdict[f]:
			if (di == res[f]["value"]):
			    found=True
			    break
		    if (not  found):
			fdict[f].append(res[f]["value"])
                    if (f.startswith(definitions.DEFNAME)):
                        tup =(f[len(definitions.DEFNAME):].replace('_',' '),self.getView(f,res[f]["value"]))
                    elif (f.startswith(definitions.RANGENAME)):
                        tup =(f[len(definitions.RANGENAME):].replace('_',' '),self.getView(f,res[f]["value"]))
                    else:
                        tup =(f.replace('_',' '),self.getView(f,res[f]["value"]))
                    allprops.append(tup)
        
	    unique_props=set(allprops)



	    print("hello")
	    #del unique_props['Name of museum']

	    musname=''
	    addl1=''
	    addl2=''
	    town=''
	    postc=''
	    adminhi=''
	    accred=''
	    govern=''
	    siz=''
	    subj=''
	    yo=''
	    yc=''
	    musrm=''
	    print unique_props
	    for prop in unique_props:
	      print(prop)
	      if(prop[0]=='museum'):
	        musrm = prop
	      if(prop[0]=='Name of museum'):
	        musname = prop

	      if(prop[0]=='Address line 1'):
	        addl1 = prop

	      if(prop[0]=='Address line 2'):
	        addl2=prop

	      if(prop[0]=='Town or City'):
	        town=prop

	      if(prop[0]=='Postcode'):
	        postc=prop

	      if(prop[0]=='Admin hierarchy'):
	        adminhi=prop

	      if(prop[0]=='Accreditation'):
	        accred=prop

	      if(prop[0]=='Governance'):
	        govern=prop

	      if(prop[0]=='Size'):
	        siz=prop

	      if(prop[0]=='Subject Matter'):
	        subj=prop

	      if(prop[0]=='Year opened'):
	        yo=prop

	      if(prop[0]=='Year closed'):
	        yc=prop

	    unique_props = sorted(unique_props)
	    print("hello")
	    print(unique_props)
	    if(musrm!=''):
	      unique_props.remove(musrm)

	    if(yc!=''):
	      unique_props.remove(yc)
	      unique_props.insert(0,yc)

	    if(yo!=''):
	      unique_props.remove(yo)
	      unique_props.insert(0,yo)
	    if(subj!=''):
	      unique_props.remove(subj)
	      unique_props.insert(0,subj)
	    if(siz!=''):
	      unique_props.remove(siz)
	      unique_props.insert(0,siz)
	    if(govern!=''):
	      unique_props.remove(govern)
	      unique_props.insert(0,govern)
	    if(accred!=''):
	      unique_props.remove(accred)
	      unique_props.insert(0,accred)
	    if(adminhi!=''):
	      unique_props.remove(adminhi)
	      unique_props.insert(0,adminhi)
	    if(postc!=''):
	      unique_props.remove(postc)
	      unique_props.insert(0,postc)
	    if(town!=''):
	      unique_props.remove(town)
	      unique_props.insert(0,town)

	    if(addl2!=''):
	      unique_props.remove(addl2)
	      unique_props.insert(0,addl2)
	    if(addl1!=''):
	      unique_props.remove(addl1)
	      unique_props.insert(0,addl1)
	    if(musname!=''):
	      unique_props.remove(musname)
	      unique_props.insert(0,musname)

	    print("also hello")
	    print(unique_props)
	    if ( definitions.VISITORNUMBERS in fdict.keys()):
 		fdict[definitions.VISITORNUMBERS]=self.visitorsort(fdict[definitions.VISITORNUMBERS])
	    if ( definitions.STATUSCHANGE in fdict.keys()):
 		fdict[definitions.STATUSCHANGE]=self.visitorsort(fdict[definitions.STATUSCHANGE])
                    
        
            alltups=[[] for col in range(len(definitions.DEFAULT_VIEW_ALL_COLUMNS))]
            count=0

            for fi in definitions.DEFAULT_VIEW_ALL_COLUMNS:
                tups=[]
                field=str(fi)
                if ( field in fdict.keys()):
		    for di in fdict[field]:
			if (field.startswith(definitions.DEFNAME)):
			    tup =(field.replace('_',' '),self.getView(field.replace(definitions.DEFNAME,""),di))
			else:
			    tup =(field.replace('_',' '),self.getView(field,di))
			    
			tups.append(tup)
                alltups[count]=tups
                count=count+1
        
            
            museumname="Unknown"
        
            for res in properties["results"]["bindings"]:
                    if (definitions.NAME_OF_MUSEUM in res):
                        museumname=res[definitions.NAME_OF_MUSEUM]["value"]
                        break
                    
        
	    print("--- %s secondxs ---" % (time.time() - start_time))

            return render_template('nakedid.html',
                                   docid=mid,
                                   alltups=alltups,
                                   allprops=unique_props,
                                   museumname=museumname,
                                   title="Details about a museum")
        
