"""
Tests for the Omni Writer.

Two categories:
  1. Structural tests -- validate the HTML file contains all required UI elements,
     accessibility tags, responsive design markers, and zero dependencies.
  2. Logic reference tests -- Python implementations of key algorithms used in the JS
     (word count, reading time, HTML-to-markdown conversion).
"""

import math
import os
import re
import pytest

# ════════════════════════════════════════════════════
#  PATHS
# ════════════════════════════════════════════════════

HTML_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "OMNI INNOVATIONS",
    "Omni Writer",
    "omni-writer.html",
)

WRITEME_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "OMNI INNOVATIONS",
    "Omni Writer",
    "WRITEME.md",
)

JSON_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "OMNI INNOVATIONS",
    "Omni Writer",
    "Omni Writer.json",
)


# ════════════════════════════════════════════════════
#  FIXTURES
# ════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def html():
    with open(HTML_PATH, encoding="utf-8") as f:
        return f.read()


# ════════════════════════════════════════════════════
#  STRUCTURAL TESTS
# ════════════════════════════════════════════════════


class TestFileExistence:
    """Verify all Omni Writer files are present."""

    def test_html_exists(self):
        assert os.path.isfile(HTML_PATH), "omni-writer.html must exist"

    def test_writeme_exists(self):
        assert os.path.isfile(WRITEME_PATH), "WRITEME.md must exist"

    def test_json_exists(self):
        assert os.path.isfile(JSON_PATH), "Omni Writer.json must exist in the subdirectory"


class TestStructure:
    """Validate the HTML file's structure and completeness."""

    def test_is_valid_html5(self, html):
        assert html.strip().startswith("<!DOCTYPE html>"), "must be HTML5"

    def test_has_viewport_meta(self, html):
        assert 'name="viewport"' in html, "must have responsive viewport meta tag"

    def test_has_title(self, html):
        m = re.search(r"<title>(.+?)</title>", html)
        assert m, "must have a <title>"
        assert "omni writer" in m.group(1).lower()

    def test_has_description_meta(self, html):
        assert 'name="description"' in html, "must have a description meta tag"

    def test_has_theme_color(self, html):
        assert 'name="theme-color"' in html, "must have a theme-color meta tag"

    def test_has_starfield_canvas(self, html):
        assert 'id="starfield"' in html, "must have starfield background canvas"

    def test_has_writing_canvas(self, html):
        assert 'id="writingCanvas"' in html, "must have writing canvas"
        assert 'contenteditable="true"' in html, "writing canvas must be contentEditable"

    def test_has_story_list(self, html):
        assert 'id="storyList"' in html, "must have story list sidebar"

    def test_has_toolbar(self, html):
        assert 'id="toolbar"' in html, "must have formatting toolbar"

    def test_has_formatting_commands(self, html):
        for cmd in ["bold", "italic", "underline"]:
            assert f'data-cmd="{cmd}"' in html, f"must have {cmd} toolbar button"

    def test_has_heading_blocks(self, html):
        for tag in ["h1", "h2", "h3"]:
            assert f'data-block="{tag}"' in html, f"must have {tag} block button"

    def test_has_chapter_bar(self, html):
        assert 'id="chapterBar"' in html, "must have chapter bar"

    def test_has_chapter_tabs(self, html):
        assert 'id="chapterTabs"' in html, "must have chapter tabs container"

    def test_has_add_chapter_button(self, html):
        assert 'id="addChapterBtn"' in html, "must have add chapter button"

    def test_has_stats_bar(self, html):
        assert 'id="statsBar"' in html, "must have stats bar"

    def test_has_word_count(self, html):
        assert 'id="wordCount"' in html, "must have word count element"

    def test_has_char_count(self, html):
        assert 'id="charCount"' in html, "must have character count element"

    def test_has_export_modal(self, html):
        assert 'id="exportModal"' in html, "must have export modal"

    def test_has_export_formats(self, html):
        for fmt in ["txt", "md", "html"]:
            assert f'data-export="{fmt}"' in html, f"must support {fmt} export"

    def test_has_new_story_modal(self, html):
        assert 'id="newStoryModal"' in html, "must have new story modal"

    def test_has_delete_modal(self, html):
        assert 'id="deleteModal"' in html, "must have delete confirmation modal"

    def test_has_save_button(self, html):
        assert 'id="saveBtn"' in html, "must have save button"

    def test_has_export_button(self, html):
        assert 'id="exportBtn"' in html, "must have export button"

    def test_has_search_input(self, html):
        assert 'id="searchInput"' in html, "must have search input"

    def test_has_keyboard_support(self, html):
        assert "keydown" in html, "must handle keyboard events"

    def test_responsive_media_queries(self, html):
        assert "@media" in html, "must have media queries"
        assert "max-width:" in html, "must have responsive breakpoints"

    def test_all_css_is_inline(self, html):
        assert '<link rel="stylesheet"' not in html, "must not use external stylesheets"

    def test_all_js_is_inline(self, html):
        assert "<script src=" not in html, "must not use external scripts"

    def test_no_external_dependencies(self, html):
        lower = html.lower()
        assert "cdn" not in lower, "must not reference CDNs"
        assert "unpkg" not in lower, "must not reference unpkg"
        assert "jsdelivr" not in lower, "must not reference jsdelivr"

    def test_dark_theme_colors(self, html):
        assert "#06060e" in html, "must use void background color"
        assert "#0a0a16" in html, "must use primary surface color"

    def test_has_localstorage_usage(self, html):
        assert "localStorage" in html, "must use localStorage for persistence"

    def test_has_storage_key(self, html):
        assert "omni-writer-stories" in html, "must use the correct storage key"

    def test_has_home_link(self, html):
        assert "index.html" in html, "must have a home link back to landing page"

    def test_has_aria_labels(self, html):
        assert "aria-label" in html, "must have ARIA labels for accessibility"

    def test_has_aria_role(self, html):
        assert 'role="textbox"' in html, "writing canvas must have textbox role"
        assert 'role="toolbar"' in html, "toolbar must have toolbar role"

    def test_has_skip_link(self, html):
        assert "skip-link" in html, "must have skip link for accessibility"

    def test_has_material_design_palette(self, html):
        # At least the primary accent from the unified palette
        assert "#c084fc" in html, "must use primary accent from unified palette"

    def test_has_autosave(self, html):
        assert "autoSave" in html.replace("-", "").replace("_", ""), \
            "must implement auto-save"

    def test_has_reduced_motion_support(self, html):
        assert "prefers-reduced-motion" in html, "must respect reduced motion preference"


