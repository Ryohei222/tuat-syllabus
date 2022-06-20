from db import *
from crawler import *
from filter import *

if __name__ == '__main__':
    conn = get_db('app/')
    init_tables(conn)
    for profile in ALL_PROFILES:
        course_list = Crawler().get_depart_data(profile.year, profile.faculty, profile.depart, profile.division, limit = 20)
        insert_courses(conn, course_list)
        insert_profile_data(conn, course_list, profile)
        conn.commit()
    conn.close()