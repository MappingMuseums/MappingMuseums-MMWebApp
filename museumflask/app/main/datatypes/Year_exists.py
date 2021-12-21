##
# @file
#  
# Implementation of a datatype follows this interface which has to be implemented: 
# 
## Purpose:Returns SPARQL for a match condition filter on the data type
# Arguments:
# 
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator
#    def getMatchFilter(self,rcount,match,condition):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns SPARQL for a  condition filter on the data type
# Arguments:
# 
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator
#    def getCompareFilter(self,rcount,match,condition):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns SPARQL for a query on the datatype without filter
# Arguments:
# 
# @param col  columne name for datatype
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator
# @param matchcolumn not used, only here for compatibility
#    def getQuery(self,col,rcount,matchstring,condition,matchcolumn):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns type for the datatype to appear in search menu
#    def getSearchType(self):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns the list of select conditions for the comaparator search menu
#    def getGUIConditions(self):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Returns html code for search menu
#    def getWidget(self):
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Returns JS code associated with the HTML for the datatype
#    def getWidgetCode(self):
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
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""

"""


class Year_exists(object):
    

    _existsquery="""
  OPTIONAL {
     ?museum    bbkmm:defRangeYear_opened ?duri_Year_opened${RCOUNT} .
               ?duri_Year_opened${RCOUNT} bbkmm:isSubClassInstanceOf  ?vr_Year_opened${RCOUNT} .
               ?vr_Year_opened${RCOUNT}    bbkmm:hasLowerRange ?lr_Year_opened${RCOUNT} .
               ?lr_Year_opened${RCOUNT}    bbkmm:hasLowerValue ?lv_Year_opened${RCOUNT} .
               ?vr_Year_opened${RCOUNT}    bbkmm:hasUpperRange ?ur_Year_opened${RCOUNT} .
               ?ur_Year_opened${RCOUNT}    bbkmm:hasUpperValue ?uv_Year_opened${RCOUNT} .
          BIND (CONCAT(?lv_Year_opened${RCOUNT},":",?uv_Year_opened${RCOUNT})  as ?Year_opened)
	     }
    
 
    OPTIONAL {
     ?museum    bbkmm:defRangeYear_closed ?duri_Year_closed${RCOUNT} .
               ?duri_Year_closed${RCOUNT} bbkmm:isSubClassInstanceOf  ?vr_Year_closed${RCOUNT} .
               ?vr_Year_closed${RCOUNT}    bbkmm:hasLowerRange ?lr_Year_closed${RCOUNT} .
               ?lr_Year_closed${RCOUNT}    bbkmm:hasLowerValue ?lv_Year_closed${RCOUNT} .
               ?vr_Year_closed${RCOUNT}    bbkmm:hasUpperRange ?ur_Year_closed${RCOUNT} .
               ?ur_Year_closed${RCOUNT}    bbkmm:hasUpperValue ?uv_Year_closed${RCOUNT} .
          BIND (CONCAT(?lv_Year_closed${RCOUNT},":",?uv_Year_closed${RCOUNT})  as ?Year_closed)
	     }

    \n """

    _searchtype="integer"

    _conditiondict={
	"LTE": ' <= ',
	"LT": ' < ',
	"GT": ' > ',
	"GTE": ' >= ',
	"EQ": ' = ',
	"NEQ": ' != ',
	'BE': ' == ',
	'PLT': ' < ',
	'PGT': ' > ',
	'PLTE': ' <= ',
	'PGTE': ' >= ',
	'PEQ': ' = ',
	'PNEQ': ' != ',
	'PBE': ' == '

	}

    _guiconditions=[
	'Before:LT',
	'After:GT',
	'Between:BE',
	'Before and including:LTE',
	'After and including:GTE',
	'In:EQ',
	'Apart from:NEQ',
	'Possibly Before:PLT',
	'Possibly After:PGT',
	'Possibly Between:PBE',
	'Possibly Before and including:PLTE',
	'Possibly After and including:PGTE',
	'Possibly In:PEQ',
	'Possibly Apart from:PNEQ'

	]

    _widget='<select id="${ID}"  name="matchstring">Year exists</select>'
    _widgetcode=""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def getMatchFilter(self,rcount,match,condition):
	ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	ms=ms.replace("${RCOUNT}",str(rcount))
	return ms

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def getCompareFilter(self,rcount,match,condition):
	if (condition == "LT"):
	    ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "LTE"):
	    ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "GT"):
	    ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "GTE"):
	    ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "EQ"):
	    ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) <= "+ match +") AND "+" (STRDT(?lv_Year_closed${RCOUNT},xsd:positiveInteger) > "+ match +") "
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "NEQ"):
	    ms="(STRDT(?uv_Year_closed${RCOUNT},xsd:positiveInteger) < "+ match +") OR "+" (STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) > "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "BE"):
	    if (match.find(":") > -1):
		marr=match.split(":")
		df=marr[0]
		dt=marr[1]
		ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) < "+ df +") AND "+" (STRDT(?lv_Year_closed${RCOUNT},xsd:positiveInteger) > "+ df +") OR \n"
		ms=ms+"(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) >= "+ df +") AND "+" (STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) <= "+ dt +")"
		ms=ms.replace("${RCOUNT}",str(rcount))
########Possibly
	elif (condition == "PLT"):
	    ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PLTE"):
	    ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PGT"):
	    ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PGTE"):
	    ms="(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PEQ"):
	    ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) <= "+ match +") AND "+" (STRDT(?uv_Year_closed${RCOUNT},xsd:positiveInteger) > "+ match +") "
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PNEQ"):
	    ms="(STRDT(?lv_Year_closed${RCOUNT},xsd:positiveInteger) < "+ match +") OR "+" (STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) > "+ match +")"
	    ms=ms.replace("${RCOUNT}",str(rcount))
	elif (condition == "PBE"):
	    if (match.find(":") > -1):
		marr=match.split(":")
		df=marr[0]
		dt=marr[1]
		ms="(STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) < "+ df +") AND "+" (STRDT(?uv_Year_closed${RCOUNT},xsd:positiveInteger) > "+ df +") OR \n"
		ms=ms+"(STRDT(?uv_Year_opened${RCOUNT},xsd:positiveInteger) >= "+ df +") AND "+" (STRDT(?lv_Year_opened${RCOUNT},xsd:positiveInteger) <= "+ dt +")"
		ms=ms.replace("${RCOUNT}",str(rcount))
	    
	return ms


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getQuery(self,col,rcount,matchstring,condition,matchcolumn):
	query=self._existsquery.replace("${RCOUNT}",str(rcount))

        return query

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def getSearchType(self):
    
        return self._searchtype

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getGUIConditions(self):

        return self._guiconditions

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def getWidget(self):

        return self._widget

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    def getWidgetCode(self):

        return self._widgetcode

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def getModelToView(self,model,tup=None):

        return model

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Allow the query to be edited. E.g. removing the output column

    def editQueryParams(self,col,querycols,queryparams):
	qcol="?"+col
	qs=queryparams.find(qcol)
	if (qs > -1):
	    queryparams=queryparams[0:qs]+queryparams[qs+len(qcol):]
	    
	
	return querycols,queryparams
