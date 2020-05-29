from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

import sys


# A handy little function for getting the proper position for a given square1
def SquarePos(i):
    # old return LPoint3((i % 8)- 3.5, int(i // 8)- 3.5, 0)
    return LPoint3((i % 8) * 2 - 7, int(i // 8) * 2 - 7, 0)


# Class for a piece. This just handles loading the model and setting initial
# position and color
class Piece(object):
    def __init__(self, square, color, heading):
        """

        :param square:
        :param color:
        """

        self.obj = loader.loadModel(self.model)
        self.obj.reparentTo(render)
        # type self.obj NodePath
        # self.obj.setColor(color)
        # self.obj.setColor((0,0,0,1))

        self.obj.setPos(SquarePos(square))
        self.obj.setScale(15)
        self.obj.setH(heading)

        self.pointer = loader.loadModel("models/pointer")
        self.pointer.reparentTo(self.obj)
        self.pointer.setColor(color)
        self.pointer.setScale(0.01)
        self.pointer.setPos(0, 0, 0.2)

    def delete(self):
        self.obj.detachNode()


class Pawn(Piece):
    model = "models/fighter"


class Yasso(Piece):
    model = "models/Yasso"


class Ali(Piece):
    model = "models/Ali"

    def __init__(self, square, color, heading):
        super().__init__(square, color, heading)
        self.obj.setScale(12)


class Lucian(Piece):
    model = "models/Lucian"


class King(Piece):
    model = "models/king"


class Queen(Piece):
    model = "models/queen"


class Bishop(Piece):
    model = "models/bishop"


class Knight(Piece):
    model = "models/knight"


class Rook(Piece):
    model = "models/rook"


def load_champion(name: str, posi: int, heading: int, color: tuple):
    if name == "Lucian":
        return Lucian(square=posi, color=color, heading=heading)
    elif name == "Yasso":
        return Yasso(square=posi, color=color, heading=heading)
    elif name == "Ali":
        return Ali(square=posi, color=color, heading=heading)
    else:
        return None
