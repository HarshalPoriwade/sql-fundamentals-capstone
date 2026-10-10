-- Archive animals released more than 365 days ago, then remove them from the live tables.
PRAGMA foreign_keys = ON;

-- One transaction: either every step below happens, or none of them does.
BEGIN TRANSACTION;

-- Copy a summary of each old release into the archive. The latest release_log row wins.
INSERT INTO released_archive
    (animal_id, name, species, intake_date, release_date, treatment_count, total_treatment_cost, archived_on)
SELECT
    a.animal_id,
    a.name,
    a.species,
    a.intake_date,
    rl.release_date,
    (SELECT COUNT(*) FROM treatments AS t WHERE t.animal_id = a.animal_id),
    (SELECT ROUND(COALESCE(SUM(t.cost), 0), 2) FROM treatments AS t WHERE t.animal_id = a.animal_id),
    date('now')
FROM animals AS a
INNER JOIN (SELECT animal_id, MAX(release_date) AS release_date
            FROM release_log GROUP BY animal_id) AS rl
    ON rl.animal_id = a.animal_id
WHERE a.status = 'Released'
  AND julianday(date('now')) - julianday(rl.release_date) > 365;

-- Children first: the foreign keys refuse to delete an animal that still has treatments or rescues.
DELETE FROM treatments WHERE animal_id IN (SELECT animal_id FROM released_archive);
DELETE FROM rescues    WHERE animal_id IN (SELECT animal_id FROM released_archive);
DELETE FROM animals    WHERE animal_id IN (SELECT animal_id FROM released_archive);

COMMIT;

SELECT animal_id, name, species, release_date, treatment_count, total_treatment_cost
FROM released_archive
ORDER BY animal_id;

SELECT
    (SELECT COUNT(*) FROM animals)    AS animals_left,
    (SELECT COUNT(*) FROM treatments) AS treatments_left,
    (SELECT COUNT(*) FROM rescues)    AS rescues_left;