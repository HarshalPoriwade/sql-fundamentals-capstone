import unittest

import run_sql
from support import IntegrityError, build_database, script_text


class SchemaTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()

    def tearDown(self):
        self.db.close()

    def columns(self, table):
        return [row[1] for row in self.db.execute(f"PRAGMA table_info({table})")]

    def count(self, table):
        return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_required_tables_have_required_columns(self):
        self.assertEqual(self.columns("animals"),
                         ["animal_id", "name", "species", "intake_date", "status"])
        self.assertEqual(self.columns("treatments"),
                         ["treatment_id", "animal_id", "treatment_date", "description", "cost"])
        self.assertEqual(self.columns("rescues"),
                         ["rescue_id", "animal_id", "location", "rescuer_name", "rescue_date"])
        for column in ["animal_id", "release_date", "note"]:
            self.assertIn(column, self.columns("release_log"))

    def test_seed_meets_minimum_row_counts(self):
        self.assertGreaterEqual(self.count("animals"), 8)
        self.assertGreaterEqual(self.count("treatments"), 15)
        self.assertGreaterEqual(self.count("rescues"), 8)

    def test_foreign_keys_are_switched_on(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_treatment_for_missing_animal_is_rejected(self):
        with self.assertRaises(IntegrityError):
            run_sql.run_script(self.db, script_text("08_integrity_demo.sql"))
        self.assertEqual(self.count("treatments"), 18)

    def test_rescue_for_missing_animal_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("INSERT INTO rescues (animal_id, location, rescuer_name, rescue_date) "
                            "VALUES (999, 'Nowhere', 'Nobody', '2026-01-01')")

    def test_animal_with_treatments_cannot_be_deleted(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("DELETE FROM animals WHERE animal_id = 1")
        self.assertEqual(self.count("animals"), 10)

    def test_unknown_status_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("UPDATE animals SET status = 'Escaped' WHERE animal_id = 1")

    def test_badly_formatted_date_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("INSERT INTO animals (name, species, intake_date) "
                            "VALUES ('Dot', 'Mallard', '10/03/2026')")

    def test_negative_cost_is_rejected(self):
        with self.assertRaises(IntegrityError):
            self.db.execute("INSERT INTO treatments (animal_id, treatment_date, description, cost) "
                            "VALUES (1, '2026-01-01', 'Refund?', -5)")

    def test_schema_script_can_be_rerun_on_a_full_database(self):
        run_sql.run_script(self.db, script_text("01_schema.sql"))
        self.assertEqual(self.count("animals"), 0)


class SplitStatementsTest(unittest.TestCase):
    def test_trigger_body_stays_in_one_statement(self):
        statements = run_sql.split_statements(script_text("05_trigger.sql"))
        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[1].rstrip().endswith("END;"))

    def test_windows_line_endings_are_accepted(self):
        text = "-- comment; with a semicolon\r\nSELECT 1;\r\nSELECT\r\n  2;\r\n"
        self.assertEqual(run_sql.split_statements(text),
                         ["-- comment; with a semicolon\nSELECT 1;", "SELECT\n  2;"])

    def test_two_statements_on_one_line_are_split(self):
        self.assertEqual(run_sql.split_statements("UPDATE t SET x = 1; SELECT 'a;b'; -- done\n"),
                         ["UPDATE t SET x = 1;", "SELECT 'a;b';"])

    def test_semicolon_inside_a_string_does_not_split(self):
        self.assertEqual(run_sql.split_statements("SELECT 'a;b';\n"), ["SELECT 'a;b';"])

    def test_unfinished_statement_is_reported(self):
        with self.assertRaises(ValueError):
            run_sql.split_statements("SELECT 1;\nSELECT 2\n")


if __name__ == "__main__":
    unittest.main()