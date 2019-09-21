import requests
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
import pytz
import uuid

# 1) Construction de l'URL où se trouve l'edt
decalage_horaire = 2 #Decalage horaire
n = 2  # Modifiable, nombre de semaines à prendre à l'avance
dates = [datetime.datetime.now() + datetime.timedelta(days=7*k + 2)
         for k in range(n)]
urls = [
    f"https://sgs-2.mines-paristech.fr/prod/oasis/ensmp/Page/TimeTableView.php?year_in_cursus=1&date={date.year}-{date.month}-{date.day}" for date in dates]

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
f = open(str(datetime.datetime.now().date()).replace("-", "_") + '.ics', 'wb')
f.write(cal.to_ical())
f.close()
