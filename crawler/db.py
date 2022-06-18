import sqlite3

from crawler.filter import Course, Profile, course_to_tuple, ALL    
# conn = sqlite3.connect('schema.db')

def course_exists(cur: sqlite3.Cursor, code: str):
    return len(cur.execute('select * from courses where code = ?', code)) >= 1

def add_course(cur: sqlite3.Cursor, course_list: list[Course]):
    for course in course_list:
        if course_exists(cur, course.code):
            continue
        cur.execute(f'insert into courses values({",".join(["?" for i in range(32)])})', *course_to_tuple(course), 'classcode')
    cur.commit()

def add_profile_data(cur: sqlite3.Cursor, course_list: list[Course], profile: Profile):
    for course in course_list:
