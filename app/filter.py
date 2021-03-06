from enum import Enum, unique
from dataclasses import dataclass

@unique
class Faculty(Enum):
    Agr = '01'
    Eng = '02'
    # GAgr = '05'
    # GEng = '06'

@unique
class Depart(Enum):
    An = '51'
    Bn = '52'
    En = '53'
    Rn = '54'
    Vn = '56'
    L = '61'
    B = '62'
    C = '63'
    U = '64'
    M = '65'
    A = '66'
    N = '00'

@unique
class Division(Enum):
    L1 = '092'
    L2 = '093'
    U1 = '094'
    U2 = '095'
    M1 = '096'
    M2 = '097'
    AS = '098'
    AE = '099'
    N = '000'

def get_depart(division: Division) -> Depart:
    return Depart[division.name[0]]

def get_faculty(depart: Depart) -> Faculty:
    if depart == Depart.N:
        return Faculty.Agr 
    if depart.value[0] == '5':
        return Faculty.Agr
    else:
        return Faculty.Eng

CURRENT_YEAR = 2022
ENTRANCE_YEAR = [2019, 2020, 2021, 2022]

class InvalidYearError(Exception):
    def __str__(self) -> str:
        return '対応していない入学年度です'

class InvalidProfileError(Exception):
    def __str__(self) -> str:
        return '(Faculty, Depart, Division) の組が正しくありません'

class Profile:
    def __init__(self, year: int, faculty: Faculty, depart: Depart, division: Division = Division.N, grade: int = 1) -> None:
        if not year in ENTRANCE_YEAR:
            raise InvalidYearError()
        self.year = year
        self.faculty = faculty
        if get_faculty(depart) != faculty:
            raise InvalidProfileError()
        self.depart = depart
        if division != Division.N and get_depart(division) != depart:
            raise InvalidProfileError()
        self.division = division
        self.grade = grade

def get_all_profiles() -> list[Profile]:
    ret = list()
    year = 2019
    for depart in Depart:
        if depart != Depart.N:
            ret.append(
                Profile(year=year, faculty=get_faculty(depart), depart=depart)
            )
    for division in Division:
        if division != Division.N:
            depart = get_depart(division)
            ret.append(
                Profile(year=year, faculty=get_faculty(depart), depart=depart, division=division)
            )
    return ret

ALL_PROFILES: list[Profile] = get_all_profiles()

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
    schedule: str = ''
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

def idx_schedule(course: Course) -> int:
    schedule = course.schedule
    if not (schedule[0] in '月火水木金'):
        return 100
    s = schedule.split(',')[0]
    a = '月火水木金'.find(s[0])
    b = int(s[1])
    return a * 10 + b