import time, random

GREY = (0.85, 0.85, 0.85, 1)
WHITE = (1, 1, 1, 1)
RED = (1, 0, 0, 1)
GREEN = (0.6, 0.98, 0.6, 1)
BLUE = (0.27, 0.50, 0.70, 1)
HIGHLIGHT = (0, 1, 1, 1)
PIECEBLACK = (.15, .15, .15, 1)
TEAM_A = RED
TEAM_B = BLUE


class Position(object):
    def __init__(self, x, y):
        """
        x为横坐标 y为纵坐标 (x,y)表示y行x列 idx=y * 8 + x 表示第idx个格子[0,63] 为负表示不在场上
        :param x: [0,7]
        :param y: [0,7
        """
        self.x = x
        self.y = y
        self.idx = y * 8 + x

    def check_on(self):
        x, y = self.x, self.y
        if x > 0 and x < 8 and y > 0 and y < 8:
            return True
        else:
            return False

    def update(self, x, y):
        self.x = x
        self.y = y
        self.idx = y * 8 + x


def posi2pos(posi: int) -> Position:
    x, y = posi % 8, posi // 8
    return Position(x, y)
