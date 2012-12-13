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

from ivory.piece import piece as ivory_piece
from ivory import square

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

def mv(piece, frsq, tosq, promotion=ivory_piece.NONE):
    val = piece
    val = ((square.index(frsq) << FRSQ_OFF) |
           (square.index(tosq) << TOSQ_OFF) |
           (piece << PIECE_OFF) | (promotion << PROMOTION_OFF))
    return val

def is_capture(mv):
    return bool(mv & CAPTURE)

def set_capture(mv):
    return mv | CAPTURE

def clear_capture(mv):
    return mv & ~CAPTURE

def is_check(mv):
    return bool(mv & CHECK)

def set_check(mv):
    return mv | CHECK

def clear_check(mv):
    return mv & ~CHECK

def is_mate(mv):
    return bool(mv & MATE)

def set_mate(mv):
    return mv | MATE

def clear_mate(mv):
    return mv & ~MATE

def is_show_file(mv):
    return bool(mv & SHOW_FILE)

def set_show_file(mv):
    return mv | SHOW_FILE

def clear_show_file(mv):
    return mv & ~SHOW_FILE

def is_show_rank(mv):
    return bool(mv & SHOW_RANK)

def set_show_rank(mv):
    return mv | SHOW_RANK

def clear_show_rank(mv):
    return mv & ~SHOW_RANK

def piece(mv):
    return (mv & PIECE) >> PIECE_OFF

def set_piece(mv, pc):
    return mv & ~PIECE | (pc << PIECE_OFF)

def promotion(mv):
    return (mv & PROMOTION) >> PROMOTION_OFF

def set_promotion(mv, pc):
    return (mv & ~PROMOTION) | (pc << PROMOTION_OFF)

def frsq(mv):
    return square.from_index((mv & FRSQ) >> FRSQ_OFF)

def set_frsq(mv, sq):
    return mv & ~FRSQ | (square.index(sq) << FRSQ_OFF)

def tosq(mv):
    return square.from_index((mv & TOSQ) >> TOSQ_OFF)

def set_tosq(mv, sq):
    return mv & ~TOSQ | (square.index(sq) << TOSQ_OFF)

def str(mv):
    if promotion(mv) == ivory_piece.KING:
        return 'O-O-O' if square.file(tosq(mv)) == 'c' else 'O-O'
    out = []
    if piece(mv) == ivory_piece.PAWN:
        if is_capture(mv):
            out.append(square.file(frsq(mv)))
            out.append('x')
    else:
        out.append(ivory_piece.str(piece(mv)).upper())
        if is_show_file(mv):
            out.append(square.file(frsq(mv)))
        if is_show_rank(mv):
            out.append(square.rank(frsq(mv)))
        if is_capture(mv):
            out.append('x')
    out.append(square.str(tosq(mv)))
    if promotion(mv):
        out.append('=')
        out.append(ivory_piece.str(promotion).upper())
    if is_check(mv):
        out.append('+')
    if is_mate(mv):
        out.append('#')
    return ''.join(out)
