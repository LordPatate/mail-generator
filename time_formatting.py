from enum import Enum
from datetime import date, time


class FrenchDaysOfWeek(str, Enum):
    MON = "Lundi"
    TUE = "Mardi"
    WED = "Mercredi"
    THU = "Jeudi"
    FRI = "Vendredi"
    SAT = "Samedi"
    SUN = "Dimanche"


class EnglishDaysOfWeek(str, Enum):
    MON = "Monday"
    TUE = "Tuesday"
    WED = "Wednesday"
    THU = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"
    SUN = "Sunday"


class FrenchMonths(str, Enum):
    JAN = "Janvier"
    FEB = "Février"
    MAR = "Mars"
    APR = "Avril"
    MAY = "Mai"
    JUN = "Juin"
    JUL = "Juillet"
    AUG = "Août"
    SEP = "Septembre"
    OCT = "Octobre"
    NOV = "Novembre"
    DEC = "Décembre"


class EnglishMonths(str, Enum):
    JAN = "January"
    FEB = "February"
    MAR = "March"
    APR = "April"
    MAY = "May"
    JUN = "June"
    JUL = "July"
    AUG = "August"
    SEP = "September"
    OCT = "October"
    NOV = "November"
    DEC = "December"


def english_date_format(some_date: date) -> str:
    day_of_week = list(EnglishDaysOfWeek)[some_date.weekday()].value
    month = list(EnglishMonths)[some_date.month - 1].value
    day_suffix = {
        1: "st",
        2: "nd",
        3: "rd",
    }.get(some_date.day, "th")
    return f"{day_of_week}, {month} {some_date.day}{day_suffix}"


def french_date_format(some_date: date) -> str:
    day_of_week = list(FrenchDaysOfWeek)[some_date.weekday()].value
    month = list(FrenchMonths)[some_date.month - 1].value
    day_suffix = {
        1: "er",
    }.get(some_date.day, "")
    return f"{day_of_week} {some_date.day}{day_suffix} {month}"


def french_time_format(some_time: time) -> str:
    return some_time.strftime("%Hh%M")


def english_time_format(some_time: time) -> str:
    suffix = (
        'p.m.' if some_time > time(13)
        else "a.m."
    )
    return some_time.strftime(f"%I:%M {suffix}")
