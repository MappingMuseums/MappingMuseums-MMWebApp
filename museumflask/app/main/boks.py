##
# @file
#  
# This class is the entry point for all plots in the visualise page.  
# Each menu on the page corresponds to a class with the same name.
# Each menu alternative corresponds to a method on the class.
# This class receives the plot call and assignes it to the correct
# subclass and method. Each of the methonds have a "parameters" and a
# contextdict parameter. The parameters are provided from the querystring
# (GET) or from the request form (POST). The contextdict is provided by
# the client and represents all knowledge around the client click.
# The parameters in the methods are reshuffled to fit the plotting class.
# Plotting is done with the bokeh classes and in module boks.
#
# The menus are built on request on the first call and can be time consuming.
# The menu is built by getTree which builds a tree which is then converted to
# HTML by getTreeFromTreeLib and the menu is pickled and cached.
#
# A file is read an put in the presentation pane with hints on the plotting.
#
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from flask.views import View
from flask import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from flask import current_app as app
from . import apputils
from . import listman
from . import tree as mytree
from . import PTreeNode
from treelib import Tree, Node
from . import models
from . import definitions
from . import model_to_view
from . import Configuration
from PTreeNode import PTreeNode as PTreeNode

from app.main.boksplots import bokehtree
from app.main.boksplots import bokehtimeandcategory
from app.main.boksplots import bokehtime
from app.main.boksplots import bokehcategorybar
from app.main.boksplots import bokehheatmap
from app.main.boksplots import bokutils

from flask import current_app as app
import pprint
import collections
import copy
import urlparse
import urllib
import pandas as pd
import traceback
import sys
import pickle
import time

