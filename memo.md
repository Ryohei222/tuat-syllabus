## 検索機能

- 一度検索した条件はあとで呼び出せるようにしたい
- 条件: (下の項目の組み合わせ or 学籍番号(?)) and 学年
    - 学部 + 学科 + コース
    - 時限
    - 必修か
    - 単位数

`22266511` は (`22`,`2`,`66`,`511`) にパースできる。順に(入学年度, 学部コード, 学科コード, ?)

## データベースの設計

時間割コードで一意にシラバスが特定できる

あとは(入学年度, 学部, 学科, コース)と受講できる科目の対応をどう表すかが問題



シラバス
profile_id 授業の色々な乗法

学科情報
profile_id time_code

## クローラー

### 科目一覧の id 一覧(?)

```py
# Table 6
'''
Detail_lbl_sbj_name
Detail_lbl_sbj_name_e
Detail_lbl_sbj_area_name
Detail_lbl_req_name
Detail_lbl_credits
Detail_lbl_org_name
Detail_lbl_grad_min
Detail_lbl_grad_max
Detail_lbl_lct_term_name
Detail_lbl_type_name
Detail_lbl_lct_cd
Detail_lbl_staff_name
Detail_lbl_staff_name_e
Detail_lbl_section_name
Detail_lbl_room_name
Detail_lbl_e_mail
'''
# Table 4
'''
Detail_lblOutline
Detail_lblStandard
Detail_lblSchedule
Detail_lblRequirements
Detail_lblTextBook
Detail_lblReferenceBook
Detail_lblGrading
Detail_lblSomething
Detail_lblKeywordD
Detail_lblOfficeHours
Detail_lblNote1
Detail_lblNote2
Detail_lblUrl
Detail_lblNumLanguageName
Detail_lblNumSbjName
Detail_lblUpdateDt
'''

```
