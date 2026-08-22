use world;
 show tables;
# QUESTION 1
 select Name, Continent, Population from country where Continent="Asia";
# QUESTION 2
 SELECT Name, population, LifeExpectancy FROM country
ORDER BY population desc;
# QUESTION 3
 SELECT Name, Continent, Population FROM country
 where Continent="Europe" and Population>20000000
ORDER BY Name;
# QUESTION 4
 SELECT Name, Region,SurfaceArea FROM country
 where Region in ("North America" , "South America")
ORDER BY Region;
# QUESTION 5
 SELECT Name, Continent,Population FROM country
 where Continent != "Africa" ORDER BY Name;
 -- QUESTION 6
 SELECT Name,Population,GovernmentForm FROM country
 where Population between 10000000 and 50000000 order by Population;
 -- QUESTION 7
 select * from city
	 SELECT 
	 co.Name,
	 ci.Name,
	co.Population
	FROM Country co
	 join 
	city ci on ci.ID=co.Capital
	 where 
	 co.Continent in ("Asia" , "Europe","Oceania");
 select * from country where Name="Afghanistan"
 -- QUESTION 8
SELECT Name,Region,Population FROM country
 where name like "A%" order by Name
-- QUESTION 9
select name,continent,Population,LifeExpectancy FROM COUNTRY 
WHERE CONTINENT in ("ASIA","EUROPE")and
Population>50000000 and LifeExpectancy>70
order by Population desc
-- QUESTION 10
select name,Continent,Population,GovernmentForm FROM COUNTRY
where CONTINENT !="Africa"and Population between 5000000 and 30000000
and Name like "%land%" order by Name; 
