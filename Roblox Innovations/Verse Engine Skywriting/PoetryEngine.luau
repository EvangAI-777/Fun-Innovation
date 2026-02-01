--[[
    PoetryEngine.luau
    ModuleScript -- place in ReplicatedStorage

    Faithful Luau port of verse_engine.py's poem generation logic.
    Five word bank categories, five template types, five voices with biases,
    plus haiku, couplet, and fragment forms.
]]

local PoetryEngine = {}

------------------------------------------------------------------------
-- Word banks by concept
------------------------------------------------------------------------

local WORDS = {
    nature = {
        nouns = {"river", "stone", "mountain", "forest", "rain", "moon", "sun", "wind",
                 "leaf", "root", "branch", "seed", "cloud", "storm", "snow", "tide",
                 "shore", "field", "meadow", "valley", "peak", "dawn", "dusk", "star"},
        verbs = {"flows", "grows", "falls", "rises", "drifts", "settles", "breaks",
                 "bends", "reaches", "fades", "blooms", "withers", "returns", "remains"},
        adjectives = {"quiet", "ancient", "patient", "wild", "still", "distant",
                      "hollow", "deep", "vast", "small", "cold", "warm", "soft", "sharp"},
    },
    time = {
        nouns = {"moment", "year", "hour", "second", "memory", "future", "past",
                 "yesterday", "tomorrow", "century", "instant", "eternity", "age", "era"},
        verbs = {"passes", "lingers", "vanishes", "stretches", "collapses", "waits",
                 "returns", "escapes", "holds", "releases", "forgets", "remembers"},
        adjectives = {"brief", "endless", "fleeting", "slow", "sudden", "inevitable",
                      "lost", "found", "borrowed", "stolen", "given", "taken"},
    },
    emotion = {
        nouns = {"grief", "joy", "longing", "peace", "fear", "hope", "love", "loss",
                 "silence", "laughter", "sorrow", "wonder", "doubt", "faith", "rage"},
        verbs = {"aches", "sings", "whispers", "screams", "settles", "rises", "fades",
                 "burns", "cools", "breaks", "mends", "waits", "arrives", "departs"},
        adjectives = {"heavy", "light", "sharp", "dull", "bright", "dark", "tender",
                      "fierce", "gentle", "raw", "numb", "alive", "quiet", "loud"},
    },
    body = {
        nouns = {"hands", "eyes", "heart", "bones", "skin", "breath", "voice", "blood",
                 "mouth", "fingers", "chest", "shoulders", "spine", "tongue", "teeth"},
        verbs = {"holds", "sees", "beats", "breaks", "touches", "breathes", "speaks",
                 "carries", "reaches", "closes", "opens", "trembles", "steadies"},
        adjectives = {"tired", "young", "old", "empty", "full", "open", "closed",
                      "scarred", "whole", "broken", "warm", "cold", "familiar", "strange"},
    },
    abstract = {
        nouns = {"truth", "nothing", "everything", "edge", "center", "distance", "weight",
                 "shadow", "light", "name", "word", "story", "question", "answer", "door"},
        verbs = {"exists", "disappears", "means", "becomes", "remains", "shifts",
                 "reveals", "hides", "asks", "answers", "matters", "changes", "stays"},
        adjectives = {"true", "false", "real", "imagined", "possible", "impossible",
                      "necessary", "uncertain", "clear", "obscure", "simple", "complex"},
    },
}

------------------------------------------------------------------------
-- Structural elements
------------------------------------------------------------------------

local ARTICLES = {"the", "a", "this", "that", "each", "every", "no", "some"}
local PREPOSITIONS = {"in", "on", "through", "beneath", "above", "between", "within", "without", "beyond", "before", "after"}
local CONNECTORS = {"and", "but", "or", "yet", "still", "though", "while", "as", "like", "when"}

------------------------------------------------------------------------
-- Line templates
------------------------------------------------------------------------

local TEMPLATES = {
    simple = {
        "{article} {adj} {noun}",
        "{noun} {verb}",
        "{adj} {noun}, {adj} {noun}",
        "{verb} the {noun}",
        "{preposition} the {noun}",
    },
    medium = {
        "{article} {adj} {noun} {verb}",
        "the {noun} {verb} {preposition} {noun2}",
        "{adj} as {article} {noun}",
        "where {noun} {verb}",
        "what the {noun} {verb}",
        "{noun} and {noun2}, {verb}",
    },
    complex = {
        "the {adj} {noun} {verb} {preposition} the {adj2} {noun2}",
        "like {article} {noun} that {verb} {preposition} {noun2}",
        "{preposition} the {adj} {noun}, {article} {noun2} {verb}",
        "even the {noun} {verb} when {noun2} {verb2}",
        "not {article} {noun}, but the {adj} {noun2}",
    },
    question = {
        "what {verb} in the {noun}?",
        "where does the {noun} {verb}?",
        "why {verb} the {adj} {noun}?",
        "who {verb} the {noun}?",
        "is this {article} {noun} or {article} {noun2}?",
    },
    statement = {
        "this is the {noun}",
        "here, the {noun} {verb}",
        "there is no {adj} {noun}",
        "only the {noun} {verb}",
        "all {noun} {verb}",
    },
}

