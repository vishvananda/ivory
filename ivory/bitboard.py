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


class bitboard(long):
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

    def lsb(self):
        # NOTE(vish): This is inneficient with python longs. Switching
        #             to numpy.long should speed it up and enable the
        #             removal of the & 0x3F.
        xored = self ^ (self - 1)
        return self.BS_SQUARES[((xored * self.DEBRUIJIN) >> 58) & 0x3F]

    def msb(self):
        bb = self
        bb |= bb >> 1
        bb |= bb >> 2
        bb |= bb >> 4
        bb |= bb >> 8
        bb |= bb >> 16
        bb |= bb >> 32
        # NOTE(vish): This is inneficient with python longs. Switching
        #             to numpy.long should speed it up and enable the
        #             removal of the & 0x3F.
        return self.BS_SQUARES[((bb * self.DEBRUIJIN) >> 58) & 0x3F]

    def squares(self):
        bb = self
        while bb:
            sq = bb.lsb()
            yield sq
            bb = bb & ~sq

    @property
    def ones(self):
        return sum(1 for sq in self.squares())

    def __new__(cls, val=0):
        if isinstance(val, basestring):
            val = cls._parse(val)
        return long.__new__(bitboard, val)

    def __str__(self):
        out = []
        for rank in xrange(8):
            for file in xrange(8):
                sq = square.from_a8(rank, file)
                out.append(self.BITS[int(sq & self != 0)])
            out.append("\n")
        return ''.join(out)

    def __not__(self):
        return bitboard(long.__and__(self))

    def __and__(self, other):
        return bitboard(long.__and__(self, other))

    def __or__(self, other):
        return bitboard(long.__or__(self, other))

    def __xor__(self, other):
        return bitboard(long.__xor__(self, other))

    def __lshift__(self, other):
        return bitboard(long.__lshift__(self, other))

    def __rshift__(self, other):
        return bitboard(long.__rshift__(self, other))

    def n(self):
         return (self << 8) & 0xFFFFFFFFFFFFFFFF

    def nn(self):
         return (self << 16) & 0xFFFFFFFFFFFFFFFF

    def e(self):
        return (self & square.NOT_LAST_FILE) << 1

    def s(self):
        return self >> 8

    def ss(self):
        return self >> 16

    def w(self):
        return (self & square.NOT_FIRST_FILE) >> 1

    def ne(self):
        return ((self & square.NOT_LAST_FILE) << 9) & 0xFFFFFFFFFFFFFFFF

    def se(self):
        return (self & square.NOT_LAST_FILE) >> 7

    def sw(self):
        return (self & square.NOT_FIRST_FILE) >> 9

    def nw(self):
        return ((self & square.NOT_FIRST_FILE) << 7) & 0xFFFFFFFFFFFFFFFF

    @classmethod
    def _parse(cls, val):
        out = 0
        val = val.replace('\n', '')
        if len(val) != 64:
            raise ValueError("invalid size for bitboard: %s" % len(val))
        for rank in xrange(8):
            for file in xrange(8):
                ch = val[(7 - rank) * 8 + file]
                if ch not in cls.BITS:
                    raise ValueError("invalid char in bitboard: %s" % sq)
                out += cls.bits_to_int[ch] * square.from_a8(rank, file)
        return out
