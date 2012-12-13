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
import os
import cPickle as pickle

from ivory.bitboard import bitboard
from ivory import move
from ivory.piece import piece
from ivory import square

class castle(int):
    CHARS = 'KQkq'
    char_to_flag = dict(zip(CHARS, [1 << i for i in xrange(4)]))
    NONE = 0
    WHITE_KING = char_to_flag['K']
    WHITE_QUEEN = char_to_flag['Q']
    BLACK_KING = char_to_flag['k']
    BLACK_QUEEN = char_to_flag['q']

    def __new__(cls, val):
        if isinstance(val, basestring):
            val = cls._parse(val)
        return int.__new__(castle, val)

    def __str__(self):
        out = ''
        for char in self.CHARS:
            if self & self.char_to_flag[char]:
                out += char
        return out or '-'

    def __repr__(self):
        return "castle('%s')" % self


    @classmethod
    def _parse(cls, val):
        if len(val) > 4:
            raise ValueError("invalid castle value: %s" % val)
        out = cls.NONE
        if val != '-':
            for char in val:
                if char not in cls.CHARS:
                    raise ValueError("invalid castle value: %s" % val)
                out |= cls.char_to_flag[char]
        return out

def _make_promotions(moves, frsq, tosq):
    for pc in (piece.KNIGHT, piece.BISHOP, piece.ROOK, piece.QUEEN):
        moves.append(move.mv(piece.PAWN, frsq, tosq, promotion=pc))

def get_pawn_moves(pos, moves):
    pawns = pos.piece_bbs[piece.PAWN] & pos.color_bbs[pos.color]
    not_occ = ~(pos.occupied)
    enp = pos.en_passant
    opp_occ = pos.color_bbs[pos.color.flip()] | enp
    if pos.color:
        # single pawn moves
        regular = pawns & ~square.BIT_RANKS[6]
        promoting = pawns & square.BIT_RANKS[6]
        single = pawns.n() & not_occ
        for sq in single.squares():
            moves.append(move.mv(piece.PAWN, square.s(sq), sq))
        for sq in (promoting.n() & not_occ).squares():
            _make_promotions(moves, sq, square.s(sq))

        # east attacks
        for sq in (regular.ne() & opp_occ).squares():
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.sw(sq), sq, prm))
        for sq in (promoting.ne() & opp_occ).squares():
            _make_promotions(moves, sq, square.sw(sq))

        # west attacks
        for sq in (regular.nw() & opp_occ).squares():
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.se(sq), sq, prm))
        for sq in (promoting.nw() & opp_occ).squares():
            _make_promotions(moves, sq, square.se(sq))

        # double pawn moves
        for sq in ((single & square.BIT_RANKS[2]).n() & not_occ).squares():
            moves.append(move.mv(piece.PAWN, square.ss(sq), sq))


    else:
        # single pawn moves
        regular = pawns & ~square.BIT_RANKS[1]
        promoting = pawns & square.BIT_RANKS[1]
        single = pawns.s() & not_occ
        for sq in single.squares():
            moves.append(move.mv(piece.PAWN, square.n(sq), sq))
        for sq in (promoting.s() & not_occ).squares():
            _make_promotions(moves, sq, square.n(sq))

        # east attacks
        for sq in (regular.se() & opp_occ).squares():
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.nw(sq), sq, prm))
        for sq in (promoting.se() & opp_occ).squares():
            _make_promotions(moves, sq, square.nw(sq))

        # west attacks
        for sq in (regular.sw() & opp_occ).squares():
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.ne(sq), sq, prm))
        for sq in (promoting.sw() & opp_occ).squares():
            _make_promotions(moves, sq, square.ne(sq))

        # double pawn moves
        for sq in ((single & square.BIT_RANKS[5]).s() & not_occ).squares():
            moves.append(move.mv(piece.PAWN, square.nn(sq), sq))

