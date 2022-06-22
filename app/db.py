import pickle
import sqlite3
import sys

import click
from flask import current_app, g
from flask.cli import with_appcontext

from app.crawler import Crawler
from app.filter import ALL_PROFILES, Course, Profile
from app import filter

sys.modules['filter'] = filter # pickle.loads で No module named 'filter' と言われるので

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_tables(path='app/'):
    """テーブルを初期化する
    """
    conn = get_db()
    conn.executescript(open(path + 'schema.sql', 'r').read())

@click.command('make-db')
@with_appcontext
def make_db():
    """クローラーを動かしてテーブルにデータを追加する
    """
    conn = get_db()
    init_tables()
    for profile in ALL_PROFILES:
        course_list = Crawler().get_depart_data(profile.year, profile.faculty, profile.depart, profile.division)
        insert_courses(course_list)
        insert_profile_data(course_list, profile)
        conn.commit()
    conn.close()

def course_exists(code: str) -> bool:
    """指定した時間割コードに対応する科目のシラバスが存在するか

    Args:
        code (str): 時間割コード

    Returns:
        bool: 指定した科目のシラバスが存在するか
    """
    conn = get_db()
    cur = conn.execute('select * from courses where code = ?', (code,))
    return cur.fetchone() != None

def insert_courses(course_list: list[Course]) -> int:
    """Course を DB に追加する

    Args:
        course_list (list[Course]): DB に追加する Course の list

    Returns:
        int: 新たに追加した科目の個数
    """
    conn = get_db()
    cnt = 0
    for course in course_list:
        if course_exists(course.code):
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

def get_course_from_code(code: str) -> Course:
    conn = get_db()
    cur = conn.execute('select course from courses where code = ?', (code,))
    return pickle.loads(cur.fetchone()[0])

def get_id_from_profile(p: Profile) -> str:
    profile_id = str(p.year) + p.faculty.value + p.depart.value + p.division.value
    return profile_id

def get_profile_from_id(pid: str) -> Profile:
    year, faculty, depart, division = \
        pid[:4], pid[4:6], pid[6:8], pid[8:]
    return Profile(year, faculty, depart, division)

def insert_profile_data(course_list: list[Course], profile: Profile):
    conn = get_db()
    for course in course_list:
        conn.execute('insert into profiles (profile_id, code)values(?, ?)', (get_id_from_profile(profile), course.code))

def get_course_from_profile(profile: Profile) -> list[Course]:
    conn = get_db()
    rows = conn.execute('select code from profiles where profile_id = ?', (get_id_from_profile(profile),)).fetchall()
    course_list = list()
    for row in rows:
        course_list.append(get_course_from_code(row[0]))
    return course_list
    