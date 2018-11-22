#!/usr/bin/python3
#cur.execute("SELECT kind, url FROM vortrag_links;") <- link für Material

acronym = "c14h"

import psycopg2, argparse, sys, datetime, uuid, lxml, pytz
from collections import OrderedDict

# tools was originally voc.tools, directly vendored from
# https://github.com/voc/schedule/blob/34C3/voc/tools.py
import tools


conn = psycopg2.connect("dbname=nnev user=anon host=/var/run/postgresql sslmode=disable")

cur = conn.cursor()
print("updating schedule.xml")

min_date = datetime.date(2014, 5, 22)
max_date = datetime.date.today()
tz = pytz.timezone('Europe/Berlin')

cur.execute("SELECT id, date, topic, abstract, speaker, password FROM vortraege WHERE date > '{}';".format(min_date.strftime("%Y-%m-%d")))
res = cur.fetchall()

#data = {'date':date.isoformat(), 'topic':abstract, 'speaker': speaker, 'password': password}

cur.close()
conn.close()

"""
now stich everything together for VOC
"""


out = { "schedule":  OrderedDict([
        ("version", "1.0"),
        ("conference",  OrderedDict([
            ("title", "Chaotische Viertelstunde, NoName e.V."),
            ("acronym", acronym),
            ("daysCount", len(res)),
            ("start", max_date.strftime("%Y-%m-%d")),
            ("end",   max_date.strftime("%Y-%m-%d")),
            ("timeslot_duration", "00:15"),
            ("days", [])
        ]))
    ])
}
i = 1
for talkid, date, titel, abstract, speaker, password  in res:
    event_n = OrderedDict([
        ('id', talkid),
        ('guid', str(uuid.uuid4())),
        # ('logo', None),
        ('date', tz.localize(datetime.datetime(date.year, date.month, date.day)).isoformat()),
        ('start', '20:00'),
        ('duration', '0:15'),
        ('room', 'Chaostreff Heidelberg'),
        ('slug', '-'.join([acronym, str(talkid), tools.normalise_string(titel)])),
        ('title', titel),
        ('subtitle', ''),
        ('track', ''),
        ('type', ''),
        ('language', 'de' ),
        ('abstract', abstract),
        ('description', '' ),
        ('do_not_record', False),
        ('persons', [ OrderedDict([
            ('id', 1),
            ('full_public_name', p.strip()),
            #('#text', p),
        ]) for p in speaker.split(',') ]),
        ('links', ["https://www.noname-ev.de/chaotische_viertelstunde.html#c14h_{}".format(talkid)])
    ])
    out['schedule']['conference']['days'].append(OrderedDict([
        ('index', i),  # day-index must be > 0
        ('date' , date.isoformat()),
        ('start', tz.localize(datetime.datetime(date.year, date.month, date.day, 19, 0, 0)).isoformat()),
        ('end', tz.localize(datetime.datetime(date.year, date.month, date.day, 23, 59, 59)).isoformat()),
        ('rooms', OrderedDict([
            ('Chaostreff Heidelberg', [event_n])
            ]))
    ]))
    i += 1

with open('schedule-{}.xml'.format(acronym), 'w') as fp:
    fp.write(tools.dict_to_schedule_xml(out));
