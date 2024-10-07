from argparse import ArgumentParser
import csv
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

FOLDER = "generated_mails"
SENDER_EMAIL_ADDRESS = "mail@example.com"
EMAIL_SUBJECT = "<Mail Subject>"


class AppointmentDetails(NamedTuple):
    date: date
    time: time
    room: str


class Student(NamedTuple):
    login: str
    meeting_date: date
    meeting_time: time
    room: str
    mail_sent: bool


def generate_body_from_template(details: AppointmentDetails) -> str:
    body_template = Path("body.template").read_text(encoding="utf-8")
    return body_template.format(
        date_fr=french_date_format(details.date),
        date_en=english_date_format(details.date),
        time_fr=french_time_format(details.time),
        time_en=english_time_format(details.time),
        room=details.room,
    )


def export_mail_to_file(msg: EmailMessage, filename: str):
    with Path(FOLDER, filename).open(mode="wb") as output_fd:
        (
            BytesGenerator(output_fd)
            .flatten(msg)
        )


def create_mail_for_student(student_email_address: str, details: AppointmentDetails):
    msg = EmailMessage(policy=SMTP)

    msg["from"] = SENDER_EMAIL_ADDRESS
    msg["to"] = student_email_address
    msg["subject"] = EMAIL_SUBJECT

    body = generate_body_from_template(details)
    msg.set_content(body)

    return msg


def parse_csv(file: str) -> list[Student]:
    with open(file, newline="") as f:
        rows = csv.reader(f, delimiter=";")
        _ = next(rows)  # skip first line (headers)
        return [
            Student(
                login,
                date.fromisoformat(meeting_date),
                time.fromisoformat(meeting_time),
                room,
                mail_sent == "TRUE",
            )
            for (login, meeting_date, meeting_time, room, mail_sent) in (
                row[:len(Student._fields)] for row in rows
            )
        ]


def main(input_csv: str):
    Path(FOLDER).mkdir(exist_ok=True)

    students = parse_csv(input_csv)

    for student in filter(lambda s: not s.mail_sent, students):
        msg = create_mail_for_student(
            f"{student.login}@epita.fr",
            AppointmentDetails(
                student.meeting_date,
                student.meeting_time,
                student.room,
            )
        )

        export_mail_to_file(msg, f"mail_to_{student.login}.eml")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_csv")
    namespace = parser.parse_args()
    main(namespace.input_csv)
