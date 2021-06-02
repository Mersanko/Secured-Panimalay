import os
import csv
basedir = os.path.abspath(os.path.dirname(__file__))


SECRET_KEY = "tothinkistheprogrammersmantra"


DB_NAME = "panimalay"
DB_HOST = "localhost"
DB_USERNAME = "root"
DB_PASSWORD = "kumsainibai2022"

with open('adminCodes.csv', newline='') as csvfile:
    ADMIN_CODES = list(csv.reader(csvfile))

