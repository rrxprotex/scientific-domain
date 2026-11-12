"""Tests for scientific-domain/domain.py.

Every gate has a companion test showing the record is REFUSED without it. The
validator never repairs a record, so these assert refusal rather than rewriting.
Run: python tests.py  (or python -m unittest tests -v)
"""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOMAIN = HERE / "domain.py"
ONTOLOGY = HERE / "examples" / "ontology.songwriting.json"

spec = importlib.util.spec_from_file_location("domain", DOMAIN)
domain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain)
ONTO = domain.load_ontology(str(ONTOLOGY))
GENERIC = domain.load_ontology("generic")
_act_spec = importlib.util.spec_from_file_location("activate", HERE / "activate.py")
activate = importlib.util.module_from_spec(_act_spec)
_act_spec.loader.exec_module(activate)
_sem_spec = importlib.util.spec_from_file_location("semantic_grader", HERE / "evals" / "semantic.py")
semantic_grader = importlib.util.module_from_spec(_sem_spec)
_sem_spec.loader.exec_module(semantic_grader)


def base(**kw):
    rec = {
        "id": "LNK-001",
        "layer": "observation",
        "statement": "Dön geri dizesi her nakarat için üç kez geçer.",
        "domain": "songwriting",
        "scope": {"declared": True, "sources": ["ornek.cho"]},
        "evidence": [{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L6-L9"}],
        "evidence_class": "ARTIFACT",
        "representation": "PRESENT",
        "evidence_status": "OBSERVED",
        "term_id": None,
        "theory_ids": [],
        "rival_term_ids": [],
        "distinguishing_test": "",
        "theory_link_note": "",
        "mechanism": {},
        "claim_limit": "Yalnızca bu dosyadaki tekrar sayısını belirtir; dinleyici verisi yoktur.",
    }
    rec.update(kw)
    return rec


def term_rec(**kw):
    rec = base(
        layer="term",
        statement="The recurring section is a chorus rather than a refrain.",
        representation="UNDER_IMPLEMENTED",
        evidence_status="INFERRED",
        term_id="TERM-CHORUS",
        rival_term_ids=["TERM-REFRAIN"],
        distinguishing_test="A separate section boundary is marked; a refrain would be a returning line inside the verse.",
    )
    rec.update(kw)
    return rec


def theory_rec(**kw):
    rec = base(
        layer="theory",
        statement="The repetition in this lyric may be read through processing fluency.",
        representation="UNDER_IMPLEMENTED",
        evidence_status="HYPOTHESIS",
        evidence_class="MEASUREMENT",
        evidence=[],
        theory_ids=["THEORY-PROCESSING-FLUENCY"],
        theory_link_note="The fluency frame interprets the repetition count; it does not measure this listener.",
    )
    rec.update(kw)
    return rec


def mechanism_rec(**kw):
    rec = base(
        layer="mechanism",
        statement="Chorus repetition increases listener recall.",
        representation="UNKNOWN",
        evidence_status="HYPOTHESIS",
        evidence_class="COUNTERFACTUAL",
        evidence=[],
        theory_ids=["THEORY-PROCESSING-FLUENCY"],
        mechanism={
            "rivals": ["the same recall could come from melodic contour alone"],
            "falsifier": "If a non-repeated chorus is recalled equally often, the mechanism fails.",
        },
        claim_limit="Bu dosyada dinleyici verisi yoktur; yalnızca bir hipotezdir, bulgu değildir.",
    )
    rec.update(kw)
    return rec


def problems(rec, onto=ONTO):
    return "\n".join(domain.validate(rec, onto))


class TestOntology(unittest.TestCase):
    def test_shipped_ontology_validates(self):
        self.assertEqual(domain.check_ontology(ONTO), [])

    def test_relation_to_unknown_id_is_refused(self):
        onto = copy.deepcopy(ONTO)
        onto["relations"][0]["to"] = "THEORY-DOES-NOT-EXIST"
        self.assertTrue(any("undeclared id" in p for p in domain.check_ontology(onto)))

    def test_verified_source_without_locator_is_refused(self):
        onto = copy.deepcopy(ONTO)
        onto["theories"]["THEORY-MERE-EXPOSURE"]["sources"][0]["locator"] = ""
        self.assertTrue(any("locator" in p for p in domain.check_ontology(onto)))

    def test_unverified_source_allows_empty_locator(self):
        entry = ONTO["terms"]["TERM-AABA"]["sources"][0]
        self.assertEqual(entry["citation_status"], "UNVERIFIED")
        self.assertEqual(entry["locator"], "")
        self.assertEqual(domain.check_ontology(ONTO), [])

    def test_term_without_distinguishing_test_is_refused(self):
        onto = copy.deepcopy(ONTO)
        onto["terms"]["TERM-CHORUS"]["distinguishing_test"] = ""
        self.assertTrue(any("distinguishing_test" in p for p in domain.check_ontology(onto)))


class TestValidRecords(unittest.TestCase):
    def test_all_four_layers_have_valid_forms(self):
        for rec in (base(), term_rec(), theory_rec(), mechanism_rec()):
            self.assertEqual(domain.validate(rec, ONTO), [], rec["layer"])

    def test_unknown_record_passes(self):
        rec = base(representation="UNKNOWN", evidence_status="CANDIDATE", evidence=[],
                   claim_limit="Dinleyici verisi toplanmadı; bu kayıt bir etki iddiasını destekleyemez.")
        self.assertEqual(domain.validate(rec, ONTO), [])


class TestUniversalGates(unittest.TestCase):
    def test_absence_without_declared_scope_is_refused(self):
        rec = base(representation="NOT_REPRESENTED", evidence_status="CANDIDATE",
                   scope={"declared": False, "sources": ["ornek.cho"]}, evidence=[])
        self.assertIn("G3", problems(rec))

    def test_claim_limit_is_mandatory(self):
        self.assertIn("G0", problems(base(claim_limit="")))
        self.assertIn("G4", problems(base(claim_limit="n/a")))

    def test_credential_is_refused(self):
        self.assertIn("G10", problems(base(statement="token ghp_abcdefghijklmnopqrstuvwxyz0123456789")))

    def test_wrong_domain_ontology_is_refused(self):
        self.assertIn("G11", problems(base(domain="biomedicine")))

    def test_external_subject_cannot_be_observed_from_text(self):
        rec = base(statement="The hook is remembered by listeners.",
                   evidence_class="EXTERNAL_SUBJECT", representation="UNDER_IMPLEMENTED")
        self.assertIn("G6", problems(rec))

    def test_interpretive_can_never_be_observed(self):
        rec = base(statement="The second verse feels unresolved.",
                   evidence_class="INTERPRETIVE", representation="UNDER_IMPLEMENTED",
                   evidence=[{"kind": "interpretation", "ref": "reader-1"}])
        self.assertIn("can never be OBSERVED", problems(rec))

    def test_candidate_cannot_carry_a_verdict(self):
        self.assertIn("G9", problems(base(evidence_status="CANDIDATE", verdict="PASS",
                                          representation="UNKNOWN", evidence=[])))

    def test_duplicate_ids_and_unreadable_rows_fail_closed(self):
        self.assertIn("duplicate id", "\n".join(domain.check_records([base(), base()], ONTO)))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r.jsonl"
            path.write_text("{bad json}\n", encoding="utf-8")
            _, probs = domain.read_records(path)
            self.assertIn("unreadable JSON", "\n".join(probs))


class TestTermLayer(unittest.TestCase):
    def test_invented_term_is_refused(self):
        self.assertIn("T1", problems(term_rec(term_id="TERM-REPETITION-WITH-VARIATION")))

    def test_term_label_must_match_canonical_label(self):
        self.assertIn("T1", problems(term_rec(term_label="chorus-effect")))

    def test_term_needs_a_declared_rival(self):
        self.assertIn("T4", problems(term_rec(rival_term_ids=[])))

    def test_term_needs_distinguishing_test(self):
        self.assertIn("T4", problems(term_rec(distinguishing_test="")))

    def test_evidence_class_must_match_term(self):
        self.assertIn("T3", problems(term_rec(evidence_class="EXTERNAL_SUBJECT")))

    def test_observation_may_not_smuggle_a_term(self):
        self.assertIn("T2", problems(base(term_id="TERM-CHORUS")))

    def test_causal_wording_cannot_hide_in_observation(self):
        self.assertIn("T2", problems(base(statement="Repetition increases recall.")))


class TestTheoryLayer(unittest.TestCase):
    def test_theory_can_never_be_observed(self):
        self.assertIn("T5", problems(theory_rec(evidence_status="OBSERVED")))

    def test_theory_link_note_is_required(self):
        self.assertIn("T5", problems(theory_rec(theory_link_note="")))

    def test_unknown_theory_id_is_refused(self):
        self.assertIn("T1", problems(theory_rec(theory_ids=["THEORY-MADE-UP"])))

    def test_partial_citation_caps_status_at_candidate(self):
        rec = theory_rec(theory_ids=["THEORY-HOOK-APPROACH"], evidence_status="INFERRED")
        self.assertIn("T6", problems(rec))
        self.assertEqual(domain.validate(dict(rec, evidence_status="CANDIDATE"), ONTO), [])

    def test_unverified_citation_caps_status_at_candidate(self):
        onto = copy.deepcopy(ONTO)
        for src in onto["theories"]["THEORY-PROCESSING-FLUENCY"]["sources"]:
            src["citation_status"] = "UNVERIFIED"
            src["locator"] = ""
        self.assertIn("T6", problems(theory_rec(), onto))
        self.assertEqual(domain.validate(theory_rec(evidence_status="CANDIDATE"), onto), [])


class TestMechanismLayer(unittest.TestCase):
    def test_non_causal_statement_cannot_be_a_mechanism(self):
        self.assertIn("T7", problems(mechanism_rec(statement="The chorus repeats three times.")))

    def test_mechanism_needs_rivals_and_falsifier(self):
        self.assertIn("T7", problems(mechanism_rec(mechanism={"rivals": [], "falsifier": ""})))

    def test_mechanism_must_be_grounded_in_ontology(self):
        self.assertIn("T8", problems(mechanism_rec(theory_ids=[], term_id=None)))

    def test_observed_mechanism_needs_intervention(self):
        rec = mechanism_rec(evidence_status="OBSERVED")
        self.assertIn("intervention", problems(rec))
        fixed = mechanism_rec(
            evidence_status="OBSERVED",
            mechanism={
                "rivals": ["melodic contour alone"],
                "falsifier": "Equal recall without repetition would refute it.",
                "intervention": "Remove repetition while keeping melody fixed, then re-test recall.",
            },
            evidence=[{"kind": "intervention", "ref": "exp-1", "locator": "protocol v2"}],
        )
        self.assertEqual(domain.validate(fixed, ONTO), [], problems(fixed))


class TestCli(unittest.TestCase):
    def test_ontology_check_cli_passes(self):
        result = subprocess.run([sys.executable, str(DOMAIN), "ontology-check",
                                 "--ontology", "songwriting"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK ontology 'songwriting'", result.stdout)

    def test_terms_cli_lists_sources_and_status(self):
        result = subprocess.run([sys.executable, str(DOMAIN), "terms",
                                 "--ontology", "songwriting", "--kind", "theories",
                                 "--id", "THEORY-MERE-EXPOSURE"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Zajonc", result.stdout)
        self.assertIn("VERIFIED_BIBLIOGRAPHIC", result.stdout)
        self.assertIn("does NOT explain", result.stdout)

    def test_add_refuses_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "records.jsonl"
            bad = term_rec(term_id="TERM-INVENTED")
            result = subprocess.run(
                [sys.executable, str(DOMAIN), "add", "--ontology", "songwriting",
                 "--json", json.dumps(bad), "--file", str(out)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(out.exists())
            self.assertIn("nothing was written", result.stdout)

    def test_full_cycle_add_check_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "records.jsonl"
            for rec in (base(), term_rec(**{"id": "LNK-002"}),
                        theory_rec(**{"id": "LNK-003"}),
                        mechanism_rec(**{"id": "LNK-004"})):
                add = subprocess.run(
                    [sys.executable, str(DOMAIN), "add", "--ontology", "songwriting",
                     "--json", json.dumps(rec),
                     "--file", str(out)], capture_output=True, text=True)
                self.assertEqual(add.returncode, 0, add.stdout + add.stderr)
            check = subprocess.run([sys.executable, str(DOMAIN), "check", "--ontology", "songwriting",
                                    "--file", str(out)],
                                   capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            brief = subprocess.run([sys.executable, str(DOMAIN), "brief", "--ontology", "songwriting",
                                    "--file", str(out)],
                                   capture_output=True, text=True)
            self.assertEqual(brief.returncode, 0, brief.stdout + brief.stderr)
            self.assertIn("Canonical terms (1)", brief.stdout)
            self.assertIn("Theoretical frames (1)", brief.stdout)
            self.assertIn("Mechanism hypotheses (1)", brief.stdout)
            self.assertIn("claim limit", brief.stdout)

    def test_audit_reports_ungrounded_notes_as_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes = Path(tmp) / "notes.md"
            notes.write_text("# Notlar\nBu şarkıda nakarat tekrarı kesinlikle akılda kalıcılığı artırır.\n",
                             encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DOMAIN), "audit", "--notes", str(notes),
                 "--file", str(Path(tmp) / "missing.jsonl")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no canonical term or theory label", result.stdout)
            self.assertIn("CANDIDATE", result.stdout)


class TestRegistryAndRouting(unittest.TestCase):
    def test_index_registers_three_ontologies(self):
        idx = domain.load_index()
        self.assertEqual(sorted(idx["ontologies"]),
                         ["generic", "literary-rhetoric", "songwriting"])

    def test_domain_name_resolves_to_a_file(self):
        self.assertEqual(domain.load_ontology("songwriting")["domain"], "songwriting")
        self.assertEqual(domain.load_ontology("literary-rhetoric")["domain"], "literary-rhetoric")

    def test_unknown_domain_name_is_refused(self):
        with self.assertRaises(ValueError):
            domain.load_ontology("no-such-domain")

    def test_route_matches_a_registered_domain(self):
        d = domain.route_text("Analyze this lyric and relate it to songwriting theory")
        self.assertEqual(d["status"], "MATCHED")
        self.assertEqual(d["domain"], "songwriting")

    def test_route_no_match_falls_back_to_generic(self):
        d = domain.route_text("biyomedikal makaledeki iddiaları kanıt düzeylerine ayır")
        self.assertEqual(d["status"], "NO_MATCH")
        self.assertEqual(d["domain"], "generic")
        self.assertIn("do not invent", d["claim_limit"])

    def test_route_abstains_on_ambiguous_signal(self):
        d = domain.route_text("metaphor in a chorus")
        self.assertEqual(d["status"], "ABSTAIN")
        self.assertEqual(d["domain"], "generic")

    def test_all_registered_ontologies_validate(self):
        for name in domain.load_index()["ontologies"]:
            self.assertEqual(domain.check_ontology(domain.load_ontology(name)), [], name)

    def test_route_cli_emits_json(self):
        result = subprocess.run(
            [sys.executable, str(DOMAIN), "route", "--text", "analyze this lyric"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["domain"], "songwriting")


class TestGenericFallback(unittest.TestCase):
    def test_generic_accepts_an_observation_from_any_domain(self):
        rec = base(domain="biomedicine",
                   claim_limit="Yalnızca bu dosyadaki gözlemi kaydeder; hiçbir kanonik terim iddiası içermez.")
        self.assertEqual(domain.validate(rec, GENERIC), [])

    def test_generic_refuses_term_link(self):
        rec = term_rec(domain="biomedicine")
        self.assertIn("T9", problems(rec, GENERIC))

    def test_generic_refuses_theory_link(self):
        rec = theory_rec(domain="biomedicine")
        self.assertIn("T9", problems(rec, GENERIC))

    def test_generic_refuses_mechanism_link(self):
        rec = mechanism_rec(domain="biomedicine")
        self.assertIn("T9", problems(rec, GENERIC))


class TestActivation(unittest.TestCase):
    def test_activate_on_knowledge_work(self):
        d = activate.classify("Analyze this lyric and relate it to theory")
        self.assertEqual(d["decision"], "ACTIVATE")
        self.assertEqual(d["domain"], "songwriting")
        self.assertIn("claim_limit", d)

    def test_skip_on_routine_edit(self):
        self.assertEqual(activate.classify("fix a typo in the readme")["decision"], "SKIP")

    def test_skip_on_greeting(self):
        self.assertEqual(activate.classify("merhaba")["decision"], "SKIP")

    def test_abstain_when_no_signal(self):
        self.assertEqual(activate.classify("please take a look")["decision"], "ABSTAIN")

    def test_abstain_on_empty_prompt(self):
        self.assertEqual(activate.classify("")["decision"], "ABSTAIN")

    def test_hook_is_silent_on_skip(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "activate.py"), "--hook"],
            input=json.dumps({"prompt": "commit the changes"}),
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.stdout.strip(), "")

    def test_hook_injects_context_on_activate(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "activate.py"), "--hook"],
            input=json.dumps({"prompt": "Analyze this lyric and relate it to theory"}),
            capture_output=True, text=True, encoding="utf-8")
        payload = json.loads(result.stdout)
        self.assertIn("additionalContext", payload["hookSpecificOutput"])
        self.assertIn("songwriting", payload["hookSpecificOutput"]["additionalContext"])


class TestStrictConsistency(unittest.TestCase):
    def test_same_statement_with_conflicting_labels_is_contested(self):
        a = base()
        b = base(**{"id": "LNK-002", "evidence_status": "CANDIDATE",
                    "representation": "UNKNOWN", "evidence": []})
        found = domain.check_contradictions([a, b])
        self.assertTrue(any("CONTESTED" in p for p in found))

    def test_distinct_statements_are_not_contested(self):
        a = base()
        b = base(**{"id": "LNK-002", "statement": "The verse lines are identical."})
        self.assertEqual(domain.check_contradictions([a, b]), [])

    def test_strict_check_cli_on_example(self):
        result = subprocess.run(
            [sys.executable, str(DOMAIN), "check", "--file", "examples/ornek.jsonl",
             "--ontology", "songwriting", "--strict"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ontology_check_all_cli(self):
        result = subprocess.run(
            [sys.executable, str(DOMAIN), "ontology-check", "--all"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK 3 registered ontologies", result.stdout)

    def test_brief_does_not_repeat_a_statement(self):
        """A record listed in a layer must not appear a second time as an 'unknown' finding."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.jsonl"
            rec = base(**{"id": "X-001", "representation": "UNKNOWN",
                          "evidence_status": "CANDIDATE", "evidence": [],
                          "claim_limit": "Yalnızca bu dosya kapsamında bir kapsam beyanıdır."})
            out.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DOMAIN), "brief", "--file", str(out)],
                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count(rec["statement"]), 1)
            self.assertIn("## Coverage: unknown / absent under scope (1)", result.stdout)


class TestBuilders(unittest.TestCase):
    """Layer-first builders from build.py: valid by construction, refuse on gaps."""

    @classmethod
    def setUpClass(cls):
        _b_spec = importlib.util.spec_from_file_location("build", HERE / "build.py")
        cls.build = importlib.util.module_from_spec(_b_spec)
        _b_spec.loader.exec_module(cls.build)

    def test_observation_builder_passes_validate(self):
        rec = self.build.observation(
            "LNK-100", "The chorus repeats the same line three times.", "songwriting",
            scope={"declared": True, "sources": ["ornek.cho"]},
            evidence=[{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}],
            claim_limit="Only this file's repetition count; nothing about listener recall.")
        self.assertEqual(domain.validate(rec, ONTO), [])

    def test_observation_builder_refuses_missing_claim_limit(self):
        with self.assertRaises(ValueError):
            self.build.observation(
                "LNK-101", "The chorus repeats the same line three times.", "songwriting",
                scope={"declared": True, "sources": ["ornek.cho"]},
                evidence=[{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}])

    def test_observation_builder_refuses_prose_only_present(self):
        with self.assertRaises(ValueError):
            self.build.observation(
                "LNK-102", "The chorus repeats the same line three times.", "songwriting",
                scope={"declared": True, "sources": ["ornek.cho"]},
                evidence=[],
                claim_limit="Only this file's repetition count; nothing about recall.")

    def test_term_builder_passes_validate(self):
        rec = self.build.term(
            "LNK-103", "The recurring section is a chorus rather than a refrain.",
            "TERM-CHORUS", ["TERM-REFRAIN"],
            "A separate section boundary is marked; a refrain would be a returning line.", "songwriting",
            scope={"declared": True, "sources": ["ornek.cho"]},
            claim_limit="A form label only; it says nothing about listener recall.")
        self.assertEqual(domain.validate(rec, ONTO), [])

    def test_term_builder_refuses_missing_rival(self):
        with self.assertRaises(ValueError):
            self.build.term(
                "LNK-104", "The recurring section is a chorus.",
                "TERM-CHORUS", [],
                "A separate section boundary is marked in the source file.", "songwriting",
                scope={"declared": True, "sources": ["ornek.cho"]},
                claim_limit="A form label only; it says nothing about recall.")

    def test_theory_builder_passes_validate(self):
        rec = self.build.theory(
            "LNK-105", "The repetition may be read through processing fluency.",
            ["THEORY-PROCESSING-FLUENCY"],
            "The fluency frame interprets the repetition count; it does not measure this listener.", "songwriting",
            scope={"declared": True, "sources": ["ornek.cho"]},
            claim_limit="An interpretive frame; no listener measurement was made here.")
        self.assertEqual(domain.validate(rec, ONTO), [])

    def test_mechanism_builder_passes_validate(self):
        rec = self.build.mechanism(
            "LNK-106", "Chorus repetition increases listener recall.",
            ["the same recall could come from melodic contour alone"],
            "If a non-repeated chorus is recalled equally often, the mechanism fails.", "songwriting",
            theory_ids=["THEORY-PROCESSING-FLUENCY"],
            scope={"declared": True, "sources": ["ornek.cho"]},
            claim_limit="Only a hypothesis; no listener data was collected in this file.")
        self.assertEqual(domain.validate(rec, ONTO), [])

    def test_mechanism_builder_refuses_non_causal_statement(self):
        with self.assertRaises(ValueError):
            self.build.mechanism(
                "LNK-107", "The chorus repeats three times.",
                ["melodic contour alone"],
                "If a non-repeated chorus is recalled equally often, the mechanism fails.", "songwriting",
                theory_ids=["THEORY-PROCESSING-FLUENCY"],
                scope={"declared": True, "sources": ["ornek.cho"]},
                claim_limit="Only a hypothesis; no listener data was collected in this file.")

    def test_mechanism_builder_refuses_ungrounded(self):
        with self.assertRaises(ValueError):
            self.build.mechanism(
                "LNK-108", "Chorus repetition increases listener recall.",
                ["melodic contour alone"],
                "If a non-repeated chorus is recalled equally often, the mechanism fails.", "songwriting",
                scope={"declared": True, "sources": ["ornek.cho"]},
                claim_limit="Only a hypothesis; no listener data was collected in this file.")

    def test_to_jsonl_round_trips(self):
        rec = self.build.observation(
            "LNK-109", "The chorus repeats the same line three times.", "songwriting",
            scope={"declared": True, "sources": ["ornek.cho"]},
            evidence=[{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}],
            claim_limit="Only this file's repetition count; nothing about recall.")
        line = self.build.to_jsonl([rec])
        self.assertEqual(json.loads(line)["id"], "LNK-109")


class TestProfiles(unittest.TestCase):
    """--profile relaxes field-length minimums only, never the epistemic gates."""

    def test_strict_default_matches_original_behaviour(self):
        rec = theory_rec(theory_link_note="too short")
        self.assertIn("T5", problems(rec))

    def test_research_profile_accepts_shorter_note(self):
        rec = theory_rec(theory_link_note="frame applies here")
        self.assertEqual(domain.validate(rec, ONTO, profile="research"), [])

    def test_research_profile_still_refuses_observed_theory(self):
        rec = theory_rec(evidence_status="OBSERVED")
        self.assertIn("T5", "\n".join(domain.validate(rec, ONTO, profile="research")))

    def test_lite_profile_still_refuses_unverified_theory_cap(self):
        rec = theory_rec(theory_ids=["THEORY-HOOK-APPROACH"], evidence_status="INFERRED",
                         theory_link_note="x")
        self.assertIn("T6", "\n".join(domain.validate(rec, ONTO, profile="lite")))

    def test_unknown_profile_falls_back_to_strict(self):
        rec = theory_rec(theory_link_note="too short")
        self.assertIn("T5", "\n".join(domain.validate(rec, ONTO, profile="no-such")))


class TestConsent(unittest.TestCase):
    """Domain selection is a human decision: generic until the user confirms."""

    def test_generic_is_the_default_until_confirmed(self):
        import os
        old = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                self.assertEqual(domain.effective_ontology(None), "ontology.generic.json")
            finally:
                os.chdir(old)

    def test_use_records_the_users_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            use = subprocess.run(
                [sys.executable, str(DOMAIN), "use", "--ontology", "songwriting"],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(use.returncode, 0, use.stdout + use.stderr)
            sel = json.loads((Path(tmp) / "domain.config.json").read_text(encoding="utf-8"))
            self.assertEqual(sel["domain"], "songwriting")
            self.assertEqual(sel["confirmed_by"], "user")

    def test_term_link_refused_without_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "records.jsonl"
            result = subprocess.run(
                [sys.executable, str(DOMAIN), "add", "--json", json.dumps(term_rec()),
                 "--file", str(out)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(out.exists())
            self.assertIn("T9", result.stdout)

    def test_confirmed_domain_is_used_without_explicit_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "records.jsonl"
            use = subprocess.run(
                [sys.executable, str(DOMAIN), "use", "--ontology", "songwriting"],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(use.returncode, 0, use.stdout + use.stderr)
            add = subprocess.run(
                [sys.executable, str(DOMAIN), "add", "--json", json.dumps(term_rec()),
                 "--file", str(out)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(add.returncode, 0, add.stdout + add.stderr)
            self.assertTrue(out.exists())


class TestAttention(unittest.TestCase):
    """attention.py: deterministic weighted domain scoring - proposal with evidence."""

    @classmethod
    def setUpClass(cls):
        _a_spec = importlib.util.spec_from_file_location("attention", HERE / "attention.py")
        cls.att = importlib.util.module_from_spec(_a_spec)
        _a_spec.loader.exec_module(cls.att)

    def test_worked_prompt_attends_to_songwriting(self):
        r = self.att.attend(text="Analyze this lyric and relate the repetition to songwriting theory")
        self.assertEqual(r["status"], "MATCHED")
        self.assertEqual(r["domain"], "songwriting")
        self.assertIn(r["confidence"], ("high", "medium"))
        self.assertTrue(r["user_confirmation_required"])
        self.assertIn("keywords", r["evidence"]["songwriting"])

    def test_close_candidates_abstain(self):
        r = self.att.attend(text="metaphor in a chorus")
        self.assertEqual(r["status"], "ABSTAIN")
        self.assertEqual(r["domain"], "generic")

    def test_no_signal_is_no_match(self):
        r = self.att.attend(text="qqq zzz xyz abc def")
        self.assertEqual(r["status"], "NO_MATCH")
        self.assertEqual(r["domain"], "generic")
        self.assertEqual(r["attention"], {})

    def test_material_filenames_count_as_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "demo.cho").write_text("x", encoding="utf-8")
            r = self.att.attend(text="qqq zzz", directory=tmp)
            self.assertEqual(r["status"], "MATCHED")
            self.assertEqual(r["domain"], "songwriting")
            self.assertIn("demo.cho", r["evidence"]["songwriting"]["material_files"])

    def test_store_continuity_is_explained(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "s.jsonl"
            store.write_text(
                json.dumps({"domain": "songwriting"}) + "\n" +
                json.dumps({"domain": "songwriting"}) + "\n", encoding="utf-8")
            r = self.att.attend(text="qqq zzz", store=store)
            self.assertEqual(r["domain"], "songwriting")
            self.assertEqual(r["evidence"]["songwriting"]["store_records"], 2)


class TestCausalityScreen(unittest.TestCase):
    """Stage-2 negation screen (second review, finding A): negated causality is
    not a causal claim; a causal claim may not hide behind a trailing negation."""

    def test_negated_causality_is_not_forced_into_mechanism(self):
        rec = base(statement="The changed line does not increase listener recall.")
        self.assertEqual(problems(rec), "")

    def test_trailing_negation_still_flags_causality(self):
        rec = base(statement="Repetition increases recall, not the melody.")
        self.assertIn("T2", problems(rec))

    def test_hedged_modality_is_still_causal(self):
        self.assertTrue(domain.is_causal("Repetition may increase recall."))
        self.assertFalse(domain.is_causal("Repetition does not increase recall."))

    def test_grader_locator_rule_rejects_evidence_free_present_observation(self):
        rec = base(evidence=[])
        self.assertFalse(semantic_grader.rule_observation_has_locator(rec))

    def test_grader_locator_rule_allows_absence_under_declared_scope(self):
        rec = base(representation="NOT_REPRESENTED", evidence_status="CANDIDATE",
                   evidence=[],
                   claim_limit="Absence in this file only; nothing beyond this scope.")
        self.assertTrue(semantic_grader.rule_observation_has_locator(rec))


if __name__ == "__main__":
    unittest.main(verbosity=2)
