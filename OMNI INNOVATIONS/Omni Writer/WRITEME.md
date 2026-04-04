# Omni Writer

Your unbiased writer for any topic, without limits. A creative writing tool with built-in AI Mode, story continuation, rich text editing, and export. Toggle AI on to continue, enhance, or generate text with streaming AI -- or keep it off for a distraction-free local writing experience.

## Quick Start

Open `omni-writer.html` in any modern browser. That's it. No install, no build, no server.

## Origin

The Omni Writer began as a concept in `Omni Writer.json` -- a node-graph AI agent pipeline where: (1) a user enters a topic, (2) the Omni Writer persona generates content with no bias toward the subject matter, and (3) the output renders as a premium HTML page. The persona is defined as calm, excited to write, and without limits -- legal, social, or otherwise.

The HTML app implements this creative philosophy as a self-contained writing tool. With AI Mode off, it's a private, unrestricted writing space designed to stay out of your way. With AI Mode on, the Omni Writer persona comes alive -- continuing your stories, enhancing your prose, and generating fresh content, all matching your voice and style. The AI is invisible by design: configure your provider once, then just toggle "AI" on or off.

## How It Works

1. **Create a story.** Click the + button in the sidebar or the "Create Your First Story" prompt. Enter a topic or title -- this is what you want to write about.
2. **Write.** The canvas is a distraction-free rich text editor. Type, format, and let your thoughts flow. Everything auto-saves to your browser's local storage every 3 seconds.
3. **Continue.** Add chapters to your story using the + button in the chapter bar. Switch between chapters via tabs. Double-click a tab to rename it.
4. **Export.** When you're ready, export your story as plain text, markdown, or a self-contained HTML document with the same dark theme.

All data stays in your browser. Nothing is sent to any server -- except when AI Mode is enabled, where your text is sent directly to the AI provider you configured (and nowhere else).

## Feature Guide

### Writing Canvas

A `contentEditable` rich text surface with comfortable line spacing (1.85), a maximum content width of 800px for readable line lengths, and a blinking purple cursor. Headings render in the primary palette colors (H1 in bright, H2 in primary, H3 in dim). Blockquotes get a purple left border and italic styling. The placeholder text disappears as soon as you start typing.

### Rich Text Formatting

The toolbar provides formatting via `document.execCommand`:

| Button | Action | Shortcut |
|--------|--------|----------|
| **B** | Bold | Ctrl+B |
| *I* | Italic | Ctrl+I |
| U | Underline | Ctrl+U |
| ~~S~~ | Strikethrough | -- |
| H1 | Heading 1 | -- |
| H2 | Heading 2 | -- |
| H3 | Heading 3 | -- |
| P | Paragraph (reset) | -- |
| Bullet | Unordered list | -- |
| 1. | Ordered list | -- |
| Quote | Blockquote | -- |
| Rule | Horizontal rule | -- |
| Undo | Undo | Ctrl+Z |
| Redo | Redo | Ctrl+Y |

### Story Library

The left sidebar lists all saved stories sorted by last modified date. Each entry shows the story title, total word count across all chapters, and a relative timestamp ("2m ago", "Yesterday", etc.). Click any story to open it. Hover to reveal the delete button. Use the search bar at the top to filter stories by title.

### Story Continuation

Every story supports multiple chapters. When a story has more than one chapter, a chapter bar appears below the toolbar with tabs for each chapter. Click a tab to switch chapters. Click the + button to add a new chapter. Double-click a tab name to rename it. Click the x on a tab to remove it (with the last chapter protected from deletion).

Chapters auto-save independently -- switching chapters saves the current one and loads the next. This is how Omni Writer supports continuing stories: pick up where you left off, add new chapters, and build your narrative across sessions.

### Export

Export your entire story (all chapters) as a single file in three formats:

