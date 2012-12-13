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
char_to_flag = dict(zip(CHARS, [1 << i for i in xrange(4)]))
NONE = 0
WHITE_KING = char_to_flag['K']
WHITE_QUEEN = char_to_flag['Q']
BLACK_KING = char_to_flag['k']
BLACK_QUEEN = char_to_flag['q']


def str(cstl):
    out = ''
    for char in CHARS:
        if cstl & char_to_flag[char]:
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
            out |= char_to_flag[char]
    return out

