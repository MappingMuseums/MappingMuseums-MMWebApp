##
# @param file
#  This file builds the menus for the browse page and also generates a dictionary
#  with all the museums and their location and classification
#  
#  The data is shown in the render call:  
#              return render_template('browseproperties.html',
#				   trees=ShowMuseumTypes.getConfiguration(),
#				   dicts=ShowMuseumTypes.dictdata,
#				   mapdata=ShowMuseumTypes.mapdata,
#				   results=None)
#
#
#    trees contain the menus; dicts contain the master museum dictionary and  
#    mapdata contains the lat/long and other data for Leaflet.
#    The dictionary assembled contains for each museum a tuple like this:
#    (id,lcount,href,name,sub,lat,lon)
#    where id -> projid
#          lcount -> length of museum vector
#          href -> action to take
#          name -> name
#          sub  -> 2018 subject
#          lat  -> lat
#          lon  -> lon
#          
#    Because it takes a long time to assemble this it has a FAST and a SLOW
#    configuration. In slow mode all models are built and pickled. In fast
#    it uses the pickled models. The choice is determined from the configuration
#    of the DEV_MODE variable. Both variations cache all the data for future calls.
#
#   SLOW mode needs to be used if the database has changed so that models are
#   rebuilt from scratch.
#   Most of the code in this class is concerned with building the menus and the
#   particulars.
#    
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
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
from . import CustomSort
from . import Configuration

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
import re

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ShowMuseumTypes():


    dates=[
	   definitions.HASNAME+definitions.YEAR_OPENED,
	   definitions.HASNAME+definitions.YEAR_CLOSED
	   ]

## Fields no longer used in configuration but needed in dispatch to select on
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



##   MENUS
    menutree=None
    locationtree=None
    dimensiontree=None
    treedict={}
## Sorting
    customsort=CustomSort.CustomSort()
    
## Conversion of model values to view
    modeltoview=model_to_view.Model_To_View()
    level =1
    stopwords=['of','and','&','museum','collection ','gallery ','national','historical']

## Data for Leaflet
    mapdata=[]

## master museum dictionary 
    dictdata=[]

#-  -  -  -  -  -  -  


    @staticmethod
    def getConfiguration():
	return ShowMuseumTypes.menutree

    @staticmethod
    def getLocationTree():
	return ShowMuseumTypes.locationtree

    @staticmethod
    def getDimensionTree():
	return ShowMuseumTypes.dimensiontree

    @staticmethod
    def getPtrsDict():
	return ShowMuseumTypes.ptrsdict

    @staticmethod
    def getMuseumDict():
	return ShowMuseumTypes.treedict
    

#-  -  -  -  -  -  -  
    def removeStopWords(self,sname):
	for word in ShowMuseumTypes.stopwords:
	    if (sname.find(word)>-1):
		sname=sname
	return sname

#-  -  -  -  -  -  -  
    def getShortName(self,name):
	namelenlimit=40
	sname=name.strip().lower()
	rname=self.removeStopWords(sname)
	rname=re.sub(r'(?:^|\ )(\w)', lambda x: ' '+x.group(1).upper(), rname)
	return rname

#-  -  -  -  -  -  -  

    def pickleDict(self,dict,name):
	with open(definitions.BASEDIR+name+'.pickle','wb') as f:
	    pickle.dump(dict, f, pickle.HIGHEST_PROTOCOL)
	f.close()
	return

#-  -  -  -  -  -  -  

    def loadDict(self,name):
	with open(definitions.BASEDIR+name+'.pickle','rb') as f:
	    o=pickle.load( f )
	f.close()
	return o 

#-  -  -  -  -  -  -  
    
    def addToDict(self,id,lcount,href,name,sub,lat,lon):
	tup=(lcount,href,name,sub,lat,lon)
	if (id in self.treedict):
	    if (not tup in self.treedict[str(id)]):
		self.treedict[str(id)].append(tup)
	else:
	    self.treedict[str(id)]=[]
	    self.treedict[str(id)].append(tup)
	
	return

    def getDictEntryLen(self,id):
	if (id in self.treedict):
	    return len(self.treedict[str(id)])+1
	else:
	    return 1

    def addListToDict(self,listofmuseums,t):
	print(t)
	print(t.getId())
	lcount=self.getDictEntryLen(t.getId())
	print (lcount)
	counter = 0
	for ltuple in sorted(listofmuseums, key=lambda x: x[1]):
	    counter=counter+1
	    if (str(type(ltuple[0])) == "<type 'tuple'>" ) :
		self.addListToDict(ltuple,t)
	    else:
		if (len(ltuple) < 5):
		    traceback.print_stack(file=sys.stdout)
		elif (len(ltuple) ==  5):
		    museum,name,sub,lat,lon=ltuple
		elif (len(ltuple) ==  6):
		    year,museum,name,sub,lat,lon=ltuple

		shortname=self.getShortName(name)
		href=museum.replace(definitions.RDFDEFURI,
				    app.config['URLREWRITEPATTERN']).replace("/id/","/nid/")

		#print("called it")
		#print(t.getId())
		#print(lcount)
		self.addToDict(t.getId(),lcount,href,shortname,sub,lat,lon)
		lcount=lcount+1
	print("counter")
	print(counter)
	return

    def addListToDictWithId(self,listofmuseums,id):
	lcount=self.getDictEntryLen(id)
	for ltuple in sorted(listofmuseums, key=lambda x: x[1]):
	    museum,name,sub,lat,lon=ltuple
	    self.addToDict(id,lcount,museum,name,sub,lat,lon)
	    lcount=lcount+1
	return
    
#-  -  -  -  -  -  -  

## Purpose:Creates a tree from the nodes in the model. 
# Arguments:
# @param model nodes list
# @param modelmap data to be added to tree node

    def getPtree(self,model,modelmap):
	ptree = PTreeNode('Root')
	for ele in model:
	    node=ele.replace(definitions.HTTPSTRING+definitions.RDFDEFURI_NOENDINGSLASH,"")
	    node=node.replace("-","/")
	    if (not node.startswith("/")):
		node="/"+node
	    if (node not in modelmap):
		print "====================================================="
		print "&&&&&& EWRRROIOR "+node+" NOT IN MODELMAP !"
		print "This is fine as long as no class in top hier"
		print "====================================================="
		op=0
	    else:
		ptree.addNode(node,data=modelmap[node])
	return ptree

#-  -  -  -  -  -  -

## Purpose:Count number of museums in node.
# Arguments:
# @param node to count from
    def getMuseumCount(self,node):
	mcount=0
        if (node.isLeaf()):
	    if (node.data != None):
		mcount=mcount+len(node.data)
        else:
	    if (node.data == None):
		noop=0
	    else:
		mcount=mcount+len(node.data)
	    for kid in node.children:
		mcount=mcount+self.getMuseumCount(kid)

        return mcount

#-  -  -  -  -  -  -

## Purpose:Recursively creates a HTML menu tree from the node
# Arguments:
# @param node root node
# @param t HTML tree
# @param menuname unique name for this menu
# @param action What happens when node is clicked
# @param path path to node in tree

    def getHTMLTree(self,node,t,menuname,action,path):
        ##print("printing node")
        ##print(node.data)
        if (not t):
            t = tree.Tree(None,False,False,menuname)
        if (node.isLeaf()):
	    newid=t.getId()+":"+node.name.strip()

	    datalen=""
	    if (node.data != None):
		datalen=str(len(node.data))
            t.addLeaf('<label id="'+newid+"L"+'" class="nocheck" onClick="{}">{} [{}]</label>'.format(
		action+'(this,\''+newid+'\',\''+node.name.strip()+' ['+datalen+']\')',
		node.name.replace("_"," "),
		datalen)
		)
	    if (not datalen == ""):
		self.addListToDictWithId(node.data,newid)
		self.addListToDictWithId(node.data,t.getId())
	    
        else:
	    opennode=True
	    if (self.level > 1):
		opennode=False
		
	    if (node.data == None):
		t.addNodeAndLevel(node.name.replace("_"," "),opennode,False,action)
	    else:
		mcount=0
		for kid in node.children:
		    mcount=mcount+self.getMuseumCount(kid)

		t.addNodeAndLevel(node.name.replace("_"," ")+" ["+str(mcount)+"]",opennode,False,action)

            for kid in node.children:
                self.level += 1
                self.getHTMLTree(kid,t,menuname,action,path+"/"+kid.name.strip())
                self.level -= 1
            t.closeLevel()
        return t