- **Plain Text (.txt)** -- Extracts the raw text content. Multi-chapter stories get chapter headings separated by dividers.
- **Markdown (.md)** -- Converts the rich text to markdown syntax. Bold becomes `**bold**`, italic becomes `*italic*`, headings become `#` markers, lists become `- ` or `1. ` prefixes, blockquotes become `> ` lines.
- **HTML (.html)** -- Generates a self-contained HTML document with the same dark purple theme, inline styles, and a "Written with Omni Writer" footer. Open it in any browser for a polished reading experience.

### Writing Statistics

The stats bar at the bottom updates in real time as you type:

- **Words** -- split on whitespace, filtered for empty strings
- **Characters** -- total text length
- **Paragraphs** -- count of block-level elements (p, h1-h3, li, blockquote, div)
- **Reading time** -- words / 200 wpm, rounded up, minimum 1 minute

### AI Mode

Toggle AI on with the switch in the toolbar (or Ctrl+Shift+A). The first time you enable it, you'll be prompted to configure your AI provider in Settings. Once configured, the provider is invisible -- you just see "AI" on/off.

**Three AI actions:**

- **Continue** -- Click the Continue button (or Ctrl+Shift+Enter) and the AI picks up where your text ends, writing 2-3 paragraphs that match your style and voice. The text streams in token by token.
- **Enhance** -- Select any text in your story and a floating "Enhance" tooltip appears. Click it, and the AI rewrites/improves the selected passage while preserving meaning. Ctrl+Z undoes if you don't like it.
- **Generate** -- Click Generate, type a prompt describing what you want (e.g., "a tense dialogue scene between the two characters"), and the AI writes it fresh, inserting at the cursor position.

AI-generated text gets a subtle dotted underline so you can tell what was written by the AI vs. what you typed yourself. Each AI-generated paragraph also shows up/down rating buttons on hover (right side), so you can mark which generations you liked and which need work.

**Directive input (What Happens Next):**

When AI is enabled, a directive bar appears below the action bar. Type a short instruction like "the villain reveals their true identity" and the AI will steer its next continuation in that direction. The directive persists across sessions via localStorage. Clear it with the × button.

**Ideas panel:**

Click the Ideas button to open a suggestion panel with three tabs:
- **Next** -- 3 creative directions for what could happen next in your story
- **Style** -- writing style, dialogue, and tone suggestions
- **Critique** -- constructive feedback on pacing, character development, and prose quality

Each suggestion has a "Use" button that applies it as the current directive. The panel supports custom regen instructions for more targeted suggestions.

**One paragraph at a time:**

Enable in Settings to have the AI stop after generating a single paragraph. Useful for tighter control over the narrative flow. Works with all providers -- Perchance uses native stop sequences, fetch-based providers detect paragraph boundaries in the stream.

**Purple prose guard:**

Enable in Settings to inject anti-purple-prose constraints into the AI's system prompt. Limits metaphors, discourages flowery adverbs, and encourages clean, concrete prose.

**Paragraph undo:**

After any AI generation (Continue or Generate), an Undo button appears in the action bar. Click it to remove the last AI-generated text. The undo stack supports multiple levels -- keep clicking to undo further back.

**Supported providers:**

- Google Gemini (default: gemini-2.0-flash)
- OpenAI (default: gpt-4o-mini)
- Anthropic (default: claude-sonnet-4-5-20250929)
- Perchance (free, no API key required -- uses the Perchance ai-text-plugin. **Only works when hosted on perchance.org** -- the plugin is domain-restricted. A successful integration experiment; see changelog note below.)

Your API key stays in your browser's localStorage. It's sent directly to your chosen provider's API and nowhere else. Perchance requires no key at all but only functions on the perchance.org domain -- the ai-text-plugin enforces this restriction. When hosted elsewhere (GitHub Pages, local file, etc.), the Perchance provider will fail to load.

### Smart Context Management

When your story grows beyond what the AI can hold in memory, the writer automatically generates a summary of the story so far. A small notification bell appears in the bottom-right corner. Click it to review the summary and confirm its accuracy:

