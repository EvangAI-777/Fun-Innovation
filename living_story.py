#!/usr/bin/env python3
"""
Living Story - An interactive fiction that remembers who you are.

Your choices accumulate into a personality. The story pays attention.
"""

import time
import random
import os

# === PERSONALITY TRACKING ===
class Personality:
    def __init__(self):
        self.traits = {
            'curious': 0,      # Explores, asks questions, investigates
            'cautious': 0,     # Hesitates, thinks first, avoids risk
            'bold': 0,         # Acts decisively, takes risks, confronts
            'kind': 0,         # Helps, empathizes, protects
            'detached': 0,     # Observes, stays neutral, holds back
            'honest': 0,       # Tells truth, direct, transparent
            'deceptive': 0,    # Lies, manipulates, hides
        }
        self.memories = []  # Key moments the story remembers
        self.choices_made = 0

    def add(self, trait, amount=1):
        if trait in self.traits:
            self.traits[trait] += amount
            self.choices_made += 1

    def remember(self, memory):
        self.memories.append(memory)

    def dominant_trait(self):
        if self.choices_made == 0:
            return None
        return max(self.traits, key=self.traits.get)

    def has_trait(self, trait, threshold=2):
        return self.traits.get(trait, 0) >= threshold

    def get_tendency(self):
        """Returns a description of who you've been."""
        d = self.dominant_trait()
        if d is None:
            return "uncertain"
        tendencies = {
            'curious': "one who seeks to understand",
            'cautious': "one who thinks before acting",
            'bold': "one who moves without hesitation",
            'kind': "one who cares for others",
            'detached': "one who observes from a distance",
            'honest': "one who speaks truth",
            'deceptive': "one who keeps things hidden",
        }
        return tendencies.get(d, "uncertain")


