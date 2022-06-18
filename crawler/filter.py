from enum import Enum, unique, auto
from dataclasses import dataclass

@unique
class Faculty(Enum):
    Agr = '01'
    Eng = '02'
    # GAgr = '05'
    # GEng = '06'

class Depart(Enum):
    An = '51'
    Bn = '52'
    En = '53'
    Rn = '54'
    Vn = '56'
    B = '61'
    L = '62'
    C = '63'
    U = '64'
    M = '65'
    A = '66'
    N = ''

class Division(Enum):
    AS = '098'
    AE = '099'
    N = ''

def get_depart(division: Division):
    return Depart[division.name[0]]

def get_faculty(depart: Depart):
    if depart == Depart.N:
        return Faculty.Agr 
    if depart.value[0] == '5':
        return Faculty.Agr
    else:
        return Faculty.Eng

CURRENT_YEAR = 2022
ENTRANCE_YEAR = [2019, 2020, 2021, 2022]


class Profile:
    def __init__(self, year: int = CURRENT_YEAR, faculty: Faculty = Faculty.Eng, depart: Depart = Depart.N, division: Division = Division.N, grade: int = 1) -> None:
        if not year in ENTRANCE_YEAR:
            year = ENTRANCE_YEAR
        if not grade in [1, 2, 3, 4, 5, 6]:
            grade = 1
        self.year = year
        self.faculty = faculty
        self.depart = depart
        self.grade = grade
        self.division = division


def get_all_profiles():
    ret = list()
    for year in ENTRANCE_YEAR:
        for depart in Depart:
            if depart != Depart.N:
                ret.append(
                    Profile(year=year, faculty=get_faculty(depart), depart=depart)
                )
                print(f'{depart=} {year=}')
        for division in Division:
            if division != Division.N:
                depart = get_depart(division)
                ret.append(
                    Profile(year=year, faculty=get_faculty(depart), depart=depart, division=division)
                )
    return ret

ALL_PROFILES = get_all_profiles()

class Filter:
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        pass


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


@dataclass
class Course:
    ''' 講義の情報を持つ dataclass '''
    name: str = ''
    name_e: str = ''
    area_name: str = ''
    req_name: str = ''
    credit: int = 0
    departments: str = ''
    grade_min: int = 0
    grade_max: int = 0
    term: str = ''
    lecture_type: str = ''
    code: str = ''
    staff_name: str = ''
    staff_name_e: str = ''
    staff_section_name: str = ''
    room_name: str = ''
    e_mail: str = ''
    outline: str = ''
    standard: str = ''
    content: str = ''
    requirements: str = ''
    textbook: str = ''
    reference_book: str = ''
    grading: str = ''
    message: str = ''
    keyword: str = ''
    office_hours: str = ''
    note1: str = ''
    note2: str = ''
    url: str = ''
    language: str = ''
    language_course: str = ''
    update_date: str = ''

def course_to_tuple(c: Course):
    t = (
        c.code,
        c.name,
        c.name_e,
        c.area_name,
        c.req_name,
        c.departments,
        c.term,
        c.lecture_type,
        c.staff_name,
        c.staff_name_e,
        c.staff_section_name,
        c.room_name,
        c.e_mail,
        c.outline,
        c.standard,
        c.content,
        c.requirements,
        c.textbook,
        c.reference_book,
        c.grading,
        c.message,
        c.keyword,
        c.office_hours,
        c.note1,
        c.note2,
        c.url,
        c.language,
        c.language_course,
        c.update_date,
        c.grade_min,
        c.grade_max,
        c.credit,
    )
    return t