from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.io import show, output_file


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Boks():
    ## Menu structure
    timelist = [
        "open at a given time",
        "that opened up to a given time",
        "that closed up to a given time",
        "open over time",
        "openings over time",
        "closings over time",
    ]
    ## Query options
    heatmapoptions = [
        definitions.GOVERNANCE,
        definitions.SUBJECT_MATTER,
        definitions.SIZE,
        "Location"
    ]

    ## routing info
    _routedict = {}

    ## implementation classes
    _open_at_a_given_time = None
    _that_opened_up_to_a_given_time = None
    _that_closed_up_to_a_given_time = None
    _openings_over_time = None
    _closings_over_time = None
    _open_over_time = None
    _openings_and_closings_over_time = None
    _heatmap = None

    UKNAME = "UK"

    NOgreeting = "Hello"
    greeting = None

    # ===============================================================================================
    # ******************** BAR *********************************
    # ===============================================================================================
    class open_at_a_given_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            newparameters.append(bokutils.ACCUMULATE_TRUE)

            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            newparameters.append(bokutils.ACCUMULATE_TRUE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                newparameters.append(parameters[0])
            newparameters.append(bokutils.ACCUMULATE_TRUE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_OPENED)
            parameters.append(bokutils.ACCUMULATE_TRUE)
            plot = Boks.categorybar.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Location(self, me, parameters=None, contextdict=None):

            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            newparameters.append(bokutils.ACCUMULATE_TRUE)
            # Append only the last one for now and if there is none we add uk
            if (len(parameters) == 0):
                newparameters.append(Boks.UKNAME)
            else:
                newparameters.append(parameters[-1])

            # for p in parameters:
            # newparameters.append(p)
            plot = Boks.categorybar.createLocationPlot("location", newparameters, contextdict)
            return plot

    # ===============================================================================================
    class that_opened_up_to_a_given_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            newparameters.append(bokutils.ACCUMULATE_FALSE)

            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            newparameters.append(bokutils.ACCUMULATE_FALSE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            parameters = []
            parameters.append(definitions.YEAR_EXISTS)
            parameters.append(bokutils.ACCUMULATE_FALSE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_EXISTS)
            parameters.append(bokutils.ACCUMULATE_FALSE)
            plot = Boks.categorybar.createPlot(me, parameters, contextdict)

            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Location(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            newparameters.append(bokutils.ACCUMULATE_TRUE)
            # Append only the last one for now and if there is none we add uk
            if (len(parameters) == 0):
                newparameters.append(Boks.UKNAME)
            else:
                newparameters.append(parameters[-1])

            # for p in parameters:
            # newparameters.append(p)
            plot = Boks.categorybar.createLocationPlot("location", newparameters, contextdict)
            return plot

    # ===============================================================================================

    class that_closed_up_to_a_given_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            newparameters.append(bokutils.ACCUMULATE_FALSE)

            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            newparameters.append(bokutils.ACCUMULATE_FALSE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            parameters = []
            parameters.append(definitions.YEAR_CLOSED)
            parameters.append(bokutils.ACCUMULATE_FALSE)
            # Create the plot
            plot = Boks.categorybar.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_CLOSED)
            parameters.append(bokutils.ACCUMULATE_FALSE)
            plot = Boks.categorybar.createPlot(me, parameters, contextdict)

            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Location(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            newparameters.append(bokutils.ACCUMULATE_TRUE)
            # Append only the last one for now and if there is none we add uk
            if (len(parameters) == 0):
                newparameters.append(Boks.UKNAME)
            else:
                newparameters.append(parameters[-1])

            # for p in parameters:
            # newparameters.append(p)
            plot = Boks.categorybar.createLocationPlot("location", newparameters, contextdict)
            return plot
    # ===============================================================================================
    # ******************** LINE  *********************************
    # ===============================================================================================

    class openings_over_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_OPENED)
            plot = Boks.time.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def Location(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            else:
                newparameters.append(Boks.UKNAME)
            # Create the plot
            plot = Boks.timeandcategory.createLocationPlot("location", newparameters, contextdict)
            return plot

    # ===============================================================================================
    class open_over_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_OPENED)
            parameters.append(definitions.YEAR_CLOSED)
            plot = Boks.time.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Location(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_EXISTS)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
            else:
                newparameters.append(Boks.UKNAME)

            # Create the plot
            plot = Boks.timeandcategory.createLocationPlot("location", newparameters, contextdict)
            return plot

    # ===============================================================================================

    class closings_over_time():

        def Governance(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Subject_Matter(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def Size(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)

            # Create the plot
            plot = Boks.timeandcategory.createPlot(me, newparameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_CLOSED)
            plot = Boks.time.createPlot(me, parameters, contextdict)
            return plot

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def Location(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_CLOSED)
            if (len(parameters) > 0):
                for p in parameters:
                    newparameters.append(p)
                    # Append only the last one for now and if there is none we add uk
            else:
                newparameters.append(Boks.UKNAME)

            # Create the plot
            plot = Boks.timeandcategory.createLocationPlot("location", newparameters, contextdict)
            return plot

    # ===============================================================================================
    class openings_and_closings_over_time():

        def All(self, me, parameters=None, contextdict=None):
            # Create the plot
            parameters = []
            parameters.append(definitions.YEAR_OPENED)
            parameters.append(definitions.YEAR_CLOSED)

            plot = Boks.time.createPlotAll(me, parameters, contextdict)
            return plot

    # ===============================================================================================
    class heatmap():

        def Generic(self, me, parameters=None, contextdict=None):
            newparameters = []
            newparameters.append(definitions.YEAR_OPENED)
            newparameters.append(definitions.YEAR_CLOSED)
            newparameters.append(parameters[0])
            newparameters.append(parameters[1])

            plot = Boks.heat.createPlot(me, newparameters, contextdict)
            return plot

        def Location(self, me, parameters=None, contextdict=None):
            # Create the plot
            newparameters = []
            # [ ['Year_opened', 'Year_closed', [u'Governance'], 'glocation', [u'Location', u'England'], 'glocation'] ]
            newparameters.append(definitions.YEAR_OPENED)
            newparameters.append(definitions.YEAR_CLOSED)
            newparameters.append("glocation")
            newparameters.append(parameters[0])
            newparameters.append(me)
            newparameters.append(parameters[1])

            plot = Boks.heat.createPlot(bokutils.PLOT_GLOCATION_KEY,
                                        newparameters,
                                        contextdict)
            return plot

    # ===============================================================================================
    #  INTIALISE STATIC VARS
    # ===============================================================================================

    btree = bokehtree.BokehTree()
    timeandcategory = bokehtimeandcategory.BokehTimeAndCategory()
    time = bokehtime.BokehTime()
    categorybar = bokehcategorybar.BokehCategoryBar()
    heat = bokehheatmap.BokehHeatmap()
    if (greeting == None):
        with open(definitions.BASEDIR + 'boksgreeting.html') as f:
            greeting = f.readlines()
        f.close()
    greeting = ''.join(greeting).replace("\n", "")
    menucoltree = None
    menuxtree = None
    menuytree = None
    menutree = None
    locatree = None
    locnode = None
    menut = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Adds a leaf to the menu
    # Arguments:
    # @menu menu
    # @action the action to take
    # @nodename the name of the node to add
    #
    def addLeaf(self, menu, action, nodename):

        newid = menu.getId()
        path = menu.getPath(newid) + "/" + nodename
        menu.addLeaf('<label id="' + newid + "L" + '" class="anchor" onClick="{}">{}</label>'.format(
            action + "(this,'" + newid + "','" + path + "')",
            nodename))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Adds a node to the tree
    # Arguments:
    #
    # @menu menu
    # @action the action to take
    # @nodename the name of the node to add

    def addNodeWithAction(self, menu, action, nodename):
        newid = menu.getId()
        path = menu.getPath(newid) + "/" + nodename
        actionstring = action + "(this,'" + newid + "','" + path + "')"
        menu.addNodeAndLevel(nodename, False, False, action=actionstring, defaultaction=False)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    ## Purpose:Build the hierarchy as nodes
    # Arguments:
    #
    # @tree    tree
    # @parent  parent
    # @hvector path vector
    # @idx     current node id

    def getSubHier(tree, parent, hvector, idx):
        if (idx < len(hvector)):
            child = tree.hasChildWithName(parent, hvector[idx])
            if (child == None):
                node = tree.create_node(hvector[idx], hvector[idx] + parent.identifier, parent=parent, data=parent.data)
                return Boks.getSubHier(tree, node, hvector, idx + 1)
            else:
                child.data = parent.data
                return Boks.getSubHier(tree, child, hvector, idx + 1)
        else:
            return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    ## Purpose:Recursion helper for above
    # Arguments:
    #
    # @hier hierarchy
    # @tree tree
    # @parent parent
    # @datadict=None dictionary to be injected into node

    def getHierSubmenu(hier, tree, parent, datadict=None):
        if (str(type(parent)) == "<type 'str'>"):
            pname = parent
        else:
            pname = parent.identifier
        if (datadict != None):
            mergedict = {}
            if (parent.data != None):
                for k in parent.data.keys():
                    mergedict[k] = parent.data[k]
            for k in datadict.keys():
                mergedict[k] = datadict[k]
            hnode = tree.create_node(hier, hier + pname, parent=parent, data=mergedict)
        else:
            hnode = tree.create_node(hier, hier + pname, parent=parent, data=parent.data)

        subprops = listman.getList("defClass" + hier + definitions.LISTNAME)
        sortedsubprops = sorted(subprops)
        for sub in sortedsubprops:
            parts = sub.split("-")
            n = Boks.getSubHier(tree, hnode, parts, 0)

        return hier

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    ## Purpose:builds a tree as a list
    # Arguments:
    #
    # @list list
    # @tree tree
    # @parent parent
    # @datadict=None dictionary to be injected into node

    def getListSubmenu(list, tree, parent, datadict=None):
        if (str(type(parent)) == "<type 'str'>"):
            pname = parent
        else:
            pname = parent.identifier

        if (datadict != None):
            mergedict = {}
            if (parent.data != None):
                for k in parent.data.keys():
                    mergedict[k] = parent.data[k]
            for k in datadict.keys():
                mergedict[k] = datadict[k]
            hnode = tree.create_node(list, list + pname, parent=parent, data=mergedict)
        else:
            hnode = tree.create_node(list, list + pname, parent=parent, data=parent.data)

        subprops = listman.getList(list + definitions.LISTNAME)
        sortedsubprops = sorted(subprops)
        for sub in sortedsubprops:
            tree.create_node(sub, sub + hnode.identifier, parent=hnode, data=hnode.data)

        return list

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    ## Purpose:builds a tree as a list
    # Arguments:
    #
    # @list list
    # @tree tree
    # @parent parent
    # @datadict=None dictionary to be injected into node

    def getIntegerAsListSubmenu(propname, tree, parent, datadict=None):
        if (str(type(parent)) == "<type 'str'>"):
            pname = parent
        else:
            pname = parent.identifier

        if (datadict != None):
            mergedict = {}
            if (parent.data != None):
                for k in parent.data.keys():
                    mergedict[k] = parent.data[k]
            for k in datadict.keys():
                mergedict[k] = datadict[k]
            hnode = tree.create_node(propname, propname + pname, parent=parent, data=mergedict)
        else:
            hnode = tree.create_node(propname, propname + pname, parent=parent, data=parent.data)

        proplist = apputils.getIntegerAsList(propname)
        for sub in proplist:
            tree.create_node(sub, sub + hnode.identifier, parent=hnode, data=hnode.data)

        return propname

    # #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    ## Purpose:Filter to remove all children from the tree. This is done to
    #          make the plots have only groups and not individual lines
    # Arguments:
    #
    # @node node
    def filterChildren(node):
        if (node.is_leaf() == True):
            return True
        else:
            return False

    @staticmethod
    ## Purpose:Removes nodes according to the filter above
    # Arguments:
    #
    # @tree tree
    # @node node

    def trimNodes(tree, node):
        # Remove all nodes with no children
        listofleafs = tree.filter_nodes(Boks.filterChildren)
        for n in listofleafs:
            tree.remove_node(n.identifier)
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    ## Purpose: Builds the complete menu tree
    def getTree(self):
        if (Boks.menutree == None):
            if (app.config['DEV_MODE'] == 'T'):
                newmenu = mytree.Tree(None, False, False, "VizTree")
                Boks.menutree = newmenu.loadTree("VizTree")
            else:
                tree = Tree()
                datadict = {"method": "ShowMuseums"}
                museumroot = tree.create_node("Visualisations", "museumsRoot", data=datadict)  # root node
                root = tree.create_node("Number of museums", "museums", parent=museumroot, data=datadict)  # root node
                l_count = 0
                for times in Boks.timelist:
                    datadict = {"method": "ShowMuseums"}
                    timesnode = tree.create_node(times, times, parent=root, data=datadict)
                    datadict = {"method": "ShowPlot"}
                    tree.create_node("All", "all-" + times, parent=timesnode, data=datadict)
                    # Dummy node to make strip leave the all alone. Not great
                    tree.create_node("All", "All" + times + "dummy", parent="all-" + times, data=datadict)

                    Boks.getHierSubmenu(definitions.GOVERNANCE, tree, timesnode, datadict)
                    Boks.getHierSubmenu(definitions.SUBJECT_MATTER, tree, timesnode, datadict)
                    Boks.getListSubmenu(definitions.SIZE, tree, timesnode, datadict)

                    if (l_count < 6):  # This just for testing of one plot set it to number desired
                        locnode = tree.create_node("Location",
                                                   times + "/" + "Location",
                                                   parent=times, data=datadict)

                        tree = self.getEnglandTree(locnode, tree, prefix=times)
                        tree = self.getGenericLocationTree(locnode, tree, 'Wales', '(pseudo) Wales', prefix=times)
                        tree = self.getGenericLocationTree(locnode, tree, 'Northern Ireland',
                                                           '(pseudo) Northern Ireland', prefix=times)
                        tree = self.getGenericLocationTree(locnode, tree, 'Scotland', '(pseudo) Scotland', prefix=times)
                        tree = self.getGenericLocationTree(locnode, tree, 'Channel Islands', '(pseudo) Channel Islands',
                                                           prefix=times)
                        tree = self.getGenericLocationTree(locnode, tree, 'Isle of Man', '(pseudo) Isle of Man',
                                                           prefix=times)
                    l_count = l_count + 1

                datadict = {"method": "ShowMuseums"}
                tree.create_node("openings and closings over time",
                                 "openings and closings over time",
                                 parent=root,
                                 data=datadict)
                datadict = {"method": "ShowPlot"}
                tree.create_node("All", "All" + "openings and closings over time",
                                 parent="openings and closings over time", data=datadict)
                # Dummy node to make strip leave the all alone. Not great
                tree.create_node("All", "All" + "openings and closings over time dummy",
                                 parent="All" + "openings and closings over time", data=datadict)

                #### Heatmaps

                DEFAULT_TABLE_PLOT_COLUMNS = apputils.readList(definitions.BASEDIR + 'DEFAULT_TABLE_PLOT_COLUMNS.txt')
                datadict = {"method": "donothing"}
                plot = tree.create_node("Table", "Table", parent=museumroot, data=datadict)  # root node
                plotx = tree.create_node("X", "PlotX", plot, data=datadict)  # root node
                datadict = {"method": "selectX"}

                for col in DEFAULT_TABLE_PLOT_COLUMNS:
                    defcol = definitions.DEFNAME + col
                    itype = None
                    if (defcol in definitions.DATATYPEDICT):
                        itype = definitions.DATATYPEDICT[defcol]
                    elif (col in definitions.DATATYPEDICT):
                        itype = definitions.DATATYPEDICT[col]
                    else:
                        print "WARNING **** No handler for :" + col

                    if (itype == definitions.DEFINED_LISTTYPE):
                        Boks.getListSubmenu(col, tree, plotx, datadict)
                    elif (itype == definitions.DEFINED_HIERTYPE):
                        Boks.getHierSubmenu(col, tree, plotx, datadict)
                    elif (itype == 'xsd:positiveInteger'):
                        Boks.getIntegerAsListSubmenu(col, tree, plotx, datadict)
                    else:
                        print "WARNING **** No handler for :" + col + " type:" + itype

                xpref = "selectX"
                locnode = tree.create_node("Location",
                                           xpref + "/" + "Location",
                                           parent=plotx,
                                           data=datadict)
                tree = self.getEnglandTree(locnode, tree, prefix=xpref)
                tree = self.getGenericLocationTree(locnode, tree, 'Wales', '(pseudo) Wales', prefix=xpref)
                tree = self.getGenericLocationTree(locnode, tree, 'Northern Ireland', '(pseudo) Northern Ireland',
                                                   prefix=xpref)
                tree = self.getGenericLocationTree(locnode, tree, 'Scotland', '(pseudo) Scotland', prefix=xpref)
                tree = self.getGenericLocationTree(locnode, tree, 'Channel Islands', '(pseudo) Channel Islands',
                                                   prefix=xpref)
                tree = self.getGenericLocationTree(locnode, tree, 'Isle of Man', '(pseudo) Isle of Man', prefix=xpref)
                print "Number of X nodes:" + str(tree.countChildren(plotx))

                datadict = {"method": "donothing"}
                ploty = tree.create_node("Y", "PlotY", plot, data=datadict)  # root node

                datadict = {"method": "selectY"}

                for col in DEFAULT_TABLE_PLOT_COLUMNS:
                    defcol = definitions.DEFNAME + col
                    itype = None
                    if (defcol in definitions.DATATYPEDICT):
                        itype = definitions.DATATYPEDICT[defcol]
                    elif (col in definitions.DATATYPEDICT):
                        itype = definitions.DATATYPEDICT[col]
                    else:
                        print "WARNING **** No handler for :" + col

                    if (itype == definitions.DEFINED_LISTTYPE):
                        Boks.getListSubmenu(col, tree, ploty, datadict)
                    elif (itype == definitions.DEFINED_HIERTYPE):
                        Boks.getHierSubmenu(col, tree, ploty, datadict)
                    elif (itype == 'xsd:positiveInteger'):
                        Boks.getIntegerAsListSubmenu(col, tree, ploty, datadict)
                    else:
                        print "WARNING **** No handler for :" + col + " type:" + itype

                print "Number of Y nodes:" + str(tree.countChildren(ploty))

                newmenu = mytree.Tree(None, False, False, "menuviz")

                Boks.trimNodes(tree, museumroot)

                #           Note, very important to not supply a dict here as this will override all local dicts.
                datadict = {}
                Boks.getTreeFromTreeLib(tree, newmenu, museumroot, datadict, filterpathlen=3)
                Boks.menutree = newmenu.getTree()
                newmenu.pickleTree("VizTree")

        return Boks.menutree

    # -  -  -  -  -  -  -
    ## Purpose:Build the x heatmap menu
    def getXTree(self):
        if (Boks.menuxtree == None):
            tree = Tree()
            datadict = {"method": "selectX"}
            root = tree.create_node("Select X property", "museumsX")  # root node

            Boks.getHierSubmenu(definitions.GOVERNANCE, tree, root)
            Boks.getHierSubmenu(definitions.SUBJECT_MATTER, tree, root)
            Boks.getListSubmenu(definitions.SIZE, tree, root)

            newmenu = mytree.Tree(None, False, False, "menux")
            Boks.getTreeFromTreeLib(tree, newmenu, root, datadict, opennodefilterpolicy=1, filterpathlen=1)
            Boks.menuxtree = newmenu.getTree()

        return Boks.menuxtree

    # -  -  -  -  -  -  -

    ## Purpose:Build the y heatmap menu
    def getYTree(self):
        if (Boks.menuytree == None):
            tree = Tree()
            datadict = {"method": "selectY"}
            root = tree.create_node("Select Y property", "museumsY")  # root node

            Boks.getHierSubmenu(definitions.GOVERNANCE, tree, root)
            Boks.getHierSubmenu(definitions.SUBJECT_MATTER, tree, root)
            Boks.getListSubmenu(definitions.SIZE, tree, root)

            newmenu = mytree.Tree(None, False, False, "menuy")
            Boks.getTreeFromTreeLib(tree, newmenu, root, datadict, opennodefilterpolicy=1, filterpathlen=1)
            Boks.menuytree = newmenu.getTree()

        return Boks.menuytree

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Implements the FLASK view
    def boksView(self, plot):

        if (request.method == 'GET'):
            js_resources = INLINE.render_js()
            css_resources = INLINE.render_css()
            return render_template("visualisation.html",
                                   trees=self.getTree(),
                                   xtrees=None,
                                   ytrees=None,
                                   loctree=None,
                                   coltrees=None,
                                   greeting=Boks.greeting)
        elif (request.method == 'POST'):
            # Heatmaps

            color = request.form.get("colorscheme-label")
            xax = request.form.get("xaxisselect-label")
            xaxparts = xax.split("/")
            yax = request.form.get("yaxisselect-label")
            yaxparts = yax.split("/")

            yaxdict = request.form.get("yaxisselect-dict")
            xaxdict = request.form.get("xaxisselect-dict")
            contextdictstr = urllib.unquote(request.form.get("contextdict")).decode('utf8')
            contextdict = urlparse.parse_qs(urlparse.urlparse(contextdictstr).query)
            contextdict[bokutils.SERVER_PATH] = request.path

            path = "/path" + urllib.unquote(request.form.get("xaxisselect-dict")).decode('utf8')
            xdict = urlparse.parse_qs(urlparse.urlparse(path).query)

            print("printing category")
            print(xaxparts[4:])
            print("printing parameters")
            print([yaxparts[4:], color])
            print("printing contextdict")
            print(contextdict)
            dataview = "heatmap"
            category = xaxparts[4:]
            parameters = [yaxparts[4:], color]
            start_time = time.time()
            obj = self.plotRoute(dataview, category, parameters, contextdict)


            print("printing obj")
            print(obj)

            # Embed plot into HTML via Flask Render
            js_resources = INLINE.render_js()
            css_resources = INLINE.render_css()
            script, div = components(obj)

            return render_template("boksplot.html",
                                   greeting=Boks.NOgreeting,
                                   plot_script=script,
                                   plot_div=div,
                                   css_resources=css_resources)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Routes the call to the view to the correct implementation
    # Arguments:
    #
    # @dataview Menu
    # @category submenu
    # @parameters see module
    # @contextdict see module

    def plotRoute(self, dataview, category, parameters, contextdict):

        if (Boks._open_at_a_given_time == None):
            Boks._open_at_a_given_time = Boks.open_at_a_given_time()
            Boks._that_opened_up_to_a_given_time = Boks.that_opened_up_to_a_given_time()
            Boks._openings_over_time = Boks.openings_over_time()
            Boks._closings_over_time = Boks.closings_over_time()
            Boks._that_closed_up_to_a_given_time = Boks.that_closed_up_to_a_given_time()
            Boks._open_over_time = Boks.open_over_time()
            Boks._openings_and_closings_over_time = Boks.openings_and_closings_over_time()
            Boks._heatmap = Boks.heatmap()

            Boks._routedict["open_at_a_given_time"] = Boks._open_at_a_given_time
            Boks._routedict["that_opened_up_to_a_given_time"] = Boks._that_opened_up_to_a_given_time
            Boks._routedict["openings_over_time"] = Boks._openings_over_time
            Boks._routedict["closings_over_time"] = Boks._closings_over_time
            Boks._routedict["that_closed_up_to_a_given_time"] = Boks._that_closed_up_to_a_given_time
            Boks._routedict["open_over_time"] = Boks._open_over_time
            Boks._routedict["openings_and_closings_over_time"] = Boks._openings_and_closings_over_time
            Boks._routedict["heatmap"] = Boks._heatmap

        if (dataview == "heatmap"):
            # We handle this differently because it should handle any of the hier/list/int types
            # Location is special, others not
            d = dir(Boks._routedict[dataview])
            if (str(type(category)) == "<type 'str'>" or str(type(category)) == "<type 'unicode'>"):
                catid = category
            else:
                catid = category[0]

            if (catid != "Location"):
                # We make it generic
                catid = "Generic"

            if (catid in d):
                if (callable(getattr(Boks._routedict[dataview], catid))):
                    func = getattr(Boks._routedict[dataview], catid)
                    print("printing it all")

                    print(d)
                    print(catid)
                    print(func)
                    return func(category, parameters, contextdict)


        else:
            d = dir(Boks._routedict[dataview])

            if (str(type(category)) == "<type 'str'>" or str(type(category)) == "<type 'unicode'>"):
                catid = category
            else:
                catid = category[0]
            if (catid in d):
                if (callable(getattr(Boks._routedict[dataview], catid))):
                    func = getattr(Boks._routedict[dataview], catid)
                    return func(category, parameters, contextdict)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Implements the FLASK view
    # Arguments:
    #
    # @plot

    def boksPlotView(self, plot):

        contextdict = urlparse.parse_qs(urlparse.urlparse(request.path).query)
        isq = request.path.find("?")
        pathnoparams = request.path
        if (isq > -1):
            pathnoparams = request.path[0:isq]
            contextdict[bokutils.SERVER_PATH] = pathnoparams
            rpath = pathnoparams.split("/")
        dataview = 4
        category = 5
        parameterstart = category + 1
        if (request.method == 'GET'):
            try:

                start_time = time.time()
                plot = self.plotRoute(rpath[dataview],
                                      rpath[category],
                                      list(rpath[parameterstart:]),
                                      contextdict)
                if hasattr(plot, 'toolbar'):
                    plot.toolbar.active_drag = None
                    plot.toolbar.active_inspect = None
                    plot.toolbar.logo = None

                print("--- %s seconds ---" % (time.time() - start_time))
            except Exception, e:
                print str(e)
                return render_template('message.html', title="Plot",
                                       message="Plot function [" + str(rpath[category]) + "] failed -> " + str(e))

            # Embed plot into HTML via Flask Render
            print 'a'
            js_resources = INLINE.render_js()
            print 'b'
            css_resources = INLINE.render_css()
            print 'c'
            script, div = components(plot)
            print 'd'
            return render_template("boksplot.html",
                                   trees=self.getTree(),
                                   plot_script=script,
                                   plot_div=div,
                                   css_resources=css_resources)

    # # - - - - - -

    @staticmethod
    ## Purpose:Join path with separator
    # Arguments:
    #
    # @sep
    # @path

    def pathJoin(sep, path):
        pathstr = ""
        for p in path:
            pathstr = pathstr + sep + p
        return pathstr

    # # - - - - - -

    @staticmethod
    ## Purpose:Get the json dict
    # Arguments:
    #
    # @dict
    def getJSDict(dict):
        dstr = "{"
        for k in dict.keys():
            dstr = dstr + " " + k + ":" + "\'" + dict[k] + "\',"
        dstr = dstr + "}"

        return dstr.replace(",}", "}")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    ## Purpose:Converts the regular tree to an HTML tree
    # Arguments:
    #
    # @tree tree
    # @t    menutree
    # @node start node
    # @data=None data to be injected in nodes
    # @opennodefilterpolicy=1 Is node open per default
    # @filterpathlen=1  depth of tree to be processed
    # @datalenoption=False Do we want nodecount in menu text?

    def getTreeFromTreeLib(tree, t, node, data=None, opennodefilterpolicy=1, filterpathlen=1, datalenoption=False):
        if (not t):
            t = mytree.Tree(None, False, False, "menux")
        thisdata = data
        if (thisdata == None):
            thisdata = {}
        if (node.data != None):
            for key, val in node.data.iteritems():
                thisdata[key] = val
        if (node.is_leaf()):
            newid = t.getId() + ":" + node.tag.strip()
            datalen = "1"
            path = tree.getPathForNode(node)
            path = Boks.pathJoin("/", path)
            thisdata["class"] = "node"
            thisdata["id"] = newid
            thisdata["path"] = path
            thisdata["name"] = node.tag.strip()

            jsdict = Boks.getJSDict(thisdata)
            leafcontent = '<label id="' + newid + "L" + '" class="nocheck anchor" onClick="{}">{} </label>'.format(
                'exec(this,' + jsdict + ')', node.tag.replace("_", " "))
            t.addLeaf(leafcontent)
        else:
            children = tree.children(node.identifier)
            datalen = len(children)
            newid = t.getId() + ":" + node.tag.strip()
            tdepth = tree.depth(node)
            if (tdepth >= opennodefilterpolicy):
                openpolicy = False
            else:
                openpolicy = True

            if (datalen > 0):
                datalen = tree.countChildren(node) - 1
                path = tree.getPathForNode(node)
                pathlen = len(path)
                path = Boks.pathJoin("/", path)
                datalentext = ""
                if (datalenoption):
                    datalentext = ' [' + str(datalen) + ']'

                if (pathlen <= filterpathlen):
                    # Upper nodes Functionality needs specifying anyway to allow for different behaviour eg clearing of x and y

                    thisdata["class"] = "node"
                    thisdata["id"] = newid
                    thisdata["path"] = path
                    thisdata["name"] = node.tag.strip()

                    jsdict = Boks.getJSDict(thisdata)
                    t.addNodeAndLevel(node.tag.replace("_", " ") + datalentext, openpolicy, False,
                                      action='exec(this,' + jsdict + ')',
                                      defaultaction=False)

                else:
                    thisdata["class"] = "node"
                    thisdata["id"] = newid
                    thisdata["path"] = path
                    thisdata["name"] = node.tag.strip()

                    jsdict = Boks.getJSDict(thisdata)
                    t.addNodeAndLevel(node.tag.replace("_", " ") + datalentext, openpolicy, False,
                                      action='exec(this,' + jsdict + ')',
                                      defaultaction=False)
            else:
                path = tree.getPathForNode(node)
                path = Boks.pathJoin("/", path)
                thisdata["class"] = "node"
                thisdata["id"] = newid
                thisdata["path"] = path
                thisdata["name"] = node.tag.strip()

                jsdict = Boks.getJSDict(thisdata)
                datalentext = ""
                if (datalenoption):
                    datalentext = ' [' + str(datalen) + ']'
                t.addNodeAtCurrentLevel(node.tag.replace("_", " ") + datalentext, openpolicy, False,
                                        'exec(this,' + jsdict + ')',
                                        node.tag.replace("_", " "))

            for kid in children:
                Boks.getTreeFromTreeLib(tree, t, kid, thisdata, opennodefilterpolicy, filterpathlen,
                                        datalenoption=datalenoption)
            t.closeLevel()
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    ## Purpose:Build tree for locations
    def getLocationTree(self):
        if (Boks.locatree == None):
            if (app.config['DEV_MODE'] == 'T'):
                menut = mytree.Tree(None, False, False, "menuLoc")
                Boks.locatree = menut.loadTree("vizloctree")
            else:
                tree = Tree()
                datadict = {"method": "selectLoc"}
                root = tree.create_node("Select Location", "Loca")  # root node

                tree = self.getEnglandTree(root, tree)
                tree = self.getGenericLocationTree(root, tree, 'Wales', '(pseudo) Wales')
                tree = self.getGenericLocationTree(root, tree, 'Northern Ireland', '(pseudo) Northern Ireland')
                tree = self.getGenericLocationTree(root, tree, 'Scotland', '(pseudo) Scotland')
                tree = self.getGenericLocationTree(root, tree, 'Channel Islands', '(pseudo) Channel Islands')
                tree = self.getGenericLocationTree(root, tree, 'Isle of Man', '(pseudo) Isle of Man')

                newmenu = mytree.Tree(None, False, False, "menuLoc")
                Boks.getTreeFromTreeLib(tree, newmenu, root, datadict, filterpathlen=1, datalenoption=False)
                Boks.locatree = newmenu.getTree()
                newmenu.pickleTree("vizloctree")
        return Boks.locatree

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Build tree for england
    # @root node
    # @tree tree
    # @prefix="" menu prefix

    def getEnglandTree(self, root, tree, prefix=""):

        # INIT
        treedict = {}

        # Create england dict
        treedict['England'] = {}

        # Regions (GORS)
        sgor = sorted(apputils.GOR_TRANSLATION_TABLE.items(), key=lambda x: x[1])
        # After this the dict becomes a list.....
        # Remove pseudo from a reversed list
        for trange in reversed(xrange(len(sgor))):
            tup = (sgor[trange])
            if (tup[0].find("99999999") > -1):
                del sgor[trange]
        regionsdict = {}
        for tup in sgor:
            regionsdict[tup[1]] = []
        # Counties
        county_and_region_table = {}
        for key, val in apputils.COUNTY_TRANSLATION_TABLE.iteritems():
            county_and_region_table[key] = val
        for key, val in apputils.CA_CODE_TO_NAME_TABLE.iteritems():
            county_and_region_table[key] = val

        scounties = sorted(county_and_region_table.items(), key=lambda x: x[1])
        # After this the dict becomes a list.....
        # Remove pseudo from a reversed list
        for trange in reversed(xrange(len(scounties))):
            tup = (scounties[trange])
            if (tup[0].find("99999999") > -1):
                del scounties[trange]
        countiesdict = {}
        for tup in scounties:
            countiesdict[tup[1]] = []

        # Put counties in regions
        for counties in countiesdict:
            if (counties in definitions.COUNTY2_REGION_DICT):
                thisregion = definitions.COUNTY2_REGION_DICT[counties]
                if (thisregion in regionsdict):
                    regionsdict[thisregion].append(counties)
                else:
                    print "Not in regiondic 1" + counties
            else:
                print "Not in regiondic 2" + counties

        # Put CA in regions

        for ca_code, ca_name in apputils.CA_CODE_TO_NAME_TABLE.iteritems():
            if (ca_code in apputils.CA_CODE_TO_GOR_TABLE):
                thisregioncode = apputils.CA_CODE_TO_GOR_TABLE[ca_code]
                thisregion = apputils.GOR_TRANSLATION_TABLE[thisregioncode]
                if (thisregion in regionsdict):
                    regionsdict[thisregion].append(ca_name)
                else:
                    print "Not in regiondic 1" + ca_name
            else:
                print "Not in regiondic 2" + ca_name

        # Put LA in regions where 99999
        for laname, countyname in definitions.LA2_COUNTY_DICT.iteritems():
            if (countyname == "(pseudo) England (UA/MD/LB"):
                if (laname in apputils.LA_TO_CA_NAMES_TABLE):
                    countyname = apputils.LA_TO_CA_NAMES_TABLE[laname]
                    # print "###adding "+laname+" to "+countyname
                    countiesdict[countyname].append(laname)
                else:
                    thisregion = definitions.LA2_REGION_DICT[laname]
                    regionsdict[thisregion].append(laname)
            elif (countyname.find("pseudo") < 0):
                countiesdict[countyname].append(laname)

        # Put LA in regions from LATOCA dict
        for laname, countyname in apputils.LA_TO_CA_NAMES_TABLE.iteritems():
            # print "###adding "+laname+" to "+countyname
            lalist = countiesdict[countyname]
            if (not laname in lalist):
                countiesdict[countyname].append(laname)

            # Get the data
            props = [definitions.NAME_OF_MUSEUM, definitions.SUBJECT_MATTER, definitions.PROJECT_ID,
                     definitions.POSTCODE]
            results = apputils.getMarkerData(props)
        try:
            results = apputils.getMarkerData(props)
        except         Exception, e:
            print str(e)
            return "*** ERROR IN GETAREATREE:" + str(e)

        # Sort the data into the dictionaries
        rlen = len(results["results"]["bindings"])
        #       print "?#?#? views.py at line: 1559 Dbg-out variable \rlen [",rlen,"]\n";
        museumdict = {}
        notinlacount = 0

        for result in results["results"]["bindings"]:
            if ("museum" in result):
                museum = result["museum"]["value"]
                if (definitions.NAME_OF_MUSEUM in result):
                    name = result[definitions.NAME_OF_MUSEUM]["value"]
                    lat = result[definitions.LATITUDE]["value"]
                    lon = result[definitions.LONGITUDE]["value"]
                    if (definitions.SUBJECT_MATTER in result):
                        sub = result[definitions.SUBJECT_MATTER]["value"]
                    else:
                        sub = "Unknown"

                    if (definitions.POSTCODE in result):
                        postcode = result[definitions.POSTCODE]["value"].replace(' ', '')

                        if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
                            thiscountry = definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"', '')
                            if (thiscountry == 'England'):
                                tup = (museum, name, sub, lat, lon)
                                if (not thiscountry in museumdict):
                                    museumdict[thiscountry] = []
                                museumdict[thiscountry].append(tup)
                                if (postcode in definitions.POSTCODE2_REGION_DICT):
                                    thisregion = definitions.POSTCODE2_REGION_DICT[postcode]
                                    key = thiscountry + "/" + thisregion
                                    if (not key in museumdict):
                                        museumdict[key] = []
                                    museumdict[key].append(tup)
                                else:
                                    print "NOT IN POSTCODE2_REGION_DICT" + postcode

                                # CA required
                                if (postcode in definitions.POSTCODE2_LA_DICT):
                                    thisla = definitions.POSTCODE2_LA_DICT[postcode]
                                else:
                                    thisla = ""
                                # - -

                                if (thisla in apputils.LA_TO_CA_NAMES_TABLE):
                                    thiscounty = apputils.LA_TO_CA_NAMES_TABLE[thisla]
                                    key = thiscountry + "/" + thisregion + "/" + thiscounty
                                elif (postcode in definitions.POSTCODE2_COUNTY_DICT):
                                    thiscounty = definitions.POSTCODE2_COUNTY_DICT[postcode]
                                    if (thiscounty.find("pseudo") > 0):
                                        key = thiscountry + "/" + thisregion
                                    else:
                                        key = thiscountry + "/" + thisregion + "/" + thiscounty

                                    if (not key in museumdict):
                                        museumdict[key] = []
                                    # Check if we already appended this as a region
                                    if (thiscounty.find("pseudo") < 0):
                                        museumdict[key].append(tup)
                                else:
                                    print "NOT IN POSTCODE2_COUNTY_DICT" + postcode

                                if (postcode in definitions.POSTCODE2_LA_DICT):
                                    thisla = definitions.POSTCODE2_LA_DICT[postcode]
                                    if (thiscounty.find("pseudo") > 0):
                                        key = thiscountry + "/" + thisregion + "/" + thisla
                                    else:
                                        key = thiscountry + "/" + thisregion + "/" + thiscounty + "/" + thisla

                                    if (not key in museumdict):
                                        museumdict[key] = []
                                    museumdict[key].append(tup)

                                    ## CA
                                    if (thisla in apputils.LA_TO_CA_NAMES_TABLE):
                                        thiscaname = apputils.LA_TO_CA_NAMES_TABLE[thisla]

                                        key = thiscountry + "/" + thisregion + "/" + thiscaname
                                        if (not key in museumdict):
                                            museumdict[key] = []
                                        museumdict[key].append(tup)
                                else:
                                    print "NOT IN POSTCODE2_LA_DICT " + postcode
                                # print postcode+" X_X_X "+thiscountry+"/"+thisregion+"/"+thiscounty+"/"+thisla

                        else:
                            # print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
                            if (postcode in definitions.POSTCODE2_DISTR_DICT):
                                print "But in region dict:" + definitions.POSTCODE2_DISTR_DICT[postcode]
                            if (postcode in definitions.POSTCODE2_COUNTY_DICT):
                                print "But in county  dict:" + definitions.POSTCODE2_COUNTY_DICT[postcode]

        idpath = "England"
        england = tree.create_node(idpath,
                                   prefix + "/" + idpath,
                                   parent=root)

        firsttime_region = True
        for reg in sorted(regionsdict):
            regnode = tree.create_node(reg,
                                       prefix + "/" + idpath + "/" + reg,
                                       parent=england)

            firsttime_county = True
            for county in sorted(regionsdict[reg]):
                key = idpath + "/" + reg + "/" + county
                if (county in countiesdict):
                    countynode = tree.create_node(county,
                                                  prefix + "/" + key,
                                                  parent=regnode)

                    for la in sorted(countiesdict[county]):
                        key = idpath + "/" + reg + "/" + county + "/" + la
                        lanode = tree.create_node(la,
                                                  prefix + "/" + key,
                                                  parent=countynode)

                # above was commented out

                else:
                    # We have a pseudo
                    if (key in museumdict):
                        countynode = tree.create_node(county,
                                                      prefix + "/" + key,
                                                      parent=regnode)

        return tree

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ## Purpose:Build tree for countries other than england
    # Arguments:
    #
    # @root root node
    # @tree tree
    # @countryparam name
    # @pseudoparam  ons code
    # @prefix="" menu prefix

    def getGenericLocationTree(self, root, tree, countryparam, pseudoparam, prefix=""):

        treedict = {}

        # Create england dict
        treedict[countryparam] = {}

        # Counties
        pseudo = pseudoparam
        countiesdict = {}
        countiesdict[pseudo] = []

        # Put counties in regions
        for county in countiesdict:
            ladict = {}
            for lakey, laval in definitions.LA2_COUNTY_DICT.iteritems():
                if (laval == county):
                    ladict[lakey] = laval
        sla = sorted(ladict)
        for las in sla:
            countiesdict[pseudo].append(las)

        # Get all postcodes
        props = [definitions.NAME_OF_MUSEUM,
                 definitions.SUBJECT_MATTER,
                 definitions.PROJECT_ID,
                 definitions.POSTCODE]
        try:
            results = apputils.getMarkerData(props)
        except         Exception, e:
            print str(e)
            return "*** ERROR IN GETAREATREE:" + str(e)

        rlen = len(results["results"]["bindings"])
        museumdict = {}
        notinlacount = 0

        for result in results["results"]["bindings"]:
            if ("museum" in result):
                museum = result["museum"]["value"]
                if (definitions.NAME_OF_MUSEUM in result):
                    name = result[definitions.NAME_OF_MUSEUM]["value"]
                    lat = result[definitions.LATITUDE]["value"]
                    lon = result[definitions.LONGITUDE]["value"]
                    if (definitions.SUBJECT_MATTER in result):
                        sub = result[definitions.SUBJECT_MATTER]["value"]
                    else:
                        sub = "Unknown"

                    if (definitions.POSTCODE in result):
                        postcode = result[definitions.POSTCODE]["value"].replace(' ', '')

                        if (name and museum and postcode and postcode in definitions.POSTCODE2_LA_DICT):
                            thiscountry = definitions.POSTCODE2_COUNTRY_DICT[postcode].replace('"', '')
                            if (thiscountry == countryparam):
                                tup = (museum, name, sub, lat, lon)
                                if (not thiscountry in museumdict):
                                    museumdict[thiscountry] = []
                                museumdict[thiscountry].append(tup)

                                if (postcode in definitions.POSTCODE2_LA_DICT):
                                    thisla = definitions.POSTCODE2_LA_DICT[postcode]
                                    key = thiscountry + "/" + pseudo + "/" + thisla

                                    if (not key in museumdict):
                                        museumdict[key] = []
                                    museumdict[key].append(tup)
                                else:
                                    print "NOT IN POSTCODE2_LA_DICT " + postcode
                        #                               print postcode+" X_X_X "+thiscountry+"/"+pseudo+"/"+thisla

                        else:
                            if (postcode in definitions.POSTCODE2_DISTR_DICT):
                                print "But in region dict:" + definitions.POSTCODE2_DISTR_DICT[postcode]
                            if (postcode in definitions.POSTCODE2_COUNTY_DICT):
                                print "But in county  dict:" + definitions.POSTCODE2_COUNTY_DICT[postcode]

                            notinlacount += 1

        # Create the tree
        countrynode = tree.create_node(countryparam,
                                       prefix + "/" + countryparam,
                                       parent=root)

        for la in sorted(countiesdict[county]):
            lanode = tree.create_node(la,
                                      prefix + "/" + countryparam + "/" + la,
                                      parent=countrynode)

        return tree
