import unittest

from support import IntegrityError, build_database, days_ago


class ActiveCasesViewTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()

    def tearDown(self):
        self.db.close()

    def test_view_has_the_required_columns(self):
        cursor = self.db.execute("SELECT * FROM active_cases")
        names = [column[0] for column in cursor.description]
        for column in ["name", "species", "intake_date", "days_in_care"]:
            self.assertIn(column, names)

    def test_released_and_transferred_animals_are_left_out(self):
        names = {row[0] for row in self.db.execute("SELECT name FROM active_cases")}
        self.assertEqual(names, {"Hazel", "Pip", "Talon", "Clover", "Ember", "Willow"})

    def test_days_in_care_counts_whole_days_since_intake(self):
        rows = dict(self.db.execute("SELECT name, days_in_care FROM active_cases"))
        self.assertEqual(rows["Hazel"], 40)
        self.assertEqual(rows["Willow"], 150)
        self.assertEqual(rows["Ember"], 3)

    def test_animal_taken_in_today_has_zero_days(self):
        self.db.execute("INSERT INTO animals (name, species, intake_date) VALUES ('Dot', 'Mallard', date('now'))")
        days = self.db.execute("SELECT days_in_care FROM active_cases WHERE name = 'Dot'").fetchone()[0]
        self.assertEqual(days, 0)

    def test_view_follows_status_changes(self):
        self.db.execute("UPDATE animals SET status = 'Released' WHERE name = 'Hazel'")
        names = {row[0] for row in self.db.execute("SELECT name FROM active_cases")}
        self.assertNotIn("Hazel", names)


class SpeciesProcedureTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()

    def tearDown(self):
        self.db.close()

    def call(self, species):
        self.db.execute("UPDATE species_cost_param SET species = ?", (species,))
        return self.db.execute(
            "SELECT name, treatment_count, total_treatment_cost FROM animals_by_species").fetchall()

    def test_returns_every_animal_of_the_species_with_total_cost(self):
        self.assertEqual(self.call("Red Fox"),
                         [("Hazel", 3, 100.5), ("Bramble", 2, 95.25), ("Ember", 1, 90.0)])

    def test_species_match_ignores_case(self):
        self.assertEqual(self.call("red fox"), self.call("RED FOX"))
        self.assertEqual(len(self.call("red fox")), 3)

    def test_animal_without_treatments_shows_zero_cost(self):
        self.db.execute("INSERT INTO animals (name, species, intake_date) "
                        "VALUES ('Dot', 'Mallard', ?)", (days_ago(self.db, 1),))
        self.assertEqual(self.call("Mallard"), [("Dot", 0, 0.0)])

    def test_unknown_species_returns_no_rows(self):
        self.assertEqual(self.call("Snow Leopard"), [])

    def test_parameter_table_holds_exactly_one_row(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("INSERT INTO species_cost_param (param_id, species) VALUES (2, 'Barn Owl')")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM species_cost_param").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()