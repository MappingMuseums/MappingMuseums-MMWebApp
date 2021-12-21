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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
SPARQLENDPOINT="http://193.61.44.11:8890/sparql"
DEFAULTGRAPH="http://bbk.ac.uk/MuseumMapProject/graph/v6"


COUNTRY_TRANSLATION_TABLE={
    "E92000001":"England",
    "L93000001":"Channel Islands",
    "M83000003":"Isle of Man",
    "N92000002":"Northern Ireland",
    "S92000003":"Scotland",
    "W92000004":"Wales"
    }

#cat NSPL_AUG_2017_UK.csv | awk -F, '{print $16}' | sort -u

COUNTY_TRANSLATION_TABLE={
    "E10000002" : "Buckinghamshire",            
    "E10000003" : "Cambridgeshire",             
    "E10000006" : "Cumbria",            
    "E10000007" : "Derbyshire",         
    "E10000008" : "Devon",              
    "E10000009" : "Dorset",             
    "E10000011" : "East Sussex",                
    "E10000012" : "Essex",              
    "E10000013" : "Gloucestershire",            
    "E10000014" : "Hampshire",          
    "E10000015" : "Hertfordshire",              
    "E10000016" : "Kent",               
    "E10000017" : "Lancashire",         
    "E10000018" : "Leicestershire",             
    "E10000019" : "Lincolnshire",               
    "E10000020" : "Norfolk",            
    "E10000021" : "Northamptonshire",           
    "E10000023" : "North Yorkshire",            
    "E10000024" : "Nottinghamshire",            
    "E10000025" : "Oxfordshire",                
    "E10000027" : "Somerset",           
    "E10000028" : "Staffordshire",              
    "E10000029" : "Suffolk",            
    "E10000030" : "Surrey",             
    "E10000031" : "Warwickshire",               
    "E10000032" : "West Sussex",                
    "E10000034" : "Worcestershire",             
    "E99999999" : "(pseudo) England (UA/MD/LB",         
    "L99999999" : "(pseudo) Channel Islands",           
    "M99999999" : "(pseudo) Isle of Man",               
    "N99999999" : "(pseudo) Northern Ireland",          
    "S99999999" : "(pseudo) Scotland",          
    "W99999999" : "(pseudo) Wales"              
    }

GOR_TRANSLATION_TABLE={
    "E12000001" : "North East",
    "E12000002" : "North West",
    "E12000003" : "Yorkshire and The Humber",
    "E12000004" : "East Midlands",
    "E12000005" : "West Midlands",
    "E12000006" : "East of England",
    "E12000007" : "London",
    "E12000008" : "South East",
    "E12000009" : "South West",
    "W99999999" : "(pseudo) Wales",
    "S99999999" : "(pseudo) Scotland",
    "N99999999" : "(pseudo) Northern Ireland",
    "L99999999" : "(pseudo) Channel Islands",
    "M99999999" : "(pseudo) Isle of Man"
    }

LA_TRANSLATION_TABLE={}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def readONSPCRepo(fname,
                  lafname,
                  postcode2_county_dict,
                  postcode2_country_dict,
                  postcode2_la_dict,
                  postcode2_region_dict,
                  county2_region_dict,
                  la2_county_dict,
                  la2_region_dict
               ):
    count=0
    with open(lafname) as f:
        content = f.readlines()
    f.close()


    for line in content:
        parts=line.split(',')
        LA_TRANSLATION_TABLE[parts[0].replace('"','')]=parts[1].replace('"','').replace('\n','').replace('\r','')
#       print parts[0]+'=='+parts[1]
        
#   pcd 0,pcd2 1,pcds 2,dointr 3,doterm 4,usertype 5,oseast1m 6,osnrth1m 7,osgrdind 8,oa11 9,cty 10,
#   laua 11,ward 12,hlthau 13,hro 14,ctry 15,gor 16,pcon 17,eer 18,teclec 19,ttwa 20,
#   pct 21,nuts 22,park 23,lsoa11 24,msoa11 25,wz11 26,ccg 27,bua11 28,buasd11 29,ru11ind 30,
#   oac11 31,lat 32,long 33,lep1 34,lep2 35,pfa 36 ,imd 37

    with open(fname) as f:
        content = f.readlines()
        header=content[0].split(',')
