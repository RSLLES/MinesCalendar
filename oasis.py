import re
import ics
import json
import fire
import requests
from bs4 import BeautifulSoup

headers = {'Content-Type': 'application/x-www-form-urlencoded'}
first_scrap_day = "2022-09-01"
last_scrap_day = "2023-06-01"
uuid = "421546789512"
timezone = "Europe/Paris"
regex = re.compile(r"<br/?>", re.IGNORECASE)

URL_LOGIN = r'https://oasis.mines-paristech.fr/prod/bo/core/Router/Ajax/ajax.php?targetProject=oasis_ensmp&route=BO\Connection\User::login'
URL_CALENDAR = r'https://oasis.mines-paristech.fr/prod/bo/core/Router/Ajax/ajax.php?targetProject=oasis_ensmp&route=Oasis\Common\Model\TimeAndSpace\Calendar\Calendar::element_feeder'
URL_UE = r'https://oasis.mines-paristech.fr/prod/bo/core/Router/Ajax/ajax.php?targetProject=oasis_ensmp&route=BO\\Layout\\MainContent::load&codepage=MYCHOICES'

#############
### Utils ###
#############

def post(url, data, cookies = None):
    return requests.post(url, data = data, headers= headers, cookies=cookies)

def get(url, cookies = None):
    return requests.get(url, cookies=cookies)

def format(text):
    return BeautifulSoup(re.sub(regex, '\n', text), "html.parser").text

###############
### Methods ###
###############

def get_cookies(login_payload):
    return post(url= URL_LOGIN, data= login_payload).cookies

def get_timetable(cookies, payload):
    return post(
        url= URL_CALENDAR, 
        data= payload,
        cookies= cookies
    ).json()

def filter_courses(timetable):
    return list(filter(lambda event : event['type'] == 'course_program', timetable))

def get_all_ue(cookies):
    html_doc = get(url= URL_UE, cookies= cookies).text
    page = BeautifulSoup(html_doc, 'html.parser')
    tables = page.select('table.table.table-striped.table-hover')
    trs = sum([table.select('tr') for table in tables], [])
    trs_checked = list(filter(lambda tr :  tr.find('input').has_attr('checked'), trs))
    ues = [tr.find('input').attrs['data-course_code'] for tr in trs_checked]
    return ues

def get_calendar_payload(ues):
    payload = "courseCodes="
    payload += "".join([ue + "," for ue in ues])[:-1] + "&"
    payload += "vg=MTlzZWFpbGxlcw%3D%3D" + "&"
    payload += "elementType=course_program" + "&"
    payload += "courseScope=ALL" + "&"
    payload += "roomTypes=" + "&"
    payload += "start=" + f"{first_scrap_day}T00:00:00" + "&"
    payload += "end=" + f"{last_scrap_day}T00:00:00"
    return payload

def create_event(event_json):
    titles = json.loads(event_json['title'])
    name = titles['PROGRAM_TITLE']
    name = name if len(name) != 0 else titles['COURSE_TITLE']
    return ics.event.Event(
        name= format(name),
        description= format(titles['GROUPS']),
        uid = str(event_json['programCode']),
        begin = event_json['start'],
        end = event_json['end']
    )

def timezone(events):
    for event in events:
        event.begin = event.begin.replace(tzinfo='Europe/Paris').to('utc')
        event.end = event.end.replace(tzinfo='Europe/Paris').to('utc')

def get_login_payload(login, password):
    return f"login={login}&password={password}&url=type=HOME&codepage=HOME"

############
### Main ###
############

def main(login, password):
    login_payload = get_login_payload(login= login, password= password)
    cookies = get_cookies(login_payload = login_payload)
    all_ue = get_all_ue(cookies= cookies)
    calendar_payload = get_calendar_payload(ues= all_ue)
    timetable = filter_courses(get_timetable(cookies= cookies, payload= calendar_payload))
    events = [create_event(event_json) for event_json in timetable]
    timezone(events)

    calendar = ics.Calendar(
        creator= uuid,
        events= events
    )

    with open('oasis.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())


###################
### Entry point ###
###################

if __name__ == '__main__':
    fire.Fire(main)