#!/usr/bin/env python3

# by TheTechromancer

from password_stretcher.lib.mutator import Mutator
import itertools


class Cap(Mutator):
    """Capitalize words in various ways."""
    # roughly the number of capital mutations when capswap is disabled
    cap_multiplier = 4
    scale = 2
    fname = 'capitalization'

    def __init__(self, _input, limit=256, capswap=False):

        self.capswap = capswap
        # the average number of words produced by the cap() (not capswap)

        super().__init__(_input, limit)


    def __len__(self):

        if not self.capswap:
            return self.cap_multiplier
        return self.limit


    def mutate(self, word: str):

        # always yield the most likely candidates first
        results = []
        for r in [word, word.lower(), word.upper(), word.swapcase(), word.capitalize(), word.title()]:
            if r not in results:
                results.append(r)
                yield r

        # then move on to full cap mutations if requested
        if self.capswap:
            for r in self._capswap(word):
                if r not in results:
                    yield r


    def _capswap(self, word):

        if isinstance(word, bytes):
            options = []
            for char in word:
                b = bytes([char])
                if b.isalpha():
                    options.append((b, b.swapcase()))
                else:
                    options.append((b,))
            for combo in itertools.product(*options):
                yield b''.join(combo)
        else:
            options = []
            for char in word:
                if char.isalpha():
                    options.append((char, char.swapcase()))
                else:
                    options.append((char,))
            for combo in itertools.product(*options):
                yield ''.join(combo)
