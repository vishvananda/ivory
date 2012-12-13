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

CHARS = 'KQkq'
CHAR_TO_FLAG = dict(zip(CHARS, [1 << i for i in xrange(4)]))
NONE = 0
BLACK_KING = CHAR_TO_FLAG['k']
BLACK_QUEEN = CHAR_TO_FLAG['q']
WHITE_KING = CHAR_TO_FLAG['K']
WHITE_QUEEN = CHAR_TO_FLAG['Q']
KING = (BLACK_KING, WHITE_KING)
QUEEN = (BLACK_QUEEN, WHITE_QUEEN)


def str(cstl):
    out = ''
    for char in CHARS:
        if cstl & CHAR_TO_FLAG[char]:
            out += char
    return out or '-'


def parse(val):
    if len(val) > 4:
        raise ValueError("invalid castle value: %s" % val)
    out = NONE
    if val != '-':
        for char in val:
            if char not in CHARS:
                raise ValueError("invalid castle value: %s" % val)
            out |= CHAR_TO_FLAG[char]
    return out
