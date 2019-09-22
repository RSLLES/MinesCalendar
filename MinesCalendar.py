# -*- encoding: utf-8 -*-
import requests
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
import pytz
import uuid

# 1) Construction de l'URL où se trouve l'edt
decalage_horaire = 2 #Decalage horaire
n = 1  # Modifiable, nombre de semaines à prendre à l'avance
dates = [datetime.datetime.now() + datetime.timedelta(days=7*(k+1) + 2)
         for k in range(n)]
urls = [
    "https://sgs-2.mines-paristech.fr/prod/oasis/ensmp/Page/TimeTableView.php?year_in_cursus=1&date=" + str(date.year) + "-" + str(date.month) + "-" + str(date.day) for date in dates]

# 2) Extraction des données
# Class contenant un évènement
class evenement:
    def __init__(self, date, annee):
        self.event = Event()
        self.event.add("dtstamp", datetime.datetime.now() - datetime.timedelta(hours=decalage_horaire))
        self.event.add("created", datetime.datetime.now() - datetime.timedelta(hours=decalage_horaire))
        jour, mois = date.split(' ')[1:]
        dictMois = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "août" :8, "septembre" : 9, "octobre" : 10, "novembre" : 11, "décembre" : 12}
        self.day, self.month, self.year = int(jour), dictMois[mois], annee

    def HeureDebut(self, heureDebut):
        self.dtstart = datetime.datetime(day = self.day, month = self.month, year = self.year, hour = int(heureDebut.split("h")[0]), minute = int(heureDebut.split("h")[1]), tzinfo=pytz.utc) - datetime.timedelta(hours=decalage_horaire)
        self.event.add('dtstart', self.dtstart)

    def HeureFin(self, heureFin):
        self.dtend = datetime.datetime(day = self.day, month = self.month, year = self.year, hour = int(heureFin.split("h")[0]), minute = int(heureFin.split("h")[1]), tzinfo=pytz.utc) - datetime.timedelta(hours=decalage_horaire)
        self.event.add('dtend', self.dtend)

    def Nom(self, nom):
        self.event.add("summary", nom)
        self.event.add('uid', str(uuid.uuid4()))
    

    def Groupes(self, groupes):
        self.event.add("description", groupes)


allEvenements = []
for url in urls:
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    jours = soup.findAll("div", {"class": "timetable-day-wrapper"})
    annee = int(soup.find("div", {"class": "timetable-week-title"}).text[-5:])
    for jour in jours:
        date = jour.find("div", {"class": "timetable-day-title"}).text
        allCours = jour.findAll("div", {'class': "timetable-day-body"})
        for cours in allCours:
            e = evenement(date, annee)
            e.HeureDebut(cours.find(
                "div", {"class": "timetable-day-time-start"}).text)
            e.HeureFin(cours.find(
                "div", {"class": "timetable-day-time-end"}).text)
            e.Nom(cours.find(
                "div", {"class": "timetable-session-course-title"}).text)

            groupes = cours.findAll("div", {"class": "timetable-session"})
            comment = ""
            for groupe in groupes:
                comment += groupe.find("div",
                                       {"class": "timetable-session-subclass"}).text
                comment += ": "
                comment += groupe.find("div",
                                       {"class": "timetable-session-room"}).text
                comment += "\n"

            e.Groupes(comment)
            allEvenements.append(e)

#3) On va a présent créer le fichier et ajouter les évnénements
cal = Calendar()

cal.add('version', '2.0')
cal.add('prodid', '-//Calendrier Mines//mxm.dk//')
for e in allEvenements:
    cal.add_component(e.event)
now = datetime.datetime.now() + datetime.timedelta(days=8)
titre = "Semaine_du_"+ str(now.day) + "_" + str(now.month) + "_" + str(now.year)
f = open(titre + ".ics", 'wb')
f.write(cal.to_ical())
f.close()


#4) On envoie par wetransfer le mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

fromaddr = "MinesCalendar@gmx.fr"
toaddr = "romain.seailles@mines-paristech.fr"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "[Emploi du temps] Semaine du  " + str(now.day) + "/" + str(now.month) + "/" + str(now.year)

body = "Ca marche toujours et oui"
msg.attach(MIMEText(body, 'plain'))

filename = titre + ".ics"
# Open PDF file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    "attachment; filename= " + str(filename),
)

# Add attachment to message and convert message to string
msg.attach(part)

import smtplib
server = smtplib.SMTP('mail.gmx.com', 25)
server.ehlo()
server.starttls()
server.ehlo()
server.login("minescalendar@gmx.fr", "MinesDeParis")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
