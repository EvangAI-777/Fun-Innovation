#!/usr/bin/env python3
"""
Verse Engine - A poetry generator with personality.

Different voices, different forms, occasionally surprising output.
"""

import random
import re

# === WORD BANKS BY CONCEPT ===
WORDS = {
    'nature': {
        'nouns': ['river', 'stone', 'mountain', 'forest', 'rain', 'moon', 'sun', 'wind',
                  'leaf', 'root', 'branch', 'seed', 'cloud', 'storm', 'snow', 'tide',
                  'shore', 'field', 'meadow', 'valley', 'peak', 'dawn', 'dusk', 'star'],
        'verbs': ['flows', 'grows', 'falls', 'rises', 'drifts', 'settles', 'breaks',
                  'bends', 'reaches', 'fades', 'blooms', 'withers', 'returns', 'remains'],
        'adjectives': ['quiet', 'ancient', 'patient', 'wild', 'still', 'distant',
                       'hollow', 'deep', 'vast', 'small', 'cold', 'warm', 'soft', 'sharp']
    },
    'time': {
        'nouns': ['moment', 'year', 'hour', 'second', 'memory', 'future', 'past',
                  'yesterday', 'tomorrow', 'century', 'instant', 'eternity', 'age', 'era'],
        'verbs': ['passes', 'lingers', 'vanishes', 'stretches', 'collapses', 'waits',
                  'returns', 'escapes', 'holds', 'releases', 'forgets', 'remembers'],
        'adjectives': ['brief', 'endless', 'fleeting', 'slow', 'sudden', 'inevitable',
                       'lost', 'found', 'borrowed', 'stolen', 'given', 'taken']
    },
    'emotion': {
        'nouns': ['grief', 'joy', 'longing', 'peace', 'fear', 'hope', 'love', 'loss',
                  'silence', 'laughter', 'sorrow', 'wonder', 'doubt', 'faith', 'rage'],
        'verbs': ['aches', 'sings', 'whispers', 'screams', 'settles', 'rises', 'fades',
                  'burns', 'cools', 'breaks', 'mends', 'waits', 'arrives', 'departs'],
        'adjectives': ['heavy', 'light', 'sharp', 'dull', 'bright', 'dark', 'tender',
                       'fierce', 'gentle', 'raw', 'numb', 'alive', 'quiet', 'loud']
    },
    'body': {
        'nouns': ['hands', 'eyes', 'heart', 'bones', 'skin', 'breath', 'voice', 'blood',
                  'mouth', 'fingers', 'chest', 'shoulders', 'spine', 'tongue', 'teeth'],
        'verbs': ['holds', 'sees', 'beats', 'breaks', 'touches', 'breathes', 'speaks',
                  'carries', 'reaches', 'closes', 'opens', 'trembles', 'steadies'],
        'adjectives': ['tired', 'young', 'old', 'empty', 'full', 'open', 'closed',
                       'scarred', 'whole', 'broken', 'warm', 'cold', 'familiar', 'strange']
    },
    'abstract': {
        'nouns': ['truth', 'nothing', 'everything', 'edge', 'center', 'distance', 'weight',
                  'shadow', 'light', 'name', 'word', 'story', 'question', 'answer', 'door'],
        'verbs': ['exists', 'disappears', 'means', 'becomes', 'remains', 'shifts',
                  'reveals', 'hides', 'asks', 'answers', 'matters', 'changes', 'stays'],
        'adjectives': ['true', 'false', 'real', 'imagined', 'possible', 'impossible',
                       'necessary', 'uncertain', 'clear', 'obscure', 'simple', 'complex']
    }
}

# === STRUCTURAL ELEMENTS ===
CONNECTORS = ['and', 'but', 'or', 'yet', 'still', 'though', 'while', 'as', 'like', 'when']
PREPOSITIONS = ['in', 'on', 'through', 'beneath', 'above', 'between', 'within', 'without', 'beyond', 'before', 'after']
ARTICLES = ['the', 'a', 'this', 'that', 'each', 'every', 'no', 'some']

# === LINE TEMPLATES ===
TEMPLATES = {
    'simple': [
        "{article} {adj} {noun}",
        "{noun} {verb}",
        "{adj} {noun}, {adj} {noun}",
        "{verb} the {noun}",
        "{preposition} the {noun}",
    ],
    'medium': [
        "{article} {adj} {noun} {verb}",
        "the {noun} {verb} {preposition} {noun2}",
        "{adj} as {article} {noun}",
        "where {noun} {verb}",
        "what the {noun} {verb}",
        "{noun} and {noun2}, {verb}",
    ],
    'complex': [
        "the {adj} {noun} {verb} {preposition} the {adj2} {noun2}",
        "like {article} {noun} that {verb} {preposition} {noun2}",
        "{preposition} the {adj} {noun}, {article} {noun2} {verb}",
        "even the {noun} {verb} when {noun2} {verb2}",
        "not {article} {noun}, but the {adj} {noun2}",
    ],
    'question': [
        "what {verb} in the {noun}?",
        "where does the {noun} {verb}?",
        "why {verb} the {adj} {noun}?",
        "who {verb} the {noun}?",
        "is this {article} {noun} or {article} {noun2}?",
    ],
    'statement': [
        "this is the {noun}",
        "here, the {noun} {verb}",
        "there is no {adj} {noun}",
        "only the {noun} {verb}",
        "all {noun} {verb}",
    ]
}

