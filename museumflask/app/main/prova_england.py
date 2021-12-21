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
    "E10000002"	: "Buckinghamshire",		
#    "E10000003"	: "Cambridgeshire",		
    "E10000006"	: "Cumbria",		
    "E10000007"	: "Derbyshire",		
    "E10000008"	: "Devon",		
    "E10000009"	: "Dorset",		
    "E10000011"	: "East Sussex",		
    "E10000012"	: "Essex",		
    "E10000013"	: "Gloucestershire",		
    "E10000014"	: "Hampshire",		
    "E10000015"	: "Hertfordshire",		
    "E10000016"	: "Kent",		
    "E10000017"	: "Lancashire",		
    "E10000018"	: "Leicestershire",		
    "E10000019"	: "Lincolnshire",		
    "E10000020"	: "Norfolk",		
    "E10000021"	: "Northamptonshire",		
    "E10000023"	: "North Yorkshire",		
    "E10000024"	: "Nottinghamshire",		
    "E10000025"	: "Oxfordshire",		
    "E10000027"	: "Somerset",		
    "E10000028"	: "Staffordshire",		
    "E10000029"	: "Suffolk",		
    "E10000030"	: "Surrey",		
    "E10000031"	: "Warwickshire",		
    "E10000032"	: "West Sussex",		
    "E10000034"	: "Worcestershire",		
    "E99999999"	: "(pseudo) England (UA/MD/LB",		
    "L99999999"	: "(pseudo) Channel Islands",		
    "M99999999"	: "(pseudo) Isle of Man",		
    "N99999999"	: "(pseudo) Northern Ireland",		
    "S99999999"	: "(pseudo) Scotland",		
    "W99999999"	: "(pseudo) Wales"		
    }

GOR_TRANSLATION_TABLE={
    "E12000001"	: "North East",
    "E12000002"	: "North West",
    "E12000003"	: "Yorkshire and The Humber",
    "E12000004"	: "East Midlands",
    "E12000005"	: "West Midlands",
    "E12000006"	: "East of England",
    "E12000007"	: "London",
    "E12000008"	: "South East",
    "E12000009"	: "South West",
    "W99999999"	: "(pseudo) Wales",
    "S99999999"	: "(pseudo) Scotland",
    "N99999999"	: "(pseudo) Northern Ireland",
    "L99999999"	: "(pseudo) Channel Islands",
    "M99999999"	: "(pseudo) Isle of Man"
    }

CA_CODE_TO_GOR_TABLE={
"E47000001":"E12000002",
"E47000002":"E12000003",
"E47000003":"E12000003",
"E47000004":"E12000002",
"E47000005":"E12000001",
"E47000006":"E12000001",
"E47000007":"E12000005",
"E47000008":"E12000006",
"E47000009":"E12000009"
}


# "LAD17CD,LAD17NM,CAUTH17CD,CAUTH17NM,FID"


CA_CODE_TO_NAME_TABLE={
"E47000001":"Greater Manchester CA",
"E47000002":"Sheffield City Region CA",
"E47000003":"West Yorkshire CA",
"E47000004":"Liverpool City Region CA",
"E47000005":"North East CA",
"E47000006":"Tees Valley CA",
"E47000007":"West Midlands CA",
"E47000008":"Cambridgeshire and Peterborough CA",
"E47000009":"West of England CA"
}

LA_TO_CA_CODES_TABLE={
"E08000001":"E47000001",
"E08000002":"E47000001",
"E08000003":"E47000001",
"E08000004":"E47000001",
"E08000005":"E47000001",
"E08000006":"E47000001",
"E08000007":"E47000001",
"E08000008":"E47000001",
"E08000009":"E47000001",
"E08000010":"E47000001",
"E08000016":"E47000002",
"E08000017":"E47000002",
"E08000018":"E47000002",
"E08000019":"E47000002",
"E08000032":"E47000003",
"E08000033":"E47000003",
"E08000034":"E47000003",
"E08000035":"E47000003",
"E08000036":"E47000003",
"E06000006":"E47000004",
"E08000011":"E47000004",
"E08000012":"E47000004",
"E08000013":"E47000004",
"E08000014":"E47000004",
"E08000015":"E47000004",
"E06000047":"E47000005",
"E06000057":"E47000005",
"E08000021":"E47000005",
"E08000022":"E47000005",
"E08000023":"E47000005",
"E08000024":"E47000005",
"E08000037":"E47000005",
"E06000005":"E47000006",
"E06000001":"E47000006",
"E06000002":"E47000006",
"E06000003":"E47000006",
"E06000004":"E47000006",
"E08000025":"E47000007",
"E08000026":"E47000007",
"E08000027":"E47000007",
"E08000028":"E47000007",
"E08000029":"E47000007",
"E08000030":"E47000007",
"E08000031":"E47000007",
"E07000008":"E47000008",
"E07000009":"E47000008",
"E07000010":"E47000008",
"E07000011":"E47000008",
"E07000012":"E47000008",
"E06000031":"E47000008",
"E06000022":"E47000009",
"E06000023":"E47000009",
"E06000025":"E47000009"
}