# ════════════════════════════════════════════════════
#  AI MODE STRUCTURAL TESTS
# ════════════════════════════════════════════════════


class TestAIMode:
    """Validate that AI Mode UI elements and infrastructure are present."""

    def test_has_ai_toggle(self, html):
        assert 'id="aiToggle"' in html, "must have AI toggle element"
        assert 'role="switch"' in html, "AI toggle must have switch role"

    def test_has_ai_action_bar(self, html):
        assert 'id="aiActionBar"' in html, "must have AI action bar"

    def test_has_ai_continue_btn(self, html):
        assert 'id="aiContinueBtn"' in html, "must have AI continue button"

    def test_has_ai_generate_btn(self, html):
        assert 'id="aiGenerateBtn"' in html, "must have AI generate button"

    def test_has_ai_stop_btn(self, html):
        assert 'id="aiStopBtn"' in html, "must have AI stop button"

    def test_has_ai_enhance_tooltip(self, html):
        assert 'id="aiEnhanceTooltip"' in html, "must have AI enhance tooltip"

    def test_has_ai_prompt_bar(self, html):
        assert 'id="aiPromptBar"' in html, "must have AI prompt bar"
        assert 'id="aiPromptInput"' in html, "must have AI prompt input"

    def test_has_settings_modal(self, html):
        assert 'id="settingsModal"' in html, "must have settings modal"

    def test_has_provider_select(self, html):
        assert 'id="settingsProvider"' in html, "must have provider select"
        assert 'value="openai"' in html, "must have OpenAI option"
        assert 'value="gemini"' in html, "must have Gemini option"
        assert 'value="anthropic"' in html, "must have Anthropic option"

    def test_has_api_key_input(self, html):
        assert 'id="settingsApiKey"' in html, "must have API key input"

    def test_has_context_bell(self, html):
        assert 'id="contextBell"' in html, "must have context notification bell"

    def test_has_context_panel(self, html):
        assert 'id="contextPanel"' in html, "must have context summary panel"
        assert 'id="contextSummaryText"' in html, "must have summary text element"
        assert 'id="contextYesBtn"' in html, "must have Yes verification button"
        assert 'id="contextNoBtn"' in html, "must have No verification button"

    def test_has_context_correction(self, html):
        assert 'id="contextCorrection"' in html, "must have correction area"
        assert 'id="contextCorrectionInput"' in html, "must have correction input"

    def test_has_ai_streaming_css(self, html):
        assert "ai-streaming" in html, "must have AI streaming indicator CSS class"
        assert "ai-pulse" in html, "must have pulse animation for streaming"

    def test_has_ai_generated_marker(self, html):
        assert "ai-generated" in html, "must have AI-generated text marker class"

    def test_has_provider_configs(self, html):
        assert "api.openai.com" in html, "must have OpenAI endpoint"
        assert "generativelanguage.googleapis.com" in html, "must have Gemini endpoint"
        assert "api.anthropic.com" in html, "must have Anthropic endpoint"

    def test_has_ai_config_storage_key(self, html):
        assert "omni-writer-ai-config" in html, "must have AI config storage key"

    def test_has_summaries_storage_key(self, html):
        assert "omni-writer-summaries" in html, "must have summaries storage key"

    def test_has_system_prompt(self, html):
        assert "Omni Writer" in html, "must reference Omni Writer in system prompt"
        assert "OMNI_SYSTEM_PROMPT" in html, "must define the system prompt constant"

    def test_still_no_external_deps(self, html):
        """AI Mode uses fetch to user-configured API endpoints, not bundled CDN deps."""
        lower = html.lower()
        assert "cdn" not in lower, "must not reference CDNs"
        assert "unpkg" not in lower, "must not reference unpkg"
        assert "jsdelivr" not in lower, "must not reference jsdelivr"


