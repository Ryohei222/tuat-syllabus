from app.crawler import Crawler
from app.filter import *

def test_single_download():
    depart_course_list = Crawler().get_depart_data(2020, Faculty.Eng, Depart.A, Division.AS)
    