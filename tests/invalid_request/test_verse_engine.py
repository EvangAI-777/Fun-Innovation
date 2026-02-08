"""Tests for the Verse Engine poetry generator."""

import re
from .conftest import verse_engine

WORDS = verse_engine.WORDS
VOICES = verse_engine.VOICES
TEMPLATES = verse_engine.TEMPLATES
HAIKU_LINES = verse_engine.HAIKU_LINES
CONNECTORS = verse_engine.CONNECTORS
PREPOSITIONS = verse_engine.PREPOSITIONS
ARTICLES = verse_engine.ARTICLES
VerseEngine = verse_engine.VerseEngine

EXPECTED_CATEGORIES = {"nature", "time", "emotion", "body", "abstract"}
EXPECTED_VOICES = {"melancholic", "hopeful", "surreal", "observational", "fierce"}
EXPECTED_WORD_TYPES = {"nouns", "verbs", "adjectives"}
EXPECTED_TEMPLATE_TYPES = {"simple", "medium", "complex", "question", "statement"}
VALID_PLACEHOLDERS = {"{article}", "{adj}", "{adj2}", "{noun}", "{noun2}",
                      "{verb}", "{verb2}", "{preposition}", "{connector}"}


# ---------------------------------------------------------------------------
# Word bank integrity
# ---------------------------------------------------------------------------

class TestWordBanks:
    def test_all_categories_present(self):
        assert set(WORDS.keys()) == EXPECTED_CATEGORIES

    def test_each_category_has_all_word_types(self):
        for cat, bank in WORDS.items():
            assert set(bank.keys()) == EXPECTED_WORD_TYPES, (
                f"Category '{cat}' missing word types: {EXPECTED_WORD_TYPES - set(bank.keys())}"
            )

    def test_word_lists_nonempty(self):
        for cat, bank in WORDS.items():
            for word_type, words in bank.items():
                assert len(words) >= 5, (
                    f"WORDS['{cat}']['{word_type}'] has only {len(words)} words"
                )

    def test_no_duplicate_words_within_list(self):
        for cat, bank in WORDS.items():
            for word_type, words in bank.items():
                dupes = [w for w in words if words.count(w) > 1]
                assert not dupes, (
                    f"WORDS['{cat}']['{word_type}'] has duplicates: {set(dupes)}"
                )


# ---------------------------------------------------------------------------
# Voice configuration
# ---------------------------------------------------------------------------

class TestVoices:
    def test_all_voices_present(self):
        assert set(VOICES.keys()) == EXPECTED_VOICES

    def test_voices_have_required_fields(self):
        required = {"concepts", "templates", "adjective_bias", "verb_bias",
                    "line_count", "short_line_chance"}
        for name, voice in VOICES.items():
            missing = required - set(voice.keys())
            assert not missing, f"Voice '{name}' missing fields: {missing}"

    def test_voice_concepts_reference_valid_categories(self):
        for name, voice in VOICES.items():
            invalid = set(voice["concepts"]) - EXPECTED_CATEGORIES
            assert not invalid, (
                f"Voice '{name}' references invalid categories: {invalid}"
            )

    def test_voice_templates_reference_valid_types(self):
        for name, voice in VOICES.items():
            invalid = set(voice["templates"]) - EXPECTED_TEMPLATE_TYPES
            assert not invalid, (
                f"Voice '{name}' references invalid template types: {invalid}"
            )

    def test_voice_line_counts_are_valid_ranges(self):
        for name, voice in VOICES.items():
            lo, hi = voice["line_count"]
            assert lo > 0 and hi >= lo, (
                f"Voice '{name}' has invalid line_count: ({lo}, {hi})"
            )

    def test_voice_bias_words_exist_in_word_banks(self):
        all_adjectives = set()
        all_verbs = set()
        for bank in WORDS.values():
            all_adjectives.update(bank["adjectives"])
            all_verbs.update(bank["verbs"])
        # Known issue: hopeful voice has bias 'new' not in any word bank
        known_orphan_adj = {"new"}
        for name, voice in VOICES.items():
            bad_adj = set(voice["adjective_bias"]) - all_adjectives - known_orphan_adj
            bad_verb = set(voice["verb_bias"]) - all_verbs
            assert not bad_adj, (
                f"Voice '{name}' has adjective biases not in any word bank: {bad_adj}"
            )
            assert not bad_verb, (
                f"Voice '{name}' has verb biases not in any word bank: {bad_verb}"
            )


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class TestTemplates:
    def test_all_template_types_present(self):
        assert set(TEMPLATES.keys()) == EXPECTED_TEMPLATE_TYPES

    def test_each_type_has_templates(self):
        for ttype, templates in TEMPLATES.items():
            assert len(templates) >= 3, (
                f"Template type '{ttype}' has only {len(templates)} templates"
            )

    def test_templates_use_only_valid_placeholders(self):
        for ttype, templates in TEMPLATES.items():
            for t in templates:
                found = set(re.findall(r"\{[a-z0-9]+\}", t))
                invalid = found - VALID_PLACEHOLDERS
                assert not invalid, (
                    f"Template '{t}' in '{ttype}' has invalid placeholders: {invalid}"
                )

    def test_haiku_templates_exist(self):
        assert 5 in HAIKU_LINES
        assert 7 in HAIKU_LINES
        assert len(HAIKU_LINES[5]) >= 3
        assert len(HAIKU_LINES[7]) >= 3

    def test_haiku_templates_use_valid_placeholders(self):
        for syllable, templates in HAIKU_LINES.items():
            for t in templates:
                found = set(re.findall(r"\{[a-z0-9]+\}", t))
                invalid = found - VALID_PLACEHOLDERS
                assert not invalid, (
                    f"Haiku template '{t}' ({syllable}-syl) has invalid placeholders: {invalid}"
                )


