import sqlite3
import tempfile
import unittest
from pathlib import Path

from lead_agent.database import (
    delete_lead,
    get_lead,
    initialize_database,
    list_leads,
    save_lead,
)


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_search_update_and_delete_lead(self) -> None:
        lead_id = save_lead(
            {
                "company_name": "Acme Ltd",
                "contact_name": "A. Person",
                "email": "person@example.test",
            },
            db_path=self.db_path,
        )

        self.assertEqual(len(list_leads("acme", self.db_path)), 1)
        self.assertEqual(get_lead(lead_id, self.db_path)["company_name"], "Acme Ltd")

        save_lead(
            {"company_name": "Acme Ltd", "industry": "Software"},
            lead_id=lead_id,
            db_path=self.db_path,
        )
        self.assertEqual(get_lead(lead_id, self.db_path)["industry"], "Software")

        delete_lead(lead_id, self.db_path)
        self.assertIsNone(get_lead(lead_id, self.db_path))

    def test_company_name_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "Company name is required"):
            save_lead({}, db_path=self.db_path)

    def test_fit_score_must_be_in_range(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            save_lead(
                {"company_name": "Acme Ltd", "fit_score": 8},
                db_path=self.db_path,
            )


if __name__ == "__main__":
    unittest.main()
