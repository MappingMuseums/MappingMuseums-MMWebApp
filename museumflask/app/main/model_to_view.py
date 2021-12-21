##
# @file
#  
#  This class defines operations that allows to go from model representation
#  of a variable to view representation and this is used mostly in search
#  to format output from the database.
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"


from . import definitions
from . import tree
import apputils 

from PTreeNode import PTreeNode as PTreeNode


class Model_To_View(object):


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Formats a model representation to a view representation of all datatypes.
# Arguments:
# 
# @model The datatype of the attribute
# @attribute The model representation

    def getView(self,model,attribute):
	if (model == definitions.GOVERNANCE):
	    parts=attribute.split(definitions.HIER_SEPARATOR)
	    lastpart=parts[len(parts)-1]
	    return lastpart.replace("_"," ")
	elif (model == definitions.SUBJECT_MATTER):
	    parts=attribute.split(definitions.HIER_SEPARATOR)
	    lastpart=parts[len(parts)-1]
	    lastpart=lastpart.replace("_"," ").replace(definitions.HIER_SUBCLASS_SEPARATOR,
						       definitions.HIER_SUBCLASS_VIEW_SEPARATOR)
	    return lastpart
	elif (model == definitions.YEAR_CLOSED):
	    if (attribute == definitions.RANGE_OPEN):
		return "Still open"
	    else:
		vals=attribute.split(definitions.RANGE_SEPARATOR)
		if (len(vals) < 2):
		    return "ERROR: this"+model+definitions.RANGE_SEPARATOR+attribute+" contained no value!"
		elif (vals[0] == vals[1]):
		    return vals[0]
		else:
		    return vals[0]+"-"+vals[1]
	elif (model == definitions.YEAR_OPENED):
	    vals=attribute.split(definitions.RANGE_SEPARATOR)
	    if (len(vals) < 2):
		return "ERROR: this"+model+definitions.RANGE_SEPARATOR+attribute+" contained no value!"
	    elif (vals[0] == vals[1]):
		return vals[0]
	    else:
		return vals[0]+"-"+vals[1]
	elif (model == definitions.STATUSCHANGE):
	    instance=apputils.getDataClassInstance(definitions.STATUSCHANGE)
	    view=instance.getModelToView(attribute)
	    return view.replace("_"," ")
	elif (model == definitions.VISITORNUMBERS):
	    instance=apputils.getDataClassInstance(definitions.VISITORNUMBERS)
	    view=instance.getModelToView(attribute)
	    return view.replace("_"," ")
	else:
	    if (model in definitions.DATATYPEDICT):
		mtype=definitions.DATATYPEDICT[model]
	    else:
		mtype=""

	    if (mtype == definitions.XSD_STRINGTYPE):
		# Check for href
		ishref=attribute.find("http")
		if (ishref > -1):
		    endhref=ishref
		    al=len(attribute)
		    while (endhref < al and attribute[endhref:endhref] != ' '):
			endhref=endhref+1
		    href=attribute[ishref:endhref]
		    part1=attribute[0:ishref]
		    part2=attribute[endhref:]
		    code='<a href="'+href+'" target="_blank">'+href+'</a>'
		    newline=part1+code+part2
		    return newline

	    return attribute.replace("_"," ")
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Formats a specific type from model to view representation
# Arguments:
# 
# @mtype type 
# @attribute model representation

    def getViewForType(self,mtype,attribute):
	if (mtype == definitions.DEFINED_HIERTYPE):
	    parts=attribute.split(definitions.HIER_SEPARATOR)
	    lastpart=parts[len(parts)-1]
	    lastpart=lastpart.replace("_"," ").replace(definitions.HIER_SUBCLASS_SEPARATOR,
						       definitions.HIER_SUBCLASS_VIEW_SEPARATOR)
	    if (lastpart.startswith(definitions.HIER_SUBCLASS_VIEW_SEPARATOR)):
		lastpart=lastpart[1:]
	    return lastpart
	elif (mtype == definitions.XSD_STRINGTYPE):
	    # Check for href
	    ishref=attribute.find("http")
	    if (ishref > -1):
		endhref=ishref
		al=len(attribute)
		while (endhref < al and attribute[endhref:endhref] != ' '):
		    endhref=endhref+1
		href=attribute[ishref:endhref]
		part1=attribute[0:ishref]
		part2=attribute[endhref:]
		code='<a href="'+href+'" target="_blank">'+href+'</a>'
		newline=part1+code+part2
		return newline
	    else:
		return attribute.replace("_"," ")
	else:
	    return attribute.replace("_"," ")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Converts a view representation to model representation
# Arguments:
# 
# @mtype type
# @attribute view representation

    def getTypeForView(self,mtype,attribute):
	if (mtype == definitions.DEFINED_HIERTYPE):
	    return  "http://"+definitions.RDFDEFURI+attribute.replace(" ","_").replace(definitions.HIER_SUBCLASS_VIEW_SEPARATOR,
										       definitions.HIER_SUBCLASS_SEPARATOR)
	else:
	    return attribute

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Converts a view representation to model representation
# This one is particular for the search menu construction in apputils.
# Arguments:
# 
# @mtype type
# @attribute view representation

    def getTypeForViewForSearch(self,mtype,attribute):
	if (mtype == definitions.DEFINED_HIERTYPE):
	    return  attribute.replace(" ","_").replace(definitions.HIER_SUBCLASS_VIEW_SEPARATOR,
						       definitions.HIER_SUBCLASS_SEPARATOR)
	else:
	    return attribute

