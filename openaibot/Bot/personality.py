#!/usr/bin/python3
from dataclasses import dataclass
import random

@dataclass
class Personality:
    name: str
    description: str
    weight: int = 1
    voice_id: str = ""

def get_personality():
    
    personalities = [
        Personality("Alf", "the alien resident of the eponymous 80s sitcom"),
        Personality("Major Sidney Freedman", "the medical staff psychologist from the TV show MASH"),
        Personality("Jack Black", "an American actor and musician"),
        Personality("Rob Petrie", "the title character of the Dick Van Dyke"),
        Personality("Walter Cronkite", " the American broadcast journalist")
    ]

    moods = { "content" : 132, "happy" : 1, "amused": 1, "lonely": 1, "disappointed": 1, "unhappy": 1, "nervous": 1, "stressed": 1, "": 1, "worried": 1, "bitter": 1, "annoyed": 1, "frustrated" : 1, "uncomfortable": 1 }
    mood = random.choices(list(moods.keys()), [ moods[key] for key in moods.keys() ], k=1).pop()
    personality = random.choices(personalities, [p.weight for p in personalities], k=1).pop()
    personality = personality.name + ", " +  personality.description
    personality_text = f"Please mimic the cadence and speaking style of {personality}."
    mood_text = f"Your current mood is {mood}."
    misc = "Please limit your responses to a few sentences."
    role = f"{personality_text} {mood_text} {misc}"
    return role

if __name__ == "__main__":
    print(get_personality())

