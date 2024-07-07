-- 1. Number of unique film titles
select count(distinct name) from movies where start_year is null;

-- 2. Film Title, Year of Release, and Rating of the film starring Lena Headey Sort By Yearof Release.
select 
    m.name as "Film Title",
    release_year as "Year of Release",
    rating as "Rating"
from film m
join movies_stars on m.id = movies_stars.movie_id
join stars on stars.id = movies_stars.star_id
where stars.name = 'Lena Headey'
order by release_year

-- 3. The name of the director and total gross of the films that have been directed.
select 
    d.name as "Director",
    concat('$',coalesce(sum(gross), 0),'M') as "Total Gross"
from movie_gross m
join movies_directors on m.id = movies_directors.movie_id
join directors d on d.id = movies_directors.directors_id
where start_year is null 
group by 1

-- 4. Film Title, Year of Release, and Rating of 5 films that have comedy genre with the largest gross
select  
    m.name as "Film Title",
    release_year as "Year of Release",
    rating as "Rating"
from film m
join movies_genres on m.id = movies_genres.movie_id
join genres on genres.id = movies_genres.genre_id
join movies_analytics on m.id = movies_analytics.movie_id
where genres.name = 'Comedy' and gross is not null
order by gross desc
limit 5

-- 5. Film Title, Year of Release and Rating of the film directed by Martin Scorsese and starring Robert De Niro
select
    m.name as "Film Title",
    release_year as "Year of Release",
    rating as "Rating"
from film m
join movies_directors on m.id = movies_directors.movie_id
join directors d on d.id = movies_directors.directors_id
join movies_stars on m.id = movies_stars.movie_id
join stars on stars.id = movies_stars.star_id
where d.name = 'Martin Scorsese' and stars.name = 'Robert De Niro'