def get_pawn_moves_2(pos, moves):
    pawns = pos.piece_bbs[piece.PAWN] & pos.color_bbs[pos.color]
    not_occ = ~(pos.occupied)
    enp = pos.en_passant
    opp_occ = pos.color_bbs[pos.color.flip()] | enp
    if pos.color:
        sets = ((bitboard.n, square.s, not_occ),
                 (bitboard.nw, square.se, opp_occ),
                 (bitboard.ne, square.sw, opp_occ))
        pro_rank, dbl_rank, push, = 6, 1, bitboard.n
        dfwd, dback = bitboard.nn, square.ss
    else:
        sets = ((bitboard.s, square.n, not_occ),
                 (bitboard.se, square.nw, opp_occ),
                 (bitboard.sw, square.ne, opp_occ))
        pro_rank, dbl_rank, push, = 1, 6, bitboard.s
        dfwd, dback = bitboard.ss, square.nn

    regular = pawns & ~square.BIT_RANKS[pro_rank]
    promoting = pawns & square.BIT_RANKS[pro_rank]
    for fwd, back, occ in sets:
        for sq in (fwd(regular) & occ).squares():
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, back(sq), sq, prm))
        for sq in (fwd(promoting) & occ).squares():
            _make_promotions(moves, sq, back(sq))

    # double pawn moves
    occ = ~(pos.occupied | push(pos.occupied))
    double = (regular & square.BIT_RANKS[dbl_rank])
    for sq in (dfwd(double) & occ).squares():
        moves.append(move.mv(piece.PAWN, dback(sq), sq))

def get_knight_moves(pos, moves):
    knights = pos.piece_bbs[piece.KNIGHT] & pos.color_bbs[pos.color]
    not_occ = ~pos.color_bbs[pos.color]
    for frsq in knights.squares():
        for tosq in (ATTACKS[piece.KNIGHT][frsq] & not_occ).squares():
            moves.append(move.mv(piece.KNIGHT, frsq, tosq))

def get_king_moves(pos, moves):
    frsq = pos.piece_bbs[piece.KING] & pos.color_bbs[pos.color]
    not_own_occ = ~pos.color_bbs[pos.color]
    for tosq in (ATTACKS[piece.KING][frsq] & not_own_occ).squares():
        if not attacked(pos, tosq):
            moves.append(move.mv(piece.KING, frsq, tosq))
    for flag, tosq, step, inter in CASTLE_FLAG_MAP[pos.color]:
        if (pos.castle & flag or inter & pos.occupied
            or attacked(pos, step) or attacked(pos, tosq)):
            continue
        moves.append(move.mv(piece.KING, frsq, tosq, piece.KING))

def _get_sliding_moves(pos, moves, pc, source=None):
    if not source:
        source = pc
    pieces = pos.piece_bbs[source] & pos.color_bbs[pos.color]
    not_own_occ = ~pos.color_bbs[pos.color]
    for frsq in pieces.squares():
        occ = pos.occupied & MASK[pc][frsq]
        for tosq in (OCC_ATTACKS[pc][frsq][occ] & not_own_occ).squares():
            moves.append(move.mv(source, frsq, tosq))

def get_bishop_moves(pos, moves):
    _get_sliding_moves(pos, moves, piece.BISHOP)

def get_rook_moves(pos, moves):
    _get_sliding_moves(pos, moves, piece.ROOK)

def get_queen_moves(pos, moves):
    _get_sliding_moves(pos, moves, piece.BISHOP, piece.QUEEN)
    _get_sliding_moves(pos, moves, piece.ROOK, piece.QUEEN)

def attacked(pos, sq, opp_cl=None):
    if not opp_cl:
        opp_cl = pos.color.flip()
    opp_occ = pos.color_bbs[opp_cl]
    if ATTACKS[piece.KING][sq] & opp_occ & pos.piece_bbs[piece.KING]:
        return True
    if ATTACKS[piece.KNIGHT][sq] & opp_occ & pos.piece_bbs[piece.KNIGHT]:
        return True
    for pc in (piece.ROOK, piece.BISHOP):
        occ = pos.occupied & MASK[pc][sq]
        pcs_or_qs = pos.piece_bbs[piece.QUEEN] | pos.piece_bbs[pc]
        if OCC_ATTACKS[pc][sq][occ] & opp_occ & pcs_or_qs:
            return True
    if opp_cl:
        pawn_attacks = square.sw(sq) | square.se(sq)
    else:
        pawn_attacks = square.nw(sq) | square.ne(sq)
    if pawn_attacks & opp_occ & pos.piece_bbs[piece.PAWN]:
        return True
    return False

def king_attacked(pos, cl):
    sq = pos.piece_bbs[piece.KING] & pos.color_bbs[cl]
    return attacked(sq, cl.flip())

