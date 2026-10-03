"""Judge ranking: winner selection, close margins, and pre-emit failures."""

import unittest

from drafthouse.critique import format_score_block, judge_candidates


def block(scores: list[int]) -> str:
    """A full 5-dim critique block from raw scores (order: PREEMIT_DIMENSIONS)."""
    return format_score_block(dict(zip(("philosophy", "hierarchy", "execution", "specificity", "restraint"), scores)))


class JudgeCandidatesTest(unittest.TestCase):
    def test_winner_by_composite(self):
        decision = judge_candidates(
            {"a": block([4, 4, 4, 4, 4]), "b": block([3, 3, 3, 3, 3]), "c": block([5, 5, 5, 5, 4])}
        )
        self.assertEqual(decision.winner, "c")
        self.assertFalse(decision.close)
        self.assertEqual(len(decision.candidates), 3)

    def test_close_margin_flags_handoff(self):
        # 4.0 vs 3.6 on the 1-5 composite: one average step apart.
        decision = judge_candidates(
            {"a": block([4, 4, 4, 4, 4]), "b": block([4, 4, 4, 4, 3])}
        )
        self.assertEqual(decision.winner, "a")
        self.assertTrue(decision.close)

    def test_failing_candidate_excluded_from_ranking(self):
        decision = judge_candidates(
            {
                "bad": block([2, 4, 4, 4, 4]),
                "good": block([4, 4, 4, 4, 4]),
                "better": block([5, 4, 4, 4, 4]),
            }
        )
        self.assertEqual(decision.winner, "better")
        # "better" and "good" are one dimension apart (4.2 vs 4.0) -> close.
        self.assertTrue(decision.close)
        by_name = {c["name"]: c for c in decision.candidates}
        self.assertFalse(by_name["bad"]["passes_preemit"])
        self.assertTrue(by_name["good"]["passes_preemit"])

    def test_all_failing_yields_no_winner(self):
        decision = judge_candidates({"a": block([2, 2, 4, 4, 4]), "b": block([3, 2, 4, 4, 4])})
        self.assertIsNone(decision.winner)
        self.assertFalse(decision.close)

    def test_to_dict_round_trips(self):
        decision = judge_candidates({"a": block([4, 4, 4, 4, 4]), "b": block([3, 3, 3, 3, 3])})
        payload = decision.to_dict()
        self.assertEqual(payload["winner"], "a")
        self.assertEqual(payload["candidates"][0]["composite"], 4.0)


if __name__ == "__main__":
    unittest.main()
