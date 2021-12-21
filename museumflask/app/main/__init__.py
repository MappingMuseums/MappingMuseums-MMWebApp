from flask import Blueprint
from flask_restful import Api, Resource, url_for

main = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# DONT REMOVE BELOW... For some reason this insures the moduls are initialised properly
from . import views, errors,models,apputils

