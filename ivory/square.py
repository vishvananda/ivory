# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Vishvananda Ishaya
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


FILES = 'abcdefgh'
RANKS = '12345678'
SQUARES = [f + r for r in RANKS for f in FILES]
INTS = [1L << i for i in xrange(64)]
BIT_FILES = [sum(INTS[x::8]) for x in xrange(8)]
BIT_RANKS = [sum(INTS[x * 8:(x * 8) + 8]) for x in xrange(8)]
BIT_A1H8 = ([sum(INTS[(7 - x) * 8::9]) for x in xrange(8)] +
            [sum(INTS[x:(8 - x) * 8:9]) for x in xrange(1, 8)])
BIT_A8H1 = ([sum(INTS[x:x * 8 + 1:7]) for x in xrange(8)] +
            [sum(INTS[x * 8 + 7::7]) for x in xrange(1, 8)])
NOT_FIRST_FILE = ~(BIT_FILES[0])
NOT_LAST_FILE = ~(BIT_FILES[-1])
NOT_FIRST_TWO_FILES = ~(BIT_FILES[0] | BIT_FILES[1])
NOT_LAST_TWO_FILES = ~(BIT_FILES[-2] | BIT_FILES[-1])
SQUARE_TO_INT = dict(zip(SQUARES, INTS))
SQUARE_TO_INT['-'] = 0L
INT_TO_SQUARE = dict(zip(INTS, SQUARES))
INT_TO_SQUARE[0L] = '-'


def sq(val=0L):
    if isinstance(val, basestring):
        val = _parse(val)
    return val


def str(sq):
    return INT_TO_SQUARE[sq]


# NOTE(vish): mask is necessary for overflow
def n(sq):
    return (sq << 8) & 0xFFFFFFFFFFFFFFFF


def e(sq):
    return (sq & NOT_LAST_FILE) << 1


def s(sq):
    return sq >> 8


def w(sq):
    return (sq & NOT_FIRST_FILE) >> 1


def nn(sq):
    return (sq << 16) & 0xFFFFFFFFFFFFFFFF


def ss(sq):
    return sq >> 16


def ne(sq):
    return ((sq & NOT_LAST_FILE) << 9) & 0xFFFFFFFFFFFFFFFF


def se(sq):
    return (sq & NOT_LAST_FILE) >> 7


def sw(sq):
    return (sq & NOT_FIRST_FILE) >> 9


def nw(sq):
    return ((sq & NOT_FIRST_FILE) << 7) & 0xFFFFFFFFFFFFFFFF


def nne(sq):
    return ((sq & NOT_LAST_FILE) << 17) & 0xFFFFFFFFFFFFFFFF


def ene(sq):
    return ((sq & NOT_LAST_TWO_FILES) << 10) & 0xFFFFFFFFFFFFFFFF


def ese(sq):
    return (sq & NOT_LAST_TWO_FILES) >> 6


def sse(sq):
    return (sq & NOT_LAST_FILE) >> 15


def ssw(sq):
    return (sq & NOT_FIRST_FILE) >> 17


def wsw(sq):
    return (sq & NOT_FIRST_TWO_FILES) >> 10


def wnw(sq):
    return ((sq & NOT_FIRST_TWO_FILES) << 6) & 0xFFFFFFFFFFFFFFFF


def nnw(sq):
    return ((sq & NOT_FIRST_FILE) << 15) & 0xFFFFFFFFFFFFFFFF


def index(sq):
    return INTS.index(sq)


def file(sq):
    return index(sq) & 0x7


def rank(sq):
    return index(sq) >> 3


def a1h8(sq):
    return 7 - rank(sq) + file(sq)


def a8h1(sq):
    return rank(sq) + file(sq)


def all():
    for i in INTS:
        yield i


def _parse(val):
    if val not in SQUARES:
        raise ValueError("Invalid square value: %s" % val)
    return SQUARE_TO_INT[val]


def from_index(index):
    return INTS[index]


def from_a8(rank, file):
    return INTS[(7 - rank) * 8 + file]


def from_a1(rank, file):
    return INTS[rank * 8 + file]


def walk(sq, dir):
    glob = globals()
    sq = glob.get(dir)(sq)
    while sq:
        yield sq
        sq = glob.get(dir)(sq)
