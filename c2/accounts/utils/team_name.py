import random

class TeamName(object):
    """
    Simple class to generate a random team name.

    """
    ADJECTIVES = (
        "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
        "summer", "icy", "quiet", "white", "cool", "winter", "quick",
        "patient", "twilight", "crimson", "wispy", "weathered", "blue",
        "broken", "cold", "damp", "falling", "frosty", "green",
        "lingering", "bold", "little", "morning", "muddy", "old",
        "red", "rough", "still", "small", "sparkling", "tasty", "shy",
        "wandering", "withered", "wild", "black", "mellow" "holy", "solitary",
        "snowy", "proud", "floral", "restless", "divine",
        "ancient", "purple", "lively", "nameless"
    )

    NOUNS = (
        "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
        "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
        "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
        "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
        "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
        "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
        "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
        "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
        "frog", "smoke", "star"
    )

    ANIMAL_NOUNS = (
        "alligators", "crocodiles", "ants", "antelopes", "badgers", "bees",
        "buffalos", "butterflies", "cheetahs", "coyotes", "dolphins", "elephants",
        "foxes", "giraffes", "gorillas", "hedgehogs", "hornets", "hyenas", "jackals",
        "kangaroos", "leopards", "lions", "lizards", "mammoths", "porcupines",
        "rabbits", "racoons", "rhinos", "sharks", "snails", "snakes", "spiders",
        "squirrels", "tigers", "wasps", "whales", "wolves", "wombats", "zebras"
    )

    def __init__(self):
        self.names = [random.choice(self.ADJECTIVES),
                      random.choice(self.ANIMAL_NOUNS)]

    def __unicode__(self):
        return u' '.join(self.names).title()

    def __repr__(self):
        return '<TeamName: %s, %s>' % (str(self), self.identifer)

    @property
    def identifer(self):
        return "%s-%s" % ('-'.join(self.names), random.randint(1,99))