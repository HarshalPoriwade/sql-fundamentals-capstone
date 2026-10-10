-- "Stored procedure" animals_by_species(species).
-- SQLite has no CREATE PROCEDURE, so the procedure is built from two parts:
--   1. species_cost_param  - a one-row table that holds the input parameter
--   2. animals_by_species  - a view that reads the parameter and returns the result
-- Call it in two statements:
--   UPDATE species_cost_param SET species = 'Red Fox';
--   SELECT * FROM animals_by_species;
DROP VIEW IF EXISTS animals_by_species;
DROP TABLE IF EXISTS species_cost_param;

-- CHECK (param_id = 1) means the table can never hold a second, competing parameter row.
CREATE TABLE species_cost_param (
    param_id INTEGER PRIMARY KEY CHECK (param_id = 1),
    species  TEXT NOT NULL
);

INSERT INTO species_cost_param (param_id, species) VALUES (1, 'Red Fox');

-- LEFT JOIN keeps an animal that has had no treatments yet; COALESCE turns its NULL sum into 0.
CREATE VIEW animals_by_species AS
SELECT
    a.animal_id,
    a.name,
    a.species,
    a.status,
    COUNT(t.treatment_id) AS treatment_count,
    ROUND(COALESCE(SUM(t.cost), 0), 2) AS total_treatment_cost
FROM animals AS a
JOIN species_cost_param AS p
    ON a.species = p.species COLLATE NOCASE
LEFT JOIN treatments AS t
    ON t.animal_id = a.animal_id
GROUP BY a.animal_id, a.name, a.species, a.status
ORDER BY total_treatment_cost DESC, a.animal_id;