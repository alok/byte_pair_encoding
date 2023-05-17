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

# %%
ALPHABET = string.ascii_letters
SAMPLE_TEXT = "aaabdaaabac"

CODON = 2  # Bio term for readframe length
DEPTH = 3
MIN_FREQ = 2

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
    # TODO replace string.punctuation with more general thing
    # replacements=dict(zip(pairs,collections.deque(string.punctuation)))
    replacements: list[bidict.bidict] = []
    replacement_char_set = set(zhon.cedict.traditional)
    while True:
        pairs = collections.Counter(itertools.pairwise(s))
        replacement_chars = []
        for _ in range(len(pairs)):
            replacement_chars.append(replacement_char_set.pop())

        replacement = bidict.bidict(
            zip(
                (p for p, ct in pairs.items() if ct > 1),
                replacement_chars,
            )
        )
        replacements.append(replacement)

        new = s
        for pair, new_char in replacement.items():
            new = new.replace("".join(pair), new_char)
        print(f"{s} -> {new}")
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
            print(f"{new}")
    return new


assert (rev_bpe(*bpe(SAMPLE_TEXT))) == SAMPLE_TEXT

# TODO replace string.punctuation with more general thing
# replacements=dict(zip(pairs,collections.deque(string.punctuation)))
replacements: list[bidict.bidict] = []
REPLACEMENT_CHAR_SET = set(zhon.cedict.traditional)
while True:
    pairs = collections.Counter(itertools.pairwise(sample))
    REPLACEMENT_CHARS = []
    for _ in range(len(pairs)):
        REPLACEMENT_CHARS.append(REPLACEMENT_CHAR_SET.pop())

    replacement = bidict.bidict(
        zip((p for p, ct in pairs.items() if ct > 1), REPLACEMENT_CHARS)
    )
    # print(replacement)
    replacements.append(replacement)
    new_sample = sample
    for pair, new_char in replacement.items():
        # print(f"{pair=}")
        new_sample = new_sample.replace("".join(pair), new_char)
    print(f"{sample} -> {new_sample}")
    if len(new_sample) < len(sample):
        sample = new_sample
    else:
        break


# rev
for replacement in reversed(replacements):
    r = replacement.inv
    for new_char, pair in r.items():
        new_sample = new_sample.replace(new_char, "".join(pair))
        print(f"{new_sample}")

newest_sample = new_sample
print(f"{newest_sample, SAMPLE_TEXT = }")
assert newest_sample == SAMPLE_TEXT
# %%

with urllib.request.urlopen(
    "https://en.wikipedia.org/wiki/Byte_pair_encoding"
) as response:
    html = response.read().decode("utf-8")
    print(html)
# %%
