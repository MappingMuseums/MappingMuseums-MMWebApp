##
# @file
# Simple tree implementation.
# This class was replaced with the treelib class and should disappear
# when the showproperties class is rewritten.
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"


import json
from . import tree


class PTreeNode(dict):

## Purpose:Removes type info from name
# Arguments:
# 
# @param name
# @param data=None
# @param children=None
# @param level=0

    def __init__(self, name, data=None,children=None,level=0):
        dict.__init__(self) 
        self.__dict__ = self
        self.name = name
        self.data = data
        self.level     = level
        self.children = [] if not children else children


## Purpose:Print representation
    def __repr__(self):        
        return '\n{indent}Node({name},{children},{leaf},{level} DATA:{data})'.format(
            indent = self.level*'\t', 
            leaf = self.isLeaf(),
            name = self.name,
            level = self.level,
            data = self.data,
            children = repr(self.children))


## Purpose:Add node to tree
# Arguments:
# 
# @param nodedesc desription of node in the forma '/a/b/c'
# @param data data to store

    def addNode(self,nodedesc,data):
        treecopy=self
        parts=nodedesc.split('/')
        plen=len(parts)
        lev=1
        while (lev < plen):
            name=parts[lev]
            anode=self.getchildatthislevel(name,treecopy.children)
            if (not anode):
                treecopy.children.append(PTreeNode(name,data))
            treecopy=self.getchildatthislevel(name,treecopy.children)
            lev=lev+1
        
## Purpose:Does tree have children
    def isLeaf(self):
        if (len(self.children) == 0):
            return True
        else:
            return False

## Purpose:Find name in children
# Arguments:
# 
# @param name to look for
# @param children amongst these

    def getchildatthislevel(self,name,children):
        for c in children:
            if ( c["name"]== name):
                return c
        return None

## Purpose:Builds a tree from a subtree
# Arguments:
# 
# @param ob subtree
# @param level=0

    def buildnode(self,ob,level=0):
        node1= PTreeNode(ob['name'],level=level)
        node1.children=[]
        for children in ob['children']:
            node1.children.append(self.buildnode(children,level=level+1)) 

        return node1

## Purpose:return json representation
    def getJSON(self,):
        return json.dumps(self, sort_keys=True, indent=2)



## Purpose:Build a dictionary of paths and the associated HTML tree from a node
# Arguments:
# 
# @param node root
# @param t menu
# @param menuname name
# @param action the action to take
# @param path path to node
# @param pathdict dictionary of paths

    def getPathDict(self,node,t,menuname,action,path,pathdict):

        if (not t):
            t = tree.Tree(None,False,False,menuname)
        if (node.isLeaf()):
	    newid=t.getId()+":"+node.name.strip()
	    pathdict[newid]=path
        else:
            t.addNodeAndLevel(node.name,True,False,action)
	    pathdict[t.getId()]=path
            for kid in node.children:
                self.level += 1
                self.getHTMLTree(kid,t,menuname,action,path+"/"+kid.name.strip(),pathdict)
                self.level -= 1
            t.closeLevel()
        return t,pathdict

## Purpose:Add child to tree
# Arguments:
# 
# @param name child
# @param data data to store

    def addChild(self,name,data):
        newnode = PTreeNode(name,data=data)
        newnode.children=[]
	self.children.append(newnode)
	return newnode
    

	
if __name__ == '__main__':
    """ Run Process from the command line. """
