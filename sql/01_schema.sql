-- Wildlife Rescue Intake Tracker: tables, keys and indexes.
-- SQLite only enforces foreign keys when this is switched on for the connection.
PRAGMA foreign_keys = ON;

-- Drop children before parents so the foreign keys never block a rebuild.
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS rescues;
DROP TABLE IF EXISTS release_log;
DROP TABLE IF EXISTS released_archive;
DROP TABLE IF EXISTS animals;

-- AUTOINCREMENT stops SQLite from handing an archived animal's id to a new animal.
-- Date checks use IS, not =: date('10/03/2026') is NULL, and a CHECK that gives NULL passes.
CREATE TABLE animals (
    animal_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    species     TEXT NOT NULL,
    intake_date TEXT NOT NULL CHECK (date(intake_date) IS intake_date),
    status      TEXT NOT NULL DEFAULT 'In Care'
                CHECK (status IN ('In Care', 'Critical', 'Ready for Release', 'Released', 'Transferred'))
);

CREATE TABLE treatments (
    treatment_id   INTEGER PRIMARY KEY,
    animal_id      INTEGER NOT NULL REFERENCES animals (animal_id),
    treatment_date TEXT NOT NULL CHECK (date(treatment_date) IS treatment_date),
    description    TEXT NOT NULL,
    cost           REAL NOT NULL CHECK (cost >= 0)
);
CREATE TABLE rescues (
    rescue_id    INTEGER PRIMARY KEY,
    animal_id    INTEGER NOT NULL REFERENCES animals (animal_id),
    location     TEXT NOT NULL,
    rescuer_name TEXT NOT NULL,
    rescue_date  TEXT NOT NULL CHECK (date(rescue_date) IS rescue_date)
);

-- No foreign key here on purpose: the log must outlive the animal row once it is archived.
CREATE TABLE release_log (
    log_id       INTEGER PRIMARY KEY,
    animal_id    INTEGER NOT NULL,
    release_date TEXT NOT NULL,
    note         TEXT
);
-- One summary row per archived animal; the PRIMARY KEY stops an animal being archived twice.
CREATE TABLE released_archive (
    animal_id            INTEGER PRIMARY KEY,
    name                 TEXT NOT NULL,
    species              TEXT NOT NULL,
    intake_date          TEXT NOT NULL,
    release_date         TEXT NOT NULL,
    treatment_count      INTEGER NOT NULL,
    total_treatment_cost REAL NOT NULL,
    archived_on          TEXT NOT NULL
);
-- Foreign key columns are what the joins and the GROUP BY reports search on.
CREATE INDEX idx_treatments_animal ON treatments (animal_id);
CREATE INDEX idx_rescues_animal ON rescues (animal_id);
CREATE INDEX idx_release_log_animal ON release_log (animal_id);