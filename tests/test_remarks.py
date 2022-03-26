from tfl.domain.remarks import *


def test_wind_pattern():
    s = "AO2 PK WND 09029/0616 SNE18 P0000 FZRANO"
    wp = wind_pattern(s)
    assert wp is not None
    assert "PK WND 09029/0616" == wp.code
    assert "Peak Wind of 29 kts from 090 degrees that occurred at 0616Z" == wp.text


def test_ao2_remark():
    s = "AO2 PK WND 09029/0616 SNE18 P0000 FZRANO"
    a = ao2(s)
    assert a is not None
    assert a.code == "AO2"
    assert a.text == "Automated station with precipitation discriminator"


def test_wind_shift():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 10021"
    ws = wind_shift(s)
    assert ws is not None
    assert ws.code == "WSHFT 0715"
    assert ws.text == "Wind shift at 07:15Z"

def test_six_hour_max():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 11021"
    sh = six_hour_max(s)
    assert sh is not None
    assert sh.code == "11021"
    assert sh.text == "Six Hour Maximum Temp of -2.1C"
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 10221"
    sh = six_hour_max(s)
    assert sh is not None
    assert sh.code == "10221"
    assert sh.text == "Six Hour Maximum Temp of 22.1C"

def test_six_hour_min():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 21021"
    sh = six_hour_min(s)
    assert sh is not None
    assert sh.code == "21021"
    assert sh.text == "Six Hour Minimum Temp of -2.1C"
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221"
    sh = six_hour_min(s)
    assert sh is not None
    assert sh.code == "20221"
    assert sh.text == "Six Hour Minimum Temp of 22.1C"

def test_three_hour_precip():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30217"
    th = three_hour_precip(s)
    assert th is not None
    assert th.code == "30217"
    assert th.text == "Three Hour Precipitation measure with 21.7 inches of precipitation"

    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30000"
    th = three_hour_precip(s)
    assert th is not None
    assert th.code == "30000"
    assert th.text == "Three Hour Precipitation measure with a trace of precipitation"

    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 3////"
    th = three_hour_precip(s)
    assert th is not None
    assert th.code == "3////"
    assert th.text == "Three Hour Precipitation measure with a indeterminable amount of precipitation"


def test_twenty_four_hour_min_max():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30217 401121084"
    tf = twenty_four_hour_min_max(s)
    assert tf.code == '401121084'
    assert tf.text == '24-hour Maximum Temp of 11.2C and Minimum Temp of -8.4C'


def test_snow_depth():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30217 4/023 401121084 RAB07"
    sd = snow_depth(s)
    assert sd.code == '4/023'
    assert sd.text == 'Snow depth of 23 inches'


def test_weather_beginning():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30217 4/023 401121084 RAB0715E22"
    wb = weather_beginning(s)
    assert wb.code == 'RAB0715E22'
    assert wb.text == 'Rain began 07:15Z, ended at 22 min after the hour'

def test_temp_dewpoint():
    s = "AO2 PK WND 09029/0616 SNE18 WSHFT 0715 P0000 FZRANO 20221 30217 4/023 401121084 RAB0715E22 T00640036"
    ht = hourly_temp_dew(s)
    assert ht.code == 'T00640036'
    assert ht.text == 'Hourly Temp 6.4C and Dewpoint 3.6C'