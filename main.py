import smtplib
import ssl
from argparse import ArgumentParser
import csv
from datetime import date, time
from email.generator import BytesGenerator
from email.message import EmailMessage
from email.policy import SMTP
import functools
from pathlib import Path
from textwrap import dedent
import tomllib
from typing import Callable, NamedTuple

from time_formatting import (
    english_date_format, english_time_format,
    french_date_format, french_time_format
)

OUTPUT_FOLDER = "generated_mails"
TEMPLATE_FILENAME = "body.template"
CONFIG_FILE = "config.toml"


class Config(NamedTuple):
    class SMTPConfig(NamedTuple):
        host: str
        port: int
        user: str
        password: str

    sender_email_address: str
    student_address_template: str
    email_subject: str
    smtp: SMTPConfig


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


def export_mail_to_file(msg: EmailMessage):
    subject_summary = msg["subject"][:32]
    dest, _ = msg["to"].split("@")
    filename = f"{subject_summary} -- to {dest}.eml"
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
        rows = csv.DictReader(f, delimiter=";")
        return [
            Student(
                row["login"],
                date.fromisoformat(row["date"]),
                time.fromisoformat(row["time"]),
                row["room"],
                row["mail_sent"] == "TRUE",
            )
            for row in rows
        ]


def send_msg_using_ssl(msg: EmailMessage):
    context = ssl.create_default_context()
    smtp = conf().smtp
    with smtplib.SMTP(smtp.host, smtp.port) as server:
        server.starttls(context=context)
        server.login(
            smtp.user,
            smtp.password,
        )
        server.send_message(msg)


def main(input_csv: str, action_on_mail: Callable[[EmailMessage], None]):
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    students = parse_csv(input_csv)

    for student in filter(lambda s: not s.mail_sent, students):
        student_email_address = conf().student_address_template.format(student.login)
        msg = create_mail_for_student(
            student_email_address,
            AppointmentDetails(
                student.meeting_date,
                student.meeting_time,
                student.room,
            )
        )

        action_on_mail(msg)


@functools.cache
def conf():
    with Path(CONFIG_FILE).open(mode="rb") as fp:
        conf_dict = tomllib.load(fp)
        smtp_dict = conf_dict.pop("smtp")
        return Config(**conf_dict, smtp=Config.SMTPConfig(**smtp_dict))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument(
        "--mode",
        choices=("CREATE", "SEND"),
        help=dedent(
            """\
            The desired behavior for each mail.
            Wether to CREATE a file or directly SEND the mail using SMTP."""
        ),
        default="CREATE",
    )
    args = parser.parse_args()
    action_map = {
        "CREATE": export_mail_to_file,
        "SEND": send_msg_using_ssl,
    }
    main(args.input_csv, action_map[args.mode])
