import sqlite3
from filter import Course, Profile, course_to_tuple, get_id_from_profile    
from flask import current_app, g
# import click
# from flask.cli import with_appcontext

DATABASE = ' '

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db
# conn = sqlite3.connect('schema.db')

def course_exists(conn: sqlite3.Connection, code: str):
    cur = conn.execute('select * from courses where code = ?', code)
    return cur.rowcount >= 1

def add_course(conn: sqlite3.Connection, course_list: list[Course]):
    for course in course_list:
        if course_exists(conn, course.code):
            continue
        conn.execute(f'insert into courses values({",".join(["?" for i in range(32)])})', *course_to_tuple(course), 'classcode')

def add_profile_data(conn: sqlite3.Connection, course_list: list[Course], profile: Profile):
    for course in course_list:
        conn.execute(f'insert into profiles values(?, ?)', get_id_from_profile(profile), course.code)

def get_course_from_profile(conn: sqlite3.Connection, profile: Profile):
    rows = conn.execute(f'select code from profiles where profile_id = ?', get_id_from_profile(profile)).fetchall()
    for row in rows:
        cur = conn.execute('select * from courses where code = ?', row[0])
        Course(*cur.fetchone())

def get_course_from_code(conn: sqlite3.Connection, code: str):
    cur = conn.execute('select * from')