#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import listman
from . import tree
from . import PTreeNode
from . import models
from . import definitions
from . import model_to_view
from . import Configuration
from . import showmuseumtypes

from PTreeNode import PTreeNode as PTreeNode


from flask import current_app as app
import pprint
import collections
import copy

from altair import Chart, Color, Scale
import pandas as pd
import traceback
import sys
import pickle


class PlotChart():

#-  -  -  -  -  -  -

    def getConfiguration(self):
        t = tree.Tree("Plot",False,False)
        t.addNodeAndLevel("Numeric property",True,False)

        for item in definitions.ATTRITYPES:
            name,value=item
            if (value.lower().find("integer") > -1 ):
                t.addLeaf('<a href="{}">{}</a>'.format("/visualisations/"+name,name.replace('_',' ')))
        t.closeLevel()
        t.closeTree()
        

        return t.getTree()

#-  -  -  -  -  -  -  

    def getChartTypes(self):
        sel=[]
        sel.append('<option value="bar">bar</option> \n')
        sel.append('<option value="pie">pie</option> \n')
        return sel
    
#-  -  -  -  -  -  -  

    def plotchartView(self,prop):
        print "?#?#? views.py at line: 190 Dbg-out variable \prop [",prop,"]\n";
        if (request.method == 'GET'):
            if (prop):
                charttype=request.form.get('charttype')
                
                results=apputils.getJSONtoPlot(prop)
                namelist=[]
                vallist=[]
                for result in results["results"]["bindings"]:
                    val=result[prop]["value"]
                    vallist.append(val)
                    name=result[prop]["value"]
                    namelist.append(name)
        
                data = pd.DataFrame({definitions.NAME_OF_MUSEUM: namelist,
                                     prop: vallist})
        
                chart=Chart(data).mark_bar().encode(
                    x=definitions.NAME_OF_MUSEUM.replace(' ','_'),
                    y=prop.replace(' ','_')+':Q'
                    )
                thischart=chart.to_json(data=True, indent=2)
                return render_template('visualisations.html',
                                   alert=None,
                                   document=thischart,
                                   trees=self.getConfiguration(),
                                   charttype=self.getChartTypes(),
                                   title="Visualisations")
            else:
                return render_template('visualisations.html',
                                   alert=None,
                                   document=None,
                                   trees=self.getConfiguration(),
                                   charttype=self.getChartTypes(),
                                   title="Visualisations")
                



