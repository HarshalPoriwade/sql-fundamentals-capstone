-- Sample data. Dates are written relative to today with date('now', '-N days'),
-- so "days in care" and the 365-day archive rule give the same answers whenever you run it.
PRAGMA foreign_keys = ON;

INSERT INTO animals (animal_id, name, species, intake_date, status) VALUES
    (1,  'Hazel',   'Red Fox',               date('now', '-40 days'),  'In Care'),
    (2,  'Pip',     'Eastern Gray Squirrel', date('now', '-12 days'),  'Critical'),
    (3,  'Talon',   'Red-tailed Hawk',       date('now', '-95 days'),  'Ready for Release'),
    (4,  'Shelly',  'Box Turtle',            date('now', '-600 days'), 'Released'),
    (5,  'Bramble', 'Red Fox',               date('now', '-520 days'), 'Released'),
    (6,  'Luna',    'Barn Owl',              date('now', '-200 days'), 'Released'),
    (7,  'Clover',  'Eastern Cottontail',    date('now', '-5 days'),   'In Care'),
    (8,  'Moss',    'Virginia Opossum',      date('now', '-30 days'),  'Transferred'),
    (9,  'Ember',   'Red Fox',               date('now', '-3 days'),   'Critical'),
    (10, 'Willow',  'White-tailed Deer',     date('now', '-150 days'), 'In Care');

INSERT INTO treatments (treatment_id, animal_id, treatment_date, description, cost) VALUES
    (1,  1,  date('now', '-40 days'),  'Intake exam and mange skin scrape', 45.00),
    (2,  1,  date('now', '-38 days'),  'Ivermectin course for mange', 30.50),
    (3,  1,  date('now', '-20 days'),  'Follow-up skin check', 25.00),
    (4,  2,  date('now', '-12 days'),  'Fluids for dehydration', 18.75),
    (5,  2,  date('now', '-11 days'),  'Splint on fractured forelimb', 60.00),
    (6,  3,  date('now', '-95 days'),  'Wing radiograph', 120.00),
    (7,  3,  date('now', '-60 days'),  'Flight conditioning session', 15.00),
    (8,  4,  date('now', '-600 days'), 'Shell fracture repair', 210.00),
    (9,  4,  date('now', '-540 days'), 'Shell recheck', 35.00),
    (10, 5,  date('now', '-520 days'), 'Intake exam', 40.00),
    (11, 5,  date('now', '-500 days'), 'Antibiotics for bite wound', 55.25),
    (12, 6,  date('now', '-200 days'), 'Eye flush and ointment', 22.00),
    (13, 6,  date('now', '-150 days'), 'Night-vision test before release', 10.00),
    (14, 7,  date('now', '-5 days'),   'Orphan feeding formula', 12.50),
    (15, 8,  date('now', '-30 days'),  'Tail laceration sutures', 75.00),
    (16, 9,  date('now', '-3 days'),   'Emergency wound cleaning', 90.00),
    (17, 10, date('now', '-150 days'), 'Leg laceration sutures', 140.00),
    (18, 10, date('now', '-100 days'), 'Physiotherapy session', 35.00);

INSERT INTO rescues (rescue_id, animal_id, location, rescuer_name, rescue_date) VALUES
    (1,  1,  'Maple Street backyard',   'Priya Shah',     date('now', '-40 days')),
    (2,  2,  'Riverside Park',          'Tom Becker',     date('now', '-13 days')),
    (3,  3,  'Highway 9 shoulder',      'Officer Lin',    date('now', '-95 days')),
    (4,  4,  'Cedar Creek trail',       'Ana Morales',    date('now', '-601 days')),
    (5,  5,  'Old Mill farm',           'Grace Okafor',   date('now', '-520 days')),
    (6,  6,  'St. Mark church barn',    'Daniel Reyes',   date('now', '-200 days')),
    (7,  7,  'Elm Elementary field',    'Priya Shah',     date('now', '-5 days')),
    (8,  8,  'Downtown parking garage', 'Sam Whitfield',  date('now', '-31 days')),
    (9,  9,  'Pine Hollow road',        'Tom Becker',     date('now', '-3 days')),
    (10, 10, 'Lakeview golf course',    'Grace Okafor',   date('now', '-151 days'));

-- Past releases. These animals were inserted as 'Released', so the trigger never saw them;
-- their release dates are recorded here by hand.
INSERT INTO release_log (animal_id, release_date, note) VALUES
    (4, date('now', '-480 days'), 'Shelly (Box Turtle) released after 120 days in care'),
    (5, date('now', '-400 days'), 'Bramble (Red Fox) released after 120 days in care'),
    (6, date('now', '-60 days'),  'Luna (Barn Owl) released after 140 days in care');