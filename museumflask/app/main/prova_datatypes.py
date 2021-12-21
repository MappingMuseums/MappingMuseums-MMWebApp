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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
SPARQLENDPOINT="http://193.61.44.11:8890/sparql"
DEFAULTGRAPH="http://bbk.ac.uk/MuseumMapProject/graph/v5"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getmuseumpredicatesold(): 

    predicatelistname="PredicateList"

    sparql = SPARQLWrapper(SPARQLENDPOINT)
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property
FROM <"""+DEFAULTGRAPH+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum 
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    print "====getmuseumpredicatesold============================================"
    print query
    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(results)
    print results['head']['vars']
    var=results['head']['vars']
    varstr=var[0]
#    print "?#?#? search.py at line: 166 Dbg-out variable \varstr [",varstr,"]\n";
#    print results['results']
    count=0
    clazzes=[]
#    pp = pprint.PrettyPrinter(indent=4)
#    pp.pprint(results)

    for result in results["results"]["bindings"]:
	uri=result[varstr]["value"]
	print "?#?#? apputils.py at line: 837 Dbg-out variable \uri [",uri,"]\n";
	uricomponents=uri.split('/')
	clazzname=uricomponents[5]
        clazzname=clazzname.replace(definitions.HASNAME,"")
        #clazzname=clazzname.replace(definitions.DEFNAME,"")
	clazzes.append((clazzname,clazzname))
	count=count+1
# 	if (count > 6):
# 	    break
#	print result["textcontent"]["value"]
 #   print "?#?#? search.py at line: 181 Dbg-out variable \clazzes [",clazzes,"]\n";

    definitions.LISTS["Predicate"]=predicatelistname
    return clazzes



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getpredicatestypes(): 
    sparql = SPARQLWrapper(SPARQLENDPOINT)
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property, ?range
FROM <"""+DEFAULTGRAPH+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum .
  ?property rdfs:range ?range
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    print "============getpredicatestypes===================================="
#    print query
#    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
#    print len(results["results"]["bindings"])
    var=results['head']['vars']
    varstr=var[0]
    count=0
    clazzes=[]

    for result in results["results"]["bindings"]:
	rtype=result["range"]["value"]
#        print rtype
        if (rtype.find("http://www.w3.org/2001/XMLSchema#")> -1):
            rtype=rtype.replace("http://www.w3.org/2001/XMLSchema#","")
        elif (rtype.find("/")> -1):
              uricomponents=rtype.split('/')
              urilen=len(uricomponents)-1
              clazzname=uricomponents[urilen]
              rtype=clazzname
              hashtag=rtype.find('#')
              if ( hashtag > -1):
                  rtype=rtype[hashtag+1:]
              
	uri=result["property"]["value"]
	uricomponents=uri.split('/')
	clazzname=uricomponents[5]
        clazzname=clazzname.replace(definitions.HASNAME,"")
        clazzname=clazzname.replace(definitions.DEFNAME,"")
	clazzes.append((clazzname,rtype))
        definitions.PROPERTY_TYPES_DICT[clazzname]=rtype
	count=count+1
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(clazzes)
    print "================================================"
    return clazzes


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getdatagroups(attributetypes):
# loop over all types picking non xml datatype
# add List to typename (dataproperty)
# get list from database
# add all elements of list as group:typename to map
#
#

    grouplist=[]
    #print "?#?#? apputils.py at line: 179 Dbg-out variable \attributetypes [",attributetypes,"]\n";
    for attributepair in attributetypes:
        #        print attributepair
        attribute=attributepair[0].strip()
        propertytype=attributepair[1].strip()
        if (not propertytype in definitions.XML_TYPES):
	    print "?#?#? apputils.py at line: 659 Dbg-out variable \propertytype [",propertytype,"]\n";
            sparql = SPARQLWrapper(SPARQLENDPOINT)
    
	    query=definitions.RDF_PREFIX_PRELUDE+"""
            prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

            select DISTINCT * 
            FROM <"""+DEFAULTGRAPH+""">
            where {
                    """+definitions.PREFIX_WITHCOLON+propertytype+definitions.LISTNAME+""" """+definitions.PREFIX_WITHCOLON+"""contents/rdf:rest*/rdf:first ?item
                  }
                  """
            sparql.setQuery(query)
            print "================================================"
            print query
            print "================================================"
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
#            print len(results["results"]["bindings"])
            if (len(results["results"]["bindings"]) < 1):
                option="<option value='1 Missing data here !'>1 Missing data here !</option>"
                grouplist.append((propertytype,option))
                option="<option value='2 Missing data here !'>2 Missing data here !</option>"
                grouplist.append((propertytype,option))
            else:
                listname=propertytype+definitions.LISTNAME
                definitions.LISTS[propertytype]=listname
                

            for result in results["results"]["bindings"]:
                item=result["item"]["value"]
#                print item
                option="<option value='"+item.strip()+"'>"+item.strip()+"</option>"
                grouplist.append((propertytype,option))


    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(grouplist)
    return grouplist
                
  

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getListCollection(name):
    datatypeslist=[]
    # Get names of all lists
    all_lists=getAllListNames()
    reslist=[]
    for lc in  range(len(all_lists)):
	# Check if list ends with Reset
	ln=all_lists[lc].replace("http://"+definitions.RDFDEFURI,"")
	print "?#?#? listman.py at line: 257 Dbg-out variable \all_lists [",ln,"]\n";
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
    insertList(definitions.ALL+name,datatypeslist)
    print "?#?#? listman.py at line: 271 Dbg-out variable \datatypeslist [",datatypeslist,"]\n";
    
    return datatypeslist