LA_TO_CA_NAMES_TABLE={
"Bolton":"Greater Manchester CA",
"Bury":"Greater Manchester CA",
"Manchester":"Greater Manchester CA",
"Oldham":"Greater Manchester CA",
"Rochdale":"Greater Manchester CA",
"Salford":"Greater Manchester CA",
"Stockport":"Greater Manchester CA",
"Tameside":"Greater Manchester CA",
"Trafford":"Greater Manchester CA",
"Wigan":"Greater Manchester CA",
"Barnsley":"Sheffield City Region CA",
"Doncaster":"Sheffield City Region CA",
"Rotherham":"Sheffield City Region CA",
"Sheffield":"Sheffield City Region CA",
"Bradford":"West Yorkshire CA",
"Calderdale":"West Yorkshire CA",
"Kirklees":"West Yorkshire CA",
"Leeds":"West Yorkshire CA",
"Wakefield":"West Yorkshire CA",
"Halton":"Liverpool City Region CA",
"Knowsley":"Liverpool City Region CA",
"Liverpool":"Liverpool City Region CA",
"St. Helens":"Liverpool City Region CA",
"Sefton":"Liverpool City Region CA",
"Wirral":"Liverpool City Region CA",
"County Durham":"North East CA",
"Northumberland":"North East CA",
"Newcastle upon Tyne":"North East CA",
"North Tyneside":"North East CA",
"South Tyneside":"North East CA",
"Sunderland":"North East CA",
"Gateshead":"North East CA",
"Darlington":"Tees Valley CA",
"Hartlepool":"Tees Valley CA",
"Middlesbrough":"Tees Valley CA",
"Redcar and Cleveland":"Tees Valley CA",
"Stockton-on-Tees":"Tees Valley CA",
"Birmingham":"West Midlands CA",
"Coventry":"West Midlands CA",
"Dudley":"West Midlands CA",
"Sandwell":"West Midlands CA",
"Solihull":"West Midlands CA",
"Walsall":"West Midlands CA",
"Wolverhampton":"West Midlands CA",
"Cambridge":"Cambridgeshire and Peterborough CA",
"East Cambridgeshire":"Cambridgeshire and Peterborough CA",
"Fenland":"Cambridgeshire and Peterborough CA",
"Huntingdonshire":"Cambridgeshire and Peterborough CA",
"South Cambridgeshire":"Cambridgeshire and Peterborough CA",
"Peterborough":"Cambridgeshire and Peterborough CA",
"Bath and North East Somerset":"West of England CA",
"Bristol, City of":"West of England CA",
"South Gloucestershire":"West of England CA"
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
#	print parts[0]+'=='+parts[1]
	
#   pcd 0,pcd2 1,pcds 2,dointr 3,doterm 4,usertype 5,oseast1m 6,osnrth1m 7,osgrdind 8,oa11 9,cty 10,
#   laua 11,ward 12,hlthau 13,hro 14,ctry 15,gor 16,pcon 17,eer 18,teclec 19,ttwa 20,
#   pct 21,nuts 22,park 23,lsoa11 24,msoa11 25,wz11 26,ccg 27,bua11 28,buasd11 29,ru11ind 30,
#   oac11 31,lat 32,long 33,lep1 34,lep2 35,pfa 36 ,imd 37

    with open(fname) as f:
	content = f.readlines()
	header=content[0].split(',')
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
    print 'key errors were '+str(keyerrors)
    print 'unknown errors were '+str(keyerrors)
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
    
columndict={}
def printtolist(key,listofmuseums):
    newkey=key.replace("/",",")
    partskey=newkey.split(",")
    lnewkey=len(partskey)
    for m in listofmuseums:
	(museum,name)=m
	mparts=museum.split("/")
	mpartslen=len(mparts)
	mkey=mparts[mpartslen-1]
	if (lnewkey < 4):
	    if (partskey[1] == "London"):
		line= "*?#?"+mkey+","+partskey[0]+",,,,"+partskey[1]+",,"+partskey[2]
	    else:
		line= "*?#?"+mkey+","+partskey[0]+",,,,"+partskey[1]+","+partskey[2]+","
	else:
	    line= "*?#?"+mkey+","+partskey[0]+",,,,"+partskey[1]+","+partskey[2]+","+partskey[3]
	    
	print line

    return

##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """


readAdminData()
#print "-----------------------------------------------------"
# Put LA in regions where 99999
#for pc,la in definitions.POSTCODE2_LA_DICT.iteritems():
#    print pc+" -> "+la
#print "-----------------------------------------------------"
#exit(1)


treedict={}

# Create england dict
treedict['England']={}
#Fill gors
sgor=sorted(GOR_TRANSLATION_TABLE.items(), key=lambda x: x[1])
# After this the dict becomes a list.....
# Remove pseudo from a reversed list
for trange in reversed(xrange(len(sgor))):
    tup=(sgor[trange])
    if (tup[0].find("99999999") > -1):
	del sgor[trange]
regionsdict={}
for tup in sgor:
    regionsdict[tup[1]]=[]
print "?#?#? prova.py at line: 74 Dbg-out variable \regionsdict [",str(regionsdict),"]\n";
    
# Counties
county_and_region_table={}
for key, val in COUNTY_TRANSLATION_TABLE.iteritems():
    county_and_region_table[key]=val
for key, val in CA_CODE_TO_NAME_TABLE.iteritems():
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
print "?#?#? prova.py at line: 86 Dbg-out variable \countiesdict [",str(countiesdict),"]\n";


# Put counties in regions
for counties in countiesdict:
    if (counties in definitions.COUNTY2_REGION_DICT):
	thisregion=definitions.COUNTY2_REGION_DICT[counties]
	if (thisregion in regionsdict):
	    regionsdict[thisregion].append(counties)
	    print "?#?#? prova_england.py at line: 413 Dbg-out variable \counties [",counties,"]\n";
	    print "?#?#? prova_england.py at line: 413 Dbg-out variable \thisregion [",thisregion,"]\n";
	else:
	    print "Not in regiondic 1"+counties
    else:
	print "Not in regiondic 2"+counties

# Put CA in regions

for ca_code,ca_name in CA_CODE_TO_NAME_TABLE.iteritems():
    if (ca_code in CA_CODE_TO_GOR_TABLE):
 	thisregioncode=CA_CODE_TO_GOR_TABLE[ca_code]
	thisregion=GOR_TRANSLATION_TABLE[thisregioncode]
 	if (thisregion in regionsdict):
 	    regionsdict[thisregion].append(ca_name)
 	else:
 	    print "Not in regiondic 11"+ca_name
    else:
	print "Not in regiondic 22"+ca_name

print "-----------------------------------------------------"
# Put LA in regions where 99999
for ctyname,regname in definitions.COUNTY2_REGION_DICT.iteritems():
    print ctyname+" //-> "+regname
print "-----------------------------------------------------"

for laname, countyname in definitions.LA2_COUNTY_DICT.iteritems():
    print laname+" +-> "+countyname
    if (countyname == "(pseudo) England (UA/MD/LB"):
	if (laname in LA_TO_CA_NAMES_TABLE):
	    countyname=LA_TO_CA_NAMES_TABLE[laname]
	    print "###adding "+laname+" to "+countyname
	    countiesdict[countyname].append(laname)
	else:
	    thisregion=definitions.LA2_REGION_DICT[laname]
	    print "............."+thisregion
	    regionsdict[thisregion].append(laname)
    elif (countyname.find("pseudo") < 0):
	countiesdict[countyname].append(laname)

	# Put LA in regions from LATOCA dict
    for laname, countyname in LA_TO_CA_NAMES_TABLE.iteritems():
	print "###adding "+laname+" to "+countyname
	lalist=countiesdict[countyname]
	if (not laname in lalist):
	    countiesdict[countyname].append(laname)

	
	
print "-----------------------------------------------------"

for reg in regionsdict:
    print reg
    for county in regionsdict[reg]:
	print "    "+county

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
		#print "?#?#? prova.py at line: 373 Dbg-out variable \postcode [",postcode,"]\n";
		
		if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
		    thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
		    # print "?#?#? prova.py at line: 373 Dbg-out variable \thiscountry [",thiscountry,"]\n";
		    if (thiscountry == 'England'):
			tup=(museum,name)
			if (not thiscountry in museumdict):
			    museumdict[thiscountry]=[]
			museumdict[thiscountry].append(tup)
			if (postcode in definitions.POSTCODE2_REGION_DICT):
			    thisregion=definitions.POSTCODE2_REGION_DICT[postcode]
			    key=thiscountry+"/"+thisregion
			    if (not key in museumdict):
				museumdict[key]=[]
			    museumdict[key].append(tup)
			    print "1 PAPPENDING KEY:"+key
			else:
			    print "NOT IN POSTCODE2_REGION_DICT"+postcode

			# CA required
			if (postcode in definitions.POSTCODE2_LA_DICT):
			    thisla=definitions.POSTCODE2_LA_DICT[postcode]
			else:
			    thisla=""
			#- - 			    
			
			if (thisla in LA_TO_CA_NAMES_TABLE):
			    thiscounty=LA_TO_CA_NAMES_TABLE[thisla]
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
				print "2 PAPPENDING KEY:"+key

			else:
			    print "NOT IN POSTCODE2_COUNTY_DICT"+postcode
			
			if (postcode in definitions.POSTCODE2_LA_DICT):
			    thisla=definitions.POSTCODE2_LA_DICT[postcode]
			    if (thiscounty.find("pseudo") > 0):
				key=thiscountry+"/"+thisregion+"/"+thisla
			    else:
				key=thiscountry+"/"+thisregion+"/"+thiscounty+"/"+thisla
				print "?#?#? prova_england.py at line: 593 Dbg-out variable \key [",key,"]\n";
				
			    if (not key in museumdict):
				museumdict[key]=[]
			    museumdict[key].append(tup)

			    ## CA
			    if (thisla in LA_TO_CA_NAMES_TABLE):
				thiscaname=LA_TO_CA_NAMES_TABLE[thisla]
				
				key=thiscountry+"/"+thisregion+"/"+thiscaname
				if (not key in museumdict):
				    museumdict[key]=[]
				museumdict[key].append(tup)
							    
			    print "3 PAPPENDING KEY:"+key
			else:
			    print "NOT IN POSTCODE2_LA_DICT "+postcode


			print museum+" "+postcode+" X_X_X "+thiscountry+"/"+thisregion+"/"+thiscounty+"/"+thisla
			
		else:
		    print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
		    if (postcode in definitions.POSTCODE2_DISTR_DICT):
			print "But in region dict:"+definitions.POSTCODE2_DISTR_DICT[postcode]
		    if (postcode in definitions.POSTCODE2_COUNTY_DICT):
			print "But in county  dict:"+definitions.POSTCODE2_COUNTY_DICT[postcode]

		    notinlacount+=1
print "?#?#? prova.py at line: 394 Dbg-out variable \notinlacount [",notinlacount,"]\n";
# iterating, always use iteritems !
for key, val in museumdict.iteritems():
   print key+" -> "+str(val)

print "-----------------------------------------------------"
print "ENGLAND: ("+str(len(museumdict['England']))+")"+str(museumdict['England'])
for reg in sorted(regionsdict):
    print "Region ---------"+reg
    print 'England'+"/"+reg+": ("+str(len(museumdict['England'+"/"+reg]))+")"+str(museumdict['England'+"/"+reg])
    regiontotal=len(museumdict['England'+"/"+reg])
    total=0
    for county in sorted(regionsdict[reg]):
	print "County    "+county
	key='England'+"/"+reg+"/"+county
	if (key in museumdict):
	    print "    "+key+": ("+str(len(museumdict[key]))+")"+str(museumdict[key])
	    #total=total+len(museumdict[key])
	    if (county in countiesdict):
		for la in sorted(countiesdict[county]):
		    key='England'+"/"+reg+"/"+county+"/"+la
		    if (key in museumdict):
			print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
			total=total+len(museumdict[key])
			print "-----------------------------------------------------"
	    else:
		# We have a pseudo
		if (key in museumdict):
		    print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
		    total=total+len(museumdict[key])
		    print "-----------------------------------------------------"
	else:
	    print "    No museums for this key:"+key
	    
    if (regiontotal != total):
	print "**** TOTOAL:"+str(total)+" NOT CORRECT REGION:"+str(regiontotal)
		    
print "-----------------------------------------------------"
print "######################################################"
for reg in sorted(regionsdict):
    regiontotal=len(museumdict['England'+"/"+reg])
    total=0
    for county in sorted(regionsdict[reg]):
	key='England'+"/"+reg+"/"+county
	if (key in museumdict):
	    if (county in countiesdict):
		for la in sorted(countiesdict[county]):
		    key='England'+"/"+reg+"/"+county+"/"+la
		    if (key in museumdict):
			#print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
			printtolist(key,museumdict[key])
	    else:
		# We have a pseudo
		if (key in museumdict):
		    #print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
		    printtolist(key,museumdict[key])
	else:
	    print "    No museums for this key:"+key
	    