------------------------------------------------------------------------
-- Haiku templates (5-7-5 syllable approximation)
------------------------------------------------------------------------

local HAIKU_LINES = {
    [5] = {
        "{adj} {noun}",
        "the {noun} {verb}",
        "{noun} and {noun2}",
        "{preposition} the {noun}",
        "a {adj} {noun}",
        "{verb} the {noun}",
    },
    [7] = {
        "the {adj} {noun} {verb}",
        "{noun} {verb} {preposition} {noun2}",
        "{adj} {noun}, {adj} {noun2}",
        "where the {adj} {noun} {verb}",
        "{preposition} the {adj} {noun}",
    },
}

------------------------------------------------------------------------
-- Voice configurations
------------------------------------------------------------------------

local VOICES = {
    melancholic = {
        concepts = {"time", "emotion", "nature"},
        templates = {"medium", "complex", "simple"},
        adjective_bias = {"lost", "empty", "quiet", "cold", "distant", "heavy", "tired", "old"},
        verb_bias = {"fades", "passes", "vanishes", "aches", "waits", "remembers"},
        lineCount = {4, 8},
        shortLineChance = 0.3,
    },
    hopeful = {
        concepts = {"nature", "time", "body"},
        templates = {"simple", "medium", "statement"},
        adjective_bias = {"warm", "bright", "new", "open", "gentle", "alive", "young"},
        verb_bias = {"grows", "rises", "blooms", "returns", "mends", "opens", "arrives"},
        lineCount = {3, 6},
        shortLineChance = 0.4,
    },
    surreal = {
        concepts = {"abstract", "body", "nature"},
        templates = {"complex", "question", "medium"},
        adjective_bias = {"impossible", "strange", "imagined", "hollow", "vast", "small"},
        verb_bias = {"becomes", "shifts", "disappears", "means", "reveals", "hides"},
        lineCount = {5, 10},
        shortLineChance = 0.2,
    },
    observational = {
        concepts = {"nature", "body", "time"},
        templates = {"simple", "statement", "medium"},
        adjective_bias = {"quiet", "small", "still", "familiar", "simple", "clear"},
        verb_bias = {"remains", "waits", "settles", "holds", "sees", "stays"},
        lineCount = {3, 5},
        shortLineChance = 0.5,
    },
    fierce = {
        concepts = {"emotion", "body", "abstract"},
        templates = {"statement", "complex", "question"},
        adjective_bias = {"sharp", "raw", "fierce", "loud", "true", "necessary", "wild"},
        verb_bias = {"burns", "breaks", "screams", "matters", "exists", "becomes"},
        lineCount = {4, 7},
        shortLineChance = 0.25,
    },
}

------------------------------------------------------------------------
-- Utility
------------------------------------------------------------------------

local rng = Random.new()

