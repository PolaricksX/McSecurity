import tempfile
import unittest
from pathlib import Path

from password_manager.generator import generate_password
from password_manager.vault import Vault


class VaultTests(unittest.TestCase):
    def test_roundtrip_and_wrong_password(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "v.json"
            v = Vault(path, "master")
            v.add("site", "me", "pw")
            v.save()
            self.assertEqual(Vault(path, "master").get("site")["password"], "pw")
            self.assertNotIn("pw", path.read_text())
            with self.assertRaises(ValueError):
                Vault(path, "wrong")

    def test_generator(self):
        pw = generate_password(20)
        self.assertEqual(len(pw), 20)
        with self.assertRaises(ValueError):
            generate_password(4)


if __name__ == "__main__":
    unittest.main()
