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

def pc(val=0):
    if isinstance(val, basestring):
        val = _parse(val)
    return val

def str(pc):
    return int_to_piece[pc]

def _parse(val):
    val = val.lower()
    if val not in PIECES:
        raise ValueError("invalid piece value: %s" % val)
    return piece_to_int[val]

def all():
    for i in INTS:
        yield i
