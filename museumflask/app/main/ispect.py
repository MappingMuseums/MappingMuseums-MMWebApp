#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile

# Nick Larsson (NickTex)

License: GPL 2 (http://www.gnu.org/copyleft/gpl.html) or BSD


REMOVE VISITORS FROM SEARCH AND START DISCUSSION
MAKE OBJECTS FOR EACH DATATYPE LIKE HIER AND PUT IN INTERFACES
MAKE OBJECTS FOR some home made types to do view and query
Can this be automated?





"""
from SPARQLWrapper import SPARQLWrapper, JSON
import operator
import definitions 

import sys
import csv
import time
import re
import cgi
import pprint

from flask import current_app as app

class Ispect(object):
    
    _dict = {}
    _clazz=""
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def __init__(self,clazz):
	self._clazz=clazz
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getSubClasses(self,clazz):
	res=getSuperClasses(self,clazz)
	res.reverse()
	return res
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getSuperClasses(self,clazz):

	cr=clazz.replace("http://"+definitions.RDFDEFURI,"")
	if (cr.startswith("http://")):
	    cr="<"+cr+">"
	else:
	    cr=definitions.PREFIX_WITHCOLON+clazz.replace("http://"+definitions.RDFDEFURI,"")

	sparql  = SPARQLWrapper("http://193.61.44.11:8890/sparql")
	reslist = []
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	
	SELECT ?superclass 
	 FROM <http://bbk.ac.uk/MuseumMapProject/graph/v5>
	WHERE {

	"""+cr+""" rdfs:subClassOf|(owl:intersectionOf/rdf:rest*/rdf:first)* ?superclass .

	}
	"""
	sparql.setQuery(query)
	#    print "================================================"
	#print query
	#    print "================================================"
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	#print len(results["results"]["bindings"])
	if (len(results["results"]["bindings"]) < 1):
	    return reslist
	else:
	    for result in results["results"]["bindings"]:
		item=result["superclass"]["value"]
		subsub=self.hasSuperClass(item)
#		print "?#?#? ispect.py at line: 80 Dbg-out variable \subsub [",item,"=="+str(subsub)+"]\n";
#		print "?#?#? ispect.py at line: 82 Dbg-out variable \subsub [",len(subsub),"]\n";
#		print "?#?#? ispect.py at line: 84 Dbg-out variable \reslist [",reslist,"]\n";
		
		if (len(subsub)> 0):
#		    print "?#?#? ispect.py at line: 85 Dbg-out variable \subsub [",len(subsub),"]\n";
		    if (subsub not in reslist):
#			print "?#?#? ispect.py at line: 87 Dbg-out variable \subsub [",subsub,"]\n";
#			print "?#?#? ispect.py at line: 87 Dbg-out variable \reslist [",reslist,"]\n";
			reslist.append(subsub[0])
		    
                else:
		    reslist.append(item)

#	del reslist[-1]
        reslist.reverse()
	return reslist

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def hasSuperClass(self,clazz):

	cr=clazz.replace("http://"+definitions.RDFDEFURI,"")
	if (cr.startswith("http://")):
	    cr="<"+cr+">"
	else:
	    cr=definitions.PREFIX_WITHCOLON+clazz.replace("http://"+definitions.RDFDEFURI,"")

	sparql  = SPARQLWrapper("http://193.61.44.11:8890/sparql")
	reslist = []
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	
	SELECT ?superclass 
	 FROM <http://bbk.ac.uk/MuseumMapProject/graph/v5>
	WHERE {

	"""+cr+""" rdfs:subClassOf|(owl:intersectionOf/rdf:rest*/rdf:first)* ?superclass .

	}
	"""
	sparql.setQuery(query)
	#    print "================================================"
	#print query
	#    print "================================================"
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	#print len(results["results"]["bindings"])
	if (len(results["results"]["bindings"]) < 1):
	    return reslist
	else:
	    for result in results["results"]["bindings"]:
		item=result["superclass"]["value"]
		reslist.append(item)
                
	del reslist[-1]
	return reslist

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def getInstanceOfClassFromProperty(self,clazz,parentinstance,property):

	reslist = []
	prefixes= definitions.RDF_PREFIX_PRELUDE+ """
	prefix bbkmm:        <http://bbk.ac.uk/MuseumMapProject/def/>"""
	cr=clazz.replace("http://"+definitions.RDFDEFURI,"")
	#print "?#?#? ispect.py at line: 157 Dbg-out variable \cr [",cr,"]\n";
	if (cr.startswith("http://")):
	    cr="<"+cr+">"
	else:
	    cr=definitions.PREFIX_WITHCOLON+clazz.replace("http://"+definitions.RDFDEFURI,"")
	shortprop=self.getPrefix(prefixes,self.firstPart(property))+self.lastPart(property)
	sparql  = SPARQLWrapper("http://193.61.44.11:8890/sparql")
	reslist = []
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	
        SELECT DISTINCT ?instance
                    WHERE {

		        ?instance a """+clazz+""" .
			<"""+str(parentinstance)+"""> """+shortprop+"""  ?instance
                            
		    }
                    ORDER BY ?instance
        
	"""
	sparql.setQuery(query)
	#    print "================================================"
	#print query
	#    print "================================================"
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	print len(results["results"]["bindings"])
	#print results["results"]["bindings"]
	if (len(results["results"]["bindings"]) < 1):
	    return reslist
	else:
	    for result in results["results"]["bindings"]:
		item=result["instance"]["value"]
		reslist.append(item)
                

	return reslist
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def getAllInstancesOfClass(self,clazz):

	reslist = []
	cr=clazz.replace("http://"+definitions.RDFDEFURI,"")
	#print "?#?#? ispect.py at line: 157 Dbg-out variable \cr [",cr,"]\n";
	if (cr.startswith("http://")):
	    cr="<"+cr+">"
	else:
	    cr=definitions.PREFIX_WITHCOLON+clazz.replace("http://"+definitions.RDFDEFURI,"")

	sparql  = SPARQLWrapper("http://193.61.44.11:8890/sparql")
	reslist = []
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	
        SELECT DISTINCT ?instance
                    WHERE {

		        ?instance a <"""+clazz+"""> 
                            
		    }
                    ORDER BY ?instance
        
	"""
	sparql.setQuery(query)
	#    print "================================================"
	#print query
	#    print "================================================"
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	print len(results["results"]["bindings"])
	#print results["results"]["bindings"]
	if (len(results["results"]["bindings"]) < 1):
	    return reslist
	else:
	    for result in results["results"]["bindings"]:
		item=result["instance"]["value"]
		reslist.append(item)
                

	return reslist
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def getProperties(self,clazz,instanceof=None):

	#print "?#?#? ispect.py at line: 195 Dbg-out variable \instanceof [",instanceof,"]\n";
	
	cr=clazz.replace("http://"+definitions.RDFDEFURI,"")
	#print "?#?#? ispect.py at line: 249 Dbg-out variable \cr [",cr,"]\n";
	if (cr.startswith("http://")):
	    cr="<"+cr+">"
	elif ( cr.find(":") > -1 and not cr.startswith( definitions.PREFIX_WITHCOLON) ):
	    noop=0
	else:
	    cr=definitions.PREFIX_WITHCOLON+clazz.replace("http://"+definitions.RDFDEFURI,"")


	sparql  = SPARQLWrapper("http://193.61.44.11:8890/sparql")
	resdict = {}
	if (instanceof !=None):
	    instancepart="<"+instanceof+"> ?property ?o ."
	else:
	    instancepart=""
	    
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	SELECT DISTINCT ?property, ?range
	FROM <http://bbk.ac.uk/MuseumMapProject/graph/v5>

	WHERE {
	values ?propertyType { owl:ObjectProperty }
	?s      ?property ?o .
	?property rdfs:domain """+cr+"""  .
	"""+instancepart+"""
	?property rdfs:range ?range
              }
	"""
	sparql.setQuery(query)
	#    print "================================================"
	#print query
	#    print "================================================"
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	#print len(results["results"]["bindings"])
	if (len(results["results"]["bindings"]) < 1):
	    return resdict
	else:
	    for result in results["results"]["bindings"]:
		p=result["property"]["value"]
		r=result["range"]["value"]
		ic=IS.isClazz(r)
		#print "?#?#? ispect.py at line: 184 Dbg-out variable \ic [",ic,"]\n";
		if (ic != None):
		    resdict[(ic,p)]=IS.getProperties(r,instanceof)
		else:
		    resdict[p]=r
                
	return resdict
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def getDescriptor(self,reverse=False):
	res=self.getSuperClasses(self._clazz)
	res.append(self._clazz)
	containerdict={}
	if (reverse):
	    res.reverse()
	for r in res:
	    pd=self.getProperties(r)
	    containerdict[r]=pd
	    
	return containerdict

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def isClazz(self,clazz):
	prefixes= definitions.RDF_PREFIX_PRELUDE+ """
	prefix bbkmm:        <http://bbk.ac.uk/MuseumMapProject/def/>"""

	if (clazz.startswith('http://www.w3.org/2001/XMLSchema#')):
	    return None
	else:
	    return self.getPrefix(prefixes,self.firstPart(clazz))+self.lastPart(clazz)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def prettyPrint(self,pdict,indent=2):
	blanks="                                                                                         "
	# iterating, always use iteritems !
	for key, val in pdict.iteritems():
	    if isinstance(val,dict):
		print blanks[0:indent]+"Property "+str(key[1])+" of type "+str(key[0])
		#val="+str(val) 
		self.prettyPrint(val,indent+2)
	    else:
		print blanks[0:indent]+"Property "+str(key) + "--> ofType:"+str(val)
	return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def lastPart(self,uri):
	parts=uri.split("/")
	last=parts[len(parts)-1]
	if (last.find("#") > -1):
	    lasthash=last.split("#")
	    return lasthash[len(lasthash)-1]
	else:
	    return last

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def firstPart(self,uri):
	
	parts=uri.split("/")
	last=parts[len(parts)-1]
	first=""
	pr=range(len(parts)-1)
	for p in pr:
	    first=first+parts[p]+"/"
	if (last.find("#") > -1):
	    lasthash=last.split("#")
	    return first+lasthash[0]+"#"
	else:
	    return first

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def getPrefix(self,listofprefixes,uri):
	parts=listofprefixes.split(">")
	prefixdict={}
	for p in parts:
	    p=p.strip()
	    line=p.split("<")
	    if (line[0].find(":") > -1):
		line[0]=line[0].replace("prefix ","")
		prefixdict[line[1].strip()]=line[0].strip()

	if (uri in prefixdict):
	    return prefixdict[uri]
	else:
	    return "$$UNKNWN PREFIX$$:"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 
    def writeQuery(self,pdict,wdict,uri):
	prefixes= definitions.RDF_PREFIX_PRELUDE+ """
	prefix bbkmm:        <http://bbk.ac.uk/MuseumMapProject/def/>"""
	
	for key, val in pdict.iteritems():
	    if isinstance(val,dict):
		if isinstance(key,tuple):
		    clazz,pred=(key)
		    parts=clazz.split(":")
		    #print "?"+parts[1]+" rdfs:subClassOf|(owl:intersectionOf/rdf:rest*/rdf:first)* "+uri+"  ."
		else:
		    pred=key
		    print "??"+uri+" rdfs:subClassOf|(owl:intersectionOf/rdf:rest*/rdf:first)* "+self.lastPart(pred)+"  ."
		    print "["+str(key)+"]" 
		if (pred.find("/") > -1):
		    self.writeQuery(val,wdict,self.lastPart(pred)+"URI")
		else:
		    self.writeQuery(val,wdict,pred+"URI")
		    
	    else:
		print "SELECT ?"+self.lastPart(key)
		print "WHERE  {"
		print uri+ " "+self.getPrefix(prefixes,
					      self.firstPart(key))+self.lastPart(key)+ " ?"+self.lastPart(key)
		print "       }"
		
		
	return wdict

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

	
##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """

    IS = Ispect("VisitorMeasurement")

    res=IS.getSuperClasses(IS._clazz)
    #print "?#?#? ispect.py at line: 83 Dbg-out variable \res [",res,"]\n";
    indent=""
    pp = pprint.PrettyPrinter(indent=4)
    for r in res:
	instlist=IS.getAllInstancesOfClass(r)
	aninst=None
	if (len(instlist) > 0):
	    instprint="INSTANCE:"+instlist[0]
	    #aninst=instlist[0]
	    #aninst="http://bbk.ac.uk/MuseumMapProject/def/TemporalEntity/id/n10/mm.aim.0882"
	else:
	    instprint="No instances found"
	indent=indent+"   "
	print indent+"=== SubclassOf "+r+" "+instprint
	pd=IS.getProperties(r,aninst)
	print indent+"PD --------------------------------"
	#pp.pprint(pd)
	IS.prettyPrint(pd)
	print indent+"PD --------------------------------"

	## This now needs to turn into recursion and building a json
	for key, val in pd.iteritems():
	    if isinstance(val,dict):
		pdclazz,pdprop=(key)
		if (aninst != None):
		    pdinst=IS.getInstanceOfClassFromProperty(pdclazz,aninst,pdprop)
		    if (len(pdinst) > 0):
			pdsub=IS.getProperties(pdclazz,pdinst[0])
			print "?#?#? ispect.py at line: 442 Dbg-out variable \pdsub [",pdsub,"]\n";
			IS.prettyPrint(pdsub)
		    
		    print "?#?#? ispect.py at line: 386 Dbg-out variable \pdinst [",pdinst,"]\n";
	print "================================================"
	
