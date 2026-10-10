-- Demonstrates the procedure, the trigger and the view working together.
PRAGMA foreign_keys = ON;

-- Call the procedure for one species. Matching ignores upper/lower case.
UPDATE species_cost_param SET species = 'red fox';
SELECT * FROM animals_by_species;

-- Talon the hawk is ready to go: releasing it fires the trigger.
UPDATE animals SET status = 'Released' WHERE animal_id = 3;

-- Saving the same status again must NOT add a second log row.
UPDATE animals SET status = 'Released' WHERE animal_id = 3;

SELECT log_id, animal_id, release_date, note FROM release_log ORDER BY log_id;

-- Talon has left active_cases.
SELECT * FROM active_cases ORDER BY days_in_care DESC;