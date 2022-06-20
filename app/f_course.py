from flask import Flask, render_template, request
from db import get_course_from_code, get_course_from_profile
from filter import Course, Depart, Profile, get_faculty
import sqlite3


DB = 'db.sqlite3'
app = Flask(__name__)

@app.route('/course/<string:code>')
def course(code):
    conn = sqlite3.connect(DB)
    c:Course = get_course_from_code(conn, code)
    conn.close()
    return render_template('course.html', c=c.__dict__)

@app.route('/search')
def search():
    year = request.args.get('year')
    depart = request.args.get('depart')
    course_list = []
    if year and depart:
        year, depart = int(year), Depart(depart)
        faculty = get_faculty(depart)
        conn = sqlite3.connect(DB)
        course_list = get_course_from_profile(conn, Profile(year, faculty, depart))
        conn.close()
    return render_template('search.html', r=course_list)


if __name__ == "__main__":
    app.run()