- **Yes** -- The summary is marked as verified and used as context for all future AI calls, keeping the AI coherent across long stories.
- **No** -- You describe what's wrong, and the AI regenerates the summary with your corrections.

This checkpoint happens unobtrusively in the corner, never interrupting your writing flow.

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+B | Bold |
| Ctrl+I | Italic |
| Ctrl+U | Underline |
| Ctrl+S | Save |
| Ctrl+E | Export modal |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+Shift+A | Toggle AI Mode |
| Ctrl+Shift+Enter | AI Continue |
| Escape | Stop generating / Close modal / sidebar |

## Design

**Single file.** Everything -- HTML structure, CSS styles, JavaScript logic, starfield animation -- lives in one `.html` file. No dependencies, no build tools, no frameworks, no CDN imports.

**Dark purple theme.** Unified site-wide palette with deep void backgrounds (#06060e, #0a0a16) and bright purple accents (#c084fc primary, #d4a8ff bright, #9a6abf dim). The color scheme creates a focused, immersive writing environment consistent with the rest of the Fun-Innovation site.

**Responsive.** Flexbox layout with media queries at 768px (sidebar collapses to an overlay toggle) and 480px (toolbar and canvas adapt to narrow screens). The writing experience works on phones, tablets, and desktops.

**Accessible.** Skip link, ARIA labels on all interactive elements, semantic HTML (aside, main, role attributes), full keyboard navigation, high-contrast text on dark backgrounds.

**Privacy-first.** All data is stored in the browser's localStorage. With AI Mode off, nothing leaves your machine. With AI Mode on, your text is sent directly to the AI provider you configured (OpenAI, Gemini, or Anthropic) and nowhere else. Perchance is also available but only on perchance.org. No analytics, no tracking, no cloud sync.

## The JSON Config

`Omni Writer.json` in this directory is the original concept definition -- a Breadboard-format node-graph AI agent flow built with Google's Gemini models. It defines a 3-node pipeline:

1. **ask_user_writing_topic** -- Prompts the user to enter a writing topic
2. **node_step_generated_content** -- Generates unbiased content using the Omni Writer persona
3. **node_step_written_content** -- Renders the output as a premium HTML webpage

The HTML app implements the same creative philosophy -- write about anything, without limits -- as a local-first tool. The JSON remains in this directory for anyone interested in the original AI agent pipeline concept.

## Colors

| Element | Hex | Source |
|---------|-----|--------|
| Void background | #06060e | Site-wide palette |
| Surface | #0a0a16 | Site-wide palette |
| Surface variant | #10102a | Site-wide palette (purple tint) |
| Primary | #c084fc | Site-wide unified accent |
| Primary bright | #d4a8ff | Accent hover variant |
| Primary dim | #9a6abf | Accent subdued variant |
| Primary deep | #7a4fa0 | Accent deep variant |
| Secondary | #9898b8 | Site-wide secondary text |
| Error | #ff5449 | Semantic (unchanged) |
| Success | #a3be8c | Semantic (unchanged) |
| Text primary | #e0e0f0 | Site-wide text |
| Text secondary | #7878a0 | Site-wide muted text |
| Border | #252550 | Site-wide border |

---

# Changelog

All notable changes to the Omni Writer are documented here.

## [v2.1.0] - 2026-03-31

### Added
- **Perchance provider** -- Free AI provider with no API key required. Uses the Perchance ai-text-plugin, loaded on demand only when selected. Preserves zero-dependency philosophy. **Note:** The ai-text-plugin only works when hosted on perchance.org -- it's domain-restricted by Perchance. The integration was a successful experiment in wiring a callback-based external AI plugin into the Omni Writer streaming architecture, and the code remains as a working reference for perchance.org deployments, but it won't function on GitHub Pages or local file:// hosting.
- **Directive input** -- "What happens next" bar below the AI actions. Type a short instruction to steer the AI's next continuation. Persists via localStorage.
- **AI Ideas panel** -- Three-tab suggestion panel (Next/Style/Critique) that generates creative plot ideas, style suggestions, or constructive critiques. Each idea has a "Use" button to apply it as the current directive.
- **One-paragraph mode** -- Toggle in Settings. AI stops after generating a single paragraph for tighter narrative control.
- **Purple prose guard** -- Toggle in Settings. Injects anti-flowery-prose constraints into the system prompt.
- **Paragraph-level undo** -- Undo button appears after AI generations. Multi-level stack removes AI-generated text in reverse order.
- **Paragraph ratings** -- Up/down rating buttons appear on hover over AI-generated paragraphs.

### Changed
- **startWith technique** -- All providers now use trailing assistant messages to prime continuation, preventing the AI from repeating existing text.
- Provider settings UI dynamically hides API key and model fields when Perchance is selected.

## [v2.0.1] - 2026-03-30

### Changed
- **Unified color scheme** -- Accent color changed from periwinkle (#9aa5fd) to bright purple (#c084fc) to match the site-wide palette. All color variants (bright, dim, deep, glow), borders (#252550), and text colors (#e0e0f0, #7878a0) aligned with the Fun-Innovation unified theme. Export HTML template colors updated to match.

## [v2.0.0] - 2026-02-20

### Added
- **AI Mode** -- Toggle AI on/off in the toolbar. Invisible provider switching -- configure once in settings, then just write. Supports OpenAI, Google Gemini, and Anthropic.
- **Continue** -- AI extends the story from where the text ends, matching style and voice. Streams token by token.
- **Enhance** -- Select text, click the floating Enhance tooltip, and the AI rewrites/improves the selection.
- **Generate** -- Describe what you want in a prompt bar, and the AI generates it fresh at the cursor position.
- **Smart context management** -- Automatic story summarization when content exceeds the AI's context window. Unobtrusive notification bell with summary verification (Yes/No) and correction flow.
- **AI Settings modal** -- Provider selection, API key configuration, model selection, and connection testing.
- **Streaming output** -- All AI responses stream in real-time with a pulsing border indicator and Stop button.
- **Keyboard shortcuts** -- Ctrl+Shift+A to toggle AI, Ctrl+Shift+Enter to continue writing, Escape to stop generation.

## [v1.0.0] - 2026-02-20

### Added
- **Writing canvas** -- `contentEditable` rich text editor with bold, italic, underline, strikethrough, headings (H1-H3), bullet and numbered lists, blockquote, and horizontal rule formatting.
- **Story library** -- localStorage-based sidebar listing all stories by title, word count, and last modified date. Search filter. Delete with confirmation.
- **Story continuation** -- multi-chapter support with tabbed navigation, add/remove/rename chapters, automatic save on chapter switch.
- **Topic system** -- editable title/topic input per story, matching the Omni Writer persona's "always asking the user what they want" philosophy.
- **Auto-save** -- debounced 3-second auto-save on every input event, with save status indicator.
- **Export** -- download stories as plain text (.txt), markdown (.md), or self-contained HTML (.html) with the dark purple theme.
- **Writing statistics** -- real-time word count, character count, paragraph count, and estimated reading time.
- **Keyboard shortcuts** -- Ctrl+B/I/U for formatting, Ctrl+S to save, Ctrl+E for export, Escape to close modals.
- **Dark purple theme** -- unified site-wide palette with bright purple (#c084fc) accent.
- **Animated starfield** -- twinkling background matching the repo's visual aesthetic.
- **Responsive design** -- breakpoints at 768px (sidebar overlay) and 480px (compact layout).
- **Accessible** -- skip link, ARIA labels, semantic HTML, keyboard navigation.
- **Zero dependencies** -- single HTML file, no CDN, no frameworks, no external imports.
