import sqlite3

from app import db
from app.filter import *

TEST_DB = 'test.sqlite3'

def test_init_tables():
    tables = ['courses', 'profiles']
    conn = sqlite3.connect(TEST_DB)
    db.init_tables(conn)
    cur = conn.execute('select * from sqlite_master')
    names = (row[1] for row in cur.fetchall())

    assert len(set(tables) & set(names)) == 2
    
def test_insert_courses():
    course_list = [
        Course(name='hoge', code = 'thiscode'),
        Course(name='fuga', code = 'thatcode'),
        Course(name='123', code = 'testcode'),
    ]
    invalid_course_list =[
        Course(name='hoge', code = '1234code'),
        Course(name='fuga', code = '1234code')
    ]
    conn = sqlite3.connect(TEST_DB)
    
    # 正しいケース
    assert 3 == db.insert_courses(conn, course_list)
    assert db.course_exists(conn, 'thiscode')
    assert db.course_exists(conn, 'thatcode')
    assert db.course_exists(conn, 'testcode')

    # code が重複するケース
    assert 1 == db.insert_courses(conn, invalid_course_list)

def test_profiles():
    proile_list = [
        Profile(2022, Faculty.Eng, Depart.A, Division.AS),
        Profile(2022, Faculty.Agr, Depart.Bn),
        Profile(2022, Faculty.Eng, Depart.M),
    ]
    course_list = [
        Course(name='aabbbbxx', code = 'thiscode'),
        Course(name='hogehgoe', code = 'thatcode'),
        Course(name='cccccccc', code = 'testcode'),
    ]
    conn = sqlite3.connect(TEST_DB)
    db.init_tables(conn)
    db.insert_courses(conn, course_list)
    db.insert_profile_data(conn, course_list, proile_list[0])
    res = db.get_course_from_profile(conn, proile_list[0])
    for course in course_list:
        assert course in res