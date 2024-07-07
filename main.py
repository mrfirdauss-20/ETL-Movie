import csv
import psycopg2
import re
from tqdm import tqdm

conn = psycopg2.connect(
        dbname='etl',
        user='postgres',
        password='postgres',
        host='host.docker.internal',
        port=5416
    )
cursor = conn.cursor()

def extract_year(X):
    start = None
    end = None
    years = re.findall(r'\b\d+\b', X)

    if '–' in X:
        start = (years[0])
        end = years[1] if len(years)>1 else None
    elif X != '':
        end = years[0] if len(years)>0 else None
    return start, end

def extract_director(X):
    stars = None
    director = None
    if 'Director:' in X and 'Stars:' in X:
        stars = X.split('|')
        director = stars[0][:-1].split(':\n')[1].split(', \n')
        stars = stars[1][:-1].split(':\n')[1].split(', \n')
    elif 'Director:' in X:
        director = X[:-1].split(':\n')[1].split(', \n')
    elif 'Stars:' in X:
        stars = X[:-1].split(':\n')[1].split(', \n')
    return director, stars

def load_data(dantum):
    dantum['year_start'], dantum['year_end'] = extract_year(dantum['YEAR'])
    dantum['DIRECTOR'], dantum['STARS'] = extract_director(dantum['STARS'])    

    dantum['ONE-LINE'] = dantum['ONE-LINE'][1:] if dantum['ONE-LINE'] != '' else None
    dantum['Gross'] = float(dantum['Gross'].replace('$', '').replace('M','')) if dantum['Gross'] != '' else None
    dantum['VOTES'] = int(dantum['VOTES'].replace(',', '')) if dantum['VOTES'] != '' else None
    dantum['GENRE'] = dantum['GENRE'][1:].split(', ') if dantum['GENRE']!= '' else None
    dantum['RATING'] = float(dantum['RATING']) if dantum['RATING'] != '' else None
    dantum['RunTime'] = int(dantum['RunTime']) if dantum['RunTime'] != '' else None

    queryMovie = "INSERT INTO movies (name, run_time, plot, rating, start_year, end_year) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"

    cursor.execute(queryMovie, (dantum['MOVIES'], dantum['RunTime'], dantum['ONE-LINE'], dantum['RATING'], dantum['year_start'], dantum['year_end']))
    movie_id = cursor.fetchone()[0]

    if dantum['STARS']:
        for star in dantum['STARS']:
            queryStar = "SELECT id FROM stars WHERE name = %s"
            cursor.execute(queryStar, (star.strip(),))
            star_id = cursor.fetchone()

            if (star_id) == None or len(star_id) == 0:
                queryStar = "INSERT INTO stars (name) VALUES (%s) RETURNING id"
                cursor.execute(queryStar, (star.strip(),))
                star_id = cursor.fetchone()
            queryMovieStar = "INSERT INTO movies_stars (movie_id, star_id) VALUES (%s, %s)"
            cursor.execute(queryMovieStar, (movie_id, star_id[0]))

    if dantum['DIRECTOR']:
        for director in dantum['DIRECTOR']:
            queryDirector = "SELECT id FROM directors WHERE name = %s"
            cursor.execute(queryDirector, (director.strip(),))
            director_id = cursor.fetchone()

            if (director_id) == None or len(director_id) == 0:
                queryDirector = "INSERT INTO directors (name) VALUES (%s) RETURNING id"
                cursor.execute(queryDirector, (director.strip(),))
                director_id = cursor.fetchone()
            queryMovieDirector = "INSERT INTO movies_directors (movie_id, directors_id) VALUES (%s, %s)"
            cursor.execute(queryMovieDirector, (movie_id, director_id[0]))

    if dantum['GENRE']:
        for genre in dantum['GENRE']:
            queryGenre = "SELECT id FROM genres WHERE name = %s"
            cursor.execute(queryGenre, (genre.strip(),))
            genre_id = cursor.fetchone()
            if (genre_id) == None or len(genre_id) == 0:
                queryGenre = "INSERT INTO genres (name) VALUES (%s) RETURNING id"
                cursor.execute(queryGenre, (genre.strip(),))
                genre_id = cursor.fetchone()
            queryMovieGenre = "INSERT INTO movies_genres (movie_id, genre_id) VALUES (%s, %s)"
            cursor.execute(queryMovieGenre, (movie_id, genre_id[0]))
    
    queryVotes = "INSERT INTO movies_votes (movie_id, vote_count) VALUES (%s, %s)"
    cursor.execute(queryVotes, (movie_id, (dantum['VOTES'])))

    queryAnalysis = "INSERT INTO movies_analytics (movie_id, gross) VALUES (%s, %s)"
    cursor.execute(queryAnalysis, (movie_id, (dantum['Gross'])))
    conn.commit()

filename = 'movies.csv'

with open(filename, mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in tqdm(csv_reader):
        load_data(row)






        