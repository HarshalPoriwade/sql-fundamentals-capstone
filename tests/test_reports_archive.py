import unittest

from support import build_database, days_ago, run_file


class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()
        self.changes_before = self.db.total_changes
        self.results = run_file(self.db, "06_reports.sql")

    def tearDown(self):
        self.db.close()

    def report(self, number):
        return self.results[number - 1]

    def test_reports_change_nothing(self):
        self.assertEqual(self.db.total_changes, self.changes_before)

    def test_animals_sorted_by_intake_date_newest_first(self):
        columns, rows = self.report(1)
        dates = [row[columns.index("intake_date")] for row in rows]
        self.assertEqual(len(rows), 10)
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual(rows[0][1], "Ember")

    def test_rescues_are_joined_to_their_animals(self):
        columns, rows = self.report(2)
        self.assertEqual(len(rows), 10)
        by_location = {row[columns.index("location")]: row for row in rows}
        talon = by_location["Highway 9 shoulder"]
        self.assertEqual(talon[columns.index("name")], "Talon")
        self.assertEqual(talon[columns.index("species")], "Red-tailed Hawk")

    def test_inner_join_drops_animals_without_a_rescue(self):
        self.db.execute("INSERT INTO animals (name, species, intake_date) VALUES ('Dot', 'Mallard', date('now'))")
        _, rows = run_file(self.db, "06_reports.sql")[1]
        self.assertNotIn("Dot", [row[4] for row in rows])

    def test_treatments_grouped_with_count_and_sum(self):
        columns, rows = self.report(3)
        totals = {row[1]: (row[2], row[3]) for row in rows}
        self.assertEqual(totals["Hazel"], (3, 100.5))
        self.assertEqual(totals["Shelly"], (2, 245.0))
        self.assertEqual(sum(count for count, _ in totals.values()), 18)
        self.assertEqual(columns, ["animal_id", "name", "treatment_count", "total_cost"])

    def test_outcomes_per_species(self):
        columns, rows = self.report(4)
        foxes = rows[0]
        self.assertEqual(foxes[:4], ("Red Fox", 3, 1, 2))
        self.assertAlmostEqual(foxes[4], 285.75)
        opossum = [row for row in rows if row[0] == "Virginia Opossum"][0]
        self.assertEqual(opossum[2:4], (0, 0))


class ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.db = build_database()

    def tearDown(self):
        self.db.close()

    def ids(self, table):
        return {row[0] for row in self.db.execute(f"SELECT animal_id FROM {table}")}

    def test_only_releases_older_than_365_days_are_archived(self):
        run_file(self.db, "09_archive.sql")
        self.assertEqual(self.ids("released_archive"), {4, 5})
        self.assertNotIn(4, self.ids("animals"))
        self.assertNotIn(5, self.ids("animals"))
        self.assertIn(6, self.ids("animals"))

    def test_archive_row_keeps_the_summary(self):
        run_file(self.db, "09_archive.sql")
        row = self.db.execute("SELECT name, release_date, treatment_count, total_treatment_cost "
                              "FROM released_archive WHERE animal_id = 4").fetchone()
        self.assertEqual(row, ("Shelly", days_ago(self.db, 480), 2, 245.0))

    def test_child_rows_are_removed_and_release_log_is_kept(self):
        run_file(self.db, "09_archive.sql")
        self.assertFalse({4, 5} & self.ids("treatments"))
        self.assertFalse({4, 5} & self.ids("rescues"))
        self.assertTrue({4, 5} <= self.ids("release_log"))
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_exactly_365_days_is_not_old_enough(self):
        self.db.execute("UPDATE release_log SET release_date = ? WHERE animal_id = 5",
                        (days_ago(self.db, 365),))
        run_file(self.db, "09_archive.sql")
        self.assertEqual(self.ids("released_archive"), {4})

    def test_animal_back_in_care_is_not_archived(self):
        self.db.execute("UPDATE animals SET status = 'In Care' WHERE animal_id = 5")
        run_file(self.db, "09_archive.sql")
        self.assertEqual(self.ids("released_archive"), {4})

    def test_running_the_archive_twice_is_safe(self):
        run_file(self.db, "09_archive.sql")
        run_file(self.db, "09_archive.sql")
        self.assertEqual(self.ids("released_archive"), {4, 5})
        self.assertEqual(len(self.ids("animals")), 8)

    def test_archived_id_is_never_given_to_a_new_animal(self):
        # Make the highest id an old release, archive it, then take in a new animal.
        self.db.execute("INSERT INTO animals (animal_id, name, species, intake_date, status) "
                        "VALUES (11, 'Old Timer', 'Mallard', ?, 'Released')", (days_ago(self.db, 900),))
        self.db.execute("INSERT INTO release_log (animal_id, release_date) VALUES (11, ?)",
                        (days_ago(self.db, 800),))
        run_file(self.db, "09_archive.sql")
        cursor = self.db.execute("INSERT INTO animals (name, species, intake_date) "
                                 "VALUES ('Newcomer', 'Mallard', date('now'))")
        self.assertEqual(cursor.lastrowid, 12)
        run_file(self.db, "09_archive.sql")
        self.assertIn(12, self.ids("animals"))


if __name__ == "__main__":
    unittest.main()