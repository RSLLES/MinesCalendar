import requests
import datetime

# 1) Construction de l'URL où se trouve l'edt
n = 2 #Modifiable, nombre de semaines à prendre à l'avance
dates = [datetime.datetime.now() + datetime.timedelta(days = 7*k) for k in range(n)]
urls = [f"https://sgs-2.mines-paristech.fr/prod/oasis/ensmp/Page/TimeTableView.php?year_in_cursus=1&date={date.year}-{date.month}-{date.day}" for date in dates]

# 2) Extraction des données
for url in urls:
    