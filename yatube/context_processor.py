import datetime as dt
""" отсюда добавляем переменные в контекст шаблона"""


def current_time(request):
    now = dt.datetime.now()
    format = '%H:%M:%S'
    return {"current_time": now.strftime(format)}


def year(request):
    """ Текущий год для футера """
    return {"year": dt.datetime.now().year}
