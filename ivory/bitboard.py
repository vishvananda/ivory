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

from ivory import square


BITS = '01'
bits_to_int = dict(zip(BITS, xrange(len(BITS))))
BS_INDEX = [
        0, 47,  1, 56, 48, 27,  2, 60,
       57, 49, 41, 37, 28, 16,  3, 61,
       54, 58, 35, 52, 50, 42, 21, 44,
       38, 32, 29, 23, 17, 11,  4, 62,
       46, 55, 26, 59, 40, 36, 15, 53,
       34, 51, 20, 43, 31, 22, 10, 45,
       25, 39, 14, 33, 19, 30,  9, 24,
       13, 18,  8, 12,  7,  6,  5, 63
]
BS_SQUARES = [square.INTS[i] for i in BS_INDEX]
DEBRUIJIN = 0x03f79d71b4cb0a89L

def lsb(bb):
    # NOTE(vish): This is inneficient with python longs. Switching
    #             to numpy.long should speed it up and enable the
    #             removal of the & 0x3F.
    xored = bb ^ (bb - 1)
    return BS_SQUARES[((xored * DEBRUIJIN) >> 58) & 0x3F]

def msb(bb):
    bb = bb
    bb |= bb >> 1
    bb |= bb >> 2
    bb |= bb >> 4
    bb |= bb >> 8
    bb |= bb >> 16
    bb |= bb >> 32
    # NOTE(vish): This is inneficient with python longs. Switching
    #             to numpy.long should speed it up and enable the
    #             removal of the & 0x3F.
    return BS_SQUARES[((bb * DEBRUIJIN) >> 58) & 0x3F]

def squares(bb):
    while bb:
        sq = lsb(bb)
        yield sq
        bb = bb & ~sq

def ones(bb):
    return sum(1 for sq in squares(bb))

def bb(val=0):
    if isinstance(val, basestring):
        val = _parse(val)
    return val

def str(bb):
    out = []
    for rank in xrange(8):
        for file in xrange(8):
            sq = square.from_a8(rank, file)
            out.append(BITS[int(sq & bb != 0)])
        out.append("\n")
    return ''.join(out)

def n(bb):
     return (bb << 8) & 0xFFFFFFFFFFFFFFFF

def nn(bb):
     return (bb << 16) & 0xFFFFFFFFFFFFFFFF

def e(bb):
    return (bb & square.NOT_LAST_FILE) << 1

def s(bb):
    return bb >> 8

def ss(bb):
    return bb >> 16

def w(bb):
    return (bb & square.NOT_FIRST_FILE) >> 1

def ne(bb):
    return ((bb & square.NOT_LAST_FILE) << 9) & 0xFFFFFFFFFFFFFFFF

def se(bb):
    return (bb & square.NOT_LAST_FILE) >> 7

def sw(bb):
    return (bb & square.NOT_FIRST_FILE) >> 9

def nw(bb):
    return ((bb & square.NOT_FIRST_FILE) << 7) & 0xFFFFFFFFFFFFFFFF

@classmethod
def _parse(val):
    out = 0
    val = val.replace('\n', '')
    if len(val) != 64:
        raise ValueError("invalid size for bitboard: %s" % len(val))
    for rank in xrange(8):
        for file in xrange(8):
            ch = val[(7 - rank) * 8 + file]
            if ch not in BITS:
                raise ValueError("invalid char in bitboard: %s" % sq)
            out += bits_to_int[ch] * square.from_a8(rank, file)
    return out
