-- Referential integrity demo. This script is MEANT to fail.
-- There is no animal 999, so the foreign key on treatments.animal_id rejects the row.
PRAGMA foreign_keys = ON;

INSERT INTO treatments (animal_id, treatment_date, description, cost)
VALUES (999, date('now'), 'Treatment for an animal that does not exist', 10.00);