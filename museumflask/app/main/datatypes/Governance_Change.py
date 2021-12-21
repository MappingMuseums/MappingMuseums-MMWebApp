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


class Governance_Change(object):
    
    OLD_statusquery="""
    OPTIONAL

    {
    ?museum bbkmm:hasStatusChange ?sc .
    ?sc bbkmm:hasStatus ?statusval .
    ?sc bbkmm:hasSequenceOrder ?statusseq .
    ?sc  bbkmm:isSubClassInstanceOf ?ch .
    ?ch  bbkmm:hasNotes ?statusnote .
    ?ch bbkmm:isSubClassInstanceOf ?te .
    
    ?te time:hasBeginning ?bi .
    ?bi  time:inXSDDateTime ?statusbegindate .

    ?te time:hasEnd ?bi2 .
    ?bi2  time:inXSDDateTime ?statusenddate

    BIND (CONCAT(?statusseq,":",?statusval,":",?statusbegindate,":",?statusenddate)  as ?${column_name})

    }
    \n """

    _statusquery="""
    OPTIONAL

    {
    ?museum bbkmm:hasGovernance_Change ?sc .
    ?sc bbkmm:hasStatus ?statusval .
    ?sc bbkmm:hasSequenceOrder ?statusseq .
    ?sc  bbkmm:isSubClassInstanceOf ?ch .
    ?ch  bbkmm:hasNotes ?statusnote .
    ?ch bbkmm:isSubClassInstanceOf ?te .
    
    ?te time:hasBeginning ?bi .
    ?bi  time:inXSDDateTime ?statusbegindate .

    ?te time:hasEnd ?bi2 .
    ?bi2  time:inXSDDateTime ?statusenddate

    BIND (CONCAT(?statusseq,":",?statusval,":",?statusbegindate,":",?statusenddate)  as ?${column_name})

    }
    \n """

    _searchtype="integer"

    _conditiondict={
	"LTE": ' <= ',
	"LT": ' < ',
	"GT": ' > ',
	"GTE": ' >= ',
	"EQ": ' = ',
	"NEQ": ' != '

	}

    _guiconditions=[
	'Before:LT',
	'After:GT',
	'Before and including:LTE',
	'After than and including:GTE',
	'Specific year only:EQ',
	'Apart from this year:NEQ'
	]

    _widget='<select id="${ID}"  name="matchstring">Governance Change</select>'
    _widgetcode=""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def getMatchFilter(self,rcount,match,condition):
        
        return "(STRDT(?statusbegindate,xsd:integer) "+self._conditiondict[condition]+" "+ match +")"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def getCompareFilter(self,rcount,match,condition):
        
        return "(STRDT(?statusbegindate,xsd:integer) "+self._conditiondict[condition]+" "+ match +")"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getQuery(self,col,rcount,matchstring,condition,matchcolumn):
	query=self._statusquery.replace("${column_name}",col)

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

    def getModelToViewOLD(self,model):
	parts=model.split(":")
	starty=parts[2]
	endy=parts[3]
	status=parts[1]

	html="""
           <table id="governancechange"  class="table table-bordered" border="1"  >
	   <thead>
           <tr>
                   <th id="gov-heading1" > 
                       Gov
                    </th>
                   <th id="gov-heading2" > 
                       From
                    </th>
                   <th id="gov-heading3" > 
                       To
                    </th>
           </tr>
	   </thead>
	<tbody>
	      <tr  class="govresult">
                 <td  class="gov-status"> ${status} </td>
                 <td  class="gov-from">   ${from} </td>
                 <td  class="gov-gov2">   ${to}  </td>
              </tr>
	</tbody>
           </table>


	"""
	
	
        return html.replace("${status}",status).replace("${from}",starty).replace("${to}",endy)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def getModelToView(self,model,tup=None):

	if (tup == None):
	    parts=model.split(":")
	    starty=parts[2]
	    endy=parts[3]
	    status=parts[1]
	else:
	    starty,endy,status=(tup)
	    
	view="${status} from ${from} to ${to}"
        return view.replace("${status}",status).replace("${from}",starty).replace("${to}",endy)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def sort(self,list):
	tuplist=[]
	for item in list:
	    parts=model.split(":")
	    starty=parts[2]
	    endy=parts[3]
	    status=parts[1]
	    tup=(starty,endy,status)
	    tuplist.append(tup)
	sortedlist=sorted(tuplist,key=lambda tup: tup[0])
	resultlist=[]
	for item in sortedlist:
	    resultlist.append(self.getModelToView(None,item))
	sortedlist=None
	tuplist=None
	return resultlist
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Allow the query to be edited. E.g. removing the output column

    def editQueryParams(self,col,querycols,queryparams):
	return querycols,queryparams
