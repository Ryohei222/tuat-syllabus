drop table if exists courses;
drop table if exists profiles;

create table courses(
    code text primary key, -- 時間割コード
    'name' text not null, -- 科目の名前
    term text not null, -- 学期
    schedule text not null, -- コマ (ex: 水3)
    grade_min int not null, -- 履修できる学年の下限
    grade_max int not null, -- 履修できる学年の上限
    classcode text not null, -- Google Classroom のクラスコード
    course blob not null -- Course オブジェクトを pickle.dumps() したバイナリ
);

create table profiles(
    id integer primary key autoincrement,
    profile_id text, -- profile に対応する id
    code text not null, -- 時間割コード
    foreign key (code) references courses(code),
    unique(profile_id, code)
);