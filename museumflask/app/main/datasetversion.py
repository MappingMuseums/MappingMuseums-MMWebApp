from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import listman
from . import tree
from . import PTreeNode
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

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Datasetversion():

    VERSION=None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    def datasetversionView(self):
	if (VERSION == None):
	    Datasetversion.VERSION=definitions.DATASETVERSION.split("/")[5]

        if (request.method == 'GET'):
            
            return VERSION
