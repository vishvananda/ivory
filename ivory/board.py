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

from ivory import piece

COLUMNS = 'abcdefgh'
ROWS = '12345678'
SQUARES = [[c + r for c in COLUMNS] for r in ROWS]
PIECES = 'pnbrqk'

class BadFen(ValueError):
    pass


class BadSquare(ValueError):
    pass


class Board(object):
    def __init__(self, fen = None):
        if not fen:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.fen = fen

    def __getitem__(self, square):
        p = self.piece_at(*self._square_col_row(square))
        return str(p) if p else None

    def piece_at(self, column, row):
        return self.board[column][row]

    @staticmethod
    def _square_col_row(square):
        try:
            return (COLUMNS.index(square[0]), ROWS.index(square[1]))
        except (IndexError, ValueError):
            raise BadSquare('square does not exist')

    def set_fen(self, value):
        try:
            rows, color, castle, enp, clock, move = value.split()
        except ValueError:
            raise BadFen('wrong number of fields')
        self.board = self._parse_fen_rows(rows)

        color_map = {'b': 0, 'B': 0, 'w': 1, 'W': 1}
        if color not in color_map:
            raise BadFen('bad active color data')
        self.active_color = color_map[color]

        if len(castle) > 4:
            raise BadFen('bad castling data')

        castle_map = dict(zip('KQkq', xrange(4)))
        self.castle = [False] * 4
        for char in castle:
            if char == '-':
                break
            if char not in castle_map:
                raise BadFen('bad char in castling data')

            self.castle[castle_map[char]] = True

        self.en_passant = None
        if enp != '-':
            try:
                self._square_col_row(enp)
            except BadSquare:
                raise BadFen('bad en passant data')
            self.en_passant = enp

        try:
            self.halfmove_clock = int(clock)
        except ValueError:
            raise BadFen('bad halfmove clock')

        try:
            self.move_num = int(move)
        except ValueError:
            raise BadFen('bad move number')

    def _parse_fen_rows(self, row_string):
        try:
            rows = row_string.split('/')
            board = [[None] * 8 for x in range(8)]
            for r, row in enumerate(reversed(rows)):
                c = 0
                for char in row:
                    if char.isdigit():
                        num = int(char)
                        if num < 1 or num > 8:
                            raise BadFen('bad integer in notation')
                        c += num
                    elif char.lower() in PIECES:
                        board[c][r] = piece.Piece(char, SQUARES[c][r], self)
                        c +=1
                    else:
                        raise BadFen('bad piece in notation')
                if c != 8:
                    raise BadFen('bad number of columns')
            if r != 7:
                raise BadFen('wrong number of rows')
            return board
        except BadFen:
            raise
        except Exception:
            raise
            raise BadFen('error parsing fen rows')


    def _write_fen_rows(self, board):
        rows = ['' for x in xrange(8)]
        counts = [0 for x in xrange(8)]
        for c, column in enumerate(board):
            for r, piece in enumerate(reversed(column)):
                if piece is None:
                    counts[r] += 1
                    if c == 7:
                        rows[r] += '%d' % counts[r]
                else:
                    if counts[r]:
                        rows[r] += '%d' % counts[r]
                        counts[r] = 0
                    rows[r] += str(piece)
        return '/'.join(rows)


    def get_fen(self):
        row_string = self._write_fen_rows(self.board)

        color_map = {0: 'b', 1: 'w'}
        color_str = color_map[self.active_color]

        castle_map = dict(zip(xrange(4), 'KQkq'))
        castle_str = ''
        for offset, value in enumerate(self.castle):
            if value:
                castle_str += castle_map[offset]

        return ' '.join([row_string, color_str, castle_str or '-',
                         self.en_passant or '-', str(self.halfmove_clock),
                         str(self.move_num)])


    fen = property(get_fen, set_fen)

