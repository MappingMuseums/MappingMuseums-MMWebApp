##
# @file
#  
# Contains the FLASK views and their html implementation and routing.
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from flask.views import View
from flask  import Blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import main as main_blueprint
from . import api  as api_blueprint
from . import apputils
from . import listman
from . import tree
from . import PTreeNode
from . import models
from . import definitions
from . import model_to_view
from . import Configuration

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



@main_blueprint.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also not to cache the pages.
    """
    r.headers["Cache-Control"] = "public, max-age=0, no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 







@main_blueprint.route('/home', methods=['GET'])
def index():
    return render_template('index.html')

@main_blueprint.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@main_blueprint.route('/technical', methods=['GET'])
def technical():
    return render_template('technical.html')

@main_blueprint.route('/browsehelp', methods=['GET'])
def browsehelp():
    return render_template('browsehelp.html')

@main_blueprint.route('/searchhelp', methods=['GET'])
def searchhelp():
    return render_template('searchhelp.html')

@main_blueprint.route('/visualisehelp', methods=['GET'])
def visualisehelp():
    return render_template('visualisehelp.html')


@main_blueprint.route('/blog', methods=['GET'])
def blog():
    return render_template('blog.html')
	
@main_blueprint.route('/findings', methods=['GET'])
def findings():
    return render_template('findings.html')

@main_blueprint.route('/report', methods=['GET'])
def report():
    return render_template('report.html')

@main_blueprint.route('/publications', methods=['GET'])
def publications():
    return render_template('publications.html')



from . import interviews
interviews= interviews.Interviews()

main_blueprint.add_url_rule('/interviews',
                            view_func=interviews.interviewsView,
                            methods=['GET','POST'])

from . import interviewresults
interviewresults= interviewresults.Interviewresults()

main_blueprint.add_url_rule('/interviewresults',
                            view_func=interviewresults.interviewresultsView,
                            methods=['POST'])

@main_blueprint.route('/aboutapp', methods=['GET'])
def aboutapp():
    return render_template('aboutapp.html')

@main_blueprint.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')



@main_blueprint.route('/people', methods=['GET'])
def people():
    return render_template('people.html')

@main_blueprint.route('/acknowledgements', methods=['GET'])
def acknowledgements():
    return render_template('acknowledgements.html')

@main_blueprint.route('/funding', methods=['GET'])
def funding():
    return render_template('funding.html')

@main_blueprint.route('/copyright', methods=['GET'])
def copyright():
    return render_template('copyright.html')

@main_blueprint.route('/glossary', methods=['GET'])
def glossary():
    return render_template('glossary.html')

@main_blueprint.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

@main_blueprint.route('/sources', methods=['GET'])
def sources():
    return render_template('sources.html')
	
@main_blueprint.route('/software', methods=['GET'])
def software():
    return render_template('software.html')

@main_blueprint.route('/data', methods=['GET'])
def data():
    return render_template('data.html')

@main_blueprint.route('/archive', methods=['GET'])
def archive():
    return render_template('archive.html')

@main_blueprint.route('/films', methods=['GET'])
def films():
    return render_template('films.html')



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

@main_blueprint.route('/json', methods=['GET'])
def jsondocument():

    testdoc="""
{
  "$schema": "https://vega.github.io/schema/vega/v3.0.json",
  "width": 400,
  "height": 200,
  "padding": 5,

  "data": [
    {
      "name": "table",
      "values": [
        {"category": "A", "amount": 28},
        {"category": "B", "amount": 55},
        {"category": "C", "amount": 43},
        {"category": "D", "amount": 91},
        {"category": "E", "amount": 81},
        {"category": "F", "amount": 53},
        {"category": "G", "amount": 19},
        {"category": "H", "amount": 87}
      ]
    }
  ],

  "signals": [
    {
      "name": "tooltip",
      "value": {},
      "on": [
        {"events": "rect:mouseover", "update": "datum"},
        {"events": "rect:mouseout",  "update": "{}"}
      ]
    }
  ],

  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width"
    },
    {
      "name": "yscale",
      "domain": {"data": "table", "field": "amount"},
      "nice": true,
      "range": "height"
    }
  ],

  "axes": [
    { "orient": "bottom", "scale": "xscale" },
    { "orient": "left", "scale": "yscale" }
  ],

  "marks": [
    {
      "type": "rect",
      "from": {"data":"table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category", "offset": 1},
          "width": {"scale": "xscale", "band": 1, "offset": -1},
          "y": {"scale": "yscale", "field": "amount"},
          "y2": {"scale": "yscale", "value": 0}
        },
        "update": {
          "fill": {"value": "steelblue"}
        },
        "hover": {
          "fill": {"value": "red"}
        }
      }
    },
    {
      "type": "text",
      "encode": {
        "enter": {
          "align": {"value": "center"},
          "baseline": {"value": "bottom"},
          "fill": {"value": "#333"}
        },
        "update": {
          "x": {"scale": "xscale", "signal": "tooltip.category", "band": 0.5},
          "y": {"scale": "yscale", "signal": "tooltip.amount", "offset": -2},
          "text": {"signal": "tooltip.amount"},
          "fillOpacity": [
            {"test": "datum === tooltip", "value": 0},
            {"value": 1}
          ]
        }
      }
    }
  ]
}
"""


    
    return render_template('json.html',
                           document=testdoc)








#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

@main_blueprint.route('/Museum/id/<mid>', methods=['GET'])
def showdocument(mid):
    try:
        properties=apputils.getMuseumPropertiesForId(mid)
    except Exception, e:
	print str(e)
        return render_template('message.html', title="Internal application error",message="Internal Application Error X detected. The Mapping Museums team would be very grateful if you could please use Get in Touch, under the Contact Us tab, to describe the actions that you took that led to this error message")
            
    for res in properties["results"]["bindings"]:
        text=res["p"]["value"]
        parts=text.split('/')
        partlen=len(parts)-1
        heading=parts[partlen].replace(definitions.HASNAME,'')
        res["p"]["value"]=heading
        



    return render_template('newdocid.html',
                           docid=mid,
                           properties=properties,
                           title="Details about a museum")




#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AppConfiguration(View):

#-  -  -  -  -  -  -  

    def getConfiguration(self):
        t = tree.Tree("Options",False,False)
        t.addNodeAndLevel("Selectionlists",True,False)
        for item in definitions.LISTS.keys():
            t.addLeaf('<a href="{}">{}</a>'.format("/configuration/"+item,item))

                
        t.closeLevel()
        t.closeTree()
        

        return t.getTree()


#-  -  -  -  -  -  -  

    def saveProperty(self,prop,values):
        res=listman.updateList(prop,values)
        return res

#-  -  -  -  -  -  -  

    def resetProperty(self,prop):
        res=listman.resetList(prop)
        return res

#-  -  -  -  -  -  -  

    def addComplementarySetNonSelected(self,prop,results):

        templist=definitions.RESET_definitions.LISTS_VALUES[prop+definitions.LISTNAME]
        for item in templist:
            found=False
            for res in results:
                if (res.find(item) > 0):
                    found=True
                    break
            if (not found):
                #item not selected add it as available
                selstr='<option value="'+item+'">'+item.replace("_"," ")+'</option> \n'
                results.append(selstr)
                
        return results

#-  -  -  -  -  -  -  
    def createSelectList(self,values,reset_values):
	sel=[]
	for val in values:
	    sel.append('<option value="{}" selected="true">{}</option> \n'.format(val,val))
	for val in reset_values:
	    if (val not in values):
		sel.append('<option value="{}">{}</option> \n'.format(val,val))
	    
	return sel
#-  -  -  -  -  -  -  

    def dispatch_request(self,prop):
        if (request.method == 'POST'):
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(request.form)
            ms=request.form.getlist('multiselect[]')
            msl=len(ms)

            propertytosave=request.form.get('property')
            propertytosave=propertytosave.replace(' ','_')
            if (not propertytosave or len(propertytosave) < 1):
                return render_template('message.html', title="Configuration",message=" No property present")

            operation=request.form.get('operation')
            if (operation == 'reset'):
                try:
                    self.resetProperty(propertytosave)
                    models.initdefinitions(True)
                except Exception, e:
		    print str(e)

                    return render_template('configuration.html',
                                           alert_type="error",
                                           alert="Configuration reset failed.",
                                           results=None,trees=self.getConfiguration(),prop=propertytosave.replace('_',' '))
                    
                re_set=[]
                for item in definitions.DATAGROUPS:
                    group,option=item
                    if (group == propertytosave):
                        opt=option.replace('>','selected="true">')
                        re_set.append(opt)

                return render_template('configuration.html',
                                       alert_type="success",
                                       alert="Configuration successfully reset.",results=re_set,trees=self.getConfiguration(),prop=propertytosave.replace('_',' '))
            
            else:
                if (msl < 1):
                    return render_template('message.html', title="Configuration",message=" No property selected")
                try:
                    status=self.saveProperty(propertytosave,ms)
                    models.initdefinitions(True)
                    return render_template('configuration.html',
                                           alert_type="success",
                                           alert="Configuration successfully saved.",results=None,trees=self.getConfiguration(),prop=propertytosave.replace('_',' '))
                except Exception, e:
		    print str(e)
                    return render_template('configuration.html',
                                           alert_type="error",
                                           alert="Configuration failed to save.",results=None,trees=self.getConfiguration(),prop=propertytosave.replace('_',' '))
                    
            
            
        else: # GET
            if (prop == None):
                return render_template('configuration.html',
                                       alert_type="success",
                                       alert=None,results=None,trees=self.getConfiguration())
            elif (prop in definitions.LISTS):
                results=[]
		for configurablenames in definitions.NAMED_CONFIGURABLE_PROPERTIES:
		    if (prop.find(configurablenames) > -1):
			# Configurable type search display columns
			if (prop in definitions.LISTS_VALUES.keys()):
			    values=definitions.LISTS_VALUES[prop]
			    reset_values=definitions.RESET_definitions.LISTS_VALUES[prop+definitions.LISTNAME]
			    results=self.createSelectList(values,reset_values)
			    if (len(results) == 0):
				return render_template('message.html', title="Configuration",message=" Selected property not stored in db")
			    else:
				return render_template('configuration.html',
						       alert_type="success",
						       alert=None,results=results,trees=self.getConfiguration(),prop=prop.replace('_',' '))
		# configurable type definitions.LIST like governance
		for item in definitions.DATAGROUPS:
		    group,option=item
		    if (group == prop):
			opt=option.replace('>','selected="true">')
			results.append(opt)
		results=self.addComplementarySetNonSelected(prop,results)
		
		return render_template('configuration.html',
				       alert_type="success",
				       alert=None,results=results,trees=self.getConfiguration(),prop=prop.replace('_',' '))
            else:
                return render_template('message.html', title="Configuration",message="Not a known property selected")
                
            
                

main_blueprint.add_url_rule('/configuration',
                            defaults={'prop': None},
                            view_func=AppConfiguration.as_view('configuration'),
                            methods=['GET','POST'])

main_blueprint.add_url_rule('/configuration/<prop>',
                            view_func=AppConfiguration.as_view('configuration_prop'),
                            methods=['GET','POST'])


stopwords=['of','and','&','museum','collection ','gallery ','national','historical']

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Static pages with template
@main_blueprint.route('/showpage/<page>', methods=['GET'])
def showstaticpage(page):
    return render_template('showpage.html',page=page)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
from . import showmuseumtypes
showmuseumtypes = showmuseumtypes.ShowMuseumTypes()

main_blueprint.add_url_rule('/browseproperties',
                            defaults={'propertytodisplay': None},
			    view_func=showmuseumtypes.showmuseumtypesView,
			    methods=['GET'])

main_blueprint.add_url_rule('/browseproperties/<propertytodisplay>',
                            view_func=showmuseumtypes.showmuseumtypesView,
                            methods=['GET'])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
from . import museum
museum = museum.Museum()



main_blueprint.add_url_rule('/Museum/<musid>',
                            view_func=museum.museumView,
                            methods=['GET'])

#-------------------------------------------------------------------------------------

from . import mapchart
mapchart= mapchart.MapChart()

main_blueprint.add_url_rule('/map',
                            defaults={'prop': None,'subprop': None},
                            view_func=mapchart.mapchartView,
                            methods=['GET'])

main_blueprint.add_url_rule('/map/<prop>/<subprop>',
                            view_func=mapchart.mapchartView,
                            methods=['GET'])

main_blueprint.add_url_rule('/map/<prop>',
                            defaults={'subprop': None},
                            view_func=mapchart.mapchartView,
                            methods=['GET'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from . import chloro
chloro= chloro.Chloro()

main_blueprint.add_url_rule('/chloro/<prop>',
                            view_func=chloro.chloroView,
                            methods=['GET'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
from . import search
search= search.Search()

main_blueprint.add_url_rule('/search',
                            view_func=search.searchView,
                            methods=['GET','POST'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
from . import addmuseum
addmuseum= addmuseum.Addmuseum()

main_blueprint.add_url_rule('/addmuseum',
                            view_func=addmuseum.addmuseumView,
                            methods=['GET','POST'])
from . import editmuseum
editmuseum= editmuseum.Editmuseum()

main_blueprint.add_url_rule('/editmuseumdata',
                            view_func=editmuseum.editmuseumView,
                            methods=['GET','POST'])

from . import allmus
allmus= allmus.Allmus()

main_blueprint.add_url_rule('/allmus',
                            view_func=allmus.allmusView,
                            methods=['GET','POST'])
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#from . import addmuseumfiona
#addmuseumfiona= addmuseumfiona.Addmuseumfiona()

#main_blueprint.add_url_rule('/addmuseumfiona',
                            #view_func=addmuseumfiona.addmuseumfionaView,
                            #methods=['GET','POST'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from . import modmuseum
modmuseum= modmuseum.Modmuseum()

main_blueprint.add_url_rule('/xp281/X1zyc3401',
                            view_func=modmuseum.modmuseumView,
                            methods=['GET','POST'])
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from . import changemuseum
changemuseum= changemuseum.Changemuseum()

main_blueprint.add_url_rule('/xp281/X3tr46hj2',
                            view_func=changemuseum.changemuseumView,
                            methods=['GET','POST'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   
    
from . import nakedid
nakedid= nakedid.NakedId()

main_blueprint.add_url_rule('/Museum/nid/<nid>/<mid>',
                            view_func=nakedid.nakedidView,
                            methods=['GET'])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from . import datasetversion
datasetversion = datasetversion.Datasetversion()
main_blueprint.add_url_rule('/datasetversion',
			    view_func=datasetversion.datasetversionView,
			    methods=['GET'])


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from . import boks
boks= boks.Boks()
main_blueprint.add_url_rule('/visualisations',
                            defaults={'plot': None},
			    view_func=boks.boksView,
			    methods=['GET','POST'])

main_blueprint.add_url_rule('/visualisations/<path:plot>',
                            defaults={'plot': None},
			    view_func=boks.boksPlotView,
			    methods=['GET'])


# API - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from . import admingeoservice
api_blueprint.add_resource(admingeoservice.Admingeoservice, '/api/geoadmin/get/<propertytodisplay>')

from . import datasetversionservice
api_blueprint.add_resource(datasetversionservice.Datasetversionservice, '/api/datasetversion/get')


