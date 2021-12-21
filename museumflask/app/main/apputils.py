##
# @file
# This module implements : 1. All the methods for accessing the ONS data for locations.
#                          2. All the definitions used in processing the ONS data.
#                          3. The query engine used in search.
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
#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#   $$Author2$:Valeri Katerinchuk, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:valery.katerinchuk@gmail.com, License:GNU GPLv3
#
#We acknowledge the use of the following software under the terms of the specified licences:
#
#Python Flask - https://flask.palletsprojects.com/en/0.12.x/license/
#
#Virtuoso - http://vos.openlinksw.com/owiki/wiki/VOS/VOSLicense
#
#
#
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField,RadioField,SelectField
from wtforms.validators import Required
from flask import request
from flask.views import View
from flask  import Blueprint

from jinja2 import TemplateNotFound


import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import operator
import csv
import sys
import time
import re
import cgi
import copy
import importlib
import inspect
import os
import pickle

from flask import current_app as app

from . import listman
from . import definitions
from app.main import datatypes


REVERSE_COUNTRY_TRANSLATION_TABLE={
    "England":"E92000001",
    "Channel Islands":"L93000001",
    "Isle of Man":"M83000003",
    "Northern Ireland":"N92000002",
    "Scotland":"S92000003",
    "Wales":"W92000004"
    }


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

REVERSE_COUNTY_TRANSLATION_TABLE={
    "Buckinghamshire" :     "E10000002",		
    #    "E10000003"	: "Cambridgeshire",		
    "Cumbria" :     "E10000006",		
    "Derbyshire" :     "E10000007",		
    "Devon" :     "E10000008",		
    "Dorset" :     "E10000009",		
    "East Sussex" :     "E10000011",		
    "Essex" :     "E10000012",		
    "Gloucestershire" :     "E10000013",		
    "Hampshire" :     "E10000014",		
    "Hertfordshire" :     "E10000015",		
    "Kent" :     "E10000016",		
    "Lancashire" :     "E10000017",		
    "Leicestershire" :     "E10000018",		
    "Lincolnshire" :     "E10000019",		
    "Norfolk" :     "E10000020",		
    "Northamptonshire" :     "E10000021",		
    "North Yorkshire" :     "E10000023",		
    "Nottinghamshire" :     "E10000024",		
    "Oxfordshire" :     "E10000025",		
    "Somerset" :     "E10000027",		
    "Staffordshire" :     "E10000028",		
    "Suffolk" :     "E10000029",		
    "Surrey" :     "E10000030",		
    "Warwickshire" :     "E10000031",		
    "West Sussex" :     "E10000032",		
    "Worcestershire" :     "E10000034",		
    "(pseudo) England (UA/MD/LB" :     "E99999999",		
    "(pseudo) Channel Islands" :     "L99999999",		
    "(pseudo) Isle of Man" :     "M99999999",		
    "(pseudo) Northern Ireland" :     "N99999999",		
    "(pseudo) Scotland" :     "S99999999",
    "(pseudo) Wales" : "W99999999"	
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

REVERSE_GOR_TRANSLATION_TABLE={
    "North East":"E12000001",
    "North West":"E12000002",
    "Yorkshire and The Humber":"E12000003",
    "East Midlands":"E12000004",
    "West Midlands":"E12000005",
    "East of England":"E12000006",
    "London":"E12000007",
    "South East":"E12000008",
    "South West":"E12000009",
    "(pseudo) Wales":"W99999999",
    "(pseudo) Scotland":"S99999999",
    "(pseudo) Northern Ireland":"N99999999",
    "(pseudo) Channel Islands":"L99999999",
    "(pseudo) Isle of Man":"M99999999"
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
"E47000001":"Greater Manchester",
"E47000002":"Sheffield City Region",
"E47000003":"West Yorkshire",
"E47000004":"Liverpool City Region",
"E47000005":"North East",
"E47000006":"Tees Valley",
"E47000007":"West Midlands",
"E47000008":"Cambridgeshire and Peterborough",
"E47000009":"West of England"
}

REVERSE_CA_CODE_TO_NAME_TABLE={
    "Greater Manchester" :     "E47000001",
    "Sheffield City Region" :     "E47000002",
    "West Yorkshire" :     "E47000003",
    "Liverpool City Region" :     "E47000004",
    "North East" :     "E47000005",
    "Tees Valley" :     "E47000006",
    "West Midlands" :     "E47000007",  
    "Cambridgeshire and Peterborough" :     "E47000008",
    "West of England":"E47000009"
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
"Bolton":"Greater Manchester",
"Bury":"Greater Manchester",
"Manchester":"Greater Manchester",
"Oldham":"Greater Manchester",
"Rochdale":"Greater Manchester",
"Salford":"Greater Manchester",
"Stockport":"Greater Manchester",
"Tameside":"Greater Manchester",
"Trafford":"Greater Manchester",
"Wigan":"Greater Manchester",
"Barnsley":"Sheffield City Region",
"Doncaster":"Sheffield City Region",
"Rotherham":"Sheffield City Region",
"Sheffield":"Sheffield City Region",
"Bradford":"West Yorkshire",
"Calderdale":"West Yorkshire",
"Kirklees":"West Yorkshire",
"Leeds":"West Yorkshire",
"Wakefield":"West Yorkshire",
"Halton":"Liverpool City Region",
"Knowsley":"Liverpool City Region",
"Liverpool":"Liverpool City Region",
"St. Helens":"Liverpool City Region",
"Sefton":"Liverpool City Region",
"Wirral":"Liverpool City Region",
"County Durham":"North East",
"Northumberland":"North East",
"Newcastle upon Tyne":"North East",
"North Tyneside":"North East",
"South Tyneside":"North East",
"Sunderland":"North East",
"Gateshead":"North East",
"Darlington":"Tees Valley",
"Hartlepool":"Tees Valley",
"Middlesbrough":"Tees Valley",
"Redcar and Cleveland":"Tees Valley",
"Stockton-on-Tees":"Tees Valley",
"Birmingham":"West Midlands",
"Coventry":"West Midlands",
"Dudley":"West Midlands",
"Sandwell":"West Midlands",
"Solihull":"West Midlands",
"Walsall":"West Midlands",
"Wolverhampton":"West Midlands",
"Cambridge":"Cambridgeshire and Peterborough",
"East Cambridgeshire":"Cambridgeshire and Peterborough",
"Fenland":"Cambridgeshire and Peterborough",
"Huntingdonshire":"Cambridgeshire and Peterborough",
"South Cambridgeshire":"Cambridgeshire and Peterborough",
"Peterborough":"Cambridgeshire and Peterborough",
"Bath and North East Somerset":"West of England",
"Bristol, City of":"West of England",
"South Gloucestershire":"West of England"
}


LA_TRANSLATION_TABLE={}
REVERSE_LA_TRANSLATION_TABLE={}

from . import model_to_view
modeltoview=model_to_view.Model_To_View()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Small set of functions to change the appearance of names (strings)
def rotate(l, n):
    return l[n:] + l[:n]

import re

def snake2camel(name):
    return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), name)
 
def snake2camelback(name):
    return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), name)
 
def camel2snake(name):
    return name[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '_' + x.group(0).lower(), name[1:])
 
def camelback2snake(name):
    return re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), name)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose: Reads the ONS csv data creates all dictionaries needed for processing
# Arguments:
# @fname                   name of ons file
# @lafname                 local authority definition file
# @postcode2_county_dict 
# @postcode2_country_dict 
# @postcode2_la_dict 
# @postcode2_region_dict 
# @county2_region_dict 
# @la2_county_dict 
# @la2_region_dict 
# @la_translation_dict 
# @reverse_la_translation_dict 

def readONSPCRepo(fname,
		  lafname,
		  postcode2_county_dict,
		  postcode2_country_dict,
		  postcode2_la_dict,
		  postcode2_region_dict,
		  county2_region_dict,
		  la2_county_dict,
		  la2_region_dict,
		  la_translation_dict,
		  reverse_la_translation_dict
		 
	       ):
    count=0
    with open(lafname) as f:
	content = f.readlines()
    f.close()


    for line in content:
	parts=line.split(',')
	la_translation_dict[parts[0].replace('"','')]=parts[1].replace('"','').replace('\n','').replace('\r','')
	reverse_la_translation_dict[parts[1].replace('"','').replace('\n','').replace('\r','')]=parts[0].replace('"','')
	#print parts[0]+'=='+parts[1]
	
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
	    if (parts[header_dict['laua 11']].replace('"','') in  la_translation_dict):
		la=str(la_translation_dict[parts[header_dict['laua 11']].replace('"','')])
		postcode2_la_dict[spc]=la
	    else:
		postcode2_la_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    keyerrors+=1

	if (len(parts[header_dict['gor 16']].replace('"','')) > 0):
	    if (parts[header_dict['gor 16']].replace('"','') in GOR_TRANSLATION_TABLE):
		gor=str(GOR_TRANSLATION_TABLE[parts[header_dict['gor 16']].replace('"','')])
		postcode2_region_dict[spc]=gor
	    else:
		postcode2_region_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    keyerrors+=1

	county2_region_dict[county]=gor
	la2_county_dict[la]=county
	la2_region_dict[la]=gor
	    
	    
	lc+=1
    f.close()
    print 'key errors were '+str(keyerrors)
    print 'unknown errors were '+str(keyerrors)
    return

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose: Reads district and county names.
# Arguments:
#  
# @fname name of file to read
def readNames(fname):
    adict={}
    lc=0
    with open(fname) as f:
	content = f.readlines()
	while (lc < len(content)):
	    line=content[lc]
	    parts=line.split(',')
	    adict[parts[0].strip()]=parts[1].strip()
            lc+=1
    f.close()
    adict['\\N']='UNKNOWN'
    adict['E99999999']='UNKNOWN'
    adict['L99999999']='UNKNOWN'
    adict['M99999999']='UNKNOWN'
    adict['S99999999']='UNKNOWN'
    adict['N99999999']='Northern Ireland,Belfast'
    adict['W99999999']='Cardiff Central,Wales'
    
    return adict

county_id_2_name_dict=readNames(definitions.BASEDIR+'county.csv')
distr_id_2_name_dict=readNames(definitions.BASEDIR+'distr.csv')

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Sets up reading of the ONS data
# Arguments:
#  
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
		  definitions.LA2_REGION_DICT,
		  LA_TRANSLATION_TABLE,
		  REVERSE_LA_TRANSLATION_TABLE
		  )
    return True
	
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Reads a list of names from a file. Used for configuration
# Arguments:
#  
# @fname name of file to read
def readList(fname):
    alist=[]
    
    with open(fname) as f:
	content = f.readlines()
	for l in content:
	    alist.append(l.strip())
    f.close()
    return alist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def getIntegerAsList(propname):
    # Get all values and put in dict
    # Get the data 
    props=[definitions.NAME_OF_MUSEUM,definitions.PROJECT_ID,propname]
    try:
        results=getMarkerData(props)
    except         Exception, e:
        print str(e)
        return "*** ERROR IN getIntegerAsListSubmenu:"+str(e)
    
    # Sort the data into the dictionary
    rlen=len(results["results"]["bindings"])
    valuesdict={}
    
    for result in results["results"]["bindings"]:
        if ("museum" in result):
            museum=result["museum"]["value"]
            if (propname in result):
                valuesdict[str((result[propname]["value"].replace(' ','')))]=str(result[propname]["value"].replace(' ',''))

    proplist=[]
    for sub in sorted(valuesdict.iterkeys()):
        proplist.append(sub)

    valuesdict=None
    props=None
    results=None
    return proplist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#