#-  -  -  -  -  -  -

## Purpose:Builds a map of a hierarchy from the database and returns the map
# Arguments:
# @param results Resultset from db
# @param property Name of hierarchy

    def getHierMapAndTotals(self,results,property):

        typemap={}
	totallist=[]
	

        for res in results["results"]["bindings"]:
	    if (property in res):
		mtype=res[property]["value"].encode('utf-8')
		uri=res["museum"]["value"].encode('utf-8')
		name=res[definitions.NAME_OF_MUSEUM]["value"].encode('utf-8')
		lat=res[definitions.LATITUDE]["value"]
		lon=res[definitions.LONGITUDE]["value"]
		if (definitions.SUBJECT_MATTER in res):
		    sub=res[definitions.SUBJECT_MATTER]["value"]
		else:
		    sub="Unknown"
	    
		mtuple=(uri,name,sub,lat,lon)
		if (not mtype in typemap):
		    typemap[str(mtype)]=[]

		mtypelist=typemap[str(mtype)]
		mtypelist.append(mtuple)

        propkeys=typemap.keys()
	shortkeytypemap={}
        for akey in typemap:
            listoftuples=typemap[akey]
            sortedtuples=sorted(listoftuples,key=lambda tup: tup[1])
	    listoftuples=None
	    newkey=akey.replace("http://bbk.ac.uk/MuseumMapProject/def","")
	    newkey=newkey.replace("-","/")
	    shortkeytypemap[newkey]=sortedtuples
	    totallist=totallist+sortedtuples

	typemap=None
	return shortkeytypemap,totallist
    
#-  -  -  -  -  -  -  

## Purpose:Initialises models from previously pickled build
    def FASTconfig(self):
	
	menut=tree.Tree(None,False,False,"menu")
        ShowMuseumTypes.menutree      = menut.loadTree("menut")
	ShowMuseumTypes.ptrsdict      = self.loadDict("ptrsdict")
	ShowMuseumTypes.treedict      = self.loadDict("treedict")
	
	return ShowMuseumTypes.menutree


