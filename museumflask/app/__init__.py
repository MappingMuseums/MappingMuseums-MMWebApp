#!/usr/bin/env python
from  config import config
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
#from flask_wtf import Form
from flask_wtf import Form
from wtforms import StringField, SubmitField,RadioField,SelectField
from wtforms.validators import Required
from flask import request
from flask.views import View
from flask  import Blueprint
from flask_compress import Compress

from jinja2 import TemplateNotFound


import pprint
import operator

import sys
import csv
import time
#from xml.dom import minidom
import sys,os
import re
import cgi
import pprint

basedir = os.path.abspath(os.path.dirname(__file__))
INIT_DONE=False

def create_app(config_name):
    global  INIT_DONE
    
    pp = pprint.PrettyPrinter(indent=4)
    app = Flask(__name__)
    Compress(app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    fname=basedir+'/searchapplication.cfg'
    with open(fname) as f:
        configmap = f.readlines()
	for line in configmap:
            print line
            parts=line.split('=')
            parts[0]=parts[0].replace('\t',' ').rstrip().lstrip()
            parts[1]=parts[1].replace('\t',' ').rstrip().lstrip()
            app.config[parts[0]]=parts[1]
	f.close()

    app.config['SECRET_KEY'] = 'hard 2 guess string'

    
    app.config['TEMPLATES_AUTO_RELOAD'] = True 

    bootstrap = Bootstrap(app)
    moment = Moment(app)


    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    from .main import api_bp  as api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    
#    from .api_1_0 import api as api_1_0_blueprint
#    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')


    return app

