# -*- coding: utf-8 -*-

# コマンド
# python -m unittest test
import os, sys, unittest
import utils

class DateTypeTest(unittest.TestCase):

    def test_sun(self):
        # 元旦
        self.assertEqual(utils.get_day_type(2015, 1, 1), "sun")
        self.assertEqual(utils.get_day_type(2016, 1, 1), "sun")
        self.assertEqual(utils.get_day_type(2017, 1, 1), "sun")

        # 成人の日
        self.assertEqual(utils.get_day_type(2015, 1, 12), "sun")
        self.assertEqual(utils.get_day_type(2016, 1, 11), "sun")
        self.assertEqual(utils.get_day_type(2017, 1, 9), "sun")

        # 建国記念の日
        self.assertEqual(utils.get_day_type(2015, 2, 11), "sun")
        self.assertEqual(utils.get_day_type(2016, 2, 11), "sun")
        self.assertEqual(utils.get_day_type(2017, 2, 11), "sun")

        # 春分の日
        self.assertEqual(utils.get_day_type(2015, 3, 21), "sun")
        self.assertEqual(utils.get_day_type(2016, 3, 20), "sun")
        self.assertEqual(utils.get_day_type(2017, 3, 20), "sun")

        # 昭和の日
        self.assertEqual(utils.get_day_type(2015, 4, 29), "sun")
        self.assertEqual(utils.get_day_type(2016, 4, 29), "sun")
        self.assertEqual(utils.get_day_type(2017, 4, 29), "sun")
        
        # 昭和の日
        self.assertEqual(utils.get_day_type(2015, 4, 29), "sun")
        self.assertEqual(utils.get_day_type(2016, 4, 29), "sun")
        self.assertEqual(utils.get_day_type(2017, 4, 29), "sun")

        # 憲法記念日
        self.assertEqual(utils.get_day_type(2015, 5, 3), "sun")
        self.assertEqual(utils.get_day_type(2016, 5, 3), "sun")
        self.assertEqual(utils.get_day_type(2017, 5, 3), "sun")

        # みどりの日
        self.assertEqual(utils.get_day_type(2015, 5, 4), "sun")
        self.assertEqual(utils.get_day_type(2016, 5, 4), "sun")
        self.assertEqual(utils.get_day_type(2017, 5, 4), "sun")

        # こどもの日
        self.assertEqual(utils.get_day_type(2015, 5, 5), "sun")
        self.assertEqual(utils.get_day_type(2016, 5, 5), "sun")
        self.assertEqual(utils.get_day_type(2017, 5, 5), "sun")

        # 振替休日
        self.assertEqual(utils.get_day_type(2015, 5, 6), "sun")

        # 海の日
        self.assertEqual(utils.get_day_type(2015, 7, 20), "sun")
        self.assertEqual(utils.get_day_type(2016, 7, 18), "sun")
        self.assertEqual(utils.get_day_type(2017, 7, 17), "sun")

        # 山の日 2016年より
        self.assertEqual(utils.get_day_type(2016, 8, 11), "sun")
        self.assertEqual(utils.get_day_type(2017, 8, 11), "sun")

        # 敬老の日
        self.assertEqual(utils.get_day_type(2015, 9, 21), "sun")
        self.assertEqual(utils.get_day_type(2016, 9, 18), "sun")
        self.assertEqual(utils.get_day_type(2017, 9, 18), "sun")

        # 国民の休日
        self.assertEqual(utils.get_day_type(2015, 9, 22), "sun")

        # 秋分の日
        self.assertEqual(utils.get_day_type(2015, 9, 23), "sun")
        self.assertEqual(utils.get_day_type(2016, 9, 22), "sun")
        self.assertEqual(utils.get_day_type(2017, 9, 23), "sun")

        # 体育の日
        self.assertEqual(utils.get_day_type(2015, 10, 12), "sun")
        self.assertEqual(utils.get_day_type(2016, 10, 10), "sun")
        self.assertEqual(utils.get_day_type(2017, 10, 9), "sun")

        # 文化の日
        self.assertEqual(utils.get_day_type(2015, 11, 3), "sun")
        self.assertEqual(utils.get_day_type(2016, 11, 3), "sun")
        self.assertEqual(utils.get_day_type(2017, 11, 3), "sun")

        # 勤労感謝の日
        self.assertEqual(utils.get_day_type(2015, 11, 23), "sun")
        self.assertEqual(utils.get_day_type(2016, 11, 23), "sun")
        self.assertEqual(utils.get_day_type(2017, 11, 23), "sun")

        # 天皇誕生日
        self.assertEqual(utils.get_day_type(2015, 12, 23), "sun")
        self.assertEqual(utils.get_day_type(2016, 12, 23), "sun")
        self.assertEqual(utils.get_day_type(2017, 12, 23), "sun")

    def test_sat(self):
        # てきとうな日
        self.assertEqual(utils.get_day_type(2015, 1, 10), "sat")
        self.assertEqual(utils.get_day_type(2016, 4, 9), "sat")
        self.assertEqual(utils.get_day_type(2016, 4, 16), "sat")

    def test_week(self):
        # てきとうな日
        self.assertEqual(utils.get_day_type(2015, 1, 15), "week")
        self.assertEqual(utils.get_day_type(2016, 4, 4), "week")
        self.assertEqual(utils.get_day_type(2016, 4, 5), "week")

if __name__ == '__main__':
    unittest.main()