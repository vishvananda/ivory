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
INTS = range(1, len(PIECES) + 1)
PIECE_TO_INT = dict(zip(PIECES, INTS))
PIECE_TO_INT['-'] = 0
INT_TO_PIECE = dict(zip(INTS, PIECES))
INT_TO_PIECE[0] = '-'
NONE = PIECE_TO_INT['-']
PAWN = PIECE_TO_INT['p']
KNIGHT = PIECE_TO_INT['n']
BISHOP = PIECE_TO_INT['b']
ROOK = PIECE_TO_INT['r']
QUEEN = PIECE_TO_INT['q']
KING = PIECE_TO_INT['k']


def pc(val=0):
    if isinstance(val, basestring):
        val = _parse(val)
    return val


def str(pc):
    return INT_TO_PIECE[pc]


def _parse(val):
    val = val.lower()
    if val not in PIECES:
        raise ValueError("invalid piece value: %s" % val)
    return PIECE_TO_INT[val]


def all():
    for i in INTS:
        yield i
