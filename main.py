import csv
import psycopg2
import re

conn = psycopg2.connect(
        dbname='etl',
        user='postgres',
        password='postgres',
        host='host.docker.internal',
        port=5416
    )
cursor = conn.cursor()

def read_csv_to_dict(filename):
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        list_of_dicts = [row for row in csv_reader]
    return list_of_dicts

def remove_parentheses_replace(text):
    text = text.replace('(', '')
    text = text.replace(')', '')
    return text
# Replace 'data.csv' with your file name
filename = 'movies.csv'
data = read_csv_to_dict(filename)

for dantum in data:
    if dantum['YEAR'] == '':
        dantum['year_start'] = None
        dantum['year_end'] = None
    elif '–' in dantum['YEAR']:
        years = re.findall(r'\b\d+\b', dantum['YEAR'])
        dantum['year_start'] = (years[0])
        dantum['year_end'] = years[1] if len(years)>1 else None
    else:
        dantum['year_start'] = None
        year = re.findall(r'\b\d+\b', dantum['YEAR'])
        dantum['year_end'] = year[0] if len(year)>0 else None

    if 'Director:' in dantum['STARS'] and 'Stars:' in dantum['STARS']:
        stars = dantum['STARS'].split('|')
        dantum['DIRECTOR'] = stars[0][:-1].split(':\n')[1].split(', \n')
        dantum['STARS'] = stars[1][:-1].split(':\n')[1].split(', \n')
    elif 'Director:' in dantum['STARS']:
        dantum['DIRECTOR'] = dantum['STARS'][:-1].split(':\n')[1].split(', \n')
        dantum['STARS'] = None
    elif 'Stars:' in dantum['STARS']:
        dantum['STARS'] = dantum['STARS'][:-1].split(':\n')[1].split(', \n')
        dantum['DIRECTOR'] = None
    else:
        dantum['STARS'] = None
        dantum['DIRECTOR'] = None
    dantum['ONE-LINE'] = dantum['ONE-LINE'][1:] if dantum['ONE-LINE'] != '' else None
    dantum['Gross'] = float(dantum['Gross'].replace('$', '').replace('M','')) if dantum['Gross'] != '' else None
    dantum['VOTES'] = int(dantum['VOTES'].replace(',', '')) if dantum['VOTES'] != '' else None
    dantum['GENRE'] = dantum['GENRE'][1:].split(', ') if dantum['GENRE']!= '' else None
    dantum['RATING'] = float(dantum['RATING']) if dantum['RATING'] != '' else None
    dantum['RunTime'] = int(dantum['RunTime']) if dantum['RunTime'] != '' else None
#     CREATE TABLE movies (
#   id integer PRIMARY KEY,
#   name varchar,
#   run_time int,
#   plot varchar,
#   rating real,
#   start_year integer,
#   end_year integer
# );
    queryMovie = "INSERT INTO movies (name, run_time, plot, rating, start_year, end_year) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"

    cursor.execute(queryMovie, (dantum['MOVIES'], dantum['RunTime'], dantum['ONE-LINE'], dantum['RATING'], dantum['year_start'], dantum['year_end']))
    movie_id = cursor.fetchone()[0]

    #     CREATE TABLE stars (
    #   id SERIAL PRIMARY KEY,
    #   name varchar(64)
    # );

    #select all stars from table, if results length != array, insert the nonexist stars into table stars
    #insert  the relation between movies_stars
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







        