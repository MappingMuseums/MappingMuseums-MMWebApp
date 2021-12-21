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
from . import apputils

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
SPARQLENDPOINT="http://193.61.44.11:8890/sparql"
DEFAULTGRAPH="http://bbk.ac.uk/MuseumMapProject/graph/v6"


#cat NSPL_AUG_2017_UK.csv | awk -F, '{print $16}' | sort -u

LA_TRANSLATION_TABLE={}
REVERSE_LA_TRANSLATION_TABLE={}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


def readAdminData():
    pcfname=definitions.BASEDIR+'os_postcodes_io.csv'
    pcfname=definitions.BASEDIR+'postcodes.csv'
    pcfname=definitions.BASEDIR+'NSPL_AUG_2017_UK.csv'
    lafname=definitions.BASEDIR+'LocalAuthMap.csv'
    apputils.readONSPCRepo(pcfname,
			   lafname,
			   definitions.POSTCODE2_COUNTY_DICT,
			   definitions.POSTCODE2_COUNTRY_DICT,
			   definitions.POSTCODE2_LA_DICT,
			   definitions.POSTCODE2_REGION_DICT,
			   definitions.COUNTY2_REGION_DICT,
			   definitions.LA2_COUNTY_DICT,
			   definitions.LA2_REGION_DICT,
			   LA_TRANSLATION_TABLE,
			   REVERSE_LA_TRANSLATION_TABLE
                  )
    return True
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getMarkerData():
    sparql = SPARQLWrapper(SPARQLENDPOINT)

    
    query="""
      prefix dcterms:         <http://purl.org/dc/terms/>  
    prefix owl:             <http://www.w3.org/2002/07/owl#> 
    prefix rdf:             <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs:            <http://www.w3.org/2000/01/rdf-schema#>  
    prefix xml:             <http://www.w3.org/XML/1998/namespace> 
    prefix xsd:             <http://www.w3.org/2001/XMLSchema#>
    prefix prov:            <http://www.w3.org/ns/prov#>
    prefix time:            <http://www.w3.org/2006/time#>
    
    prefix bbkmm: <http://bbk.ac.uk/MuseumMapProject/def/> 
   
    SELECT DISTINCT  ?museum ?Latitude ?Longitude ?Name_of_museum ?Postcode  
    FROM <"""+DEFAULTGRAPH+""">
    WHERE { 
    ?museum  rdf:type bbkmm:Museum .
    ?museum  bbkmm:hasLatitude ?Latitude . 
    ?museum  bbkmm:hasLongitude ?Longitude . 
    OPTIONAL{ ?museum   bbkmm:hasName_of_museum ?Name_of_museum . } 
OPTIONAL{ ?museum   bbkmm:hasPostcode ?Postcode . } 

    } 
            
    """
    print "-------------------------------------------------------------------" 
    print query
    print "-------------------------------------------------------------------" 
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print results
    #print "End Results-------------------------------------------------------------------" 
    return results
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def printtolist(key,listofmuseums,pads,incountry):

    LA_DECOR_TABLE={
	"England":"?????",
	"Channel Islands":" (Channel Islands)",
	"Isle of Man":" (Isle of Man)",
	"Northern Ireland":" (NI Loc Gov District)",
	"Scotland":" (Scottish Council Area)",
	"Wales":" (Welsh UA)"
    }
    LA_TRAIL_TABLE={
	"England":"",
	"Channel Islands":",,,,",
	"Isle of Man":",,,,",
	"Northern Ireland":",,,,,",
	"Scotland":",,,,,,",
	"Wales":",,,,,,,"
    }

    newkey=key.replace("/",",")
    nparts=newkey.split(",")
    print "LISTOFMUSEUMS-----------------------------------------------------"
    print listofmuseums
    print "-----------------------------------------------------"
    for m in listofmuseums:
	(museum,name)=m
	mparts=museum.split("/")
	mpartslen=len(mparts)
	mkey=mparts[mpartslen-1]
	#print "*?#?"+mkey+","+nparts[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[nparts[0]]+pads+","+nparts[2]+LA_DECOR_TABLE[nparts[0]]+":"+REVERSE_LA_TRANSLATION_TABLE[nparts[2]]+pade+",,,"
	print "*?#?"+mkey+","+nparts[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[nparts[0]]+pads+","+nparts[2]+LA_DECOR_TABLE[nparts[0]]+":"+REVERSE_LA_TRANSLATION_TABLE[nparts[2]]+LA_TRAIL_TABLE[nparts[0]]
    return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def doCountry(incountry,inpseudo,pads,pade):
    treedict={}
    
    # Create england dict
    treedict[incountry]={}
    
    # Counties
    pseudo=inpseudo
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
        print "?#?#? prova.py at line: 307 Dbg-out variable \las [",las,"]\n";
        countiesdict[pseudo].append(las)
        
    print "-----------------------------------------------------"
    
    # Get all postcodes
    results=getMarkerData()
    
    rlen=len(results["results"]["bindings"])
    print "?#?#? prova.py at line: 365 Dbg-out variable \rlen [",rlen,"]\n";
    museumdict={}
    notinlacount=0
    
    for result in results["results"]["bindings"]:
        if ("museum" in result):
            museum=result["museum"]["value"]
            if (definitions.NAME_OF_MUSEUM in result):
                name=result[definitions.NAME_OF_MUSEUM]["value"]
                if (definitions.POSTCODE in result):
                    postcode=result[definitions.POSTCODE]["value"].replace(' ','')
                    print "?#?#? prova.py at line: 373 Dbg-out variable \postcode [",postcode,"]\n";
                    
                    if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
                        thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
			print "?#?#? prova.py at line: 373 Dbg-out variable \thiscountry [",thiscountry,"]\n";
                        if (thiscountry.strip() == incountry.strip()):
                            tup=(museum,name)
                            if (not thiscountry in museumdict):
                                museumdict[thiscountry]=[]
                            museumdict[thiscountry].append(tup)
    
                            if (postcode in definitions.POSTCODE2_LA_DICT):
                                thisla=definitions.POSTCODE2_LA_DICT[postcode]
                                key=thiscountry+"/"+pseudo+"/"+thisla
                                    
                                if (not key in museumdict):
                                    museumdict[key]=[]
                                museumdict[key].append(tup)
                                print "3 PAPPENDING KEY:"+key
                            else:
                                print "NOT IN POSTCODE2_LA_DICT "+postcode
                            print postcode+" X_X_X "+thiscountry+"/"+pseudo+"/"+thisla
                            
                    else:
                        print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
                        if (postcode in definitions.POSTCODE2_DISTR_DICT):
                            print "But in region dict:"+definitions.POSTCODE2_DISTR_DICT[postcode]
                        if (postcode in definitions.POSTCODE2_COUNTY_DICT):
                            print "But in county  dict:"+definitions.POSTCODE2_COUNTY_DICT[postcode]
    
                        notinlacount+=1
    print "?#?#? prova.py at line: 394 Dbg-out variable \notinlacount [",notinlacount,"]\n";
    for key, val in museumdict.iteritems():
       print key+" -> "+str(val)
    print "-----------------------------------------------------"
    print incountry+": ("+str(len(museumdict[incountry]))+")"+str(museumdict[incountry])
    for la in sorted(countiesdict[county]):
        key=incountry+"/"+pseudo+"/"+la
        if (key in museumdict):
            print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
            print "-----------------------------------------------------"
        else:
            print "    No museums for this key:"+key
                
                    
    
    print "######################################################"
    print "museumdict-----------------------------------------------------"
    print museumdict
    print "countiesdict-----------------------------------------------------"
    print countiesdict
    print "-----------------------------------------------------"
    for la in sorted(countiesdict[county]):
        key=incountry+"/"+pseudo+"/"+la
        if (key in museumdict):
            printtolist(key,museumdict[key],pads,incountry)
        else:
            print "    No museums for this key:"+key
    
    
    return

##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """


readAdminData()
doCountry("Wales","(pseudo) Wales","",",,")
doCountry("Scotland","(pseudo) Scotland",",",",")
doCountry("Northern Ireland","(pseudo) Northern Ireland",",,","")
doCountry("Channel Islands","(pseudo) Channel Islands","",",,")
doCountry('Isle of Man','(pseudo) Isle of Man',"",",,")

#print "-----------------------------------------------------"
# Put LA in regions where 99999
#for pc,la in definitions.POSTCODE2_LA_DICT.iteritems():
#    print pc+" -> "+la
#print "-----------------------------------------------------"
#exit(1)






	    