local function pick(list: {string}): string
    return list[rng:NextInteger(1, #list)]
end

local function tableContains(t: {string}, val: string): boolean
    for _, v in t do
        if v == val then return true end
    end
    return false
end

------------------------------------------------------------------------
-- Engine state (per-generation, not persistent)
------------------------------------------------------------------------

type EngineState = {
    voice: typeof(VOICES.melancholic),
    voiceName: string,
    usedWords: { [string]: boolean },
}

local function newState(voiceName: string?): EngineState
    local name = voiceName or pick({"melancholic", "hopeful", "surreal", "observational", "fierce"})
    return {
        voice = VOICES[name],
        voiceName = name,
        usedWords = {},
    }
end

------------------------------------------------------------------------
-- Word selection (respects voice biases, reduces repetition)
------------------------------------------------------------------------

local function getWord(state: EngineState, wordType: string, concept: string?): string
    local c = concept or pick(state.voice.concepts)
    local wordList = WORDS[c][wordType]

    -- Determine bias key: "adjectives" -> "adjective_bias", "verbs" -> "verb_bias"
    local biasKey = string.sub(wordType, 1, -2) .. "_bias"  -- strip trailing 's', add '_bias'
    local biasWords = state.voice[biasKey]

    local word: string
    if biasWords and rng:NextNumber() < 0.6 then
        -- Filter bias words that exist in this concept's word list
        local valid = {}
        for _, bw in biasWords do
            if tableContains(wordList, bw) then
                table.insert(valid, bw)
            end
        end
        word = #valid > 0 and pick(valid) or pick(wordList)
    else
        word = pick(wordList)
    end

    -- Reduce repetition (try up to 5 times)
    local attempts = 0
    while state.usedWords[word] and attempts < 5 do
        word = pick(wordList)
        attempts += 1
    end

    state.usedWords[word] = true
    return word
end

------------------------------------------------------------------------
-- Template filling
------------------------------------------------------------------------

local function fillTemplate(state: EngineState, template: string): string
    local concept1 = pick(state.voice.concepts)
    local concept2 = pick(state.voice.concepts)

    local replacements = {
        ["{article}"] = pick(ARTICLES),
        ["{adj}"] = getWord(state, "adjectives", concept1),
        ["{adj2}"] = getWord(state, "adjectives", concept2),
        ["{noun}"] = getWord(state, "nouns", concept1),
        ["{noun2}"] = getWord(state, "nouns", concept2),
        ["{verb}"] = getWord(state, "verbs", concept1),
        ["{verb2}"] = getWord(state, "verbs", concept2),
        ["{preposition}"] = pick(PREPOSITIONS),
        ["{connector}"] = pick(CONNECTORS),
    }

    local result = template
    for key, value in replacements do
        result = string.gsub(result, key, value, 1)
    end

    return result
end

local function generateLine(state: EngineState, templateType: string?): string
    local tt = templateType or pick(state.voice.templates)
    local template = pick(TEMPLATES[tt])
    return fillTemplate(state, template)
end

------------------------------------------------------------------------
-- Public API
------------------------------------------------------------------------

--[[
    Generate a full poem. Returns { lines: {string}, voice: string }.
]]
function PoetryEngine.generatePoem(voiceName: string?): { lines: {string}, voice: string }
    local state = newState(voiceName)
    local minLines, maxLines = state.voice.lineCount[1], state.voice.lineCount[2]
    local numLines = rng:NextInteger(minLines, maxLines)

    local lines = {}
    for i = 1, numLines do
        local templateType: string
        if i == 1 then
            templateType = pick({"simple", "statement", "medium"})
        elseif i == numLines then
            templateType = pick({"simple", "statement"})
        else
            templateType = pick(state.voice.templates)
        end

        local line = generateLine(state, templateType)

        -- Sometimes truncate for rhythm
        if rng:NextNumber() < state.voice.shortLineChance then
            local commaPos = string.find(line, ",")
            if commaPos then
                line = string.sub(line, 1, commaPos - 1)
            else
                local thePos = string.find(line, " the ", 5)
                if thePos then
                    line = string.sub(line, 1, thePos - 1)
                end
            end
        end

        table.insert(lines, line)
    end

    -- Occasional stanza break
    if numLines > 5 and rng:NextNumber() < 0.5 then
        local breakPoint = rng:NextInteger(3, numLines - 1)
        table.insert(lines, breakPoint, "")
    end

    return { lines = lines, voice = state.voiceName }
end

--[[
    Generate a haiku (5-7-5). Returns { lines: {string}, voice: string }.
]]
function PoetryEngine.generateHaiku(): { lines: {string}, voice: string }
    local state = newState(pick({"observational", "melancholic", "surreal"}))

    local lines = {}
    for _, syllableCount in {5, 7, 5} do
        local template = pick(HAIKU_LINES[syllableCount])
        table.insert(lines, fillTemplate(state, template))
    end

    return { lines = lines, voice = state.voiceName }
end

--[[
    Generate a couplet (two lines). Returns { lines: {string}, voice: string }.
]]
function PoetryEngine.generateCouplet(): { lines: {string}, voice: string }
    local state = newState()

    local line1 = generateLine(state, "medium")
    local line2 = generateLine(state, "simple")

    return { lines = {line1, line2}, voice = state.voiceName }
end

--[[
    Generate a fragment (one line). Returns { lines: {string}, voice: string }.
]]
function PoetryEngine.generateFragment(): { lines: {string}, voice: string }
    local state = newState()

    local templateType = rng:NextNumber() < 0.5 and "simple" or "medium"
    local line = generateLine(state, templateType)

    return { lines = {line}, voice = state.voiceName }
end

--[[
    Generate by form name. Returns { lines: {string}, voice: string }.
]]
function PoetryEngine.generate(form: string, voiceName: string?): { lines: {string}, voice: string }
    if form == "haiku" then
        return PoetryEngine.generateHaiku()
    elseif form == "couplet" then
        return PoetryEngine.generateCouplet()
    elseif form == "fragment" then
        return PoetryEngine.generateFragment()
    else
        return PoetryEngine.generatePoem(voiceName)
    end
end

return PoetryEngine
