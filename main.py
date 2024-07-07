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
genreMap = {}
starMap = {}
directorMap = {} 
movies_stars = []
movies_directors = []
movies_genres = []
movies_votes = []
movies_analytics = [] 
filename = 'dataset/movies.csv'

with open(filename, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in tqdm(csv_reader):
        record = Data(row)
        genreMap, starMap, directorMap, movies_stars, movies_directors, movies_genres, movies_votes, movies_analytics = record.insertToDB(conn, genreMap, starMap, directorMap, movies_stars, movies_directors, movies_genres, movies_votes, movies_analytics)
    cursor.executemany("INSERT INTO movies_stars (movie_id, star_id) VALUES (%s, %s)", movies_stars)
    cursor.executemany("INSERT INTO movies_directors (movie_id, director_id) VALUES (%s, %s)", movies_directors)
    cursor.executemany("INSERT INTO movies_genres (movie_id, genre_id) VALUES (%s, %s)", movies_genres)
    cursor.executemany("INSERT INTO movies_votes (movie_id, vote_count) VALUES (%s, %s)", movies_votes)
    cursor.executemany("INSERT INTO movies_analytics (movie_id, gross) VALUES (%s, %s)", movies_analytics)
    conn.commit()






        