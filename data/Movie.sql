CREATE TABLE movies (
  id SERIAL PRIMARY KEY,
  name varchar(256),
  run_time int,
  plot text,
  rating real,
  start_year integer,
  end_year integer
);

CREATE TABLE movies_votes (
  movie_id integer,
  vote_count integer
);

CREATE TABLE movies_analytics (
  movie_id integer,
  gross real
);

CREATE TABLE stars (
  id SERIAL PRIMARY KEY,
  name varchar(256)
);

CREATE TABLE movies_stars (
  star_id integer,
  movie_id integer
);

CREATE TABLE directors (
  id SERIAL PRIMARY KEY,
  name varchar(256)
);

CREATE TABLE movies_directors (
  directors_id integer,
  movie_id integer
);

CREATE TABLE genres (
  id SERIAL PRIMARY KEY,
  name varchar(256)
);

CREATE TABLE movies_genres (
  movie_id integer,
  genre_id integer
);

ALTER TABLE movies_votes ADD FOREIGN KEY (movie_id) REFERENCES movies (id);

ALTER TABLE movies_genres ADD FOREIGN KEY (movie_id) REFERENCES movies (id);

ALTER TABLE movies_genres ADD FOREIGN KEY (genre_id) REFERENCES genres (id);

ALTER TABLE movies_analytics ADD FOREIGN KEY (movie_id) REFERENCES movies (id);

ALTER TABLE movies_stars ADD FOREIGN KEY (star_id) REFERENCES stars (id);

ALTER TABLE movies_stars ADD FOREIGN KEY (movie_id) REFERENCES movies (id);

ALTER TABLE movies_directors ADD FOREIGN KEY (directors_id) REFERENCES directors (id);

ALTER TABLE movies_directors ADD FOREIGN KEY (movie_id) REFERENCES movies (id);

create view movie_gross (id, name, rating, start_year, end_year, gross) as 
select
  m.id,
	name,
	rating,
	start_year,
	end_year,
  gross
from movies m 
join movies_analytics ma on ma.movie_id = m.id
where gross is not null;

create view film (id, name, rating, release_year) as
select
  m.id,
  name,
  rating,
  end_year
from movies m
where start_year is null;