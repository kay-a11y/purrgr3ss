from purrgress.utils import date as du

def test_minutes_between_rollover():
    assert du.minutes_between("23:55", "00:10") == 15
    assert du.minutes_between("12:00", "12:30") == 30
