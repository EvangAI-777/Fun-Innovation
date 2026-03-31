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
| AI streaming | Yes (3 providers, fetch-based SSE) | Yes (Perchance AI plugin, callback-based) |
| Free AI (no key) | No (all providers require API key) | Yes (Perchance plugin is free) |
| Token counting | No (character-based heuristic) | Yes (plugin's `countTokens`) |
| `startWith` prefix | No | Yes (forces AI to continue from last paragraph) |
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

**8. Perchance AI text plugin as a provider** — Add Perchance's `ai-text-plugin` as a fourth AI provider alongside OpenAI, Gemini, and Anthropic. This is the engine powering both generator configs and offers a unique value proposition: **free AI generation with no API key required**.

**How the plugin works (from the generator configs):**

The generators import the plugin via Perchance's module system (`ai = {import:ai-text-plugin}`) and call it with a rich options object:

```javascript
let streamObj = ai({
  instruction: "...",          // System prompt / writing instructions
  startWith: "...",            // Text the AI should "continue from" (injected as prefix)
  stopSequences: ["\n\n"],     // Stop generation at paragraph boundaries
  onStart: (data) => {},       // Called when generation begins
  onChunk: (data) => {         // Called per token — data.textChunk, data.isFromStartWith
    storySoFarEl.value += data.textChunk;
  },
  onFinish: (data) => {        // Called when generation completes — data.stopReason
    // cleanup, save to localStorage
  },
});
streamObj.stop();              // Abort generation
streamObj.submitUserRating({score, reason}); // Rate the output
```

The plugin also exposes metadata via `ai({getMetaObject:true})` which returns `{ countTokens, idealMaxContextTokens }` — used by the hierarchical summary system to decide when context compression is needed.

**Key plugin capabilities relevant to Omni Writer:**
- **Streaming with `onChunk`/`onFinish` callbacks** — maps directly to Omni Writer's `streamAI()` pattern but uses callbacks instead of `ReadableStream`. The adapter would need to bridge these two models.
- **`startWith` parameter** — forces the AI to begin its response with specific text (the last paragraph of the story). This is how the generators maintain coherent continuation without repeating context. Omni Writer could use this to improve continuation quality.
- **`stopSequences`** — native support for one-paragraph-at-a-time mode. Omni Writer currently has no stop sequence support; adding it via the Perchance plugin would be trivial, and the same concept could be added for other providers.
- **`countTokens` / `idealMaxContextTokens`** — token counting without external libraries. Could enhance Omni Writer's smart context system with accurate token counts instead of character-based heuristics.
- **`submitUserRating`** — built-in rating submission that improves Perchance's AI. Maps directly to the Tier 3 paragraph rating feature.

**Integration approach:**

1. **Load the plugin** — The `ai-text-plugin` is hosted at `perchance.org/ai-text-plugin`. Since Omni Writer is a standalone HTML file with zero dependencies, loading an external script is a design decision that needs consideration. Two options:
   - **Dynamic import**: Only load the plugin script when the user selects "Perchance" as their provider in settings. This keeps the zero-dependency promise intact for users who don't use it.
   - **Iframe bridge**: Load a hidden Perchance generator page in an iframe and communicate via `postMessage`. More isolated but more complex.

2. **Add to PROVIDERS registry** — Create a `perchance` entry in the existing `PROVIDERS` object (`omni-writer.html:~2050`):
   ```javascript
   perchance: {
     name: 'Perchance',
     requiresKey: false,  // Key differentiator — no API key needed
     defaultModel: 'default',
     models: ['default'],
     getEndpoint: () => null,  // Not HTTP-based
     // Custom streaming via plugin callbacks instead of fetch()
   }
   ```

3. **Adapt `streamAI()` function** — The existing `streamAI()` at line 2083 assumes a fetch-based SSE streaming model. For Perchance, create an alternate code path that uses the plugin's callback API:
   ```javascript
   if (aiConfig.provider === 'perchance') {
     const streamObj = perchanceAI({
       instruction: messages.map(m => m.content).join('\n'),
       startWith: lastParagraph,
       stopSequences: oneParagraphMode ? ['\n\n'] : [],
       onChunk: (data) => { if (!data.isFromStartWith) onChunk(data.textChunk); },
       onFinish: () => onDone(),
     });
     abortController = { abort: () => streamObj.stop() };  // Shim abort interface
     return;
   }
   ```

4. **Leverage `startWith` for all providers** — The `startWith` pattern (feeding the last paragraph as a forced prefix) is a genuinely good prompt engineering technique. Consider adopting it for OpenAI/Gemini/Anthropic too, by prepending the last paragraph as an `assistant` message in the messages array.

5. **Token counting** — If the Perchance plugin is loaded, use its `countTokens` function to improve Omni Writer's smart context management (currently character-based at `omni-writer.html:~2400`). This would make summary checkpoints more accurate.

**Considerations:**
- **Privacy**: The Perchance plugin routes requests through Perchance's servers. Document this clearly in the AI Settings modal so users understand the data flow.
- **Availability**: The plugin requires an internet connection to `perchance.org`. If the CDN is down, the provider should gracefully degrade with a clear error.
- **Zero-dependency philosophy**: Loading an external script technically breaks the "no CDN, no external imports" promise. The dynamic-import approach mitigates this — the plugin is only loaded on demand, and the app remains fully functional without it.
- **Rate limits**: Perchance's free tier may have rate limits or usage caps. Handle `429` or equivalent errors gracefully.

**9. Hierarchical summary system (from Perchance plugin)** — The generators implement a sophisticated multi-level summarization system (`getMessagesWithSummaryReplacements()` + `injectSummariesAndComputeNextSummariesInBackgroundIfNeeded()`) that's more advanced than Omni Writer's current single-checkpoint approach. Key differences:

| Aspect | Omni Writer (current) | Generator approach |
|--------|----------------------|-------------------|
| Trigger | Single checkpoint when context exceeded | Continuous background summarization |
| Levels | 1 (flat summary) | Hierarchical (`SUMMARY^1`, `SUMMARY^2`, ...) |
| Visibility | Notification bell, user confirms | Inline markers in text, user can edit |
| Token counting | Character-based heuristic | Plugin's `countTokens` function |
| Summary quality | User-verified | Auto-generated, sometimes re-summarized |

The hierarchical approach could be adapted for Omni Writer as an enhancement to the existing smart context system. Instead of one summary checkpoint, maintain a tree of summaries at increasing levels of abstraction. When context is exceeded, swap in higher-level summaries for older content while keeping recent paragraphs verbatim. This would allow much longer stories without degradation.

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
2. Add one-paragraph-at-a-time toggle (with `stopSequences` support)
3. Add AI idea suggestions panel (💡 button + dropdown)
4. Add brainstorm/critique tabs to suggestions
5. Add paragraph-level undo for AI generations
6. Add purple prose guard (optional toggle)
7. Add Perchance as fourth AI provider (dynamic script load, callback-to-stream adapter, no-API-key flow)
8. Add `startWith` continuation technique (adopt for all providers)
9. Upgrade smart context with plugin's `countTokens` + hierarchical summary system
10. Version bump to v2.1.0 + doc updates