## Purpose:Creates an RDF list of values for properties in listnames.
# This is used to allow configurations to be reset after a change
# If a list named xxListReset does not exist create one from the name xxList 
# Called in models ini
# Arguments:
#  
# @listnames conveniece method to create lists for many properties
def createResetLists(listnames):
    for alist in listnames.keys():
        values=listman.getList(listnames[alist]+"Reset")
        if (app.config['DEV_MODE'] == 'F'  or len(values) < 1):
            values=listman.getList(listnames[alist])
            if (len(values) < 1):
                print "createResetLists *** ERROR : no list values for list "+listnames[alist]
                print "createResetLists *** ERROR : Bad things will happen "
            else:
                listman.insertList(listnames[alist]+"Reset",values)
                definitions.RESET_LISTS[listnames[alist]]=listnames[alist]+"Reset"
                definitions.RESET_LISTS_VALUES[listnames[alist]]=values
                
        else:
            definitions.RESET_LISTS_VALUES[listnames[alist]]=values
            definitions.RESET_LISTS[listnames[alist]]=listnames[alist]+"Reset"
            
    return 

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#
## Purpose:Generates a unique list of values for a property from the DB
# Arguments:
#  
# @colname
# @typename
def getValuesForType(colname,typename):
    basename=colname.replace(definitions.DEFNAME,"")
    try:
	results=getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+basename)
    except Exception, e:
	print str(e)
	return render_template('message.html', title="Internal application error",message="Internal Application Error A detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
       

    typemap={}
    typelist=[]

    for res in results["results"]["bindings"]:
	mtype=res[basename]["value"].encode('utf-8')
	if (typename == definitions.DEFINED_HIERTYPE):
	    mtype=mtype.replace(definitions.HTTPSTRING+definitions.RDFDEFURI,'')
	    parts=mtype.split(definitions.HIER_SUBCLASS_SEPARATOR)
	    path=""
	    for p in parts:
		path=path+str(p)
		if (not path in typemap):
		    typemap[str(path)]=True
		path=path+definitions.HIER_SUBCLASS_SEPARATOR
	else:
	    if (not mtype in typemap):
		typemap[str(mtype)]=True

    
    for key  in typemap.keys():
	typelist.append(key)

    typemap=None
    
    return typelist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose: Generates a unique list of values for a column from a map and inserts it in db
# Arguments:
#  
# @colname    property
# @typename   type of property
# @attritypes the map from which the values are taken
def createListOfAllValues(colname,typename,attritypes):
    colcopy=colname.replace(definitions.DEFNAME,definitions.DEFNAME+"Class")
    propertytype=""
    for attributepair in attritypes:
        attribute=attributepair[0].strip()
        propertytype=attributepair[1].strip()
	if (propertytype== colcopy):
	    lname=propertytype+definitions.LISTNAME
	    values=listman.getList(lname)
	    if (len(values) < 1):
		values=getValuesForType(colname,typename)
		listman.insertList(lname,values)
		return 
	
    return 

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#

## Purpose:# Creates a cache for all lists accessibel by name key
#            Called in models ini
# Arguments:
#  
# @listnames list of names for the lists to cache
def createListCache(listnames):
    cache={}
    for alist in listnames.keys():
        values=listman.getList(listnames[alist])
	if (len(values) < 1):
	    print "createListCache *** ERROR : no list values for list "+listnames[alist]
	    print "createListCache *** ERROR : Bad things will happen "
	else:
            cache[alist]=values
    return cache

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get content for a column for all museums
# Arguments:
#  
# @property column name
def getallMuseumsOfProperty(property): 
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])

    colquery=getQueryForCol(property.replace(definitions.PREFIX_WITHCOLON,"").replace(definitions.HASNAME,""),0,False)    
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 


    SELECT DISTINCT  ?museum ?textcontent ?"""+property.replace(definitions.PREFIX_WITHCOLON,"").replace(definitions.HASNAME,"")+"""
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
       ?museum rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
       ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.NAME_OF_MUSEUM+""" ?textcontent .
       """+colquery+""" 
              }
    ORDER BY ASC(?property)
              
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get all properties for a museum with id
# Arguments:
#  
# @shortid museum id
def getRDF():
	idlist = getValuesForType("project_id", "xsd:string")
	#print(idlist)
	dircsv = os.path.dirname(os.path.realpath(__file__))
	print dircsv
	file1 = open(dircsv+"/myfile.txt", "w")
	##file1.write("sod off dickbag")
	file1.write('<?xml version="1.0"?> \n<rdf:RDF\nxmlns:dcterms="http://purl.org/dc/terms/"\nxmlns:owl="http://www.w3.org/2002/07/owl#"\nxmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\nxmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n')
	file1.write('xmlns:xml="http://www.w3.org/XML/1998/namespace"\nxmlns:xsd="http://www.w3.org/2001/XMLSchema#"\nxmlns:prov="http://www.w3.org/ns/prov#"\nxmlns:time="http://www.w3.org/2006/time#"\nxmlns:bbkmm="http://mappingMuseums.dcs.bbk.ac.uk/">\n')

	for item in idlist:
		ycobj = ""
		yoobj = ""
		sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
		query = definitions.RDF_PREFIX_PRELUDE + """
	    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

	   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
	WHERE {VALUES ?x{<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+item+""">} ?x ?y ?z}
 	"""

		sparql.setQuery(query)
		####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
		sparql.setMethod("POST")
		print query
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		dict = results['results']['bindings']
		file1.write('<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Museum/'+item+'">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Museum"/>\n</rdf:type>\n')
		for x in dict:
			subject = (x['x']['value'])
			property = (x['y']['value'])
			object =(x['z']['value'])

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGovernance"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Unknown':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Unknown_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-Private':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-Private_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-Not_for_profit':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-Not_for_profit_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-Unknown':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-Unknown_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Government-Local_Authority':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Government-Local_Authority_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Government-National':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Government-National_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-National_Trust':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-National_Trust_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-National_Trust_for_Scotland':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-National_Trust_for_Scotland_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-Historic_Environment_Scotland':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-Historic_Environment_Scotland_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/University':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_University_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Independent-English_Heritage':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Independent-English_Heritage_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Government-Other':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Government-Other_Entity"/>\n</bbkmm:defGovernance>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Government-Cadw':
					file1.write(
						'<bbkmm:defGovernance>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Governance_Government-Cadw_Entity"/>\n</bbkmm:defGovernance>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defSize"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																													    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																													   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																													WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																												 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_huge':
						file1.write(
							'<bbkmm:defSize>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_huge_Entity"/>\n</bbkmm:defSize>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_large':
						file1.write(
							'<bbkmm:defSize>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_large_Entity"/>\n</bbkmm:defSize>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_medium':
						file1.write(
							'<bbkmm:defSize>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_medium_Entity"/>\n</bbkmm:defSize>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_small':
						file1.write(
							'<bbkmm:defSize>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_small_Entity"/>\n</bbkmm:defSize>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_unknown':
						file1.write(
							'<bbkmm:defSize>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_unknown_Entity"/>\n</bbkmm:defSize>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defSubject_Matter"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Local_Histories':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Local_Histories_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Fossils':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Fossils_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Cars_and_motorbikes':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Cars_and_motorbikes_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Mixed':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Mixed_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Sea_and_seafaring-Boats_and_ships':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Sea_and_seafaring-Boats_and_ships_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Film_Cinema_and_TV':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Film_Cinema_and_TV_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Religious_buildings':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Religious_buildings_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Houses-Large_houses':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Houses-Large_houses_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Ceramics':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Ceramics_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Watermills':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Watermills_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Fine_and_decorative_arts':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Fine_and_decorative_arts_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Literary':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Literary_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Trains_and_railways':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Trains_and_railways_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Medicine_and_health-Professional_association':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Medicine_and_health-Professional_association_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Military':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Military_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Mixed-Encyclopaedic':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Mixed-Encyclopaedic_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Costume_and_textiles':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Costume_and_textiles_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Food_and_drink':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Food_and_drink_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Aviation':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Aviation_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Airforce':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Airforce_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Farming':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Farming_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Toys_and_models':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Toys_and_models_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Roman':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Roman_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Canals':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Canals_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Mixed':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Mixed_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Bicycles':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Bicycles_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Event_or_site':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Event_or_site_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Mining_and_quarrying':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Mining_and_quarrying_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Rural_life':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Rural_life_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Castles_and_forts':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Castles_and_forts_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Ethnic_group':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Ethnic_group_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Cricket':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Cricket_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-School':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-School_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Sea_and_seafaring-Fishing':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Sea_and_seafaring-Fishing_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Photography':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Photography_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Science_and_technology-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Science_and_technology-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Mixed-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Mixed-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Geology':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Geology_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Mixed':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Mixed_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Bunker':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Bunker_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Sea_and_seafaring-Mixed':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Sea_and_seafaring-Mixed_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Music':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Music_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Glass':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Glass_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Metals':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Metals_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Regiment':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Regiment_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Textiles':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Textiles_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Utilities-Water_and_waste':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Utilities-Water_and_waste_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Medieval':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Medieval_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Prehistory':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Prehistory_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Communications':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Communications_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Houses-Small_houses':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Houses-Small_houses_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Science_and_technology-Computing_and_gaming':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Science_and_technology-Computing_and_gaming_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Services-Police':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Services-Police_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Potteries':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Potteries_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Rugby_and_football':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Rugby_and_football_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Shops':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Shops_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Communications-Radio':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Communications-Radio_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Services-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Services-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/War_and_conflict-Navy':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_War_and_conflict-Navy_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Medicine_and_health-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Medicine_and_health-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Services-Fire':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Services-Fire_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Art':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Art_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Mixed':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Mixed_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Textiles':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Textiles_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Herbaria_and_gardening':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Herbaria_and_gardening_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Houses-Medium_houses':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Houses-Medium_houses_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Religion':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Religion_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Mixed-Bygones':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Mixed-Bygones_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Sea_and_seafaring-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Sea_and_seafaring-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Forges':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Forges_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Leisure_and_sport-Fairgrounds_and_amusements':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Leisure_and_sport-Fairgrounds_and_amusements_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Steam_and_engines':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Steam_and_engines_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Utilities-Gas_and_electricity':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Utilities-Gas_and_electricity_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Medicine_and_health-Hospital':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Medicine_and_health-Hospital_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Civic':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Civic_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Palace':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Palace_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Print':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Print_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Transport-Buses_and_trams':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Transport-Buses_and_trams_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Political':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Political_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Industrial_life':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Industrial_life_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Religious':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Religious_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Sea_and_seafaring-Lighthouses':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Sea_and_seafaring-Lighthouses_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Communications-Post':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Communications-Post_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Buildings-Penal':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Buildings-Penal_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Freemasons':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Freemasons_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Crafts':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Crafts_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Music':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Music_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Explorer':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Explorer_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Industry_and_manufacture-Clocks_and_watches':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Industry_and_manufacture-Clocks_and_watches_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Rural_Industry-Windmills':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Rural_Industry-Windmills_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Belief_and_identity-Church_treasuries':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Belief_and_identity-Church_treasuries_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Design':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Design_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Arts-Literature':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Arts-Literature_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Dinosaurs':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Dinosaurs_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Personality-Scientific':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Personality-Scientific_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Archaeology-Greek_and_Egyptian':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Archaeology-Greek_and_Egyptian_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Natural_world-Zoology':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Natural_world-Zoology_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Communications-Other':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Communications-Other_Entity"/>\n</bbkmm:defSubject_Matter>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Services-RNLI':
					file1.write(
						'<bbkmm:defSubject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Subject_Matter_Services-RNLI_Entity"/>\n</bbkmm:defSubject_Matter>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDOMUS_identifier"):
				file1.write(
					'<bbkmm:hasDOMUS_identifier>\n<rdf:Description>\n<xsd:int>'+object+'</xsd:int>\n</rdf:Description>\n</bbkmm:hasDOMUS_identifier>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defDOMUS_Subject_Matter"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																									    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																									   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																									WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																								 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_agriculture':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_agriculture_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_archaeology':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_archaeology_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_archives':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_archives_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_arms_and_armour':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_arms_and_armour_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_biology_and_natural_history':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_biology_and_natural_history_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_costume_and_textiles':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_costume_and_textiles_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_decorative_and_applied_arts':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_decorative_and_applied_arts_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_ethnography':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_ethnography_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_fine_art':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_fine_art_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_geology':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_geology_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_maritime':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_maritime_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_medicine':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_medicine_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_military':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_military_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_mixed_collection':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_mixed_collection_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_music':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_music_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_oral_history':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_oral_history_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_personalia':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_personalia_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_photography':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_photography_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_science_and_industry':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_science_and_industry_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_social_history':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_social_history_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/DOMUS_Subject_Matter_transport':
						file1.write(
							'<bbkmm:defDOMUS_Subject_Matter>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/DOMUS_Subject_Matter_transport_Entity"/>\n</bbkmm:defDOMUS_Subject_Matter>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defSize_prov"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																									    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																									   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																									WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																								 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_ace_size_designation':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_ace_size_designation_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_aim_size_designation':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_aim_size_designation_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_babbidge_ewles_and_smith_':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_babbidge_ewles_and_smith__Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_domus':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_domus_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mafam':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mafam_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mafam_year_stated':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mafam_year_stated_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mm':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mm_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mm_manual_estimate_':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mm_manual_estimate__Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mm_prediction_random_forest':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mm_prediction_random_forest_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_national_trust_annual_report_':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_national_trust_annual_report__Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_nilmvn':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_nilmvn_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_scottish_national_audit':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_scottish_national_audit_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_unknown':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_unknown_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_visitbritain':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_visitbritain_Entity"/>\n</bbkmm:defSize_prov>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Size_prov_mmint':
						file1.write(
							'<bbkmm:defSize_prov>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Size_prov_mmint_Entity"/>\n</bbkmm:defSize_prov>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_services"):
				file1.write('<bbkmm:hasDeprivation_index_services>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_services_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_services>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_income"):
				file1.write('<bbkmm:hasDeprivation_index_income>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_income_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_income>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_housing"):
				file1.write('<bbkmm:hasDeprivation_index_housing>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_housing_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_housing>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_health"):
				file1.write('<bbkmm:hasDeprivation_index_health>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_health_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_health>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_employment"):
				file1.write('<bbkmm:hasDeprivation_index_employment>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_employment_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_employment>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_education"):
				file1.write('<bbkmm:hasDeprivation_index_education>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_education_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_education>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index_crime"):
				file1.write('<bbkmm:hasDeprivation_index_crime>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_crime_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index_crime>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasDeprivation_index"):
				file1.write('<bbkmm:hasDeprivation_index>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Deprivation_index_'+object+'_Entity"/>\n</bbkmm:hasDeprivation_index>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_supergroup_name_long"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																									    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																									   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																									WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																								 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rAffluent_England':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rAffluent_England_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rBusiness_Education_and_Heritage_Centres':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rBusiness_Education_and_Heritage_Centres_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rCountryside_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rCountryside_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rEthnically_Diverse_Metropolitan_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rEthnically_Diverse_Metropolitan_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rLondon_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rLondon_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rServices_and_Industrial_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rServices_and_Industrial_Legacy_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rTown_and_Country_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rTown_and_Country_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_rUrban_Settlements':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_name_long_rUrban_Settlements_Entity"/>\n</bbkmm:defGeodemographic_supergroup_name_long>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_supergroup_code"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																					    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																					   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																					WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																				 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					print object
					if object == '1r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_1r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '2r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_2r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '3r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_3r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '4r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_4r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '5r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_5r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '6r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_6r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '7r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_7r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')

					if object == '8r':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_code_8r_Entity"/>\n</bbkmm:defGeodemographic_supergroup_code>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_supergroup"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																													    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																													   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																													WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																												 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Affluent_England':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Affluent_England_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Business_Education_and_Heritage_Centres':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Business_Education_and_Heritage_Centres_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Countryside_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Countryside_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Ethnically_Diverse_Metropolitan_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Ethnically_Diverse_Metropolitan_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_London_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_London_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Services_and_Industrial_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Services_and_Industrial_Legacy_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Town_and_Country_Living':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Town_and_Country_Living_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_Urban_Settlements':
						file1.write(
							'<bbkmm:defGeodemographic_supergroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_supergroup_Urban_Settlements_Entity"/>\n</bbkmm:defGeodemographic_supergroup>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_subgroup_name_long"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																									    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																									   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																									WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																								 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arCountry_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arCountry_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arEthnically_Diverse_Metropolitan__Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arEthnically_Diverse_Metropolitan__Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arIndustrial_and_Multiethnic':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arIndustrial_and_Multiethnic_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arLarger_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arLarger_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arLondon_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arLondon_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arManufacturing_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arManufacturing_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arMining_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arMining_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arOlder_Farming_Communities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arOlder_Farming_Communities_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arRuralUrban_Fringe':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arRuralUrban_Fringe_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arService_Economy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arService_Economy_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arSparse_English_and_Welsh_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arSparse_English_and_Welsh_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_arUrban_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_arUrban_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brAffluent_rural':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brAffluent_rural_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brAgeing_Coastal_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brAgeing_Coastal_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brCity_Periphery':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brCity_Periphery_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brExpanding_Areas':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brExpanding_Areas_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brNorthern_Ireland_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brNorthern_Ireland_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brRural_Growth_Areas':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brRural_Growth_Areas_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brScottish_Industrial_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brScottish_Industrial_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brSeaside_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brSeaside_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_brUniversity_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_brUniversity_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_crProsperous_Semirural':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_crProsperous_Semirural_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_crProsperous_Towns':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_crProsperous_Towns_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_crScottish_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_name_long_crScottish_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup_name_long>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_subgroup_code"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																	    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																	   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																	WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == '2a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_2a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '7c2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_7c2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '4a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_4a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '3a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_3a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '1b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_1b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '7a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_7a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '3a2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_3a2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '2b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_2b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '5a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_5a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '8a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_8a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '1a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_1a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '8b2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_8b2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '3b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_3b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '1b2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_1b2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '8b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_8b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '3c1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_3c1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '6b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_6b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '6a1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_6a1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '6a2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_6a2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '6a3r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_6a3r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '3b2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_3b2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '7b1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_7b1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '8a2r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_8a2r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')

					if object == '7c1r':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_code_7c1r_Entity"/>\n</bbkmm:defGeodemographic_subgroup_code>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_subgroup"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																					    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																					   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																					WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																				 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Affluent_rural':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Affluent_rural_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Ageing_Coastal_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Ageing_Coastal_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_City_Periphery':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_City_Periphery_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Country_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Country_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Ethnically_Diverse_Metropolitan__Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Ethnically_Diverse_Metropolitan__Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Expanding_Areas':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Expanding_Areas_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Industrial_and_Multiethnic':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Industrial_and_Multiethnic_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Larger_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Larger_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_London_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_London_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Manufacturing_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Manufacturing_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Mining_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Mining_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Northern_Ireland_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Northern_Ireland_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Older_Farming_Communities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Older_Farming_Communities_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Prosperous_Semirural':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Prosperous_Semirural_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Prosperous_Towns':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Prosperous_Towns_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_RuralUrban_Fringe':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_RuralUrban_Fringe_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Rural_Growth_Areas':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Rural_Growth_Areas_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Scottish_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Scottish_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Scottish_Industrial_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Scottish_Industrial_Legacy_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Seaside_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Seaside_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Service_Economy':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Service_Economy_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Sparse_English_and_Welsh_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Sparse_English_and_Welsh_Countryside_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_University_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_University_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_Urban_Living':
						file1.write(
							'<bbkmm:defGeodemographic_subgroup>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_subgroup_Urban_Living_Entity"/>\n</bbkmm:defGeodemographic_subgroup>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_group_name_long"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
																	    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																	   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																	WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
																 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arCountry_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arCountry_Living_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arEnglish_and_Welsh_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arEnglish_and_Welsh_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arEthnically_Diverse_Metropolitan__Living':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arEthnically_Diverse_Metropolitan__Living_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arLarger_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arLarger_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arLondon_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arLondon_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arManufacturing_Traits':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arManufacturing_Traits_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arRuralUrban_Fringe':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arRuralUrban_Fringe_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_arServices_Manufacturing_and_Mining_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_arServices_Manufacturing_and_Mining_Legacy_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brNorthern_Ireland_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brNorthern_Ireland_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brRemoter_Coastal_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brRemoter_Coastal_Living_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brScottish_Industrial_Heritage':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brScottish_Industrial_Heritage_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brSuburban_Traits':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brSuburban_Traits_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brThriving_Rural':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brThriving_Rural_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_brUniversity_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_brUniversity_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_crScottish_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_crScottish_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_crTown_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group_name_long>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_name_long_crTown_Living_Entity"/>\n</bbkmm:defGeodemographic_group_name_long>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_group_code"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
													    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

													   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
													WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
												 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == '2ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_2ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '7cr':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_7cr_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '4ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_4ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '3ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_3ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '1br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_1br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '7ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_7ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '2br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_2br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '5ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_5ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '8ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_8ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '1ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_1ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '8br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_8br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '3br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_3br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '3cr':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_3cr_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '6br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_6br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '6ar':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_6ar_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')

					if object == '7br':
						file1.write(
							'<bbkmm:defGeodemographic_group_code>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_code_7br_Entity"/>\n</bbkmm:defGeodemographic_group_code>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defGeodemographic_group"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
									    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

									   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
									WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
								 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Country_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Country_Living_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_English_and_Welsh_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_English_and_Welsh_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Ethnically_Diverse_Metropolitan__Living':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Ethnically_Diverse_Metropolitan__Living_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Larger_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Larger_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_London_Cosmopolitan':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_London_Cosmopolitan_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Manufacturing_Traits':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Manufacturing_Traits_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Northern_Ireland_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Northern_Ireland_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Remoter_Coastal_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Remoter_Coastal_Living_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_RuralUrban_Fringe':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_RuralUrban_Fringe_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Scottish_Countryside':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Scottish_Countryside_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Scottish_Industrial_Heritage':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Scottish_Industrial_Heritage_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Services_Manufacturing_and_Mining_Legacy':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Services_Manufacturing_and_Mining_Legacy_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Suburban_Traits':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Suburban_Traits_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Thriving_Rural':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Thriving_Rural_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_Town_Living':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_Town_Living_Entity"/>\n</bbkmm:defGeodemographic_group>\n')
					if object == 'http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_University_Towns_and_Cities':
						file1.write(
							'<bbkmm:defGeodemographic_group>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Geodemographic_group_University_Towns_and_Cities_Entity"/>\n</bbkmm:defGeodemographic_group>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToEnglish_District_or_Borough"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Dorset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Dorset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Breckland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Breckland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bath_and_North_East_Somerset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bath_and_North_East_Somerset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Doncaster':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Doncaster_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Kirklees':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Kirklees_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Gloucestershire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Gloucestershire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Test_Valley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Test_Valley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Westminster':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Westminster_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Castle_Point':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Castle_Point_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Maldon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Maldon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sefton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sefton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Dorset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Dorset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hillingdon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hillingdon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Cambridgeshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Cambridgeshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Norfolk':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Norfolk_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Teignbridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Teignbridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Staffordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Staffordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Enfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Enfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Aylesbury_Vale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Aylesbury_Vale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/High_Peak':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_High_Peak_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hinckley_and_Bosworth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hinckley_and_Bosworth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Basingstoke_and_Deane':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Basingstoke_and_Deane_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Birmingham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Birmingham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Weymouth_and_Portland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Weymouth_and_Portland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Waverley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Waverley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Cheltenham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Cheltenham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Northumberland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Northumberland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wycombe':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wycombe_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Cotswold':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Cotswold_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Somerset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Somerset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Redcar_and_Cleveland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Redcar_and_Cleveland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Vale_of_White_Horse':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Vale_of_White_Horse_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Pendle':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Pendle_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Devon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Devon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Hams':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Hams_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Eden':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Eden_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wealden':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wealden_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Torridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Torridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lichfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lichfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Manchester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Manchester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Suffolk_Coastal':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Suffolk_Coastal_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tandridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tandridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Northamptonshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Northamptonshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Warwick':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Warwick_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sedgemoor':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sedgemoor_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Derbyshire_Dales':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Derbyshire_Dales_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/New_Forest':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_New_Forest_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Gloucester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Gloucester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Craven':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Craven_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bolton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bolton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Burnley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Burnley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Braintree':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Braintree_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Stafford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Stafford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Kesteven':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Kesteven_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Waveney':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Waveney_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rotherham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rotherham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/St_Albans':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_St_Albans_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Dorset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Dorset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Gateshead':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Gateshead_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Dudley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Dudley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Cambridgeshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Cambridgeshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/StratfordonAvon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_StratfordonAvon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Darlington':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Darlington_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/City_of_London':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_City_of_London_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Carlisle':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Carlisle_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Selby':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Selby_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Greenwich':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Greenwich_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Oldham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Oldham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Somerset':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Somerset_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Oadby_and_Wigston':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Oadby_and_Wigston_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wakefield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wakefield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Southwark':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Southwark_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hammersmith_and_Fulham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hammersmith_and_Fulham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Liverpool':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Liverpool_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bassetlaw':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bassetlaw_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/King_s_Lynn_and_West_Norfolk':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_King_s_Lynn_and_West_Norfolk_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Richmondshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Richmondshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Leeds':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Leeds_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sunderland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sunderland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Hertfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Hertfordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Watford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Watford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hertsmere':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hertsmere_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Devon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Devon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Horsham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Horsham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/NewcastleunderLyme':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_NewcastleunderLyme_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wyre_Forest':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wyre_Forest_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lancaster':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lancaster_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Harrow':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Harrow_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Trafford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Trafford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Richmon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Richmon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Great_Yarmouth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Great_Yarmouth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Babergh':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Babergh_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Fylde':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Fylde_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hyndburn':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hyndburn_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lewes':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lewes_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Salford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Salford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Chichester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Chichester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Daventry':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Daventry_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hartlepool':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hartlepool_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Cambridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Cambridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lambeth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lambeth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Staffordshire_Moorlands':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Staffordshire_Moorlands_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mendip':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mendip_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rother':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rother_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Oxfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Oxfordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mid_Sussex':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mid_Sussex_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/St_Edmundsbury':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_St_Edmundsbury_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ribble_Valley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ribble_Valley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Thanet':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Thanet_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Calderdale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Calderdale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Purbeck':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Purbeck_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Warwickshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Warwickshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Derbyshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Derbyshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hastings':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hastings_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tonbridge_and_Malling':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tonbridge_and_Malling_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Dover':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Dover_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mid_Suffolk':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mid_Suffolk_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Eastbourne':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Eastbourne_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Harrogate':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Harrogate_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rochford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rochford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Guildford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Guildford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Chesterfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Chesterfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Chiltern':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Chiltern_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Colchester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Colchester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Walsall':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Walsall_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Oxfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Oxfordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Stockport':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Stockport_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Broadland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Broadland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Nuneaton_and_Bedworth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Nuneaton_and_Bedworth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Northampton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Northampton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Lindsey':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Lindsey_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_West_Leicestershire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_West_Leicestershire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Holland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Holland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Kettering':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Kettering_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/County_Durham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_County_Durham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Tyneside':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Tyneside_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tameside':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tameside_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Chorley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Chorley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wigan':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wigan_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Lakeland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Lakeland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Preston':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Preston_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Barnet':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Barnet_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Camden':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Camden_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bromley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bromley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Kensingto':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Kensingto_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rushmoor':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rushmoor_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Winchester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Winchester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Norfolk':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Norfolk_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Hertfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Hertfordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Arun':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Arun_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/East_Hampshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_East_Hampshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Cherwell':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Cherwell_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bexley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bexley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ashford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ashford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Kensington_and_Chelsea':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Kensington_and_Chelsea_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Uttlesford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Uttlesford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Devon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Devon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bromsgrove':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bromsgrove_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wolverhampton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wolverhampton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Barnsley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Barnsley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sheffield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sheffield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hambleton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hambleton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ryedale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ryedale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Swale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Swale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Dacorum':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Dacorum_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Melton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Melton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tower_Hamlets':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tower_Hamlets_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Islington':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Islington_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sandwell':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sandwell_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rossendale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rossendale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Basildon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Basildon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Chelmsford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Chelmsford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Solihull':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Solihull_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Amber_Valley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Amber_Valley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Stroud':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Stroud_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hounslow':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hounslow_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lincoln':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lincoln_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Taunton_Deane':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Taunton_Deane_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Haringey':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Haringey_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Northamptonshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Northamptonshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bradford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bradford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Fareham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Fareham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Lindsey':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Lindsey_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Scarborough':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Scarborough_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Newark_and_Sherwood':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Newark_and_Sherwood_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Boston':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Boston_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/StocktononTees':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_StocktononTees_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Middlesbrough':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Middlesbrough_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bury':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bury_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wirral':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wirral_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Ribble':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Ribble_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Brentwood':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Brentwood_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tendring':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tendring_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Elmbridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Elmbridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Epsom_and_Ewell':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Epsom_and_Ewell_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Canterbury':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Canterbury_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Peterborough':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Peterborough_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Eastleigh':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Eastleigh_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Redditch':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Redditch_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Staffordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Staffordshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Christchurch':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Christchurch_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Maidstone':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Maidstone_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Shepway':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Shepway_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Gedling':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Gedling_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Huntingdonshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Huntingdonshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Allerdale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Allerdale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Harborough':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Harborough_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wychavon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wychavon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Forest_of_Dean':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Forest_of_Dean_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Norwich':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Norwich_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Corby':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Corby_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Coventry':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Coventry_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Broxtowe':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Broxtowe_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Bolsover':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Bolsover_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Charnwood':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Charnwood_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Halton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Halton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Croydon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Croydon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Runnymede':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Runnymede_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tunbridge_Wells':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tunbridge_Wells_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Fenland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Fenland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ipswich':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ipswich_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Oxford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Oxford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sevenoaks':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sevenoaks_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Crawley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Crawley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Exeter':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Exeter_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mid_Devon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mid_Devon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hackney':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hackney_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Sutton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Sutton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Kesteven':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Kesteven_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Surrey_Heath':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Surrey_Heath_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Gosport':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Gosport_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Kingston_upon_Thames':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Kingston_upon_Thames_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wellingborough':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wellingborough_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Erewash':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Erewash_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Newcastle_upon_Tyne':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Newcastle_upon_Tyne_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rochdale':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rochdale_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/BarrowinFurness':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_BarrowinFurness_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mole_Valley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mole_Valley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Dartford':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Dartford_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Epping_Forest':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Epping_Forest_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Havant':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Havant_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/South_Bucks':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_South_Bucks_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Worcester':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Worcester_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Richmond_upon_Thames':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Richmond_upon_Thames_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Havering':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Havering_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rushcliffe':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rushcliffe_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wyre':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wyre_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Copeland':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Copeland_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Brent':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Brent_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Gravesham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Gravesham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Harlow':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Harlow_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tewkesbury':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tewkesbury_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Rugby':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Rugby_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Welwyn_Hatfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Welwyn_Hatfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Lewisham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Lewisham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Stevenage':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Stevenage_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Adur':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Adur_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Mansfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Mansfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Broxbourne':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Broxbourne_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Malvern_Hills':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Malvern_Hills_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Wandsworth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Wandsworth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ealing':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ealing_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Newham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Newham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Merton':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Merton_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Forest_Heath':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Forest_Heath_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Cannock_Chase':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Cannock_Chase_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Worthing':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Worthing_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Blaby':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Blaby_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Ashfield':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Ashfield_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Knowsley':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Knowsley_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_Tyneside':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_Tyneside_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Stratford-on-Avon':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Stratford-on-Avon_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/St_Helens':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_St_Helens_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/North_East_Derbyshire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_North_East_Derbyshire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/West_Lancashire':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_West_Lancashire_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Redbridge':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Redbridge_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/C':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_C_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Reigate_and_Banstead':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Reigate_and_Banstead_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Spelthorne':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Spelthorne_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Tamworth':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Tamworth_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Woking':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Woking_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Three_Rivers':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Three_Rivers_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Waltham_Forest':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Waltham_Forest_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Barking_and_Dagenham':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Barking_and_Dagenham_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hart':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hart_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/Hammersmi':
					file1.write(
						'<bbkmm:PartOfEnglish_District_or_Borough>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_District_or_Borough_Hammersmi_Entity"/>\n</bbkmm:PartOfEnglish_District_or_Borough>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToEnglish_CA"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/West_of_England':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_West_of_England_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/Sheffield_City_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_Sheffield_City_Region_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/West_Yorkshire':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_West_Yorkshire_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/Liverpool_City_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_Liverpool_City_Region_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/Cambridgeshire_and_Peterborough':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_Cambridgeshire_and_Peterborough_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/West_Midlands':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_West_Midlands_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/North_East':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_North_East_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/Tees_Valley':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_Tees_Valley_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/Greater_Manchester':
					file1.write(
						'<bbkmm:PartOfEnglish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_CA_Greater_Manchester_Entity"/>\n</bbkmm:PartOfEnglish_CA>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToEnglish_County"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Dorset':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Dorset_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Norfolk':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Norfolk_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Hampshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Hampshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Essex':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Essex_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Devon':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Devon_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Staffordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Staffordshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Buckinghamshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Buckinghamshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Derbyshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Derbyshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Leicestershire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Leicestershire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Surrey':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Surrey_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Gloucestershire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Gloucestershire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Somerset':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Somerset_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Oxfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Oxfordshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Lancashire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Lancashire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Cumbria':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Cumbria_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/East_Sussex':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_East_Sussex_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Suffolk':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Suffolk_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Northamptonshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Northamptonshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Warwickshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Warwickshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/North_Yorkshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_North_Yorkshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Lincolnshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Lincolnshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Hertfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Hertfordshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Nottinghamshire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Nottinghamshire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/West_Sussex':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_West_Sussex_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Worcestershire':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Worcestershire_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/Kent':
					file1.write(
						'<bbkmm:PartOfEnglish_County>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_County_Kent_Entity"/>\n</bbkmm:PartOfEnglish_County>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToEnglish_UA"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Southampton':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Southampton_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/North_Somerset':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_North_Somerset_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Swindon':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Swindon_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Wiltshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Wiltshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/StokeonTrent':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_StokeonTrent_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Isle_of_Wight':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Isle_of_Wight_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Bournemouth':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Bournemouth_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Cheshire_West_and_Chester':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Cheshire_West_and_Chester_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Brighton_and_Hove':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Brighton_and_Hove_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Herefordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Herefordshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Cornwall':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Cornwall_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/North_East_Lincolnshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_North_East_Lincolnshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Telford_and_Wrekin':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Telford_and_Wrekin_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/York':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_York_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Bedford':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Bedford_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Reading':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Reading_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/East_Riding_of_Yorkshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_East_Riding_of_Yorkshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Shropshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Shropshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Blackburn_with_Darwen':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Blackburn_with_Darwen_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Nottingham':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Nottingham_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Leicester':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Leicester_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Medway':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Medway_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Central_Bedfordshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Central_Bedfordshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Bristol':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Bristol_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Torbay':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Torbay_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Windsor_and_Maidenhead':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Windsor_and_Maidenhead_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/SouthendonSea':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_SouthendonSea_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/West_Berkshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_West_Berkshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/North_Lincolnshire':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_North_Lincolnshire_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Cheshire_East':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Cheshire_East_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Wokingham':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Wokingham_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Kingston_upon_Hull':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Kingston_upon_Hull_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Milton_Keynes':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Milton_Keynes_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Blackpool':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Blackpool_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Portsmouth':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Portsmouth_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Stoke-on-Trent':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Stoke-on-Trent_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Thurrock':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Thurrock_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Warrington':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Warrington_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Plymouth':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Plymouth_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Derby':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Derby_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Poole':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Poole_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Isles_of_Scilly':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Isles_of_Scilly_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Luton':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Luton_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Rutland':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Rutland_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Bracknell_Forest':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Bracknell_Forest_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/Slough':
					file1.write(
						'<bbkmm:PartOfEnglish_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_UA_Slough_Entity"/>\n</bbkmm:PartOfEnglish_UA>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToEnglish_Region"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_South_East_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_South_West_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_East_of_England_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_Yorkshire_and_The_Humber_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_West_Midlands_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_London_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_London_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_North_West_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_East_Midlands_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_North_East_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_West_Midlands_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_South_West_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_East_Midlands_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_South_East_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_Yorkshire_and_The_Humber_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_East_of_England_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_North_West_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East_English_Region':
					file1.write(
						'<bbkmm:PartOfEnglish_Region>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/English_Region_North_East_English_Region_Entity"/>\n</bbkmm:PartOfEnglish_Region>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToScottish_Council_Area"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Moray':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Moray_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Highland':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Highland_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Shetland_Islands':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Shetland_Islands_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Perth_and_Kinross':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Perth_and_Kinross_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/South_Lanarkshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_South_Lanarkshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Stirling':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Stirling_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Fife':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Fife_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/City_of_Edinburgh':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_City_of_Edinburgh_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Midlothian':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Midlothian_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Na_hEileanan_Siar':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Na_hEileanan_Siar_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Scottish_Borders':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Scottish_Borders_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/South_Ayrshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_South_Ayrshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Ayrshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Ayrshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Argyll_and_Bute':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Argyll_and_Bute_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/North_Lanarkshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_North_Lanarkshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Aberdeenshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Aberdeenshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Orkney_Islands':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Orkney_Islands_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Dundee_City':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Dundee_City_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Renfrewshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Renfrewshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Dumfries_and_Galloway':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Dumfries_and_Galloway_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/North_Ayrshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_North_Ayrshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Glasgow_City':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Glasgow_City_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Clackmannanshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Clackmannanshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Aberdeen_City':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Aberdeen_City_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/West_Lothian':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_West_Lothian_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Angus':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Angus_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Dunbartonshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Dunbartonshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Falkirk':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Falkirk_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/West_Dunbartonshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_West_Dunbartonshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Lothian':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Lothian_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Inverclyde':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Inverclyde_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Glasgow_City_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Glasgow_City_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/West_Lothian_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_West_Lothian_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Aberdeenshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Aberdeenshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Na_h-Eileanan_Siar_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Na_h-Eileanan_Siar_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Na_h-Eileanan_Siar':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Na_h-Eileanan_Siar_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/North_Ayrshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_North_Ayrshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Perth_and_Kinross_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Perth_and_Kinross_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Highland_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Highland_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Moray_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Moray_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/City_of_Edinburgh_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_City_of_Edinburgh_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Aberdeen_City_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Aberdeen_City_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Dumfries_and_Galloway_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Dumfries_and_Galloway_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/West_Dunbartonshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_West_Dunbartonshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Scottish_Borders_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Scottish_Borders_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Ayrshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Ayrshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Renfrewshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Renfrewshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/East_Renfrewshire':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_East_Renfrewshire_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Fife_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Fife_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Renfrewshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Renfrewshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Falkirk_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Falkirk_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Argyll_and_Bute_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Argyll_and_Bute_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/South_Ayrshire_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_South_Ayrshire_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/Shetland_Islands_Scottish_Council_Area':
					file1.write(
						'<bbkmm:PartOfScottish_CA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Scottish_CA_Shetland_Islands_Scottish_Council_Area_Entity"/>\n</bbkmm:PartOfScottish_CA>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToNI_Loc_Gov_District"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Ards_and_North_Down':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Ards_and_North_Down_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Fermanagh_and_Omagh':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Fermanagh_and_Omagh_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Mid_Ulster':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Mid_Ulster_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Belfast':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Belfast_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Lisburn_and_Castlereagh':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Lisburn_and_Castlereagh_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Mid_and_East_Antrim':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Mid_and_East_Antrim_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Armagh_City':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Armagh_City_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Causeway_Coast_and_Glens':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Causeway_Coast_and_Glens_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Mid_and_East_Antrim_NI_Loc_Gov_District':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Mid_and_East_Antrim_NI_Loc_Gov_District_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Derry_City_and_Strabane':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Derry_City_and_Strabane_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Newry':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Newry_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Armagh_City_NI_Loc_Gov_District':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Armagh_City_NI_Loc_Gov_District_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Antrim_and_Newtownabbey':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Antrim_and_Newtownabbey_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Mid_Ulster_NI_Loc_Gov_District':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Mid_Ulster_NI_Loc_Gov_District_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Belfast_NI_Loc_Gov_District':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Belfast_NI_Loc_Gov_District_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/Fermanagh_and_Omagh_NI_Loc_Gov_District':
					file1.write(
						'<bbkmm:PartOfNI_Loc_Gov_District>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/NI_Loc_Gov_District_Fermanagh_and_Omagh_NI_Loc_Gov_District_Entity"/>\n</bbkmm:PartOfNI_Loc_Gov_District>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToWelsh_UA"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Gwynedd':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Gwynedd_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Isle_of_Anglesey':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Isle_of_Anglesey_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Carmarthenshire':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Carmarthenshire_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Denbighshire':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Denbighshire_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Powys':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Powys_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Conwy':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Conwy_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Wrexham':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Wrexham_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Swansea':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Swansea_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Pembrokeshire':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Pembrokeshire_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Ceredigion_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Ceredigion_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Ceredigion':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Ceredigion_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Flintshire':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Flintshire_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Neath_Port_Talbot':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Neath_Port_Talbot_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Monmouthshire_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Monmouthshire_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Monmouthshire':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Monmouthshire_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Blaenau_Gwent':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Blaenau_Gwent_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Torfaen':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Torfaen_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Caerphilly':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Caerphilly_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Vale_of_Glamorgan':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Vale_of_Glamorgan_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Cardiff':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Cardiff_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Rhondda_Cynon_Taf':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Rhondda_Cynon_Taf_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Merthyr_Tydfil':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Merthyr_Tydfil_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Bridgend':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Bridgend_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Newport':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Newport_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Cardiff_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Cardiff_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Blaenau_Gwent_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Blaenau_Gwent_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Swansea_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Swansea_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/Wrexham_Welsh_UA':
					file1.write('<bbkmm:PartOfWelsh_UA>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Welsh_UA_Wrexham_Welsh_UA_Entity"/>\n</bbkmm:PartOfWelsh_UA>\n')

			if (property == "http://bbk.ac.uk/MuseumMapProject/def/refersToCountry"):
				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/England':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_England_Entity"/>\n</bbkmm:PartOfCountry>\n')


				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Wales':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_Wales_Entity"/>\n</bbkmm:PartOfCountry>\n')


				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Northern_Ireland':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_Northern_Ireland_Entity"/>\n</bbkmm:PartOfCountry>\n')


				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Scotland':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_Scotland_Entity"/>\n</bbkmm:PartOfCountry>\n')


				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Isle_of_Man':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_Isle_of_Man_Entity"/>\n</bbkmm:PartOfCountry>\n')


				if object == 'http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Channel_Islands':
					file1.write('<bbkmm:PartOfCountry>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Country_Channel_Islands_Entity"/>\n</bbkmm:PartOfCountry>\n')



			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defPrimary_provenance_of_data"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
					    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

					   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
					WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
				 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")
				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_MDN'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_MDN_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_Misc'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_Misc_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_MusCal'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_MusCal_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_aimM'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_aimM_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_aimNM'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_aimNM_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_hud'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_hud_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_ace'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_ace_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_aim'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_aim_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_domus'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_domus_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_fcm'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_fcm_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_hha'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_hha_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_mald'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_mald_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_mgs'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_mgs_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_misc'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_misc_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_musassoc'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_musassoc_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_nimc'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_nimc_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_New'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_New_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
					if (object == 'http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_wiki'):
						file1.write('<bbkmm:Primary_provenance_of_data>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Primary_provenance_of_data_wiki_Entity"/>\n</bbkmm:Primary_provenance_of_data>\n')
						break
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defAccreditation"):
				sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
				query = definitions.RDF_PREFIX_PRELUDE + """
					    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

					   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
					WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
				 	"""

				sparql.setQuery(query)
				####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
				sparql.setMethod("POST")

				sparql.setReturnFormat(JSON)
				resultsacrr = sparql.query().convert()
				dict = resultsacrr['results']['bindings']

				for x in dict:
					subject = (x['x']['value'])
					property = (x['y']['value'])
					object = (x['z']['value'])
					if(object=='Accredited'):
						file1.write('<bbkmm:defAccreditation>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Accreditation_Accredited_Entity"/>\n</bbkmm:defAccreditation>\n')
						break
					if (object == 'Unaccredited'):
						file1.write('<bbkmm:defAccreditation>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/Accreditation_Unaccredited_Entity"/>\n</bbkmm:defAccreditation>\n')
						break
			if(property=="http://bbk.ac.uk/MuseumMapProject/def/hasNotes"):
				file1.write('<bbkmm:hasNotes>\n<rdf:Description>\n<xsd:string>'+object+'</xsd:string>\n</rdf:Description>\n</bbkmm:hasNotes>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasPostcode"):
				file1.write('<bbkmm:hasPostcode>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasPostcode>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasAddress_line_1"):
				file1.write('<bbkmm:hasAddress_line_1>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasAddress_line_1>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasAddress_line_2"):
				file1.write('<bbkmm:hasAddress_line_2>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasAddress_line_2>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasAddress_line_3"):
				file1.write('<bbkmm:hasAddress_line_3>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasAddress_line_3>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasName_of_museum"):
				file1.write('<bbkmm:hasName_of_museum>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasName_of_museum>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasTown_or_City"):
				file1.write('<bbkmm:hasTown_or_City>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasTown_or_City>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasproject_id"):
				file1.write('<bbkmm:hasproject_id>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasproject_id>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/hasIdentifier_used_in_source_database"):
				file1.write('<bbkmm:hasIdentifier_used_in_source_database>\n<rdf:Description>\n<xsd:string>' + object + '</xsd:string>\n</rdf:Description>\n</bbkmm:hasIdentifier_used_in_source_database>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed"):
				ycobj=object
				file1.write('<bbkmm:defRangeYear_closed>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange/'+item+'_closed"/>\n</bbkmm:defRangeYear_closed>\n')
			if (property == "http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened"):
				yoobj=object
				file1.write('<bbkmm:defRangeYear_opened>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange/'+item+'_opened"/>\n</bbkmm:defRangeYear_opened>\n')
		file1.write('</rdf:Description>\n')
		if (yoobj != ''):
			file1.write('<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange/' + item + '_opened">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange"/>\n</rdf:type>\n<bbkmm:hasLowerValue>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue/' + item + '_opened"/>\n</bbkmm:hasLowerValue>\n<bbkmm:hasUpperValue>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue/' + item + '_opened"/>\n</bbkmm:hasUpperValue>\n</rdf:Description>\n')

			sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
			query = definitions.RDF_PREFIX_PRELUDE + """
										    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

										   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
										WHERE {VALUES ?x{<""" + yoobj + """>} ?x ?y ?z}
									 	"""

			sparql.setQuery(query)
			####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
			sparql.setMethod("POST")

			sparql.setReturnFormat(JSON)
			resultsacrr = sparql.query().convert()
			dict = resultsacrr['results']['bindings']

			for x in dict:
				subject = (x['x']['value'])
				property = (x['y']['value'])
				object = (x['z']['value'])
				if (property == 'http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf'):
					sparql2 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
					query2 = definitions.RDF_PREFIX_PRELUDE + """
															    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

															   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
															WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
														 	"""

					sparql2.setQuery(query2)
					####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
					sparql2.setMethod("POST")

					sparql2.setReturnFormat(JSON)
					resultsacrr2 = sparql2.query().convert()
					dict2 = resultsacrr2['results']['bindings']

					for x in dict2:
						subject2 = (x['x']['value'])
						property2 = (x['y']['value'])
						object2 = (x['z']['value'])
						if (property2 == 'http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange'):
							sparql3 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
							query3 = definitions.RDF_PREFIX_PRELUDE + """
																						    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																						   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																						WHERE {VALUES ?x{<""" + object2 + """>} ?x ?y ?z}
																					 	"""

							sparql3.setQuery(query3)
							####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
							sparql3.setMethod("POST")

							sparql3.setReturnFormat(JSON)
							resultsacrr3 = sparql3.query().convert()
							dict3 = resultsacrr3['results']['bindings']

							for x in dict3:
								subject3 = (x['x']['value'])
								property3 = (x['y']['value'])
								object3 = (x['z']['value'])
								if (property3 == 'http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue'):
									file1.write(
										'<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue/' + item + '_opened">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue"/>\n</rdf:type>\n<bbkmm:hasValue>\n<rdf:Description>\n<xsd:anyType>' + object3 + '</xsd:anyType>\n</rdf:Description>\n</bbkmm:hasValue>\n</rdf:Description>\n')
						if (property == 'http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange'):
							sparql3 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
							query3 = definitions.RDF_PREFIX_PRELUDE + """
																													    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																													   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																													WHERE {VALUES ?x{<""" + object2 + """>} ?x ?y ?z}
																												 	"""

							sparql3.setQuery(query3)
							####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
							sparql3.setMethod("POST")

							sparql3.setReturnFormat(JSON)
							resultsacrr3 = sparql3.query().convert()
							dict3 = resultsacrr3['results']['bindings']

							for x in dict3:
								subject3 = (x['x']['value'])
								property3 = (x['y']['value'])
								object3 = (x['z']['value'])
								if (property3 == 'http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue'):
									file1.write(
										'<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue/' + item + '">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue"/>\n</rdf:type>\n<bbkmm:hasValue>\n<rdf:Description>\n<xsd:anyType>' + object3 + '</xsd:anyType>\n</rdf:Description>\n</bbkmm:hasValue>\n</rdf:Description>\n')

		if(ycobj!=''):
			file1.write('<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange/'+item+'_closed">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/ValueRange"/>\n</rdf:type>\n<bbkmm:hasLowerValue>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue/'+item+'_closed"/>\n</bbkmm:hasLowerValue>\n<bbkmm:hasUpperValue>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue/'+item+'_closed"/>\n</bbkmm:hasUpperValue>\n</rdf:Description>\n')

			sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
			query = definitions.RDF_PREFIX_PRELUDE + """
								    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

								   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
								WHERE {VALUES ?x{<""" + ycobj + """>} ?x ?y ?z}
							 	"""

			sparql.setQuery(query)
			####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
			sparql.setMethod("POST")

			sparql.setReturnFormat(JSON)
			resultsacrr = sparql.query().convert()
			dict = resultsacrr['results']['bindings']

			for x in dict:
				subject = (x['x']['value'])
				property = (x['y']['value'])
				object = (x['z']['value'])
				if(property=='http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf'):
					sparql2 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
					query2 = definitions.RDF_PREFIX_PRELUDE + """
													    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

													   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
													WHERE {VALUES ?x{<""" + object + """>} ?x ?y ?z}
												 	"""

					sparql2.setQuery(query2)
					####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
					sparql2.setMethod("POST")

					sparql2.setReturnFormat(JSON)
					resultsacrr2 = sparql2.query().convert()
					dict2 = resultsacrr2['results']['bindings']

					for x in dict2:
						subject2 = (x['x']['value'])
						property2 = (x['y']['value'])
						object2 = (x['z']['value'])
						if (property2 == 'http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange'):
							sparql3 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
							query3 = definitions.RDF_PREFIX_PRELUDE + """
																				    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																				   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																				WHERE {VALUES ?x{<""" + object2 + """>} ?x ?y ?z}
																			 	"""

							sparql3.setQuery(query3)
							####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
							sparql3.setMethod("POST")

							sparql3.setReturnFormat(JSON)
							resultsacrr3 = sparql3.query().convert()
							dict3 = resultsacrr3['results']['bindings']

							for x in dict3:
								subject3 = (x['x']['value'])
								property3 = (x['y']['value'])
								object3 = (x['z']['value'])
								if(property3=='http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue'):
									file1.write('<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue/'+item+'_closed">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/LowerValue"/>\n</rdf:type>\n<bbkmm:hasValue>\n<rdf:Description>\n<xsd:anyType>'+object3+'</xsd:anyType>\n</rdf:Description>\n</bbkmm:hasValue>\n</rdf:Description>\n')
						if (property == 'http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange'):
							sparql3 = SPARQLWrapper(app.config['SPARQLENDPOINT'])
							query3 = definitions.RDF_PREFIX_PRELUDE + """
																											    	prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>

																											   	SELECT  ?x ?y ?z   FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
																											WHERE {VALUES ?x{<""" + object2 + """>} ?x ?y ?z}
																										 	"""

							sparql3.setQuery(query3)
							####print "?#?#? apputils.py at line: 740 Dbg-out variable \query [", query, "]\n";
							sparql3.setMethod("POST")

							sparql3.setReturnFormat(JSON)
							resultsacrr3 = sparql3.query().convert()
							dict3 = resultsacrr3['results']['bindings']

							for x in dict3:
								subject3 = (x['x']['value'])
								property3 = (x['y']['value'])
								object3 = (x['z']['value'])
								if (property3 == 'http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue'):
									file1.write(
										'<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue/'+item+'_closed">\n<rdf:type>\n<rdf:Description rdf:about="http://mappingMuseums.dcs.bbk.ac.uk/UpperValue"/>\n</rdf:type>\n<bbkmm:hasValue>\n<rdf:Description>\n<xsd:anyType>' + object3 + '</xsd:anyType>\n</rdf:Description>\n</bbkmm:hasValue>\n</rdf:Description>\n')

	file1.write('</rdf:RDF>')
	file1.close()
	return






def getMuseumPropertiesForId(shortid):
    museumid=' "'+shortid+'"^^xsd:string .'
    querycols=""
    queryparams=""
    coldict={}

    i=0
    for tup in definitions.LISTITEMS:
	col,val=tup
	coldict[col]=val
    rcount=0
    for key, val in coldict.iteritems():
	if (key.find(definitions.DEFRANGE) > -1):
	    querycols=querycols+getQueryForCol(key.replace(definitions.DEFRANGE,""),rcount)
	else:
	    querycols=querycols+getQueryForCol(key,rcount)


	if (key.find(definitions.DEFRANGE) > -1):
	    queryparams=queryparams+"?"+key.replace(definitions.DEFRANGE,"")+" "
	else:
	    queryparams=queryparams+"?"+key.replace("def","")+" "
	rcount+=1

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum  """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
           ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+""" """+str(museumid)+"""
    """+str(querycols)+"""
    } """

    sparql.setQuery(query)
    print "?#?#? apputils.py at line: 740 Dbg-out variable \query [",query,"]\n";
    sparql.setMethod("POST")
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
	

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get  data for use with the Admin data property of ONS classifications for visualisation
# Arguments:
#  
# @patharray the menu path
# @startperiod start year
# @endperiod   end year
# @columns=None columns to retrieve
# @locationname="location" The location attribute to retrieve on

def getVizLocationData(patharray,startperiod,endperiod,columns=None,locationname="location"):
    
    pl=len(patharray)-1
    placename=patharray[pl].replace("_CA","").replace("_"," ")
    placename=placename.replace(" CA","")
    placenamewithquotes='"'+placename+'"'

    querycols=""
    queryparams=""
    if (columns != None):
	rcount=0
	for col in columns:
	    querycols=querycols+getQueryForCol(col,rcount)
	    queryparams=queryparams+"?"+col+" "
	    rcount+=1
	    
	
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    if (placename =="UK"):
	subquery="""
	?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
	?adm a """+definitions.PREFIX_WITHCOLON+"""Country   .
	?museum """+definitions.PREFIX_WITHCOLON+"""refersToCountry ?adm .
	?adm """+definitions.PREFIX_WITHCOLON+"""hasName ?"""+locationname+""" .
	"""
    else:
        ## Country level has no containment so we need to remove this bit if query is for country
	localcontainment="""?adm """+definitions.PREFIX_WITHCOLON+"""contains ?"""+locationname+""" ."""
	for key, val in COUNTRY_TRANSLATION_TABLE.iteritems():
	    if (placename == val):
		localcontainment=""
		break;
    
	subquery="""
	?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
	?adm """+definitions.PREFIX_WITHCOLON+"""hasName  """+placenamewithquotes+"""^^xsd:string .
	"""+localcontainment+"""
	?"""+locationname+""" a ?clazz .
	?"""+locationname+""" """+definitions.PREFIX_WITHCOLON+"""containedBy ?adm .
	BIND(concat(\""""+definitions.HTTPSTRING+definitions.RDFDEFURI+"""refersTo",strafter(STR(?clazz),"/def/")) AS ?pred) .
	?museum ?pred2 ?"""+locationname+""" .
	"""


    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum ?clazz ?"""+locationname+""" ?Year_opened ?Year_closed """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <"""+app.config['GEOADMINGRAPH']+""">
    WHERE
    {
    
    """+subquery+"""
    """+str(querycols)+"""

    OPTIONAL {
     ?museum    """+definitions.PREFIX_WITHCOLON+"""defRangeYear_opened ?duri_Year_opened_3 .
               ?duri_Year_opened_3  """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_Year_opened_3 .
               ?vr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasLowerRange ?lr_Year_opened_3 .
               ?lr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasLowerValue ?lv_Year_opened_3 .
               ?vr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasUpperRange ?ur_Year_opened_3 .
               ?ur_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasUpperValue ?uv_Year_opened_3 .
          BIND (CONCAT(?lv_Year_opened_3,":",?uv_Year_opened_3)  as ?Year_opened)
             }


    OPTIONAL {
     ?museum    """+definitions.PREFIX_WITHCOLON+"""defRangeYear_closed ?duri_Year_closed_4 .
               ?duri_Year_closed_4 """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_Year_closed_4 .
               ?vr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasLowerRange ?lr_Year_closed_4 .
               ?lr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasLowerValue ?lv_Year_closed_4 .
               ?vr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasUpperRange ?ur_Year_closed_4 .
               ?ur_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasUpperValue ?uv_Year_closed_4 .
          BIND (CONCAT(?lv_Year_closed_4,":",?uv_Year_closed_4)  as ?Year_closed)
             }



    } """

    print "BEGIN ###################### getVizLocationData QUERY ####################################"
    print query
    print "END ###################### getVizLocationData QUERY ####################################"

    sparql.setQuery(query)
    sparql.setMethod("POST")
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
	

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves data to be used with the browse page
# Arguments:
#  
# @columns columns to retrieve
# @filters=None 
# @vardict=None dictionary to be used when SPARQL variables duplicate each other

def getMarkerData(columns,filters=None,vardict=None): 

    vizgeoquery="""
    ?adm a ?clazz .
    ?adm """+definitions.PREFIX_WITHCOLON+"""hasName  '${GEOENTITY}'^^xsd:string .
    BIND(concat('http://bbk.ac.uk/MuseumMapProject/def/refersTo',strafter(STR(?clazz),'/def/')) AS ?pred) .
    ?museum ?pred2 ?adm .
    \n """

    vizadmgeoquery="""
    ?adm a ${GEOADMAREA} .
    ?adm """+definitions.PREFIX_WITHCOLON+"""hasTypedName  ?geoadmname .
    BIND(concat(strafter(STR(?adm),'/def/')) AS ?GeoAdmcol) .
    ?museum ?pred2 ?adm .
    \n """

    geoquery=""
    querycols=""
    queryparams=""
    filter=""
    if (filters==None):
	filters=[]

## Deal with the visualisation geo query
#  Once this works it should be turned into a ligthweight datatype class that
#  can be added dynamically and does not have all the search interfaces. Only need
#  to work with markerdata and getquery for col. Remnove params from markerdata

    if (definitions.GEOCOL in columns):
	for key, val in vardict.iteritems():
	    vizgeoquery=vizgeoquery.replace(key.strip(),val.strip())
	geoquery=vizgeoquery
	queryparams=queryparams+"?"+definitions.GEOCOL+" "
	columns.remove(definitions.GEOCOL)
	filters.append('FILTER(STR(?pred) = STR(?pred2))')
    elif (definitions.GEOADMCOL in columns):
	for key, val in vardict.iteritems():
	    vizadmgeoquery=vizadmgeoquery.replace(key.strip(),val.strip())
	geoquery=vizadmgeoquery
	queryparams=queryparams+"?"+definitions.GEOADMCOL+" ?geoadmname "
	columns.remove(definitions.GEOADMCOL)


    for f in filters:
	filter=filter+f+" . \n"
	
    rcount=1
    for col in columns:
        querycols=querycols+getQueryForCol(col,rcount)
        queryparams=queryparams+"?"+col+" "
	rcount+=1


    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    SELECT DISTINCT  ?museum ?Latitude ?Longitude """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <"""+app.config['GEOADMINGRAPH']+""">
    WHERE { 
    ?museum  rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
    ?museum  """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.LATITUDE+""" ?Latitude . 
    ?museum  """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.LONGITUDE+""" ?Longitude . 
    """+str(geoquery)+"""
    """+str(querycols)+"""
    """+str(filter)+"""
    } """

    print "----------------------------------- getMarkerData QUERY ----------------------"
    print query
    print "----------------------------------- end of getMarkerData QUERY ----------------------"

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Removes type info from name
# Arguments:
#  
# @shortid
def getMuseumPropertiesForIdWorking(shortid):
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
    
SELECT DISTINCT  ?p ?o
FROM <"""+app.config['DEFAULTGRAPH']+""">
FROM <http://bbk.a.c.uk/MuseumMapOrdnance/graph/v1>
WHERE { 
        <http://bbk.ac.uk/MuseumMapProject/data/Museum/id/"""+shortid+"""> ?p ?o .

        
    }
     """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    properties = sparql.query().convert()
    return properties

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Is this clazz an abstract clazz?
# Arguments:
#  
# @clazz name
def isDataClass(clazz):
    if (clazz.find(":") < 0 and clazz in definitions.DATATYPEDICT and definitions.DATATYPEDICT[clazz]==clazz ):
	return True
    else:
	return False

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Loads a class inmplementation
# Arguments:
#  
# @clazz name
def getDataClassInstance(clazz):
    
    l=__name__.rfind(".")
    mname=__name__[:l]+"."+"datatypes."+clazz
    instance=None
    try:
	my_module = importlib.import_module(mname)
	try:
	    MyClass = getattr(my_module, clazz)
	    instance = MyClass()

	except AttributeError:
	    print "?#?#? apputils.py at line: 908 Dbg-out variable \clazz [",clazz,"]\n";
	    print "$$$$$$$$$ CLASS DOES NOT EXIST !"
	    
    except ImportError:
	print "?#?#? apputils.py at line: 903 Dbg-out variable \mname [",mname,"]\n";
	print "$$$$$$$$$ MODULE  DOES NOT EXIST !"
	 
	 
    return instance


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Look for data type implementations and create a cache
# This works both on the attritypes (LIST) and the datadict (DICT) so we need to check which it is
# Arguments:
#  
# @datadict cache
def discoverDatatypes(datadict):

    #print "DATADICT DISC+++++++++++++++++++++++++++++++++++++++++++++++++++"
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(datadict)
    #print "DATADICT+++++++++++++++++++++++++++++++++++++++++++++++++++"
    dname=os.path.dirname(inspect.getfile(sys.modules[__name__]))+"/"+"datatypes"
    dstruct=str(type(datadict))
    # Get a list of all files in directory
    for file in os.listdir(dname):
	if file.endswith(".py"):
	    fname=os.path.join(dname, file)
	    parts=fname.split("/")
	    plen=len(parts)
	    modname=parts[plen-1]
	    fdot=modname.find(".")
	    dataname=modname[:fdot]
	    if (not dataname.startswith("__")):
		# Compare with datatypes
		if (dstruct == "<type 'dict'>"):
		    if (not dataname in datadict):
			# If not in datadict check it loads
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    print dataname
			    datadict[dataname]=dataname
			    # Check its interface
		else:
		    # Attritypes
		    found=False
		    for item in datadict:
			name,ntype=(item)
			if (name == dataname):
			    found=True
			    break;
		    if (not found):
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    datatypeforsearch=instance.getSearchType()
			    tup=(dataname,datatypeforsearch)
			    print tup
			    print "+++"

			    datadict.append(tup)
			    # Check its interface

    print datadict
    return datadict
def discoverDatatypes2(datadict):

    #print "DATADICT DISC+++++++++++++++++++++++++++++++++++++++++++++++++++"
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(datadict)
    #print "DATADICT+++++++++++++++++++++++++++++++++++++++++++++++++++"
    dname=os.path.dirname(inspect.getfile(sys.modules[__name__]))+"/"+"datatypes"
    dstruct=str(type(datadict))
    # Get a list of all files in directory
    for file in os.listdir(dname):
	if file.endswith(".py"):
	    fname=os.path.join(dname, file)
	    parts=fname.split("/")
	    plen=len(parts)
	    modname=parts[plen-1]
	    fdot=modname.find(".")
	    dataname=modname[:fdot]
	    if (not dataname.startswith("__")):
		# Compare with datatypes
		if (dstruct == "<type 'dict'>"):
		    if (not dataname in datadict):
			# If not in datadict check it loads
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    print("i am HERE")
			    dataname= u"Admin_Area".encode(encoding='ascii',errors='strict')
			    dataname2=u"Year_exists".encode(encoding='ascii',errors='strict')
			    datadict[dataname2]=dataname2
			    datadict[dataname]=dataname
			    # Check its interface
		else:
		    # Attritypes
		    found=False
		    for item in datadict:
			name,ntype=(item)
			if (name == dataname):
			    found=True
			    break;
		    if (not found):
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    datatypeforsearch=instance.getSearchType()
			    tup=(dataname,datatypeforsearch)
			    print tup
			    print "+++"

			    print "herere"
			    datadict[dataname]=datatypeforsearch

			    # Check its interface

    print datadict
    return datadict
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Creates the select menu for the datatypes used in search
# loop over all types picking non xml datatype
# add List to typename (dataproperty)
# get list from database
# add all elements of list as group:typename to map
# Arguments:
#  
# @attributetypes the types to retrieve the values for
def getdatagroups(attributetypes):

    grouplist=[]
    acount=0
    for attributepair in attributetypes:
        #        print attributepair
        attribute=attributepair[0].strip()
        propertytype=attributepair[1].strip()
        if (not propertytype in definitions.XML_TYPES):
            sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    
	    query=definitions.RDF_PREFIX_PRELUDE+"""
            prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

            select DISTINCT * 
            FROM <"""+app.config['DEFAULTGRAPH']+""">
            where {
                    """+definitions.PREFIX_WITHCOLON+propertytype+definitions.LISTNAME+""" """+definitions.PREFIX_WITHCOLON+"""contents/rdf:rest*/rdf:first ?item
                  }
                  """
            print query
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            if (len(results["results"]["bindings"]) < 1):
		# Check for range type and replace with atomic type
		
		if (propertytype in definitions.DATATYPEDICT):
		    dvalue=definitions.DATATYPEDICT[propertytype]
		    if (dvalue == definitions.DEFINED_RANGETYPE):
			# Get type
			dtype=propertytype.replace(definitions.DEFRANGE,"")
			dvalue=definitions.DATATYPEDICT[dtype]
			attributetypes[acount]=(attribute,dvalue.replace(definitions.XML_TYPES_PREFIX,""))
		    else:
			if (isDataClass(definitions.DATATYPEDICT[attribute])):
			    instance=getDataClassInstance(definitions.DATATYPEDICT[attribute])
			    datatypeforsearch=instance.getSearchType()
			    attributetypes[acount]=(attribute,datatypeforsearch)

		elif (attribute in definitions.DATATYPEDICT):
		    # We have a class
		    if (isDataClass(definitions.DATATYPEDICT[attribute])):
			instance=getDataClassInstance(definitions.DATATYPEDICT[attribute])
			datatypeforsearch=instance.getSearchType()
			attributetypes[acount]=(attribute,datatypeforsearch)
		else:
		    option="<option value='1 Missing data here !'>1 Missing data here !</option>"
		    grouplist.append((propertytype,option))
		    option="<option value='2 Missing data here !'>2 Missing data here !</option>"
		    grouplist.append((propertytype,option))
            else:
                listname=propertytype+definitions.LISTNAME
                definitions.LISTS[propertytype]=listname
                
	    if (propertytype.find(definitions.DEFCLASS) > -1):
		dtype=propertytype.replace(definitions.DEFCLASS,definitions.DEFNAME).strip()
	    else:
		dtype=propertytype.strip()


	    # Now get all the values from the DB, create presentation items for search menu and create the
	    # menuitems.
	    itemlist=[]
            for result in results["results"]["bindings"]:
                item=result["item"]["value"].strip()
		itemlist.append(item)

	    sorteditems=sorted(list(set(itemlist)))
	    uniqvalues={}
            for item in sorteditems:
		presitem=item
		if (dtype in definitions.DATATYPEDICT):
		    dvalue=definitions.DATATYPEDICT[dtype] 
		    presitem=modeltoview.getViewForType(dvalue,item)
		    item=modeltoview.getTypeForViewForSearch(dvalue,presitem)
		else:
		    print "ERRIOROOR : DTYPE "+dtype+" NOT FOUND"

		uniqvalues[item]=presitem

	    sorteditems=None
	    skeys=sorted(uniqvalues.keys())
	    for key in skeys :
		option="<option value='"+key+"'>"+uniqvalues[key].replace("_"," ")+"</option>"
		grouplist.append((propertytype,option))

	    uniqvalues=None
	    results=None
	acount+=1
	
    return grouplist
                
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
  

## Purpose:Retrieves classes and predicates. Side effect that they go into
#          the definitions dict as well
# 
def getpredicatestypes(): 

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property, ?range
FROM <"""+app.config['DEFAULTGRAPH']+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum .
  ?property rdfs:range ?range
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    var=results['head']['vars']
    varstr=var[0]
    count=0
    clazzes=[]

    for result in results["results"]["bindings"]:
	rtype=result["range"]["value"]
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
	if (clazzname.find(definitions.DEFRANGE)> -1):
	    rtype=clazzname
	    clazzname=clazzname.replace(definitions.DEFRANGE,"")
	else:
	    clazzname=clazzname.replace(definitions.HASNAME,"")
	    clazzname=clazzname.replace(definitions.DEFNAME,"")

	if (not clazzname =="isSubClassInstanceOf"):
	    clazzes.append((clazzname,rtype))
	    definitions.PROPERTY_TYPES_DICT[clazzname]=rtype
	    
	count=count+1
    return clazzes

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves all predicats relating to a museum
# 
def getmuseumpredicates(): 

    predicatelistname="PredicateList"

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property
FROM <"""+app.config['DEFAULTGRAPH']+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum 
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    var=results['head']['vars']
    varstr=var[0]
    count=0
    clazzes=[]

    for result in results["results"]["bindings"]:
	uri=result[varstr]["value"]
	uricomponents=uri.split('/')
	clazzname=uricomponents[5]
        clazzname=clazzname.replace(definitions.HASNAME,"")

        ### !! NOTE we dont want this visible as it is only for system use
	if (not clazzname == "isSubClassInstanceOf"):
	    clazzes.append((clazzname,clazzname))
	count=count+1


    definitions.LISTS["Predicate"]=predicatelistname


    
    return clazzes


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Returns the column if defined in the datatyep map
# Arguments:
#  
# @incol col to look for
def getDefinedType(incol):
    if (not incol.startswith(definitions.DEFNAME)):
	defcol=definitions.DEFNAME+incol
	if (defcol in definitions.DATATYPEDICT):
	    col=defcol
	else:
	    defcol=definitions.DEFRANGE+incol
	    if (defcol in definitions.DATATYPEDICT):
		col=defcol
	    else:
		col=incol
    else:
	col=incol
    return col
    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Is this column an abstract type?
# Arguments:
#  
# @incol  colomn
# @defcol its abstract type name

def isTypeAClazz(incol,defcol):
    
    if (incol == defcol and  definitions.DATATYPEDICT[defcol].find("xsd") < 0):
	return True
    else:
	return False
    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def editQueryParams(incol,querycols,queryparams):
    col=getDefinedType(incol)
    if (isDataClass(definitions.DATATYPEDICT[col])):
 	instance=getDataClassInstance(definitions.DATATYPEDICT[col])
 	print("instance")
 	print(instance)
 	querycols,queryparams=instance.editQueryParams(col,querycols,queryparams)
	
    return querycols,queryparams

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Creates a query for a column
# Arguments:
#  
# @incol the column to search
# @rcount variable repeat count
# @optional=True Is the query optional?
# @museumuri='?museum ' name of museum class variable
# @matchstrings=[] query match string
# @conditions=[]   condition
# @matchcolumns=[] column name
# @coltoargdict={} macro name for column in case type is an implementation class

def getQueryForCol(incol,
		   rcount,optional=True,
		   museumuri='?museum ',
		   matchstrings=[],
		   conditions=[],
		   matchcolumns=[],
		   coltoargdict={}):


    rangequery="""
    OPTIONAL {
     ?museum    """+definitions.PREFIX_WITHCOLON+"""defRange${column_name} ?duri_${rcount} .
               ?duri_${rcount} """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_${rcount} .
               ?vr_${rcount}    """+definitions.PREFIX_WITHCOLON+"""hasLowerRange ?lr_${rcount} .
               ?lr_${rcount}    """+definitions.PREFIX_WITHCOLON+"""hasLowerValue ?lv_${rcount} .
               ?vr_${rcount}    """+definitions.PREFIX_WITHCOLON+"""hasUpperRange ?ur_${rcount} .
               ?ur_${rcount}    """+definitions.PREFIX_WITHCOLON+"""hasUpperValue ?uv_${rcount} .
          BIND (CONCAT(?lv_${rcount},":",?uv_${rcount})  as ?${column_name})
	     }
    \n """



#- - - - -
    col=getDefinedType(incol)
    query=""
    
											
    if (not col in definitions.DATATYPEDICT):
	print "$$$$$$$$$$$$$$$$$$ "+col+" col not found"
    elif (definitions.DATATYPEDICT[col] == definitions.DEFINED_RANGETYPE):
	query=rangequery.replace("${column_name}",incol).replace("${rcount}",str(incol)+"_"+str(rcount))
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_LISTTYPE):
        # Get the object property and then its hasObject
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+col+'uri . \n'
	colwithoutdef=col[3:]
        query=query+'?'+col+'uri '+definitions.PREFIX_WITHCOLON+definitions.HASNAME+colwithoutdef+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_HIERTYPE):
        # Get the object property and then its hasObject
	colwithoutdef=col[3:]
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
    elif (definitions.DATATYPEDICT[col] in definitions.XML_TYPES_WITH_PREFIX):
        #  plain type
        if(optional):
            query="OPTIONAL{ "+museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" . } \n"
        else:
            query= museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" .  \n"

    elif (col in definitions.DATATYPEDICT and isDataClass(definitions.DATATYPEDICT[col])):
	instance=getDataClassInstance(definitions.DATATYPEDICT[col])
	if (incol in matchcolumns):
	    query=instance.getQuery(incol,
				    rcount,
				    matchstrings[coltoargdict[incol]],
				    conditions[coltoargdict[incol]],
				    matchcolumns[coltoargdict[incol]])

	else:
	    query=instance.getQuery(incol,
				    rcount,
				    None,
				    None,
				    None)
	    
    else:
	print "$$$$$$$$$$ ERROR UNKNOWN DATATYPE "+col+"$$$$$$$$$$"
	query=""
	    
    return query


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Create virtuoso data type statement for column
# Arguments:
#  
# @col name
# @coltocountdict variable counts
# @lowerorupper="" name of SPARQL variable

def getCol(col,coltocountdict,lowerorupper=""):
    dtype=getDefinedType(col)
    if (dtype.startswith(definitions.DEFRANGE)):
	##Return lower index
	rcount=coltocountdict[col]
	if (len(lowerorupper)>0):
	    q='STRDT(?'+lowerorupper+'_${rcount},'+definitions.DATATYPEDICT[col]+')'
	else:
	    q='STRDT(?lv_${rcount},'+definitions.DATATYPEDICT[col]+')'
	    
        return q.replace("${rcount}",str(col)+"_"+str(rcount))
    else:
	return "?"+col
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


## Purpose:Returns a filter clause for a column
# Arguments:
#  
# @matchcolumns   columns
# @conditions     conditions 
# @matchstrings   strings to match
# @coltocountdict variable count

def getFilterClause(matchcolumns,conditions,matchstrings,coltocountdict): 
    matchfilter=""
    filterdict={}

    for col,cond,match in zip(matchcolumns,conditions,matchstrings):

	#print col
	#print cond
	#print match
	#print filterdict
	if (col not in filterdict):
	   filterdict[col]=[]

        if (len(match) >0):
	    defcol=getDefinedType(col)
	    #print definitions.DATATYPEDICT[defcol]
	    isd=isDataClass(definitions.DATATYPEDICT[defcol])
	    ist=isTypeAClazz(col,defcol)
	    
	    print "b4if"
	    #print defcol

	    print "b4ifagen"
	    if (defcol not in definitions.DATATYPEDICT):
		print "if"
		print defcol+" col not found"

	    elif (cond == "match"):
		print "elif1"
		if (isTypeAClazz(col,defcol)):
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			rcount=coltocountdict[col]
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			filterdict[col].append(("||",instance.getMatchFilter(rcount,match,cond)))
		# Check if we have a hier
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_HIERTYPE):
		    defmatch=modeltoview.getTypeForView(definitions.DEFINED_HIERTYPE,match)		    
		    # Fixes the scotland problem without removing contains on strings.
		    #filterdict[col].append(("||",'(strEnds(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(defmatch)+'")))'))
		    filterdict[col].append(("||",'(CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(defmatch)+'")))'))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_LISTTYPE):
		    filterdict[col].append(("||",'(LCASE(str('+"?"+str(col)+')) = '+'LCASE("'+str(match)+'"))'))
		else:
		    filterdict[col].append(("||",'(CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(match)+'")))'))
		    
	    elif (cond == "notmatch"):
		print "elif2"
		if (isTypeAClazz(col,defcol)):
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			rcount=coltocountdict[col]
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			filterdict[col].append(("||",instance.getMatchFilter(rcount,match,cond)))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_HIERTYPE):
		    defmatch=modeltoview.getTypeForView(definitions.DEFINED_HIERTYPE,match)		    
		    filterdict[col].append(("||",'(! CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(defmatch)+'")))'))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_LISTTYPE):
		    filterdict[col].append(("||",'(LCASE(str('+"?"+str(col)+')) != '+'LCASE("'+str(match)+'"))'))
		else:
		    filterdict[col].append(("||",'(! CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(match)+'")))'))
		    
	    elif (isTypeAClazz(col,defcol)):
		print "elif3"
		if (isTypeAClazz(col,defcol)):
		    print "elif3if1"
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			print "elif3if2"
			print coltocountdict
			print 'col'
			print col
			print 'defs'
			print definitions.DATATYPEDICT
			print 'defcol'
			print defcol
			rcount=coltocountdict[col]
			print 'rcount'
			print rcount
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			print 'instance'
			print instance
			## We dont have any dataclasses with nonnumeric comparisons (match/not)
			## To fix similar problems in the match/not perhaps the below solution can just be copied?
			fl=len(filterdict[col])
			if (fl == 0):
			    print "elif3if3"
			    filterdict[col].append( (") . \n",instance.getCompareFilter(rcount,match,cond)))
			elif (fl == 1):
			    print "elif3elif3"
			    filterdict[col].append( (" ","FILTER("+instance.getCompareFilter(rcount,match,cond)))
			else:
			    print "elif3else"
			    filterdict[col].append( (" ","). \n FILTER("+instance.getCompareFilter(rcount,match,cond)))

##          Range lower value=lv uppervalue=uv
            elif (cond == "LTE"):
		print "elif4"
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' <= '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' <= '+match+')'))
            elif (cond == "LT"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' < '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' < '+match+')'))
            elif (cond == "GT"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' > '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' > '+match+')'))
            elif (cond == "GTE"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' >= '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' >= '+match+')'))
            elif (cond == "EQ"):
		print "elif5"
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' = '+match+')'))
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' = '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' = '+match+')'))
            elif (cond == "NEQ"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' < '+match+')'))
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' > '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' != '+match+')'))
            elif (cond == "BET"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    if (match.find(":") > 0):
			parts=match.split(":")
			lower=parts[0]
			higher=parts[1]
		    else:
			lower=match
			higher=match
		    
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' >= '+lower+')'))
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"uv")+' <= '+higher+')'))
		else:
		    lower=match
		    higher=match
		    
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' >= '+match+')'))
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' <= '+match+')'))

            elif (cond == "PBET"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    if (match.find(":") > 0):
			parts=match.split(":")
			lower=parts[0]
			higher=parts[1]
		    else:
			lower=match
			higher=match
		    
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"uv")+' >= '+lower+')'))
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' <= '+higher+')'))
		else:
		    lower=match
		    higher=match
		    
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"uv")+' >= '+lower+')'))
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' <= '+higher+')'))



	    # Range
            elif (cond == "PLTE"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
            elif (cond == "PLT"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
            elif (cond == "PGT"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' > '+match+')'))
            elif (cond == "PGTE"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' >= '+match+')'))
            elif (cond == "PEQ"):
		filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
		filterdict[col].append(("||",'('+match+' <= '+getCol(col,coltocountdict,"uv")+')'))
            elif (cond == "PNEQ"):
		filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' != '+match+')'))
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' != '+match+')'))
	    # Date
            elif (cond == "DLTE"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' <= "'+match+'"^^xsd:date)'))
            elif (cond == "DLT"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' < "'+match+'"^^xsd:date)'))
            elif (cond == "DGT"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' > "'+match+'"^^xsd:date)'))
            elif (cond == "DGTE"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' >= "'+match+'"^^xsd:date)'))
            elif (cond == "DEQ"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' = "'+match+'"^^xsd:date)'))
            elif (cond == "DNEQ"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' != "'+match+'"^^xsd:date)'))
        elif (cond == "True"):
            filterdict[col].append(("||",'(STR('+getCol(col,coltocountdict)+') =  STR(true) )'))
        elif (cond == "False"):
            filterdict[col].append(("||",'(STR('+getCol(col,coltocountdict)+') =  STR(false) )'))

    for key, val in filterdict.iteritems():
	if (len(val) == 1):
	    op,cond=val[0]
	    matchfilter=matchfilter+ "FILTER ("+cond+") . \n"
	else:
	    tempfilter=""
	    for f in val:
		op,cond=f
		tempfilter=tempfilter+cond+" "+op
	    tlen=len(tempfilter)-2
	    tempfilter=tempfilter[0:tlen]
	    matchfilter=matchfilter+ "FILTER ("+tempfilter+") . \n"
    filterdict=None
    return matchfilter

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Create a query for a list of columns
# Arguments:
#  
# @columns      column names
# @matchcolumns match names
# @conditions   conditions
# @matchstrings strings to match
# @ordercolumn  which column to order on

def getSearchResults(columns,matchcolumns,conditions,matchstrings,ordercolumn): 
    freesearch='no'
    if(ordercolumn=='?free'):
		ordercolumn='?museum'
		freesearch='yes'
    querycols=""
    queryparams=""
    coltocountdict={}
    coltoargdict={}
    


    ## Make sure we have subject in columns. Adding it here means it becomes optional.
    ## This should be removed eventually so that it is always optional if specified.
    if (not definitions.NAME_OF_MUSEUM in columns):
	columns.insert(0,definitions.NAME_OF_MUSEUM)

    argcount=0
    for col in matchcolumns:
	coltoargdict[col]=argcount
	argcount+=1

    rcount=1
    print "columns"
    print columns
    print "matchstrings"
    print matchstrings
    for col in columns:
        print col
        print rcount
        print matchstrings
        querycols=querycols+getQueryForCol(col,rcount,matchstrings=matchstrings,
					   conditions=conditions,
					   matchcolumns=matchcolumns,
					   coltoargdict=coltoargdict)
        queryparams=queryparams+"?"+col+" "
	print("all is somewhat well")

	querycols,queryparams=editQueryParams(col,querycols,queryparams)
	coltocountdict[col]=rcount
	rcount+=1

    print "yello"
    print coltocountdict
    print col
    matchfilter=getFilterClause(matchcolumns,conditions,matchstrings,coltocountdict)
    if "Independent-National_Trust" in matchstrings:
		print("awesome")
		matchfilter = matchfilter+'FILTER (LCASE(str(?Governance))=LCASE("http://bbk.ac.uk/MuseumMapProject/def/Independent-National_Trust")) .'
    if(freesearch=='yes'):
		#if(matchcolumns[0]=='Admin_Area'):
			#matchfilter = getFilterClause(matchcolumns, conditions, matchstrings, coltocountdict)
			#matchfilter = "FILTER ((CONTAINS(LCASE(STR(?pred12)),LCASE(STR(\"" + matchstrings[0] + "\"))))) . "
		#else:
		matchfilter="FILTER ((CONTAINS(LCASE(str(?"+matchcolumns[0]+")),LCASE(\""+matchstrings[0]+"\")))) . "
    print matchfilter
### Mapdata additions, make sure not to duplicate properties
    map_querycols=""
    map_queryparams=""


    map_columns=[definitions.LATITUDE,definitions.LONGITUDE]
    print("wibble")
    for map_col in map_columns:
	if (not map_col in columns):
	    map_querycols=map_querycols+getQueryForCol(map_col,rcount,optional=False)
	    map_queryparams=map_queryparams+"?"+map_col+" "
	    coltocountdict[map_col]=rcount
	    rcount+=1
	    

    print ("wibble2")
    print(querycols)
    if(matchcolumns[0]=='Admin_Area'):
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      querycols=querycols[:querycols.rfind('\n')]
      matchfilter="FILTER ((CONTAINS(LCASE(str(?Admin_hierarchy)),LCASE(\""+matchstrings[0]+"\")))) ."
      print(querycols)
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum """+str(queryparams)+"""  """+str(map_queryparams)+"""
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <http://bbk.ac.uk/MuseumMapProject/graph/ukadmin>
    WHERE { 
    ?museum  rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
    """+str(map_querycols)+"""
    """+str(querycols)+str(matchfilter)+"""
    } ORDER BY """+str(ordercolumn)

    print "?#?#? apputils.py at line: 1642 Dbg-out variable \query [",query,"]\n";
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    newresults=[]
    newres=[]
    for key in results["head"]["vars"]:
        newres.append(key)
    newresults.append(newres)

    for res in results["results"]["bindings"]:
        newres=[]
        for key in results["head"]["vars"]:
            if (key in res):
                newres.append(res[key]["value"])
            else:
                newres.append("")
        newresults.append(newres)
                
        
    print("matchcolumns")
    print(matchcolumns)
    finalresults=[]
    for col in matchcolumns:
        print("conditions")
        print(conditions)

        if(col == "Year_closed"):
            for cond in conditions:
                print("cond")
                print(cond)
                if(cond=="GT"):


                    for result in newresults:


                        target=0
                        for item in result:


                            if(item=="9999:9999"):
                                ##print("all is really well")
                               target=1
                        if(target==0):
                            finalresults.append(result)
                    return finalresults
    return newresults

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def getOptionsDict(attribute,module): 
    
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])

    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
    SELECT DISTINCT ?options
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
    <"""+definitions.HTTPSTRING+definitions.RDFDEFURI_NOENDINGSLASH+"""/SystemOption/id/"""+module+"""/TheSystemOption> """+definitions.PREFIX_WITHCOLON+"""has"""+attribute+"""Options  ?options .
    
    }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    var=results['head']['vars']
    optdict={}
    for result in results["results"]["bindings"]:
	all=result["options"]["value"]
	allcomponents=all.split(',')
	for opt in allcomponents:
	    kv=opt.split(':')
	    optdict[kv[0]]=kv[1]
	    
    return optdict


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Get content for a column for all museums
# Arguments:
#  
# @property column name
def getPropertyForMuseumID(property,museumid): 

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])

    colquery=getQueryForCol(property,0,False)    
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 


    SELECT DISTINCT  ?museum ?textcontent ?"""+property.replace(definitions.PREFIX_WITHCOLON,"").replace(definitions.HASNAME,"")+"""
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
       ?museum rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
       ?museum """+definitions.PREFIX_WITHCOLON+"""hasproject_id  "${MUSEUMID}"^^xsd:string .
       """+colquery+""" 
              }
    ORDER BY ASC(?property)
              
    """
    query=query.replace("${MUSEUMID}",museumid)
    pp = pprint.PrettyPrinter(indent=4)
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    rlen=len(results["results"]["bindings"])
    if (rlen > 0):
        resvalue=str(results["results"]["bindings"][0][property]["value"])
	if (resvalue.find(definitions.RDFDEFURI_NOENDINGSLASH) > -1):
	    parts=resvalue.split("/")
	    plen=len(parts)-1
	    resvalue=parts[plen]
    else:
        resvalue=""
    return resvalue


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def deleteMuseumID(museumid): 
    
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    pp = pprint.PrettyPrinter(indent=4)
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    WITH <"""+app.config['DEFAULTGRAPH']+""">
    DELETE {?museum ?p ?o }
    WHERE {
    ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
    ?museum """+definitions.PREFIX_WITHCOLON+"""hasproject_id  "${MUSEUMID}"^^xsd:string .
    ?museum ?p ?o
    }
    """
    query=query.replace("${MUSEUMID}",museumid)
    print query
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    pp.pprint(results)

    return results

def uploadMuseum(filepath, Altpostcode):
    dircsv = os.path.dirname(os.path.realpath(__file__))

    with open(dircsv + '/addmusfiles/'+filepath, 'rb') as csvfile:
        linereader = csv.reader(csvfile, delimiter='$', quotechar='"')
        rowtitle = next(linereader)
        row0 = next(linereader)
        row0 = next(linereader)
        row0 = next(linereader)
        row0 = next(linereader)
        row0 = next(linereader)
        print(row0)
        domusidentifier = row0[0]
        projectid = row0[1]
        primaryprovenanceofdata = row0[2]
        identifierusedinsourcedb = row0[3]
        nameofmuseum = row0[4]
        alternatemuseumname = row0[5]
        alternatemuseumnamesource= row0[6]
        addressline1= row0[7]
        addressline2= row0[8]
        addressline3= row0[9]
        townorcity= row0[10]
        postcode= row0[11]
        latitude= row0[12]
        longitude= row0[13]
        yearmuseumfirstdocumented= row0[14]
        yearmuseumfirstdocumentedsource= row0[15]
        yearopened= row0[16]
        yearopenedsource= row0[17]
        yearclosed= row0[18]
        yearclosedsource= row0[19]
        founder= row0[20]
        foundersource= row0[21]
        subjectmatter= row0[22]
        domussubjectmatter= row0[23]
        accreditation= row0[24]
        accreditationsource= row0[25]
        governance= row0[26]
        governancesource= row0[27]
        acesizedesignation= row0[28]
        acesizesource= row0[29]
        aimsizedesignation= row0[30]
        aimsizesource= row0[31]
        notesinternal= row0[32]
        notes= row0[33]
        size= row0[34]
        sizeprov= row0[35]
        media= row0[36]
        admincountry=""
        adminwelshua=""
        adminscottishcouncilarea=""
        adminnilocgovdistrict=""
        adminenglishregion=""
        adminenglishcounty=""
        adminenglishua=""
        adminenglishca=""
        adminenglishdistrictorborough=""
        deprivationindex=""
        deprivationindexincome=""
        deprivationindexemployment=""
        deprivationindexeducation=""
        deprivationindexhealth=""
        deprivationindexcrime=""
        deprivationindexhousing=""
        deprivationindexservices=""
        regioncountry=""
        geodemographicsupergroupcode=""
        geodemographicsupergroup=""
        geodemographicgroupcode=""
        geodemographicgroup=""
        geodemographicsubgroupcode=""
        geodemographicsubgroup=""
        geodemographicsupergrouplong=""
        geodemographicgrouplong=""
        geodemographicsubgrouplong=""
        print (yearopened)
        print(yearclosed)
        ##return
        with open(dircsv + '/../../mm_input_maindatasheet_V10_2018_12_04.csv', 'a') as mainfile:
            mainwriter = csv.writer(mainfile, delimiter='$',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            mainwriter.writerow('')
            for item in row0[:-1]:
                if (item==''):
                    mainfile.write(item)
                    mainfile.write('$')
                elif(item==postcode):
                        if(Altpostcode!=""):
                            mainfile.write('"')
                            mainfile.write(Altpostcode)
                            mainfile.write('"')
                            mainfile.write('$')
                        else:
                            mainfile.write('"')
                            mainfile.write(item)
                            mainfile.write('"')
                            mainfile.write('$')
                else:
                    mainfile.write('"')
                    mainfile.write(item)
                    mainfile.write('"')
                    mainfile.write('$')


            mainfile.write(media)
           ## os.system("ls -l")
        ##os.chmod(dircsv + '/../../mm_input_maindatasheet_V10_2018_12_04.csv', 0o777)
        os.system("python "+dircsv + "/../../location_Enumbers.py "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv | grep  \*\? | sed s/\*\?\#\?//g > "+dircsv + "/../../geobaseU#.csv")
        ##os.chmod("./geobaseU#.csv", 0o777)
        os.system("sed 's/\"//g' "+dircsv + "/../../geobaseU#.csv > "+dircsv + "/../../geobaseW.csv")
        ##os.chmod("./geobaseW.csv", 0o777)
        os.system("python "+dircsv + "/../../england_Enumbers.py "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv | grep \*\? | cut -c 7- > "+dircsv + "/../../geobaseE.csv")
        ##os.chmod("./geobaseE.csv", 0o777)
        os.system("sed 's/\"//g' "+dircsv + "/../../geobaseE.csv > "+dircsv + "/../../geobaseF.csv")
        ##os.chmod("./geobaseF.csv", 0o777)
        os.system("cat "+dircsv + "/../../geobaseF.csv "+dircsv + "/../../geobaseW.csv > "+dircsv + "/../../geobaseA.csv")

        ##os.chmod("./geobaseA.csv", 0o777)
        if(Altpostcode != ''):
                secondpostcode = "\""+Altpostcode+"\""
        postfront = postcode[:2]
        print "postfront"
        print postfront
        if(postfront=="GY") or (postfront =="JE"):
                print"GYOR"
                admincountry="Channel Islands"
        elif(postfront=="IM"):
                print "IMOR"
                admincountry="Isle of Man"
        else:
          print "else"
          with open(dircsv + '/../../geobaseA.csv', 'rb') as adminfile:
            for line in adminfile:
                linearr = line.split(',')

                ##print(linearr[0], linearr[1])
                ##print(projectid)
                if(linearr[0]==projectid):
                    print("true")
                    admincountry = linearr[1].split(':')[0]
                    adminwelshua = linearr[2].split(':')[0]
                    adminscottishcouncilarea = linearr[3].split(':')[0]
                    adminnilocgovdistrict = linearr[4].split(':')[0]
                    adminenglishregion = linearr[5].split(':')[0]
                    adminenglishcounty = linearr[6].split(':')[0]
                    adminenglishua = linearr[7].split(':')[0]
                    adminenglishca = linearr[8].split(':')[0]
                    adminenglishdistrictorborough = linearr[9].split(':')[0]

        print ("dog"+admincountry+"cat")
        print ("dog"+adminenglishdistrictorborough+"cat")

    lsoacode=""
    ladcode=""
    with open(dircsv + '/../../json/NSPL_AUG_2017_UK.csv', 'rb') as postcodefile:
        for line in postcodefile:
            linearr2 = line.split(',')
            secondpostcode = "\""+postcode+"\""
            if(Altpostcode != ''):
                secondpostcode = "\""+Altpostcode+"\""
            if(linearr2[2]==secondpostcode):
                lsoacode=linearr2[24]
                ladcode=linearr2[11]
    print(secondpostcode)
    lsoasplit=lsoacode.split("\"")
    lsoacode=lsoasplit[1]
    ladsplit = ladcode.split("\"")
    ladcode = ladsplit[1]
    print(lsoacode)
    print(ladcode)
    with open(dircsv + '/../../museumsall_gss_lsoa2011.tsv', 'a') as lsoafile:
        mainwriter2 = csv.writer(lsoafile, delimiter='\t')
        mainwriter2.writerow('')
        lsoafile.write(projectid+'\t'+lsoacode)

    with open(dircsv + '/../../museumsall_gss_lad2011.tsv', 'a') as ladfile:
        mainwriter3 = csv.writer(ladfile, delimiter='\t')
        mainwriter3.writerow('')
        ladfile.write(projectid+'\t'+ladcode)


    os.system("python "+dircsv + "/../../addColumnsWithIndexFile.py "+dircsv + "/../../deprivation_index_deciles_merged_uk_2017_lsoa2011-1.csv "+dircsv + "/../../museumsall_gss_lsoa2011.tsv "+dircsv + "/../../deprivheader.csv "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv > "+dircsv + "/../../maininput2.csv")
    os.system("python "+dircsv + "/../../addColumnsWithIndexFile.py "+dircsv + "/../../output_area_class-lad2011.tsv "+dircsv + "/../../museumsall_gss_lad2011.tsv "+dircsv + "/../../outputheader.csv "+dircsv + "/../../maininput2.csv > "+dircsv + "/../../maininput3.csv")
    if (admincountry != 'Isle of Man') and (admincountry != 'Channel Islands'):
        with open(dircsv + '/../../maininput3.csv', 'rb') as mainfile3:
            counter=1
            for line in mainfile3:
                if(counter<6):
                    counter = counter+1
                else:
                    linearr = line.split('$')

                    ##print(linearr[1])
                    projid = linearr[1].split('\"')[1]
                    ##print(projid)
                    if (projid == projectid):
                        deprivationindex = linearr[37]
                        deprivationindexincome = linearr[38]
                        deprivationindexemployment = linearr[39]
                        deprivationindexeducation = linearr[40]
                        deprivationindexhealth = linearr[41]
                        deprivationindexcrime = linearr[42]
                        deprivationindexhousing = linearr[43]
                        deprivationindexservices = linearr[44]
                        regioncountry = linearr[45].split('\"')[1]
                        geodemographicsupergroupcode = linearr[46].split('\"')[1]
                        geodemographicsupergroup = linearr[47].split('\"')[1]
                        geodemographicgroupcode = linearr[48].split('\"')[1]
                        geodemographicgroup = linearr[49].split('\"')[1]
                        geodemographicsubgroupcode = linearr[50].split('\"')[1]
                        geodemographicsubgroup = linearr[51].split('\"')[1]
                        geodemographicsupergrouplong = linearr[52].split('\"')[1]
                        geodemographicgrouplong = linearr[53].split('\"')[1]
                        geodemographicsubgrouplong = linearr[54].split('\"')[1]
    print(geodemographicsubgrouplong)

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    ##pp = pprint.PrettyPrinter(indent=4)

    query = definitions.RDF_PREFIX_PRELUDE + """
       prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

       
       INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
       {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> rdf:type bbkmm:Museum.
       <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasproject_id  \""""+projectid+"""\"^^xsd:string"""
    if(nameofmuseum!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasName_of_museum  \""""+nameofmuseum+"""\"^^xsd:string"""
    if (alternatemuseumname != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAlternative_museum_name  \"""" + alternatemuseumname + """\"^^xsd:string"""
    if (alternatemuseumnamesource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAlternative_museum_name_source  \"""" + alternatemuseumnamesource + """\"^^xsd:string"""
    if(latitude!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasLatitude  """+latitude
    if(longitude!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasLongitude """+longitude

    if (yearmuseumfirstdocumentedsource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasYear_museum_first_documented_source  \"""" + yearmuseumfirstdocumentedsource + """\"^^xsd:string"""
    if(primaryprovenanceofdata!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data/id/82/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data>.
        <http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data/id/82/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data_New>.
        <http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data/id/82/"""+projectid+"""> bbkmm:hasPrimary_provenance_of_data \""""+primaryprovenanceofdata+"""\"^^xsd:string.
        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defPrimary_provenance_of_data <http://bbk.ac.uk/MuseumMapProject/def/Primary_provenance_of_data/id/82/"""+projectid+""">"""
    if(addressline1!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasAddress_line_1 \""""+addressline1+"""\"^^xsd:string"""
    if (addressline2 != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAddress_line_2 \"""" + addressline2 + """\"^^xsd:string"""
    if (addressline3 != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAddress_line_3 \"""" + addressline3 + """\"^^xsd:string"""
    if(townorcity!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasTown_or_City \""""+townorcity+"""\"^^xsd:string"""

    if (postcode != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasPostcode \"""" + postcode + """\"^^xsd:string"""

    query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasAdmin_hierarchy \""""

    if(admincountry!=''):
        print("added country")
        query=query+"""/"""+admincountry
    if(adminwelshua!=''):
        print("added welshua")
        query = query + """/""" + adminwelshua
    if(adminscottishcouncilarea!=''):
        print("added scottishca")
        query = query + """/""" + adminscottishcouncilarea
    if(adminnilocgovdistrict!=''):
        print("added locgovdist")
        query = query + """/""" + adminnilocgovdistrict
    if(adminenglishregion!=''):
        print("added engregion")
        query = query + """/""" + adminenglishregion
    if(adminenglishcounty!=''):
        print("added engcounty")
        query = query + """/""" + adminenglishcounty
    if(adminenglishua!=''):
        print("added engua")
        query = query + """/""" + adminenglishua
    if(adminenglishca!=''):
        print("added engca")
        query = query + """/""" + adminenglishca
    if(adminenglishdistrictorborough!='')and not ("\n" in adminenglishdistrictorborough):
        print("added engdistorbour")
        query = query + """/""" + adminenglishdistrictorborough

    query=query+"""\"^^xsd:string"""
    if (admincountry != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasRegion_country  \""""+admincountry+"""\"^^xsd:string"""
        if(admincountry=='England'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/England>"""
        if (admincountry == 'Scotland'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Scotland>"""
        if (admincountry == 'Wales'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Wales>"""
        if (admincountry == 'Isle of Man'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Isle_of_Man>"""
        if (admincountry == 'Channel Islands'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Channel_Islands>"""
        if (admincountry == 'Northern Ireland'):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Northern_Ireland>"""
    if (adminwelshua != ''):
        welshregioncode="http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/"+adminwelshua[:-11].replace(" ", "_")
        secondwelshregioncode=welshregioncode+"_Welsh_UA"
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:refersToWelsh_UA <"""+welshregioncode+""">.
        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:refersToWelsh_UA <"""+secondwelshregioncode+""">"""
    if (adminscottishcouncilarea != ''):
        scottishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/" + adminscottishcouncilarea[:-24].replace(" ", "_")
        secondscottishregioncode = scottishregioncode + "_Scottish_Council_Area"
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToScottish_Council_Area <""" + scottishregioncode + """>.
                <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToScottish_Council_Area <""" + secondscottishregioncode + """>"""
    if (adminnilocgovdistrict != ''):
        niregioncode = "http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/" + adminnilocgovdistrict[:-22].replace(" ","_")
        secondniregioncode = niregioncode + "_NI_Loc_Gov_District"
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToNI_Loc_Gov_District <""" + niregioncode + """>.
                        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToNI_Loc_Gov_District <""" + secondniregioncode + """>"""
    if (adminenglishregion != ''):
        engregioncode=''
        secondenglishregioncode=''
        if(adminenglishregion=='East Midlands (English Region)'):
            engregioncode="http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands"
            secondenglishregioncode="http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands_English_Region"
        if(adminenglishregion=='East of England (English Region)'):
            engregioncode ="http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England_English_Region"
        if(adminenglishregion=='London (English Region)'):
            engregioncode ="http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London_English_Region"
        if(adminenglishregion=='North East (English Region)'):
            engregioncode ="http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East_English_Region"
        if (adminenglishregion == 'North West (English Region)'):
            engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West_English_Region"
        if (adminenglishregion == 'South East (English Region)'):
            engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East_English_Region"
        if (adminenglishregion == 'South West (English Region)'):
            engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West_English_Region"
        if (adminenglishregion == 'West Midlands (English Region)'):
            engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands_English_Region"
        if (adminenglishregion == 'Yorkshire and The Humber (English Region)'):
            engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber"
            secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber_English_Region"
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:refersToEnglish_Region  <"""+engregioncode+""">.
        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:refersToEnglish_Region  <"""+secondenglishregioncode+""">"""
    if (adminenglishcounty != ''):
        englishcountycode = "http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/" + adminenglishcounty[:-17].replace(" ", "_")
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_County <""" + englishcountycode + """>"""
    if (adminenglishua != ''):
        englishuacode = "http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/" + adminenglishua[:-13].replace(" ", "_")
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_UA <""" + englishuacode + """>"""
    if (adminenglishca != ''):
        englishcacode = "http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/" + adminenglishca[:-13].replace(" ","_")
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_CA <""" + englishcacode + """>"""
    if (adminenglishdistrictorborough != ''):
        englishdistrictorboroughcode = "http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/" + adminenglishdistrictorborough[:-30].replace(" ","_")
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_District_or_Borough <""" + englishdistrictorboroughcode + """>"""

    if(yearclosed!=''):
        if(len(yearclosed.split(":"))==2):
            uppervalue=yearclosed.split(":")[1]
            lowervalue = yearclosed.split(":")[0]
        else:
            uppervalue=yearclosed
            lowervalue=yearclosed
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/110/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/LowerValue>.
            <http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/110/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>  \""""+lowervalue+"""\"^^<http://www.w3.org/2001/XMLSchema#anyType>.
            <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/111/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/UpperValue>.
            <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/111/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue> \""""+uppervalue+"""\"^^<http://www.w3.org/2001/XMLSchema#anyType>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/107/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/ValueRange>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/107/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasDataType> "xsd:positiveInteger"^^<http://www.w3.org/2001/XMLSchema#string>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/107/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange> <http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/110/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/107/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange> <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/111/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/Year_closed/id/108/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Year_closed>.
            <http://bbk.ac.uk/MuseumMapProject/def/Year_closed/id/108/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/107/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed> <http://bbk.ac.uk/MuseumMapProject/def/Year_closed/id/108/""" + projectid + """>"""
    if(yearopened!=''):
        if (len(yearopened.split(":"))==2):
            youppervalue = yearopened.split(":")[1]
            yolowervalue = yearopened.split(":")[0]
        else:
            youppervalue = yearopened
            yolowervalue = yearopened
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/103/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/LowerValue>.
            <http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/103/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>  \""""+yolowervalue+"""\"^^<http://www.w3.org/2001/XMLSchema#anyType>.
            <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/104/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/UpperValue>.
            <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/104/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue>  \""""+youppervalue+"""\"^^<http://www.w3.org/2001/XMLSchema#anyType>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/100/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/ValueRange>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/100/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasDataType> "xsd:positiveInteger"^^<http://www.w3.org/2001/XMLSchema#string>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/100/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange> <http://bbk.ac.uk/MuseumMapProject/def/LowerValue/id/103/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/100/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange> <http://bbk.ac.uk/MuseumMapProject/def/UpperValue/id/104/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/Year_opened/id/101/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Year_opened>.
            <http://bbk.ac.uk/MuseumMapProject/def/Year_opened/id/101/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/ValueRange/id/100/""" + projectid + """>.
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened> <http://bbk.ac.uk/MuseumMapProject/def/Year_opened/id/101/""" + projectid + """>"""
    if (yearopenedsource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasYear_opened_source \"""" + yearopenedsource + """\"^^xsd:string"""
    if (yearclosedsource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasYear_closed_source \"""" + yearclosedsource + """\"^^xsd:string"""
    if (founder != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasFounder \"""" + founder + """\"^^xsd:string"""
    if (foundersource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasFounder_source \"""" + foundersource + """\"^^xsd:string"""
    if (governancesource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasGovernance_source \"""" + governancesource + """\"^^xsd:string"""
    if (accreditationsource != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAccreditation_source \"""" + accreditationsource + """\"^^xsd:string"""
    if (notes != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasNotes \"""" + notes + """\"^^xsd:string"""
    if (regioncountry != ''):
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country \"""" + regioncountry + """\"^^xsd:string"""
    if(subjectmatter!=''):
        primesubjectmatter=''
        if(len(subjectmatter.split("-"))==2):
            primesubjectmatter=subjectmatter.split("-")[0].replace(" ", "_")
        else:
            primesubjectmatter=subjectmatter.replace(" ", "_")
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:defSubject_Matter  <http://bbk.ac.uk/MuseumMapProject/def/"""+subjectmatter.replace(" ", "_")+""">.
            <http://bbk.ac.uk/MuseumMapProject/def/defClassClassification_2018/id/93/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/defClassClassification_2018>.
            <http://bbk.ac.uk/MuseumMapProject/def/"""+primesubjectmatter+"""/id/105/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/"""+primesubjectmatter+""">.
            <http://bbk.ac.uk/MuseumMapProject/def/"""+primesubjectmatter+"""/id/105/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/defClassClassification_2018/id/93/""" + projectid + """>"""
        if(primesubjectmatter!=subjectmatter.replace(" ", "_")):
            query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/"""+subjectmatter.replace(" ", "_")+"""/id/153/""" + projectid + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/"""+subjectmatter.replace(" ", "_")+""">.
            <http://bbk.ac.uk/MuseumMapProject/def/"""+subjectmatter.replace(" ", "_")+"""/id/153/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/"""+primesubjectmatter+"""/id/105/""" + projectid + """>"""
    if(accreditation!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Accreditation/id/243/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation>"""
        if(accreditation=="Unaccredited"):
            query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Accreditation/id/243/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Unaccredited>"""
        else:
            query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Accreditation/id/243/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Accredited>"""

        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Accreditation/id/243/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasAccreditation> \""""+accreditation+"""\"^^<http://www.w3.org/2001/XMLSchema#string>.
        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> <http://bbk.ac.uk/MuseumMapProject/def/defAccreditation> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation/id/243/"""+projectid+""">"""
    if(governance!=''):
        primegovernance = ''
        if (len(governance.split("-"))==2):
            primegovernance = governance.split("-")[0].replace(" ", "_")
        else:
            primegovernance = governance.replace(" ", "_")
        query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGovernance  <http://bbk.ac.uk/MuseumMapProject/def/"""+governance.replace(" ", "_")+""">.
                    <http://bbk.ac.uk/MuseumMapProject/def/defClassGovernance/id/246/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/defClassGovernance>.
                    <http://bbk.ac.uk/MuseumMapProject/def/"""+primegovernance+"""/id/247/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>	<http://bbk.ac.uk/MuseumMapProject/def/"""+primegovernance+""">.
                    <http://bbk.ac.uk/MuseumMapProject/def/"""+primegovernance+"""/id/247/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/defClassGovernance/id/246/"""+projectid+""">"""
        if (primegovernance != governance.replace(" ", "_")):
            query = query + """.<http://bbk.ac.uk/MuseumMapProject/def/"""+governance.replace(" ", "_")+"""/id/252/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/"""+governance.replace(" ", "_")+""">.
                    <http://bbk.ac.uk/MuseumMapProject/def/"""+governance.replace(" ", "_")+"""/id/252/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf> <http://bbk.ac.uk/MuseumMapProject/def/"""+primegovernance+"""/id/247/"""+projectid+""">"""
    if(size!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Size/id/304/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/Size>.

            <http://bbk.ac.uk/MuseumMapProject/def/Size/id/304/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/Size_"""+size+""">.

            <http://bbk.ac.uk/MuseumMapProject/def/Size/id/304/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasSize>  \""""+size+"""\"^^<http://www.w3.org/2001/XMLSchema#string>.

            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defSize <http://bbk.ac.uk/MuseumMapProject/def/Size/id/304/"""+projectid+""">"""
    if(media!=''):
        query=query+""".<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasmedia """+media

    if (admincountry != 'Isle of Man') and (admincountry != 'Channel Islands'):
        query=query+""" .<http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code/id/384/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code/id/384/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code_"""+geodemographicgroupcode[-2:]+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code/id/384/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_code> \""""+geodemographicsubgroupcode+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_subgroup_code <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code/id/384/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup/id/410/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup/id/410/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_"""+geodemographicsubgroup.replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup/id/410/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup> \""""+geodemographicsubgroup+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_subgroup <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup/id/410/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long/id/464/"""+projectid+""">  	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long>.
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long/id/464/"""+projectid+""">  	<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_"""+geodemographicgroupcode[-2:]+geodemographicsubgrouplong.split("-")[1].replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long/id/464/"""+projectid+"""> <hhttp://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_name_long> \""""+geodemographicsubgrouplong+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_subgroup_name_long <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long/id/464/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group/id/366/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group/id/366/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_"""+geodemographicgroup.replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group/id/366/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group> \""""+geodemographicgroup+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_group <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group/id/366/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code/id/348/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code/id/348/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code_"""+geodemographicgroupcode[-2:]+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code/id/348/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_code> \""""+geodemographicgroupcode+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_group_code <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code/id/348/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long/id/446/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long/id/446/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_"""+geodemographicgrouplong.split("-")[0][-2:]+geodemographicgrouplong.split("-")[1].replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long/id/446/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_name_long> \""""+geodemographicgrouplong+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_group_name_long <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long/id/446/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup/id/338/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup/id/338/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_"""+geodemographicsupergroup.replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup/id/338/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup> \""""+geodemographicsupergroup+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_supergroup <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup/id/338/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code/id/328/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code/id/328/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code_r> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code/id/328/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_code> \""""+geodemographicsupergroupcode+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_supergroup_code <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code/id/328/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long/id/436/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long/id/436/"""+projectid+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_r"""+geodemographicsupergrouplong.split("-")[1].replace(" ", "_")+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long/id/436/"""+projectid+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_name_long> \""""+geodemographicsupergrouplong+"""\"^^<http://www.w3.org/2001/XMLSchema#string> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:defGeodemographic_supergroup_name_long <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long/id/436/"""+projectid+"""> .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_housing """+deprivationindexhousing+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_employment """+deprivationindexemployment+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_crime """+deprivationindexcrime+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_services """+deprivationindexservices+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_income """+deprivationindexincome+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_health """+deprivationindexhealth+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index_education """+deprivationindexeducation+""" .
            <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasDeprivation_index """+deprivationindex
    query = query + """}"""




       #?museum ?p ?o }


       ##"""
    #query = query.replace("${MUSEUMID}", museumid)
    print query
    ##return
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if (yearmuseumfirstdocumented != ''):
        query = definitions.RDF_PREFIX_PRELUDE + """
               prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


               INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
               {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/"""+projectid+"""> bbkmm:hasYear_museum_first_documented """+yearmuseumfirstdocumented+""" }"""
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
   ## pp.pprint(results)
    return

    ##return results


def editMuseum(filepath, oldname, Latitude, Longitude, Altpostcode):
    dircsv = os.path.dirname(os.path.realpath(__file__))
    file = open(dircsv + '/editmusfiles/editindex.txt', 'r')
    print("unpickling")
    idindex = pickle.load(file)
    print("idindex")
    print(idindex)
    with open(filepath, 'rb') as csvfile:
        linereader = csv.reader(csvfile, delimiter='$', quotechar='"')
       ## rowtitle = next(linereader)

        row0 = next(linereader)
        domusidentifier = row0[0]
        projectid = row0[1]
        editid="mm.Edit."+str(idindex)
        idindex = idindex + 1
        ##file.close()
        file = open(dircsv + '/editmusfiles/editindex.txt', 'w')
        pickle.dump(idindex, file)
        primaryprovenanceofdata = row0[2]
        identifierusedinsourcedb = row0[3]
        nameofmuseum = row0[4]
        alternatemuseumname = row0[5]
        alternatemuseumnamesource = row0[6]
        addressline1 = row0[7]
        addressline2 = row0[8]
        addressline3 = row0[9]
        townorcity = row0[10]
        postcode = row0[11]
        latitude = Latitude
        longitude = Longitude
        yearmuseumfirstdocumented = row0[14]
        yearmuseumfirstdocumentedsource = row0[15]
        yearopened = row0[16]
        yearopenedsource = row0[17]
        yearclosed = row0[18]
        yearclosedsource = row0[19]
        founder = row0[20]
        foundersource = row0[21]
        subjectmatter = row0[22]
        domussubjectmatter = row0[23]
        accreditation = row0[24]
        accreditationsource = row0[25]
        governance = row0[26]
        governancesource = row0[27]
        acesizedesignation = row0[28]
        acesizesource = row0[29]
        aimsizedesignation = row0[30]
        aimsizesource = row0[31]
        notesinternal = row0[32]
        notes = row0[33]
        size = row0[34]
        sizeprov = row0[35]
        media = row0[36]
        oldnameofmuseum=oldname
        admincountry = ""
        adminwelshua = ""
        adminscottishcouncilarea = ""
        adminnilocgovdistrict = ""
        adminenglishregion = ""
        adminenglishcounty = ""
        adminenglishua = ""
        adminenglishca = ""
        adminenglishdistrictorborough = ""
        deprivationindex = ""
        deprivationindexincome = ""
        deprivationindexemployment = ""
        deprivationindexeducation = ""
        deprivationindexhealth = ""
        deprivationindexcrime = ""
        deprivationindexhousing = ""
        deprivationindexservices = ""
        regioncountry = ""
        geodemographicsupergroupcode = ""
        geodemographicsupergroup = ""
        geodemographicgroupcode = ""
        geodemographicgroup = ""
        geodemographicsubgroupcode = ""
        geodemographicsubgroup = ""
        geodemographicsupergrouplong = ""
        geodemographicgrouplong = ""
        geodemographicsubgrouplong = ""
        print (nameofmuseum)
        print(postcode)

        sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
        ##pp = pprint.PrettyPrinter(indent=4)

        if (nameofmuseum == '')or (projectid==''):
            return
        if (nameofmuseum != oldnameofmuseum):
            query = definitions.RDF_PREFIX_PRELUDE + """
               prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


               DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
               {?x ?y ?z}}
               WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasName_of_museum}   ?x ?y ?z}"""


        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """>
            INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
            { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasName_of_museum  \"""" + nameofmuseum + """\"^^xsd:string}"""
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()




        if(founder!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasFounder}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasFounder  \"""" + founder + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(foundersource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasFounder_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasFounder_source  \"""" + foundersource + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(alternatemuseumname!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAlternative_museum_name}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAlternative_museum_name  \"""" + alternatemuseumname + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(alternatemuseumnamesource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAlternative_museum_name_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAlternative_museum_name_source  \"""" + alternatemuseumnamesource + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(yearopenedsource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasYear_opened_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasYear_opened_source  \"""" + yearopenedsource + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(yearclosedsource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasYear_closed_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasYear_closed_source  \"""" + yearclosedsource + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(governancesource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasGovernance_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasGovernance_source  \"""" + governancesource + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(accreditationsource!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAccreditation_source}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAccreditation_source  \"""" + accreditation + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
        if(postcode!=''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 

                                    
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasPostcode}   ?x ?y ?z}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasPostcode  \"""" + postcode + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()


            if (latitude != ''):
                query = definitions.RDF_PREFIX_PRELUDE + """
                               prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                               DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                               {?x ?y ?z}}
                              WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasLatitude}   ?x ?y ?z}"""


                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print query
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasLatitude  """ + latitude + """}"""
                                              

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print query
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()



            if (longitude != ''):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                 WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasLongitude}   ?x ?y ?z}"""


                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print query
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasLongitude  """ + longitude + """}"""
                                                               

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print query
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()









            
            with open(dircsv + '/../../mm_input_maindatasheet_V10_2018_12_04.csv', 'a') as mainfile:
                mainwriter = csv.writer(mainfile, delimiter='$',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
                mainwriter.writerow('')
                for item in row0[:-1]:
                    if (item == ''):
                        mainfile.write(item)
                        mainfile.write('$')
                    elif (item==projectid):
                        mainfile.write('"')
                        mainfile.write(editid)
                        mainfile.write('"')
                        mainfile.write('$')
                    elif(item==postcode):
                        if(Altpostcode!=""):
                            mainfile.write('"')
                            mainfile.write(Altpostcode)
                            mainfile.write('"')
                            mainfile.write('$')
                        else:
                            mainfile.write('"')
                            mainfile.write(item)
                            mainfile.write('"')
                            mainfile.write('$')
                    else:
                        mainfile.write('"')
                        mainfile.write(item)
                        mainfile.write('"')
                        mainfile.write('$')

                mainfile.write(media)
            if(Altpostcode!=""):
              postcode = Altpostcode
            ## os.system("ls -l")
            os.system(
                "python "+dircsv + "/../../location_Enumbers.py "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv | grep  \*\? | sed s/\*\?\#\?//g > "+dircsv + "/../../geobaseU#.csv")
            os.system(
                "python "+dircsv + "/../../england_Enumbers.py "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv | grep \*\? | cut -c 7- > "+dircsv + "/../../geobaseE.csv")
            os.system("sed 's/\"//g' "+dircsv + "/../../geobaseE.csv > "+dircsv + "/../../geobaseF.csv")
            os.system("cat "+dircsv + "/../../geobaseF.csv "+dircsv + "/../../geobaseU#.csv > "+dircsv + "/../../geobaseA.csv")

            postfront = postcode[:2]
            if(postfront=="GY" or postfront =="JE"):
                admincountry="Channel Islands"
            elif(postfront=="IM"):
                admincountry="Isle of Man"
            else:
              with open(dircsv + '/../../geobaseA.csv', 'rb') as adminfile:
                for line in adminfile:
                    linearr = line.split(',')
                    ##print(linearr[0])
                    if (linearr[0] == editid) or (linearr[0] == "\""+editid+"\""):
                        admincountry = linearr[1].split(':')[0]
                        adminwelshua = linearr[2].split(':')[0]
                        adminscottishcouncilarea = linearr[3].split(':')[0]
                        adminnilocgovdistrict = linearr[4].split(':')[0]
                        adminenglishregion = linearr[5].split(':')[0]
                        adminenglishcounty = linearr[6].split(':')[0]
                        adminenglishua = linearr[7].split(':')[0]
                        adminenglishca = linearr[8].split(':')[0]
                        adminenglishdistrictorborough = linearr[9].split(':')[0]
        # print (adminenglishregion)
        # print (adminenglishdistrictorborough)
            lsoacode = ""
            ladcode = ""
            with open(dircsv + '/../../json/NSPL_AUG_2017_UK.csv', 'rb') as postcodefile:
                for line in postcodefile:
                    linearr2 = line.split(',')
                    secondpostcode = "\"" + postcode + "\""
                    if (linearr2[2] == secondpostcode):
                        lsoacode = linearr2[24]
                        ladcode = linearr2[11]
            print(secondpostcode)
            lsoasplit = lsoacode.split("\"")
            lsoacode = lsoasplit[1]
            ladsplit = ladcode.split("\"")
            ladcode = ladsplit[1]
            print(lsoacode)
            print(ladcode)
            with open(dircsv + '/../../museumsall_gss_lsoa2011.tsv', 'a') as lsoafile:
                mainwriter2 = csv.writer(lsoafile, delimiter='\t')
                mainwriter2.writerow('')
                lsoafile.write(editid + '\t' + lsoacode)
            with open(dircsv + '/../../museumsall_gss_lad2011.tsv', 'a') as ladfile:
                mainwriter3 = csv.writer(ladfile, delimiter='\t')
                mainwriter3.writerow('')
                ladfile.write(editid + '\t' + ladcode)

            os.system(
                "python "+dircsv + "/../../addColumnsWithIndexFile.py "+dircsv + "/../../deprivation_index_deciles_merged_uk_2017_lsoa2011-1.csv "+dircsv + "/../../museumsall_gss_lsoa2011.tsv "+dircsv + "/../../deprivheader.csv "+dircsv + "/../../mm_input_maindatasheet_V10_2018_12_04.csv > "+dircsv + "/../../maininput2.csv")
            os.system(
                "python "+dircsv + "/../../addColumnsWithIndexFile.py "+dircsv + "/../../output_area_class-lad2011.tsv "+dircsv + "/../../museumsall_gss_lad2011.tsv "+dircsv + "/../../outputheader.csv "+dircsv + "/../../maininput2.csv > "+dircsv + "/../../maininput3.csv")
            if (admincountry != 'Isle of Man') and (admincountry != 'Channel Islands'):
                with open(dircsv + '/../../maininput3.csv', 'rb') as mainfile3:
                    counter = 1
                    for line in mainfile3:
                        if (counter < 6):
                            counter = counter + 1
                        else:
                            linearr = line.split('$')

                            ##print(linearr[1])
                            projid = linearr[1].split('\"')[1]
                            ##print(projid)

                            if (projid == editid):
                                deprivationindex = linearr[37]
                                deprivationindexincome = linearr[38]
                                deprivationindexemployment = linearr[39]
                                deprivationindexeducation = linearr[40]
                                deprivationindexhealth = linearr[41]
                                deprivationindexcrime = linearr[42]
                                deprivationindexhousing = linearr[43]
                                deprivationindexservices = linearr[44]
                                print deprivationindex
                                print deprivationindexincome
                                print deprivationindexemployment
                                print deprivationindexeducation
                                print deprivationindexhealth
                                print deprivationindexcrime
                                print deprivationindexhousing
                                print deprivationindexservices
                                if(postfront=="GY" or postfront =="JE"):
                                    regioncountry="Channel Islands"
                                elif(postfront=="IM"):
                                    regioncountry="Isle of Man"
                                else:
                                  regioncountry = linearr[45].split('\"')[1]
                                  geodemographicsupergroupcode = linearr[46].split('\"')[1]
                                  geodemographicsupergroup = linearr[47].split('\"')[1]
                                  geodemographicgroupcode = linearr[48].split('\"')[1]
                                  geodemographicgroup = linearr[49].split('\"')[1]
                                  geodemographicsubgroupcode = linearr[50].split('\"')[1]
                                  geodemographicsubgroup = linearr[51].split('\"')[1]
                                  geodemographicsupergrouplong = linearr[52].split('\"')[1]
                                  geodemographicgrouplong = linearr[53].split('\"')[1]
                                  geodemographicsubgrouplong = linearr[54].split('\"')[1]

            print regioncountry
            print geodemographicsupergroupcode
            print geodemographicsupergroup
            print geodemographicgroupcode
            print geodemographicgroup
            print geodemographicsubgroupcode
            print geodemographicsubgroup
            print geodemographicsupergrouplong
            print geodemographicgrouplong
            print geodemographicsubgrouplong


            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 
                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAdmin_hierarchy}   ?x ?y ?z}"""



            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)

            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 
                                                INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>

                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAdmin_hierarchy \""""
            if (admincountry != ''):
                query = query + """/""" + admincountry
            if (adminwelshua != ''):
                query = query + """/""" + adminwelshua
            if (adminscottishcouncilarea != ''):
                query = query + """/""" + adminscottishcouncilarea
            if (adminnilocgovdistrict != ''):
                query = query + """/""" + adminnilocgovdistrict
            if (adminenglishregion != ''):
                query = query + """/""" + adminenglishregion
            if (adminenglishcounty != ''):
                query = query + """/""" + adminenglishcounty
            if (adminenglishua != ''):
                query = query + """/""" + adminenglishua
            if (adminenglishca != ''):
                query = query + """/""" + adminenglishca
            if (adminenglishdistrictorborough != '')and not ("\n" in adminenglishdistrictorborough):
                query = query + """/""" + adminenglishdistrictorborough

            query = query + """\"^^xsd:string}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print query
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)

            results = sparql.query().convert()

            if (admincountry != ''):
                if (admincountry != 'England'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                 WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                    print query
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"""" + admincountry + """\"^^xsd:string}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()


                if (admincountry == 'England'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                     WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/England>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print query
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()


                if (admincountry == 'Scotland'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Scotland>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()


                if (admincountry == 'Wales'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Wales>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()


                if (admincountry == 'Isle of Man'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Isle_of_Man>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()

                if (admincountry == 'Channel Islands'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Channel_Islands>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()

                if (admincountry == 'Northern Ireland'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    DELETE {GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {?x ?y ?z}}
                                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToCountry}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                    INSERT DATA into GRAPH <""" + \
                            app.config[
                                'DEFAULTGRAPH'] + """>
                                                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToCountry  <http://bbk.ac.uk/MuseumMapProject/def/Country/id/n3/Northern_Ireland>}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                        DELETE {GRAPH <""" + \
                    app.config[
                        'DEFAULTGRAPH'] + """>
                                                        {?x ?y ?z}}
                                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToWelsh_UA}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                    DELETE {GRAPH <""" + \
                    app.config[
                        'DEFAULTGRAPH'] + """>
                                                    {?x ?y ?z}}
                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToScottish_Council_Area}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            DELETE {GRAPH <""" + \
                    app.config[
                        'DEFAULTGRAPH'] + """>
                                            {?x ?y ?z}}
                                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToNI_Loc_Gov_District}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            if (adminwelshua != ''):
                welshregioncode = "http://bbk.ac.uk/MuseumMapProject/def/Welsh_UA/id/n4/" + adminwelshua[:-11].replace(
                    " ", "_")
                secondwelshregioncode = welshregioncode + "_Welsh_UA"


                query = definitions.RDF_PREFIX_PRELUDE + """
                                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                                INSERT DATA into GRAPH <""" + \
                        app.config[
                            'DEFAULTGRAPH'] + """>
                                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToWelsh_UA <""" + welshregioncode + """>.
                <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToWelsh_UA <""" + secondwelshregioncode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()




            if (adminscottishcouncilarea != ''):
                scottishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/Scottish_Council_Area/id/n5/" + adminscottishcouncilarea[
                                                                                                            :-24].replace(
                    " ",
                    "_")
                secondscottishregioncode = scottishregioncode + "_Scottish_Council_Area"

                query = definitions.RDF_PREFIX_PRELUDE + """
                                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                            INSERT DATA into GRAPH <""" + \
                        app.config[
                            'DEFAULTGRAPH'] + """>
                                                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToScottish_Council_Area <""" + scottishregioncode + """>.
                        <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToScottish_Council_Area <""" + secondscottishregioncode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()





            if (adminnilocgovdistrict != ''):
                niregioncode = "http://bbk.ac.uk/MuseumMapProject/def/NI_Loc_Gov_District/id/n6/" + adminnilocgovdistrict[
                                                                                                    :-22].replace(" ",
                                                                                                                  "_")
                secondniregioncode = niregioncode + "_NI_Loc_Gov_District"
                query = definitions.RDF_PREFIX_PRELUDE + """
                                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                        INSERT DATA into GRAPH <""" + \
                        app.config[
                            'DEFAULTGRAPH'] + """>
                                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToNI_Loc_Gov_District <""" + niregioncode + """>.
                                <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToNI_Loc_Gov_District <""" + secondniregioncode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()




            if (adminenglishregion != ''): ##IMPORTANT!!!!!!!: INSERT HERE CALCULATIONS FOR HASREGIONCOUNTRY WHICH IS THW ENGLISH REGION MINUS THE STUFF IN BRACKETS FOLLOWED BY XSD STRING. The regioncountry data has no underscore when two words present
                ########################################
    ###############DONT FORGET TO UPDATE UPLOADMUSEUM WITH THIS ALSO
                ##################################
                ########################################
                ##################################
                ###############################
                ############################
                ##IMPORTANT!!!!!!!: INSERT HERE CALCULATIONS FOR HASREGIONCOUNTRY WHICH IS THe ENGLISH REGION MINUS THE STUFF IN BRACKETS FOLLOWED BY XSD STRING The regioncountry data has no underscore when two words present
                engregioncode = ''
                secondenglishregioncode = ''
                if (adminenglishregion == 'East Midlands (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"East Midlands\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()

                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_Midlands_English_Region"
                if (adminenglishregion == 'East of England (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"East of England\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/East_of_England_English_Region"
                if (adminenglishregion == 'London (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"London\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/London_English_Region"
                if (adminenglishregion == 'North East (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"North East\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_East_English_Region"
                if (adminenglishregion == 'North West (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"North West\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/North_West_English_Region"
                if (adminenglishregion == 'South East (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"South East\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_East_English_Region"
                if (adminenglishregion == 'South West (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"South West\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/South_West_English_Region"
                if (adminenglishregion == 'West Midlands (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"West Midlands\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/West_Midlands_English_Region"
                if (adminenglishregion == 'Yorkshire and The Humber (English Region)'):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                                {?x ?y ?z}}
                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasRegion_country}   ?x ?y ?z}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                INSERT DATA into GRAPH <""" + app.config[
                        'DEFAULTGRAPH'] + """>
                                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasRegion_country  \"Yorkshire and The Humber\"^^xsd:string}"""

                    # ?museum ?p ?o }

                    ##"""
                    # query = query.replace("${MUSEUMID}", museumid)
                    print(query)
                    sparql.setQuery(query)
                    sparql.setMethod("POST")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    engregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber"
                    secondenglishregioncode = "http://bbk.ac.uk/MuseumMapProject/def/English_Region/id/n8/Yorkshire_and_The_Humber_English_Region"
                query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                            {?x ?y ?z}}
                                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToEnglish_Region}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_Region  <""" + engregioncode + """>.
                <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_Region  <""" + secondenglishregioncode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()




            if (adminenglishcounty != ''):
                englishcountycode = "http://bbk.ac.uk/MuseumMapProject/def/English_County/id/n7/" + adminenglishcounty[
                                                                                                    :-17].replace(" ",
                                                                                                                  "_")
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToEnglish_County}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_County <""" + englishcountycode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()



            if (adminenglishua != ''):
                englishuacode = "http://bbk.ac.uk/MuseumMapProject/def/English_UA/id/n10/" + adminenglishua[
                                                                                             :-13].replace(" ",
                                                                                                           "_")
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToEnglish_UA}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_UA <""" + englishuacode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()




            if (adminenglishca != ''):
                englishcacode = "http://bbk.ac.uk/MuseumMapProject/def/English_CA/id/n11/" + adminenglishca[
                                                                                             :-13].replace(" ",
                                                                                                           "_")
                query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToEnglish_CA}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_CA <""" + englishcacode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()




            if (adminenglishdistrictorborough != ''):
                englishdistrictorboroughcode = "http://bbk.ac.uk/MuseumMapProject/def/English_District_or_Borough/id/n9/" + adminenglishdistrictorborough[
                                                                                                                            :-30].replace(
                    " ", "_")
                query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                            {?x ?y ?z}}
                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:refersToEnglish_District_or_Borough}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:refersToEnglish_District_or_Borough <""" + englishdistrictorboroughcode + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()


            print(geodemographicgroupcode[-2:])

            if(geodemographicgroupcode[-2:]!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_code}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_code} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_code} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_code>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()


                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_code_""" + geodemographicgroupcode[-2:] + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_code> \"""" + geodemographicsubgroupcode + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ###########################################################################################
            if(geodemographicsubgroup!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_""" + geodemographicsubgroup.replace(" ", "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup> \"""" + geodemographicsubgroup + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ################################################################################################################
            if(geodemographicsubgrouplong!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_name_long}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_name_long} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_subgroup_name_long} VALUES ?a {<hhttp://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_name_long>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                if(geodemographicsubgrouplong!=''):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_subgroup_name_long_""" + geodemographicgroupcode[
                                                                                                                                                                                                                                                                     -2:] + \
                        geodemographicsubgrouplong.split("-")[1].replace(" ", "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <hhttp://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_subgroup_name_long> \"""" + geodemographicsubgrouplong + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ############################################################################################
            if(geodemographicgroup!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_""" + geodemographicgroup.replace(
                    " ", "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group> \"""" + geodemographicgroup + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ####################################################################################
            if(geodemographicgroupcode!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_code}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_code} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_code} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_code>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_code_""" + geodemographicgroupcode[-2:] + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_code> \"""" + geodemographicgroupcode + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            #####################################################################################
            if(geodemographicgrouplong!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_name_long}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_name_long} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_group_name_long} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_name_long>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                if(geodemographicgrouplong!=''):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_group_name_long_""" + \
                        geodemographicgrouplong.split("-")[0][-2:] + geodemographicgrouplong.split("-")[1].replace(" ",
                                                                                                                   "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_group_name_long> \"""" + geodemographicgrouplong + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ##############################################################################
            if(geodemographicsupergroup!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_""" + geodemographicsupergroup.replace(
                    " ", "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup> \"""" + geodemographicsupergroup + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            #####################################################################################################
            if(geodemographicsupergroupcode!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_code}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_code} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_code} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_code>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_code_r>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_code> \"""" + geodemographicsupergroupcode + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            ############################################################################################
            if(geodemographicsupergrouplong!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_name_long}  ?x ?y ?z}"""
                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                vard = sparql.query().convert()
                print("printing")
                print(vard)
                print("again")
                for result in vard["results"]["bindings"]:
                    vard2 = (result["z"]["value"])
                    break

                print(vard2)

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_name_long} VALUES ?a {<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGeodemographic_supergroup_name_long} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_name_long>}   ?x ?y ?z . ?z ?a ?b}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                if(geodemographicsupergrouplong!=''):
                    query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Geodemographic_supergroup_name_long_r""" + \
                        geodemographicsupergrouplong.split("-")[1].replace(" ", "_") + """>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasGeodemographic_supergroup_name_long> \"""" + geodemographicsupergrouplong + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            #################################################################################

            if(deprivationindexhousing!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_housing}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_housing """ + deprivationindexhousing + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexemployment!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                            {?x ?y ?z}}
                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_employment}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_employment """ + deprivationindexemployment + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexcrime!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_crime}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_crime """ + deprivationindexcrime + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexservices!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_services}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_services """ + deprivationindexservices + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexincome!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_income}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_income """ + deprivationindexincome + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexhealth!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_health}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_health """ + deprivationindexhealth + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindexeducation!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index_education}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index_education """ + deprivationindexeducation + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            if(deprivationindex!=""):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasDeprivation_index}   ?x ?y ?z}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasDeprivation_index """ + deprivationindex + """}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()










        if (addressline1 != ''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?x ?y ?z}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAddress_line_1}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                        {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAddress_line_1 \"""" + addressline1 + """\"^^xsd:string}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAddress_line_2}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAddress_line_2 \"""" + addressline2 + """\"^^xsd:string}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasAddress_line_3}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasAddress_line_3 \"""" + addressline3 + """\"^^xsd:string}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()





        if (townorcity != ''):
            query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                            {?x ?y ?z}}
                                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasTown_or_City}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasTown_or_City \"""" + townorcity + """\"^^xsd:string}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()




        if (yearclosed != ''):
            print(yearclosed)
            if (len(yearclosed.split(":")) == 2):
                uppervalue = yearclosed.split(":")[1]
                lowervalue = yearclosed.split(":")[0]
            else:
                uppervalue = yearclosed
                lowervalue = yearclosed

            print(uppervalue)
            query = definitions.RDF_PREFIX_PRELUDE + """
                                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                SELECT DISTINCT ?d FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>
                                    
                                                                       
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange>}    ?x ?y ?z. ?z ?a ?b .?b ?c ?d }"""
            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            vard = sparql.query().convert()
            print("printing")
            print(vard)
            print("again")
            for result in vard["results"]["bindings"]:
                vard2 =(result["d"]["value"])
                break

            print(vard2)

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?d ?e ?f}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange>} VALUES ?e {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>}   ?x ?y ?z. ?z ?a ?b .?b ?c ?d . ?d ?e ?f}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)

            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {<"""+vard2+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>  \"""" + lowervalue + """\"^^<http://www.w3.org/2001/XMLSchema#anyType>}"""


            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                            SELECT DISTINCT ?d FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange>}    ?x ?y ?z. ?z ?a ?b .?b ?c ?d }"""
            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            vard = sparql.query().convert()
            print("printing")
            print(vard)
            print("again")
            for result in vard["results"]["bindings"]:
                vard2 = (result["d"]["value"])
                break

            print(vard2)
            query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                            {?d ?e ?f}}
                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_closed>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange>} VALUES ?e {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue>}   ?x ?y ?z. ?z ?a ?b .?b ?c ?d . ?d ?e ?f}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                            INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                            {<"""+vard2+"""> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue>  \"""" + uppervalue + """\"^^<http://www.w3.org/2001/XMLSchema#anyType>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()




        if (yearopened != ''):
            if (len(yearopened.split(":")) == 2):
                youppervalue = yearopened.split(":")[1]
                yolowervalue = yearopened.split(":")[0]
            else:
                youppervalue = yearopened
                yolowervalue = yearopened
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        SELECT DISTINCT ?d FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange>}    ?x ?y ?z. ?z ?a ?b .?b ?c ?d }"""
            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            vard = sparql.query().convert()
            print("printing")
            print(vard)
            print("again")
            for result in vard["results"]["bindings"]:
                vard2 = (result["d"]["value"])
                break

            print(vard2)

            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?d ?e ?f}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerRange>} VALUES ?e {<http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>}   ?x ?y ?z. ?z ?a ?b .?b ?c ?d . ?d ?e ?f}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)

            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)

            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasLowerValue>  \"""" + yolowervalue + """\"^^<http://www.w3.org/2001/XMLSchema#anyType>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        SELECT DISTINCT ?d FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange>}    ?x ?y ?z. ?z ?a ?b .?b ?c ?d }"""
            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            vard = sparql.query().convert()
            print("printing")
            print(vard)
            print("again")
            for result in vard["results"]["bindings"]:
                vard2 = (result["d"]["value"])
                break

            print(vard2)
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?d ?e ?f}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {<http://bbk.ac.uk/MuseumMapProject/def/defRangeYear_opened>} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/isSubClassInstanceOf>} VALUES ?c {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperRange>} VALUES ?e {<http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue>}   ?x ?y ?z. ?z ?a ?b .?b ?c ?d . ?d ?e ?f}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                        {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasUpperValue>  \"""" + youppervalue + """\"^^<http://www.w3.org/2001/XMLSchema#anyType>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()##########################################################################################################################################################






        if (subjectmatter != ''):
            primesubjectmatter = subjectmatter.replace(" ","_")
            primesubjectmatter = primesubjectmatter.replace(":", "-")

            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?x ?y ?z}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSubject_Matter}   ?x ?y ?z}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                    {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:defSubject_Matter <http://bbk.ac.uk/MuseumMapProject/def/""" + primesubjectmatter + """>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()



        if (accreditation != ''):

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defAccreditation}  ?x ?y ?z}"""
            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            vard = sparql.query().convert()
            print("printing")
            print(vard)
            print("again")
            for result in vard["results"]["bindings"]:
                vard2 = (result["z"]["value"])
                break

            print(vard2)

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?z ?a ?b}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defAccreditation} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Unaccredited>}   ?x ?y ?z . ?z ?a ?b}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?z ?a ?b}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defAccreditation} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Accredited>}   ?x ?y ?z . ?z ?a ?b}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?z ?a ?b}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defAccreditation} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasAccreditation>}   ?x ?y ?z . ?z ?a ?b}"""



            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            if (accreditation == "Unaccredited"):
                query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                        {<"""+vard2+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Unaccredited>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()


            else:
                query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
                    'DEFAULTGRAPH'] + """>
                                            {<"""+vard2+"""> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://bbk.ac.uk/MuseumMapProject/def/Accreditation_Accredited>}"""

                # ?museum ?p ?o }

                ##"""
                # query = query.replace("${MUSEUMID}", museumid)
                print(query)
                sparql.setQuery(query)
                sparql.setMethod("POST")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()

            query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
                'DEFAULTGRAPH'] + """>
                                            {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasAccreditation> \"""" + accreditation + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
            print(query)
            sparql.setQuery(query)
            sparql.setMethod("POST")
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
















    if (governance != ''):
        primegovernance = ''

        primegovernance = governance.replace(" ", "_")
        primegovernance = primegovernance.replace(":", "-")


        query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                            {?x ?y ?z}}
                                            WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defGovernance}   ?x ?y ?z}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
            'DEFAULTGRAPH'] + """>
                                            {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:defGovernance <http://bbk.ac.uk/MuseumMapProject/def/""" + primegovernance + """>}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()


    if (size != ''):

        query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        SELECT DISTINCT ?z FROM <http://bbk.ac.uk/MuseumMapProject/graph/v10>


                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize}  ?x ?y ?z}"""
        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        vard = sparql.query().convert()
        print("printing")
        print(vard)
        print("again")
        for result in vard["results"]["bindings"]:
            vard2 = (result["z"]["value"])
            break

        print(vard2)

        query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?z ?a ?b}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Size_huge>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                        prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                        DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                        {?z ?a ?b}}
                                        WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Size_large>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Size_medium>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Size_small>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                    DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                    {?z ?a ?b}}
                                    WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?b {<http://bbk.ac.uk/MuseumMapProject/def/Size_unknown>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?z ?a ?b}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:defSize} VALUES ?a {<http://bbk.ac.uk/MuseumMapProject/def/hasSize>}   ?x ?y ?z . ?z ?a ?b}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()




        query = definitions.RDF_PREFIX_PRELUDE + """
                                            prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                            INSERT DATA into GRAPH <""" + app.config[
            'DEFAULTGRAPH'] + """>
                                            {<""" + vard2 + """> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://bbk.ac.uk/MuseumMapProject/def/Size_""" + size + """>}"""

            # ?museum ?p ?o }

            ##"""
            # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()




        query = definitions.RDF_PREFIX_PRELUDE + """
                                                    prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                                    INSERT DATA into GRAPH <""" + app.config[
            'DEFAULTGRAPH'] + """>
                                                    {<""" + vard2 + """> <http://bbk.ac.uk/MuseumMapProject/def/hasSize>  \"""" + size + """\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()







    if (media != ''):
        query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasmedia}   ?x ?y ?z}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config[
            'DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasmedia """+ media+"""}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    if (notes != ''):
        query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                DELETE {GRAPH <""" + app.config['DEFAULTGRAPH'] + """>
                                {?x ?y ?z}}
                                WHERE {VALUES ?x { <http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """>} VALUES ?y {bbkmm:hasNotes}   ?x ?y ?z}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        query = definitions.RDF_PREFIX_PRELUDE + """
                                prefix """ + definitions.PREFIX_WITHCOLON + """ <http://""" + definitions.RDFDEFURI + """> 


                                INSERT DATA into GRAPH <""" + app.config[
            'DEFAULTGRAPH'] + """>
                                {<http://bbk.ac.uk/MuseumMapProject/def/Museum/id/n0/""" + projectid + """> bbkmm:hasNotes \""""+ notes+"""\"^^<http://www.w3.org/2001/XMLSchema#string>}"""

        # ?museum ?p ?o }

        ##"""
        # query = query.replace("${MUSEUMID}", museumid)
        print(query)
        sparql.setQuery(query)
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()




    return "Done"

    ##query = query + """}"""

    # ?museum ?p ?o }

    ##"""
    # query = query.replace("${MUSEUMID}", museumid)
    ##print query
    ##sparql.setQuery(query)
    ##sparql.setMethod("POST")
    ##sparql.setReturnFormat(JSON)
    ##results = sparql.query().convert()
    ## pp.pprint(results)
    return


    # return results




#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Executes the supplied query by post
# Arguments:
#   @query    The query
#   Used for running updates

def executebypost(query):
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    pp = pprint.PrettyPrinter(indent=4)
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    pp.pprint(results)

    return results

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Creates update statement for data properties and supported abstractions
# Arguments:
#   @incol    Name of column (property) as defined in definitions or spreadsheet
#   @pid      Museum id eg mm.MDN.005
#   @newvalue New value to insert. Appropriate the data property of course as the raw value will be inserted
#
#Examples:
#qq=apputils.getUpdateStatementForCol(definitions.ACCREDITATION,pid,"Unaccredited") #List
#qq=apputils.getUpdateStatementForCol(definitions.SUBJECT_MATTER,pid,"War_and_conflict-Other") #Hier
#qq=apputils.getUpdateStatementForCol(definitions.POSTCODE,pid,"NICKSCODE") # data
#qq=apputils.getUpdateStatementForCol(definitions.YEAR_OPENED,pid,"1888:1898") #Range
#
def getUpdateStatementForCol(incol,pid,newvalue):

    rangequery=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
     WITH <"""+app.config['DEFAULTGRAPH']+""">
   DELETE { ?lr_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""LowerValue ?lv_${INCOL} .
            ?ur_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""UpperValue ?uv_${INCOL}
          }  

   INSERT { ?lr_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""LowerValue "${LOWER}"^^xsd:positiveInteger .
            ?ur_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""UpperValue "${HIGHER}"^^xsd:positiveInteger
          }  
   WHERE {
            ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+"""  "${PID}"^^xsd:string .
            ?museum    """+definitions.PREFIX_WITHCOLON+definitions.DEFRANGE+"""${INCOL} ?duri_${INCOL} .
               ?duri_${INCOL}  """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_${INCOL} .
               ?vr_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""LowerRange ?lr_${INCOL} .
               ?lr_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""LowerValue ?lv_${INCOL} .
               ?vr_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""UpperRange ?ur_${INCOL} .
               ?ur_${INCOL}    """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""UpperValue ?uv_${INCOL} 
             

         }
     \n """

#- - - - -

    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
     WITH <"""+app.config['DEFAULTGRAPH']+""">

     DELETE {  ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL}  ?pc }  
     INSERT {  ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL}  '${NEWVALUE}'^^xsd:string}  
 
    WHERE {
            ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+"""  '${PID}'^^xsd:string .
                    
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL}  ?pc 
  
}
    \n """


#- - - - -
    listquery=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
     WITH <"""+app.config['DEFAULTGRAPH']+""">

     DELETE {  ?def${INCOL}uri """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL} ?${INCOL} }  
     INSERT {  ?def${INCOL}uri """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL} '${NEWVALUE}'^^xsd:string}  
 
    WHERE {
            ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+"""  '${PID}'^^xsd:string .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.DEFNAME+"""${INCOL} ?def${INCOL}uri . 
            ?def${INCOL}uri """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+"""${INCOL} ?${INCOL}          
  
          }
    \n """


#- - - - -
    hierquery=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
     WITH <"""+app.config['DEFAULTGRAPH']+""">

     DELETE { ?museum """+definitions.PREFIX_WITHCOLON+definitions.DEFNAME+"""${INCOL} ?def${INCOL}uri }  
     INSERT { ?museum """+definitions.PREFIX_WITHCOLON+definitions.DEFNAME+"""${INCOL} """+definitions.PREFIX_WITHCOLON+"""${NEWVALUE} }  
 
    WHERE {
            ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+"""  '${PID}'^^xsd:string .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.DEFNAME+"""${INCOL} ?def${INCOL}uri 
  
          }
    \n """

#- - - - -

    col=getDefinedType(incol)

    if (not col in definitions.DATATYPEDICT):
	print "$$$$$$$$$$$$$$$$$$ "+col+" col not found"
	return ""
    elif (definitions.DATATYPEDICT[col] == definitions.DEFINED_RANGETYPE):
	if (newvalue.find(":") > 0):
	    parts=newvalue.split(":")
	    lower=parts[0]
	    higher=parts[1]
	else:
	    lower=newvalue
	    higher=newvalue

	query=rangequery.replace("${INCOL}",str(incol))
	query=query.replace("${LOWER}",str(lower))
	query=query.replace("${HIGHER}",str(higher))
	query=query.replace("${PID}",str(pid))

    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_LISTTYPE):
	query=listquery.replace("${INCOL}",str(incol))
	query=query.replace("${NEWVALUE}",str(newvalue))
	query=query.replace("${PID}",str(pid))


    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_HIERTYPE):
	query=hierquery.replace("${INCOL}",str(incol))
	query=query.replace("${NEWVALUE}",str(newvalue))
	query=query.replace("${PID}",str(pid))

    elif (definitions.DATATYPEDICT[col] in definitions.XML_TYPES_WITH_PREFIX):
        #  plain type
	query=query.replace("${INCOL}",str(incol))
	query=query.replace("${NEWVALUE}",str(newvalue))
	query=query.replace("${PID}",str(pid))

    elif (col in definitions.DATATYPEDICT and isDataClass(definitions.DATATYPEDICT[col])):
	print "$$$$$$$$$$ UPDATE NOT IMPLEMENTED FOR THIS DATATYPE "+col+"$$$$$$$$$$"
	query=""
    else:
	print "$$$$$$$$$$ ERROR UNKNOWN DATATYPE "+col+"$$$$$$$$$$"
	query=""

    return query


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Processes and methodologies can make good servants but are poor masters.
#    - Mark Dowd, John McDonald & Justin Schuh 
#      in "The Art of Software Security Assessment"
     
