-- Read-only reports. Nothing in this script changes the data.

-- Report 1: every animal, newest intake first.
SELECT animal_id, name, species, intake_date, status
FROM animals
ORDER BY intake_date DESC, animal_id;

-- Report 2: each rescue with the details of the animal it brought in.
SELECT r.rescue_id, r.rescue_date, r.location, r.rescuer_name, a.name, a.species, a.status
FROM rescues AS r
INNER JOIN animals AS a
    ON a.animal_id = r.animal_id
ORDER BY r.rescue_date DESC, r.rescue_id;

-- Report 3: treatments grouped by animal - how many, and what they cost in total.
SELECT a.animal_id, a.name, COUNT(t.treatment_id) AS treatment_count, ROUND(SUM(t.cost), 2) AS total_cost
FROM treatments AS t
INNER JOIN animals AS a
    ON a.animal_id = t.animal_id
GROUP BY a.animal_id, a.name
ORDER BY total_cost DESC, a.animal_id;

-- Report 4: outcome analytics per species - intakes, releases and spend.
SELECT
    a.species,
    COUNT(*)                                                AS animals,
    SUM(CASE WHEN a.status = 'Released' THEN 1 ELSE 0 END) AS released,
    SUM(CASE WHEN a.status IN ('Released', 'Transferred') THEN 0 ELSE 1 END) AS still_in_care,
    ROUND(COALESCE(SUM(c.cost), 0), 2)                     AS total_cost
FROM animals AS a
LEFT JOIN (SELECT animal_id, SUM(cost) AS cost FROM treatments GROUP BY animal_id) AS c
    ON c.animal_id = a.animal_id
GROUP BY a.species
ORDER BY animals DESC, a.species;