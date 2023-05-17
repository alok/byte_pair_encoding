# %%
import string
import collections
import zhon.cedict
import itertools
import bidict
import tyro
from dataclasses import dataclass, replace
from typing import Sequence, Mapping
import urllib.request
import urllib.response
import zhon.hanzi
import zhon.pinyin
import zhon.zhuyin
import zhon.cedict

# %%
ALPHABET = string.ascii_letters
SAMPLE_TEXT = "aaabdaaabac"

CODON = 2  # Bio term for readframe length
DEPTH = 3
MIN_FREQ = 100

not_in_sample = set(ALPHABET) - set(SAMPLE_TEXT)  # alphabet minus sampletext members

text = SAMPLE_TEXT
luc_dict = {}

# # Megan's attempt

# for _ in range(DEPTH):
#     splt = [text[i : i + CODON] for i in range(0, len(text), CODON)]
#     # get frequency table? (intuition that this probably isn't especially efficient)
#     frequency = collections.Counter(
#         splt
#     ).most_common()  # ...seems to auto spit out most common first? TODO:doublecheck this
#     while True:
#         p, n = frequency.popitem()
#         print(f{'p='})
#         if n < MIN_FREQ:
#             break

#         s = not_in_sample.pop()
#         print(f'f{p,s=}')
#         luc_dict.update({s: p})
#         text = text.replace(p, s)

# print(text)
# print(luc_dict)

# # %%
# # ## pseudocode
# # text2 = SAMPLE_TEXT
# # lut_dict = dict()
# #
# # for all common_pairs in SAMPLE_TEXT:
# #     add to lut_dict
# #     replace in text_2
# #
# # for all common_pairs in text_2:
# #     add to lut_dict
# #     replace in text_2
# #
# # ## todo: set up so you can use a variable to set depth of recursion
# # ## (note that in this implementation, you also need to know depth to de-convert; {X:ab, Y:bc, Z:XY})

# %%
sample = SAMPLE_TEXT


def bpe(s: str) -> tuple[str, list[bidict.bidict]]:
    """As decadent Western pig, this uses Chinese characters as the complement of text."""
    replacements: list[bidict.bidict] = []

    replacement_char_set = set(
        itertools.chain(
            zhon.cedict.traditional, zhon.hanzi.characters, zhon.zhuyin.characters
        )
    )

    while True:
        # TODO really want more_itertools.chunk (ignore last char)
        pairs = collections.Counter(itertools.pairwise(s))
        pairs = ["".join(p) for p, ct in pairs.items() if ct > MIN_FREQ]
        # TODO 'most common' optimization
        # pairs = pairs.most_common(1)
        replacement_chars = []

        for _ in range(len(pairs)):
            replacement_chars.append(replacement_char_set.pop())

        replacement = bidict.bidict(
            zip(
                pairs,
                replacement_chars,
            )
        )
        replacements.append(replacement)

        new = s
        for pair, new_char in replacement.items():
            new = new.replace("".join(pair), new_char)

        if len(new) < len(s):
            s = new
        else:
            break
    return s, replacements


def rev_bpe(s: str, replacements: list[bidict.bidict]) -> str:
    # rev
    new = s
    for replacement in reversed(replacements):
        for new_char, pair in replacement.inv.items():
            new = new.replace(new_char, "".join(pair))

    return new


# TODO add hypothesis test
def test_bpe(s: str):
    encoded, replacements = bpe(s)
    out = rev_bpe(encoded, replacements)
    assert out == s


test_bpe(SAMPLE_TEXT)
# %%


# %%
with urllib.request.urlopen(
    "https://en.wikipedia.org/wiki/Byte_pair_encoding"
) as response:
    html: str = response.read().decode("utf-8")[:12_500]
    test_bpe(html)
# TODO: extend to byte-level BPE to handle bigger vocabs https://huggingface.co/learn/nlp-course/chapter6/5
# %%
