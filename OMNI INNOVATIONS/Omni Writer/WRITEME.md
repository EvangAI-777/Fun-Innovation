# Omni Writer

Your unbiased writer for any topic, without limits. A privacy-first, local-only creative writing tool with story continuation, rich text editing, and export.

## Quick Start

Open `omni-writer.html` in any modern browser. That's it. No install, no build, no server.

## Origin

The Omni Writer began as a concept in `Omni Writer.json` -- a node-graph AI agent pipeline where: (1) a user enters a topic, (2) the Omni Writer persona generates content with no bias toward the subject matter, and (3) the output renders as a premium HTML page. The persona is defined as calm, excited to write, and without limits -- legal, social, or otherwise.

The HTML app implements this creative philosophy as a self-contained local writing tool. Instead of generating content for you, it gives you the writing space itself -- private, unrestricted, and designed to stay out of your way while you write about anything.

## How It Works

1. **Create a story.** Click the + button in the sidebar or the "Create Your First Story" prompt. Enter a topic or title -- this is what you want to write about.
2. **Write.** The canvas is a distraction-free rich text editor. Type, format, and let your thoughts flow. Everything auto-saves to your browser's local storage every 3 seconds.
3. **Continue.** Add chapters to your story using the + button in the chapter bar. Switch between chapters via tabs. Double-click a tab to rename it.
4. **Export.** When you're ready, export your story as plain text, markdown, or a self-contained HTML document with the same dark theme.

All data stays in your browser. Nothing is sent to any server.

## Feature Guide

### Writing Canvas

A `contentEditable` rich text surface with comfortable line spacing (1.85), a maximum content width of 800px for readable line lengths, and a blinking indigo cursor. Headings render in the primary palette colors (H1 in bright, H2 in primary, H3 in dim). Blockquotes get an indigo left border and italic styling. The placeholder text disappears as soon as you start typing.

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
- **HTML (.html)** -- Generates a self-contained HTML document with the same dark indigo theme, inline styles, and a "Written with Omni Writer" footer. Open it in any browser for a polished reading experience.

### Writing Statistics

The stats bar at the bottom updates in real time as you type:

- **Words** -- split on whitespace, filtered for empty strings
- **Characters** -- total text length
- **Paragraphs** -- count of block-level elements (p, h1-h3, li, blockquote, div)
- **Reading time** -- words / 200 wpm, rounded up, minimum 1 minute

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
| Escape | Close modal / sidebar |

## Design

**Single file.** Everything -- HTML structure, CSS styles, JavaScript logic, starfield animation -- lives in one `.html` file. No dependencies, no build tools, no frameworks, no CDN imports.

**Dark indigo theme.** Material Design 3 palette from the original `Omni Writer.json` config. Deep void backgrounds (#06060e, #0a0a16) with indigo/blue-violet accents (#9aa5fd primary, #bcc2ff bright, #6570c4 dim). The color scheme creates a focused, immersive writing environment.

**Responsive.** Flexbox layout with media queries at 768px (sidebar collapses to an overlay toggle) and 480px (toolbar and canvas adapt to narrow screens). The writing experience works on phones, tablets, and desktops.

**Accessible.** Skip link, ARIA labels on all interactive elements, semantic HTML (aside, main, role attributes), full keyboard navigation, high-contrast text on dark backgrounds.

**Privacy-first.** All data is stored in the browser's localStorage. Nothing leaves your machine. No analytics, no tracking, no cloud sync.

## The JSON Config

`Omni Writer.json` in this directory is the original concept definition -- a Breadboard-format node-graph AI agent flow built with Google's Gemini models. It defines a 3-node pipeline:

1. **ask_user_writing_topic** -- Prompts the user to enter a writing topic
2. **node_step_generated_content** -- Generates unbiased content using the Omni Writer persona
3. **node_step_written_content** -- Renders the output as a premium HTML webpage

The HTML app implements the same creative philosophy -- write about anything, without limits -- as a local-first tool. The JSON remains in this directory for anyone interested in the original AI agent pipeline concept.

## Colors

| Element | Hex | Source |
|---------|-----|--------|
| Void background | #06060e | Repo convention |
| Surface | #0a0a16 | Repo convention |
| Surface variant | #10102a | Repo convention (indigo tint) |
| Primary | #9aa5fd | JSON primary-70 |
| Primary bright | #bcc2ff | JSON primary-80 |
| Primary dim | #6570c4 | JSON primary-50 |
| Primary deep | #4c57a9 | JSON primary-40 |
| Secondary | #74758b | JSON secondary-50 |
| Error | #ff5449 | JSON error-60 |
| Success | #a3be8c | Repo convention |
| Text primary | #e4e1e6 | JSON neutral-90 |
| Text secondary | #78767a | JSON neutral-50 |
| Border | #303034 | JSON neutral-20 |

---

# Changelog

All notable changes to the Omni Writer are documented here.

## [v1.0.0] - 2026-02-20

### Added
- **Writing canvas** -- `contentEditable` rich text editor with bold, italic, underline, strikethrough, headings (H1-H3), bullet and numbered lists, blockquote, and horizontal rule formatting.
- **Story library** -- localStorage-based sidebar listing all stories by title, word count, and last modified date. Search filter. Delete with confirmation.
- **Story continuation** -- multi-chapter support with tabbed navigation, add/remove/rename chapters, automatic save on chapter switch.
- **Topic system** -- editable title/topic input per story, matching the Omni Writer persona's "always asking the user what they want" philosophy.
- **Auto-save** -- debounced 3-second auto-save on every input event, with save status indicator.
- **Export** -- download stories as plain text (.txt), markdown (.md), or self-contained HTML (.html) with the dark indigo theme.
- **Writing statistics** -- real-time word count, character count, paragraph count, and estimated reading time.
- **Keyboard shortcuts** -- Ctrl+B/I/U for formatting, Ctrl+S to save, Ctrl+E for export, Escape to close modals.
- **Dark indigo theme** -- Material Design 3 palette from the original Omni Writer.json config.
- **Animated starfield** -- twinkling background matching the repo's visual aesthetic.
- **Responsive design** -- breakpoints at 768px (sidebar overlay) and 480px (compact layout).
- **Accessible** -- skip link, ARIA labels, semantic HTML, keyboard navigation.
- **Zero dependencies** -- single HTML file, no CDN, no frameworks, no external imports.
