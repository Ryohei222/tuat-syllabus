drop table if exists courses;
drop table if exists profiles;

create table courses(
    code text primary key,
    'name' text not null,
    name_e text not null,
    area_name text not null,
    req_name text not null,
    departments text not null,
    term text not null,
    lecture_type text not null,
    staff_name text not null,
    staff_name_e text not null,
    staff_section_name text not null,
    room_name text not null,
    e_mail text not null,
    outline text not null,
    standard text not null,
    content text not null,
    requirements text not null,
    textbook text not null,
    reference_book text not null,
    grading text not null,
    message text not null,
    keyword text not null,
    office_hours text not null,
    note1 text not null,
    note2 text not null,
    url text not null,
    language text not null,
    language_course text not null,
    update_date text not null,
    grade_min int not null,
    grade_max int not null,
    credit int not null,
    classcode text not null
);

create table profiles(
    id int primary key autoincrement,
    profile_id int,
    code text not null,
    foreign key (code) references courses(code)
);