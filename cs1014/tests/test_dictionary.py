import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.mistake_test_template import *
from cs1014.dictionaries import *
from cs1014.input_mistakes import *


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
        ret = list_str_as_list_var(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip\n'
                       'print(total_precipitation)\n')
        ret = list_str_as_list_var(keys)
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

    def test_blank_key(self):
        keys = ["distance", "time"]
        self.to_source('distance_in_kilometers = trip_data["____"]/1000\n'
                       'trip_data = {"distance":123000.0, "time":14000.0}\n'
                       'print(average_speed_in_mph) \n'
                       'average_speed_in_mph = ____ / time_in_hours\n'
                       'time_in_hours = trip_data["____"]/____\n'
                       '____ = distance_in_kilometers / 1.6\n')
        ret = blank_key(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('trip_data = {"distance":123000.0, "time":14000.0}\n'
                       'distance_in_kilometers = trip_data["distance"]/1000\n'
                       'distance_in_miles = distance_in_kilometers / 1.6\n'
                       'time_in_hours = trip_data["time"]/3600\n'
                       'average_speed_in_mph = distance_in_miles / time_in_hours\n'
                       'print(average_speed_in_mph) \n')
        ret = blank_key(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_dict_parens_brack(self):
        # TODO: Check output string
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for rain in weather_reports:\n'
                       '    sum = sum + weather_reports(["Data"]["Precipitation"])\n'
                       'print(sum)\n')
        ret = dict_parens_brack()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                       'print(["price"])')
        ret = dict_parens_brack()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = dict_parens_brack()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_comma_dict_acc(self):
        # TODO: Check output string
        self.to_source("import weather\n"
                       "weather_reports = weather.get_weather()\n"
                       "total = 0\n"
                       "for report in weather_reports:\n"
                       "    total = total + report['Data'],['Precipitation']\n"
                       "print(total)\n")
        ret = comma_dict_acc()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = comma_dict_acc()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_no_dict_in_loop(self):
        # TODO: Check output values
        self.to_source("import weather\n"
                       "weather_reports = weather.get_weather()\n"
                       "total = 0\n"
                       "for precip in weather_reports:\n"
                       "    total = total + precip\n"
                       "print(total)\n")
        ret = no_dict_in_loop()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = no_dict_in_loop()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def func_filter(self):
        keys = ["Precipitation", "Data"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation = 0\n'
                       'for report in weather_reports:\n'
                       '    total_pecipitation = total_precipitation + weather.get_weather("Data")\n'
                       'print(total_precipitation)\n')
        ret = func_filter(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'precipitation_total=0\n'
                       'weather_reports = weather.get_weather("Precipitation")\n'
                       'for report in weather_reports:\n'
                       '    precipitation_total = precipitation_total + 1\n')
        ret = func_filter(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = func_filter()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_str_list(self):
        # TODO: check output values
        keys = ["Precipitation", "Data"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'totalPrecip = 0\n'
                       'for weather in weather_reports:\n'
                       '    totalPrecip = totalPrecip + ["Precipitation"]\n'
                       'print(totalPrecip)\n')
        ret = str_list(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = str_list(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_list_var_dict_acc(self):
        # TODO: Check output values
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'pt = 0\n'
                       'for precipitation in weather_reports["Precipitation"]:\n'
                       '    pt = pt + precipiation\n'
                       'print(pt)\n')
        ret = list_var_dict_acc()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('total_precipitation = 0\n'
                       'for precip in weather_reports:\n'
                       '    total_precipitation = total_precipitation + precip["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = list_var_dict_acc()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_key_comp(self):
        # TODO: Check output values
        keys = ["Data", "Precipitation", "City", "Station"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Data"] == "Precipitation":\n'
                       '        sum = sum + weather_instance["Data"]\n'
                       'print(sum)\n')
        ret = key_comp(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = key_comp(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_col_dict(self):
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'precipitation = 0\n'
                       'for weather in weather_reports:\n'
                       '    preciptation = precipitaion + weather["Data":"Precipitation"]\n'
                       'print(precipitation)\n')
        ret = col_dict()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = col_dict()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_var_key(self):
        # TODO: Check output value
        keys = ["Station", "City", "Precipitation"]
        self.to_source("import weather\n"
                       "weather_reports = weather.get_weather()\n"
                       "sum = 0\n"
                       "for rain in weather_reports:\n"
                       "    if rain[Station][City] == Chicago:\n"
                       "        sum = sum + rain[Data][Precipitation]\n"
                       "print(sum)\n")
        ret = var_key(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = var_key(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_key_order(self):
        keys1 = ["Station", "City"]
        keys2 = ["Data", "Precipitation"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather in weather_reports:\n'
                       '    if weather["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Chicago"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = key_order(keys1)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
        ret = key_order(keys2)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = key_order(keys1)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
        ret = key_order(keys2)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    station = weather_instance["Station"]\n'
                       '    city = station["City"]\n'
                       '    if city == "Chicago":\n'
                       '        data = weather_instance["Data"]\n'
                       '        precipitation = data["Precipitation"]\n'
                       '        sum = sum + precipitation\n'
                       'print(sum)\n')
        ret = key_order(keys1)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
        ret = key_order(keys2)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_key_order_unchained(self):
        keys1 = ["Station", "City"]
        keys2 = ["Data", "Precipitation"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    station = weather_instance["City"]\n'
                       '    city = station["Station"]\n'
                       '    if city == "Chicago":\n'
                       '        data = weather_instance["Precipitation"]\n'
                       '        precipitation = data["Data"]\n'
                       '        sum = sum + precipitation\n'
                       'print(sum)\n')
        ret = key_order_unchained(keys1)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))
        ret = key_order_unchained(keys2)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    station = weather_instance["Station"]\n'
                       '    city = station["City"]\n'
                       '    if city == "Chicago":\n'
                       '        data = weather_instance["Data"]\n'
                       '        precipitation = data["Precipitation"]\n'
                       '        sum = sum + precipitation\n'
                       'print(sum)\n')
        ret = key_order_unchained(keys1)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
        ret = key_order_unchained(keys2)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = key_order_unchained(keys1)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))
        ret = key_order_unchained(keys2)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_filt_key(self):
        # TODO: Check output values
        c_value = "Chicago"
        num_slices = 3
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    total_precipitation = total_precipitation + report["Data"]["Precipitation"]["Chicago"]\n'
                       'print (total_precipitation)\n')
        ret = filt_key(c_value, num_slices)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = filt_key(c_value, num_slices)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == "Chicago":\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = filt_key(c_value, num_slices)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_miss_dict_acc(self):
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if City == "Chicago":\n'
                       '        sum = sum + "Precipitation"\n'
                       'print(sum)\n')
        ret = miss_dict_acc()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = miss_dict_acc()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_compare_key(self):
        c_value = "Chicago"
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather_instance in weather_reports:\n'
                       '    if weather_instance["Station"]["City"] == ["Chicago"]:\n'
                       '        sum = sum + weather_instance["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = compare_key(c_value)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = compare_key(c_value)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_str_equality(self):
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = 0\n'
                       'for weather in weather_reports:\n'
                       '    if("City" == "Chichago"):\n'
                       '        sum = sum + weather["Data"]["Precipitation"]\n'
                       'print(sum)\n')
        ret = str_equality()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation = 0\n'
                       'for report in weather_reports:\n'
                       '    if report["Station"]["City" == "Chicago"]:\n'
                       '        total_precipitation = total_precipitation + report["Data"]["Precipitation"]\n'
                       'print(total_precipitation)\n')
        ret = str_equality()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = str_equality()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_unnecessary_cast(self):
        cast_list = ["float"]
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = int(precip["Chicago"])\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = unnecessary_cast(cast_list)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = unnecessary_cast(cast_list)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_fetch_acc_dict(self):
        keys = ["Data", "Precipitation", "Station", "Chicago"]
        self.to_source('import weather\n'
                       'precipitation = 0\n'
                       'weather_reports = weather.get_weather("Chicago")\n'
                       'where = weather.get_weather["Chicago"]\n'
                       'for weather in weather_reports:\n'
                       '    precipitation = precipitation + weather["Data"]["Precipitation"]\n'
                       'print(precipitation)\n')
        ret = fetch_acc_dict(keys)
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = fetch_acc_dict(keys)
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_app_assign(self):
        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum = sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(sum)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show(sum)\n')
        ret = app_assign()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'total_precipitation_Chicago\n'
                       'for report in weather_reports:\n'
                       '    precip = report["Data"]["Precipitation"]\n'
                       '    chicago_precip = precip["Chicago"]\n'
                       '    total_precipitation = total_precipitation + chicago_recip\n'
                       'print (total_precipitation)\n')
        ret = app_assign()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_show_args(self):
        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(sum)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show(sum)\n')
        ret = show_args()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(sum)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show()\n')
        ret = show_args()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_dict_plot(self):
        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = {}\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(weather_reports)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show()\n'.format(self._dict_str))
        ret = dict_plot()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(sum)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show()\n')
        ret = dict_plot()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_comp_in_dict_acc(self):
        self.to_source('import weather\n'
                       'weather_reports = weather.get_weather()\n'
                       'total_precipitation_Chicago = 0\n'
                       'for report in weather_reports:\n'
                       '    if report["Station"]["City" == "Chicago"]:\n'
                       '        total_precipitation_Chicago = total_precipitation_Chicago + '
                       'report["Data"]["Precipitation"]\n'
                       'print(total_precipitation_Chicago)\n')
        ret = comp_in_dict_acc()
        self.assertTrue(ret, "Didn't give message, returned {} instead".format(ret))

        self.to_source('import weather\n'
                       'import matplotlib.pyplot as plt\n'
                       'weather_reports = weather.get_weather()\n'
                       'sum = []\n'
                       'for rain in weather_reports:\n'
                       '    if rain["Station"]["City"] == "Chicago":\n'
                       '        sum.append(rain["Data"]["Precipitation"])\n'
                       'plt.plot(sum)\n'
                       'plt.xlabel("Years")\n'
                       'plt.ylabel("Precipitation")\n'
                       'plt.title("Chicago Rain")\n'
                       'plt.show()\n')
        ret = dict_plot()
        self.assertFalse(ret, "Expected False, got {} instead".format(ret))

    def test_general_testing(self):
        self.to_source('print("fun")')
        matches = find_matches("_var_")
        var = matches[0]["_var_"]
        self.assertTrue(var.ast_name == "Name", "is: {}".format(var.ast_name))
