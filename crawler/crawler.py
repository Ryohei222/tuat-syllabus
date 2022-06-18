from requests import Response, Session, get, request
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

INTERVAL = 0.5

class Crawler:
    def __init__(self):
        self.sess = Session()

    def extract_params(self, html: str) -> dict:
        """HTML 内の form のパラメータを抽出する

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

    def make_payload(self, html: str, params: dict) -> dict:
        payload = self.extract_params(html) | params
        return payload

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

    def post_form(self, url, params) -> Response:
        return self.sess.post(url, data=urlencode(params), headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def transition_all_course_result(self, ddl_fac: str = '02') -> Response:
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
        return r

    def get_one_course_detail(self, ddl_fac, num) -> Course:
        # test に移す
        r = self.transition_all_course_result(ddl_fac)
        return self.get_course_detail(r, num)

    def get_course_detail(self, r:Response, num:int , ddlLines:int=0) -> Course:
        # ddlLines: 1ページあたりの件数
        res = self.sess.post(SEARCH_LIST_URL, self.make_payload(r.text, {
            'rdlGrid:ddlLines': f'{ddlLines}', f'rdlGrid:gridList:_ctl{num + 2}:_ctl0': '詳細'
        }))
        print(res.request.body)
        return self.extract_course_detail(res.text)

    def get_all_course(self, ddl_fac: str = '02') -> list[Course]:
        r = self.transition_all_course_result(ddl_fac)
        soup = BeautifulSoup(r.text, 'html.parser')
        course_cnt = int(soup.select('#rdlGrid_gridList > tr')
                         [-2].select('font')[0].text)
        course_list = list()
        for i in range(1, course_cnt + 1):
            course_list.append(self.get_course_detail(r, i))
            sleep(INTERVAL)

        return course_list

    def get_courses(self, url: str) -> list[Course]:
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        course_cnt = len(soup.select('#rdlGrid_gridList > tr')) - 2
        print(course_cnt)
        course_list = list()
        for i in range(1, course_cnt + 1):
            s = Session()
            r = s.get(url)
            r = s.post(SEARCH_LIST_URL, self.make_payload(r.text, {
                'rdlGrid:ddlLines': '50', f'rdlGrid:gridList:_ctl{i + 2}:_ctl0': '詳細'
            }))
            course_list.append(self.extract_course_detail(r.text))
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

    def get_depart_data(self, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N) -> list[Course]:
        """全科目の検索結果のページに遷移する

        Args:
            ddl_fac (str, optional): 学部を表す2桁のコード. Defaults to '02'(工学部).

        Returns:
            list: (科目名, 教員) が入ったリストを返す
        """
        # 共通教育科目
        for i in range(2):
            r = self.transition_depart_result(i, year, faculty, depart, division)
            sbj_list = []
            soup = BeautifulSoup(r.text, 'html.parser')
            page_cnt = len([1 for a in soup.select('a') if 'gvCurList' in a.get('href', '')]) + 1

            for page in range(1, page_cnt + 1):
                if page != 1:
                    r = self.post_form(CUR_SBJ_LIST_URL, self.make_payload(r.text, {
                        '__EVENTTARGET': 'gvCurList', '__EVENTARGUMENT': f'Page${page}'
                    }))
                    soup = BeautifulSoup(r.text, 'html.parser')
                for t in soup.select('td > a[target]'):
                    course_list = self.get_courses(t['href'])
                    req_name = t.parent.fetchNextSiblings(limit=3)[1].text
                    for c in course_list:
                        c.req_name = req_name
                        sbj_list.append(c)
                return sbj_list
          
        return sbj_list

if __name__ == '__main__':
    depart_course_list = Crawler().get_depart_data(2020, Faculty.Eng, Depart.A, Division.AS)
    '''
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
        print(f'{p.faculty=} {p.depart=} {p.division=} {p.year=}')
        if p.faculty != Faculty.Eng:
            continue
        depart_course_list = Crawler().get_depart_data(p.year, Faculty.Eng, p.depart, p.division)
        for dcourse in depart_course_list:
            # dcourse: (科目区分, url, 単位, 受講できる学年, 必修 / 選択必修)
            # 教員名が与えられないので取得する必要がある。
            print(f'{dcourse.url}')
            if not dcourse.name in name_to_course:
                continue
            for course in name_to_course[dcourse.name]:
                print(f'{course.name=} {course.staff_name=}')
    '''