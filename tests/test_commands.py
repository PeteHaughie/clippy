"""Command-token matching and memory staging."""

import unittest

from clippy.session import Session, command_matches


class CommandMatchesTests(unittest.TestCase):
    def test_exact_and_with_argument(self):
        self.assertTrue(command_matches("/help", "/help"))
        self.assertTrue(command_matches("/help me", "/help"))
        self.assertTrue(command_matches("/move top-left", "/move"))

    def test_prefix_collisions_do_not_match(self):
        self.assertFalse(command_matches("/helper", "/help"))
        self.assertFalse(command_matches("/exiting", "/exit"))
        self.assertFalse(command_matches("/skills", "/skill"))
        self.assertFalse(command_matches("/timeout", "/time"))

    def test_skills_and_skill_distinguish(self):
        self.assertTrue(command_matches("/skills", "/skills"))
        self.assertTrue(command_matches("/skill memory now", "/skill"))
        self.assertFalse(command_matches("/skills", "/skill"))


class MemoryStagingTests(unittest.TestCase):
    def _stub(self, *, enabled=True, every=3):
        s = Session.__new__(Session)
        s.memory_enabled = enabled
        s.memory_every_n_turns = every
        s._memory_batch = []
        s._curator_busy = False
        s._pending_user_text = None
        s.curated = []
        s._curate = lambda turns: s.curated.append(list(turns))
        return s

    def test_pairs_user_with_answer(self):
        s = self._stub()
        s._pending_user_text = "I like espresso"
        s._account_memory("Noted.")
        self.assertEqual(s._memory_batch, [("I like espresso", "Noted.")])
        self.assertIsNone(s._pending_user_text)

    def test_empty_answer_clears_staging_without_pairing(self):
        s = self._stub()
        s._pending_user_text = "hello"
        s._account_memory("")
        self.assertEqual(s._memory_batch, [])
        self.assertIsNone(s._pending_user_text)

    def test_batched_curation_fires_at_threshold(self):
        s = self._stub(every=2)
        for i in range(2):
            s._pending_user_text = f"u{i}"
            s._account_memory(f"a{i}")
        self.assertEqual(s.curated, [[("u0", "a0"), ("u1", "a1")]])
        self.assertEqual(s._memory_batch, [])

    def test_disabled_memory_still_clears_staging(self):
        s = self._stub(enabled=False)
        s._pending_user_text = "x"
        s._account_memory("y")
        self.assertEqual(s._memory_batch, [])
        self.assertIsNone(s._pending_user_text)


if __name__ == "__main__":
    unittest.main()
