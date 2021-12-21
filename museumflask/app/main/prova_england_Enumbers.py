

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
#from flask import current_app as app

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

#SPARQLENDPOINT=app.config['SPARQLENDPOINT']
SPARQLENDPOINT="http://193.61.44.11:8890/sparql"

DEFAULTGRAPH="http://bbk.ac.uk/MuseumMapProject/graph/v6"



#cat NSPL_AUG_2017_UK.csv | awk -F, '{print $16}' | sort -u




# "LAD17CD,LAD17NM,CAUTH17CD,CAUTH17NM,FID"






LA_TRANSLATION_TABLE={}
REVERSE_LA_TRANSLATION_TABLE={}
SEPARATOR="$"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

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
def readmainsheet(fname):
    # READY THE MAINSHEET
    print "Reading from "+fname
### Read fname
    with open(fname) as f:
        content = f.readlines()
    f.close()
    headerdict={}
    header=content[0].split(SEPARATOR)
    hcount=0
    for h in header:
        headerdict[h.replace('"','').replace(' ','_').lower().strip().replace('\n', '').replace('\r', '')]=hcount
        hcount=hcount+1

    shortheader=content[1].split(SEPARATOR)
    datatype=content[2].split(SEPARATOR)
    visibility=content[3].split(SEPARATOR)
    columnnumbers=content[4].split(SEPARATOR)


    datastart=5
    j=datastart
    datamatrix=[]
    matrixcount=0
    contentlen=len(content)
    contentlen=contentlen-datastart

    for j in range (0,contentlen):
        datamatrix.append([])
    
    j=datastart

    while j < len(content):
        datamatrix[matrixcount]=content[j].split(SEPARATOR)
        matrixcount += 1
        j += 1

    return datamatrix,headerdict

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
##                  Country Region,county,UA,CA,Borough


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
                line= "*?#? 1"+mkey+","+partskey[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[partskey[0]]+",,,,"+partskey[1]+" (English Region):"+apputils.REVERSE_GOR_TRANSLATION_TABLE[partskey[1]]+",,,,"+partskey[2]+" (London Borough):"+REVERSE_LA_TRANSLATION_TABLE[partskey[2]]
            else:
                # No Borogh
                if (partskey[2] in apputils.REVERSE_COUNTY_TRANSLATION_TABLE):
                    fields=partskey[2]+" (English County):"+apputils.REVERSE_COUNTY_TRANSLATION_TABLE[partskey[2]]+",,"
                elif(partskey[2] in apputils.REVERSE_CA_CODE_TO_NAME_TABLE):
                    fields=",,"+partskey[2]+" (English CA):"+apputils.REVERSE_CA_CODE_TO_NAME_TABLE[partskey[2]]
                else:
                    # UA
                    fields=","+partskey[2]+" (English UA):"+REVERSE_LA_TRANSLATION_TABLE[partskey[2]]+","
                line= "*?#? 2"+mkey+","+partskey[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[partskey[0]]+",,,,"+partskey[1]+" (English Region):"+apputils.REVERSE_GOR_TRANSLATION_TABLE[partskey[1]]+","+fields+","
        else:
            #line= "*?#?"+mkey+","+partskey[0]+":"+",,,,"+partskey[1]+":"+","+partskey[2]+":"+","+partskey[3]+":"
            if (partskey[2] in apputils.REVERSE_CA_CODE_TO_NAME_TABLE):
                line= "*?#? 3"+mkey+","+partskey[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[partskey[0]]+",,,,"+partskey[1]+" (English Region):"+apputils.REVERSE_GOR_TRANSLATION_TABLE[partskey[1]]+",,,"+partskey[2]+" (English CA):"+apputils.REVERSE_CA_CODE_TO_NAME_TABLE[partskey[2]]+","+partskey[3]+" (English District or Borough):"+REVERSE_LA_TRANSLATION_TABLE[partskey[3]]
            else:
                if (partskey[2] in apputils.REVERSE_COUNTY_TRANSLATION_TABLE):
                    fields=partskey[2]+" (English County):"+apputils.REVERSE_COUNTY_TRANSLATION_TABLE[partskey[2]]+",,"
                elif(partskey[2] in apputils.REVERSE_CA_CODE_TO_NAME_TABLE):
                    fields=",,"+partskey[2]+" (English CA):"+apputils.REVERSE_CA_CODE_TO_NAME_TABLE[partskey[2]]
                else:
                    # UA
                    fields=","+partskey[2]+" (English UA):"+REVERSE_LA_TRANSLATION_TABLE[partskey[2]]+","
                line= "*?#? 4"+mkey+","+partskey[0]+":"+apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[partskey[0]]+",,,,"+partskey[1]+" (English Region):"+apputils.REVERSE_GOR_TRANSLATION_TABLE[partskey[1]]+","+fields+","+partskey[3]+" (English District or Borough):"+REVERSE_LA_TRANSLATION_TABLE[partskey[3]]
            
        print line

    return
##                  Country Region,county,UA,CA,Borough

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
print "?#?#? prova.py at line: 74 Dbg-out variable \regionsdict [",str(regionsdict),"]\n";
    
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

for ca_code,ca_name in apputils.CA_CODE_TO_NAME_TABLE.iteritems():
    if (ca_code in apputils.CA_CODE_TO_GOR_TABLE):
        thisregioncode=apputils.CA_CODE_TO_GOR_TABLE[ca_code]
        thisregion=apputils.GOR_TRANSLATION_TABLE[thisregioncode]
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
        if (laname in apputils.LA_TO_CA_NAMES_TABLE):
            countyname=apputils.LA_TO_CA_NAMES_TABLE[laname]
            print "###adding "+laname+" to "+countyname
            countiesdict[countyname].append(laname)
        else:
            thisregion=definitions.LA2_REGION_DICT[laname]
            print "............."+thisregion
            regionsdict[thisregion].append(laname)
    elif (countyname.find("pseudo") < 0):
        countiesdict[countyname].append(laname)
#    else:
        # these are scot/wa/ni names we don't want
        
        # Put LA in regions from LATOCA dict
    for laname, countyname in apputils.LA_TO_CA_NAMES_TABLE.iteritems():
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
#results=getMarkerData()
fname=str(sys.argv[1])
datamatrix,headerdict=readmainsheet(fname)
print "HEADERDICT:"+str(headerdict)
museumdict={}
notinlacount=0
postcode_ptr=headerdict["postcode"]
projid_ptr=headerdict["project_id"]
name_ptr=headerdict["name_of_museum"]
for row in datamatrix:
    museum=row[projid_ptr]
    name=row[name_ptr]
    postcode=row[postcode_ptr].replace(' ','').replace('"','')
    print "?#?#? prova.py at line: 373 Dbg-out variable \postcode [",postcode,"]\n";
    if (postcode in definitions.POSTCODE2_COUNTRY_DICT):
	thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
	if (thiscountry == 'Isle of Man' or thiscountry == 'Channel Islands'):
	    tup=(museum,name)
	    if (not thiscountry in museumdict):
		museumdict[thiscountry]=[]
	    museumdict[thiscountry].append(tup)
	    print "Channel PAPPENDING KEY:"+key
    if (postcode in definitions.POSTCODE2_LA_DICT):
        thiscountry=definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
        #print "?#?#? prova.py at line: 373 Dbg-out variable \thiscountry [",thiscountry,"]\n";
        if (thiscountry == 'England' ):
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
                if (thisla in apputils.LA_TO_CA_NAMES_TABLE):
                    thiscaname=apputils.LA_TO_CA_NAMES_TABLE[thisla]
                    
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
print "MUSEUMDICT:"+str(museumdict)
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
key='Isle of Man'
listofmuseums=museumdict[key]
for m in listofmuseums:
    (museum,name)=m
    mparts=museum.split("/")
    mpartslen=len(mparts)
    mkey=mparts[mpartslen-1]
    print "*?#? 6{},{}:{},,,,,,,,".format(mkey,key,apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[key])

key='Channel Islands'
listofmuseums=museumdict[key]
for m in listofmuseums:
    (museum,name)=m
    mparts=museum.split("/")
    mpartslen=len(mparts)
    mkey=mparts[mpartslen-1]
    print "*?#? 6{},{}:{},,,,,,,,".format(mkey,key,apputils.REVERSE_COUNTRY_TRANSLATION_TABLE[key])


    
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
            
    
