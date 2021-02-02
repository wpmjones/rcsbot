import csv
from datetime import datetime


def get_season_start():
    with open('/home/tuba/season.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            return row['start']


def get_season_end():
    with open('/home/tuba/season.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            return row['end']


def get_days_left():
    date_format = '%Y-%m-%d'
    now = datetime.now()
    with open('/home/tuba/season.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            season_end = row['end']
    delta = datetime.strptime(season_end, date_format) - now
    return delta.days + 1


def get_days_since():
    date_format = '%Y-%m-%d'
    now = datetime.now()
    with open('/home/tuba/season.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            season_start = row['start']
    delta = now - datetime.strptime(season_start, date_format)
    return delta.days


def get_season_length():
    date_format = '%Y-%m-%d'
    with open('/home/tuba/season.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            season_start = row['start']
            season_end = row['end']
    delta = datetime.strptime(season_end, date_format) - datetime.strptime(season_start, date_format)
    return delta.days


def update_season(new_start_date, new_end_date):
    with open("/home/tuba/season.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["start", "end"])
        writer.writerow([new_start_date, new_end_date])
    return "success"