# ════════════════════════════════════════════════════
#  LOGIC REFERENCE TESTS
# ════════════════════════════════════════════════════


class TestWordCount:
    """Reference tests for the word count algorithm used in the JS."""

    def _count_words(self, text):
        """Python implementation matching the JS: split on whitespace, filter empty."""
        trimmed = text.strip()
        if not trimmed:
            return 0
        return len([w for w in trimmed.split() if len(w) > 0])

    def test_empty_string(self):
        assert self._count_words("") == 0

    def test_whitespace_only(self):
        assert self._count_words("   \n\t  ") == 0

    def test_single_word(self):
        assert self._count_words("hello") == 1

    def test_multiple_words(self):
        assert self._count_words("Hello world. This is a test.") == 6

    def test_extra_whitespace(self):
        assert self._count_words("  hello   world  ") == 2

    def test_newlines(self):
        assert self._count_words("hello\nworld\nfoo") == 3


class TestReadingTime:
    """Reference tests for the reading time calculation."""

    WPM = 200

    def _reading_time(self, word_count):
        """Python implementation matching the JS."""
        if word_count <= 0:
            return 0
        return max(1, math.ceil(word_count / self.WPM))

    def test_zero_words(self):
        assert self._reading_time(0) == 0

    def test_one_word(self):
        assert self._reading_time(1) == 1

    def test_200_words(self):
        assert self._reading_time(200) == 1

    def test_201_words(self):
        assert self._reading_time(201) == 2

    def test_400_words(self):
        assert self._reading_time(400) == 2

    def test_1000_words(self):
        assert self._reading_time(1000) == 5


class TestHtmlToMarkdown:
    """Reference tests for the HTML-to-markdown conversion logic."""

    def _convert(self, html_str):
        """Simplified Python HTML-to-markdown matching the JS converter's output."""
        import re as _re
        text = html_str
        # Headings
        text = _re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n\n", text)
        text = _re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n\n", text)
        text = _re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n\n", text)
        # Bold
        text = _re.sub(r"<(?:strong|b)>(.*?)</(?:strong|b)>", r"**\1**", text)
        # Italic
        text = _re.sub(r"<(?:em|i)>(.*?)</(?:em|i)>", r"*\1*", text)
        # Strikethrough
        text = _re.sub(r"<(?:s|strike|del)>(.*?)</(?:s|strike|del)>", r"~~\1~~", text)
        # Paragraphs
        text = _re.sub(r"<p>(.*?)</p>", r"\1\n\n", text)
        # Line breaks
        text = _re.sub(r"<br\s*/?>", "\n", text)
        # Horizontal rules
        text = _re.sub(r"<hr\s*/?>", "\n---\n\n", text)
        return text.strip()

    def test_bold(self):
        result = self._convert("<strong>hello</strong>")
        assert "**hello**" in result

    def test_bold_b_tag(self):
        result = self._convert("<b>hello</b>")
        assert "**hello**" in result

    def test_italic(self):
        result = self._convert("<em>hello</em>")
        assert "*hello*" in result

    def test_italic_i_tag(self):
        result = self._convert("<i>hello</i>")
        assert "*hello*" in result

    def test_strikethrough(self):
        result = self._convert("<s>hello</s>")
        assert "~~hello~~" in result

    def test_heading_1(self):
        result = self._convert("<h1>Title</h1>")
        assert "# Title" in result

    def test_heading_2(self):
        result = self._convert("<h2>Subtitle</h2>")
        assert "## Subtitle" in result

    def test_heading_3(self):
        result = self._convert("<h3>Section</h3>")
        assert "### Section" in result

    def test_paragraph(self):
        result = self._convert("<p>Some text here.</p>")
        assert "Some text here." in result

    def test_horizontal_rule(self):
        result = self._convert("<hr>")
        assert "---" in result
