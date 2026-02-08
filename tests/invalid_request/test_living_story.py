"""Tests for the Living Story personality tracking system."""

import pytest
from .conftest import living_story

Personality = living_story.Personality
LivingStory = living_story.LivingStory

ALL_TRAITS = ["curious", "cautious", "bold", "kind", "detached", "honest", "deceptive"]


# ---------------------------------------------------------------------------
# Personality class
# ---------------------------------------------------------------------------

class TestPersonality:
    def test_initial_traits_are_zero(self):
        p = Personality()
        for trait in ALL_TRAITS:
            assert p.traits[trait] == 0

    def test_all_expected_traits_exist(self):
        p = Personality()
        assert set(p.traits.keys()) == set(ALL_TRAITS)

    def test_initial_choices_zero(self):
        p = Personality()
        assert p.choices_made == 0

    def test_add_increments_trait(self):
        p = Personality()
        p.add("curious")
        assert p.traits["curious"] == 1
        assert p.choices_made == 1

    def test_add_custom_amount(self):
        p = Personality()
        p.add("bold", 3)
        assert p.traits["bold"] == 3

    def test_add_invalid_trait_ignored(self):
        p = Personality()
        p.add("nonexistent")
        assert p.choices_made == 0

    def test_dominant_trait_none_when_no_choices(self):
        p = Personality()
        assert p.dominant_trait() is None

    def test_dominant_trait_correct(self):
        p = Personality()
        p.add("kind", 5)
        p.add("bold", 2)
        p.add("curious", 1)
        assert p.dominant_trait() == "kind"

    def test_has_trait_below_threshold(self):
        p = Personality()
        p.add("cautious", 1)
        assert not p.has_trait("cautious", threshold=2)

    def test_has_trait_at_threshold(self):
        p = Personality()
        p.add("cautious", 2)
        assert p.has_trait("cautious", threshold=2)

    def test_has_trait_above_threshold(self):
        p = Personality()
        p.add("cautious", 5)
        assert p.has_trait("cautious", threshold=2)

    def test_remember_stores_memories(self):
        p = Personality()
        p.remember("read the warning")
        p.remember("helped the figure")
        assert len(p.memories) == 2
        assert "read the warning" in p.memories

    def test_get_tendency_when_no_choices(self):
        p = Personality()
        assert p.get_tendency() == "uncertain"

    def test_get_tendency_for_each_trait(self):
        for trait in ALL_TRAITS:
            p = Personality()
            p.add(trait, 5)
            tendency = p.get_tendency()
            assert tendency != "uncertain", (
                f"Trait '{trait}' returned 'uncertain' as tendency"
            )
            assert isinstance(tendency, str)
            assert len(tendency) > 5  # should be a real description


# ---------------------------------------------------------------------------
# LivingStory initial state
# ---------------------------------------------------------------------------

class TestLivingStoryState:
    def test_initial_state(self):
        s = LivingStory()
        assert s.name is None
        assert s.found_the_door is False
        assert s.helped_the_figure is False
        assert s.took_the_key is False
        assert s.lied_to_voice is False

    def test_player_is_personality(self):
        s = LivingStory()
        assert isinstance(s.player, Personality)

    def test_story_has_all_scene_methods(self):
        s = LivingStory()
        scenes = ["intro", "the_waking", "the_corridor", "the_figure",
                   "the_door", "the_voice", "the_ending"]
        for scene in scenes:
            assert hasattr(s, scene), f"LivingStory missing scene method: {scene}"
            assert callable(getattr(s, scene))


# ---------------------------------------------------------------------------
# Personality integration scenarios
# ---------------------------------------------------------------------------

class TestPersonalityScenarios:
    """Test that the personality system produces coherent results for story paths."""

    def test_kind_playthrough(self):
        p = Personality()
        p.add("kind", 5)
        p.add("curious", 2)
        p.remember("helped the figure, received the key")
        assert p.dominant_trait() == "kind"
        assert p.has_trait("kind", 3)
        assert "one who cares" in p.get_tendency()

    def test_bold_playthrough(self):
        p = Personality()
        p.add("bold", 4)
        p.add("bold", 2)
        p.remember("walked through darkness")
        p.remember("demanded the key")
        assert p.dominant_trait() == "bold"
        assert len(p.memories) == 2

    def test_deceptive_playthrough(self):
        p = Personality()
        p.add("deceptive", 3)
        p.add("cautious", 1)
        assert p.dominant_trait() == "deceptive"
        assert "hidden" in p.get_tendency()

    def test_mixed_traits_picks_highest(self):
        p = Personality()
        p.add("curious", 3)
        p.add("cautious", 3)
        p.add("honest", 4)
        assert p.dominant_trait() == "honest"
