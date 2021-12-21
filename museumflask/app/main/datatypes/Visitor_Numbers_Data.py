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
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# OPTIONAL  
## Purpose:Returns the formatting of the datatype for the search table cell.
#          This requires a call in the model_to_view_class and needs to be
#          changed to be done by introspection.
#    def getModelToView(self,model,tup=None):
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


class Visitor_Numbers_Data(object):
    

    _visitorsquery="""
    OPTIONAL
    {
    ?museum  bbkmm:hasVisitor_Numbers_Data ?visi .
    ?visi bbkmm:hasValue ?VisitorMeasurement_val .
    ?visi bbkmm:hasSequenceOrder ?VisitorMeasurement_seq .
    ?visi bbkmm:isSubClassInstanceOf ?tm .
    ?tm bbkmm:isSubClassInstanceOf ?te .
    ?tm prov:hadPrimarySource ?pe .
    ?pe prov:value ?pv .
    ?te time:hasBeginning ?bi .
    ?bi  time:inXSDDateTime ?VisitorMeasurement_date .
    BIND (CONCAT(?VisitorMeasurement_seq,":",?VisitorMeasurement_val,":",?VisitorMeasurement_date,":",?pv)  as ?${column_name})

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
	'Smaller than:LT',
	'Larger than:GT',
	'Smaller and including:LTE',
	'Larger than and including:GTE',
	'Specific number only:EQ'
	]


    _widget='<select id="${ID}"  name="matchstring">Visitor Numbers Data</select>'
    _widgetcode=""

#    FILTER ((?lv_Year_closed_4,xsd:positiveInteger) > """+str(startperiod)+""")  ) .

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def getMatchFilter(self,rcount,match,condition):
        
        return "(STRDT(?VisitorMeasurement_val,xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def getCompareFilter(self,rcount,match,condition):
        
        return "(STRDT(?VisitorMeasurement_val,xsd:positiveInteger) "+self._conditiondict[condition]+" "+ match +")"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def getQuery(self,col,rcount,matchstring,condition,matchcolumn):
	query=self._visitorsquery.replace("${column_name}",col)

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
	vis=parts[1]

	html="""
           <table id="visitornumbersdata"  class="table table-bordered" border="1"  >
	   <thead>
           <tr>
                   <th id="vn-heading1" > 
                       Num
                    </th>
                   <th id="vn-heading2" > 
                       At
                    </th>
           </tr>
	   </thead>
	<tbody>
	      <tr  class="vnresult">
                 <td  class="vn-status"> ${visitors} </td>
                 <td  class="vn-from">   ${from} </td>
              </tr>
	</tbody>
           </table>


	"""
	
	
        return html.replace("${visitors}",vis).replace("${from}",starty)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def getModelToView(self,model,tup=None):
	if (tup == None):
	    parts=model.split(":")
	    prov=parts[3]
	    starty=parts[2]
	    vis=parts[1]
	else:
	    prov,starty,vis=(tup)
	    
	
	view="${visitors} at ${date} from ${prov}"
        return view.replace("${visitors}",vis).replace("${date}",starty).replace("${prov}",prov)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sort(self,list):
	tuplist=[]
	for item in list:
	    parts=model.split(":")
	    prov=parts[3]
	    starty=parts[2]
	    vis=parts[1]
	    tup=(starty,vis)
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
