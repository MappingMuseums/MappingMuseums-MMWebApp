##
# @file
#  
# Implementation of a custom sorter. The sort object needs to have one method for
# each sorting type. The each method takes a list in and sorts it and returns the sorted list.
# 
## Purpose:Sorts a list
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""

"""


class CustomSort(object):
    

    _guiconditions=[
	'Matches:EQ',
	'Not Matches to:NEQ'
	]


    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Returns a sorted list
# Arguments:list to sort
# 

    def OtherSort(self,inlist):
	
	return sorted(inlist)

