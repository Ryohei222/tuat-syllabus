from ast import Div
from calendar import c
from gettext import translation
from requests import Response, Session
from filter import *
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from time import sleep
import pickle

SEARCH_MAIN_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/SearchMain.aspx'
SEARCH_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/SearchList.aspx'
CUR_SEARCH_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurSearch.aspx'
CUR_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurList.aspx'
CUR_SBJ_LIST_URL = 'https://spica.gakumu.tuat.ac.jp/syllabus/CurSbjList.aspx'


class Crawler:
    def __init__(self):
        self.sess = Session()

    def extract_params(self, res: str) -> dict:
        """HTML 内の form のパラメータを抽出する

        Args:
            res (str): パラメータを抽出する HTML

        Returns:
            dict: パラメータ名: パラメーターの値　が入った dict
        """

        params = {}
        soup = BeautifulSoup(res, 'html.parser')
        for elem in soup.find_all('input'):
            if elem['type'] in ('hidden', 'text'):
                params[elem['id']] = elem.get('value', '')
        return params

    def make_payload(self, res: str, params: dict):
        payload = self.extract_params(res) | params
        return payload


    def post_form(self, url, params):
        return self.sess.post(url, data=urlencode(params), headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def transition_all_course_result(self, ddl_fac: str = '02') -> str:
        """全科目の検索結果のページに遷移する

        Args:
            ddl_fac (str, optional): 学部を表す2桁のコード. Defaults to '02'(工学部).

        Returns:
            str: 検索結果の HTML
        """
        
        r = self.sess.get(SEARCH_MAIN_URL)
        r = self.post_form(SEARCH_MAIN_URL, self.make_payload(r.text, {
            'ddl_fac': ddl_fac, 'ddl_year': '2022', 'btnSearch': '検　索'}))
        r = self.post_form(SEARCH_LIST_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'rdlGrid$ddlLines', 'rdlGrid:ddlLines': '0'}))
        return r.text

    def get_one_course_detail(self, ddl_fac, num):
        r = self.transition_all_course_result(ddl_fac)
        return self.get_course_detail(r, num)

    def get_course_detail(self, r, num):
        res = self.sess.post(SEARCH_LIST_URL, self.make_payload(r, {
            'rdlGrid:ddlLines': '0', f'rdlGrid:gridList:_ctl{num + 2}:_ctl0': '詳細'
        }))
        soup = BeautifulSoup(res.text, 'html.parser')
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
        return course

    def get_all_course(self, ddl_fac: str = '02'):
        res = self.transition_all_course_result(ddl_fac)
        soup = BeautifulSoup(res, 'html.parser')
        course_cnt = int(soup.select('#rdlGrid_gridList > tr')
                         [-2].select('font')[0].text)
        courses = []
        for i in range(1, course_cnt + 1):
            courses.append(self.get_course_detail(res, i))
            print(courses[i - 1].name)
            sleep(0.5)

        return courses

    def transition_depart_result(self, event:int, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N) -> Response:
        """実行教育課程表のページに遷移する
        """
        r = self.sess.get(CUR_SEARCH_URL)
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'ddl_fac', 'ddl_fac': faculty.value}))
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'ddl_dpt', 'ddl_fac': faculty.value, 'ddl_dpt': depart.value}))
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'ddl_div', 'ddl_fac': faculty.value, 'ddl_dpt': depart.value, 'ddl_div': division.value}))
        r = self.post_form(CUR_SEARCH_URL, self.make_payload(r.text, {
            'txt_enter_year': year, 'ddl_fac': faculty.value, 'ddl_dpt': depart.value, 'ddl_div': division.value, 'btnInspection': '検索'}))
        r = self.post_form(CUR_LIST_URL, self.make_payload(r.text, {
            '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'${event}'}))
        return r

    def get_depart_data(self, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N) -> list[Course]:
        """全科目の検索結果のページに遷移する

        Args:
            ddl_fac (str, optional): 学部を表す2桁のコード. Defaults to '02'(工学部).

        Returns:
            list: (科目名, 教員) が入ったリストを返す
        """

        # 共通教育科目
        r = self.transition_depart_result(0, year, faculty, depart, division)
        sbj_list = []
        soup = BeautifulSoup(r.text, 'html.parser')
        page_cnt = len([1 for a in soup.select('a') if 'gvCurList' in a.get('href', '')]) + 1
        area_name = ''
        for page in range(1, page_cnt + 1):
            if page != 1:
                r = self.post_form(CUR_SBJ_LIST_URL, self.make_payload(r.text, {
                    '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'Page${page}'
                }))
                soup = BeautifulSoup(r.text, 'html.parser')
            for t in soup.select('td > a[target]'):
                c = Course()
                T = t.parent
                if T.previousSibling.text != '\xa0':
                    area_name = T.previousSibling.text
                c.area_name = area_name
                c.name = t.text
                c.url = t['href']
                S = T.fetchNextSiblings(limit=3)
                c.credit = int(S[0].text)
                c.req_name = S[1].text
                if S[2].text != '\xa0':
                    c.grade_min = int(S[2].text)
                sbj_list.append(c)

        r = self.transition_depart_result(1, year, faculty, depart, division)
        soup = BeautifulSoup(r.text, 'html.parser')
        page_cnt = len([1 for a in soup.select('a') if 'gvCurList' in a.get('href', '')]) + 1

        for page in range(1, page_cnt + 1):
            if page != 1:
                r = self.post_form(CUR_SBJ_LIST_URL, self.make_payload(r.text, {
                    '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'Page${page}'
                }))
                soup = BeautifulSoup(r.text, 'html.parser')
            for t in soup.select('td > a[target]'):
                c = Course()
                T = t.parent
                if T.previousSibling.text != '\xa0':
                    area_name = T.previousSibling.text
                c.area_name = area_name
                c.name = t.text
                c.url = t['href']
                S = T.fetchNextSiblings(limit=3)
                c.credit = int(S[0].text)
                c.req_name = S[1].text
                if S[2].text != '\xa0':
                    c.grade_min = int(S[2].text)
                sbj_list.append(c)
        
        return sbj_list



if __name__ == '__main__':
    if input('ダウンロードしますか？: ') == 'y':
        course_list = Crawler().get_all_course()
        with open('course_list.pickle', mode='wb') as f:
            pickle.dump(course_list, f)
    else:
        with open('course_list.pickle', mode='rb') as f:
            course_list = pickle.load(f)
    name_to_course = dict()
    for course in course_list:
        if not course.name in name_to_course:
            name_to_course[course.name] = [course]
        else:
            name_to_course[course.name].append(course)
    for p in ALL_PROFILES:
        if p.faculty != Faculty.Eng:
            continue
        depart_course_list = Crawler().get_depart_data(p.year, Faculty.Eng, p.depart, p.division)
        for dcourse in depart_course_list:
            print(f'{dcourse.name=}')
            for course in name_to_course[dcourse.name]:
                print(course)
        break