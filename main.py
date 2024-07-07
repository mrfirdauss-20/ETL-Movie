import csv
import psycopg2
from tqdm import tqdm
from data import Data

conn = psycopg2.connect(
        dbname='etl',
        user='postgres',
        password='postgres',
        host='host.docker.internal',
        port=5416
    )
cursor = conn.cursor()

filename = 'movies.csv'

with open(filename, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in tqdm(csv_reader):
        record = Data(row)
        record.insertToDB(conn)






        