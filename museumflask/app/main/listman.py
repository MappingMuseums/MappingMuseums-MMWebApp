##
# @file
#  
#  
#  
#  
#  
#  
#  
#  
#  
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import operator

import sys
import csv
import time
import re
import cgi

from flask import current_app as app

from . import definitions
from definitions import PREFIX_WITHCOLON
from definitions import PREFIX_WITHCOLON
from definitions import PROPERTY_TYPES_DICT
from definitions import XML_TYPES
from definitions import LISTS
from definitions import RESET_LISTS



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Updata a list in db
# Arguments:
# 
# @param classproperty name of list
# @param lizt list to be saved

def updateList(classproperty,lizt):
## Note: Adds Lizt to end of classproperty
    
    textvalues=""
    for item in lizt:
        textvalues=textvalues+'"'+str(item)+'"'+" "

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query="DEFINE sql:log-enable 2 \n"
    query=query+definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    DELETE  
    {
      GRAPH <"""+app.config['DEFAULTGRAPH']+""">
       {
          """+PREFIX_WITHCOLON+classproperty+"""  ?p  ?item
       }
    }
    WHERE
    {
      """+PREFIX_WITHCOLON+classproperty+"""  ?p  ?item
    }
    """
    sparql.setQuery(query)
    sparql.setMethod("POSTDIRECTLY")
    print "================================================"
    print query
    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print len(results["results"]["bindings"])
    print results

    query="DEFINE sql:log-enable 2 \n"
    query=query+definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    INSERT
    {
      GRAPH <"""+app.config['DEFAULTGRAPH']+""">

       {
         """+PREFIX_WITHCOLON+classproperty+"""  """+PREFIX_WITHCOLON+"""contents ("""+textvalues+""") .
       }
    }
    WHERE
    {
      """+PREFIX_WITHCOLON+classproperty+"""  ?p  ?item
    }
    """
    sparql.setQuery(query)
    sparql.setMethod("POSTDIRECTLY")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print len(results["results"]["bindings"])
    print results
    
    return "OK"


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Insert a list in db
# Arguments:
# 
# @param classproperty name of list
# @param lizt list to be inserted

def insertList(classproperty,lizt):
    #print "?#?#? listman.py at line: 119 Dbg-out variable \lizt [",lizt,"]\n";
    #print "?#?#? listman.py at line: 119 Dbg-out variable \classproperty [",classproperty,"]\n";
    textvalues=""
    for item in lizt:
        textvalues=textvalues+'"'+str(item)+'"'+" "

	
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    INSERT
    {
      GRAPH <"""+app.config['DEFAULTGRAPH']+""">

       {
         """+PREFIX_WITHCOLON+classproperty+"""  """+PREFIX_WITHCOLON+"""contents ("""+textvalues+""") .
       }
    }
    """
    sparql.setQuery(query)
    sparql.setMethod("POSTDIRECTLY")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return "OK"


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get a list from the db
# Arguments:
# 
# @param classproperty name of list
def getList(classproperty):
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    reslist=[]
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select ?element (count(?mid)-1 as ?position) 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    where { 
              """+PREFIX_WITHCOLON+classproperty+""" """+PREFIX_WITHCOLON+"""contents/rdf:rest* ?mid . ?mid rdf:rest* ?node .
              ?node rdf:first ?element .
          }
          order by ?position
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["element"]["value"]
            reslist.append(item)
	    

    return reslist


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Reset a list to its original value
# Arguments:
# 
# @param listname name of list
def resetList(listname):
    values=getList(listname+"ListReset")
    if (len(values) < 1):
        print "*** ERROR : no RESET list values for list "+listname
        print "*** ERROR : Bad things will happen "
    else:
        updateList(listname,values)
    return "OK"
                
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Inserts a configuration in the db
# Arguments:
# 
# @param classproperty name
# @param config values

def insertConfig(classproperty,config):

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    configcopy=config.replace('\n', ' ').replace('\r', '').replace('\"', '\\"')
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    INSERT
    {
      GRAPH <"""+app.config['DEFAULTGRAPH']+""">

       {
         """+PREFIX_WITHCOLON+classproperty+"""  """+PREFIX_WITHCOLON+"""hasConfig '"""+configcopy+"""'^^xsd:string .
       }
    }
    """
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return "OK"


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves a configuration from the db
# Arguments:
# 
# @param classproperty name
def getConfig(classproperty):
    sparql  = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    reslist = ""
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select DISTINCT * 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    where {
    """+PREFIX_WITHCOLON+classproperty+"""  """+PREFIX_WITHCOLON+"""hasConfig ?item
    }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["item"]["value"]
            reslist=item
                

    return reslist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves all variables that are rdf:lists
def getAllListNames():
    sparql  = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    reslist = []
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select DISTINCT ?name 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    where {
            ?name  bbkmm:contents  ?node .
    }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["name"]["value"]
            reslist.append(item)
                

    return reslist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves all variables that are rdf:lists
def getAllListNamesWithFilter(filter):
    sparql  = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    reslist = []
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select DISTINCT ?name 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    where {
            ?name  bbkmm:contents  ?node .
    FILTER ((CONTAINS(LCASE(str(?name)),LCASE('"""+filter+"""'))))
    }
    
    """
    sparql.setQuery(query)
    #print "?#?#? listman.py at line: 306 Dbg-out variable \query [",query,"]\n";
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["name"]["value"]
	    #print "?#?#? listman.py at line: 314 Dbg-out variable \item [",item,"]\n";
            reslist.append(item)
                

    return reslist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get all values for a list name
# Arguments:
# 
# @param name the list
def getListCollection(name):
#    print "?#?#? listman.py at line: 323 Dbg-out variable \name [",name,"]\n";
    datatypeslist=[]
    # Get names of all lists
    all_lists=getAllListNames()
#    print "?#?#? listman.py at line: 327 Dbg-out variable \all_lists [",all_lists,"]\n";
    reslist=[]
    for lc in  range(len(all_lists)):
	# Check if list ends with Reset
	ln=all_lists[lc].replace("http://"+definitions.RDFDEFURI,"")
	if (not ln.endswith(definitions.RESET_NAME)):
	    # Check if first bit of list is named name
	    if (ln.startswith(name)):
		reslist.append(ln)
		
    
    # Get all props in res list
    for lc in reslist:
	thislist=getList(lc)
	# Add to all list
	datatypeslist=datatypeslist+thislist
	
    # Write the all list and return it
    #insertList(definitions.ALL+name,datatypeslist)
    return datatypeslist

	

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
