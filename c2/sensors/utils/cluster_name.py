import random

def generate_cluster_name():
    """
    Simple method to generate a random cluster name.

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
        "ancient", "purple", "lively", "nameless", "tossed"
    )

    ANIMAL_NOUNS = (
        "alligators", "crocodiles", "ants", "antelopes", "badgers", "bees",
        "buffalos", "butterflies", "cheetahs", "coyotes", "dolphins", "elephants",
        "foxes", "giraffes", "gorillas", "hedgehogs", "hornets", "hyenas", "jackals",
        "kangaroos", "leopards", "lions", "lizards", "mammoths", "porcupines",
        "rabbits", "racoons", "rhinos", "sharks", "snails", "snakes", "spiders",
        "squirrels", "tigers", "wasps", "whales", "wolves", "wombats", "zebras", "salad"
    )

    return u"%s %s" % (random.choice(ADJECTIVES), random.choice(ANIMAL_NOUNS), )
