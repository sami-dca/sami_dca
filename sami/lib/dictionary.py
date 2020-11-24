# -*- coding: UTF8 -*-

# Atom regex : ([A-Za-z]{1,})

dictionary = {
    "adjectives": [  # Source : https://enchantedlearning.com/wordlist/adjectivesforpeople.shtml
        "able",
        "abnormal",
        "adventurous",
        "affectionate",
        "agile",
        "agreeable",
        "alert",
        "amazing",
        "ambitious",
        "amiable",
        "amusing",
        "analytical",
        "angelic",
        "apathetic",
        "apprehensive",
        "ardent",
        "artificial",
        "artistic",
        "assertive",
        "attentive",
        "average",
        "awesome",
        "awful",
        "balanced",
        "beautiful",
        "beneficent",
        "blue",
        "blunt",
        "boisterous",
        "brave",
        "bright",
        "brilliant",
        "buff",
        "callous",
        "candid",
        "cantankerous",
        "capable",
        "careful",
        "careless",
        "caustic",
        "cautious",
        "charming",
        "cheerful",
        "chic",
        "childish",
        "childlike",
        "churlish",
        "circumspect",
        "civil",
        "clean",
        "clever",
        "clumsy",
        "coherent",
        "cold",
        "competent",
        "composed",
        "conceited",
        "condescending",
        "confident",
        "confused",
        "conscientious",
        "considerate",
        "content",
        "cool",
        "cooperative",
        "cordial",
        "courageous",
        "cowardly",
        "crabby",
        "crafty",
        "cranky",
        "crass",
        "critical",
        "cruel",
        "curious",
        "cynical",
        "dainty",
        "decisive",
        "deep",
        "deferential",
        "deft",
        "delicate",
        "delightful",
        "demonic",
        "demure",
        "dependent",
        "depressed",
        "devoted",
        "dextrous",
        "diligent",
        "direct",
        "dirty",
        "disagreeable",
        "discerning",
        "discreet",
        "disruptive",
        "distant",
        "distraught",
        "distrustful",
        "dowdy",
        "dramatic",
        "dreary",
        "drowsy",
        "drugged",
        "drunk",
        "dull",
        "dutiful",
        "eager",
        "earnest",
        "efficient",
        "egotistical",
        "elfin",
        "emotional",
        "energetic",
        "enterprising",
        "enthusiastic",
        "evasive",
        "exacting",
        "excellent",
        "excitable",
        "experienced",
        "fabulous",
        "fastidious",
        "ferocious",
        "fervent",
        "fiery",
        "flabby",
        "flaky",
        "flashy",
        "frank",
        "friendly",
        "funny",
        "fussy",
        "generous",
        "gentle",
        "gloomy",
        "gluttonous",
        "good",
        "grave",
        "great",
        "groggy",
        "grouchy",
        "guarded",
        "hateful",
        "hearty",
        "helpful",
        "hesitant",
        "hypercritical",
        "hysterical",
        "idiotic",
        "idle",
        "illogical",
        "imaginative",
        "immature",
        "immodest",
        "impatient",
        "imperturbable",
        "impetuous",
        "impractical",
        "impressionable",
        "impressive",
        "impulsive",
        "inactive",
        "incisive",
        "incompetent",
        "inconsiderate",
        "inconsistent",
        "indefatigable",
        "independent",
        "indiscreet",
        "indolent",
        "industrious",
        "inexperienced",
        "insensitive",
        "inspiring",
        "intelligent",
        "interesting",
        "intolerant",
        "inventive",
        "irascible",
        "irritable",
        "irritating",
        "jocular",
        "jovial",
        "joyous",
        "judgmental",
        "keen",
        "kind",
        "lame",
        "lazy",
        "lean",
        "leery",
        "lethargic",
        "listless",
        "lithe",
        "lively",
        "local",
        "logical",
        "lovable",
        "lovely",
        "maternal",
        "mature",
        "mean",
        "meddlesome",
        "mercurial",
        "methodical",
        "meticulous",
        "mild",
        "miserable",
        "modest",
        "moronic",
        "morose",
        "motivated",
        "musical",
        "naive",
        "nasty",
        "natural",
        "naughty",
        "negative",
        "nervous",
        "noisy",
        "normal",
        "nosy",
        "numb",
        "obliging",
        "obnoxious",
        "orderly",
        "ostentatious",
        "outgoing",
        "outspoken",
        "passionate",
        "passive",
        "paternal",
        "paternalistic",
        "patient",
        "peaceful",
        "peevish",
        "pensive",
        "persevering",
        "persnickety",
        "petulant",
        "picky",
        "plain",
        "playful",
        "pleasant",
        "plucky",
        "polite",
        "popular",
        "positive",
        "powerful",
        "practical",
        "prejudiced",
        "pretty",
        "proficient",
        "proud",
        "provocative",
        "prudent",
        "punctual",
        "quarrelsome",
        "querulous",
        "quick",
        "quiet",
        "realistic",
        "reassuring",
        "reclusive",
        "reliable",
        "reluctant",
        "resentful",
        "reserved",
        "resigned",
        "resourceful",
        "respected",
        "respectful",
        "responsible",
        "restless",
        "revered",
        "ridiculous",
        "sad",
        "sassy",
        "saucy",
        "sedate",
        "selfish",
        "sensible",
        "sensitive",
        "sentimental",
        "serene",
        "serious",
        "sharp",
        "shrewd",
        "shy",
        "silly",
        "sincere",
        "sleepy",
        "slight",
        "sloppy",
        "slothful",
        "slovenly",
        "slow",
        "smart",
        "snazzy",
        "sneering",
        "snobby",
        "sober",
        "somber",
        "sophisticated",
        "soulful",
        "soulless",
        "sour",
        "spirited",
        "spiteful",
        "stable",
        "staid",
        "steady",
        "stern",
        "stoic",
        "striking",
        "strong",
        "stupid",
        "sturdy",
        "subtle",
        "sulky",
        "sullen",
        "supercilious",
        "superficial",
        "surly",
        "suspicious",
        "sweet",
        "tactful",
        "tactless",
        "talented",
        "testy",
        "thinking",
        "thoughtful",
        "thoughtless",
        "timid",
        "tired",
        "tolerant",
        "touchy",
        "tranquil",
        "ugly",
        "unaffected",
        "unbalanced",
        "uncertain",
        "uncooperative",
        "undependable",
        "unemotional",
        "unfriendly",
        "unguarded",
        "unhelpful",
        "unimaginative",
        "unmotivated",
        "unpleasant",
        "unpopular",
        "unreliable",
        "unsophisticated",
        "unstable",
        "unsure",
        "unthinking",
        "unwilling",
        "venal",
        "versatile",
        "vigilant",
        "volcanic",
        "vulnerable",
        "warm",
        "warmhearted",
        "wary",
        "watchful",
        "weak",
        "willing",
        "wonderful",
        "zealous",
    ],
    "animals": [  # Source : https://a-z-animals.com/animals/
        "aardvark",
        "abyssinian",
        "affenpinscher",
        "akbash",
        "akita",
        "albatross",
        "alligator",
        "angelfish",
        "ant",
        "anteater",
        "antelope",
        "armadillo",
        "avocet",
        "axolotl",
        "baboon",
        "badger",
        "balinese",
        "bandicoot",
        "barb",
        "barnacle",
        "barracuda",
        "bat",
        "beagle",
        "bear",
        "beaver",
        "beetle",
        "binturong",
        "bird",
        "birman",
        "bison",
        "bloodhound",
        "bobcat",
        "bombay",
        "bongo",
        "bonobo",
        "booby",
        "budgerigar",
        "buffalo",
        "bulldog",
        "bullfrog",
        "burmese",
        "butterfly",
        "caiman",
        "camel",
        "capybara",
        "caracal",
        "cassowary",
        "cat",
        "caterpillar",
        "catfish",
        "centipede",
        "chameleon",
        "chamois",
        "cheetah",
        "chicken",
        "chihuahua",
        "chimpanzee",
        "chinchilla",
        "chinook",
        "chipmunk",
        "cichlid",
        "coati",
        "cockroach",
        "collie",
        "coral",
        "cougar",
        "cow",
        "coyote",
        "crab",
        "crane",
        "crocodile",
        "cuscus",
        "cuttlefish",
        "dachshund",
        "dalmatian",
        "deer",
        "dhole",
        "dingo",
        "discus",
        "dodo",
        "dog",
        "dolphin",
        "donkey",
        "dormouse",
        "dragonfly",
        "drever",
        "duck",
        "dugong",
        "dunker",
        "eagle",
        "earwig",
        "echidna",
        "elephant",
        "emu",
        "falcon",
        "ferret",
        "fish",
        "flamingo",
        "flounder",
        "fly",
        "fossa",
        "fox",
        "frigatebird",
        "frog",
        "gar",
        "gecko",
        "gerbil",
        "gharial",
        "gibbon",
        "giraffe",
        "goat",
        "goose",
        "gopher",
        "gorilla",
        "grasshopper",
        "greyhound",
        "grouse",
        "guppy",
        "hamster",
        "hare",
        "harrier",
        "havanese",
        "hedgehog",
        "heron",
        "himalayan",
        "hippopotamus",
        "horse",
        "human",
        "hyena",
        "ibis",
        "iguana",
        "impala",
        "indri",
        "insect",
        "jackal",
        "jaguar",
        "javanese",
        "jellyfish",
        "kakapo",
        "kangaroo",
        "kingfisher",
        "kiwi",
        "koala",
        "kudu",
        "labradoodle",
        "ladybug",
        "lemming",
        "lemur",
        "leopard",
        "liger",
        "lion",
        "lionfish",
        "lizard",
        "llama",
        "lobster",
        "lynx",
        "macaw",
        "magpie",
        "maltese",
        "manatee",
        "mandrill",
        "markhor",
        "mastiff",
        "mayfly",
        "meerkat",
        "millipede",
        "mole",
        "molly",
        "mongoose",
        "mongrel",
        "monkey",
        "moorhen",
        "moose",
        "moth",
        "mouse",
        "mule",
        "neanderthal",
        "newfoundland",
        "newt",
        "nightingale",
        "numbat",
        "ocelot",
        "octopus",
        "okapi",
        "olm",
        "opossum",
        "ostrich",
        "otter",
        "oyster",
        "pademelon",
        "panther",
        "parrot",
        "peacock",
        "pekingese",
        "pelican",
        "penguin",
        "persian",
        "pheasant",
        "pig",
        "pika",
        "pike",
        "piranha",
        "platypus",
        "pointer",
        "poodle",
        "porcupine",
        "possum",
        "prawn",
        "puffin",
        "pug",
        "puma",
        "quail",
        "quetzal",
        "quokka",
        "quoll",
        "rabbit",
        "raccoon",
        "ragdoll",
        "rat",
        "rattlesnake",
        "reindeer",
        "rhinoceros",
        "robin",
        "rottweiler",
        "salamander",
        "saola",
        "scorpion",
        "seahorse",
        "seal",
        "serval",
        "sheep",
        "shrimp",
        "siamese",
        "siberian",
        "skunk",
        "sloth",
        "snail",
        "snake",
        "snowshoe",
        "somali",
        "sparrow",
        "sponge",
        "squid",
        "squirrel",
        "starfish",
        "stingray",
        "stoat",
        "swan",
        "tang",
        "tapir",
        "tarsier",
        "termite",
        "tetra",
        "tiffany",
        "tiger",
        "tortoise",
        "toucan",
        "tropicbird",
        "tuatara",
        "turkey",
        "uakari",
        "uguisu",
        "umbrellabird",
        "vulture",
        "wallaby",
        "walrus",
        "warthog",
        "wasp",
        "weasel",
        "whippet",
        "wildebeest",
        "wolf",
        "wolverine",
        "wombat",
        "woodlouse",
        "woodpecker",
        "wrasse",
        "yak",
        "zebra",
        "zebu",
        "zonkey",
        "zorse",
    ]
}


def count_possibilities(dic):
    """
    Counts how many unique names can be created from the
    combinations of each lists contained in the passed dictionary.
    """
    total = 0
    for value in dic:
        total *= len(dic[value])
    return total
