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

import unittest
from ivory import board

class BoardTestCase(unittest.TestCase):

    def test_create_fen(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        b = board.Board(fen)
        self.assertEqual(b.fen, fen)

    def test_create_no_fen(self):
        expected = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        b = board.Board()
        self.assertEqual(b.fen, expected)

    def test_index(self):
        b = board.Board()
        self.assertEqual(b['a1'], 'R')
        self.assertEqual(b['a8'], 'r')
        self.assertEqual(b['e1'], 'K')
        self.assertEqual(b['e8'], 'k')
        self.assertEqual(b['e5'], None)

    def test_start_position(self):
        b = board.Board()
        expected = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.assertEqual(b.fen, expected)
        self.assertEqual(b.moves,
                set(['a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
                     'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
                     'Na3', 'Nc3', 'Nf3', 'Nh3']))
