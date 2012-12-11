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

class piece(int):
    PIECES = 'pnbrqk'
    INTS = range(1, len(PIECES) + 1)
    piece_to_int = dict(zip(PIECES, INTS))
    piece_to_int['-'] = 0
    int_to_piece = dict(zip(INTS, PIECES))
    int_to_piece[0] = '-'
    NONE = piece_to_int['-']
    PAWN = piece_to_int['p']
    KNIGHT = piece_to_int['n']
    BISHOP = piece_to_int['b']
    ROOK = piece_to_int['r']
    QUEEN = piece_to_int['q']
    KING = piece_to_int['k']

    def __new__(cls, val=0):
        if isinstance(val, basestring):
            val = cls._parse(val)
        return int.__new__(piece, val)

    def __str__(self):
        return self.int_to_piece[self]

    def __repr__(self):
        return "piece('%s')" % self

    @classmethod
    def _parse(cls, val):
        val = val.lower()
        if val not in cls.PIECES:
            raise ValueError("invalid piece value: %s" % val)
        return cls.piece_to_int[val]

    @classmethod
    def all(cls):
        for i in cls.INTS:
            yield cls(i)