def _calc_slide_attacks(sq, occ, pc):
    result = bitboard()
    dirs = ['ne', 'se', 'sw', 'nw'] if pc == piece.BISHOP else 'nesw'
    for dir in dirs:
        for test in square.walk(sq, dir):
            result |= test
            if test & occ:
                break
    return result

def _occ_attack_table(sq, pc):
    mask = MASK[pc][sq]
    bits = mask.ones
    attacks = {}
    for occ_index in xrange(1 << mask.ones):
        occ = bitboard()
        for sq_index, test_sq in enumerate(mask.squares()):
            if occ_index & (1L << sq_index):
                occ |= test_sq
        attacks[occ] = _calc_slide_attacks(sq, occ, pc)
    return attacks

def _king_moves(sq):
    return bitboard(square.n(sq) | square.s(sq) |
                    square.e(sq) | square.w(sq) |
                    square.ne(sq) | square.se(sq) |
                    square.sw(sq) | square.nw(sq))

def _knight_moves(sq):
    return bitboard(square.nne(sq) | square.ene(sq) |
                    square.ese(sq) | square.sse(sq) |
                    square.ssw(sq) | square.wsw(sq) |
                    square.wnw(sq) | square.nnw(sq))

CASTLE_FLAG_MAP = (
    (
        (castle.WHITE_QUEEN, square.sq('c1'), square.sq('d1'),
         bitboard(square.sq('b1') | square.sq('c1') | square.sq('d1'))),
        (castle.WHITE_KING, square.sq('g1'), square.sq('f1'),
         bitboard(square.sq('f1') | square.sq('g1'))),
    ),
    (
        (castle.BLACK_QUEEN, square.sq('c8'), square.sq('d8'),
         bitboard(square.sq('b8') | square.sq('c8') | square.sq('d8'))),
        (castle.BLACK_KING, square.sq('g8'), square.sq('f8'),
         bitboard(square.sq('f8') | square.sq('g8'))),
    ),
    )
CASTLE_SQUARE_MAP = {
    square.sq('c1'): (square.sq('a1'), square.sq('d1')),
    square.sq('g1'): (square.sq('h1'), square.sq('f1')),
    square.sq('c8'): (square.sq('a8'), square.sq('d8')),
    square.sq('g8'): (square.sq('h8'), square.sq('f8')),
}

if os.path.exists('attacks.pickle'):
    with open('attacks.pickle') as f:
        ATTACKS, MASK, OCC_ATTACKS = pickle.load(f)
else:
    ATTACKS = {}
    ATTACKS[piece.BISHOP] = {}
    ATTACKS[piece.ROOK] = {}
    ATTACKS[piece.KING] = {}
    ATTACKS[piece.KNIGHT] = {}
    MASK = {}
    MASK[piece.BISHOP] = {}
    MASK[piece.ROOK] = {}
    OCC_ATTACKS = {}
    OCC_ATTACKS[piece.BISHOP] = {}
    OCC_ATTACKS[piece.ROOK] = {}

    for sq in square.all():
        rank = bitboard(square.BIT_RANKS[square.rank(sq)])
        file = bitboard(square.BIT_FILES[square.file(sq)])
        a1h8 = bitboard(square.BIT_A1H8[square.a1h8(sq)])
        a8h1 = bitboard(square.BIT_A8H1[square.a8h1(sq)])

        ATTACKS[piece.BISHOP][sq] = a1h8 | a8h1
        MASK[piece.BISHOP][sq] = ((a1h8 & ~a1h8.msb() & ~a1h8.lsb()) |
                                  (a8h1 & ~a8h1.msb() & ~a8h1.lsb()))
        ATTACKS[piece.ROOK][sq] = rank | file
        MASK[piece.ROOK][sq] = ((rank & ~rank.msb() & ~rank.lsb()) |
                                (file & ~file.msb() & ~file.lsb()))
        OCC_ATTACKS[piece.BISHOP][sq] = _occ_attack_table(sq, piece.BISHOP)
        OCC_ATTACKS[piece.ROOK][sq] = _occ_attack_table(sq, piece.ROOK)
        ATTACKS[piece.KING][sq] = _king_moves(sq)
        ATTACKS[piece.KNIGHT][sq] = _knight_moves(sq)
    with open('attacks.pickle', 'w') as f:
        pickle.dump((ATTACKS, MASK, OCC_ATTACKS), f, -1)
