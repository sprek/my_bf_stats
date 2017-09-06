import datetime as dt

def get_date_from_date_int(date_int):
    """ --------------------------------------------------
    Converts an integer in the format: YYYYmmDDHHMMSS into
    a datetime object
    """
    date_str=str(date_int)
    assert len(date_str) == len("YYYYmmDDHHMMSS")
    return dt.datetime(year=int(date_str[0:4]), month=int(date_str[4:6]), day=int(date_str[6:8]),
                       hour=int(date_str[8:10]), minute=int(date_str[10:12]), second=int(date_str[12:14]))

def convert_time_to_int(time_str):
    """ --------------------------------------------------
    Converts a string in format H:MM:SS to an integer in 
    the format: HMMSS
    """
    return int(str(time_str).replace(':',''))

def get_current_time():
    """ --------------------------------------------------
    Returns an integer in the format YYYYMMDDHHmmSS representing the current time
    """
    now = dt.datetime.now()
    return ''.join(map(lambda x: '{0:02d}'.format(x),[now.year, now.month, now.day, now.hour, now.minute, now.second]))

def datetime_to_int(dt_obj):
    """ --------------------------------------------------
    returns an integer in the format YYYYMMDDHHmmSS
    """
    return int(''.join(map(lambda x: '{0:02d}'.format(x),[dt_obj.year, dt_obj.month, dt_obj.day, 0, 0, 0])))

def get_last_sunday():
    """ --------------------------------------------------
    returns an integer of the format YYYYMMDDHHmmSS representing Sunday at 0:00
    """
    today=dt.date.today()
    # <sunday>.weekday() == 0
    last_sun = today - dt.timedelta(days=((today.weekday()+1) % 7))
    last_sun=datetime_to_int(last_sun)
    return last_sun

def get_minutes_in_time(time_int):
    """ --------------------------------------------------
    Converts a time integer in the format HMMSS to a float
    equal to the number of minutes
    """
    total=0
    time_str=str(time_int)
    if len(time_str) >= 1:
        total += int(time_str[-2:]) / 60.0
    if len(time_str) >= 3:
        total += int(time_str[-4:-2])
    if len(time_str) >= 5:
        total += int(time_str[0:-4]) * 60
    return total

def get_time_str_from_int(time_int):
    """ --------------------------------------------------
    Converts a time integer in the format HMMSS to a string
    in the format: H:MM:SS
    """
    new_str=''
    time_str=str(time_int)
    if len(time_str) >= 1:
        new_str = time_str[-2:]
    if len(time_str) >= 3:
        new_str = time_str[-4:-2] + ':' + new_str
    if len(time_str) >= 5:
        new_str = time_str[0:-4] + ':' + new_str
    return new_str

def get_timedelta_from_time_str(time_str):
    """ --------------------------------------------------
    Converts a time string in the format H:MM:SS to a 
    timedelta object
    """
    td=dt.timedelta(minutes=get_minutes_in_time(convert_time_to_int(time_str)))
    return td

def get_time_str_from_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return_time=""
    if seconds >= 0:
        return_time='{0:02d}'.format(seconds)
    if minutes > 0 or hours > 0:
        return_time='{0:02d}'.format(minutes) + ":" + return_time
    if hours > 0:
        return_time=str(hours) + ":" + return_time
    return return_time

def subtract_times(time_int_a, time_int_b):
    diff_time=get_timedelta_from_time_str(get_time_str_from_int(time_int_a)) - \
        get_timedelta_from_time_str(get_time_str_from_int(time_int_b))
    return get_time_str_from_timedelta (diff_time)
