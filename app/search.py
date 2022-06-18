from flask import Blueprint, request

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route('', methods = ['GET'])
def search():
    