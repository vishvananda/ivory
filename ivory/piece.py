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

PIECES = 'pnbrqk'
COLORS = 'wb'

class BadPiece(ValueError):
    pass


class BadColor(ValueError):
    pass


class Piece(object):
    class_map = None

    def __new__(cls, value, square=None, board=None):
        if value.lower() not in PIECES:
            raise BadPiece('bad piece type specified')
        if not Piece.class_map:
            Piece.class_map = {
                'p': Pawn,
                'n': Knight,
                'b': Bishop,
                'r': Rook,
                'q': Queen,
                'k': King
            }
        piece = cls.class_map[value.lower()]
        return object.__new__(piece, value, square, board)

    def __init__(self, value, square=None, board=None):
        self.color = 1 if value < 'a' else 0
        self.value = value.lower()
        self.square = square
        self.board = board

    def __str__(self):
        return self.value.upper() if self.color else self.value

class Pawn(Piece):
    pass

class Knight(Piece):
    pass

class Rook(Piece):
    pass

class Bishop(Piece):
    pass

class Queen(Piece):
    pass

class King(Piece):
    pass
