##
# @file
# Builds the menu tree for browse. Contains a number of methods to split sequences of museums
# on year into buckets of N length.
# The class was superceded by a new tree lib as the task became more complex and this solution
# was nonworkable for the visualise page.
# It represents a bit of effort to convert from this tree to the new treelib so as long as it works
# it could be left alone. If however new functionality is needed the better and cleaner approach
# in Boks should be used.
# 
# This class essentially builds and maintains a css tree as text and in this lies the problem. 
# The tree should be maintained as a normal tree structure and the text generated on the finished tree.
# The tree contains a dictionary that relates nodes to museum lists which is generated for the JS to
# support the browsing of lists of museums.
#
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""

"""
from . import definitions
import copy
import pickle

class Tree(object):
    
    _tree = []
    _id="item"
    _level=-1
    _levelcount=[]
    _rootname=None
    _noleafs=False
    _leafdict={}
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Init
# Arguments:
# 
# @param rootnodename
# @param opened is menu open
# @param disabled is menu disabled
# @param base='item' menuname base

    def __init__(self, rootnodename,opened,disabled,base='item'):
        self._id=base
        if(not rootnodename):
            self.newTree()
        else:
            self._rootname = rootnodename
            self.newTree()
            self.addNodeAndLevel(self._rootname,True,False)
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
## Purpose:Creates new tree
    def newTree(self):
        self._tree=[]
        self._level=-1
        self._levelcount=[]
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
## Purpose:Whether tree has leaves
# Arguments:
# 
# @param value=False
    def setNoLeafs(self,value=False):
        self._noleafs=value
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Truncates the level of a menu
# Arguments:
# 
# @param level
    def truncLevel(self,level):
	pos=list(self.find_all(level, '-'))
	if (len(pos) > 1):
	    trunc=level[:pos[-1]]
	    return trunc
	else:
	    return None
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Parse the label from an id
# Arguments:
# 
# @param ids
    def getLabelFromString(self,ids):
	lepos=ids.find("</label>")
	stpos=copy.copy(lepos)
	if (lepos > -1):
	    while (stpos >= 0):
		if(ids[stpos] == ">"):
		    break
	        stpos=stpos - 1
	    label=ids[stpos+1:lepos]
	    
	    return label
	return None
	    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Calculates a path from an id
# Arguments:
# 
# @param id
    def getPath(self,id):
	iddict={}
	path=""
	thisid=""
	for i,line in enumerate(self._tree):
	    #get id
	    pat1='<input id="'
	    idpos=line.find(pat1)
	    if (idpos > -1):
		subline=line[idpos+len(pat1):]
		pat2='"'
		qpos=subline.find(pat2)
		if (qpos > -1):
		    thisid=subline[0:qpos]
		    iddict[thisid]=i
	

	line=self._tree[iddict[id]]
	path=self.getLabelFromString(line)
	uplevel=self.truncLevel(id)
	while (uplevel != None):
	    if (uplevel not in iddict):
		dc=0
                uplevel=None
		
	    elif (iddict[uplevel] not in self._tree):
                uplevel=None
	    else:
		line=self._tree[iddict[uplevel]]
		path=self.getLabelFromString(line)+"/"+path
		uplevel=self.truncLevel(uplevel)

	    
	return "/"+path
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Calculates a path from an id
# Arguments:
# 
# @param id
    def getPathForID(self,id):
	iddict={}
	path=""
	thisid=""
	for i,line in enumerate(self._tree):
	    #get id
	    pat1='<input id="'
	    idpos=line.find(pat1)
	    if (idpos > -1):
		subline=line[idpos+len(pat1):]
		pat2='"'
		qpos=subline.find(pat2)
		if (qpos > -1):
		    thisid=subline[0:qpos]
		    iddict[thisid]=i
	

	line=self._tree[iddict[id]]
	path=self.getLabelFromString(line)
	uplevel=self.truncLevel(id)
	while (uplevel != None):
	    if (not uplevel in iddict):
		break;
	    line=self._tree[iddict[uplevel]]
	    path=self.getLabelFromString(line)+"/"+path
	    uplevel=self.truncLevel(uplevel)
	    
	    
	
	return "/"+path
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Calculates a path from last id
    def getPathFromLastId(self):
	iddict={}
	path=""
	thisid=""
	for i,line in enumerate(self._tree):
	    #get id
	    pat1='<input id="'
	    idpos=line.find(pat1)
	    if (idpos > -1):
		subline=line[idpos+len(pat1):]
		pat2='"'
		qpos=subline.find(pat2)
		if (qpos > -1):
		    thisid=subline[0:qpos]
		    iddict[thisid]=i
	

	line=self._tree[iddict[thisid]]
	path=self.getLabelFromString(line)
	uplevel=self.truncLevel(thisid)
	while (uplevel != None):
	    if (uplevel not in iddict):
		line=self._tree[0]
		path=self.getLabelFromString(line).strip()+"/"+path
		break
	    else:
		line=self._tree[iddict[uplevel]]
		path=self.getLabelFromString(line)+"/"+path
		uplevel=self.truncLevel(uplevel)

	    
	return "/"+path
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Parse id from line
# Arguments:
# 
# @param line
    def getIdFromLine(self,line):
	pat1='<input id="'
	idpos=line.find(pat1)
	thisid=None
	if (idpos > -1):
	    subline=line[idpos+len(pat1):]
	    pat2='"'
	    qpos=subline.find(pat2)
	    if (qpos > -1):
		thisid=subline[0:qpos]
	return thisid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Appends a subtree to an existing tree line by line
# Arguments:
# 
# @param line
    def append(self,line):
	self._tree.append(line)
	
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Returns last line in tree
    def getLastLine(self):
	line=self._tree[-1]
	return line

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Replaces the last line in a tree
# Arguments:
# 
# @param line
    def putLastLine(self,line):
	self._tree[-1]=line
	return line

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Changes an id on a line and returns the new line and its id
# Arguments:
# 
# @param mod
# @param line
# @param id

    def modifyId(self,mod,line,id):
	thisid=id
	newid=newid=mod+thisid
	#get id
	pat1='<input id="'
	idpos=line.find(pat1)
	if (idpos > -1):
	    subline=line[idpos+len(pat1):]
	    pat2='"'
	    qpos=subline.find(pat2)
	    if (qpos > -1):
		thisid=subline[0:qpos]
		newid=mod+thisid
	line=line.replace(thisid,newid)
	return line,thisid


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Adds a subtree to the tree
# Arguments:
# 
# @param sub
# @param start

    def addSubTree(self,sub,start):
	sd=sub.getDict()
	#print type(sd)
	for key, val in sd.iteritems():
	    self._leafdict[key]=val
	
	st=sub.getTree()
        count=start
	while ( count < len (st)):
	    self._tree.append(st[count])
            count+=1
            
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Adds a subtree to the tree
# Arguments:
# 
# @param sub
# @param start

    def printTree(self,sub,start):
	st=sub.getTree()
        count=start
	print ">>--------------------------------"
	while ( count < len (st)):
	    print str(count)+"::"+st[count]
            count+=1
            
	print "<<--------------------------------"
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Reduce the level of the tree
    def lowerLevel(self):
        if (self._level >= 0):
            self._level-=1
#            del self._levelcount[-1]
            idl = len(self._id)
            self._id=self._id[:idl-3]
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Close the current level
    def closeLevel(self):
        if (self._level >= 0):
            self._level-=1
#            del self._levelcount[-1]
            idl = len(self._id)
            self._id=self._id[:idl-3]
            self._tree.append(
                '</ul> \n'+
                '</li> \n'+
#                '</ul> \n'+
                '</ul> \n')
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Close the whole tree
    def closeTree(self):
        for i in range(self._level+1):
            self.closeLevel()
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:formats the current id
    def getId(self):
        params=[]
        for i in range(self._level+1):
            params.append(int(self._levelcount[i]))

        return self._id.format(*params)
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
            
## Purpose:Increases the level
    def addLevel(self):
        self._level+=1

	if (len(self._levelcount) <= self._level):
	    self._levelcount.append(0)
        self._id=self._id+"-{}"
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Adds a leav to the tree with menu item and default action
# Arguments:
# 
# @param item
    def addLeaf(self,item):
	if (self._noleafs):
	    itemid=self.getId()
	    if (itemid in self._leafdict):
		itemlist=self._leafdict[itemid]
		itemlist.append(item)
	    else:
		itemlist=[]
		itemlist.append(item)
		self._leafdict[itemid]=itemlist
		self._tree.append('<li><a href="#tab1" onclick="SHOW('+"'"+itemid+"'"+')">Show</a></li>')
	else:
		self._tree.append('<li>'+item+'</li>')
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Create the JS dict to be used with  the browse page
    def defineDict(self):
	jsdata=[]
	jsdata.append("<script>")
	jsdata.append("treedict={")
	# iterating, always use iteritems !
	for key, val in self._leafdict.iteritems():
	    jsdata.append('"'+key+'":'+str(val)+",")
	    
	jsdata[-1]=jsdata[-1].replace("],","]")
	jsdata.append("};")
	jsdata.append("</script>")
	self._tree=jsdata+self._tree
	return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Adds a node to the tree and increases the level
# Arguments:
# 
# @param nodecontent
# @param opened is open?
# @param disabled is disabled?
# @param action='ShowMuseums' click action
# @param defaultaction=True   use default action

    def addNodeAndLevel(self,nodecontent,opened,disabled,action='ShowMuseums',defaultaction=True):
        ##print("printing nodecontent")
        ##print(nodecontent)
        if (not self._rootname):
            self._rootname=nodecontent

        self.addLevel()
        self._levelcount[self._level]=self._levelcount[self._level]+1
        
        newid=self.getId()
        if (opened):
            op=''
        else:
            op=''
        if (disabled):
            dis='disabled="disabled"'
        else:
            dis=''

	code='<ul> \n'
	if (defaultaction == True):
            code=code+'<li><input class="wulf" id="'+newid+'" type="checkbox" '+op+' '+dis+' /><label class="nocheck" id="'+newid+"L"+'" for="'+newid+'" onClick="'+action+'(this,\''+newid+'\',\''+nodecontent+'\')">'+nodecontent+'</label> \n'
	else:
            code=code+'<li><input class="devilwulf" id="'+newid+'" type="checkbox" '+op+' '+dis+' /><label class="nocheck" id="'+newid+"L"+'" for="'+newid+'" onClick="'+action+'">'+nodecontent+'</label> \n'
	    
	code=code+' <ul>\n'
        self._tree.append(code)
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Add a node at the current level
# Arguments:
# 
# @param nodecontent
# @param opened is open?
# @param disabled is disabled?
# @param action='ShowMuseums' click action

    def addNodeAtCurrentLevel(self,nodecontent,opened,disabled,action='ShowMuseums'):
        self._levelcount[self._level]=self._levelcount[self._level]+1
        newid=self.getId()
        if (opened):
            op=''
        else:
            op=''
        if (disabled):
            dis='disabled="disabled"'
        else:
            dis=''
        if (not self._rootname):
            self._rootname=nodecontent

        self._tree.append(
            '</ul></li><li><input class="hellwulf" id="'+newid+'" type="checkbox"'+op+' '+dis+' /><label class="nocheck" id="'+newid+"L"+'" for="'+newid+'" onClick="'+action+'(this,\''+newid+'\',\''+nodecontent+'\')">'+nodecontent+'</label> \n'+
            '<ul>\n')
        return
        
            
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
## Purpose:Return the current tree level
    def getCurrentLevel(self):
        return self._level

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Return the whole tree
    def getTree(self):
        return self._tree
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Return tree dictionary
    def getDict(self):
        return self._leafdict

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Calculate a bucket list of blist size of museums included in years.
# Arguments:
# 
# @param blist example:buckets=[10,1] buckets of 10 years
# @param ptr   traverse pointer index in list
# @param inputlist list

    def dobucket(self,blist,ptr,inputlist):
        if (ptr < len(blist)):
            firsttime=True
            prevhundreds=0
            newlist=[]
            for atuple in inputlist:
    
                iyear=int(atuple[0])
                item=atuple[1]
                hundreds=int(iyear/blist[ptr])*blist[ptr]
                if (hundreds != prevhundreds):
                    alist=[]
                    newlist.append(alist)
    
                    if (firsttime):
                        firsttime=False
                    else:
                        worklist=self.dobucket(blist,ptr+1,worklist)
                        nl=len(newlist)-2
                        newlist[nl]=worklist
    
                    worklist=alist
    
                prevhundreds=hundreds
                worklist.append(atuple)
    
    
            # Check that last level was triggered by sequence data
            atuple=inputlist[-1]
            iyear=int(atuple[0])
            item=atuple[1]
            mod=int(iyear % blist[ptr])
            if (mod > 0 and ptr+1 < len(blist)):
                worklist=self.dobucket(blist,ptr+1,worklist)
                nl=len(newlist)-1
                newlist[nl]=worklist
    
            return newlist
        else:
            return inputlist

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
## Purpose:Generates lists of musuems with bucket sizes in years using the prev method
#          from the sorted sequence of museums.
# Arguments:
# 
# @param sortedtuples museums
# @param buckets      bucket definition

    def generateLists(self,sortedtuples,buckets):
        newlist=[]
        isprocessed=[]
        worklist=newlist
        prevhundreds=0
        firsttime=True
        d=buckets[0]
        for atuple in sortedtuples:
            iyear=int(atuple[0])
            item=atuple[1]
            hundreds=int(iyear/d)*d
            if (hundreds != prevhundreds):
                alist=[]
                newlist.append(alist)
                if (firsttime):
                    firsttime=False
                else:
                    worklist=self.dobucket(buckets,1,worklist)
                    nl=len(newlist)-2
                    newlist[nl]=worklist
                    ptup=(prevhundreds,nl)
                    isprocessed.append(ptup)
                worklist=alist
                    
            prevhundreds=hundreds
            worklist.append(atuple)
	# Isprocessed? Check if last sequence of data triggered processing
        isp=False
        for atuple in isprocessed:
            prevhu=int(atuple[0])
            index=atuple[1]
            if (prevhu == prevhundreds):
                isp=True
                break
        if (not isp and len(worklist)>0):
	    # Trigger process
            worklist=self.dobucket(buckets,1,worklist)
            nl=len(newlist)-1
            newlist[nl]=worklist
	return newlist
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose: Recursively add to tree from bucket lists
# Arguments:
# 
# @param list list to add
# @param tree tree to add to
# @param nodename node to add to
# @param bucket definition
# @param ptr    list pointer
# @param open   menu open?

    def createtreefromlist(self,list,tree,nodename,bucket,ptr,open):
        tree.addNodeAndLevel(nodename,open,False)
        for item in list:
            if (str(type(item)) == "<type 'list'>" ) :
                ptr+=1

		if (ptr < len(bucket)):
		    atuple=item[0][0]
		    syear=str(atuple[0])
		    year=int(syear)
		    label=int(year/bucket[ptr-1])*bucket[ptr-1]
		    label="["+str(label)+"]--("+str(len(item))+")"
		    open=True
		else:
		    label="["+str(item[0][0])+"]--("+str(len(item))+")"
		    open=False
		tree=self.createtreefromlist(item,tree,
					     label,
					     bucket,ptr,open)
                ptr-=1
                tree.closeLevel()
            else:
                tree.addLeaf(str(item[1]))
        return tree


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Save tree with name
# Arguments:
# 
# @param name
    def pickleTree(self,name):
        print "Pickling tree: "+name
	with open(definitions.BASEDIR+name+'.pickle','wb') as f:
	    pickle.dump(self._tree, f, pickle.HIGHEST_PROTOCOL)
        print "done"
	f.close()
	return
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Load tree with name
# Arguments:
# 
# @param name
    def loadTree(self,name):
        print "Tree marshall pickling: "+name
	with open(definitions.BASEDIR+name+'.pickle','rb') as f:
	    self._tree=pickle.load( f )
        print "done"
	f.close()
	return self._tree

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Finds a substring in a string
# Arguments:
# 
# @param a_str input
# @param sub   to find

    def find_all(self,a_str, sub):
	start = 0
	while True:
	    start = a_str.find(sub, start)
	    if start == -1: return
	    yield start
	    start += len(sub) # use start += 1 to find overlapping matches


##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """

