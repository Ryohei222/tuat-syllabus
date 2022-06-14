from crawler import Crawler


class TestCrawler:
    def test_single_download(self):
        # Arrange
        ddl_fac = '02'  # 開講学部として工学部(02)を選択
        num = 1  # 検索結果の一番上の科目を選択
        # Act
        cr = Crawler()
        course = cr.get_one_course_detail(ddl_fac, num)
        # Assert
        print(course)
        assert course.name == 'アカデミックライティング入門'
        assert course.staff_name == '野間 竜男'
        assert course.code == '020001'
        assert course.keyword == '文章作法、批判的思考、論理的文章'
