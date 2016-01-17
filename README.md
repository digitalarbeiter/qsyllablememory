QSyllableMemory
===============

Reading exercise game.

Installation
------------
Clone git repository:

   $ git clone 

Next, get a vocabulary. A vocabulary consists of a directory containing first
and foremost, a file named vocabulary.txt. This file has one word per line,
properly hyphenated. Lines starting with a # are treated as comments.
From each word in the vocabulary.txt, a filename is derived by stripping
all the hyphens and expanding the umlauts. The vocabulary directory is
expected to contain <word>.jpg and <word>.mp3 files for each word in the
vocabulary.txt. The JPEG file contains an image for the word, whereas the
MP3 file contains the spoken word.

Example:

   $ cat vocabulary/vocabulary.txt
   Je-di
   Pro-gram-mer
   $ ls vocabulary/
   jedi.jpg
   jedi.mp3
   programmer.jpg
   programmer.mp3
   vocabulary.txt


Playing the Game
----------------

   $ cd qsyllablememory
   $ python qsyllablememory.py /path/to/vocabulary/

