import requests
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


# 1) Construction de l'URL où se trouve l'edt
n = 1  # Modifiable, nombre de semaines à prendre à l'avance
dates = [datetime.datetime.now() + datetime.timedelta(days=7*k)
         for k in range(n)]
urls = [
    f"https://sgs-2.mines-paristech.fr/prod/oasis/ensmp/Page/TimeTableView.php?year_in_cursus=1&date={date.year}-{date.month}-{date.day}" for date in dates]

# 2) Extraction des données
# Class contenant un évènement
class evenement:
    def __init__(self, date, annee):
        self.event = Event()
        jour, mois = date.split(' ')[1:]
        dictMois = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "août" :8, "septembre" : 9, "octobre" : 10, "novembre" : 11, "décembre" : 12}
        self.date = datetime.datetime(day = int(jour), month = dictMois[mois], year = annee)
        print(date)
        print(self.date)

    def ICS(self):
        """Méthode qui retourne sous string le texte à mettre dans le fichier ICS"""
        pass

    def Date(self, date):
        self.event.add("date", )

    def HeureDebut(self, heureDebut):
        self.heureDebut = heureDebut

    def HeureFin(self, heureFin):
        self.heureFin = heureFin

    def Nom(self, nom):
        self.nom = nom

    def Groupes(self, groupes):
        self.groupes = groupes

    def Print(self):
        L = f"Le {self.date} de {self.heureDebut} a {self.heureFin}:\n"
        L += self.nom
        L += "\n"
        L += self.groupes
        print(L)


allEvenements = []
for url in urls:
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    jours = soup.findAll("div", {"class": "timetable-day-wrapper"})
    annee = int(soup.find("div", {"class": "timetable-week-title"}).split(' ')[-1]) #Probleme
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