def getList(classproperty):
    sparql = SPARQLWrapper(SPARQLENDPOINT)
    reslist=[]
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select ?element (count(?mid)-1 as ?position) 
    FROM <"""+DEFAULTGRAPH+""">
    where { 
              """+definitions.PREFIX_WITHCOLON+classproperty+""" """+definitions.PREFIX_WITHCOLON+"""contents/rdf:rest* ?mid . ?mid rdf:rest* ?node .
              ?node rdf:first ?element .
          }
          order by ?position
    """
    sparql.setQuery(query)
#    print "================================================"
    print query
#    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
#    print len(results["results"]["bindings"])
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["element"]["value"]
            reslist.append(item)
                

    return reslist


def insertList(classproperty,lizt):
    textvalues=""
    for item in lizt:
        textvalues=textvalues+'"'+str(item)+'"'+" "

    sparql = SPARQLWrapper(SPARQLENDPOINT)
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    INSERT
    {
      GRAPH <"""+DEFAULTGRAPH+""">

       {
         """+definitions.PREFIX_WITHCOLON+classproperty+"""  """+definitions.PREFIX_WITHCOLON+"""contents ("""+textvalues+""") .
       }
    }
    """
    sparql.setQuery(query)
#    print "================================================"
#    print query
#    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print len(results["results"]["bindings"])
    print results
    
    return "OK"


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def getAllListNames():
    sparql  = SPARQLWrapper(SPARQLENDPOINT)
    reslist = []
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    select DISTINCT ?name 
    FROM <"""+DEFAULTGRAPH+""">
    where {
            ?name  bbkmm:contents  ?node .
    }
    """
    sparql.setQuery(query)
#    print "================================================"
#    print query
#    print "================================================"
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
#    print len(results["results"]["bindings"])
    if (len(results["results"]["bindings"]) < 1):
        return reslist
    else:
        for result in results["results"]["bindings"]:
            item=result["name"]["value"]
            reslist.append(item)
                

    return reslist





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getQueryForCol(incol,optional=True,museumuri='?museum '):
    print "?#?#? apputils.py at line: 855 Dbg-out variable \col [",incol,"]\n";
    if (not incol.startswith(definitions.DEFNAME)):
	defcol=definitions.DEFNAME+incol
	if (defcol in definitions.DATATYPEDICT):
	    col=defcol
	else:
	    col=incol
    else:
	col=incol
	
    if (col in definitions.DATATYPEDICT):
	print "definde:"+definitions.DATATYPEDICT[col]
    else:
	print col+" col not found"
    
    if (definitions.DATATYPEDICT[col] == definitions.DEFINED_RANGETYPE):
        # Get the object property and then its hasObject
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+col+'uri . \n'
	query=query+'?'+col+'uri '+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col[3:]+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
	print "?#?#? apputils.py at line: 884 Dbg-out variable \query [",query,"]\n";
	    
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_LISTTYPE):
        # Get the object property and then its hasObject
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+col+'uri . \n'
	colwithoutdef=col[3:]
        query=query+'?'+col+'uri '+definitions.PREFIX_WITHCOLON+definitions.HASNAME+colwithoutdef+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
	print "?#?#? apputils.py at line: 894 Dbg-out variable \query [",query,"]\n";
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_HIERTYPE):
        # Get the object property and then its hasObject
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+col+'uri . \n'
        query=query+'?'+col+'uri '+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+' ?'+col+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
	print "?#?#? apputils.py at line: 894 Dbg-out variable \query [",query,"]\n";
    elif (definitions.DATATYPEDICT[col] in definitions.XML_TYPES_WITH_PREFIX):
        #  plain type
        if(optional):
            query="OPTIONAL{ "+museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" . } \n"
        else:
            query= museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" .  \n"
            
    else:
	print "$$$$$$$$$$ ERROR UNKNOWN DATATYPE "+col+"$$$$$$$$$$"
	query=""
    return query


##======================================================================================================

if __name__ == '__main__':
    """ Run Process from the command line. """


pp = pprint.PrettyPrinter(indent=4)

# The following 3 methods have a side effect that the lists are entered into LISTS as well
definitions.LISTITEMS  = getmuseumpredicatesold()
print 'LISTITEMS ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
pp.pprint(definitions.LISTITEMS)
print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
definitions.ATTRITYPES = getpredicatestypes()
print 'ATTRITYPES ++++++++++++++++++++++++++++++++++++++++++++++++++++++'

pp.pprint(definitions.ATTRITYPES)
print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

if (definitions.INITIALISE_LISTS):
    datatypelist= getListCollection(definitions.DATATYPESLISTNAME)
    definitions.PREDICATELIST= getListCollection(definitions.PREDICATELISTNAME)
else:
    datatypelist= getList(definitions.ALL+definitions.DATATYPESLISTNAME)
    definitions.PREDICATELIST=getList(definitions.ALL+definitions.PREDICATELISTNAME)

for dtype in datatypelist:
    parts=dtype.split('#')
    colname=parts[0].replace(definitions.PREFIX_WITHCOLON+definitions.HASNAME,'')
    colname=colname.replace(definitions.HASNAME,'')
    typename=parts[1].replace(definitions.PREFIX_WITHCOLON,'')
    definitions.DATATYPEDICT[colname]=typename

print 'DATADICT ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
pp.pprint(definitions.DATATYPEDICT)
print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
definitions.DATAGROUPS = getdatagroups(definitions.ATTRITYPES)
print 'DATAGROUPS ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
pp.pprint(definitions.DATAGROUPS)
print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

columns=['Name_of_museum', 'County', 'Subject_classification_1998', 'Year_opened_and_closed', 'Governance']

for col in columns:
    query=getQueryForCol(col)
    print "?#?#? prova_datatypes.py at line: 448 Dbg-out variable \query [",query,"]\n";
    
