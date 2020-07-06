from flask import Blueprint

osf = Blueprint("osf",__name__)

from . import views