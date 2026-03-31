# Merge Plan: AI Story Generator 1 & 2 Design Patterns → Omni Writer

## What These Files Are

Both `.md` files are **Perchance.org generator configs** — not standard markdown. They define a paragraph-by-paragraph AI story generator with a specific UI layout and interaction model. They're configuration code from a platform called Perchance, containing mixed Perchance template syntax, HTML, CSS, and JavaScript.

## Design Features Worth Extracting

### From Generator 1 (the logic engine):
1. **Paragraph-by-paragraph generation** — "one paragraph at a time" toggle with stop sequences at `\n\n`
2. **"What happens next" directive slots** — 5 input fields that inject user instructions into the AI prompt as prioritized directives
3. **AI suggestion generators** — lightbulb buttons (💡🧠😎🎤📃) that generate clickable idea lists for story direction, roasts, brainstorming, speaking styles, and critique
4. **Purple prose auto-fix** — post-generation text replacements that swap cliches ("the cacophony" → "the sound", "tapestry of" → "pattern of")
5. **Hierarchical summary system** — `getMessagesWithSummaryReplacements()` that compresses old paragraphs into summary blocks for infinite context (similar to Omni Writer's existing smart context, but with a different approach: inline `SUMMARY^N:` markers visible in the textarea)
6. **Rating system** — thumbs up/down per paragraph with optional reason, submitted back to the AI provider
7. **Inline continue button** — tracks caret position in textarea, shows a floating ▶️ button when cursor is at end of text, Tab key shortcut
8. **Undo delete** — timed undo button when deleting last paragraph
9. **Streaming performance optimization** — temporarily strips prefix text during streaming for very long stories (>50k chars)

### From Generator 2 (the UI layout):
- Same UI structure as Generator 1 but with slightly different prompts
- The HTML section shows the actual layout: overview textarea → story textarea → control bar (rate/regen/delete) → "what happens next" inputs → generate button → checkbox

## What Omni Writer Already Has (overlapping features)

| Feature | Omni Writer | Generators |
|---------|-------------|------------|
| AI streaming | Yes (3 providers) | Yes (Perchance AI plugin) |
| Continue story | Yes (Ctrl+Shift+Enter) | Yes (▶️ button) |
| Enhance text | Yes (selection-based) | No |
| Generate from prompt | Yes (prompt bar) | Partial (via "what happens next" fields) |
| Smart context/summary | Yes (notification bell + verify) | Yes (inline SUMMARY^ markers) |
| Multi-chapter | Yes | No |
| Rich text | Yes (contentEditable) | No (plain textarea) |
| Story library | Yes (sidebar, multi-story) | No (single story, localStorage) |
| Dark mode | Always dark | Toggle light/dark |
| Paragraph rating | No | Yes (👍👎 + reason) |
| Idea suggestions | No | Yes (5 AI-powered suggestion types) |
| What-happens-next slots | No | Yes (directive injection) |
| One-paragraph-at-a-time | No (streams freely) | Yes (stop at \n\n) |
| Caret-tracking continue | No | Yes (floating button at cursor) |
| Cliche auto-fix | No | Yes |

## Features to Merge Into Omni Writer

### Tier 1 — High-value, low-conflict additions:

**1. "What Happens Next" directive input** — Add a collapsible input field below the writing canvas (or in a slide-out panel) where users type a direction/instruction. When AI Continue is triggered, this text gets injected into the system prompt as a prioritized directive. This is the generators' killer feature — it gives users narrative control without breaking the flow.

**2. AI Idea Suggestions panel** — A "💡 Ideas" button in the toolbar that opens a dropdown with 3 AI-generated one-sentence suggestions for what could happen next, each with a "use" button that populates the directive input. Adapts generators' `generateWhatHappensNextIdeas()` pattern.

**3. One-paragraph-at-a-time mode** — Add a toggle in AI settings (or toolbar) that stops generation after one paragraph (`\n\n`). Maps to the generators' `oneParagraphAtATimeCheckbox` behavior. Implementation: detect `\n\n` in the stream buffer and call `abortController.abort()`.

### Tier 2 — Medium-value, medium-effort:

**4. Story critique/brainstorm panel** — Extend the ideas system with tabs: "Next" (plot suggestions), "Style" (brainstorm genres/styles/vocab), "Critique" (improvement suggestions). Maps to generators' 5 suggestion types, consolidated into 3 tabs.

**5. Paragraph-level undo** — When AI generates text, track the pre-generation state. Add a toast/undo button that lets users revert the last AI generation without Ctrl+Z. Cleaner than the generators' approach since Omni Writer uses contentEditable (can use `document.execCommand` undo stack or manual snapshot).

### Tier 3 — Nice-to-have, requires careful integration:

**6. Purple prose guard** — Optional post-processing pass on AI output that detects and replaces common AI cliches. Could be a toggle in settings ("Reduce AI cliches"). The generators' regex list is a good starting point but should be expanded.

**7. Paragraph rating** — After each AI generation, briefly show 👍👎 buttons near the generated text. Ratings stored locally for now (could inform future prompt tuning). Lower priority since Omni Writer doesn't report to Perchance.

### Tier 4 — Perchance Plugin Integration:

**8. Perchance AI text plugin** — Investigate integrating the `ai-text-plugin` from Perchance as an additional AI provider option alongside OpenAI, Gemini, and Anthropic. This would give users access to Perchance's free AI model without needing their own API key. Implementation: add a `perchance` entry to the `PROVIDERS` object in `omni-writer.html` that imports and interfaces with the plugin's `ai()` function, adapting its streaming `onChunk`/`onFinish` callbacks to Omni Writer's `streamAI()` pattern.

## What NOT to Merge

- **The textarea-based editing** — Omni Writer's contentEditable rich text is strictly superior
- **The caret-tracking floating button** — Omni Writer already has a Continue button in the toolbar; the inline version adds complexity for marginal UX gain in a rich-text context
- **The light/dark toggle** — Omni Writer is dark-only by design (site-wide palette)
- **The comments/feedback system** — Perchance-specific, not applicable

## Implementation Approach

All changes go into the existing `omni-writer.html` single file. No new files except tests.

**Files to modify:**
- `OMNI INNOVATIONS/Omni Writer/omni-writer.html` — All UI and logic changes
- `tests/omniversal/test_omni_writer.py` — New tests for added features
- `OMNI INNOVATIONS/Omni Writer/WRITEME.md` — Document new features

**Sequencing (small commits):**
1. Add "what happens next" directive input + wire into AI Continue prompt
2. Add one-paragraph-at-a-time toggle
3. Add AI idea suggestions panel (💡 button + dropdown)
4. Add brainstorm/critique tabs to suggestions
5. Add paragraph-level undo for AI generations
6. Add purple prose guard (optional toggle)
7. Investigate Perchance plugin integration as a provider
8. Version bump to v2.1.0 + doc updates
