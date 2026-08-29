DROP DATABASE LAYOFF
create database Layoff
use Layoff

select * from layoffs ;


# 1. REMOVE DUPLICATE
# 2. STANDERDIZED THE DATA
# 3. HANDLE NULL VALES OR BLANK FIELDS
# 4. REMOVE ANY COLUMNS

# 1. REMOVE DUPLCATES:

-- GOOD PRACTICE
-- Generating the copy of data incase we loose some important data -------------------------------------------------------------------------------------------------
CREATE TABLE layoffs_stagging
LIKE layoffs ;

SELECT *
FROM layoffs_stagging;

INSERT layoffs_stagging
SELECT *
FROM layoffs;


-- STEP 1 : Remove Duplicates -----------------------------------------------------------------------------------------------------------------------------------------------

SELECT *, 
           ROW_NUMBER() OVER ( 
               PARTITION BY company, location, industry, total_laid_off, 
                            percentage_laid_off, `date`, stage, country, 
                            funds_raised_millions
               ORDER BY company 
           ) AS row_num 
    FROM layoffs_stagging;

WITH duplicate_cte AS ( 
    SELECT *, 
           ROW_NUMBER() OVER ( 
               PARTITION BY company, location, industry, total_laid_off, 
                            percentage_laid_off, `date`, stage, country, 
                            funds_raised_millions
               ORDER BY company 
           ) AS row_num 
    FROM layoffs_stagging
)
SELECT*
FROM duplicate_cte
WHERE row_num>1;

SELECT *
FROM layoffs_stagging
WHERE company= 'CASPER';

WITH duplicate_cte AS ( 
    SELECT *, 
           ROW_NUMBER() OVER ( 
               PARTITION BY company, location, industry, total_laid_off, 
                            percentage_laid_off, `date`, stage, country, 
                            funds_raised_millions
               ORDER BY company 
           ) AS row_num 
    FROM layoffs_stagging
)
Delete 
FROM duplicate_cte
WHERE row_num>1;

/* Creating table with this name to keep in mind that duplicates have been removed. This table is used for further cleaning. */
CREATE TABLE `layoffs_stagging2` (
  `company` text,
  `location` text,
  `industry` text,
  `total_laid_off` int DEFAULT NULL,
  `percentage_laid_off` text,
  `date` text,
  `stage` text,
  `country` text,
  `funds_raised_millions` int DEFAULT NULL,
  `row_num` int
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SELECT *
FROM layoffs_stagging2;


INSERT INTO layoffs_stagging2
SELECT *,
ROW_NUMBER() OVER (
PARTITION BY company,location,industry,total_laid_off, 
percentage_laid_off,'date',stage, country, funds_raised_millions) AS row_num
FROM layoffs_stagging;

select * from layoffs_stagging2
where row_num>1;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM layoffs_stagging2
WHERE row_num > 1;

-- STEP 2: Standardizing data-----------------------------------------------------------------------------------------------------------------------------------
SELECT company, TRIM(company)
FROM layoffs_stagging2;

UPDATE layoffs_stagging2
SET company= TRIM(company);

SELECT DISTINCT industry
FROM layoffs_stagging2
ORDER BY 1;

SELECT *
FROM layoffs_stagging2
WHERE industry LIKE 'Crypto%';

UPDATE layoffs_stagging2
SET industry = 'Crypto'
WHERE industry LIKE 'Crypto%';

SELECT DISTINCT location
FROM layoffs_stagging2;

SELECT DISTINCT country
FROM layoffs_stagging2
ORDER BY 1;

UPDATE layoffs_stagging2
SET country = 'United States'
WHERE country LIKE 'United States%';


-- Updating the date column by changing its data type i.e. text to date format 
SELECT `date`
FROM layoffs_stagging2;

UPDATE layoffs_stagging2
SET `date`= STR_TO_DATE (`date`, '%m/%d/%Y');

ALTER TABLE layoffs_duplicate_removal
MODIFY COLUMN `date` DATE;

-- STEP 3: Finding NULL and BLANK spaces----------------------------------------------------------------------------------------------------------------------------
SELECT *
FROM layoffs_stagging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

UPDATE layoffs_stagging2
SET industry = NULL
WHERE industry = '';

SELECT *
FROM layoffs_stagging2
WHERE industry is NULL;

SELECT *
FROM layoffs_stagging2
WHERE company = 'Airbnb';

SELECT *
FROM layoffs_stagging2 t1
JOIN layoffs_stagging2 t2
	ON t1.company = t2.company
WHERE (t1.industry is NULL)
AND t2.industry is NOT NULL;

UPDATE layoffs_stagging2 t1
JOIN layoffs_stagging2 t2
	ON t1.company = t2.company
SET t1.industry = t2.industry
WHERE (t1.industry is NULL)
AND t2.industry is NOT NULL;

-- STEP 4 : Deleting unwanted rows and columns --------------------------------------------------------------------------------------------------------------------
DELETE
FROM layoffs_stagging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

SELECT *
FROM layoffs_stagging2

ALTER TABLE layoffs_stagging2
DROP COLUMN row_num;