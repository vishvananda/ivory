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

from ivory.piece import piece
from ivory import square

class move(int):
    NONE = 0
    CAPTURE = 1 << 0
    CHECK = 1 << 1
    MATE = 1 << 2
    SHOW_FILE = 1 << 3
    SHOW_RANK = 1 << 4
    FLAGS = 0xFF << 0
    NOT_FLAGS = ~FLAGS
    FRSQ_OFF = 8
    FRSQ = 0xFF << FRSQ_OFF
    TOSQ_OFF = 8 + FRSQ_OFF
    TOSQ = 0xFF << TOSQ_OFF
    PIECE_OFF = 8 + TOSQ_OFF
    PIECE = 0xF << PIECE_OFF
    PROMOTION_OFF = 4 + PIECE_OFF
    PROMOTION = 0xF << PROMOTION_OFF

    def __new__(self, piece, frsq, tosq, promotion=piece.NONE,
                capture=False, check=False, mate=False,
                show_file=False, show_rank=False):
        val = piece
        val = ((square.index(frsq) << self.FRSQ_OFF) |
               (square.index(tosq) << self.TOSQ_OFF) |
               (piece << self.PIECE_OFF) | (promotion << self.PROMOTION_OFF))
        if capture:
            val |= self.CAPTURE
        if check:
            val |= self.CHECK
        if mate:
            val |= self.MATE
        if show_file:
            val |= self.SHOW_FILE
        if show_rank:
            val |= self.SHOW_RANK
        return int.__new__(move, val)

    @classmethod
    def from_int(self, value):
        return int.__new__(move, value)

    def __eq__(self, other):
        return int(self & self.NOT_FLAGS) == int(other & self.NOT_FLAGS)

    def __hash__(self):
        return hash(self & self.NOT_FLAGS)

    def __not__(self):
        return move.from_int(int.__and__(self))

    def __and__(self, other):
        return move.from_int(int.__and__(self, other))

    def __or__(self, other):
       return move.from_int(int.__or__(self, other))

    def __lshift__(self, other):
       return move.from_int(int.__lshift__(self, other))

    def __rshift__(self, other):
       return move.from_int(int.__rshift__(self, other))

    @property
    def capture(self):
        return bool(self & self.CAPTURE)

    def set_capture(self):
        return self | self.CAPTURE

    def clear_capture(self):
        return self & ~self.CAPTURE

    @property
    def check(self):
        return bool(self & self.CHECK)

    def set_check(self):
        return self | self.CHECK

    def clear_check(self):
        return self & ~self.CHECK

    @property
    def mate(self):
        return bool(self & self.MATE)

    def set_mate(self):
        return self | self.MATE

    def clear_mate(self):
        return self & ~self.MATE

    @property
    def show_file(self):
        return bool(self & self.SHOW_FILE)

    def set_show_file(self):
        return self | self.SHOW_FILE

    def clear_show_file(self):
        return self & ~self.SHOW_FILE

    @property
    def show_rank(self):
        return bool(self & self.SHOW_RANK)

    def set_show_rank(self):
        return self | self.SHOW_RANK

    def clear_show_rank(self):
        return self & ~self.SHOW_RANK

    @property
    def piece(self):
        return piece((self & self.PIECE) >> self.PIECE_OFF)

    def set_piece(self, pc):
        return self & ~self.PIECE | (pc << self.PIECE_OFF)

    @property
    def promotion(self):
        pc = (self & self.PROMOTION) >> self.PROMOTION_OFF
        return piece(pc) if pc != piece.NONE else None

    def set_promotion(self, pc):
        return (self & ~self.PROMOTION) | (pc << self.PROMOTION_OFF)

    @property
    def frsq(self):
        return square.from_index((self & self.FRSQ) >> self.FRSQ_OFF)

    def set_frsq(self, sq):
        return self & ~self.FRSQ | (square.index(sq) << self.FRSQ_OFF)

    @property
    def tosq(self):
        return square.from_index((self & self.TOSQ) >> self.TOSQ_OFF)

    def set_tosq(self, sq):
        return self & ~self.TOSQ | (square.index(sq) << self.TOSQ_OFF)

    def __repr__(self):
        out = "move(%r, %r, %r" % (self.piece, self.frsq, self.tosq)
        for val in ('promotion', 'capture', 'check', 'mate',
                    'show_file', 'show_rank'):
            if getattr(self, val):
                out += ", %s=%r" % (val, getattr(self, val))
        out += ")"
        return out

    def __str__(self):
        if self.promotion == piece.KING:
            return 'O-O-O' if square.file(self.tosq) == 'c' else 'O-O'
        out = []
        if self.piece == piece.PAWN:
            if self.capture:
                out.append(square.file(self.frsq))
                out.append('x')
        else:
            out.append(str(self.piece).upper())
            if self.show_file:
                out.append(square.file(self.frsq))
            if self.show_rank:
                out.append(square.rank(self.frsq))
            if self.capture:
                out.append('x')
        out.append(square.str(self.tosq))
        if self.promotion:
            out.append('=')
            out.append(str(self.promotion).upper())
        if self.check:
            out.append('+')
        if self.mate:
            out.append('#')
        return ''.join(out)
