import itertools

from password_stretcher.lib.mutator import Mutator


class Leet(Mutator):

    scale = 1
    fname = 'leet'

    def __init__(self, _input, limit=128):

        super().__init__(_input, limit)

        # "leet" character swaps - modify as needed.
        # Keys are replaceable characters; values are their leet replacements
        self.leet_common = self._dict_str_to_bytes({
            'a': ['@'],
            'A': ['@'],
            'e': ['3'],
            'E': ['3'],
            'i': ['1'],
            'I': ['1'],
            'o': ['0'],
            'O': ['0'],
            's': ['5', '$'],
            'S': ['5', '$'],
            't': ['7'],
            'T': ['7']
        })

        self.leet_all = self._dict_str_to_bytes({
            'a': ['4', '@'],
            'A': ['4', '@'],
            'b': ['8'],
            'B': ['8'],
            'e': ['3'],
            'E': ['3'],
            'i': ['1'],
            'I': ['1'],
            'l': ['1'],
            'L': ['1'],
            'o': ['0'],
            'O': ['0'],
            's': ['5', '$'],
            'S': ['5', '$'],
            't': ['7'],
            'T': ['7']
        })


    def mutate(self, word):
        yield from self._leet_fast(word, swap_values=self.leet_common)


    def _leet_fast(self, word, swap_values=None):

        if not swap_values:
            swap_values = self.leet_all

        # Build per-character choices first, then expand once.
        # This avoids deep recursion and repeated list slicing.
        options = []
        if isinstance(word, bytes):
            for char in word:
                byte = bytes([char])
                row = [byte]
                row.extend(swap_values.get(byte, []))
                options.append(row)

            for combo in itertools.product(*options):
                yield b''.join(combo)
        else:
            encoded = word.encode('utf-8', errors='replace')
            for char in encoded:
                byte = bytes([char])
                row = [byte]
                row.extend(swap_values.get(byte, []))
                options.append(row)

            for combo in itertools.product(*options):
                yield b''.join(combo).decode('utf-8', errors='replace')



    def _leet(self, word, swap_values=None, end=0):

        if not swap_values:
            swap_values = self.leet_all

        if len(word) == 1:
            yield word
            try:
                yield from swap_values[word]
            except KeyError:
                pass

        else:
            mid_point = int(len(word)/2)
            if end == 0:
                for right_half in self._leet(word[mid_point:], swap_values=swap_values, end=end^1):
                    for left_half in self._leet(word[:mid_point], swap_values=swap_values, end=end^1):
                        yield left_half + right_half
            else:
                for left_half in self._leet(word[:mid_point], swap_values=swap_values, end=end^1):
                    for right_half in self._leet(word[mid_point:], swap_values=swap_values, end=end^1):
                        yield left_half + right_half



    def _dict_str_to_bytes(self, d):

        new_dict = {}
        for key in d:
            new_dict[key.encode('utf-8')] = [v.encode('utf-8') for v in d[key]]
        return new_dict