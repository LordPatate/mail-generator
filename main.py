from datetime import date, time
from email.generator import BytesGenerator
from email.message import EmailMessage
from email.policy import SMTP
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


def export_to_file(msg: EmailMessage):
    with open("mail.eml", mode="wb") as output_fd:
        (
            BytesGenerator(output_fd)
            .flatten(msg)
        )


def main():
    student_email_address = "mail@example.com"
    details = AppointmentDetails(
        date=date(2024, 10, 8),
        time=time(18),
    )

    msg = EmailMessage(policy=SMTP)
    msg["from"] = "mail@example.com"
    msg["to"] = student_email_address
    msg["subject"] = "<Mail Subject>"
    body = generate_body_from_template(details)
    msg.set_content(body)

    export_to_file(msg)


if __name__ == "__main__":
    main()
