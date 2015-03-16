#!/usr/bin/env
from __future__ import unicode_literals
from collections import defaultdict
import os

import bs4
import jinja2
from slugify import slugify


INPUT_FILE_PATH = 'punkty.xml'


class InfoPoint(object):
    CENTRAL = 0
    NOM = 1
    STREET = 2
    CODE = 3
    CITY = 4
    STATE = 5
    PHONE = 6
    EMAIL = 7
    PAYMENT = 8
    SELL_POINT = 9

    STATE_TO_ID = {
        'dolnoslaskie': 'pl1',
        'kujawsko-pomorskie': 'pl2',
        'lubelskie': 'pl3',
        'lubuskie': 'pl4',
        'lodzkie': 'pl5',
        'malopolskie': 'pl6',
        'mazowieckie': 'pl7',
        'opolskie': 'pl8',
        'podkarpackie': 'pl9',
        'podlaskie': 'pl10',
        'pomorskie': 'pl11',
        'slaskie': 'pl12',
        'swietokrzyskie': 'pl13',
        'warminsko-mazurskie': 'pl14',
        'wielkopolskie': 'pl15',
        'zachodniopomorskie': 'pl16',
    }

    def __init__(
        self, central, nom, street, code, city, state, phone, email, payment, sell_point):

        self.central = central
        self.nom = nom
        self.street = street
        self.code = code
        self.city = city
        self.state = state
        self.phone = phone
        self.email = email
        self.payment = payment
        self.sell_point = sell_point

    @classmethod
    def from_row(cls, row):
        central = row[cls.CENTRAL].find('Data').text
        nom = row[cls.NOM].find('Data').text
        street = row[cls.STREET].find('Data').text
        code = row[cls.CODE].find('Data').text
        city = row[cls.CITY].find('Data').text.capitalize()
        state = row[cls.STATE].find('Data').text
        payment = int(row[cls.PAYMENT].find('Data').text)
        sell_point = int(row[cls.SELL_POINT].find('Data').text)

        email = row[cls.EMAIL].find('Data')
        phone = row[cls.PHONE].find('Data')

        return cls(
            central=central,
            nom=nom,
            street=street,
            code=code,
            city=city,
            state=state,
            phone=phone,
            email=email,
            payment=payment,
            sell_point=sell_point
        )

    @property
    def city_slug(self):
        return slugify(self.city)

    @property
    def state_slug(self):
        return slugify(self.state)

    @property
    def state_capitalized(self):
        return self.state.capitalize()

    @property
    def state_id(self):
        return self.STATE_TO_ID.get(self.state_slug)

    @property
    def phone_normalized(self):
        return self.phone.text if self.phone else self.phone

    @property
    def email_normalized(self):
        return self.email.text if self.email else self.email

    @property
    def state_key(self):
        return self.state_id, self.state_capitalized

    @property
    def city_key(self):
        return self.city, self.city_slug

    def __json__(self):
        return {
            'centrala': self.central,
            'nom': self.nom,
            'ulica': self.street,
            'kod': self.code,
            'telefon': self.phone_normalized,
            'email': self.email_normalized,
            'doladowanie': self.payment,
            'sprzedaz': self.sell_point,
        }


class FileCreator(object):
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.soup = bs4.BeautifulSoup(
            self.file.read(), 'xml', from_encoding='utf-8')

    def process_points(self):
        points_list = defaultdict(lambda: defaultdict(list))
        worksheet = self.soup.find('Table')
        rows = worksheet.find_all('Row')

        for row in rows[1:]:
            info_point = self.process_single_row(row)
            points_list[info_point.state_key][info_point.city_key].append(
                info_point.__json__()
            )
        return points_list

    def process_single_row(self, row):
        single_row = row.find_all('Cell')
        info_point = InfoPoint.from_row(single_row)
        return info_point


def write_html(points_list):
    template_loader = jinja2.FileSystemLoader(searchpath=os.getcwd())
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('templates/points.html')

    html = template.render({'states': points_list})
    with open(os.path.join(os.getcwd(), 'points_lista1.html'), 'w') as f:
        f.write(html.encode('utf-8'))

creator = FileCreator(INPUT_FILE_PATH)
points_list = creator.process_points()
write_html(points_list)
