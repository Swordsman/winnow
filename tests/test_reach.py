"""Unit tests for the resolution ladder (Resolver), reach handling in the
orchestrator loop, honest misses, and P3 promotion TTLs."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fold import Graph, parse, tokenize  # noqa: E402
from winnow import Resolver, extract_reaches, kebab, replay_client, run  # noqa: E402


def graph_from(src):
    g = Graph()
    for form in parse(tokenize(src)):
        if form[0] == "meta":
            g.set_meta(form)
        else:
            g.apply(form)
    return g


# turn 1 introduces material; turn 2 touches unrelated nodes so turn-1
# material cools; several nodes are dormant (answered/superseded) -> cold
LADDER_SRC = """
(delta :turn 1
  (term adjacency-matrix :gloss "NxN boolean" :aka ("the matrix"))
  (add (question q1 (represent hierarchy store) :status answered
       :by user :src t1))
  (add (claim c1 (stores-in links adjacency-matrix) :by user :src t1))
  (add (edge (answers c1 q1)))
  (add (decision d1 (implement store flat) :status superseded
       :by user :src t1)))
(delta :turn 2
  (add (claim c2 (has other thing) :by user :src t2))
  (add (claim c3 (has more stuff) :by user :src t2))
  (add (claim c4 (has yet more) :by user :src t2))
  (add (claim c5 (has still more) :by user :src t2))
  (add (claim c6 (has even more) :by user :src t2))
  (add (claim c7 (has final bits) :by user :src t2)))
"""


class TestKebab(unittest.TestCase):
    def test_normalizes(self):
        self.assertEqual(kebab("The Matrix!"), "the-matrix")
        self.assertEqual(kebab("FUSE layer"), "fuse-layer")


class TestExtractReaches(unittest.TestCase):
    def test_finds_reach_forms(self):
        text = ('(add (claim x1 (has a b) :by user :src t1))\n'
                '(reach adjacency-matrix)\n(reach the earlier decision)')
        self.assertEqual(extract_reaches(text),
                         [["adjacency-matrix"],
                          ["the", "earlier", "decision"]])

    def test_reach_never_in_ops(self):
        from winnow import extract_forms
        ops = extract_forms('(reach foo)(add (claim x1 (has a b)))')
        self.assertEqual([f[0] for f in ops], ["add"])


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.g = graph_from(LADDER_SRC)

    def test_resident_hit_rung_0_or_1(self):
        rung, hits = Resolver(self.g).resolve(["c7"])
        self.assertLessEqual(rung, 1)
        self.assertEqual(hits, ["c7"])

    def test_alias_resolves_via_registry(self):
        # "the matrix" is an :aka for adjacency-matrix; c1 mentions it
        rung, hits = Resolver(self.g).resolve(["the", "matrix",
                                               "the-matrix"])
        self.assertIn("c1", hits)

    def test_cold_hit_rung_3(self):
        rung, hits = Resolver(self.g).resolve(["flat"])
        self.assertEqual(rung, 3)
        self.assertEqual(hits, ["d1"])

    def test_honest_miss_rung_5(self):
        rung, hits = Resolver(self.g).resolve(["completely-unknown-thing"])
        self.assertEqual((rung, hits), (5, []))

    def test_llm_escalation_on_lexical_miss(self):
        # surface form matches nothing procedurally; the escalation
        # callable maps it to a registry term
        llm = lambda system, user: "adjacency-matrix\n"  # noqa: E731
        rung, hits = Resolver(self.g, llm=llm).resolve(["grid-thing"])
        self.assertIn("c1", hits)

    def test_widening_capped_by_profile(self):
        g = graph_from('(meta :profile (:widening-base 1))' + LADDER_SRC)
        r = Resolver(g)
        _, _, warm, _ = g.tiers()
        if warm:
            rung, hits = r.resolve([warm[0]])
            self.assertLessEqual(len(hits), 1)


class TestPromotionTTL(unittest.TestCase):
    def test_promote_puts_node_in_fire_then_expires(self):
        g = graph_from(LADDER_SRC)   # promotion-ttl default 2
        g.promote("d1")
        fire, *_ = g.tiers()
        self.assertIn("d1", fire)
        g.apply(parse(tokenize(
            "(delta :turn 3 (add (claim c8 (has a b) :by user :src t3)))"))[0])
        fire, *_ = g.tiers()
        self.assertIn("d1", fire)    # survives one delta
        g.apply(parse(tokenize(
            "(delta :turn 4 (add (claim c9 (has c d) :by user :src t4)))"))[0])
        fire, *_ = g.tiers()
        self.assertNotIn("d1", fire)  # ttl 2 exhausted

    def test_promote_unknown_id_is_noop(self):
        g = graph_from(LADDER_SRC)
        g.promote("zz")
        self.assertNotIn("zz", g.promotions)


TRANSCRIPT = """\
[t1 user]
Remember the flat store decision? It also causes lock contention.
"""

# extractor reaches for dormant material, gets a re-pass with pull
# results, then emits; one reach misses -> honest-miss question
FIXTURE = """\
(reach flat)
(reach the-phlogiston-design)
%%%
(add (claim x1 (causes flat lock-contention) :by user :src t1))
(add (edge (about x1 d1)))
%%%
(add (claim x1 (causes flat lock-contention) :by user :src t1))
(add (edge (about x1 d1)))
"""

SEED = LADDER_SRC


class TestReachLoop(unittest.TestCase):
    def test_reach_repass_miss_and_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            tp = os.path.join(d, "t.txt")
            fp = os.path.join(d, "f.txt")
            op = os.path.join(d, "out.wno")
            sp = os.path.join(d, "seed.txt")
            open(tp, "w").write(TRANSCRIPT)
            open(fp, "w").write(FIXTURE)
            open(sp, "w").write(SEED)
            g = run(tp, op, replay_client(fp), llm_normalize=True,
                    per_turn=True, verbose=False, seed=SEED)
            # the claim landed and links to the promoted dormant decision
            self.assertTrue(any(n["frame"] == "claim" and
                                "lock-contention" in str(n["payload"])
                                for n in g.nodes.values()))
            self.assertTrue(any(t == "about" and b == "d1"
                                for t, a, b in g.edges))
            # honest miss became an open question by the orchestrator
            miss = [n for n in g.nodes.values()
                    if n["frame"] == "question" and
                    "the-phlogiston-design" in str(n["payload"])]
            self.assertEqual(len(miss), 1)
            self.assertEqual(miss[0]["status"], "open")
            self.assertEqual(miss[0]["by"], "orchestrator")
            self.assertEqual(g.validate(), [])


if __name__ == "__main__":
    unittest.main()
