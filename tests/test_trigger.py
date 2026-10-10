import unittest

from support import build_database, run_file, today


class ReleaseTriggerTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()

    def tearDown(self):
        self.db.close()

    def log_rows(self, animal_id):
        return self.db.execute(
            "SELECT animal_id, release_date, note FROM release_log WHERE animal_id = ?",
            (animal_id,)).fetchall()

    def test_release_writes_one_log_row_with_todays_date_and_a_note(self):
        self.db.execute("UPDATE animals SET status = 'Released' WHERE animal_id = 3")
        self.assertEqual(self.log_rows(3), [
            (3, today(self.db), "Talon (Red-tailed Hawk) released after 95 days in care")])

    def test_saving_released_again_does_not_log_twice(self):
        self.db.execute("UPDATE animals SET status = 'Released' WHERE animal_id = 3")
        self.db.execute("UPDATE animals SET status = 'Released' WHERE animal_id = 3")
        self.assertEqual(len(self.log_rows(3)), 1)

    def test_other_status_changes_are_not_logged(self):
        self.db.execute("UPDATE animals SET status = 'Critical' WHERE animal_id = 1")
        self.db.execute("UPDATE animals SET status = 'Transferred' WHERE animal_id = 2")
        self.assertEqual(self.log_rows(1), [])
        self.assertEqual(self.log_rows(2), [])

    def test_editing_another_column_of_a_released_animal_is_not_logged(self):
        before = len(self.log_rows(6))
        self.db.execute("UPDATE animals SET name = 'Luna II' WHERE animal_id = 6")
        self.assertEqual(len(self.log_rows(6)), before)

    def test_releasing_several_animals_in_one_update_logs_each(self):
        self.db.execute("UPDATE animals SET status = 'Released' WHERE species = 'Red Fox'")
        logged = {row[0] for row in self.db.execute(
            "SELECT animal_id FROM release_log WHERE release_date = date('now')")}
        self.assertEqual(logged, {1, 9})

    def test_demo_script_releases_talon_once(self):
        results = run_file(self.db, "07_release_demo.sql")
        procedure, log, active = results
        self.assertEqual([row[1] for row in procedure[1]], ["Hazel", "Bramble", "Ember"])
        self.assertEqual([row[1] for row in log[1]].count(3), 1)
        self.assertNotIn("Talon", [row[1] for row in active[1]])


if __name__ == "__main__":
    unittest.main()