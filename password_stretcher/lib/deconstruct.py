import re
from typing import ClassVar

from password_stretcher.lib.mutator import Mutator


class Deconstruct(Mutator):

    word_regexes: ClassVar[list[re.Pattern[bytes]]] = [re.compile(r, re.IGNORECASE) for r in [
        rb'\w+',
        rb'[0-9]+',
        rb'[\w0-9]+',
        rb'[a-z]+',
        rb'[a-z0-9]+',
        rb'[a-z-]+',
        rb'[a-z0-9-]+'
    ]]

    def __init__(self, _input, limit=256):

        super().__init__(_input, limit)


    def mutate(self, word):

        yield word
        for r in self.word_regexes:
            yield from r.findall(word)
