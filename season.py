import csv
from datetime import datetime


def get_season_start():
    with open('/home/tuba/season.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            return row['start']


def get_season_end():
    with open('/home/tuba/season.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            return row['end']


def get_days_left():
    date_format = '%Y-%m-%d'
    now = datetime.now()
    with open('/home/tuba/season.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            season_end = row['end']
    delta = datetime.strptime(season_end, date_format) - now
    return delta.days + 1


def get_days_since():
    date_format = '%Y-%m-%d'
    now = datetime.now()
    with open('/home/tuba/season.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            season_start = row['start']
    delta = now - datetime.strptime(season_start, date_format)
    return delta.days


def get_season_length():
    date_format = '%Y-%m-%d'
    with open('/home/tuba/season.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            season_start = row['start']
            season_end = row['end']
    delta = datetime.strptime(season_end, date_format) - datetime.strptime(season_start, date_format)
    return delta.days
