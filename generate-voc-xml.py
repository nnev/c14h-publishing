#!/usr/bin/python3

acronym = "C14H"

import psycopg2, argparse, sys, datetime, uuid, lxml
from collections import OrderedDict

# tools was originally voc.tools, directly vendored from
# https://github.com/voc/schedule/blob/34C3/voc/tools.py
import tools

def err(code, msg):
    print(msg, file=sys.stderr)
    exit(code)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', '--id', dest='id', type=int, action='store', default=-1, help='ID of the talk to be published')

args = parser.parse_args()

conn = psycopg2.connect("dbname=nnev user=anon host=/var/run/postgresql sslmode=disable")

cur = conn.cursor()

if args.id > 0:
    cur.execute("SELECT id, date, topic, abstract, speaker, password FROM vortraege WHERE id = {};".format(args.id))
else:
    print("no talk-ID provided, ExcNotImplemented")
    exit(0)

res = cur.fetchall()

if len(res) < 1:
    err(1, "no talks with ID {} found".format(args.id))
elif len(res) > 1:
    err(2, "more than one talk with ID {} found, please check before proceeding, something is very broken here".format(args.id))

talkid, date, titel, abstract, speaker, password = res[0]

#data = {'date':date.isoformat(), 'topic':abstract, 'speaker': speaker, 'password': password}

min_date = datetime.date(2014, 5, 22)
max_date = datetime.date.today()

# get the number of talks with videos
cur.execute("SELECT date FROM vortraege WHERE date > '{}'".format(min_date.strftime("%Y-%m-%d")))
all_dates = [e[0] for e in cur.fetchall()]

cur.close()
conn.close()
