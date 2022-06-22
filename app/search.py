from flask import Blueprint, render_template, request
from app.db import get_course_from_profile

from app.filter import Course, Depart, Division, Profile, get_depart, get_faculty

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route('/', methods = ['GET'])
def index():
    depart = request.args.get('depart')
    division = request.args.get('division', Division.N.value)
    grade = request.args.get('grade', 4)
    term = request.args.get('term')
    course_list = []
    try:
        depart, division = Depart(depart), Division(division)
    except:
        return render_template('search.html')
    faculty = get_faculty(depart)
    if get_depart(division) != depart:
        division = Division.N
    course_list: list[Course] = get_course_from_profile(Profile(2019, faculty, depart, division))
    if term:
        course_list = [c for c in course_list if c.term[0] == term[0]]
    try:
        grade = int(grade)
    except:
        grade = 4
    course_list = [c for c in course_list if \
        (type(c.grade_min) == int or c.grade_min.isdecimal())  and int(c.grade_min) <= grade]
    course_dict = dict()
    for c in course_list:
        if c.name in course_dict:
            course_dict[c.name].append(c)
        else:
            course_dict[c.name] = [c]
    # course_list.sort(key=idx_schedule)
    return render_template('search.html', r=course_list, d=course_dict)