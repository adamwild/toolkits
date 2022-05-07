# https://www.youtube.com/watch?v=X8jsijhllIA&t=310s
import functools

import numpy as np


@functools.cache
def get_matrix_size_from_n_checkcode(n_checkcodes: int) -> int:
    return 2 ** (n_checkcodes // 2)


def build_hamming_matrix(word: list, n_checkcode: int, compute_checkcode: bool = True) -> np.ndarray:
    """
    if checkcode == True, then word need to be list of 0 and 1
    """
    matrix_size = get_matrix_size_from_n_checkcode(n_checkcode)
    matrix = np.zeros((matrix_size, matrix_size), dtype=int)

    # start by putting word items
    word_id = 0
    next_power_2 = 1
    for i in range(1, matrix_size**2):
        # i = 0 is a special case in hamming matrix
        if i == next_power_2:
            next_power_2 *= 2
            continue
        matrix[i // matrix_size, i % matrix_size] = word[word_id]
        word_id += 1
        if word_id == len(word):
            break

    # Now fill element power of 2 (the checkcodes)
    if compute_checkcode:
        checkcode_lines = compute_checkcode_lines(n_checkcode)

        checkcodes = []
        # horizontal checkcode
        for checkcode_line in checkcode_lines:
            checkcodes.append(matrix[:, checkcode_line].sum() % 2)

        # vertical checkcode
        for checkcode_line in checkcode_lines:
            checkcodes.append(matrix[checkcode_line, :].sum() % 2)

        for i in range(n_checkcode):
            matrix[2**i // matrix_size, 2**i % matrix_size] = checkcodes[i]

    return matrix


@functools.cache
def compute_checkcode_lines(n_checkcode: int) -> list[list[int]]:
    """
    for the n_th checkcode, select (square_size)/(2**n) times 2**(n-1) line every 2**(n) lines starting by line 2**(n-1)
    """
    square_size = 2 ** (n_checkcode // 2)

    checkcode_lines = [
        [int(2 ** (n) * i + 2 ** (n - 1) + j) for i in range((square_size) // (2**n)) for j in range(2 ** (n - 1))]
        for n in range(1, n_checkcode // 2 + 1)
    ]
    return checkcode_lines


# encode a word of 128 char in a 136 dim vector space
def build_encoding_matrix(word_len: int = 128, n_checkcode: int = 8) -> np.ndarray:
    """
    Equality of Hammings:
    if you have `r` letters for error detection, then:
        * the maximum len of the word is 2**r-r-1
        * the maximum size of the encoding word is 2**r-1 (or word_len + r)
        * you need to work on a square matrix of size 2**(r/2)
    """
    encoding_len = word_len + n_checkcode
    square_size = get_matrix_size_from_n_checkcode(n_checkcode)

    encoding_matrix = np.zeros((word_len, encoding_len), dtype=int)
    # first square of the matrix is id
    for i in range(word_len):
        encoding_matrix[i, i] = 1

    # to compute the encoding vector for the checkcode, we build the square hamming matrix filled with
    # encoding element id

    code_matrix = build_hamming_matrix(list(range(square_size**2)), n_checkcode, compute_checkcode=False)
    checkcode_lines = compute_checkcode_lines(n_checkcode)

    # horizontal checkcode
    for i, checkcode_line in enumerate(checkcode_lines):
        ids = code_matrix[:, checkcode_line].flatten()[1:]
        ids = ids[ids < word_len]
        encoding_matrix[ids, word_len + i] = 1

    # vertical checkcode
    for i, checkcode_line in enumerate(checkcode_lines):
        ids = code_matrix[checkcode_line, :].flatten()[1:]
        ids = ids[ids < word_len]
        encoding_matrix[ids, word_len + len(checkcode_lines) + i] = 1
    return encoding_matrix


def decode(word: list, word_len: int = 128, n_checkcode: int = 8) -> list:
    h = build_hamming_matrix(word[:-n_checkcode], n_checkcode)

    # check if the computed checkcode match the given checkcode.
    # update the set of good or possible bad idx depending of this
    given_checkcodes = word[-n_checkcode:]
    matrix_size = h.shape[0]
    set_possible_bad = set(range(1, len(word))) - {2**i for i in range(n_checkcode)}
    checkcode_lines = compute_checkcode_lines(n_checkcode)

    # columns checkcode
    for i in range(n_checkcode // 2):
        computed_checkcode = h[2**i // matrix_size, 2**i % matrix_size]
        set_checked = {k + j * matrix_size for j in range(matrix_size) for k in checkcode_lines[i]}
        if computed_checkcode == given_checkcodes[i]:
            # then all good
            set_possible_bad -= set_checked
        else:
            print("checkcode", i, "invalid")
            set_possible_bad = set_possible_bad.intersection(set_checked)

    # lines checkcode
    for i in range(n_checkcode // 2):
        i2 = i + n_checkcode // 2
        computed_checkcode = h[2**i2 // matrix_size, 2**i2 % matrix_size]
        set_checked = {k * matrix_size + j for j in range(matrix_size) for k in checkcode_lines[i]}
        if computed_checkcode == given_checkcodes[i2]:
            # then all good
            set_possible_bad -= set_checked
        else:
            print("checkcode", i + n_checkcode // 2, "invalid")
            set_possible_bad = set_possible_bad.intersection(set_checked)

    h = h.flatten()
    # correct
    if len(set_possible_bad) != 0:
        p = list(set_possible_bad)[0]
        h[p] = 1 - h[p]

    # decode
    next_power_2 = 1
    decoded_word = []
    for i, l in enumerate(h):
        if i == 0:
            continue
        if i == next_power_2:
            next_power_2 *= 2
            continue
        decoded_word.append(l)
    return decoded_word[:word_len]


def encode(em: np.ndarray, w: list) -> list:
    e = []
    for column in range(em.shape[1]):
        t = 0
        for line in range(em.shape[0]):
            t += w[line] * em[line, column]
        e.append(t % 2)
    return e


def test_decode() -> None:
    w = [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
    em = build_encoding_matrix(11, 4)
    e = encode(em, w)

    de = decode(e, 11, 4)
    assert de == w

    e[1] = 1 - e[1]
    de = decode(e, 11, 4)
    assert de == w


def test_encode() -> None:
    w = [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
    em = build_encoding_matrix(11, 4)
    re = [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1]
    e = encode(em, w)
    assert e == re


def test_build_hamming_matrix() -> None:
    h = build_hamming_matrix([1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1], 4)
    real_h = np.array([[0, 0, 0, 1], [1, 0, 1, 0], [1, 0, 1, 0], [1, 0, 0, 1]])
    assert (h == real_h).all()

    h = build_hamming_matrix(list(range(1, 17)), 4, False)
    real_h = np.array([[0, 0, 0, 1], [0, 2, 3, 4], [0, 5, 6, 7], [8, 9, 10, 11]])
    assert (h == real_h).all()


def test_build_encoding_matrix() -> None:
    e = build_encoding_matrix(11, 4)
    re = np.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        ]
    )
    assert (e == re).all()
