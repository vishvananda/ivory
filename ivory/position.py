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

from ivory import bitboard
from ivory import move
from ivory import movegen
from ivory import piece
from ivory import square


class Position(object):
    def __init__(self, fen=None):
        if not fen:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.fen = fen

    def __str__(self):
        return self.fen

    def __repr__(self):
        return "(%r)" % self.fen

    def _get_square_color(self, sq):
        if self.color_bbs[0] & sq:
            return 0
        return 1

    def _get_fen_board(self):
        pieces = [None] * 64
        for sq, pc in self.squares.iteritems():
            val = piece.str(pc)
            if self._get_square_color(sq) == 1:
                val = val.upper()
            pieces[square.index(sq)] = val
        ranks = []
        for rank in xrange(8):
            count = 0
            out = ''
            for file in xrange(8):
                pc = pieces[square.index(square.from_a8(rank, file))]
                if pc is None:
                    count += 1
                    if file == 7:
                        out += '%d' % count
                else:
                    if count:
                        out += '%d' % count
                        count = 0
                    out += pc
            ranks.append(out)
        return '/'.join(ranks)

    @property
    def fen(self):
        board_string = self._get_fen_board()

        return ' '.join([board_string, 'bw'[self.color], str(self.castle),
                         self.en_passant or '-', str(self.halfmove_clock),
                         str(self.move_num)])

    @staticmethod
    def _parse_color(val):
        if val not in 'bw':
            raise ValueError("invalid color value: %s" % val)
        return 0 if val == 'b' else 1

    @staticmethod
    def _parse_piece_color(val):
        if val.lower() in piece.PIECES:
            return int(val.isupper())
        else:
            raise ValueError("invalid piece: %s" % val)

    @fen.setter
    def fen(self, value):
        try:
            board, cl, cst, enp, clock, move_num = value.split()
        except ValueError:
            raise ValueError('wrong number of fields')
        self._clear()
        self._parse_fen_board(board)
        self.color = self._parse_color(cl)
        self.castle = movegen.castle(cst)

        if enp != '-':
            try:
                self.en_passant = square.sq(enp)
            except ValueError:
                raise ValueError('bad en passant data')
            self.en_passant = enp

        try:
            self.halfmove_clock = int(clock)
        except ValueError:
            raise ValueError('bad halfmove clock')

        try:
            self.move_num = int(move_num)
        except ValueError:
            raise ValueError('bad move number')

    def _clear(self):
        self.piece_bbs = {}
        for pc in piece.all():
            self.piece_bbs[pc] = bitboard.bb()
        self.color_bbs = {}
        self.squares = {}
        self.color_bbs[0] = bitboard.bb()
        self.color_bbs[1] = bitboard.bb()
        self.castle = movegen.castle('KQkq')
        self.en_passant = square.sq()
        self.halfmove_clock = 0
        self.move_num = 1

    def set_square(self, sq, pc, cl=None):
        if cl is None:
            cl = self.color
        self.piece_bbs[pc] |= sq
        self.color_bbs[cl] |= sq
        self.squares[sq] = pc

    def clear_square(self, sq):
        pc = self.squares.get(sq)
        if pc:
            self.piece_bbs[pc] &= ~sq
            self.color_bbs[0] &= ~sq
            self.color_bbs[1] &= ~sq
            del self.squares[sq]
        return pc

    def _parse_fen_board(self, board_string):
        try:
            ranks = board_string.split('/')
            board = [[None] * 8 for x in range(8)]
            for rank, data in enumerate(ranks):
                file = 0
                for char in data:
                    if char.isdigit():
                        num = int(char)
                        if num < 1 or num > 8:
                            raise ValueError('bad integer in board data')
                        file += num
                    else:
                        try:
                            pc = piece.pc(char)
                            cl = self._parse_piece_color(char)
                            self.set_square(square.from_a8(rank, file), pc, cl)
                            file += 1
                        except ValueError:
                            raise ValueError('bad piece in board data')
                if file != 8:
                    raise ValueError('bad number of files')
            if rank != 7:
                raise ValueError('wrong number of ranks')
            return board
        except ValueError:
            raise
        except Exception:
            raise
            raise ValueError('error parsing fen board data')

    @property
    def occupied(self):
        return self.color_bbs[0] | self.color_bbs[1]

    @property
    def pseudo_moves(self):
        moves = []
        movegen.get_pawn_moves(self, moves)
        movegen.get_knight_moves(self, moves)
        movegen.get_bishop_moves(self, moves)
        movegen.get_rook_moves(self, moves)
        movegen.get_queen_moves(self, moves)
        movegen.get_king_moves(self, moves)
        return moves

    @property
    def moves(self):
        moves = self.pseudo_moves
        self._test_moves(moves)
        self._disambiguate_moves(moves)
        return moves

    def _test_moves(self, moves, check_end=True):
        for mv in moves:
            moving_color = self.color
            pc = self.make_move(mv)
            if movegen.king_attacked(self, moving_color):
                moves.pop(mv)
                continue
            if pc:
                moves[moves.index(mv)] = move.set_capture(mv)

            if check_end and movegen.king_attacked(self, self.color):
                if self._game_over(self):
                    moves[moves.index(mv)] = move.set_mate(mv)
                else:
                    moves[moves.index(mv)] = move.set_check(mv)
            self.unmake_move(mv, pc)

    def _game_over(self):
        moves = self.moves
        self._test_moves(moves, False)
        return not moves

    def _disambiguate_moves(self, moves):
        files = {}
        ranks = {}
        for mv in moves:
            if move.promotion(mv):
                continue
            ps = (move.piece(mv), move.tosq(mv))
            files.setdefault(ps, [])
            ranks.setdefault(ps, [])
            files[ps].append(square.file(move.frsq(mv)))
            ranks[ps].append(square.rank(move.frsq(mv)))

        opp_cl = not self.color
        for i, mv in enumerate(moves):
            ps = (move.piece(mv), move.tosq(mv))
            if files[ps].count(square.file(move.frsq(mv))) > 1:
                moves[i] = moves[i].set_show_rank()
            if ranks[ps].count(square.rank(move.frsq(mv))) > 1:
                moves[i] = moves[i].set_show_file()

    def __getitem__(self, index):
        return self.squares.get(index)

    MOVES = []
    def make_move(self, mv):
        self.MOVES.append(move)
        cl = self.color
        self.color = not self.color
        opp_cl = self.color
        self.halfmove_clock += 1
        if cl == 0:
            self.move_num += 1
        pc = self.clear_square(move.tosq(mv))
        self.set_square(move.tosq(mv), move.piece(mv), cl)
        self.clear_square(move.frsq(mv))

        if move.promotion(mv) == piece.PAWN:
            back = square.n if opp_cl == 1 else square.s
            self.clear_square(back(move.tosq(mv)))
        elif move.promotion(mv) == piece.KING:
            frsq, tosq = self.CASTLE_SQUARE_MAP[move.tosq(mv)]
            rook = self.clear_square(frsq)
            self.set_square(tosq, rook, cl)
        return pc

    def unmake_move(self, mv, pc):
        self.MOVES.pop()
        opp_cl = self.color
        self.color = not self.color
        cl = self.color
        self.halfmove_clock -= 1
        if cl == 0:
            self.move_num -= 1
        self.set_square(move.frsq(mv), move.piece(mv), cl)
        self.clear_square(move.tosq(mv))

        if move.promotion(mv) == piece.PAWN:
            back = square.n if opp_cl == 1 else square.s
            self.set_square(back(move.osq(mv)), piece.PAWN, opp_cl)
        elif move.promotion(mv) == piece.KING:
            frsq, tosq = self.CASTLE_SQUARE_MAP[move.tosq(mv)]
            rook = self.clear_square(frsq)
            self.set_square(move.tosq(mv), rook, cl)
        elif pc:
            self.set_square(move.tosq(mv), pc, opp_cl)

    def perft(self, depth):
        nodes = 0
        if depth == 0:
            return 1
        for move in self.pseudo_moves:
            pc = self.make_move(move)
            nodes += self.perft(depth - 1)
            self.unmake_move(move, pc)
        return nodes

# NOTE(vish): insert constants into locals
for sq in square.all():
    locals()[square.str(sq)] = sq

for pc in piece.all():
    locals()[piece.str(pc)] = pc

p1 = Position()
print p1.fen

import time
a = time.time()
import cProfile
cProfile.run('nodes = p1.perft(3)')
print nodes, time.time() - a