# === VOICE CONFIGURATIONS ===
VOICES = {
    'melancholic': {
        'concepts': ['time', 'emotion', 'nature'],
        'templates': ['medium', 'complex', 'simple'],
        'adjective_bias': ['lost', 'empty', 'quiet', 'cold', 'distant', 'heavy', 'tired', 'old'],
        'verb_bias': ['fades', 'passes', 'vanishes', 'aches', 'waits', 'remembers'],
        'line_count': (4, 8),
        'short_line_chance': 0.3,
    },
    'hopeful': {
        'concepts': ['nature', 'time', 'body'],
        'templates': ['simple', 'medium', 'statement'],
        'adjective_bias': ['warm', 'bright', 'new', 'open', 'gentle', 'alive', 'young'],
        'verb_bias': ['grows', 'rises', 'blooms', 'returns', 'mends', 'opens', 'arrives'],
        'line_count': (3, 6),
        'short_line_chance': 0.4,
    },
    'surreal': {
        'concepts': ['abstract', 'body', 'nature'],
        'templates': ['complex', 'question', 'medium'],
        'adjective_bias': ['impossible', 'strange', 'imagined', 'hollow', 'vast', 'small'],
        'verb_bias': ['becomes', 'shifts', 'disappears', 'means', 'reveals', 'hides'],
        'line_count': (5, 10),
        'short_line_chance': 0.2,
    },
    'observational': {
        'concepts': ['nature', 'body', 'time'],
        'templates': ['simple', 'statement', 'medium'],
        'adjective_bias': ['quiet', 'small', 'still', 'familiar', 'simple', 'clear'],
        'verb_bias': ['remains', 'waits', 'settles', 'holds', 'sees', 'stays'],
        'line_count': (3, 5),
        'short_line_chance': 0.5,
    },
    'fierce': {
        'concepts': ['emotion', 'body', 'abstract'],
        'templates': ['statement', 'complex', 'question'],
        'adjective_bias': ['sharp', 'raw', 'fierce', 'loud', 'true', 'necessary', 'wild'],
        'verb_bias': ['burns', 'breaks', 'screams', 'matters', 'exists', 'becomes'],
        'line_count': (4, 7),
        'short_line_chance': 0.25,
    }
}

# === HAIKU TEMPLATES (5-7-5 approximation) ===
HAIKU_LINES = {
    5: [  # ~5 syllables
        "{adj} {noun}",
        "the {noun} {verb}",
        "{noun} and {noun2}",
        "{preposition} the {noun}",
        "a {adj} {noun}",
        "{verb} the {noun}",
    ],
    7: [  # ~7 syllables
        "the {adj} {noun} {verb}",
        "{noun} {verb} {preposition} {noun2}",
        "{adj} {noun}, {adj} {noun2}",
        "where the {adj} {noun} {verb}",
        "{preposition} the {adj} {noun}",
    ]
}


