# Birthday Reminder Script

## Description
This script is designed to send automatic birthday reminder emails for birthdays occurring on the same day the script is run. Optionally, it can also create an `.ics` calendar file for those birthdays, which is especially useful for email clients like Thunderbird that don't display birthdays from contacts in the calendar.

## Features
- Fetch the VCF file from the URL
- Check for birthdays on the current day
- Send an email reminder for any birthdays that fall on the current day
- Optionally, create or update an `.ics` calendar file with the birthday events (if `ICS_OUTPUT` is set to `True` in the `.env` file). The `.ics` file can be used to add birthday events to your calendar applications. The `.ics` file is updated with each script execution.
- Simple configurable via a single `.env` file
- Multi-language (german/english)

## Installation
### Requirements
This script requires Python 3 and the following dependencies:

```bash
pip install vobject pytz requests icalendar python-decouple
```

## Setup
1. Copy the file `birthday_reminder.py` to a folder of your choice.
2. Copy the HTML template file `template_birthday.html` for email notifications to a folder of your choice.
3. Create a `.env` file in the folder containing `birthday_reminder.py` with __at least__ the following parameters:

   ```ini
   SMTP_HOST = '<Your SMTP server>'
   SMTP_PORT = '<Your SMTP port>'
   SMTP_USERNAME = '<Your SMTP username>'
   SMTP_PASSWORD = '<Your SMTP password>'
   SENDER_EMAIL = '<Your sender email>'
   SENDER_NAME = '<Your name>'
   RECEIVER_EMAIL = '<Recipient email>'
   VCF_URL = '<URL of the VCF file containing the birthday information>'
   TEMPLATE_BIRTHDAY_PATH = '/path/to/template_birthday.html'
   ```
5. Secure the `.env` file by restricting permissions:
   ```bash
   chmod 600 .env
   ```  
6. Make the script executable:
   ```bash
   chmod +x birthday_reminder.py
   ```

## Usage
### Automated Execution with Cronjob (Recommended) 
To run the script automatically at a set interval (e.g., every day at 8 o'clock a.m.), add a Cronjob:

1. Open the Crontab editor:
   ```bash
   crontab -e
   ```
2. Add the following line to execute the script every 30 minutes:
   ```bash
   0 8 * * * /usr/bin/python3 /path/to/birthday_reminder.py
   ```
   Ensure the correct path to Python and the script is used.

### Manual Execution
Run the script with:
```bash
python3 birthday_reminder.py
```

## Customization
### Additional `.env` Parameters
| Parameter               | Description                          | Example Value             | Default Value           |
|-------------------------|--------------------------------------|---------------------------|-------------------------|
| `TIMEZONE`             | Timezone for event processing       | `Europe/Berlin`, `UTC`           | `Europe/Berlin`                   |
| `DATE_FORMAT_BIRTHDAYS`          | Date format for birthdays           | `%d.%m.%Y`, `%m/%d/%Y`    | `%d.%m.%Y`     |
| `LANGUAGE`            | Language setting (`EN` or `DE`)     | `EN`, `DE`                       | `EN`                    |
| `ICS_OUTPUT`   | determine if an `.ics` file should be created           | `True` or `False`       | `False`     |
| `ICS_OUTPUT_PATH`   |  Path where the `.ics` file will be saved (necessary if `ICS_OUTPUT=True`)           | /path/to/birthday.ics       | `Null`     |

## `.ics` File Option

> [!NOTE]
> The `.ics` file is updated with each execution of the script. If any birthdays are found for the current day, the calendar events in the `.ics` file will reflect them. This ensures that the `.ics` file always contains up-to-date information.

The optional `.ics` calendar file can be particularly useful if your email client, like Thunderbird, does not display birthdays from contacts in the calendar. When enabled (`ICS_OUTPUT=True` in the configuration), the script will generate a calendar file that contains yearly events for the birthdays.

This `.ics` file can be imported into most calendar applications, such as Google Calendar, Outlook, or Apple Calendar, to ensure that birthdays are displayed directly in the calendar.

## Webserver for ICS File Access (Optional)

If you want to make the generated `.ics` file available as an internet calendar, it's recommended to serve the `.ics` file via a web server. This is not part of the script itself but can be achieved by hosting the `.ics` file on a web server (e.g., Apache, Nginx, or any cloud storage service).

Once the `.ics` file is publicly accessible, users can subscribe to it using their calendar applications, allowing them to automatically receive updates if the file changes.

## Disclaimer
> [!CAUTION]
> This script is provided "as is," without any warranties or guarantees. The author is not responsible for any data loss, missed reminders, or unintended consequences resulting from the use of this script. Users are responsible for configuring and testing the script to ensure it meets their needs. Use at your own risk.
