#!/usr/bin/python
# Update country codes across database
#
# Prereqs:
# virtualenv env
# source env/bin/activate
# curl https://bootstrap.pypa.io/get-pip.py | python
# pip3 install mysql-connector country_converter
# python3 update_countries --local

import argparse
import country_converter as coco
import logging
import mysql.connector

import database_connector

class FlightDB(database_connector.DatabaseConnector):
  pass

def clean(raw_name):
  name = cc.convert(names=[raw_name], to='name_short')
  if name == 'not found':
    return (None, None)
  code = cc.convert(names=[raw_name], to='ISO2')
  return (name, code)

if __name__ == "__main__":
  # Suppress noisy coco warnings
  logging.getLogger().setLevel(logging.ERROR)

  parser = argparse.ArgumentParser()
  parser.add_argument('--airlines', default=False, action='store_true')
  parser.add_argument('--airports', default=False, action='store_true')
  parser.add_argument('--countries', default=False, action='store_true')

  parser.add_argument('--live_run', default=False, action='store_true')
  parser.add_argument('--local', default=False, action='store_true')
  args = parser.parse_args()

  fdb = FlightDB(args)
  cc = coco.CountryConverter()

  if args.countries:
    fdb.cursor.execute('SELECT * FROM countries')
    for row in fdb.cursor:
      country, code = clean(row['name'])
      if not country:
        continue
      if row['name'] != country:
        print('NAME', row['name'], '->', country)
      if row['iso_code'] != code:
        print('CODE', row['name'], row['iso_code'], '->', code)

  if args.airlines:
    fdb.cursor.execute('SELECT country FROM airlines GROUP BY country')
    for row in fdb.cursor:
      country, code = clean(row['country'])
      if country:
        print(row['country'], country, code)
      else:
        print('Dubious entry', row)
