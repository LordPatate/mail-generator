from datetime import date, time
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from time_formatting import (
    english_date_format, english_time_format,
    french_date_format, french_time_format
)


class AppointmentDetails(NamedTuple):
    date: date
    time: time
    room: str = "A203"


def generate_body_from_template(details: AppointmentDetails) -> str:
    body_template = Path("body.template").read_text(encoding="utf-8")
    return body_template.format(
        date_fr=french_date_format(details.date),
        date_en=english_date_format(details.date),
        time_fr=french_time_format(details.time),
        time_en=english_time_format(details.time),
        room=details.room,
    )