class VerseEngine:
    def __init__(self):
        self.voice = None
        self.used_words = set()  # Avoid too much repetition

    def set_voice(self, voice_name):
        if voice_name in VOICES:
            self.voice = VOICES[voice_name]
        else:
            self.voice = random.choice(list(VOICES.values()))

    def get_word(self, word_type, concept=None):
        """Get a word, respecting voice biases."""
        if concept is None:
            concept = random.choice(self.voice['concepts'])

        word_list = WORDS[concept][word_type].copy()

        # Apply bias if exists
        bias_key = f'{word_type[:-1]}_bias'  # 'adjectives' -> 'adjective_bias'
        if bias_key in self.voice:
            bias_words = [w for w in self.voice[bias_key] if w in word_list]
            if bias_words and random.random() < 0.6:
                word = random.choice(bias_words)
            else:
                word = random.choice(word_list)
        else:
            word = random.choice(word_list)

        # Track usage to reduce repetition
        attempts = 0
        while word in self.used_words and attempts < 5:
            word = random.choice(word_list)
            attempts += 1

        self.used_words.add(word)
        return word

    def fill_template(self, template):
        """Fill a template with words."""
        result = template

        # Get concepts for this line
        concept1 = random.choice(self.voice['concepts'])
        concept2 = random.choice(self.voice['concepts'])

        replacements = {
            '{article}': random.choice(ARTICLES),
            '{adj}': self.get_word('adjectives', concept1),
            '{adj2}': self.get_word('adjectives', concept2),
            '{noun}': self.get_word('nouns', concept1),
            '{noun2}': self.get_word('nouns', concept2),
            '{verb}': self.get_word('verbs', concept1),
            '{verb2}': self.get_word('verbs', concept2),
            '{preposition}': random.choice(PREPOSITIONS),
            '{connector}': random.choice(CONNECTORS),
        }

        for key, value in replacements.items():
            result = result.replace(key, value, 1)

        return result

    def generate_line(self, template_type=None):
        """Generate a single line."""
        if template_type is None:
            template_type = random.choice(self.voice['templates'])

        template = random.choice(TEMPLATES[template_type])
        return self.fill_template(template)

    def generate_poem(self, voice_name=None):
        """Generate a complete poem."""
        self.used_words.clear()

        if voice_name:
            self.set_voice(voice_name)
        else:
            self.set_voice(random.choice(list(VOICES.keys())))

        min_lines, max_lines = self.voice['line_count']
        num_lines = random.randint(min_lines, max_lines)

        lines = []
        for i in range(num_lines):
            # Vary template types throughout poem
            if i == 0:
                # Opening line - often simple or statement
                template_type = random.choice(['simple', 'statement', 'medium'])
            elif i == num_lines - 1:
                # Closing line - often simple or statement
                template_type = random.choice(['simple', 'statement'])
            else:
                template_type = random.choice(self.voice['templates'])

            line = self.generate_line(template_type)

            # Sometimes create short lines for rhythm
            if random.random() < self.voice['short_line_chance']:
                # Truncate to first phrase
                if ',' in line:
                    line = line.split(',')[0]
                elif ' the ' in line[4:]:  # Keep at least first word
                    idx = line.index(' the ', 4)
                    line = line[:idx]

            lines.append(line)

        # Add occasional line breaks for stanzas
        if num_lines > 5 and random.random() < 0.5:
            break_point = random.randint(2, num_lines - 2)
            lines.insert(break_point, '')

        return '\n'.join(lines)

    def generate_haiku(self):
        """Generate a haiku (5-7-5)."""
        self.used_words.clear()
        self.set_voice(random.choice(['observational', 'melancholic', 'surreal']))

        lines = []
        for syllable_count in [5, 7, 5]:
            template = random.choice(HAIKU_LINES[syllable_count])
            lines.append(self.fill_template(template))

        return '\n'.join(lines)

    def generate_couplet(self):
        """Generate a two-line poem."""
        self.used_words.clear()
        self.set_voice(random.choice(list(VOICES.keys())))

        line1 = self.generate_line('medium')
        line2 = self.generate_line('simple')

        return f"{line1}\n{line2}"

    def generate_fragment(self):
        """Generate a poetic fragment - just a line or two."""
        self.used_words.clear()
        self.set_voice(random.choice(list(VOICES.keys())))

        if random.random() < 0.5:
            return self.generate_line('simple')
        else:
            return self.generate_line('medium')


def display_menu():
    print("\n" + "=" * 50)
    print("  VERSE ENGINE")
    print("  A poetry generator with personality")
    print("=" * 50)
    print("\n  [1] Generate poem (random voice)")
    print("  [2] Generate poem (choose voice)")
    print("  [3] Generate haiku")
    print("  [4] Generate couplet")
    print("  [5] Generate fragment")
    print("  [6] Batch generate (5 poems)")
    print("  [q] Quit")
    print()


def voice_menu():
    print("\n  Voices:")
    print("    [1] Melancholic - loss, memory, weight")
    print("    [2] Hopeful - growth, light, opening")
    print("    [3] Surreal - strange, shifting, dreamlike")
    print("    [4] Observational - quiet, still, noticing")
    print("    [5] Fierce - sharp, urgent, alive")
    print()


def main():
    engine = VerseEngine()
    voices = ['melancholic', 'hopeful', 'surreal', 'observational', 'fierce']

    print("\n" + "~" * 50)
    print("  Welcome to Verse Engine")
    print("  Press Enter after each poem for the next")
    print("~" * 50)

    while True:
        display_menu()
        choice = input("  > ").strip().lower()

        if choice == 'q':
            print("\n  // end transmission //\n")
            break

        elif choice == '1':
            print("\n" + "-" * 40)
            print(engine.generate_poem())
            print("-" * 40)

        elif choice == '2':
            voice_menu()
            v = input("  > ").strip()
            try:
                voice_idx = int(v) - 1
                if 0 <= voice_idx < len(voices):
                    print("\n" + "-" * 40)
                    print(f"  [{voices[voice_idx]}]\n")
                    print(engine.generate_poem(voices[voice_idx]))
                    print("-" * 40)
                else:
                    print("  Invalid choice.")
            except ValueError:
                print("  Invalid choice.")

        elif choice == '3':
            print("\n" + "-" * 40)
            print(engine.generate_haiku())
            print("-" * 40)

        elif choice == '4':
            print("\n" + "-" * 40)
            print(engine.generate_couplet())
            print("-" * 40)

        elif choice == '5':
            print("\n" + "-" * 40)
            print(engine.generate_fragment())
            print("-" * 40)

        elif choice == '6':
            print("\n" + "=" * 50)
            for i, voice in enumerate(voices):
                print(f"\n  [{voice}]\n")
                print(engine.generate_poem(voice))
                if i < len(voices) - 1:
                    print("\n" + "~" * 40)
            print("\n" + "=" * 50)

        else:
            print("  Unknown option.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  // silence //\n")
