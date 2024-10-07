from argparse import ArgumentParser
import csv
from datetime import date, time
from email.generator import BytesGenerator
from email.message import EmailMessage
from email.policy import SMTP
import functools
from pathlib import Path
import tomllib
from typing import NamedTuple

from time_formatting import (
    english_date_format, english_time_format,
    french_date_format, french_time_format
)

OUTPUT_FOLDER = "generated_mails"
TEMPLATE_FILENAME = "body.template"
CONFIG_FILE = "config.toml"


class Config(NamedTuple):
    sender_email_address: str
    student_mail_template: str
    email_subject: str


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
    body_template = Path(TEMPLATE_FILENAME).read_text(encoding="utf-8")
    return body_template.format(
        date_fr=french_date_format(details.date),
        date_en=english_date_format(details.date),
        time_fr=french_time_format(details.time),
        time_en=english_time_format(details.time),
        room=details.room,
    )


def export_mail_to_file(msg: EmailMessage, filename: str):
    with Path(OUTPUT_FOLDER, filename).open(mode="wb") as output_fd:
        (
            BytesGenerator(output_fd)
            .flatten(msg)
        )


def create_mail_for_student(student_email_address: str, details: AppointmentDetails):
    msg = EmailMessage(policy=SMTP)

    msg["from"] = conf().sender_email_address
    msg["to"] = student_email_address
    msg["subject"] = conf().email_subject

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
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    students = parse_csv(input_csv)

    for student in filter(lambda s: not s.mail_sent, students):
        msg = create_mail_for_student(
            conf().student_mail_template.format(student.login),
            AppointmentDetails(
                student.meeting_date,
                student.meeting_time,
                student.room,
            )
        )

        export_mail_to_file(msg, f"mail_to_{student.login}.eml")


@functools.cache
def conf():
    with Path(CONFIG_FILE).open(mode="rb") as fp:
        conf_dict = tomllib.load(fp)
        return Config(**conf_dict)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_csv")
    args = parser.parse_args()
    main(args.input_csv)
