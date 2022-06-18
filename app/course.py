from flask import Blueprint, request
from app.db import 
bp = Blueprint("search", __name__, url_prefix="/course")

@bp.route('/<string:code>', methods = ['GET'])
def course(code):
    c = 