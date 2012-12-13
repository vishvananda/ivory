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

from ivory import castle
from ivory import move
from ivory import movegen
from ivory import piece
from ivory import square


class Position(object):
    ROOK_SQUARES = (
        (square.sq('a8'), square.sq('h8')),
        (square.sq('a1'), square.sq('h1')),
    )
    CASTLE_SQUARE_MAP = {
        square.sq('c8'): (ROOK_SQUARES[0][0], square.sq('d8')),
        square.sq('g8'): (ROOK_SQUARES[0][1], square.sq('f8')),
        square.sq('c1'): (ROOK_SQUARES[1][0], square.sq('d1')),
        square.sq('g1'): (ROOK_SQUARES[1][1], square.sq('f1')),
    }

    def __init__(self, fen=None):
        if not fen:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.fen = fen

    def __repr__(self):
        return "(%r)" % self.fen

    def _get_square_color(self, sq):
        if self.color_bbs[0] & sq:
            return 0
        return 1

    def __str__(self):
        out = []
        for rank in xrange(8):
            for file in xrange(8):
                sq = square.from_a8(rank, file)
                piece_str = piece.str(self.squares[sq])
                if self.color_bbs[1] & sq:
                    piece_str = piece_str.upper()
                out.append(piece_str)
            out.append('\n')
        return ''.join(out)

    def _get_fen_board(self):
        pieces = [None] * 64
        for sq, pc in self.squares.iteritems():
            if pc:
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

        return ' '.join([board_string, 'bw'[self.color],
                         castle.str(self.castle), self.enp or '-',
                         str(self.halfmove_clock), str(self.move_num)])

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
        self.castle = castle.parse(cst)

        if enp != '-':
            try:
                self.enp = square.sq(enp)
            except ValueError:
                raise ValueError('bad en passant data')
            self.enp = enp

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
            self.piece_bbs[pc] = 0L
        self.color_bbs = {}
        self.color_bbs[0] = 0L
        self.color_bbs[1] = 0L
        self.squares = {}
        for sq in square.all():
            self.squares[sq] = 0L
        self.castle = castle.parse('KQkq')
        self.enp = square.sq()
        self.halfmove_clock = 0
        self.move_num = 1

    def set_square(self, sq, pc, cl=None):
        if cl is None:
            cl = self.color
        self.piece_bbs[pc] |= sq
        self.color_bbs[cl] |= sq
        self.squares[sq] = pc

    def clear_square(self, sq):
        pc = self.squares[sq]
        if pc:
            self.piece_bbs[pc] &= ~sq
            self.color_bbs[0] &= ~sq
            self.color_bbs[1] &= ~sq
            self.squares[sq] = 0L
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
    def legal_moves(self):
        moves = self.pseudo_moves
        legal = self._validate_moves(moves)
        return self._disambiguate_moves(legal)

    def _validate_moves(self, moves, check_end=True):
        legal = []
        for i, mv in enumerate(moves):
            moving_color = self.color
            pc = self.make_move(mv)
            if not movegen.king_attacked(self, moving_color):
                if pc:
                    mv = move.set_capture(mv)

                if check_end and movegen.king_attacked(self, self.color):
                    if self._game_over():
                        mv = move.set_mate(mv)
                    else:
                        mv = move.set_check(mv)
                legal.append(mv)
            self.unmake_move()
        return legal

    def _game_over(self):
        moves = self.pseudo_moves
        return not self._validate_moves(moves, False)

    def _disambiguate_moves(self, moves):
        files = {}
        ranks = {}
        unamb = list(moves)
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
                unamb[i] = moves[i].set_show_rank()
            if ranks[ps].count(square.rank(move.frsq(mv))) > 1:
                unamb[i] = moves[i].set_show_file()
        return unamb

    def __getitem__(self, index):
        return self.squares.get(index)

    moves = []
    def make_move(self, mv):
        cl = self.color
        half, cast, enp = self.halfmove_clock, self.castle, self.enp
        self.color = not self.color
        opp_cl = self.color
        if cl == 0:
            self.move_num += 1
        self.enp = 0L
        frsq = move.frsq(mv)
        tosq = move.tosq(mv)
        prom = move.promotion(mv)
        pc = self.clear_square(tosq)
        mvpc = move.piece(mv)
        if pc or mvpc == piece.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        if prom and prom != piece.PAWN and prom != piece.KING:
            mvpc = prom
        self.set_square(tosq, mvpc, cl)
        self.clear_square(frsq)
        if tosq == self.ROOK_SQUARES[opp_cl][0]:
            self.castle &= ~castle.QUEEN[opp_cl]
        elif tosq == self.ROOK_SQUARES[opp_cl][1]:
            self.castle &= ~castle.KING[opp_cl]
        if mvpc == piece.KING:
            self.castle &= ~castle.QUEEN[cl]
            self.castle &= ~castle.KING[cl]
            if prom == piece.KING:
                rfrsq, rtosq = self.CASTLE_SQUARE_MAP[tosq]
                rook = self.clear_square(rfrsq)
                self.set_square(rtosq, rook, cl)
        elif mvpc == piece.ROOK:
            if frsq == self.ROOK_SQUARES[cl][0]:
                self.castle &= ~castle.QUEEN[cl]
            elif frsq == self.ROOK_SQUARES[cl][1]:
                self.castle &= ~castle.KING[cl]
        elif mvpc == piece.PAWN:
            back = square.n(tosq) if opp_cl == 1 else square.s(tosq)
            if prom == piece.PAWN:
                self.clear_square(back)
            else:
                diff = square.rank(frsq) - square.rank(tosq)
                if diff == 2 or diff == -2:
                    self.enp = back
        self.moves.append((mv, pc, half, cast, enp))
        return pc

    def unmake_move(self):
        mv, pc, self.halfmove_clock, self.castle, self.enp = self.moves.pop()
        opp_cl = self.color
        self.color = not self.color
        cl = self.color
        if cl == 0:
            self.move_num -= 1
        tosq = move.tosq(mv)
        mvpc = move.piece(mv)
        prom = move.promotion(mv)
        self.set_square(move.frsq(mv), mvpc, cl)
        self.clear_square(tosq)

        if prom == piece.PAWN:
            back = square.n if opp_cl == 1 else square.s
            self.set_square(back(tosq), piece.PAWN, opp_cl)
        elif prom == piece.KING:
            rfrsq, rtosq = self.CASTLE_SQUARE_MAP[tosq]
            rook = self.clear_square(rtosq)
            self.set_square(rfrsq, rook, cl)
        if pc:
            self.set_square(tosq, pc, opp_cl)
        if self.squares[square.sq('h1')] == piece.PAWN:
            print move.str(mv), piece.str(pc)
            raise Exception()

    def zero_stats(self):
        self.num_captures = 0
        self.num_en_passant = 0
        self.num_checks = 0
        self.num_mates = 0
        self.num_promotions = 0
        self.num_castles = 0

    def perft(self, depth):
        nodes = 0
        if depth == 0:
            return 1
        for mv in self.pseudo_moves:
            pc = self.make_move(mv)
            if not movegen.king_attacked(self, not self.color):
                nodes += self.perft(depth - 1)
                if depth == 1:
                    if pc:
                        self.num_captures += 1
                    prm = move.promotion(mv)
                    if prm:
                        if prm == piece.PAWN:
                            self.num_captures += 1
                            self.num_en_passant += 1
                        elif prm == piece.KING:
                            self.num_castles += 1
                        else:
                            self.num_promotions += 1

                    if movegen.king_attacked(self, self.color):
                        self.num_checks += 1
                        if self._game_over():
                            self.num_mates += 1
            self.unmake_move()
        return nodes

# NOTE(vish): insert constants into locals
for sq in square.all():
    locals()[square.str(sq)] = sq

for pc in piece.all():
    locals()[piece.str(pc)] = pc

#fen = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
fen = '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1'
p1 = Position(fen)
print piece.str(p1.squares[square.sq('a8')])
import time
import prettytable
pt = prettytable.PrettyTable()
pt.field_names = ['Depth', 'Nodes', 'Captures', 'E.p.', 'Castles',
                  'Promotions', 'Checks', 'Mates', 'Time']
pt.align = 'l'
#import cProfile
#cProfile.run('nodes = p1.perft(4)')
for i in xrange(1, 6):
    p1.zero_stats()
    a = time.time()
    nodes = p1.perft(i)
    b = time.time()
    pt.add_row([i, nodes, p1.num_captures, p1.num_en_passant, p1.num_castles,
                p1.num_promotions, p1.num_checks, p1.num_mates, b - a])
print pt
