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

from ivory import bitboard
from ivory import castle
from ivory import move
from ivory import piece
from ivory import square

def _make_promotions(moves, frsq, tosq):
    for pc in (piece.KNIGHT, piece.BISHOP, piece.ROOK, piece.QUEEN):
        moves.append(move.mv(piece.PAWN, frsq, tosq, promotion=pc))

def get_pawn_moves(pos, moves):
    pawns = pos.piece_bbs[piece.PAWN] & pos.color_bbs[pos.color]
    not_occ = ~(pos.occupied)
    enp = pos.en_passant
    opp_occ = pos.color_bbs[not pos.color] | enp
    if pos.color:
        # single pawn moves
        regular = pawns & ~square.BIT_RANKS[6]
        promoting = pawns & square.BIT_RANKS[6]
        single = bitboard.n(pawns) & not_occ
        for sq in bitboard.squares(single):
            moves.append(move.mv(piece.PAWN, square.s(sq), sq))
        for sq in bitboard.squares(bitboard.n(promoting) & not_occ):
            _make_promotions(moves, sq, square.s(sq))

        # east attacks
        for sq in bitboard.squares(bitboard.ne(regular) & opp_occ):
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.sw(sq), sq, prm))
        for sq in bitboard.squares(bitboard.ne(promoting) & opp_occ):
            _make_promotions(moves, sq, square.sw(sq))

        # west attacks
        for sq in bitboard.squares(bitboard.nw(regular) & opp_occ):
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.se(sq), sq, prm))
        for sq in bitboard.squares(bitboard.nw(promoting) & opp_occ):
            _make_promotions(moves, sq, square.se(sq))

        # double pawn moves
        doubles = bitboard.n(single & square.BIT_RANKS[2])
        for sq in bitboard.squares(doubles & not_occ):
            moves.append(move.mv(piece.PAWN, square.ss(sq), sq))


    else:
        # single pawn moves
        regular = pawns & ~square.BIT_RANKS[1]
        promoting = pawns & square.BIT_RANKS[1]
        single = bitboard.s(pawns) & not_occ
        for sq in bitboard.squares(single):
            moves.append(move.mv(piece.PAWN, square.n(sq), sq))
        for sq in bitboard.squares(bitboard.s(promoting) & not_occ):
            _make_promotions(moves, sq, square.n(sq))

        # east attacks
        for sq in bitboard.squares(bitboard.se(regular) & opp_occ):
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.nw(sq), sq, prm))
        for sq in bitboard.squares(bitboard.se(promoting) & opp_occ):
            _make_promotions(moves, sq, square.nw(sq))

        # west attacks
        for sq in bitboard.squares(bitboard.sw(regular) & opp_occ):
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, square.ne(sq), sq, prm))
        for sq in bitboard.squares(bitboard.sw(promoting) & opp_occ):
            _make_promotions(moves, sq, square.ne(sq))

        # double pawn moves
        doubles = bitboard.s(single & square.BIT_RANKS[5])
        for sq in bitboard.squares(doubles & not_occ):
            moves.append(move.mv(piece.PAWN, square.nn(sq), sq))

def get_pawn_moves_2(pos, moves):
    pawns = pos.piece_bbs[piece.PAWN] & pos.color_bbs[pos.color]
    not_occ = ~(pos.occupied)
    enp = pos.en_passant
    opp_occ = pos.color_bbs[not pos.color] | enp
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
        for sq in bitboard.squares(fwd(regular) & occ):
            prm = piece.PAWN if sq == enp else piece.NONE
            moves.append(move.mv(piece.PAWN, back(sq), sq, prm))
        for sq in bitboard.squares(fwd(promoting) & occ):
            _make_promotions(moves, sq, back(sq))

    # double pawn moves
    occ = ~(pos.occupied | push(pos.occupied))
    double = (regular & square.BIT_RANKS[dbl_rank])
    for sq in bitboard.squares(dfwd(double) & occ):
        moves.append(move.mv(piece.PAWN, dback(sq), sq))

def get_knight_moves(pos, moves):
    knights = pos.piece_bbs[piece.KNIGHT] & pos.color_bbs[pos.color]
    not_occ = ~pos.color_bbs[pos.color]
    for frsq in bitboard.squares(knights):
        for tosq in bitboard.squares(ATTACKS[piece.KNIGHT][frsq] & not_occ):
            moves.append(move.mv(piece.KNIGHT, frsq, tosq))