#-  -  -  -  -  -  -  
## Purpose:Builds the menu from scratch by retrieving data from the db for
#  each property(column) to include in the menu.

    def SLOWconfig(self):

 	try:
	    props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID]
 	    results=apputils.getMarkerData(props)
 	except Exception, e:
 	    print str(e)
 	    return render_template('message.html', title="Internal application error",message="Internal Application Error N detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
	
	total_list=[]

	stopper = 1
	for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            name=res[definitions.NAME_OF_MUSEUM]["value"].encode('utf-8')
	    lat=res[definitions.LATITUDE]["value"]
	    lon=res[definitions.LONGITUDE]["value"]
	    if (definitions.SUBJECT_MATTER in res):
		sub=res[definitions.SUBJECT_MATTER]["value"]
	    else:
		sub="Unknown"
	    savetuple=(uri,name,sub,lat,lon)
	    total_list.append(savetuple)


	menut = tree.Tree("Museums ["+str(len(total_list))+"]",False,False,"menu")
	#self.addListToDict(total_list,menut)
	##the above call is removed as it seems to add a copy of all museums to the base dict

	#### Handling of generic properties
	DEFAULT_BROWSE_COLUMNS=apputils.readList(definitions.BASEDIR+'DEFAULT_BROWSE_COLUMNS.txt')

	for col in DEFAULT_BROWSE_COLUMNS:
	    defcol=definitions.DEFNAME+col
	    itype=None
	    if (defcol in definitions.DATATYPEDICT ):
		itype=definitions.DATATYPEDICT[defcol]
	    elif (col in definitions.DATATYPEDICT ):
		itype=definitions.DATATYPEDICT[col]
	    else:
		print "WARNING **** No handler for :"+col




	    if(itype == definitions.DEFINED_LISTTYPE):


		try:
		    props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID,col]
		    results=apputils.getMarkerData(props)
		except Exception, e:
		    print str(e)
		    return render_template('message.html', title="Internal application error",message="Internal Application Error O detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
       
		subtree,total_list=self.delegate_genericproperty(results,col)

		menut.addNodeAndLevel (col.replace('_',' ')+" ["+str(len(total_list))+"]",False,False)
		#print(menut.getTree())
		if(col!="Size"):
			subtree.closeLevel()
			menut.addSubTree(subtree,1)
			menut.closeLevel()

		#print("total")
		if(col=="Size"):
			#filel = open("./myfile.txt", "w")

			#print(total_list)
			counter = 0
			print("printing list length")
			for item in total_list:
				 counter = counter+1
			print(counter)
			print menut.getId()
			print menut.getTree()
			print menut.getDict()
			#print (col)
			#print(menut)
			#stopper = 0

		self.addListToDict(total_list,menut)
		if(col=="Size"):
			subtree.closeLevel()
			menut.addSubTree(subtree, 1)
			menut.closeLevel()
		total_list=None

	    elif(itype == definitions.DEFINED_HIERTYPE):
		print("lol")
		print (col)
		print("elifitype")
		print(itype)
		try:
		    if (col == definitions.SUBJECT_MATTER):
			print("its if")
			props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID]
		    else:
			print("its else")
			props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID,col]
		    results=apputils.getMarkerData(props)
		except Exception, e:
		    print str(e)
		    return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 525   \n <br/><p><pre>"+str(e)+"</pre></p>")


		b=definitions.HASNAME+col

		subprops=listman.getList("defClass"+b.replace(definitions.HASNAME,'')+definitions.LISTNAME)

		options=apputils.getOptionsDict(col,definitions.MAINSHEET) 
		if ("sortoption" in options):
		    print("sortoption in options")
		    method=options["sortoption"]
		    print("method")
		    ##print(method)
		    if (callable(getattr(ShowMuseumTypes.customsort, method))):
			print("callable")
			func = getattr(ShowMuseumTypes.customsort, method)
			sortedsubprops=func(subprops)
		    else:
			print("not callable")
			sortedsubprops=sorted(subprops)
		else:
		    print("sortoption not in options")
		    sortedsubprops=sorted(subprops)
			
		


		if (len(sortedsubprops) > 0):
		    print("len(sortedsubprops) > 0")
		    modelmap,totallist=self.getHierMapAndTotals(results,col)
		    menut.addNodeAndLevel('{} [{}]'.format(b.replace('_',' ').replace(definitions.HASNAME,''),
							 str(len(totallist))
							 ),False,False)

		    print("addingtodict")
		    counter = 0
		    for item in totallist:
		     counter = counter+1
		    print(counter)
		    self.addListToDict(totallist,menut)

		    ptree=self.getPtree(sortedsubprops,modelmap)
		    subtree=None
		    level=1

		    subtree=self.getHTMLTree(ptree,subtree,col,'ShowMuseums',"")

		    print("adding sub")
		    ##print(subtree)
		    menut.addSubTree(subtree,1)

		    total_list=None

	    elif(itype == 'xsd:positiveInteger'):

		print("itype == 'xsd:positiveInteger'")
		try:
		    props=[definitions.NAME_OF_MUSEUM,definitions.PROJECT_ID,col]
		    print "?#?#? showmuseumtypes.py at line: 498 Dbg-out variable \props [",props,"]\n";
		    results=apputils.getMarkerData(props)
		except Exception, e:
		    print str(e)
		    return render_template('message.html', title="Internal application error",message="Internal Application Error P detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
       
		subtree,total_list=self.delegate_genericproperty(results,col)
		menut.addNodeAndLevel (col.replace('_',' ')+" ["+str(len(total_list))+"]",False,False)

		self.addListToDict(total_list,menut)
		subtree.closeLevel()
		menut.addSubTree(subtree,1)
		menut.closeLevel()
	
		total_list=None
		
	    else:
		print "WARNING **** No handler for :"+col+" type:"+itype

	#### END Handling of generic properties


  	locationlist=[]

  	Esubtree,total_list=self.getEnglandTree()
  	locationlist=locationlist+total_list

  	Wsubtree,total_list=self.getGenericLocationTree('Wales','(pseudo) Wales','W')
  	locationlist=locationlist+total_list

  	NIsubtree,total_list=self.getGenericLocationTree('Northern Ireland','(pseudo) Northern Ireland','NI')
  	locationlist=locationlist+total_list

  	Ssubtree,total_list=self.getGenericLocationTree('Scotland','(pseudo) Scotland','S')
  	locationlist=locationlist+total_list

   	channelsubtree,total_list=self.getGenericLocationTree('Channel Islands','(pseudo) Channel Islands','Ch')
   	locationlist=locationlist+total_list

   	iomsubtree,total_list=self.getGenericLocationTree('Isle of Man','(pseudo) Isle of Man','Imn')
   	locationlist=locationlist+total_list


  	menut.addNodeAndLevel("Location"+" ["+str(len(locationlist))+"]",False,False)
  	self.addListToDict(locationlist,menut)

  	menut.addSubTree(Esubtree,1)
  	menut.closeLevel()

  	Wsubtree.closeLevel()
  	menut.addSubTree(Wsubtree,1)

  	NIsubtree.closeLevel()
  	menut.addSubTree(NIsubtree,1)

  	Ssubtree.closeLevel()
  	menut.addSubTree(Ssubtree,1)

  	channelsubtree.closeLevel()
   	menut.addSubTree(channelsubtree,1)

   	iomsubtree.closeLevel()
   	iomsubtree.closeLevel()
   	menut.addSubTree(iomsubtree,1)

  	#menut.closeLevel()



	try:
	    props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID,definitions.YEAR_OPENED]
	    print "?#?#? showmuseumtypes.py at line: 582 Dbg-out variable \props [",props,"]\n";
 	    results=apputils.getMarkerData(props)
	except Exception, e:
	    print str(e)
	    return render_template('message.html', title="Internal application error",message="Internal Application Error Q detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")


	total_list,subtree=self.delegate_foundationyearOLD(definitions.YEAR_OPENED,
							   results,
							   "Year_opened",0,1)
 	menut.addNodeAndLevel ("Year opened"+" ["+str(len(total_list))+"]",False,False)
 	menut.addSubTree(subtree,1)
	self.addListToDict(total_list,menut)


	try:
	    props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID,definitions.YEAR_CLOSED]
	    print "?#?#? showmuseumtypes.py at line: 599 Dbg-out variable \props [",props,"]\n";
 	    results=apputils.getMarkerData(props)
	except Exception, e:
	    print str(e)
	    return render_template('message.html', title="Internal application error",message="Internal Application Error R detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

	total_list,subtree=self.delegate_foundationyearOLD(definitions.YEAR_CLOSED,
							   results,
							   "Year_closed",0,1)
 	menut.addNodeAndLevel ("Year closed"+" ["+str(len(total_list))+"]",False,False)
 	menut.addSubTree(subtree,1)
	self.addListToDict(total_list,menut)


	#### Handling of generic properties 2
	DEFAULT_BROWSE_COLUMNS2 = apputils.readList(definitions.BASEDIR + 'DEFAULT_BROWSE_COLUMNS2.txt')

	for col in DEFAULT_BROWSE_COLUMNS2:
		defcol = definitions.DEFNAME + col
		itype = None
		if (defcol in definitions.DATATYPEDICT):
			itype = definitions.DATATYPEDICT[defcol]
		elif (col in definitions.DATATYPEDICT):
			itype = definitions.DATATYPEDICT[col]
		else:
			print "WARNING **** No handler for :" + col

		if (itype == definitions.DEFINED_LISTTYPE):
			print("lol")
			print (col)
			print("itype")
			print(itype)
			try:
				props = [definitions.NAME_OF_MUSEUM, definitions.SUBJECT_MATTER, definitions.PROJECT_ID, col]
				results = apputils.getMarkerData(props)
			except Exception, e:
				print str(e)
				return render_template('message.html', title="Internal application error",
									   message="Internal Application Error S detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

			subtree, total_list = self.delegate_genericproperty(results, col)
			print("total list")
			##print(total_list)
			menut.addNodeAndLevel(col.replace('_', ' ') + " [" + str(len(total_list)) + "]", False, False)
			if(col!="Geodemographic_group" and col!="Geodemographic_subgroup"):
				subtree.closeLevel()
				menut.addSubTree(subtree, 1)
				menut.closeLevel()
			self.addListToDict(total_list, menut)
			if (col == "Geodemographic_group" or col == "Geodemographic_subgroup"):
				subtree.closeLevel()
				menut.addSubTree(subtree, 1)
				menut.closeLevel()
			total_list = None

		elif (itype == definitions.DEFINED_HIERTYPE):
			print("lol")
			print (col)
			print("elifitype")
			print(itype)
			try:
				if (col == definitions.SUBJECT_MATTER):
					props = [definitions.NAME_OF_MUSEUM, definitions.SUBJECT_MATTER, definitions.PROJECT_ID]
				else:
					props = [definitions.NAME_OF_MUSEUM, definitions.SUBJECT_MATTER, definitions.PROJECT_ID, col]
				results = apputils.getMarkerData(props)
			except Exception, e:
				print str(e)
				return render_template('message.html', title="Internal application error",
									   message="Internal Application Error T detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

			b = definitions.HASNAME + col

			subprops = listman.getList("defClass" + b.replace(definitions.HASNAME, '') + definitions.LISTNAME)

			options = apputils.getOptionsDict(col, definitions.MAINSHEET)
			if ("sortoption" in options):
				method = options["sortoption"]
				print("method")
				##print(method)
				if (callable(getattr(ShowMuseumTypes.customsort, method))):
					func = getattr(ShowMuseumTypes.customsort, method)
					sortedsubprops = func(subprops)
				else:
					sortedsubprops = sorted(subprops)
			else:
				sortedsubprops = sorted(subprops)

			if (len(sortedsubprops) > 0):
				modelmap, totallist = self.getHierMapAndTotals(results, col)
				menut.addNodeAndLevel('{} [{}]'.format(b.replace('_', ' ').replace(definitions.HASNAME, ''),
													   str(len(totallist))
													   ), False, False)
				self.addListToDict(totallist, menut)

				ptree = self.getPtree(sortedsubprops, modelmap)
				subtree = None
				level = 1

				subtree = self.getHTMLTree(ptree, subtree, col, 'ShowMuseums', "")

				menut.addSubTree(subtree, 1)

				total_list = None

		elif (itype == 'xsd:positiveInteger'):

			print("itype == 'xsd:positiveInteger'")
			try:
				props = [definitions.NAME_OF_MUSEUM, definitions.PROJECT_ID, col]
				print "?#?#? showmuseumtypes.py at line: 498 Dbg-out variable \props [", props, "]\n";
				results = apputils.getMarkerData(props)
			except Exception, e:
				print str(e)
				return render_template('message.html', title="Internal application error",
									   message="Internal Application Error U detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

			subtree, total_list = self.delegate_genericproperty(results, col)
			menut.addNodeAndLevel(col.replace('_', ' ') + " [" + str(len(total_list)) + "]", False, False)
			self.addListToDict(total_list, menut)
			subtree.closeLevel()
			menut.addSubTree(subtree, 1)
			menut.closeLevel()

			total_list = None

		else:
			print "WARNING **** No handler for :" + col + " type:" + itype

	#### END Handling of generic properties 2  
 	##statusch=definitions.STATUSCHANGE
 	##try:
	    ##props=[definitions.NAME_OF_MUSEUM,definitions.PROJECT_ID,statusch]
	    ##print "?#?#? showmuseumtypes.py at line: 616 Dbg-out variable \props [",props,"]\n";
 	    ##results=apputils.getMarkerData(props)
	    ##print "LEN RES "+str(len(results))

 	##except Exception, e:
 	    ##print str(e)
 	    ##return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 525   \n <br/><p><pre>"+str(e)+"</pre></p>")

	##total_list,subtree=self.delegate_foundationyearOLD(definitions.STATUSCHANGE,
							   ##results,
							   ##definitions.STATUSCHANGE,2,3)

 	##menut.addNodeAndLevel (definitions.STATUSCHANGE.replace('_',' ')+" ["+str(len(total_list))+"]",False,False)
 	##menut.addSubTree(subtree,1)
	##self.addListToDict(total_list,menut)


       





	menut.closeTree()
	menut.defineDict()

	
        ShowMuseumTypes.menutree      = menut.getTree()
	
	self.pickleDict(self.ptrsdict,"ptrsdict")
	self.pickleDict(self.treedict,"treedict")
        menut.pickleTree("menut")

	return ShowMuseumTypes.menutree

    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Purpose:Chooses the initialisation type
    def getConfiguration_work(self):

	if (app.config['DEV_MODE'] == 'F'):
	    return self.SLOWconfig()
	else:
	    return self.FASTconfig()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Purpose:Creates the location menu for england
    def getEnglandTree(self):

	# INIT
	treedict={}

	# Create england dict
	treedict['England']={}

	# Regions (GORS)
	sgor=sorted(apputils.GOR_TRANSLATION_TABLE.items(), key=lambda x: x[1])
	# After this the dict becomes a list.....
	# Remove pseudo from a reversed list
	for trange in reversed(xrange(len(sgor))):
	    tup=(sgor[trange])
	    if (tup[0].find("99999999") > -1):
		del sgor[trange]
	regionsdict={}
	for tup in sgor:
	    regionsdict[tup[1]]=[]
	# Counties
	county_and_region_table={}
	for key, val in apputils.COUNTY_TRANSLATION_TABLE.iteritems():
	    county_and_region_table[key]=val
	for key, val in apputils.CA_CODE_TO_NAME_TABLE.iteritems():
	    county_and_region_table[key]=val

	scounties=sorted(county_and_region_table.items(), key=lambda x: x[1])
	# After this the dict becomes a list.....
	# Remove pseudo from a reversed list
	for trange in reversed(xrange(len(scounties))):
	    tup=(scounties[trange])
	    if (tup[0].find("99999999") > -1):
		del scounties[trange]
	countiesdict={}
	for tup in scounties:
	    countiesdict[tup[1]]=[]

	# Put counties in regions
	for counties in countiesdict:
	    if (counties in definitions.COUNTY2_REGION_DICT):
		thisregion=definitions.COUNTY2_REGION_DICT[counties]
		if (thisregion in regionsdict):
		    regionsdict[thisregion].append(counties)
		else:
		    print "Not in regiondic 1"+counties
	    else:
		print "Not in regiondic 2"+counties

	# Put CA in regions

	for ca_code,ca_name in apputils.CA_CODE_TO_NAME_TABLE.iteritems():
	    if (ca_code in apputils.CA_CODE_TO_GOR_TABLE):
		thisregioncode=apputils.CA_CODE_TO_GOR_TABLE[ca_code]
		thisregion=apputils.GOR_TRANSLATION_TABLE[thisregioncode]
		if (thisregion in regionsdict):
		    regionsdict[thisregion].append(ca_name)
		else:
		    print "Not in regiondic 1"+ca_name
	    else:
		print "Not in regiondic 2"+ca_name


	# Put LA in regions where 99999
	for laname, countyname in definitions.LA2_COUNTY_DICT.iteritems():
	    if (countyname == "(pseudo) England (UA/MD/LB"):
		if (laname in apputils.LA_TO_CA_NAMES_TABLE):
		    countyname=apputils.LA_TO_CA_NAMES_TABLE[laname]
		    countiesdict[countyname].append(laname)
		else:
		    thisregion=definitions.LA2_REGION_DICT[laname]
		    regionsdict[thisregion].append(laname)
	    elif (countyname.find("pseudo") < 0):
		countiesdict[countyname].append(laname)

	# Put LA in regions from LATOCA dict
	for laname, countyname in apputils.LA_TO_CA_NAMES_TABLE.iteritems():
	    lalist=countiesdict[countyname]
	    if (not laname in lalist):
		countiesdict[countyname].append(laname)

	# Get the data 

	    props=[definitions.NAME_OF_MUSEUM,definitions.SUBJECT_MATTER,definitions.PROJECT_ID,definitions.POSTCODE]
 	    results=apputils.getMarkerData(props)
	try:
	    results=apputils.getMarkerData(props)
	except         Exception, e:
	    print str(e)
	    return "*** ERROR IN GETAREATREE:"+str(e)
	
	# Sort the data into the dictionaries
        rlen=len(results["results"]["bindings"])
        museumdict={}
        notinlacount=0
        #print str(results["results"]["bindings"])
        for result in results["results"]["bindings"]:
            if ("museum" in result):
        	museum=result["museum"]["value"]
        	if (definitions.NAME_OF_MUSEUM in result):
        	    name=result[definitions.NAME_OF_MUSEUM]["value"]
		    lat=result[definitions.LATITUDE]["value"]
		    lon=result[definitions.LONGITUDE]["value"]
		    if (definitions.SUBJECT_MATTER in result):
			sub=result[definitions.SUBJECT_MATTER]["value"]
		    else:
			sub="Unknown"
	    

        	    if (definitions.POSTCODE in result):
        		postcode=result[definitions.POSTCODE]["value"].replace(' ','')
        		
        		if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
        		    thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
        		    if (thiscountry == 'England'):
				tup=(museum,name,sub,lat,lon)
        			if (not thiscountry in museumdict):
        			    museumdict[thiscountry]=[]
        			museumdict[thiscountry].append(tup)
        			if (postcode in definitions.POSTCODE2_REGION_DICT):
        			    thisregion=definitions.POSTCODE2_REGION_DICT[postcode]
        			    key=thiscountry+"/"+thisregion
        			    if (not key in museumdict):
        				museumdict[key]=[]
        			    museumdict[key].append(tup)
        			else:
        			    print "NOT IN POSTCODE2_REGION_DICT"+postcode
        
				# CA required
				if (postcode in definitions.POSTCODE2_LA_DICT):
				    thisla=definitions.POSTCODE2_LA_DICT[postcode]
				else:
				    thisla=""
			        #- - 			    

				if (thisla in apputils.LA_TO_CA_NAMES_TABLE):
				    thiscounty=apputils.LA_TO_CA_NAMES_TABLE[thisla]
				    key=thiscountry+"/"+thisregion+"/"+thiscounty
        			elif (postcode in definitions.POSTCODE2_COUNTY_DICT):
        			    thiscounty=definitions.POSTCODE2_COUNTY_DICT[postcode]
        			    if (thiscounty.find("pseudo") > 0):
        				key=thiscountry+"/"+thisregion
        			    else:
        				key=thiscountry+"/"+thisregion+"/"+thiscounty
        				
        			    if (not key in museumdict):
        				museumdict[key]=[]
        			    # Check if we already appended this as a region
        			    if (thiscounty.find("pseudo") < 0):
        				museumdict[key].append(tup)
        			else:
        			    print "NOT IN POSTCODE2_COUNTY_DICT"+postcode
        			
        			if (postcode in definitions.POSTCODE2_LA_DICT):
        			    thisla=definitions.POSTCODE2_LA_DICT[postcode]
        			    if (thiscounty.find("pseudo") > 0):
        				key=thiscountry+"/"+thisregion+"/"+thisla
        			    else:
        				key=thiscountry+"/"+thisregion+"/"+thiscounty+"/"+thisla
        				
        			    if (not key in museumdict):
        				museumdict[key]=[]
        			    museumdict[key].append(tup)

                                    ## CA
				    if (thisla in apputils.LA_TO_CA_NAMES_TABLE):
					thiscaname=apputils.LA_TO_CA_NAMES_TABLE[thisla]
				
					key=thiscountry+"/"+thisregion+"/"+thiscaname
					if (not key in museumdict):
					    museumdict[key]=[]
					museumdict[key].append(tup)
        			else:
        			    print "NOT IN POSTCODE2_LA_DICT "+postcode
        			# print postcode+" X_X_X "+thiscountry+"/"+thisregion+"/"+thiscounty+"/"+thisla
        			
        		else:
        		    print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
        		    if (postcode in definitions.POSTCODE2_DISTR_DICT):
        			print "But in region dict:"+definitions.POSTCODE2_DISTR_DICT[postcode]
        		    if (postcode in definitions.POSTCODE2_COUNTY_DICT):
        			print "But in county  dict:"+definitions.POSTCODE2_COUNTY_DICT[postcode]
        
        		    notinlacount+=1

        # Create the tree
	t = tree.Tree("Museums by England/localauth",True,False,"area")
	t.setNoLeafs(True)

	t.addNodeAndLevel('{} [{}] '.format('England',str(len(museumdict['England']))),
			  False,False)
	self.addListToDict(museumdict['England'],t)

	firsttime_region=True
        for reg in sorted(regionsdict):
	    if (firsttime_region):
		print("reg")
		print(reg)
		t.addNodeAndLevel('{} [{}] '.format(reg,str(len(museumdict['England'+"/"+reg]))),
				  False,False)
		firsttime_region=False
	    else:
		t.addNodeAtCurrentLevel('{} [{}] '.format(reg,str(len(museumdict['England'+"/"+reg]))),
					False,False)
	    self.addListToDict(museumdict['England'+"/"+reg],t)
            regiontotal=len(museumdict['England'+"/"+reg])
            total=0

	    firsttime_county=True
            for county in sorted(regionsdict[reg]):
        	key='England'+"/"+reg+"/"+county
        	if (key in museumdict):
		    #self.addListToDict(museumdict[key],t)
        	    if (county in countiesdict):
			if (firsttime_county):
			    t.addNodeAndLevel('{} [{}] '.format(county,str(len(museumdict[key]))),False,False)
			    firsttime_county=False
			else:
			    t.addNodeAtCurrentLevel('{} [{}] '.format(county,str(len(museumdict[key]))),
						    False,False)
			self.addListToDict(museumdict[key],t)

			firsttime_la=True
        		for la in sorted(countiesdict[county]):
        		    key='England'+"/"+reg+"/"+county+"/"+la
        		    if (key in museumdict):
				if (firsttime_la):
				    t.addNodeAndLevel('{} [{}] '.format(la,str(len(museumdict[key]))),
						      False,False)
				    firsttime_la=False
				else:
				    t.addNodeAtCurrentLevel('{} [{}] '.format(la,str(len(museumdict[key]))),
							    False,False)

				self.addListToDict(museumdict[key],t)
        			total=total+len(museumdict[key])
			if (not firsttime_la):
			    t.closeLevel()
        	    else:
        		# We have a pseudo
        		if (key in museumdict):
			    if (firsttime_county):
				t.addNodeAndLevel('{} [{}] '.format(county,str(len(museumdict[key]))),False,False)
				firsttime_county=False
			    else:
				t.addNodeAtCurrentLevel('{} [{}] '.format(county,str(len(museumdict[key]))),False,False)

			    self.addListToDict(museumdict[key],t)
        		    total=total+len(museumdict[key])
        	else:
        	    print "    No museums for this key:"+key
		    if (firsttime_county):
			t.addNodeAndLevel('{} [{}] '.format(county,"0"),False,False)
			firsttime_county=False
		    else:
			t.addNodeAtCurrentLevel('{} [{}] '.format(county,"0"),
						    False,False)
        	    
	
	    if (not firsttime_county):
		t.closeLevel()


		    
	t.closeLevel()

		
	return (t,museumdict['England'])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Purpose:Creates the location menu for other places than england/ 
# Arguments:
# @param countryparam What place to build for
# @param pseudoparam ONS pseudo code for country
# @param menuextension unique name of menu

    def getGenericLocationTree(self,countryparam,pseudoparam,menuextension):

	treedict={}
	
	# Create england dict
	treedict[countryparam]={}
	
	# Counties
	pseudo=pseudoparam
	countiesdict={}
	countiesdict[pseudo]=[]
	
	
	# Put counties in regions
	for county in countiesdict:
	    ladict={}
	    for lakey, laval in definitions.LA2_COUNTY_DICT.iteritems():
		if (laval == county):
		    ladict[lakey]=laval
	sla=sorted(ladict)
	for las in sla:
	    countiesdict[pseudo].append(las)
	    
	
	# Get all postcodes
	props=[definitions.NAME_OF_MUSEUM,
	       definitions.SUBJECT_MATTER,
	       definitions.PROJECT_ID,
	       definitions.POSTCODE]
	try:
	    results=apputils.getMarkerData(props)
	except         Exception, e:
	    print str(e)
	    return "*** ERROR IN GETAREATREE:"+str(e)
	
	rlen=len(results["results"]["bindings"])
	museumdict={}
	notinlacount=0
	
	for result in results["results"]["bindings"]:
	    if ("museum" in result):
		museum=result["museum"]["value"]
		if (definitions.NAME_OF_MUSEUM in result):
		    name=result[definitions.NAME_OF_MUSEUM]["value"]
		    lat=result[definitions.LATITUDE]["value"]
		    lon=result[definitions.LONGITUDE]["value"]
		    if (definitions.SUBJECT_MATTER in result):
			sub=result[definitions.SUBJECT_MATTER]["value"]
		    else:
			sub="Unknown"
	    
		    if (definitions.POSTCODE in result):
			postcode=result[definitions.POSTCODE]["value"].replace(' ','')
			
			if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
			    thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
			    if (thiscountry == countryparam):
				tup=(museum,name,sub,lat,lon)
				if (not thiscountry in museumdict):
				    museumdict[thiscountry]=[]
				museumdict[thiscountry].append(tup)
	
				if (postcode in definitions.POSTCODE2_LA_DICT):
				    thisla=definitions.POSTCODE2_LA_DICT[postcode]
				    key=thiscountry+"/"+pseudo+"/"+thisla
					
				    if (not key in museumdict):
					museumdict[key]=[]
				    museumdict[key].append(tup)
				else:
				    print "NOT IN POSTCODE2_LA_DICT "+postcode
#				print postcode+" X_X_X "+thiscountry+"/"+pseudo+"/"+thisla
				
			else:
			    print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
			    if (postcode in definitions.POSTCODE2_DISTR_DICT):
				print "But in region dict:"+definitions.POSTCODE2_DISTR_DICT[postcode]
			    if (postcode in definitions.POSTCODE2_COUNTY_DICT):
				print "But in county  dict:"+definitions.POSTCODE2_COUNTY_DICT[postcode]
	
			    notinlacount+=1


	# Create the tree
	t = tree.Tree("Museums by "+countryparam+" pseudo",True,False,menuextension+"area")
 	t.setNoLeafs(True)
 	t.addNodeAndLevel('{} [{}] '.format(countryparam,str(len(museumdict[countryparam]))),
 			  False,False)
 	self.addListToDict(museumdict[countryparam],t)
	

	firsttime_la=True
	for la in sorted(countiesdict[county]):
	    key=countryparam+"/"+pseudo+"/"+la
	    if (key in museumdict):
		if (firsttime_la):
		    t.addNodeAndLevel('{} [{}] '.format(la,str(len(museumdict[key]))),
				      False,False)
		    firsttime_la=False
		else:
		    t.addNodeAtCurrentLevel('{} [{}] '.format(la,str(len(museumdict[key]))),
					    False,False)
		self.addListToDict(museumdict[key],t)
	    else:
		print countryparam+":No museums for this key:"+key
		if (firsttime_la):
		    t.addNodeAndLevel('{} [{}] '.format(la,"0"),False,False)
		    firsttime_la=False
		else:
		    t.addNodeAtCurrentLevel('{} [{}] '.format(la,"0"),
					    False,False)
        	    
		    
 	if (not firsttime_la):
	    t.closeLevel()
		
	return (t,museumdict[countryparam])


#-  -  -  -  -  -  -  

## Purpose:Generates an interval i.e. number of musuems from 1990 to 2000
#          and creates the menu for the interval. Used with open and close years
# Arguments:
# @param listofitems list of museums
# @param tree Tree to work with
# @param displayinterval bucket length, as in number of years
# @param nodename name of node
# @param open menu open by default?
# @param disabled menu disabled by default?

    def generateinterval(self,listofitems,tree,displayinterval,nodename,open,disabled):

        count=0
        macid=0
        macrolist=[]
        countlist=[]
        firsttime=True
        macroid=""
        macrocount=0
        tree.addNodeAtCurrentLevel(nodename,True,False)
        sortedtuples=sorted(listofitems,key=lambda tup: tup[0])
	prevhundreds=[]
	for d in displayinterval:
	    prevhundreds.append(0)
	    
        for atuple in sortedtuples:
            iyear=int(atuple[0])
            item=atuple[1]
	    dcount=0
	    for d in displayinterval:
		hundreds=int(iyear/displayinterval[dcount])*displayinterval[dcount]
		if (hundreds != prevhundreds[dcount]):
		    if (firsttime):
			macroid="{"+nodename+str(macrocount)+"}"
			tree.addNodeAndLevel(str(hundreds)+"--("+macroid+")",False,False)
			firsttime=False
		    else:
			macroid="{"+nodename+str(macrocount)+"}"
			tree.addNodeAtCurrentLevel(str(hundreds)+"--("+macroid+")",False,False)
		    macrolist.append(macroid)
		    countlist.append(count)
		    macrocount+=1
		    prevhundreds[dcount]=hundreds
		    dcount+=1
		    count=0
		tree.addLeaf(item)
		count+=1

        
        treetext=tree.getTree()

        countlist=apputils.rotate(countlist,1)
        cl=len(countlist)-1
        last=countlist[cl]
        last=last+1
        countlist[cl]=last

        j=0
        while j < len(treetext):
            k=0
            while k < len(macrolist):
                treetext[j]=treetext[j].replace(macrolist[k],str(countlist[k]))
                k+= 1
            j += 1
        return
            

## Purpose:Creates a menu with still open,before 1960s and after 1960s museums.
# Arguments:
# @param property column open/close
# @param results  resultset to analyse

    def delegate_foundationyear(self,property,results):

        t = tree.Tree("Museums by "+property.replace("_"," "),False,False)
        nineninelist= []
        pre1960list = []
        sixtieslist = [] 


        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            parts=uri.split('/')
            partlen=len(parts)-1
            interval=res[property]["value"]
	    parts=interval.split(definitions.RANGE_SEPARATOR)
	    year=parts[0]

            name=res[definitions.NAME_OF_MUSEUM]["value"].encode('utf-8')
	    lat=res[definitions.LATITUDE]["value"]
	    lon=res[definitions.LONGITUDE]["value"]
	    if (definitions.SUBJECT_MATTER in res):
		sub=res[definitions.SUBJECT_MATTER]["value"]
	    else:
		sub="Unknown"

            try:
                iyear=int(year)
                shortname=parts[partslen]
		mtuple=(year,shortname,name,sub,lat,lon)
                if (iyear == 9999):
                    nineninelist.append(item)
                elif(iyear < 1960):
                    pre1960list.append((year,item))
                else:
                    sixtieslist.append((year,item))
            

            except Exception, e:
		print str(e)

            
        t.addNodeAndLevel("Still open",False,False)
        for item in nineninelist:
            t.addLeaf(item)

        self.generateinterval(pre1960list,t,[10],"pre-1960",False,False)
        t.closeLevel()
	t.closeLevel()

	buckets=[10,1]

	sortedtuples=sorted(sixtieslist,key=lambda tup: tup[0])
	newlist=t.generateLists(sortedtuples,buckets)
	t=t.createtreefromlist(newlist,t,"post-1960",buckets,0,True)
	t.closeLevel()

        #self.generateinterval(sixtieslist,t,[10,1],"post-1960",False,False)
        t.closeLevel()
                
                        

        t.closeTree()
        treetext=t.getTree()

        return treetext
    
#-  -  -  -  -  -  -  
## Purpose:Generates an interval i.e. number of musuems from 1990 to 2000
#          and creates the menu for the interval. Used with open and close years
# Arguments:
# @param listofitems list of museums
# @param tree Tree to work with
# @param displayinterval bucket length, as in number of years
# @param nodename name of node
# @param open menu open by default?
# @param disabled menu disabled by default?
    def generateintervalOLD(self,listofitems,tree,displayinterval,nodename,open,disabled,isunknown):

#	mtuple=(year,uri,name)

        count=0
        firsttime=True
	if(isunknown == False):
	    tree.addNodeAndLevel(nodename,open,disabled)
	else:
	    tree.addNodeAtCurrentLevel(nodename,open,disabled)
	    
	rootid=tree.getId()
        sortedtuples=sorted(listofitems,key=lambda tup: tup[0])
	prevhundreds=[]
	for d in displayinterval:
	    prevhundreds.append(0)
	    
	displaydict={}
        for atuple in sortedtuples:
            iyear=int(atuple[0])
            uri=atuple[1]
	    name=atuple[2]
	    dcount=0
	    for d in displayinterval:
		hundreds=int(iyear/displayinterval[dcount])*displayinterval[dcount]
		if (hundreds != prevhundreds[dcount]):
		    prevhundreds[dcount]=hundreds
		    dcount+=1
		    count=0
		if (not hundreds in displaydict):
		    displaydict[hundreds]=[]
		displaydict[hundreds].append((uri,name,atuple[3],atuple[4],atuple[5]))

	sortedinterval=sorted(displaydict.items())
	total_list=[]
	for ival in sortedinterval:
	    ind,alist=ival
	    if (firsttime):
		tree.addNodeAndLevel(str(ind)+" ["+str(len(alist))+"]",False,False) 
		firsttime=False
	    else:
		tree.addNodeAtCurrentLevel(str(ind)+" ["+str(len(alist))+"]",False,False)
	    self.addListToDict(alist,tree)
	    total_list=total_list+alist
        
        return total_list,rootid
            
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Creates the HTML menu from the list without leaves appearing.
# Arguments:
# @param self,list,tree,nodename,bucket,ptr,open,tlist)
    def createtreefromlistnoleaves(self,list,tree,nodename,bucket,ptr,open,tlist):
        tree.addNodeAndLevel(nodename,open,False)
	nodeid=tree.getId()
	nodelist=[]
	lb1=[]
        for item in list:
            if (str(type(item)) == "<type 'list'>" ) :
                ptr+=1
		tot=0
		for subitem in item:
		    tot=tot+len(subitem)
		    if (len(subitem) == 6):
			tyear,turi,tname,sub,lat,lon=(subitem)
			lb1.append((turi,tname,sub,lat,lon))

		if (ptr < len(bucket)):
		    atuple=item[0][0]
		    syear=str(atuple[0])
		    year=int(syear)
		    label=int(year/bucket[ptr-1])*bucket[ptr-1]
		    label=str(label)+" ["+str(tot)+"]"
		    open=True
		else:
		    label=str(item[0][0])+" ["+str(len(item))+"]"
		    open=False
		alist,tree,rootid,tlist=self.createtreefromlistnoleaves(item,tree,
								  label,
								  bucket,ptr,open,tlist)
                ptr-=1
                tree.closeLevel()
            else:
		tyear,turi,tname,sub,lat,lon=item
		nodelist.append((turi,tname,sub,lat,lon))
		
	
	if (len(nodelist) > 0):
	    self.addListToDict(nodelist,tree)
	    tlist=tlist+nodelist
	    return nodelist,tree,nodeid,tlist
	else:
	    self.addListToDict(lb1,tree)
	    return lb1,tree,nodeid,tlist
	
	
    
#-  -  -  -  -  -  -  

## Purpose:Removes type info from name
# Arguments:
# @param name
# @param self,property,results,menuname,partspointerstart,partspointerend)
    def delegate_foundationyearOLD(self,property,results,menuname,partspointerstart,partspointerend):

	cleanprop=property.replace("_"," ")
        t = tree.Tree("Museums by "+cleanprop,True,False,menuname)
	t.setNoLeafs(True)

        nineninelist= []
        pre1960list = []
        sixtieslist = [] 
	total_list=[]
	
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
	    if (property in res):
		#year=res[property]["value"].replace(".0","")
		interval=res[property]["value"]
		parts=interval.split(definitions.RANGE_SEPARATOR)

		name=res[definitions.NAME_OF_MUSEUM]["value"].encode('utf-8')
		lat=res[definitions.LATITUDE]["value"]
		lon=res[definitions.LONGITUDE]["value"]
		if (definitions.SUBJECT_MATTER in res):
		    sub=res[definitions.SUBJECT_MATTER]["value"]
		else:
		    sub="Unknown"
	    
		try:
		    syear=parts[partspointerstart]
		    eyear=parts[partspointerend]
		    if (syear == "9999"):
			if (eyear == "9999"):
			    year=int(syear)
			else:
			    year=int(eyear)
		    else:
			if (eyear == "9999"):
			    year=int(syear)
			else:
			    year=(int(syear)+int(eyear))/2
			
		    mtuple=(year,uri,name,sub,lat,lon)
		    savetuple=(uri,name,sub,lat,lon)
		    if (year == 9999):
			nineninelist.append(savetuple)
		    elif(year < 1960):
			pre1960list.append(mtuple)
		    else:
			sixtieslist.append(mtuple)
            

		except Exception, e:
		    print str(e)
		    noop=0


	isunknown=True
	if (len(nineninelist) > 0):
	    t.addNodeAndLevel("Still open"+' ['+str(len(nineninelist))+']',False,False)
	    self.addListToDict(nineninelist,t)
	    total_list=total_list+nineninelist
	else:
	    isunknown=False


	    
	if (len(pre1960list) > 0):
	    templist,rootid=self.generateintervalOLD(pre1960list,t,[10],"pre-1960 ["+str(len(pre1960list))+"]",False,False,isunknown)
	    self.addListToDictWithId(templist,rootid)
	    total_list=total_list+templist
	    if (len(templist) > 0):
		t.closeLevel()
		t.closeLevel()
	    else:
		t.closeLevel()
	    
	    templist=None
	else:
	    t.closeLevel()
	

	buckets=[10,1]

	sortedtuples=sorted(sixtieslist,key=lambda tup: tup[0])
	newlist=t.generateLists(sortedtuples,buckets)
	post1960_tot=0
	for sublists in newlist:
            if (str(type(sublists)) == "<type 'list'>" ) :
		for subitem in sublists:
		    post1960_tot=post1960_tot+len(subitem)
	    else:
		post1960_tot=post1960_tot+len(sublists)

	tlist=[]

 	nodelist,t,rootid,tlist=self.createtreefromlistnoleaves(newlist,t,"post-1960 ["+str(len(sixtieslist))+"]",buckets,0,False,tlist)
	self.addListToDictWithId(tlist,rootid)

	total_list=total_list+tlist

	t.closeLevel()
        t.closeLevel()
        t.closeTree()

        return total_list,t
    
#-  -  -  -  -  -  -  


## Purpose:Removes type info from name
# Arguments:
# @param name
# @param self,property,results)
    def delegate_countyproperty(self,property,results):
        columns=""
        count=0
        treemap={}
        typemap={}
        treetext=[]
        countlist=[]
        t = tree.Tree("Museums by "+property.replace("_"," "),False,False)
        firsttime=True

        for res in results["results"]["bindings"]:
            mtype=res[property]["value"].encode('utf-8')
            uri=res["museum"]["value"].encode('utf-8')
            name=res["textcontent"]["value"].encode('utf-8')
            mtuple=(mtype,uri,name)
            if (not mtype in typemap):
                typemap[str(mtype)]=[]

            mtypelist=typemap[str(mtype)]
            mtypelist.append(mtuple)

        propkeys=typemap.keys()
        typeptr=0
        uriptr=1
        nameptr=2
        countfacets=0
        count=0
        previousletter=''
        firsttimealpha=True
        
        for akey in sorted(typemap):
            firstletter=akey[0]
            if (firstletter != previousletter):
                if (firsttimealpha):
                    t.addNodeAndLevel(firstletter,False,False)
                    firsttimealpha=False
                else:
                    t.closeLevel()
                    t.addNodeAtCurrentLevel(firstletter,False,False)
                    firsttime=True
                    
                previousletter=firstletter
                
            listoftuples=typemap[akey]
            if (firsttime):
                t.addNodeAndLevel(akey+'--({})',False,False)
                firsttime=False
            else:
                t.addNodeAtCurrentLevel(akey+'--({})',False,False)
                
            sortedtuples=sorted(listoftuples,key=lambda tup: tup[2])
            countfacets+=1
            for atuple in sortedtuples :
                parts=atuple[uriptr].split('/')
                partlen=len(parts)-1
                tname=str(atuple[nameptr])
                shortname=self.getShortName(tname)
                t.addLeaf('<a href="{}" target="restable">{}</a>'.format(atuple[uriptr].replace(definitions.RDFDATAURI,
                                                                                      app.config['URLREWRITEPATTERN']).replace("/id/","/nid/"),
                                                               '<strong>+</strong> '+shortname))

                count+=1

            countlist.append(count)
            count=0
                
        t.closeLevel()
        t.closeTree()
        treetext=t.getTree()

        j=0
        k=0
        while j < len(treetext):
            if (treetext[j].find("--")>0):
                treetext[j]=treetext[j].format(countlist[k])
                k+=1
            treetext[j]=treetext[j].encode('utf-8')
            j += 1
            
        
        return treetext;


    
            
        
#-  -  -  -  -  -  -  
## Purpose:Removes type info from name
# Arguments:
# @param name
# @param self,sortedtuples,inkey,treeref)
    def doTuples(self,sortedtuples,inkey,treeref):
	museumdict={}
	museumdict[inkey]=[]
	count=0
        subt = tree.Tree(None,True,False,treeref)
	subt.setNoLeafs(True)
        typeptr=0
        uriptr=1
        nameptr=2
	subptr=3
	latptr=4
	lonptr=5
	for atuple in sortedtuples :
	    parts=atuple[uriptr].split('/')
	    partlen=len(parts)-1
	    tname=str(atuple[nameptr])
	    tup=(atuple[uriptr].replace(definitions.RDFDEFURI,
					app.config['URLREWRITEPATTERN']).replace("/id/","/nid/"),
		 tname,
		 atuple[subptr],
		 atuple[latptr],
		 atuple[lonptr])
	    museumdict[inkey].append(tup)
	    count+=1

    
	subt.closeLevel()
	return (count,subt,museumdict)

## Purpose:Removes type info from name
# Arguments:
# @param name
# @param self,results,property)
    def delegate_genericproperty(self,results,property):
        columns=""
        count=0
        typemap={}
	totallist=[]
	
	cleanprop=property.replace("_"," ")
        t = tree.Tree("Museums by "+cleanprop,True,False,property)
	t.setNoLeafs(True)

        for res in results["results"]["bindings"]:
	    if (property in res):
		mtype=res[property]["value"].encode('utf-8')
		uri=res["museum"]["value"].encode('utf-8')
		name=res[definitions.NAME_OF_MUSEUM]["value"].encode('utf-8')
		lat=res[definitions.LATITUDE]["value"]
		lon=res[definitions.LONGITUDE]["value"]
		if (definitions.SUBJECT_MATTER in res):
		    sub=res[definitions.SUBJECT_MATTER]["value"]
		else:
		    sub="Unknown"

		mtuple=(mtype,uri,name,sub,lat,lon)
		if (not mtype in typemap):
		    typemap[str(mtype)]=[]

		mtypelist=typemap[str(mtype)]
		mtypelist.append(mtuple)

        propkeys=typemap.keys()
        typeptr=0
        uriptr=1
        nameptr=2
	subptr=3
	latptr=4
	lonptr=5
        countfacets=0
        count=0
	first=True
        for akey in sorted(typemap):
            listoftuples=typemap[akey]
            sortedtuples=sorted(listoftuples,key=lambda tup: tup[2])
	    (scount,subt,museumdict)=self.doTuples(sortedtuples,akey,cleanprop)
	    if (first):
		t.addNodeAndLevel(self.modeltoview.getView(property,akey)+' ['+str(scount)+']',False,False)
		first=False
	    else:
		t.addNodeAtCurrentLevel(self.modeltoview.getView(property,akey)+' ['+str(scount)+']',False,False)
	    self.addListToDict(museumdict[akey],t)
	    totallist=totallist+museumdict[akey]
	    museumdict={}

	    t.addSubTree(subt,1)
            countfacets+=1



        return (t,totallist);

#-  -  -  -  -  -  -  


## Purpose:Removes type info from name
# Arguments:
# @param name
# @param self,property,results)
    def delegate_postcodeproperty(self,property,results):
        columns=""
        count=0
        treemap={}
        typemap={}
        countlist=[]

        t = tree.Tree("Museums by "+property.replace("_"," "),False,False)


        for res in results["results"]["bindings"]:
            mtype=res[property]["value"].encode('utf-8')
            uri=res["museum"]["value"].encode('utf-8')
            name=res["textcontent"]["value"].encode('utf-8')
            mtuple=(mtype,uri,name)
            if (not mtype in typemap):
                typemap[str(mtype)]=[]

            mtypelist=typemap[str(mtype)]
            mtypelist.append(mtuple)

        propkeys=typemap.keys()
        typeptr=0
        uriptr=1
        nameptr=2
        countfacets=0
        count=0
        level=0
        roottime=True
        firsttime=[True for col in range(4)]
        letter=["" for col in range(4)]
        lettercount=[0 for col in range(4)]
        lastlevel=0
        
        for akey in sorted(typemap):
            listoftuples=typemap[akey]
            cumulativekey=""
            level=0
            maxlc=3
            endlc=maxlc-1
            
            for lc in  range(maxlc):
                if (letter[lc] != akey[lc:lc+1]):
                    letter[lc]=akey[lc:lc+1]
                    # Close
                    if (roottime):
                        noop=1
                    elif(lastlevel >= lc) :
                        while (lastlevel > lc):
                            t.closeLevel()
                            lastlevel=lastlevel-1
                    # Open
                    if (roottime):
                        roottime=False
                        t.addNodeAndLevel(akey[0:lc+1]+"["+str(lc)+"]",False,False)
                    elif (firsttime[lc]):
                        firsttime[lc]=False
                        t.addNodeAndLevel(akey[0:lc+1]+"["+str(lc)+"]",False,False)
                        lastlevel=lc
                    elif (lc == endlc):
                        lastlevel=lc
                        t.addNodeAtCurrentLevel(akey[0:lc+1]+"["+str(lc)+"]",False,False)
                    else :
                        lastlevel=lc
                        t.addNodeAndLevel(akey[0:lc+1]+"["+str(lc)+"]",False,False)
                    lettercount[lc]+=1
                    level+=1
                    


            sortedtuples=sorted(listoftuples,key=lambda tup: tup[2])
            countfacets+=1
            for atuple in sortedtuples :
                parts=atuple[uriptr].split('/')
                partlen=len(parts)-1
                tname=str(atuple[nameptr])
                shortname=self.getShortName(tname) 

                t.addLeaf('<a href="{}" target="restable">{}</a>'.format(atuple[uriptr].replace(definitions.RDFDATAURI,
                                                                                                              app.config['URLREWRITEPATTERN']).replace("/id/","/nid/"),
                                                                                       '<strong>+</strong> '+shortname))

                count+=1
            countlist.append(count)
            count=0
                
        t.closeTree()
        treetext=t.getTree()

        j=0
        k=0
        while j < len(treetext):
            if (treetext[j].find("--")>0):
                treetext[j]=treetext[j].format(countlist[k])
                k+=1
            treetext[j]=treetext[j].encode('utf-8')
            j += 1


        return treetext

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def showmuseumtypesView(self,propertytodisplay):

	if (ShowMuseumTypes.menutree is None):
	    ShowMuseumTypes.menutree = self.getConfiguration_work()
            mapindex=0
            ShowMuseumTypes.mapdata.append("var museums=[")
            idtoindexmap={}
            
            ShowMuseumTypes.dictdata.append("museumdict={")
            counterdebug=0
            for key, val in self.treedict.iteritems():
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
                    else:
                        sub=self.modeltoview.getView(definitions.SUBJECT_MATTER,sub)
    
                    if (href not in idtoindexmap):
                        idtoindexmap[href]=mapindex
                        thisindex=mapindex
                        mapindex+=1
                        ShowMuseumTypes.mapdata.append('["{}","{}","{}",{},{}],'.format(href,name.upper(),sub,lat,lon))
                    else:
                        thisindex=idtoindexmap[href]
                        
                    if (icount==vallen):
                        alist='[{},{}]'.format(count,thisindex)
                        #print "alist:"+alist
                        arrs=arrs+alist
                    else:
                        alist='[{},{}],'.format(count,thisindex)
                        arrs=arrs+alist
                        icount=icount+1

                counterdebug=counterdebug+1
                #if(counterdebug==114):
                #	print(counterdebug)
                #	print('"'+key+'":['+arrs+"],")
                ShowMuseumTypes.dictdata.append('"'+key+'":['+arrs+"],")
            ShowMuseumTypes.dictdata[-1]=ShowMuseumTypes.dictdata[-1].replace("]],","]]")
            ShowMuseumTypes.dictdata.append("};")
    
    
            ShowMuseumTypes.mapdata[-1]=ShowMuseumTypes.mapdata[-1].replace("],","]")
            ShowMuseumTypes.mapdata.append("];")
        


        if (request.method == 'GET' and propertytodisplay != None):
            
            columns=""
            count=0
            ordercolumn="?"+str(propertytodisplay)
            if ( propertytodisplay == self.fields[ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.YEAR_CLOSED]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+definitions.YEAR_CLOSED)
                except Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error U detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")

                treetext=self.delegate_foundationyear(definitions.YEAR_CLOSED,results)
            elif (propertytodisplay == self.fields[ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.YEAR_OPENED]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+definitions.YEAR_OPENED)
                except  Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error V detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
            
                treetext=self.delegate_foundationyear(definitions.YEAR_OPENED,results)
            elif (propertytodisplay == self.fields[ShowMuseumTypes.ptrsdict[definitions.HASNAME+definitions.COUNTY]]):

                try:
                    results=apputils.getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+propertytodisplay)
                except    Exception, e:
		    print str(e)
                    return render_template('message.html', title="Internal application error",message="Internal Application Error W detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
                
                treetext=self.delegate_countyproperty(definitions.COUNTY,results)
	                


            return render_template('browsemenu.html',
				   results=treetext,
				   trees=ShowMuseumTypes.getConfiguration(),
				   dicts=ShowMuseumTypes.dictdata,
				   mapdata=ShowMuseumTypes.mapdata,
				   property=propertytodisplay)
        else:
            
            ##print("listlength")
            ##print(ShowMuseumTypes.getConfiguration())
            return render_template('browseproperties.html',
				   trees=ShowMuseumTypes.getConfiguration(),
				   dicts=ShowMuseumTypes.dictdata,
				   mapdata=ShowMuseumTypes.mapdata,
				   results=None)



