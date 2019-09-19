import requests
import datetime
from bs4 import BeautifulSoup

# 1) Construction de l'URL où se trouve l'edt
n = 1 #Modifiable, nombre de semaines à prendre à l'avance
dates = [datetime.datetime.now() + datetime.timedelta(days = 7*k) for k in range(n)]
urls = [f"https://sgs-2.mines-paristech.fr/prod/oasis/ensmp/Page/TimeTableView.php?year_in_cursus=1&date={date.year}-{date.month}-{date.day}" for date in dates]

# 2) Extraction des données
# Class contenant un évènement
class evenement:
    def __init__(self, date):
        self.date = date

    def HeureDebut(self, heureDebut):
        self.heureDebut = heureDebut

    def HeureFin(self, heureFin):
        self.heureFin = heureFin

    def Nom(self, nom):
        self.nom = nom
    
allEvenements = []
for url in urls:
    soup = BeautifulSoup(requests.get(url).text, features="html.parser")
    jours = soup.findAll("div", {"class": "timetable-day-wrapper"})
    for jour in jours:
        date = jour.find("div", {"class": "timetable-day-title"}).text
        allCours = jour.findAll("div", {'class': "timetable-day-body"})
        for cours in allCours:
            e = evenement(date)
            e.HeureDebut(cours.find("div", {"class": "timetable-day-time-start"}).text)
            e.heureFin(cours.find("div", {"class": "timetable-day-time-end"}).text)
            e.Nom(cours.find("div", {"class": "timetable-session-course-title"}).text)

            groupes = cours.findAll("div", {"class": "timetable-day-time-start"}).text


    