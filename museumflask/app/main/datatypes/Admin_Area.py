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
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""

"""
from flask import current_app as app


class Admin_Area(object):
    
    _adminareaqueryNOT="""



    ?adm bbkmm:hasTypedName  ?sname .
    ?adm a ?clazz .
    BIND (strafter(STR(?clazz),"/def/")  as ?${column_name} ).
        
    \n """

    
    _adminareaqueryOLD="""
    ?adm a ?clazz .
    ?adm bbkmm:hasTypedName  "${match_string}"^^xsd:string .
    BIND(concat("http://bbk.ac.uk/MuseumMapProject/def/refersTo",strafter(STR(?clazz),"/def/")) AS ?pred${rcount}) .
    BIND (strafter(STR(?clazz),"/def/")  as ?${column_name} ).
    ?museum ?candidatepred${rcount} ?adm .

        
    \n """

    _adminareaquery="""
    ?adm a ?clazz .
    ?adm bbkmm:hasTypedName  ?pred${rcount} .
    BIND (strafter(STR(?clazz),"/def/")  as ?${column_name} ).
    ?museum ?candidatepred${rcount} ?adm .

        
    \n """

    _searchtype="Admin_Area"

    _conditiondict={
	"EQ": ' = ',
	"NEQ": ' != '

	}

    _guiconditions=[
	'Matches:EQ',
	'Not Matching:NEQ'
	]

    _widget='<input id="${ID}" name="matchstring" placeholder="Enter an Admin Area"/>'


    ## Do not use hashes as these will become newlines. Always single quotes for quote
    ## Beware of any chars that interfere with JS such as <>
    
    _widgetcode="""
    var input = document.getElementById('${ID}');
    //console.log('input:'+input);
    var awesomplete = new Awesomplete(input, {
    minChars: 2,
    autoFirst: true
    });
    var lastvalue='';
    
    $('input').on('keyup', function(event){
    //console.log(this.value.length);
    //console.log('kc'+event.keyCode );
    var RETURN=13;
    if (this.value.length > 0 && this.value != lastvalue && event.keyCode != RETURN)
    {
    $.ajax({
    url: '/api/geoadmin/get/' + this.value,
    type: 'GET',
    dataType: 'json',
    success:function(data) 
    {
    var list = [];
    //console.log(data);
    $.each(data, function(key, value) 
    {
    //console.log(key+':'+value)
    list.push(value);
    });
    awesomplete.list = list;
    }
    
    })
    lastvalue=this.value;
    }
    
    });
    
    """

    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns SPARQL for a match condition filter on the data type
# Arguments:
# 
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator



    def getMatchFilter(self,rcount,match,condition):
	if (condition == "EQ"):
	    matchfilter='(STR(?pred${rcount}) = STR('+"'"+ match +"'"+') )'
	else:
	    matchfilter='(STR(?sname) != STR('+"'"+ match +"'))"
	    
	
	return matchfilter.replace("${rcount}",str(rcount))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns SPARQL for a  condition filter on the data type
# Arguments:
# 
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator


    def getCompareFilter(self,rcount,match,condition):
	if (condition == "EQ"):
	    compfilter='(STR(?pred${rcount}) '+self._conditiondict[condition]+' STR('+"'"+ match +"'"+') )'
	else:
	    compfilter='(STR(?sname) != STR('+"'"+ match +"'))"
	    
	
        return compfilter.replace("${rcount}",str(rcount))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns SPARQL for a query on the datatype without filter
# Arguments:
# 
# @param col  columne name for datatype
# @param rcount count to be attached to SPARQL variables
# @param match string to match
# @param condition comparator
# @param matchcolumn not used, only here for compatibility
    

    def getQuery(self,col,rcount,matchstring,condition,matchcolumn):
	if (condition == None):
	    # Case when we want the output but we are not searching on the field
	    query=self._adminareaquery.replace("${column_name}",col)
	elif (condition == "EQ"):
	    self._col=str(col)
	    query=self._adminareaquery.replace("${column_name}",col)
	    query=query.replace("${match_string}",matchstring)
	else:
	    self._col=str(col)
	    query=self._adminareaqueryNOT.replace("${column_name}",col)
	    query=query.replace("${match_string}",matchstring)
	    
        return query.replace("${rcount}",str(rcount))
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns type for the datatype to appear in search menu


    def getSearchType(self):
    
        return self._searchtype

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns the list of select conditions for the comaparator search menu

    def getGUIConditions(self):

        return self._guiconditions

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Returns html code for search menu

    def getWidget(self):

        return self._widget

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Returns JS code associated with the HTML for the datatype



    def getWidgetCode(self):

        return self._widgetcode

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Allow the query to be edited. E.g. removing the output column

    def editQueryParams(self,col,querycols,queryparams):
	return querycols,queryparams
