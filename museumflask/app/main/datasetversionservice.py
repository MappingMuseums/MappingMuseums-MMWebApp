##
# @file
#  
# The api service to return the data set version 
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import definitions

from flask import current_app as app
import pprint
import traceback
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from flask_restful import Api, Resource, url_for
from flask.views import MethodView

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Datasetversionservice(MethodView):


    VERSION=None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -



## Purpose:Returns the dataset version as a string
# 
    def get(self):
	if (Datasetversionservice.VERSION == None):
	    Datasetversionservice.VERSION=definitions.DATASETVERSION.split("/")[5]

        return Datasetversionservice.VERSION


