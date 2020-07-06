from flask import Blueprint

mods = Blueprint("mods",__name__)

from . import views