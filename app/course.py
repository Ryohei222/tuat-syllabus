from flask import Blueprint, request, render_template
from app.db import get_course_from_code
bp = Blueprint("search", __name__, url_prefix="/course")

@bp.route('/<string:code>', methods = ['GET'])
def course(code):
    c = get_course_from_code(code)
    return render_template('code.html', code)   