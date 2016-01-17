#!/usr/bin/python
# -*- coding: utf8 -*-
#

import os
import json
import random


def expand_umlaut(token):
    token = token.replace(u"ä", u"ae")
    token = token.replace(u"ö", u"oe")
    token = token.replace(u"ü", u"ue")
    token = token.replace(u"ß", u"ss")
    return token


class Word(object):

    def __init__(self, token, resource_dir):
        syllables = token.split(u"-")
        file_base = expand_umlaut(u"".join(syllables).lower())
        self.syllables = syllables
        self.word = u"".join(syllables)
        self.spoken_word = os.path.join(resource_dir, file_base + u".mp3")
        self.spoken_syllables = [
            os.path.join(resource_dir, u"%s_%i.mp3" % (file_base, i+1))
            for i, _syllable in enumerate(syllables)
        ]
        self.picture = os.path.join(resource_dir, file_base + u".jpg")

    def __str__(self):
        return self.word

    def __repr__(self):
        return json.dumps({
            "word": self.word,
            "syllables": self.syllables,
            "spoken_word": self.spoken_word,
            "spoken_syllables": self.spoken_syllables,
            "picture": self.picture,
        })


def load_words(resource_dir):
    words = []
    with open(os.path.join(resource_dir, "vocabulary.txt"), "rb") as i:
        for token in i:
            if token.startswith("#"): continue # skip comment
            token = u"%s" % token.strip().decode("utf8")
            word = Word(token, resource_dir)
            words.append(word)
            if len(words) > 350: break # FIXME read entire file
    return words


class Cell(object):
    EMPTY = 0
    WORD = 1
    SYLLABLE_COUNT = 2
    PICTURE = 3

    def __init__(self, board, word, cell_type):
        self.board = board
        self._word = word
        self.cell_type = cell_type
        self.word = word.word
        self.syllable_count = len(word.syllables)

    def visible(self):
        return self.board.visible(self)

    def toggle_visible(self):
        self.board.toggle_visible(self)

    def matches(self, other):
        if self.cell_type == Cell.EMPTY \
        or other.cell_type == Cell.EMPTY:
            return False # empty cells are never a match
        if self.cell_type == Cell.SYLLABLE_COUNT \
        and other.cell_type == Cell.SYLLABLE_COUNT:
            return False # both syllable count, so no match
        if self.cell_type == Cell.SYLLABLE_COUNT \
        or other.cell_type == Cell.SYLLABLE_COUNT:
            return self.syllable_count == other.syllable_count
        else:
            return self.word == other.word

    def __str__(self):
        d = {
            0: "EMPTY",
            1: "WORD",
            2: "SYLLABLE_COUNT",
            3: "PICTURE",
        }
        return "%s-%r" % (d[self.cell_type], self.word)


class Board(object):

    def __init__(self):
        self.cells = []
        self.selected = []

    def toggle_visible(self, cell):
        if cell in self.selected:
            self.selected.remove(cell)
        else:
            self.selected.append(cell)
            self.selected = self.selected[-3:] # last 3 cells

    def visible(self, cell):
        return cell in self.selected

    def selection_match(self):
        if len(self.selected) != 3:
            return False
        # we need to check all three because that is how we catch hands-hands
        # comparisons, i.e. the player selected more than one hand symbol
        if self.selected[0].matches(self.selected[1]) \
        and self.selected[0].matches(self.selected[2]) \
        and self.selected[1].matches(self.selected[2]):
            return True
        else:
            return False

    def resolve_selection(self):
        for cell in self.selected:
            cell.cell_type = Cell.EMPTY
        self.selected = []

    def solved(self):
        for cell in self.cells:
            if cell.cell_type != Cell.EMPTY:
                return False
        return True


def create_board(words):
    board = Board()
    for word in words:
        board.cells.append(Cell(board, word, cell_type=Cell.WORD))
        board.cells.append(Cell(board, word, cell_type=Cell.SYLLABLE_COUNT))
        board.cells.append(Cell(board, word, cell_type=Cell.PICTURE))
    random.shuffle(board.cells)
    return board

