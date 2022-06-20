import sqlite3
import pickle
from filter import Course, Profile   
# from flask import current_app, g
# import click
# from flask.cli import with_appcontext

DATABASE = 'db.sqlite3'

def get_db(path='') -> sqlite3.Connection:
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db
    '''
    conn = sqlite3.connect(path + DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn
# conn = sqlite3.connect('schema.db')

def init_tables(conn: sqlite3.Connection, path='app/'):
    conn.executescript(open(path + 'schema.sql', 'r').read())

def course_exists(conn: sqlite3.Connection, code: str):
    '''指定した時間割コードに対応する科目が存在するか
    '''
    cur = conn.execute('select * from courses where code = ?', (code,))
    return cur.fetchone() != None

def insert_courses(conn: sqlite3.Connection, course_list: list[Course]) -> int:
    cnt = 0
    for course in course_list:
        if course_exists(conn, course.code):
            continue
        conn.execute('insert into courses values(?, ?, ?, ?, ?, ?, ?, ?)',
            (course.code,
            course.name,
            course.term,
            course.schedule,
            course.grade_min,
            course.grade_max,
            'classcode',
            pickle.dumps(course))
        )
        cnt += 1
    return cnt

def get_course_from_code(conn: sqlite3.Connection, code: str) -> Course:
    cur = conn.execute('select course from courses where code = ?', (code,))
    return pickle.loads(cur.fetchone()[0])

def get_id_from_profile(p: Profile):
    profile_id = str(p.year) + p.faculty.value + p.depart.value + p.division.value
    return profile_id

def get_profile_from_id(pid: str):
    year, faculty, depart, division = \
        pid[:4], pid[4:6], pid[6:8], pid[8:]
    return Profile(year, faculty, depart, division)

def insert_profile_data(conn: sqlite3.Connection, course_list: list[Course], profile: Profile):
    for course in course_list:
        conn.execute('insert into profiles (profile_id, code)values(?, ?)', (get_id_from_profile(profile), course.code))

def get_course_from_profile(conn: sqlite3.Connection, profile: Profile):
    rows = conn.execute('select code from profiles where profile_id = ?', (get_id_from_profile(profile),)).fetchall()
    course_list = list()
    for row in rows:
        course_list.append(get_course_from_code(conn, row[0]))
    return course_list
    