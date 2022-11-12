import datetime
import jdatetime


# convert current date time to persian date time
def jalali_datetime(date: datetime):
    """
    converts datetime to persian date time
    :param date: date.datetime
    :return: jalali standard datetime
    """
    date = datetime.datetime.strptime((str(date)).split(".")[0], '%Y-%m-%d %H:%M:%S')
    return jdatetime.datetime.fromtimestamp(int(date.strftime('%s'))).strftime('%Y-%m-%d %H:%M:%S')