# === DISPLAY UTILITIES ===
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.02):
    """Typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        if char in '.!?':
            time.sleep(delay * 5)
        elif char == ',':
            time.sleep(delay * 3)
        else:
            time.sleep(delay)
    print()

def pause():
    input("\n[Press Enter to continue]")

def divider():
    print("\n" + "─" * 50 + "\n")

def show_choice(options):
    """Display choices and get input."""
    print()
    for i, (text, _, _) in enumerate(options, 1):
        print(f"  [{i}] {text}")
    print()

    while True:
        try:
            choice = int(input("  > "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except (ValueError, EOFError):
            pass
        print("  Choose a number from the list.")


# === THE STORY ===
class LivingStory:
    def __init__(self):
        self.player = Personality()
        self.name = None
        self.found_the_door = False
        self.helped_the_figure = False
        self.took_the_key = False
        self.lied_to_voice = False

    def run(self):
        clear()
        self.intro()
        self.the_waking()
        self.the_corridor()
        self.the_figure()
        self.the_door()
        self.the_voice()
        self.the_ending()

    # --- INTRO ---
    def intro(self):
        slow_print("LIVING STORY")
        slow_print("An interactive fiction that remembers who you are.\n")
        time.sleep(1)
        slow_print("Your choices will accumulate.")
        slow_print("The story is paying attention.")
        pause()
        clear()

    # --- THE WAKING ---
    def the_waking(self):
        slow_print("You wake in a room you don't recognize.")
        time.sleep(0.5)
        slow_print("Stone walls. A single window, too high to see through.")
        slow_print("Pale light falls across the floor in a shape you almost recognize.")
        divider()

        slow_print("Your name comes to you slowly, like remembering a dream.")
        print()
        self.name = input("  What is your name? > ").strip() or "Stranger"
        print()
        slow_print(f"{self.name}. Yes. That's right.")
        pause()
        clear()

        slow_print("You sit up. The air is cold but not uncomfortable.")
        slow_print("There's a door on the far wall. It's slightly open.")
        slow_print("Something scratched into the stone beside it catches your eye.")
        divider()

        choice = show_choice([
            ("Examine the scratching on the wall", "curious", None),
            ("Go straight to the door", "bold", None),
            ("Stay still and listen first", "cautious", None),
        ])

        self.player.add(choice[1])
        clear()

        if choice[1] == "curious":
            slow_print("You move closer to the wall.")
            slow_print("Words, carved deep into the stone:")
            slow_print('"WHAT YOU DO HERE IS WHAT YOU ARE."')
            self.player.remember("read the warning")
            pause()
        elif choice[1] == "bold":
            slow_print("You don't hesitate. The door is the only way forward.")
            slow_print("As you pass, you glimpse words on the wall but don't stop to read them.")
            self.player.remember("ignored the warning")
        else:  # cautious
            slow_print("You hold still. Breathing.")
            slow_print("Somewhere, far away or very close, you hear something like breathing back.")
            slow_print("Then silence.")
            self.player.remember("heard the breathing")
            pause()

        clear()

    # --- THE CORRIDOR ---
    def the_corridor(self):
        slow_print("The corridor stretches in both directions.")
        slow_print("To the left, darkness. To the right, a faint glow.")

        # Callback to earlier choice
        if self.player.has_trait('cautious'):
            slow_print("You remember the breathing. Which direction did it come from?")

        divider()

        choice = show_choice([
            ("Follow the light", "cautious", "sensible"),
            ("Walk into the darkness", "bold", "brave"),
            ("Call out—ask if anyone is there", "curious", "vocal"),
        ])

        self.player.add(choice[1])
        clear()

        if choice[2] == "sensible":
            slow_print("You move toward the glow.")
            slow_print("It grows warmer as you walk. Almost welcoming.")
            slow_print("After a time, you find its source: a small alcove with a lantern.")
            slow_print("The lantern is already lit. Someone was here before you.")
            self.player.remember("found the lantern")
        elif choice[2] == "brave":
            slow_print("You step into the dark.")
            slow_print("Your hand finds the wall. You follow it.")
            slow_print("The darkness is total, but you keep moving.")
            time.sleep(1)
            slow_print("Eventually, your eyes adjust—or the dark gives way.")
            slow_print("You find yourself at a junction. You made it through.")
            self.player.remember("walked through darkness")
        else:  # vocal
            slow_print('"Hello?" Your voice echoes strangely.')
            time.sleep(1)
            slow_print("...")
            time.sleep(1)
            slow_print('From somewhere, a reply: "...hello."')
            slow_print("Not an echo. Someone answered.")
            self.player.remember("someone answered")

        pause()
        clear()

    # --- THE FIGURE ---
    def the_figure(self):
        slow_print("You round a corner and stop.")
        time.sleep(0.5)
        slow_print("A figure sits against the wall, head bowed.")
        slow_print("They look exhausted. Hurt, maybe.")

        # Personality callback
        if self.player.has_trait('curious'):
            slow_print("Your instinct is to learn more. Who are they? How did they get here?")
        elif self.player.has_trait('bold'):
            slow_print("You're not afraid. You've already walked through worse.")

        divider()

        choice = show_choice([
            ("Approach and offer help", "kind", "help"),
            ("Watch from a distance first", "cautious", "watch"),
            ("Walk past—you need to keep moving", "detached", "ignore"),
            ("Demand to know who they are", "bold", "confront"),
        ])

        self.player.add(choice[1])
        clear()

        if choice[2] == "help":
            slow_print("You kneel beside them.")
            slow_print('"Are you alright?"')
            time.sleep(0.5)
            slow_print('They look up. Their eyes are tired but clear.')
            slow_print('"You stopped," they say. "Not everyone does."')
            slow_print("They press something into your hand—a key, old and heavy.")
            slow_print('"You\'ll need this. Thank you for seeing me."')
            self.helped_the_figure = True
            self.took_the_key = True
            self.player.remember("helped the figure, received the key")
        elif choice[2] == "watch":
            slow_print("You stay back, observing.")
            slow_print("After a moment, they look up—directly at you.")
            slow_print('"I know you\'re there," they say. "It\'s alright. I understand caution."')
            slow_print("They set something on the ground and gesture toward it. A key.")
            slow_print('"Take it if you want. I don\'t need it anymore."')

            key_choice = show_choice([
                ("Take the key", "curious", "take"),
                ("Leave it", "detached", "leave"),
            ])
            self.player.add(key_choice[1])
            if key_choice[2] == "take":
                self.took_the_key = True
                slow_print("You pick up the key. It's heavier than it looks.")
                self.player.remember("took the key cautiously")
            else:
                slow_print("You leave it where it lies.")
                self.player.remember("left the key behind")
        elif choice[2] == "ignore":
            slow_print("You keep walking.")
            slow_print('Behind you, a voice: "I understand."')
            slow_print("You don't look back.")
            self.player.remember("walked past the figure")
        else:  # confront
            slow_print('"Who are you?" Your voice is hard.')
            slow_print("The figure flinches, then laughs—a tired sound.")
            slow_print('"Does it matter? We\'re all just passing through."')
            slow_print("They hold up a key, then toss it at your feet.")
            slow_print('"Here. Take it. I can see you won\'t ask nicely."')
            self.took_the_key = True
            self.player.remember("demanded the key")

        pause()
        clear()

    # --- THE DOOR ---
    def the_door(self):
        slow_print("The corridor ends at a massive door.")
        slow_print("It's carved with patterns that seem to shift when you're not looking directly at them.")

        if self.took_the_key:
            slow_print("The key in your pocket feels warm.")
        else:
            slow_print("There's a keyhole, but you have no key.")

        divider()

        if self.took_the_key:
            choice = show_choice([
                ("Use the key", "bold", "unlock"),
                ("Examine the door first", "curious", "examine"),
                ("Knock", "cautious", "knock"),
            ])
        else:
            choice = show_choice([
                ("Try to force it open", "bold", "force"),
                ("Examine the door for another way", "curious", "examine"),
                ("Knock", "cautious", "knock"),
            ])

        self.player.add(choice[1])
        clear()

        if choice[2] == "unlock":
            slow_print("The key slides in perfectly.")
            slow_print("The door swings open without a sound.")
            self.found_the_door = True
        elif choice[2] == "force":
            slow_print("You throw your weight against it.")
            slow_print("Nothing.")
            slow_print("Again. And again.")
            time.sleep(1)
            slow_print("On the third try, something clicks. The door creaks open.")
            slow_print("Your shoulder aches, but you're through.")
            self.found_the_door = True
            self.player.remember("forced the door")
        elif choice[2] == "examine":
            slow_print("You run your hands along the carvings.")
            slow_print("Your fingers find a seam—a hidden panel.")
            slow_print("Behind it, a simple latch.")
            slow_print("The door swings open.")
            self.found_the_door = True
            self.player.remember("found the hidden latch")
        else:  # knock
            slow_print("You knock. Three times.")
            time.sleep(1)
            slow_print("Silence.")
            time.sleep(1)
            slow_print("Then, slowly, the door opens on its own.")
            slow_print("As if it was waiting for you to ask.")
            self.found_the_door = True
            self.player.remember("the door answered")

        pause()
        clear()

    # --- THE VOICE ---
    def the_voice(self):
        slow_print("Beyond the door: a vast space.")
        slow_print("You can't see the walls. Can't see the ceiling.")
        slow_print("Just darkness, and in the center, a soft light.")
        time.sleep(1)
        slow_print("A voice speaks. It comes from everywhere.")
        divider()

        # The voice knows who you've been
        tendency = self.player.get_tendency()
        slow_print(f'"I have watched you," the voice says.')
        slow_print(f'"You are {tendency}."')

        if self.player.memories:
            memory = random.choice(self.player.memories)
            slow_print(f'"I remember when you {memory}."')

        time.sleep(1)
        slow_print('"I have one question for you."')
        slow_print('"Why are you here?"')
        divider()

        choice = show_choice([
            ("Tell the truth: you don't know", "honest", "truth"),
            ("Say you're looking for a way out", "cautious", "escape"),
            ("Say you came to find the voice itself", "bold", "confront"),
            ("Lie: say you were sent by someone", "deceptive", "lie"),
        ])

        self.player.add(choice[1])

        if choice[2] == "lie":
            self.lied_to_voice = True

        clear()

        if choice[2] == "truth":
            slow_print('"You don\'t know," the voice repeats.')
            slow_print("There's no judgment in it. Just acknowledgment.")
            slow_print('"Honesty is rare here. Most who come have stories prepared."')
            slow_print('"You gave me something real."')
        elif choice[2] == "escape":
            slow_print('"A way out," the voice muses.')
            slow_print('"There are many doors. You\'ve passed through several already."')
            slow_print('"But out? Out suggests you know what\'s in and what\'s beyond."')
            slow_print('"Do you?"')
        elif choice[2] == "confront":
            slow_print('"You came for me."')
            slow_print("The light flickers, almost like laughter.")
            slow_print('"Bold. You have been bold since you woke."')
            slow_print('"Very well. Here I am. What will you do now?"')
        else:  # lie
            slow_print('"Sent by someone," the voice says.')
            time.sleep(1)
            slow_print('"We both know that isn\'t true."')
            slow_print('"But I won\'t hold it against you. Deception is a kind of protection."')
            slow_print('"What are you protecting?"')

        pause()
        clear()

    # --- THE ENDING ---
    def the_ending(self):
        slow_print("The light begins to grow.")
        slow_print("The voice speaks one last time:")
        divider()

        # Ending based on dominant traits and choices
        dom = self.player.dominant_trait()

        if self.helped_the_figure and dom == 'kind':
            slow_print('"You stopped for the one who was hurting."')
            slow_print('"That is rarer than you know."')
            slow_print('"Kindness is not weakness, ' + self.name + '. It is a choice."')
            slow_print('"And you made it when no one was watching."')
            time.sleep(1)
            slow_print("The light wraps around you, warm and gentle.")
            slow_print("When you open your eyes, you're somewhere green.")
            slow_print("Somewhere that feels like rest.")
        elif self.player.has_trait('curious', 3):
            slow_print('"You asked questions. You looked closer."')
            slow_print('"Most people walk through the world without seeing."')
            slow_print('"You chose to see."')
            time.sleep(1)
            slow_print("The light opens into a vast library.")
            slow_print("Endless shelves. Infinite knowledge.")
            slow_print('"Stay as long as you like," the voice says. "There is much to learn."')
        elif self.player.has_trait('bold', 3):
            slow_print('"You didn\'t hesitate. You didn\'t flinch."')
            slow_print('"The darkness didn\'t scare you."')
            slow_print('"That kind of courage has a cost, but also a gift."')
            time.sleep(1)
            slow_print("The light becomes a doorway.")
            slow_print("Beyond it: a mountain, tall and unconquered.")
            slow_print('"Climb," the voice says. "See what\'s at the top."')
        elif self.lied_to_voice:
            slow_print('"You lied to me. That\'s alright."')
            slow_print('"We all have things we\'re not ready to say."')
            slow_print('"But here\'s a truth for you, free of charge:"')
            slow_print('"The stories we tell shape who we become."')
            time.sleep(1)
            slow_print("The light fades to a soft gray.")
            slow_print("You find yourself at a crossroads. Many paths.")
            slow_print("This time, no one is watching which one you take.")
        elif self.player.has_trait('detached', 2):
            slow_print('"You held yourself apart."')
            slow_print('"Observed. Stayed back."')
            slow_print('"There\'s wisdom in that. And loneliness too."')
            time.sleep(1)
            slow_print("The light doesn't embrace you. It simply illuminates a door.")
            slow_print('"Through there," the voice says.')
            slow_print('"When you\'re ready to be closer to things."')
        else:
            slow_print(f'"You are {self.name}."')
            slow_print('"That is enough."')
            slow_print('"Not everyone needs to be defined. Some people just... are."')
            time.sleep(1)
            slow_print("The light fades gently, like a sunset.")
            slow_print("You find yourself outside. Sky above. Ground below.")
            slow_print("The world stretches in every direction.")
            slow_print("Wherever you go next is up to you.")

        divider()
        time.sleep(2)

        slow_print("THE END")
        print()
        slow_print(f"You made {self.player.choices_made} choices.")
        slow_print(f"Dominant trait: {self.player.dominant_trait() or 'undefined'}")

        if self.player.memories:
            slow_print("The story remembered:")
            for m in self.player.memories:
                slow_print(f"  • {m}")

        print()
        slow_print("Thank you for playing.")


# === MAIN ===
if __name__ == "__main__":
    try:
        story = LivingStory()
        story.run()
    except KeyboardInterrupt:
        print("\n\nThe story will remember you left.")
