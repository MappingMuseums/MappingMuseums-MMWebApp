##
# @file
#  
# Implements a configuration to be stored in the DB 
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

import json
import listman 

class Configuration:
    DATA_PTR='DATA'
    TYPE_PTR='DATATYPE'
    OPTIONS_PTR='OPTIONS'

    def __init__(self, configs = {},name=None):
        self.config = configs
        if (name):
            self.name=name
        else:
            self.name='AnonymousConfiguration'
            
        return
    
    def set(self,key,value):
        self.config[key]=value
        return

    def get(self,key):
        if self.config.has_key(key):
            return self.config[key]
        return None
    
    def printKey(self,key):
        if self.config.has_key(key):
            print "[",key,"]:"+str(self.config[key])
        else:
            print "[",key,"]:UNKNOWN"
        return 

    def save(self):
        json_str = json.dumps(self.config, sort_keys=True, indent=2)
        listman.insertConfig(self.name,json_str)
        return
    
        
    def load(self):
        self.dict={}
        json_str=listman.getConfig(self.name)
        self.dict=json.loads(json_str)  
        return
        
if __name__ == '__main__':
    """ Run Process from the command line. """
