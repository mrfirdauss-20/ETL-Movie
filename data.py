import re
class Data():
    def __init__(self, X):
        self.movie = X['MOVIES']
        self.year_start, self.year_end = self.extract_year(X['YEAR'])
        self.director, self.stars = self.extract_director(X['STARS'])
        self.one_line = X['ONE-LINE'][1:] if X['ONE-LINE'] != '' else None
        self.gross = float(X['Gross'].replace('$', '').replace('M','')) if X['Gross'] != '' else None
        self.votes = int(X['VOTES'].replace(',', '')) if X['VOTES'] != '' else None
        self.genre = X['GENRE'][1:].split(', ') if X['GENRE']!= '' else None
        self.rating = float(X['RATING']) if X['RATING'] != '' else None
        self.run_time = int(X['RunTime']) if X['RunTime'] != '' else None
    
    def extract_year(self, X):
        start = None
        end = None
        years = re.findall(r'\b\d+\b', X)

        if '–' in X:
            start = (years[0])
            end = years[1] if len(years)>1 else None
        elif X != '':
            end = years[0] if len(years)>0 else None
        return start, end
    def extract_director(self, X):
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

    def insertToDB(self, conn):
        cursor = conn.cursor()
        queryMovie = "INSERT INTO movies (name, run_time, plot, rating, start_year, end_year) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
        cursor.execute(queryMovie, (self.movie, self.run_time, self.one_line, self.rating, self.year_start, self.year_end))

        movie_id = cursor.fetchone()[0]

        if self.stars:
            for star in self.stars:
                queryStar = "SELECT id FROM stars WHERE name = %s"
                cursor.execute(queryStar, (star.strip(),))
                star_id = cursor.fetchone()

                if (star_id) == None or len(star_id) == 0:
                    queryStar = "INSERT INTO stars (name) VALUES (%s) RETURNING id"
                    cursor.execute(queryStar, (star.strip(),))
                    star_id = cursor.fetchone()
                queryMovieStar = "INSERT INTO movies_stars (movie_id, star_id) VALUES (%s, %s)"
                cursor.execute(queryMovieStar, (movie_id, star_id[0]))
        
        if self.director:
            for director in self.director:
                queryDirector = "SELECT id FROM directors WHERE name = %s"
                cursor.execute(queryDirector, (director.strip(),))
                director_id = cursor.fetchone()
                if (director_id) == None or len(director_id) == 0:
                    queryDirector = "INSERT INTO directors (name) VALUES (%s) RETURNING id"
                    cursor.execute(queryDirector, (director.strip(),))
                    director_id = cursor.fetchone()
                queryMovieDirector = "INSERT INTO movies_directors (movie_id, director_id) VALUES (%s, %s)"
                cursor.execute(queryMovieDirector, (movie_id, director_id[0]))
        
        if self.genre:
            for genre in self.genre:
                queryGenre = "SELECT id FROM genres WHERE name = %s"
                cursor.execute(queryGenre, (genre.strip(),))
                genre_id = cursor.fetchone()
                if (genre_id) == None or len(genre_id) == 0:
                    queryGenre = "INSERT INTO genres (name) VALUES (%s) RETURNING id"
                    cursor.execute(queryGenre, (genre.strip(),))
                    genre_id = cursor.fetchone()
                queryMovieGenre = "INSERT INTO movies_genres (movie_id, genre_id) VALUES (%s, %s)"
                cursor.execute(queryMovieGenre, (movie_id, genre_id[0]))

        queryVote = "INSERT INTO movies_votes (movie_id, vote_count) VALUES (%s, %s)"
        cursor.execute(queryVote, (movie_id, self.votes))

        queryAnalysis = "INSERT INTO movies_analytics (movie_id, gross) VALUES (%s, %s)"
        cursor.execute(queryAnalysis, (movie_id, self.gross))
        conn.commit()