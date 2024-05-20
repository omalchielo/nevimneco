import requests
from bs4 import BeautifulSoup
import time
from email.message import EmailMessage
import ssl
import smtplib

# Přihlašovací údaje
email = "omalchielo@gmail.com"
password = "xxx"

# URL
login_url = "https://kratochvilova.moje-autoskola.cz/"
rides_url = "https://kratochvilova.moje-autoskola.cz/zak_kalendar.php"

# Vytvoření session
session = requests.Session()

def login(session):
    # Načtení přihlašovací stránky pro získání potřebných cookies
    session.get(login_url)

    # Data pro přihlášení
    login_data = {
        'log_email': email,
        'log_heslo': password,
        'akce': 'login'
    }

    # Přihlášení
    response = session.post(login_url, data=login_data)

    # Zkontrolování, zda bylo přihlášení úspěšné
    if "nepřihlášen" in response.text:
        print("Přihlášení se nezdařilo.")
        return False
    else:
        print("Přihlášení bylo úspěšné.")
        return True

def check_rides(session):
    # Získání stránky s jízdami
    rides_page = session.get(rides_url)
    soup = BeautifulSoup(rides_page.content, 'html.parser')

    # Kontrola, zda jsou k dispozici nějaké jízdy
    no_rides_message = "Nebyl nalezen žádný dostupný termín pro přímé naplánování jízdy."
    if no_rides_message in rides_page.text:
        print("Nebyl nalezen žádný dostupný termín pro přímé naplánování jízdy.")
        return False
    else:
        # Najít a vytisknout informace o jízdách
        rides_table = soup.find('div', {'class': 'tab-content'})
        if rides_table:
            table = rides_table.find('table', {'class': 'table'})
            if table:
                email_sender = "botrozvrh@gmail.com"
                email_password = "ogkybntogxdmekzl"
                email_receiver = ["omalchielo@gmail.com"]
                subject = "NOVÝ JÍZDY"  # Přidávání předmětu e-mailu
                for receiver in email_receiver:
                    em = EmailMessage()
                    em.set_content("BYLY PŘIDÁNY NOVÉ JÍZDY")
                    em["Subject"] = subject  # Nastavení předmětu e-mailu
                    em["From"] = email_sender
                    em["To"] = receiver

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                        smtp.login(email_sender, email_password)
                        smtp.send_message(em)
                for row in table.find_all('tr'):
                    columns = row.find_all('td')
                    if columns:
                        ride_info = [column.text.strip() for column in columns]
                        print(" | ".join(ride_info))
                return True
            else:
                print("Nepodařilo se najít tabulku s jízdami.")
                return False
        else:
            print("Nepodařilo se najít informace o jízdách.")
            return False

def send_status_email():
    email_sender = "botrozvrh@gmail.com"
    email_password = "ogkybntogxdmekzl"
    email_receiver = ["omalchielo@gmail.com"]
    subject = "Kód běží"
    for receiver in email_receiver:
        em = EmailMessage()
        em.set_content("Kód běží")
        em["Subject"] = subject
        em["From"] = email_sender
        em["To"] = receiver

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(em)

# Přihlášení na začátku
if not login(session):
    print("Nepodařilo se přihlásit. Skript se ukončuje.")
    exit()

# Hlavní smyčka pro pravidelnou kontrolu
login_interval = 3600  # přihlásit každou hodinu
status_email_interval = 3600  # poslat e-mail o stavu každou hodinu
last_login_time = time.time()
last_status_email_time = time.time()

while True:
    try:
        if time.time() - last_login_time > login_interval:
            if login(session):
                last_login_time = time.time()
            else:
                print("Chyba při přihlášení, zkusím to znovu za 5 minut.")
                time.sleep(300)
                continue

        if time.time() - last_status_email_time > status_email_interval:
            send_status_email()
            last_status_email_time = time.time()

        if check_rides(session):
            print("Nové jízdy nalezeny!")

        else:
            print("Žádné nové jízdy nebyly nalezeny.")
    except Exception as e:
        print(f"Chyba při kontrole jízd: {e}")

    time.sleep(120)