def get_king_moves(pos, moves):
    frsq = pos.piece_bbs[piece.KING] & pos.color_bbs[pos.color]
    not_own_occ = ~pos.color_bbs[pos.color]
    for tosq in bitboard.squares(ATTACKS[piece.KING][frsq] & not_own_occ):
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
    for frsq in bitboard.squares(pieces):
        occ = pos.occupied & MASK[pc][frsq]
        for tosq in bitboard.squares(OCC_ATTACKS[pc][frsq][occ] & not_own_occ):
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
        opp_cl = not pos.color
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
    return attacked(sq, not cl)

def _calc_slide_attacks(sq, occ, pc):
    result = bitboard.bb()
    dirs = ['ne', 'se', 'sw', 'nw'] if pc == piece.BISHOP else 'nesw'
    for dir in dirs:
        for test in square.walk(sq, dir):
            result |= test
            if test & occ:
                break
    return result

def _occ_attack_table(sq, pc):
    mask = MASK[pc][sq]
    bits = bitboard.ones(mask)
    attacks = {}
    for occ_index in xrange(1 << bits):
        occ = bitboard.bb()
        for sq_index, test_sq in enumerate(bitboard.squares(mask)):
            if occ_index & (1L << sq_index):
                occ |= test_sq
        attacks[occ] = _calc_slide_attacks(sq, occ, pc)
    return attacks

def _king_moves(sq):
    return bitboard.bb(square.n(sq) | square.s(sq) |
                       square.e(sq) | square.w(sq) |
                       square.ne(sq) | square.se(sq) |
                       square.sw(sq) | square.nw(sq))

def _knight_moves(sq):
    return bitboard.bb(square.nne(sq) | square.ene(sq) |
                       square.ese(sq) | square.sse(sq) |
                       square.ssw(sq) | square.wsw(sq) |
                       square.wnw(sq) | square.nnw(sq))

CASTLE_FLAG_MAP = (
    (
        (castle.WHITE_QUEEN, square.sq('c1'), square.sq('d1'),
         bitboard.bb(square.sq('b1') | square.sq('c1') | square.sq('d1'))),
        (castle.WHITE_KING, square.sq('g1'), square.sq('f1'),
         bitboard.bb(square.sq('f1') | square.sq('g1'))),
    ),
    (
        (castle.BLACK_QUEEN, square.sq('c8'), square.sq('d8'),
         bitboard.bb(square.sq('b8') | square.sq('c8') | square.sq('d8'))),
        (castle.BLACK_KING, square.sq('g8'), square.sq('f8'),
         bitboard.bb(square.sq('f8') | square.sq('g8'))),
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
        rank = bitboard.bb(square.BIT_RANKS[square.rank(sq)])
        file = bitboard.bb(square.BIT_FILES[square.file(sq)])
        a1h8 = bitboard.bb(square.BIT_A1H8[square.a1h8(sq)])
        a8h1 = bitboard.bb(square.BIT_A8H1[square.a8h1(sq)])

        ATTACKS[piece.BISHOP][sq] = a1h8 | a8h1
        MASK[piece.BISHOP][sq] = (
                (a1h8 & ~bitboard.msb(a1h8) & ~bitboard.lsb(a1h8)) |
                (a8h1 & ~bitboard.msb(a8h1) & ~bitboard.lsb(a8h1))
        )
        ATTACKS[piece.ROOK][sq] = rank | file
        MASK[piece.ROOK][sq] = (
            (rank & ~bitboard.msb(rank) & ~bitboard.lsb(rank)) |
            (file & ~bitboard.msb(file) & ~bitboard.lsb(file))
        )
        OCC_ATTACKS[piece.BISHOP][sq] = _occ_attack_table(sq, piece.BISHOP)
        OCC_ATTACKS[piece.ROOK][sq] = _occ_attack_table(sq, piece.ROOK)
        ATTACKS[piece.KING][sq] = _king_moves(sq)
        ATTACKS[piece.KNIGHT][sq] = _knight_moves(sq)
    with open('attacks.pickle', 'w') as f:
        pickle.dump((ATTACKS, MASK, OCC_ATTACKS), f, -1)
