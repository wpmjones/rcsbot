import csv
from datetime import datetime, date

def getSeasonStart():
  with open('/home/tuba/season.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      return row['start']

def getSeasonEnd():
  with open('/home/tuba/season.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      return row['end']

def getDaysLeft():
  dateFormat = '%Y-%m-%d'
  now = datetime.now()
  with open('/home/tuba/season.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      seasonEnd = row['end']
  delta = datetime.strptime(seasonEnd, dateFormat) - now
  return delta.days + 1

def getDaysSince():
  dateFormat = '%Y-%m-%d'
  now = datetime.now()
  with open('/home/tuba/season.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      seasonStart = row['start']
  delta = now - datetime.strptime(seasonStart, dateFormat)
  return delta.days

def getSeasonLength():
  dateFormat = '%Y-%m-%d'
  with open('/home/tuba/season.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      seasonStart = row['start']
      seasonEnd = row['end']
  delta = datetime.strptime(seasonEnd, dateFormat) - datetime.strptime(seasonStart, dateFormat)
  return delta.days
