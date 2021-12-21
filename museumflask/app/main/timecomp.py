#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile

# Nick Larsson (NickTex)

License: GPL 2 (http://www.gnu.org/copyleft/gpl.html) or BSD

"""

#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    
comparators=[
    "=",
    "<",
    "<=",
    ">",
    ">=",
    "!=",

    "==",
    "<<",
    "<<=",
    ">>",
    ">>=",
    "!=="
]
def generatetimepairs():
    timepairs=[]
    timepairs.append((1900,1900))
    timepairs.append((1895,1900))
    timepairs.append((1895,1895))
    timepairs.append((1895,1905))
    timepairs.append((1905,1905))
    return timepairs

def comparetimes(c,date):
    tp=generatetimepairs()
    res=[]
    
    if (c == "="):
	for p in tp:
	    f,t=p
	    res.append(compare_equal(f,t,date))
    elif (c == "<"):
	for p in tp:
	    f,t=p
	    res.append(compare_less(f,t,date))
    elif (c == "<="):
	for p in tp:
	    f,t=p
	    res.append(compare_less_equal(f,t,date))
    elif (c == ">"):
	for p in tp:
	    f,t=p
	    res.append(compare_greater(f,t,date))
    elif (c == ">="):
	for p in tp:
	    f,t=p
	    res.append(compare_greater_equal(f,t,date))
    elif (c == "!="):
	for p in tp:
	    f,t=p
	    res.append(compare_not_equal(f,t,date))
		       
    ##  "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    if (c == "=="):
	for p in tp:
	    f,t=p
	    res.append(p_compare_equal(f,t,date))
    elif (c == "<<"):
	for p in tp:
	    f,t=p
	    res.append(p_compare_less(f,t,date))
    elif (c == "<<="):
	for p in tp:
	    f,t=p
	    res.append(p_compare_less_equal(f,t,date))
    elif (c == ">>"):
	for p in tp:
	    f,t=p
	    res.append(p_compare_greater(f,t,date))
    elif (c == ">>="):
	for p in tp:
	    f,t=p
	    res.append(p_compare_greater_equal(f,t,date))
    elif (c == "!=="):
	for p in tp:
	    f,t=p
	    res.append(p_compare_not_equal(f,t,date))
		       

    for i in range(0,len(tp)):
	f,t=tp[i]
	r=res[i]
	print '({},{}) {} {} -> {}'.format(f,t,c,date,r)
    return
		       
def compare_equal(f,t,d):
    if (f == d and t == d):
	return True
    else:
	return False

def compare_less(f,t,d):
    if (t < d ):
	return True
    else:
	return False

def compare_less_equal(f,t,d):
    if (t <= d ):
	return True
    else:
	return False

def compare_greater(f,t,d):
    if (f > d ):
	return True
    else:
	return False

def compare_greater_equal(f,t,d):
    if (f >= d ):
	return True
    else:
	return False

def compare_not_equal(f,t,d):
    if (compare_less_equal(f,t,d) or compare_greater(f,t,d)):
	return True
    elif ( t < d or f > d):
	return True
    else:
	return False

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def p_compare_equal(f,t,d):
    if (f <= d and d <= t):
	return True
    else:
	return False

def p_compare_less(f,t,d):
    if (f < d ):
	return True
    else:
	return False

def p_compare_less_equal(f,t,d):
    if (f <= d ):
	return True
    else:
	return False

def p_compare_greater(f,t,d):
    if (t > d ):
	return True
    else:
	return False

def p_compare_greater_equal(f,t,d):
    if (t >= d ):
	return True
    else:
	return False

def p_compare_not_equal(f,t,d):
    if (not  (f == d and t == d)):
	return True
    else:
	return False


    
	
    
    
if __name__ == '__main__':
    """ Run Process from the command line. """

    comparetimes("=",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("<",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("<=",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes(">",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes(">=",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("!=",1900)

    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"

    comparetimes("==",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("<<",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("<<=",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes(">>",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes(">>=",1900)
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - -"
    comparetimes("!==",1900)
    
