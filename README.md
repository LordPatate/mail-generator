# Mail generator

Generates e-mails from a template and a CSV file.
Primarily written to invite students on appointments for individual follow-up meetings.

## Usage

```console
python main.py <path to CSV file>
```

See detailed usage with `--help`.

## Expected CSV file format

The CSV file should have the following columns:

| Header name  | Description                                                                                               | Example            |
| ------------ | --------------------------------------------------------------------------------------------------------- | ------------------ |
| login        | Used to build the email address                                                                           | firstname.lastname |
| date | The meeting date (iso format)                                                                             | 2024-10-01         |
| time | The meeting time (hh:mm)                                                                                  | 18:00              |
| room         | The meeting room                                                                                          | A203               |
| mail_sent    | Whether mail was already sent or not. The script will only generate or send mails if this column is FALSE | FALSE              |

The file should have a "headers" row with these exact names for the corresponding columns.

It can have any number of additional columns, they won't be processed.

Here is an example with an additional column "priority":
```csv
login;priority;date;time;room;mail_sent;;
firstname_1.lastname_1;1;2024-10-01;18:00;A203;TRUE;;
firstname_2.lastname_2;2;2024-10-01;18:20;A203;FALSE;;
firstname_3.lastname_3;3;2024-10-01;18:40;A203;FALSE;;
```

Using this CSV file, the script would generate a mail for students `firstname_2.lastname_2` and `firstname_3.lastname_3`; and ignore `firstname_1.lastname_1` since the mail was already sent.