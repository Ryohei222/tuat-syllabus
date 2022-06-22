from time import sleep
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from requests import Response, Session, get

from app.filter import *

SEARCH_MAIN_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/SearchMain.aspx'
SEARCH_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/SearchList.aspx'
CUR_SEARCH_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurSearch.aspx'
CUR_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurList.aspx'
CUR_SBJ_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurSbjList.aspx'

INTERVAL = 0.5

COURSE_TABLE6_INFOS = (
    'name', 'name_e', 'area_name', 'req_name', 'credit',
    'departments', 'grade_min', 'grade_max', 'term', 'lecture_type', 'code',
    'staff_name', 'staff_name_e', 'staff_section_name',
    'room_name', 'e_mail'
)

COURSE_TABLE4_INFOS = (
    'outline', 'standard', 'content', 'requirements',
    'textbook', 'reference_book', 'grading', 'message',
    'keyword', 'office_hours', 'note1', 'note2', 'url',
    'language', 'language_course', 'update_date'
)


class Crawler:
    def __init__(self):
        self.sess = Session()

    def extract_params(self, html: str) -> dict:
        """HTML 内の hidden な form のパラメータを抽出する

        Args:
            html (str): パラメータを抽出する HTML

        Returns:
            dict: パラメータ名: パラメーターの値　が入った dict
        """
        params = {}
        soup = BeautifulSoup(html, 'html.parser')
        for elem in soup.find_all('input'):
            if elem['type'] in ('hidden', 'text'):
                params[elem['id']] = elem.get('value', '')
        return params

    def extract_course_detail(self, html: str) -> Course:
        soup = BeautifulSoup(html, 'html.parser')
        course = Course()

        table6 = soup.select('#Table6 > tr > td > span')
        for i, t in enumerate(table6):
            setattr(course, COURSE_TABLE6_INFOS[i], t.text)

        table4 = [r for r in soup.select(
            '#Table4 > tr > td') if len(r.text) >= 2]
        for i in range(1, 32, 2):
            setattr(course, COURSE_TABLE4_INFOS[i // 2],
                    table4[i].find_next('span').text)

        course.name_e = course.name_e[1:-1]
        course.staff_name_e = course.staff_name_e[1:-1]
        if type(course.grade_min) == str and course.grade_min.isdigit():
            course.grade_min = int(course.grade_min)
        if type(course.grade_max) == str and course.grade_max.isdigit():
            course.grade_max = int(course.grade_max)
        if type(course.credit) == str and course.credit.isdigit():
            course.credit = int(course.credit)
        return course

    def make_payload(self, html: str, params: dict) -> dict:
        payload = self.extract_params(html) | params
        return payload

    def post_form(self, url, params) -> Response:
        return self.sess.post(url, data=urlencode(params), headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def get_courses(self, url: str) -> list[Course]:
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        course_cnt = len(soup.select('#rdlGrid_gridList > tr')) - 2
        schedules = []
        for i in range(course_cnt):
            schedules.append(
                soup.select_one(f'#rdlGrid_gridList > tr:nth-child({i + 2}) > td:nth-child(5)').text
            )
        course_list: list[Course] = list()
        for i in range(course_cnt):
            s = Session()
            r = s.get(url)
            r = s.post(SEARCH_LIST_URL, self.make_payload(r.text, {
                'rdlGrid:ddlLines': '50', f'rdlGrid:gridList:_ctl{i + 3}:_ctl0': '詳細'
            }))
            course_list.append(self.extract_course_detail(r.text))
            course_list[i].schedule = schedules[i]
            sleep(INTERVAL)
        return course_list

    def transition_depart_result(self, event:int, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N) -> Response:
        """実行教育課程表のページに遷移する
        """
        r = self.sess.get(CUR_SEARCH_URL)
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'ddl_fac', 'ddl_fac': faculty.value}))
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'ddl_dpt', 'ddl_fac': faculty.value, 'ddl_dpt': depart.value}))
        # コースを指定しない場合、ddl_div 属性が存在するとエラーになる
        if division == Division.N:
            r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
                'txt_enter_year': year, 'ddl_fac': faculty.value, 'ddl_dpt': depart.value, 'btnInspection': '検索'}))
        else:
            r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
                '__EVENTTARGET': 'ddl_div', 'ddl_fac': faculty.value, 'ddl_dpt': depart.value, 'ddl_div': division.value}))
            r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
                'txt_enter_year': year, 'ddl_fac': faculty.value, 'ddl_dpt': depart.value, 'ddl_div': division.value, 'btnInspection': '検索'}))
        r = self.post_form(CUR_LIST_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'${event}'}))
        return r

    def get_depart_data(self, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N, limit:int = 1000) -> list[Course]:
        # 共通教育科目
        for i in range(2):
            r = self.transition_depart_result(i, year, faculty, depart, division)
            sbj_list = []
            soup = BeautifulSoup(r.text, 'html.parser')
            page_cnt = len([1 for a in soup.select('a') if 'gvCurList' in a.get('href', '')]) + 1

            for page in range(1, page_cnt + 1):
                if len(sbj_list) >= limit * (i + 1):
                    break
                if page != 1:
                    r = self.post_form(CUR_SBJ_LIST_URL, self.make_payload(r.text, {
                        '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'Page${page}'
                    }))
                    soup = BeautifulSoup(r.text, 'html.parser')
                for t in soup.select('td > a[target]'):
                    if len(sbj_list) >= limit * (i + 1):
                        break
                    course_list = self.get_courses(t['href'])
                    req_name = t.parent.fetchNextSiblings(limit=3)[1].text
                    for c in course_list:
                        c.req_name = req_name
                        sbj_list.append(c)
                        print(f'{year=} {depart=} {division=} {c.name} {c.code}')
          
        return sbj_list
