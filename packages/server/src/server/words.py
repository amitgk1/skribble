import random


class WordManager:
    def __init__(self, words):
        """
        initializes the WordManager with a pool of words.
        It creates a list of all words (full_word_pool),
        a set of available words (available_words),
        and a set of used words (used_words) to track the words that have already been chosen
        """
        self.full_word_pool = list(words)
        self.available_words = set(words)
        self.used_words = set()

    def get_word_options(self, count=3):
        """
        Returns a list of count random words from the available word pool.
        If there aren't enough words left, it raises an error.
        """
        if len(self.available_words) < count:
            raise ValueError("Not enough words left to choose from. Please reset.")

        options = random.sample(sorted(self.available_words), count)
        return options

    def pick_word(self, word):
        """
        Removes the chosen word from the available words pool and adds it to the used words set.
        If the word is not available or has already been picked, it raises an error
        """
        if word not in self.available_words:
            raise ValueError(f"The word '{word}' is not available or already picked.")

        self.available_words.remove(word)
        self.used_words.add(word)

    def reset(self):
        """Resets the word pool by restoring all words to the available words set and clears the used words set"""
        self.available_words = set(self.full_word_pool)
        self.used_words.clear()


drawable_words = [
    "apple",
    "car",
    "house",
    "dog",
    "cat",
    "tree",
    "sun",
    "moon",
    "boat",
    "phone",
    "computer",
    "bottle",
    "ball",
    "shoe",
    "glasses",
    "hat",
    "fish",
    "star",
    "book",
    "key",
    "chair",
    "door",
    "table",
    "bed",
    "pencil",
    "cup",
    "cake",
    "camera",
    "broom",
    "toothbrush",
    "ice cream",
    "pizza",
    "burger",
    "lamp",
    "watch",
    "radio",
    "guitar",
    "drum",
    "violin",
    "airplane",
    "train",
    "bus",
    "truck",
    "bicycle",
    "tent",
    "flag",
    "ladder",
    "hammer",
    "cloud",
    "snowman",
]
