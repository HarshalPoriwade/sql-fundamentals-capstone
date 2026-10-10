-- active_cases: every animal still at the centre, with how many whole days it has been in care.
-- 'Transferred' animals left for another facility, so they are not active here either.
DROP VIEW IF EXISTS active_cases;

CREATE VIEW active_cases AS
SELECT
    animal_id,
    name,
    species,
    intake_date,
    CAST(julianday(date('now')) - julianday(intake_date) AS INTEGER) AS days_in_care
FROM animals
WHERE status NOT IN ('Released', 'Transferred');