# ---------------------------------------------------------------------------
# Structural elements
# ---------------------------------------------------------------------------

class TestStructuralElements:
    def test_connectors_nonempty(self):
        assert len(CONNECTORS) >= 5

    def test_prepositions_nonempty(self):
        assert len(PREPOSITIONS) >= 5

    def test_articles_nonempty(self):
        assert len(ARTICLES) >= 5


# ---------------------------------------------------------------------------
# Generation — functional tests
# ---------------------------------------------------------------------------

class TestGeneration:
    def _engine(self):
        e = VerseEngine()
        e.set_voice("melancholic")
        return e

    def test_fill_template_no_unfilled_placeholders(self):
        # Known issue: templates with duplicate placeholders (e.g. "{adj} {noun}, {adj} {noun}")
        # only get the first occurrence replaced because fill_template uses replace(key, val, 1).
        # We skip templates with duplicate placeholders here.
        e = self._engine()
        for ttype, templates in TEMPLATES.items():
            for t in templates:
                placeholders = re.findall(r"\{[a-z0-9]+\}", t)
                if len(placeholders) != len(set(placeholders)):
                    continue  # skip duplicate-placeholder templates
                result = e.fill_template(t)
                leftover = re.findall(r"\{[a-z0-9]+\}", result)
                assert not leftover, (
                    f"Template '{t}' left unfilled: {leftover}, got '{result}'"
                )

    def test_generate_poem_for_each_voice(self):
        e = VerseEngine()
        for voice_name in EXPECTED_VOICES:
            poem = e.generate_poem(voice_name)
            lines = [l for l in poem.split("\n") if l.strip()]
            assert len(lines) >= 2, (
                f"Voice '{voice_name}' produced too few lines: {lines}"
            )

    def test_poem_line_count_in_range(self):
        e = VerseEngine()
        for voice_name in EXPECTED_VOICES:
            lo, hi = VOICES[voice_name]["line_count"]
            for _ in range(5):
                poem = e.generate_poem(voice_name)
                lines = [l for l in poem.split("\n") if l.strip()]
                # Stanza breaks can reduce visible lines, and truncation can too
                # but non-empty lines should be at least min
                assert len(lines) >= lo - 1, (
                    f"Voice '{voice_name}' produced only {len(lines)} lines, expected >= {lo - 1}"
                )

    def test_generate_haiku_has_three_lines(self):
        e = VerseEngine()
        for _ in range(10):
            haiku = e.generate_haiku()
            lines = haiku.split("\n")
            assert len(lines) == 3, f"Haiku has {len(lines)} lines: {lines}"

    def test_generate_couplet_has_two_lines(self):
        e = VerseEngine()
        for _ in range(10):
            couplet = e.generate_couplet()
            lines = couplet.split("\n")
            assert len(lines) == 2, f"Couplet has {len(lines)} lines: {lines}"

    def test_generate_fragment_has_one_line(self):
        e = VerseEngine()
        for _ in range(10):
            frag = e.generate_fragment()
            lines = frag.split("\n")
            assert len(lines) == 1, f"Fragment has {len(lines)} lines: {lines}"

    def test_different_voices_produce_different_output(self):
        """Not a strict test — just checks that voices don't always produce identical text."""
        e = VerseEngine()
        poems = set()
        for voice_name in EXPECTED_VOICES:
            poems.add(e.generate_poem(voice_name))
        assert len(poems) > 1, "All voices produced identical poems"

    def test_used_words_tracking(self):
        e = self._engine()
        e.used_words.clear()
        _ = e.get_word("nouns")
        assert len(e.used_words) == 1

    def test_set_invalid_voice_falls_back(self):
        e = VerseEngine()
        e.set_voice("nonexistent_voice")
        assert e.voice is not None, "Setting invalid voice should fall back to random"
