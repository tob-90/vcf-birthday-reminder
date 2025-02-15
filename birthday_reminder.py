#!/usr/bin/python3
import vobject
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import pytz
import requests
from decouple import config
# import random
# import string

# Konfigurations-ENV abrufen
smtp_server = config('SMTP_HOST')
smtp_port = config('SMTP_PORT', cast=int)
smtp_username = config('SMTP_USERNAME')
smtp_password = config('SMTP_PASSWORD')
sender_email = config('SENDER_EMAIL')
sender_name = config('SENDER_NAME')
to_email = config('RECEIVER_EMAIL')
vcf_url = config('VCF_URL')
template_file_path = config('TEMPLATE_BIRTHDAY_PATH', default='template_birthday.html')
TIMEZONE = pytz.timezone(config('TIMEZONE', default='Europe/Berlin'))
DATE_FORMAT = config("DATE_FORMAT_BIRTHDAYS", default='%d.%m.%Y') # US-Format: '%m/%d/%Y'
ics_output = config('ICS_OUTPUT', default='False').lower() == 'true'
ics_path = config('ICS_OUTPUT_PATH')
language = config('LANGUAGE', default='EN')

# Wörterbuch für die Texte
texts = {
    'DE': {
        'subject': "Geburtstag:",
        'header': "Geburtstags-Erinnerung",
        'body1': "Heute ist der Geburtstag von",
        'body2': ".",
        'footer': "Diese E-Mail wurde automatisch generiert. Bitte nicht antworten."
    },
    'EN': {
        'subject': "Birthday:",
        'header': "Birthday Reminder",
        'body1': "Today is",
        'body2': "'s birthday.",
        'footer': "This email was automatically generated. Please do not reply."
    }
}

# Wähle die Texte basierend auf der Sprache aus
selected_texts = texts.get(language, texts['EN'])  # Fallback auf Englisch, wenn die Sprache nicht gefunden wird

def fetch_vcf(url):
    response = requests.get(url)
    response.raise_for_status()  # Wirft eine Ausnahme bei einem Fehler
    return response.text

def parse_vcf(vcf_data):
    return vobject.readComponents(vcf_data)

def extract_birthdays(components):
    birthdays = []
    for component in components:
        try:
            name = component.fn.value
            bday_str = component.bday.value
            # Versuche, das Datum im ersten Format zu parsen
            try:
                bday = datetime.strptime(bday_str, "%Y-%m-%d").date()
            except ValueError:
                # Versuche, das Datum im zweiten Format zu parsen
                bday = datetime.strptime(bday_str, "%Y%m%d").date()
            birthdays.append((name, bday))
        except AttributeError:
            continue
    return birthdays

# def generate_random_string(length=25):
    # """Generiert eine zufällige Zeichenkette der angegebenen Länge."""
    # letters_and_digits = string.ascii_letters + string.digits
    # return ''.join(random.choice(letters_and_digits) for i in range(length))

def create_ics(birthdays, output_path):
    calendar = Calendar()
    for name, bday in birthdays:
        event = Event()
        event.add('summary', f"🎂 {name} (*{bday.strftime('%d.%m.%Y')})")
        event.add('dtstart', bday)
        event.add('rrule', {'freq': 'yearly'})
        event.add('dtend', bday + timedelta(days=1))  # All-day event
        
        # UID basierend auf Name und Geburtsdatum
        event.add('uid', f"{name.replace(' ', '_')}_{bday.strftime('%Y%m%d')}")  # Eindeutige UID
        
        # DTSTAMP hinzufügen
        event.add('dtstamp', datetime.now())  # Aktuelles Datum und Uhrzeit
        
        event.add('description', f"{selected_texts['body1']} {name}{selected_texts['body2']}")  # Beschreibung
        event.add('status', 'CONFIRMED')  # Status des Ereignisses

        # VALARM hinzufügen
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        #alarm.add('description', f"Erinnerung: {name} hat heute Geburtstag!")
        
        # Trigger auf 9 Stunden nach dem Ereignis setzen
        alarm.add('trigger', timedelta(hours=9))  # 9 Stunden nach dem Ereignis
        event.add_component(alarm)

        calendar.add_component(event)
    
    with open(output_path, 'wb') as f:
        f.write(calendar.to_ical())

# Funktion zum Senden einer E-Mail
def send_email(name, sender_name, sender_email, subject, body, to_email):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)

    msg.attach(MIMEText(body, 'html'))

    try:
        if smtp_port == 587:
            # Verwende STARTTLS für Port 587
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls() 
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, to_email, msg.as_string())
        else:
            # Verwende SSL für alle anderen Ports
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, to_email, msg.as_string())
        print("E-Mail erfolgreich verschickt.")
    except Exception as e:
        print(f"Fehler beim Versenden der E-Mail: {e}")

def load_template(template_file_path, name):
    with open(template_file_path, 'r', encoding='utf-8') as file:
        template = file.read()
    
    body = template.replace("{{lang}}", "de" if language == "DE" else "en")\
                   .replace('{{name}}', name)\
                   .replace("{{header}}", selected_texts['header'])\
                   .replace('{{body1}}', selected_texts['body1'])\
                   .replace('{{body2}}', selected_texts['body2'])\
                   .replace("{{footer}}", selected_texts['footer'])
    
    return body

def main():
    vcf_data = fetch_vcf(vcf_url)  # VCF-Daten von der URL abrufen
    components = parse_vcf(vcf_data)
    birthdays = extract_birthdays(components)

    today = datetime.now(TIMEZONE).date()  # Aktuelles Datum in der richtigen Zeitzone
    for name, bday in birthdays:
        if bday.month == today.month and bday.day == today.day:
            subject = f"{selected_texts['subject']} {name} (*{bday.strftime(DATE_FORMAT)})"
            body = load_template(template_file_path, name)
            send_email(name, sender_name, sender_email, subject, body, to_email)

    if ics_output:
        create_ics(birthdays, ics_path)
        print(f"ICS-Datei erstellt unter {ics_path}")

if __name__ == "__main__":
    main()
