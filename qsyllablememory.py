#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import random

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt
from PyQt4.phonon import Phonon

from syllable_memory import load_words, Cell, create_board



class QCell(QWidget):

    def __init__(self, board_widget, cell, size=None, font_size=None):
        super(QCell, self).__init__()
        self.board_widget = board_widget
        self.font_size = font_size or 24
        self.size = size or (300, 200)
        self.cell = cell
        self.background_color = QColor(255, 255, 255)
        self.frame_color = QColor(30, 30, 30)
        self.setMinimumSize(*self.size)
        self.mouse_pressed = False

    def drawFrame(self, painter):
        painter.fillRect(
            0,
            0,
            self.size[0]-1,
            self.size[1]-1,
            self.background_color,
        )
        painter.setPen(self.frame_color)
        painter.drawRect(0, 0, self.size[0]-1, self.size[1]-1)

    def paintInvisible(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawFrame(painter)
        font = QFont("Helvetica", self.font_size * 2, QFont.Bold);
        text = QStaticText("?")
        text.prepare(font=font)
        x = (self.size[0] - text.size().width()) / 2
        y = (self.size[1] - text.size().height()) / 2
        painter.setFont(font)
        painter.setPen(self.frame_color)
        painter.drawStaticText(x, y, text)
        painter.end()

    def paintEmpty(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawFrame(painter)
        painter.setPen(self.frame_color)
        painter.drawLine(0, 0, self.size[0]-1, self.size[1]-1)
        painter.drawLine(0, self.size[1]-1, self.size[0]-1, 0)
        painter.end()

    def mousePressEvent(self, event):
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event):
        if not self.mouse_pressed:
            return # press was in another widget
        self.mouse_pressed = False
        if self.cell.cell_type == Cell.EMPTY:
            return
        self.cell.toggle_visible()
        self.repaint()
        QTimer.singleShot(0, self.checkSelection)

    def checkSelection(self):
        if self.cell.board.selection_match():
            # resolve match  in a moment
            QTimer.singleShot(300, self.goodSelection)

    def goodSelection(self):
        print "MATCH: ", map(str, self.cell.board.selected)
        self.cell.board.resolve_selection()
        if not self.cell.board.solved():
            self.board_widget.play("correct.ogg")
        else:
            print "SOLVED!"
            self.board_widget.play("finished.ogg")
            self.board_widget.start_game()
        QTimer.singleShot(0, self.board_widget.repaint)


class QCellPicture(QCell):

    def __init__(self, board_widget, cell, size=None, font_size=None):
        super(QCellPicture, self).__init__(board_widget, cell, size, font_size)

    def paintEvent(self, event):
        if self.cell.cell_type == Cell.EMPTY:
            return self.paintEmpty(event)
        if not self.cell.visible():
            return self.paintInvisible(event)
        self.board_widget.play(self.cell._word.spoken_word)
        painter = QPainter()
        painter.begin(self)
        self.drawFrame(painter)
        pixmap = QPixmap(os.path.join(os.getcwd(), self.cell._word.picture))
        pixmap = pixmap.scaled(self.size[0]-2, self.size[1]-2, Qt.KeepAspectRatio)
        x = (self.size[0] - pixmap.width()) / 2
        y = (self.size[1] - pixmap.height()) / 2
        painter.drawPixmap(max(x, 1), max(y, 1), pixmap)
        painter.end()


class QCellSyllableCount(QCell):

    def __init__(self, board_widget, cell, size=None, font_size=None):
        super(QCellSyllableCount, self).__init__(board_widget, cell, size, font_size)

    def paintEvent(self, event):
        if self.cell.cell_type == Cell.EMPTY:
            return self.paintEmpty(event)
        if not self.cell.visible():
            return self.paintInvisible(event)
        painter = QPainter()
        painter.begin(self)
        self.drawFrame(painter)
        font = QFont("Helvetica", self.font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        text = QStaticText("%i" % len(self.cell._word.syllables))
        text.prepare(font=font)
        x = (self.size[0] - text.size().width()) / 2
        y = (self.size[1] - text.size().height()) / 2
        painter.drawStaticText(x, y, text)
        painter.end()


class QCellWord(QCell):

    def __init__(self, board_widget, cell, size=None, font_size=None):
        super(QCellWord, self).__init__(board_widget, cell, size, font_size)

    def paintEvent(self, event):
        if self.cell.cell_type == Cell.EMPTY:
            return self.paintEmpty(event)
        if not self.cell.visible():
            return self.paintInvisible(event)
        font = QFont("Helvetica", self.font_size, QFont.Bold)
        colors = [ QColor(255, 0, 0), QColor(0, 0, 255) ]
        parts = []
        x = 0
        for i, syllable in enumerate(self.cell._word.syllables):
            text = QStaticText(syllable)
            text.prepare(font=font)
            y = (self.size[1] - text.size().height()) / 2
            parts.append((colors[i % 2], x, y, text))
            x += text.size().width()
        x_offset = (self.size[0] - x) / 2
        painter = QPainter()
        painter.begin(self)
        self.drawFrame(painter)
        painter.setFont(font)
        for color, x, y, text in parts:
            painter.setPen(color)
            painter.drawStaticText(x + x_offset, y, text)
        painter.end()


class QSyllableMemory(QWidget):

    def __init__(self, app, all_words):
        super(QSyllableMemory, self).__init__()
        random.shuffle(all_words)
        self.all_words = all_words
        self.app = app
        self.start_word = 0
        self.setWindowTitle("Syllable Memory") 
        self.layout = QGridLayout(self)
        self.layout.setRowStretch(3, 3)
        self.resize(900, 600)
        self.silence = Phonon.MediaSource("silence.ogg")
        self.player = Phonon.MediaObject(self)
        audio = Phonon.AudioOutput(Phonon.MusicCategory, self)
        audio.setMuted(False)
        audio.setVolume(50.0)
        Phonon.createPath(self.player, audio)
        print "AUDIO:", audio.outputDevice().name(), "at", audio.volume(), "%"
        self.player.aboutToFinish.connect(self.enqueue_silence)
        self.play("start.ogg")
        self.player.play()

    def enqueue_silence(self):
        self.player.enqueue(self.silence)

    def play(self, audio_fname):
        self.player.enqueue(Phonon.MediaSource(audio_fname))

    def start_game(self):
        self.board = create_board(
            self.all_words[self.start_word : self.start_word+3]
        )
        self.start_word += 3
        for i, cell in enumerate(self.board.cells):
            if cell.cell_type == Cell.WORD:
                widget = QCellWord(self, cell)
            elif cell.cell_type == Cell.SYLLABLE_COUNT:
                widget = QCellSyllableCount(self, cell)
            elif cell.cell_type == Cell.PICTURE:
                widget = QCellPicture(self, cell)
            else:
                print "unknown cell type", cell.cell_type
                widget = None
            self.layout.addWidget(widget, i / 3, i % 3)

    def run(self):
        self.start_game()
        self.show()
        sys.exit(self.app.exec_())


def qsyllablememory(args, words):
    app = QApplication(args)
    app.setApplicationName("qsyllablememory")
    qsm = QSyllableMemory(app, words)
    qsm.run()
    return


if __name__ == "__main__":
    if len(sys.argv) > 1:
        vocabulary_dir = sys.argv[1]
    else:
        vocabulary_dir = "vocabulary"
    all_words = load_words(vocabulary_dir)
    qsyllablememory(sys.argv[1:], all_words)

