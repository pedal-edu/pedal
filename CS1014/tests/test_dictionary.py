import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.mistake_test_template import *
from CS1014.dictionaries import *


class DictionaryMistakeTest(MistakeTest):
    def setUp(self):
        self._dict_str = ("[{'City': 'Birmingham',  'Precipitation':  0.0, 'Temperature': 46},"
                          "{'City': 'Fairbanks' ,  'Precipitation': 1.37, 'Temperature': 57},"
                          "{'City': 'Miami',       'Precipitation': 1.86, 'Temperature': 80},"
                          "{'City': 'Los Angeles', 'Precipitation':  0.5, 'Temperature': 73},"
                          "{'City': 'Denver',      'Precipitation':  0.0, 'Temperature': 49},"
                          "{'City': 'Chicago',     'Precipitation': 0.23, 'Temperature': 40}]")

    def test_hard_coding(self):
        constants = [99.23, "99.23"]
        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print ("99.23")')
        ret = hard_coding(constants)
        self.assertTrue(ret, "Expected feedback message, got {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'price = "99.23"\n'
                       'print (price)')
        ret = hard_coding(constants)
        self.assertTrue(ret, "Expected feedback message, got {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (book["price"])')
        ret = hard_coding(constants)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_print_dict_key(self):
        # TODO: Check output string
        key_list = ['price', 'number_of_pages', 'discount']
        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'how_much= book["price"]\n'
                       'print("price")')
        ret = print_dict_key(key_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'how_much= book["price"]\n'
                       'print(["price"])')
        ret = print_dict_key(key_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (book["price"])')
        ret = print_dict_key(key_list)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_var_instead_of_key(self):
        # TODO: Check output string
        key_list = ['price', 'number_of_pages', 'discount']

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (price)')
        ret = var_instead_of_key(key_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (book["price"])')
        ret = var_instead_of_key(key_list)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_parens_in_dict(self):
        # TODO: Check output string
        key_list = ['price', 'number_of_pages', 'discount']

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (book("price"))')
        ret = parens_in_dict(key_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print (book["price"])')
        ret = parens_in_dict(key_list)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_list_as_dict(self):
        # TODO: Check output string
        self.to_source("total = 0\n"
                       "weather_reports = {}\n"
                       "for precipitation in weather_reports:\n"
                       "    total = total + weather_reports['Precipitation']\n"
                       "print (total)".format(self._dict_str))
        ret = list_as_dict()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source("total = 0\n"
                       "weather_reports = {}\n"
                       "for precipitation in weather_reports:\n"
                       "    total = total + precipitation['Precipitation']\n"
                       "print (total)\n".format(self._dict_str))
        ret = list_as_dict()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_dict_out_of_loop(self):
        # TODO: Check output string
        keys = ['Precipitation']
        self.to_source('rain = weather_reports["Precipitation"]\n'
                       'total = 0\n'
                       'for report in weather_reports:\n'
                       '    total = total + rain\n'
                       'print(total)\n')
        ret = dict_out_of_loop(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('weather_reports = {}\n'
                       'total = 0\n'
                       'for report in weather_reports:\n'
                       '    total = total + report["Precipitation"]\n'
                       'print(total)\n'.format(self._dict_str))
        ret = dict_out_of_loop(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_wrong_keys(self):
        # TODO: Check output string
        keys = ["Temperature"]
        self.to_source("total = 0\n"
                       "for reports in weather_reports:\n"
                       "    total = total + reports['Temperature']\n"
                       "print(total)\n")
        ret = wrong_keys(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source("total = 0\n"
                       "for reports in weather_reports:\n"
                       "    total = total + reports['Precipitation']\n"
                       "print(total)\n")
        ret = wrong_keys(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_dict_access_not_in_loop(self):
        self.to_source('weatherPrecipitation = weather_reports["Precipitation"]\n'
                       'for report in weather_reports:\n'
                       '    total_precipitation = weatherPrecipitation + total_precipitation\n'
                       'print(total_precipitation)\n')
        ret = dict_access_not_in_loop()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('for weather_report in weather_reports:\n'
                       '    total = total + precipitations[Precipitation]\n'
                       'print(total)\n')
        ret = dict_access_not_in_loop()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

        self.to_source('for weather_report in weather_reports:\n'
                       '    total = total + precipitations["Precipitation"]\n'
                       'print(total)\n')
        ret = dict_access_not_in_loop()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_hard_coded_list(self):
        val_list = [0.0, 1.37, 1.86, 0.5, 0.0, 0.23]
        self.to_source('total_rain = 0\n'
                       'weather_reports = [0.0,1.37,1.86,0.5,0.0,0.23]\n'
                       'for rain in weather_reports:\n'
                       '    total_rain = rain + total_rain\n'
                       'print(total_rain)\n')
        ret = hard_coded_list(val_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_rain = 0\n'
                       'weather_reports = {}\n'
                       'for rain in weather_reports:\n'
                       '    total_rain = rain + total_rain\n'
                       'print(total_rain)\n'.format(self._dict_str))
        ret = hard_coded_list(val_list)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_iter_as_key(self):
        # TODO: Check output string
        keys = ["Precipitation"]
        self.to_source('total_precipitation = 0\n'
                       'for Precipitation in weather_reports:\n'
                       '    total_precipitation = total_precipitation + "Precipitation"\n'
                       'print(total_precipitation)\n')
        ret = iter_as_key(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for Precipitation in weather_reports:\n'
                       '    total_precipitation = total_precipitation + Precipitation["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = iter_as_key(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = iter_as_key(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_dict_acc_as_lis_var(self):
        keys = ["Precipitation"]
        self.to_source('precipitation_total=0\n'
                       'precipitation_list=[]\n'
                       'for precipitation in ["Precipitation"]:\n'
                       '    precipitation_list.append("Precipitation")\n'
                       'for precipitation in precipitation_list:\n'
                       '    precipitation_total=precipitation_total + precipitation\n'
                       'print(precipitation_total)\n')
        ret = dict_acc_as_lis_var(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = dict_acc_as_lis_var(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_append_and_sum(self):
        self.to_source('precipitation_total=0\n'
                       'precipitation_list=[]\n'
                       'for precipitation in weather_reports["Precipitation"]:\n'
                       '    precipitation_list.append("Precipitation")\n'
                       'for precipitation in precipitation_list:\n'
                       '    precipitation_total= precipitation_total + 1\n'
                       'print(precipitation_total)\n')
        ret = append_and_sum()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = append_and_sum()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_iter_prop_dict_acc(self):
        self.to_source('for weather_reports["Precipitation"] in weather_reports:\n'
                       '    total = weather_reports[Precipitation] + total\n'
                       'print(total)\n')
        ret = iter_prop_dict_acc()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = iter_prop_dict_acc()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_list_str_dict(self):
        # TODO: Check output string
        keys = ["Precipitation"]
        self.to_source('total=0\n'
                       'number=0\n'
                       'for precipitation1 in "Precipitation":\n'
                       '    total= total+ precipitation1["Precipitation"]\n'
                       '    number= number + 1\n'
                       'average= total/ total\n'
                       'print(average)\n')
        ret = list_str_dict(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = list_str_dict(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_missing_key(self):
        # TODO: Check output string
        keys = ["Precipitation", "Data"]
        self.to_source('total=0\n'
                       'number=0\n'
                       'for precipitation1 in "Precipitation":\n'
                       '    total= total+ precipitation1["Precipitation"]\n'
                       '    number= number + 1\n'
                       'average= total/ total\n'
                       'print(average)\n')
        ret = missing_key(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = missing_key(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