#       print "?#?#? apputils.py at line: 71 Dbg-out variable \header [",len(header),"]\n";
        lc=1
    f.close()


    header_dict={}
    hcount=0
    for h in header:
        header_dict[h.strip()]=hcount
        hcount=hcount+1

    keyerrors=0
    unknown=0
    print 'starting dict....'
    while (lc < len(content)):
        line=content[lc]
        line = line.strip()
        parts=line.split(',')
        pc=parts[header_dict['pcd 0']].replace('"','').replace(' ','')
        spc=str(pc)

        if (len(parts[header_dict['cty 10']].replace('"','')) >0):
            if (parts[header_dict['cty 10']].replace('"','') in COUNTY_TRANSLATION_TABLE):
                county=str(COUNTY_TRANSLATION_TABLE[parts[header_dict['cty 10']].replace('"','')])
                postcode2_county_dict[spc]=county
            else:
                postcode2_county_dict[spc]='UNKNOWN'
                unknown+=1
        else:
            #print 'key is in error:'+ parts[header_dict['cty 10']].replace('"','')
            keyerrors+=1
            
        if (len(parts[header_dict['ctry 15']].replace('"','')) > 0):
            if (parts[header_dict['ctry 15']].replace('"','') in COUNTRY_TRANSLATION_TABLE):
                postcode2_country_dict[spc]=str(COUNTRY_TRANSLATION_TABLE[parts[header_dict['ctry 15']].replace('"','')])
            else:
                postcode2_country_dict[spc]='UNKNOWN'
                unknown+=1
        else:
            #print 'key is in error:'+ parts[header_dict['ctry 15']].replace('"','')
            keyerrors+=1

        if (len(parts[header_dict['laua 11']].replace('"','')) > 0):
            if (parts[header_dict['laua 11']].replace('"','') in  LA_TRANSLATION_TABLE):
                la=str(LA_TRANSLATION_TABLE[parts[header_dict['laua 11']].replace('"','')])
                postcode2_la_dict[spc]=la
            else:
                postcode2_la_dict[spc]='UNKNOWN'
                unknown+=1
        else:
            #print 'key is in error:'+parts[header_dict['laua 11']].replace('"','')
            keyerrors+=1

        if (len(parts[header_dict['gor 16']].replace('"','')) > 0):
            if (parts[header_dict['gor 16']].replace('"','') in GOR_TRANSLATION_TABLE):
                gor=str(GOR_TRANSLATION_TABLE[parts[header_dict['gor 16']].replace('"','')])
                postcode2_region_dict[spc]=gor
            else:
                postcode2_region_dict[spc]='UNKNOWN'
                unknown+=1
        else:
            #print 'key is in error:'+parts[header_dict['gor 16']].replace('"','')
            keyerrors+=1

        county2_region_dict[county]=gor
        la2_county_dict[la]=county
        la2_region_dict[la]=gor
            
        lc+=1
    f.close()
    #print 'key errors were '+str(keyerrors)
    #print 'unknown errors were '+str(keyerrors)
    
    return
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def readAdminData():
    pcfname=definitions.BASEDIR+'os_postcodes_io.csv'
    pcfname=definitions.BASEDIR+'postcodes.csv'
    pcfname=definitions.BASEDIR+'NSPL_AUG_2017_UK.csv'
    lafname=definitions.BASEDIR+'LocalAuthMap.csv'
    readONSPCRepo(pcfname,
                  lafname,
                  definitions.POSTCODE2_COUNTY_DICT,
                  definitions.POSTCODE2_COUNTRY_DICT,
                  definitions.POSTCODE2_LA_DICT,
                  definitions.POSTCODE2_REGION_DICT,
                  definitions.COUNTY2_REGION_DICT,
                  definitions.LA2_COUNTY_DICT,
                  definitions.LA2_REGION_DICT
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
def printtolist(key,listofmuseums,pads,pade):
    newkey=key.replace("/",",")
    nparts=newkey.split(",")
    for m in listofmuseums:
	(museum,name)=m
	mparts=museum.split("/")
	mpartslen=len(mparts)
	mkey=mparts[mpartslen-1]
	print "*?#?"+mkey+","+nparts[0]+pads+","+nparts[2]+pade+",,,"
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
                        if (thiscountry == incountry):
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
    for la in sorted(countiesdict[county]):
        key=incountry+"/"+pseudo+"/"+la
        if (key in museumdict):
            printtolist(key,museumdict[key],pads,pade)
        else:
            print "    No museums for this key:"+key
    
    
    return

##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """


readAdminData()
#doCountry("Wales","(pseudo) Wales","",",ScD,NiD")
doCountry("Wales","(pseudo) Wales","",",,")
#doCountry("Scotland","(pseudo) Scotland",",WD",",NiD")
doCountry("Scotland","(pseudo) Scotland",",",",")
#doCountry("Northern Ireland","(pseudo) Northern Ireland",",WD,ScD","")
doCountry("Northern Ireland","(pseudo) Northern Ireland",",,","")
#doCountry("Channel Islands","(pseudo) Channel Islands")
#doCountry('Isle of Man','(pseudo) Isle of Man')

#print "-----------------------------------------------------"
# Put LA in regions where 99999
#for pc,la in definitions.POSTCODE2_LA_DICT.iteritems():
#    print pc+" -> "+la
#print "-----------------------------------------------------"
#exit(1)






	    

