from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "resources/keywords/etb/etb_regression_keywords.resource").read_text(encoding="utf-8")


def block(name: str, next_name: str) -> str:
    return TEXT[TEXT.index(name + "\n"):TEXT.index(next_name + "\n")]


class MobileReviewTask4Contracts(unittest.TestCase):
    def assert_preparation_owned_by_try(self, body: str, case_marker: str):
        prepare = body.index("Prepare CIS State")
        self.assertLess(body.index("TRY"), prepare, case_marker + " preparation must be inside TRY")
        finally_pos = body.index("FINALLY")
        cleanup = body.index("Cleanup CIS State", finally_pos)
        self.assertGreater(cleanup, finally_pos)
        self.assertIn("Assert CIS Cleanup Policy", body[finally_pos:])

    def test_positive_preparation_is_inside_cleanup_lifecycle(self):
        self.assert_preparation_owned_by_try(block("Run ETB Positive Case", "Run ETB TC002 PDPA Case"), "positive")

    def test_tc002_preparation_is_inside_cleanup_lifecycle(self):
        body = block("Run ETB TC002 PDPA Case", "Run ETB Expected RGI Case")
        self.assert_preparation_owned_by_try(body, "tc002")
        self.assertIn("TC002_CLEANUP_FAILED", body)
        self.assertIn("PDPA_CLEANUP_FAILED", body)

    def test_rgi_preparation_is_inside_cleanup_lifecycle(self):
        self.assert_preparation_owned_by_try(block("Run ETB Expected RGI Case", "Run ETB Expected RGI After Laser Code"), "rgi")

    def test_rgi_after_laser_preparation_is_inside_cleanup_lifecycle(self):
        self.assert_preparation_owned_by_try(block("Run ETB Expected RGI After Laser Code", "Reset ETB Application To Landing"), "rgi_after_laser")


if __name__ == "__main__":
    unittest.main(verbosity=2)
