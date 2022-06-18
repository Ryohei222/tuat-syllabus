import sqlite3

from crawler.filter import Course, Profile, course_to_tuple, ALL, get_id_from_profile    
# conn = sqlite3.connect('schema.db')

def course_exists(cur: sqlite3.Cursor, code: str):
    cur.execute('select * from courses where code = ?', code)
    return len(cur.fetchall()) >= 1

def add_course(cur: sqlite3.Cursor, course_list: list[Course]):
    for course in course_list:
        if course_exists(cur, course.code):
            continue
        cur.execute(f'insert into courses values({",".join(["?" for i in range(32)])})', *course_to_tuple(course), 'classcode')

def add_profile_data(cur: sqlite3.Cursor, course_list: list[Course], profile: Profile):
    for course in course_list:
        cur.execute(f'insert into profiles values(?, ?)', get_id_from_profile(profile), course.code)

def get_course_from_profile(cur: sqlite3.Cursor, profile: Profile):
    cur.execute(f'select code from profiles where profile_id = ?', get_id_from_profile(profile))
    codes = [row[0] for row in cur.fetchall()]
    for code in codes:
        cur.execute('select * from courses where code = ?', code)
        Course(*cur.fetchone())
    