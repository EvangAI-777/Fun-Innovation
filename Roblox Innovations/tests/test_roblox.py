"""
Static analysis tests for Roblox Luau projects.

Since Luau scripts can't run outside Roblox Studio, these tests parse
the source files as text and validate structure, conventions, and known
bad patterns. This catches the same class of bugs the v1.0.3 manual
audit found (deprecated APIs, missing fields, architectural drift)
but automatically, on every push.
"""

import re
from pathlib import Path

import pytest

ROBLOX_DIR = Path(__file__).resolve().parent.parent

PROJECTS = [
    "Academic Planner Study Hub",
    "Ecosystem Survival",
    "Flow Field Obby",
    "Generative Music Rooms",
    "Living Story RPG",
    "Notes Organizer Bulletin Board",
    "Verse Engine Skywriting",
]

# Each project must have exactly these four roles
ROLE_SUFFIXES = {"Config", "Client", "Server"}
# Plus one "core" module (Manager/Engine/Generator) — name varies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def luau_files(project: str) -> list[Path]:
    return sorted((ROBLOX_DIR / project).glob("*.luau"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Architecture conformance
# ---------------------------------------------------------------------------

class TestArchitecture:
    """Every project follows the 4-script pattern."""

    @pytest.mark.parametrize("project", PROJECTS)
    def test_has_four_luau_files(self, project: str):
        files = luau_files(project)
        assert len(files) == 4, (
            f"{project} has {len(files)} .luau files, expected 4: "
            f"{[f.name for f in files]}"
        )

    @pytest.mark.parametrize("project", PROJECTS)
    def test_has_config(self, project: str):
        names = {f.stem for f in luau_files(project)}
        configs = [n for n in names if n.endswith("Config")]
        assert len(configs) == 1, f"{project}: expected 1 Config, got {configs}"

    @pytest.mark.parametrize("project", PROJECTS)
    def test_has_server(self, project: str):
        names = {f.stem for f in luau_files(project)}
        servers = [n for n in names if n.endswith("Server")]
        assert len(servers) == 1, f"{project}: expected 1 Server, got {servers}"

    @pytest.mark.parametrize("project", PROJECTS)
    def test_has_client(self, project: str):
        names = {f.stem for f in luau_files(project)}
        clients = [n for n in names if n.endswith("Client")]
        assert len(clients) == 1, f"{project}: expected 1 Client, got {clients}"

    @pytest.mark.parametrize("project", PROJECTS)
    def test_has_core_module(self, project: str):
        names = {f.stem for f in luau_files(project)}
        core = [n for n in names
                if not (n.endswith("Config") or n.endswith("Server") or n.endswith("Client"))]
        assert len(core) == 1, f"{project}: expected 1 core module, got {core}"

    @pytest.mark.parametrize("project", PROJECTS)
    def test_config_returns_table(self, project: str):
        config_file = next(f for f in luau_files(project) if f.stem.endswith("Config"))
        src = read(config_file)
        assert re.search(r"^return\s+\w+", src, re.MULTILINE), (
            f"{config_file.name} doesn't end with 'return <table>'"
        )

    @pytest.mark.parametrize("project", PROJECTS)
    def test_core_module_returns_table(self, project: str):
        core_file = next(
            f for f in luau_files(project)
            if not (f.stem.endswith("Config") or f.stem.endswith("Server") or f.stem.endswith("Client"))
        )
        src = read(core_file)
        assert re.search(r"^return\s+\w+", src, re.MULTILINE), (
            f"{core_file.name} doesn't end with 'return <table>'"
        )


# ---------------------------------------------------------------------------
# Deprecated / dangerous API detection
# ---------------------------------------------------------------------------

DEPRECATED_PATTERNS = [
    (r"(?<!task\.)(?<!\w)wait\s*\(", "Use task.wait() instead of wait()"),
    (r"(?<!task\.)(?<!\w)spawn\s*\(", "Use task.spawn() instead of spawn()"),
    (r"(?<!task\.)(?<!\w)delay\s*\(", "Use task.delay() instead of delay()"),
    (r"(?<!os\.)(?<!\w)tick\s*\(", "Use os.clock() instead of tick()"),
    (r":connect\s*\(", "Use :Connect() (capital C) — lowercase is deprecated"),
]


class TestDeprecatedAPIs:
    """Catch deprecated Roblox APIs that should have been migrated."""

    @pytest.mark.parametrize("project", PROJECTS)
    def test_no_deprecated_apis(self, project: str):
        violations = []
        for path in luau_files(project):
            src = read(path)
            for line_num, line in enumerate(src.splitlines(), 1):
                # Skip comments
                stripped = line.lstrip()
                if stripped.startswith("--"):
                    continue
                for pattern, msg in DEPRECATED_PATTERNS:
                    if re.search(pattern, line):
                        violations.append(f"  {path.name}:{line_num}: {msg}")
        assert not violations, (
            f"{project} has deprecated API usage:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# Config value sanity checks
# ---------------------------------------------------------------------------

class TestConfigSanity:
    """Basic sanity: configs define expected fields, values are reasonable."""

    @pytest.mark.parametrize("project", PROJECTS)
    def test_config_not_empty(self, project: str):
        config_file = next(f for f in luau_files(project) if f.stem.endswith("Config"))
        src = read(config_file)
        # Should have at least a few assignments
        assignments = re.findall(r"Config\.\w+\s*=", src)
        assert len(assignments) >= 3, (
            f"{config_file.name} has only {len(assignments)} Config fields — suspiciously few"
        )

    @pytest.mark.parametrize("project", PROJECTS)
    def test_no_hardcoded_player_ids(self, project: str):
        """Player IDs in config files are a security/portability smell."""
        for path in luau_files(project):
            src = read(path)
            # Roblox user IDs are large integers, often in game:GetService("Players"):GetPlayerByUserId()
            # We flag hardcoded numeric IDs > 6 digits in config files
            if path.stem.endswith("Config"):
                matches = re.findall(r"\b\d{7,}\b", src)
                assert not matches, (
                    f"{path.name} contains hardcoded large numbers that might be player IDs: {matches}"
                )


# ---------------------------------------------------------------------------
# Cross-module references
# ---------------------------------------------------------------------------

class TestCrossReferences:
    """Server and Client scripts should require their Config and core module."""

    @pytest.mark.parametrize("project", PROJECTS)
    def test_server_requires_config(self, project: str):
        server_file = next(f for f in luau_files(project) if f.stem.endswith("Server"))
        config_name = next(f.stem for f in luau_files(project) if f.stem.endswith("Config"))
        src = read(server_file)
        assert config_name in src, (
            f"{server_file.name} doesn't reference {config_name}"
        )

    @pytest.mark.parametrize("project", PROJECTS)
    def test_server_requires_core(self, project: str):
        server_file = next(f for f in luau_files(project) if f.stem.endswith("Server"))
        core_name = next(
            f.stem for f in luau_files(project)
            if not (f.stem.endswith("Config") or f.stem.endswith("Server") or f.stem.endswith("Client"))
        )
        src = read(server_file)
        assert core_name in src, (
            f"{server_file.name} doesn't reference {core_name}"
        )

    @pytest.mark.parametrize("project", PROJECTS)
    def test_client_requires_config(self, project: str):
        client_file = next(f for f in luau_files(project) if f.stem.endswith("Client"))
        config_name = next(f.stem for f in luau_files(project) if f.stem.endswith("Config"))
        src = read(client_file)
        # Client might reference config directly or through a remote; check for name presence
        assert config_name in src, (
            f"{client_file.name} doesn't reference {config_name}"
        )


# ---------------------------------------------------------------------------
# Header / documentation checks
# ---------------------------------------------------------------------------

class TestDocumentation:
    """Every file should have a module header comment."""

    @pytest.mark.parametrize("project", PROJECTS)
    def test_all_files_have_headers(self, project: str):
        missing = []
        for path in luau_files(project):
            src = read(path)
            # Should start with --[[ or -- within first 5 lines
            first_lines = "\n".join(src.splitlines()[:5])
            if not re.search(r"^--", first_lines, re.MULTILINE):
                missing.append(path.name)
        assert not missing, (
            f"{project} files missing header comments: {missing}"
        )


# ---------------------------------------------------------------------------
# Template integrity (PoetryEngine-specific)
# ---------------------------------------------------------------------------

class TestPoetryEngine:
    """Validate PoetryEngine template placeholders and word banks."""

    @pytest.fixture
    def engine_src(self) -> str:
        path = ROBLOX_DIR / "Verse Engine Skywriting" / "PoetryEngine.luau"
        return read(path)

    def test_templates_use_valid_placeholders(self, engine_src: str):
        valid = {"{article}", "{adj}", "{adj2}", "{noun}", "{noun2}",
                 "{verb}", "{verb2}", "{preposition}", "{connector}"}
        known = {"{noun}", "{adj}", "{verb}", "{article}", "{preposition}"}
        # Only check quoted strings that contain a known template placeholder
        quoted_strings = re.findall(r'"([^"]*)"', engine_src)
        placeholders = set()
        for s in quoted_strings:
            found = set(re.findall(r"\{[a-z0-9]+\}", s))
            if found & known:  # only if it looks like a real template
                placeholders.update(found)
        invalid = placeholders - valid
        assert not invalid, f"Unknown template placeholders: {invalid}"

    def test_all_word_bank_categories_have_required_types(self, engine_src: str):
        # Each WORDS category should have nouns, verbs, adjectives
        categories = re.findall(r"(\w+)\s*=\s*\{[^}]*nouns\s*=", engine_src)
        assert len(categories) == 5, f"Expected 5 word categories, got {len(categories)}: {categories}"

    def test_all_voices_defined(self, engine_src: str):
        voices = re.findall(r"(\w+)\s*=\s*\{\s*\n?\s*concepts\s*=", engine_src)
        expected = {"melancholic", "hopeful", "surreal", "observational", "fierce"}
        assert set(voices) == expected, f"Voice mismatch: got {set(voices)}, expected {expected}"

    def test_voice_concepts_reference_valid_categories(self, engine_src: str):
        # Extract concept lists from voices
        concept_refs = re.findall(r'concepts\s*=\s*\{([^}]+)\}', engine_src)
        valid_categories = {"nature", "time", "emotion", "body", "abstract"}
        for concept_list in concept_refs:
            concepts = re.findall(r'"(\w+)"', concept_list)
            invalid = set(concepts) - valid_categories
            assert not invalid, f"Voice references invalid word categories: {invalid}"
