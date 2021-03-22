#!/usr/bin/python

import os
import sys
import time
import signal
import argparse
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from common import board


class Server(object):
    """
    Othello server, implements a simple file-based playing protocol

    """

    # server file names
    START_SCRIPT = 'launch.sh'
    STATE_FILE = 'state.txt'
    MOVE_FILE = 'move.txt'

    # HISTORY_FILE = 'history.txt'
    # STDOUT_FILE = 'yourlog.txt'

    def __init__(self, p1_dir, p2_dir, delay, stdout, history, output):
        self.basedir = os.path.abspath('.')

        self.player_dirs = [p1_dir, p2_dir]
        self.player_color = [board.Board.BLACK, board.Board.WHITE]
        self.color_names = ['black', 'white']
        self.board = board.Board()

        self.history = []  # a list of performed moves (tuple: ((x,y), color)
        self.history_file = open(history, 'w')
        self.output_file = output

        self.delay = delay
        self.redir_stdout = stdout

        self.result = None

        # start and finish times of match
        self.start = None
        self.finish = None

    def __del__(self):
        self.history_file.close()

    def run(self):
        self.start = time.localtime()
        player = 0

        illegal_count = [0, 0]  # counts the number of illegal move attempts

        while True:  # runs until endgame

            # checks whether players have available moves
            no_moves_current = len(self.board.legal_moves(self.player_color[player])) == 0
            no_moves_opponent = len(self.board.legal_moves(self.board.opponent(self.player_color[player]))) == 0

            # calculates scores
            p1_score = sum([1 for char in str(self.board) if char == self.board.BLACK])
            p2_score = sum([1 for char in str(self.board) if char == self.board.WHITE])

            # disqualify player if he attempts illegal moves 5 times in a row
            if illegal_count[player] >= 5:
                print('Player %d DISQUALIFIED! Too many illegal move attempts.' % (player + 1))
                print('End of game reached!')
                print('Player 1 (black): %d' % p1_score)
                print('Player 2 (white): %d' % p2_score)

                self.result = 1 - player
                self.finish = time.localtime()
                return self.result

            # checks whether both players don't have available moves (end of game)
            if no_moves_current and no_moves_opponent:

                print('End of game reached! Scores:')
                print('Player 1 (black): %d' % p1_score)
                print('Player 2 (white): %d' % p2_score)

                if p1_score > p2_score:
                    print('Player 1 wins!')
                elif p2_score > p1_score:
                    print('Player 2 wins!')
                else:
                    print('Draw!')

                self.result = 0 if p1_score > p2_score else 1 if p2_score > p1_score else 2
                self.finish = time.localtime()
                return self.result

            # if current player has no moves, toggle player and continue
            if no_moves_current:
                print('Player %d has no legal moves and will not play this turn.' % (player + 1))
                illegal_count[player] = 0
                player = 1 - player
                continue

            player_dir = self.player_dirs[player]
            os.chdir(os.path.join(self.basedir, player_dir))

            # puts file in player dir
            path_to_state = self.STATE_FILE
            state_file = open(path_to_state, 'w')

            state_file.write(str(self.board))
            state_file.close()

            # starts player process
            stdout = open(self.redir_stdout, 'a') if self.redir_stdout is not None else sys.stdout
            player_process = subprocess.Popen(
                ['./launch.sh', self.STATE_FILE, self.color_names[player]],
                stdout=stdout,
                preexec_fn=os.setsid
            )

            #  waits 'delay' seconds for the move to complete
            print('Waiting for next move of Player %d...' % (player + 1))
            a = player_process.wait(self.delay)
            #time.sleep(self.delay)

            # kills player process, collects and processes move
            # os.killpg(os.getpgid(player_process.pid), signal.SIGKILL)
            player_process.terminate()

            print('Will read player\'s move.')

            move_path = self.MOVE_FILE
            if os.path.exists(move_path):
                # reads move
                try:
                    x, y = (int(c) for c in open(move_path).read().strip().split(','))
                except ValueError:
                    print("Error while reading Player %d move." % (player + 1))
                    print("Possibly it has not performed a move or its format is not correct.")
                    print("Player %d current call flagged as illegal move." % (player + 1))
                    illegal_count[player] += 1
                    player = 1 - player
                    continue

                # saves move in history
                self.history_file.write('%d,%d,%s\n' % (x, y, self.player_color[player]))
                self.history.append(((x, y), self.player_color[player]))

                if self.board.process_move((x, y), self.player_color[player]):
                    illegal_count[player] = 0
                    print('Player %d move %d,%d accepted.' % (player + 1, x, y))

                else:
                    illegal_count[player] += 1
                    print('Player %d move %d,%d ILLEGAL!' % (player + 1, x, y))

            else:
                print('Player %d has not made a move and lost its turn.' % (player + 1))

            round_score = self.board.piece_count[self.player_color[0]] - self.board.piece_count[self.board.opponent(self.player_color[0])]
            print('Current board: Player [BLACK] score = ' + str(round_score))
            print(self.board.decorated_str())

            # toggle player for next move
            player = 1 - player

    def write_output(self):
        """
        Writes a xml file with detailed match data
        :return:
        """
        os.chdir(self.basedir)

        root = ET.Element('othello-match')

        colors = [self.board.BLACK, self.board.WHITE, 'None']
        self.player_dirs.append('None')  # trick for writing a draw match

        timing = ET.SubElement(root, 'timing')
        timing.set('start', time.asctime(self.start))
        timing.set('finish', time.asctime(self.finish))

        scores = [self.board.piece_count['B'], self.board.piece_count['W']]

        for idx, p in enumerate(self.player_dirs[:2]):
            elem = ET.SubElement(root, 'player%d' % (idx + 1))
            elem.set('directory', p)
            elem.set('color', colors[idx])

            result = 'win' if scores[idx] > scores[idx - 1] else 'loss' if scores[idx] < scores[idx - 1] else 'draw'
            elem.set('result', result)
            elem.set('score', str(scores[idx]))

        moves = ET.SubElement(root, 'moves')

        for coords, color in self.history:
            move = ET.SubElement(moves, 'move')
            move.set('coord', '%d,%d' % coords)
            move.set('color', color)

        # preety xml thanks to: https://stackoverflow.com/a/1206856/1251716
        ugly_xml = ET.tostring(root).decode('utf-8')
        dom = xml.dom.minidom.parseString(ugly_xml)  # or xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml()
        f = open(self.output_file, 'w')
        f.write(pretty_xml)
        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Othello server.')
    parser.add_argument('players', metavar='player', type=str, nargs=2,
                        help='Path to player directory')
    parser.add_argument('-d', '--delay', type=float, metavar='delay',
                        default=5.0,
                        help='Time allocated for players to make a move.')

    parser.add_argument('-r', '--redir-stdout', dest='redir_stdout', type=str,
                        default=None, metavar='stdout-file',
                        help='File to redirect players output')

    parser.add_argument('-l', '--log-history', type=str, dest='history',
                        default='history.txt', metavar='log-history',
                        help='File to save game log (history).')

    parser.add_argument('-o', '--output-file', type=str, dest='output',
                        default='results.xml', metavar='output-file',
                        help='File to save game details (includes history)')

    args = parser.parse_args()
    p1, p2 = args.players

    s = Server(p1, p2, args.delay, args.redir_stdout, args.history, args.output)
    s.run()
    s.write_output()
