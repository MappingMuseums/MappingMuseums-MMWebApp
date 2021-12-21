##
# @file
#  
#  This is an API service for the search front end to provide 
#  locations from the geo graph that matches the users characters
#  as they type.
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3


from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import definitions

from flask import current_app as app
import pprint
import traceback
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from flask_restful import Api, Resource, url_for
from flask.views import MethodView

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Admingeoservice(MethodView):


    yoptlist=[
	definitions.SUBJECT_MATTER,
	definitions.DOMUS_SUBJECTCLASSIFICATION,
	definitions.GOVERNANCE
	
	]

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Purpose: Returns a set of geonames matching the propertytodisplay parameters starting letters
# Arguments:
#  @propertytodisplay The starting letters to match

    def get(self, propertytodisplay):
	lcaseprop=propertytodisplay.lower()
	sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])

	queryold=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	
	SELECT DISTINCT  Str(?subname)  Str(?ssname) Str(?sssname) 
	FROM <"""+app.config['GEOADMINGRAPH']+""">


	WHERE { 
	?adm a bbkmm:Country .
	OPTIONAL{
	?adm bbkmm:contains ?sub .
	?sub  bbkmm:hasTypedName  ?subname .
	FILTER(STRSTARTS( LCASE(?subname),"""+'"'+lcaseprop+'"'+""")) 
	
	}
	OPTIONAL{
	?sub bbkmm:contains ?subsub .
	?subsub bbkmm:hasTypedName ?ssname .
	FILTER (STRSTARTS( LCASE(?ssname),"""+'"'+lcaseprop+'"'+""")) 
	}
	OPTIONAL {
	?subsub bbkmm:contains ?subsubsub .
	?subsubsub bbkmm:hasTypedName ?sssname
	FILTER (STRSTARTS( LCASE(?sssname),"""+'"'+lcaseprop+'"'+""")) 
	}
	}group by ?subname order by ?subname
              
        """
	query=definitions.RDF_PREFIX_PRELUDE+"""
	prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
	



	SELECT DISTINCT STR(?sname) 
	FROM <"""+app.config['GEOADMINGRAPH']+""">
	WHERE { 
	?adm bbkmm:hasTypedName  ?sname .
	?adm a ?clazz .
	
	FILTER(STRSTARTS( LCASE(?sname),"""+'"'+lcaseprop+'"'+""")) 


	}
	group by ?sname order by ?sname
              
        """
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	
	proplist=[]
	vars=results['head']['vars']
	    
	for res in results["results"]["bindings"]:
	    for item in vars:
		if (item in res):
		    proplist.append(str(res[item]["value"]))
	ps=set(proplist)    
	return sorted(list(ps))


