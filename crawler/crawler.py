from ast import Div
from gettext import translation
from requests import Session
from filter import *
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from time import sleep

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

    def get_depart_data(self, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N) -> list:
        """全科目の検索結果のページに遷移する

        Args:
            ddl_fac (str, optional): 学部を表す2桁のコード. Defaults to '02'(工学部).

        Returns:
            list: (科目名, 教員) が入ったリストを返す
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
            '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': '$0'}))
        sbj_url_list = []
        soup = BeautifulSoup(r.text, 'html.parser')
        print(r.text)
        page_cnt = len([1 for a in soup.select('a') if 'gvCurList' in a.get('href', '')])

        for page in range(1, page_cnt + 1):
            if page != 1:
                r = self.post_form(CUR_SBJ_LIST_URL, self.make_payload(r.text, {
                    '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'Page${page}'
                }))
                soup = BeautifulSoup(r.text, 'html.parser')
            for t in soup.select('td > a[target]'):
                sbj_url_list.append(t['href'])
        
        print(sbj_url_list)
        # print(r.request.body)



if __name__ == '__main__':
    # Crawler().get_all_course()
    Crawler().get_depart_data(2022, Faculty.Eng, Depart.A, Division.AS)
