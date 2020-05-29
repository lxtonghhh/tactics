#!/usr/bin/env python

# Author: Shao Zhang and Phil Saltzman
# Models: Eddie Canaan
# Last Updated: 2015-03-13
#
# This tutorial shows how to determine what objects the mouse is pointing to
# We do this using a collision ray that extends from the mouse position
# and points straight into the scene, and see what it collides with. We pick
# the object with the closest collision

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
from tactics.common import Position, posi2pos
from tactics.champion import make_champions
from tactics.battle import BattleController
from tactics.model import load_champion
import sys
from enum import Enum

GREY = (0.85, 0.85, 0.85, 1)
WHITE = (1, 1, 1, 1)
RED = (1, 0, 0, 1)
GREEN = (0.6, 0.98, 0.6, 1)
BLUE = (0.27, 0.50, 0.70, 1)
HIGHLIGHT = (0, 1, 1, 1)
PIECEBLACK = (.15, .15, .15, 1)

TEAM_A = RED
TEAM_B = BLUE


# Now we define some helper functions that we will need later

# This function, given a line (vector plus origin point) and a desired z value,
# will give us the point on the line where the desired z value is what we want.
# This is how we know where to position an object in 3D space based on a 2D mouse
# position. It also assumes that we are dragging in the XY plane.
#
# This is derived from the mathematical of a plane, solved for a given point
def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())


# A handy little function for getting the proper position for a given square1
def SquarePos(i):
    # old return LPoint3((i % 8)- 3.5, int(i // 8)- 3.5, 0)
    return LPoint3((i % 8) * 2 - 7, int(i // 8) * 2 - 7, 0)


# Helper function for determining whether a square should be white or black
# The modulo operations (%) generate the every-other pattern of a chess-board
def SquareColor(i):
    if (i + ((i // 8) % 2)) % 2:
        return GREY
    else:
        return WHITE


class GameStatus(Enum):
    Strategy = 1
    Battle = 2  # 战斗中
    End = 3  # 战斗结束后


class ChessboardDemo(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        # This code puts the standard title and instruction text on screen
        self.title = OnscreenText(text="Auto Chess",
                                  style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                                  pos=(0.8, -0.95), scale=.07)
        """
        self.escapeEvent = OnscreenText(
            text="ESC: Quit", parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale=.05)
        self.mouse1Event = OnscreenText(
            text="Left-click and drag: Pick up and drag piece",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)
        
        """

        self.accept('escape', sys.exit)  # Escape quits
        self.disableMouse()  # Disble mouse camera control
        # camera.setPosHpr(0, -12, 8, 0, -35, 0)  # Set the camera
        # x左右 y里外 z上下 hpr旋转角度
        camera.setPosHpr(0, -24, 16, 0, -35, 0)  # Set the camera
        self.setupLights()  # Setup default lighting

        # Now we set picker
        self.setPicker(isShow=False)

        # Now we create the chess board and its pieces
        self.renderChessboard()

        # This will represent the index of the currently highlited square
        self.hiSq = False
        # This wil represent the index of the square where currently dragged piece
        # was grabbed from
        self.dragging = False

        # Now init game data
        self.gamestatus = GameStatus.Strategy
        self.scoreA = 0
        self.scoreB = 0

        # 初始化棋子
        self.initA()
        self.initB()

        self.init_pieces()
        self.init_battle_controller()
        self.renderPiece()

        # 战斗开始按钮 改变游戏状态
        self.accept('s', self.start_fight)

        # 计分板
        self.set_score_board()

        # Start the task that handles the picking
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')

        self.accept("mouse1", self.grabPiece)  # left-click grabs a piece
        self.accept("mouse1-up", self.releasePiece)  # releasing places it

    def initA(self):
        # 设置红方棋子
        self.ca = make_champions("Ali", 8) + make_champions("Lucian", 1)

    def initB(self):
        # 设置蓝方棋子
        self.cb = make_champions("Yasso", 9)

    def start_fight(self):

        if self.gamestatus == GameStatus.Battle:
            # 战斗中 无效
            pass
        elif self.gamestatus == GameStatus.End:
            # 战斗结束 重置棋子
            self.update_score_board()
            self.reset_game()
            self.gamestatus = GameStatus.Strategy
        elif self.gamestatus == GameStatus.Strategy:
            self.gamestatus = GameStatus.Battle
            self.update_score_board()
            self.battleTask = taskMgr.add(self.battleTask, 'battleTask')
        else:
            pass

    def set_score_board(self):
        if self.gamestatus == GameStatus.Strategy:
            status = "Strategy Stage"
        else:
            status = "Battle Stage"
        self.status_board = OnscreenText(
            text="{0}".format(status), parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale=0.1)
        self.score_board = OnscreenText(
            text="{0}:{1}".format(self.scoreA, self.scoreB),
            align=TextNode.ACenter, parent=base.a2dTopCenter,
            style=1, fg=(1, 1, 1, 1), pos=(0, -0.1), scale=0.1)

    def update_score_board(self):
        if self.gamestatus == GameStatus.Strategy:
            status = "Strategy Stage"
        else:
            status = "Battle Stage"
        self.status_board.setText("{0}".format(status))
        self.score_board.setText("{0}:{1}".format(self.scoreA, self.scoreB))

    def set_blood_bar(self):
        bc = self.bc
        self.blood_bars = [None] * len(bc.position_queue)
        for j in range(0, len(bc.position_queue), 2):
            self.blood_bars[j] = OnscreenText(
                text="",
                parent=base.a2dTopLeft, align=TextNode.ALeft,
                style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.32 - (j // 2) * 0.05), scale=.05)
        for j in range(1, len(bc.position_queue), 2):
            self.blood_bars[j] = OnscreenText(
                text="",
                parent=base.a2dTopRight, align=TextNode.ARight,
                style=1, fg=(1, 1, 1, 1), pos=(-0.06, -0.32 - (j // 2) * 0.05), scale=.05)

    def reset_game(self):
        self.initA()
        self.initB()
        for item in self.pieces:
            if item:
                item.delete()
        for item in self.blood_bars:
            if item:
                item.destroy()
        self.init_pieces()
        self.init_battle_controller()
        self.renderPiece()

    def init_battle_controller(self):
        ca = self.ca
        cb = self.cb
        bc = BattleController(pieces=self.pieces, championsA=ca, championsB=cb)
        self.bc = bc
        # 初始化英雄血条
        self.set_blood_bar()
        # 初始化位置 从第0列和第7列开始排布
        for j in range(0, len(bc.position_queue), 2):
            # A
            x = (j // 2) // 8
            y = (j // 2) % 8
            bc.set_position(j, x, y)
        for j in range(1, len(bc.position_queue), 2):
            # B
            x = 7 - (j // 2) // 8
            y = (j // 2) % 8
            bc.set_position(j, x, y)

        self.tick = 0

        self.updateBloodBar()

    def setUI(self):
        obj = DirectLabel(text="Test", text_bg=(1, 1, 0, 1), parent=base.a2dTopLeft, text_style=1,
                          text_pos=(0.1, -0.32), text_fg=(), text_scale=0.05, enableEdit=True)

    def setPicker(self, isShow=False):
        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        # 展示射线
        if isShow:
            self.picker.showCollisions(render)
        else:
            pass

    def updateBloodBar(self):
        # self.slider=DirectSlider(range=(0,100),value=100,)

        bc = self.bc
        bq = bc.battle_queue
        for i, champion in enumerate(bq):
            if champion.name != "Blank":
                self.blood_bars[i].setText("{0}: {1}/{2}".format(champion.name, int(champion.HP), champion.HP_MAX))

    def renderChessboard(self):

        # We will attach all of the squares to their own root. This way we can do the
        # collision pass just on the squares and save the time of checking the rest
        # of the scene
        self.squareRoot = render.attachNewNode("squareRoot")

        # For each square
        self.squares = [None for i in range(64)]

        for i in range(64):
            # Load, parent, color, and position the model (a single square
            # polygon)
            self.squares[i] = loader.loadModel("models/square")
            self.squares[i].reparentTo(self.squareRoot)
            self.squares[i].setPos(SquarePos(i))
            self.squares[i].setColor(SquareColor(i))
            # old self.squares[i].setScale((1,1,1))
            self.squares[i].setScale((2, 2, 2))
            # Set the model itself to be collideable with the ray. If this model was
            # any more complex than a single polygon, you should set up a collision
            # sphere around it instead. But for single polygons this works
            # fine.
            self.squares[i].find("**/polygon").node().setIntoCollideMask(
                BitMask32.bit(1))
            # Set a tag on the square's node so we can look up what square this is
            # later during the collision pass
            self.squares[i].find("**/polygon").node().setTag('square', str(i))

            # We will use this variable as a pointer to whatever piece is currently
            # in this square

    def init_pieces(self):
        self.pieces = [None for i in range(64)]

    def renderPiece(self):

        bc = self.bc
        bq = bc.battle_queue
        pq = bc.position_queue
        aq = bc.alive_queue
        # A方 白色
        for i in range(0, len(bq), 2):
            if aq[i]:
                posi = pq[i].idx
                name = bq[i].name
                # self.pieces[posi] = Pawn(posi, WHITE)
                self.pieces[posi] = load_champion(name, posi, heading=90, color=TEAM_A)
            else:
                pass
        # B方 黑色
        for i in range(1, len(bq), 2):
            if aq[i]:
                posi = pq[i].idx
                name = bq[i].name
                # self.pieces[posi] = Pawn(posi, BLACK)
                self.pieces[posi] = load_champion(name, posi, heading=-90, color=TEAM_B)

            else:
                pass

    def renderOnePiece(self, idx, name, old_pos, new_pos):

        self.pieces[old_pos.idx].delete()
        self.pieces[old_pos.idx] = None
        if new_pos is None:
            # 阵亡 移出
            # print(self.pieces[old_pos.idx], old_pos.idx)
            pass
        else:
            # print(self.pieces[old_pos.idx], old_pos.idx, new_pos.idx)
            if idx % 2 == 0:
                self.pieces[new_pos.idx] = load_champion(name=name, posi=new_pos.idx, heading=90, color=TEAM_A)
                # self.pieces[new_pos.idx] = Pawn(new_pos.idx, WHITE)
            else:
                self.pieces[new_pos.idx] = load_champion(name=name, posi=new_pos.idx, heading=-90, color=TEAM_B)
                # self.pieces[new_pos.idx] = Pawn(new_pos.idx, BLACK)
        """
        self.pieces[old_pos.idx] = None
              if new_pos is None:
            # 阵亡 移出
            pass
        else:
            if idx % 2 == 0:
                self.pieces[new_pos.idx] = Pawn(new_pos.idx, WHITE)
            else:
                self.pieces[new_pos.idx] = Pawn(new_pos.idx, BLACK)
        
        """

    # This function swaps the positions of two pieces
    def swapPieces(self, fr, to):
        # 改变棋子模型位置
        # 改变棋子数据
        bc = self.bc
        pq = bc.position_queue
        aq = bc.alive_queue
        board = bc.board  # 记录64个格子是否被占用
        # 根据位置获得棋子fr的idx
        # 首先确保移动棋子fr存活
        idx_fr = None
        for i, item in enumerate(pq):
            if item and item.idx == fr and aq[i] == True:
                idx_fr = i
                break
            else:
                continue

        if idx_fr is None:
            # 未找到存活棋子 不应该
            raise Exception

        idx_to = None
        for i, item in enumerate(pq):
            if item and item.idx == to and aq[i] == True:
                idx_to = i
                break
            else:
                continue
        if idx_to is not None:
            # 目标位置有存活棋子
            # 1.交换模型位置
            print(type(self.pieces[fr]), "前往目标位置已有棋子: ", type(self.pieces[to]))
            self.pieces[fr], self.pieces[to] = self.pieces[to], self.pieces[fr]
            self.pieces[fr].square = fr
            self.pieces[fr].obj.setPos(SquarePos(fr))
            self.pieces[to].square = to
            self.pieces[to].obj.setPos(SquarePos(to))
            # 2.更新棋子位置信息
            fr_pos, to_pos = posi2pos(fr), posi2pos(to)
            pq[idx_fr] = to_pos
            pq[idx_to] = fr_pos
            # 3.更新格子占用信息
            board[fr], board[to] = board[to], board[fr]
        else:
            # 目标位置为空
            # 1.移动模型位置
            print(type(self.pieces[fr]), "前往目标位置为空", type(self.pieces[to]))
            self.pieces[fr], self.pieces[to] = self.pieces[to], self.pieces[fr]
            self.pieces[to].square = to
            self.pieces[to].obj.setPos(SquarePos(to))
            # 2.更新棋子位置信息
            fr_pos, to_pos = posi2pos(fr), posi2pos(to)
            pq[idx_fr] = to_pos
            # 3.更新格子占用信息
            board[fr], board[to] = board[to], board[fr]
        bc.show_board()
        bc.show_postion_queue()

    def battleTask(self, task):
        bc = self.bc
        tick = self.tick
        # 战斗环节
        num = len(bc.battle_queue)

        print("===本轮开始：", tick)
        bc.show_board()
        self.updateBloodBar()
        self.tick += 1
        # 判断阵营胜负
        Bwin = all([not bc.alive_queue[i] for i in range(0, num, 2)])
        Awin = all([not bc.alive_queue[i] for i in range(1, num, 2)])
        if Awin:
            print("======本轮战斗结束 红方获胜======")
            self.scoreA += 1
            self.gamestatus = GameStatus.End
            self.update_score_board()
            return Task.done
        elif Bwin:
            print("======本轮战斗结束 蓝方获胜======")
            self.scoreB += 1
            self.gamestatus = GameStatus.End
            self.update_score_board()
            return Task.done
        else:
            bc.fight()
            return Task.cont

    def mouseTask(self, task):
        # This task deals with the highlighting and dragging based on the mouse

        # First, clear the current highlight
        if self.hiSq is not False:
            self.squares[self.hiSq].setColor(SquareColor(self.hiSq))
            self.hiSq = False

        # Check to see if we can access the mouse. We need it to do anything
        # else
        if self.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.mouseWatcherNode.getMouse()
            # print("mouse pos: ",mpos)
            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            # If we are dragging something, set the position of the object
            # to be at the appropriate point over the plane of the board
            if self.dragging is not False:
                # Gets the point described by pickerRay.getOrigin(), which is relative to
                # camera, relative instead to render
                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                # Same thing with the direction of the ray
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                new_pos = PointAtZ(.5, nearPoint, nearVec)
                self.pieces[self.dragging].obj.setPos(new_pos)
                # print(self.dragging,"set pos: ", new_pos)
            # Do the actual collision pass (Do it only on the squares for
            # efficiency purposes)
            self.picker.traverse(self.squareRoot)
            if self.pq.getNumEntries() > 0:
                # if we have hit something, sort the hits so that the closest
                # is first, and highlight that node
                self.pq.sortEntries()
                i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                # Set the highlight on the picked square
                self.squares[i].setColor(HIGHLIGHT)
                self.hiSq = i

        return Task.cont

    def grabPiece(self):
        # If a square is highlighted and it has a piece, set it to dragging
        # mode
        if self.hiSq is not False and self.pieces[self.hiSq]:
            self.dragging = self.hiSq
            print("grab from", self.dragging)
            self.hiSq = False

    def releasePiece(self):
        # Letting go of a piece. If we are not on a square, return it to its original
        # position. Otherwise, swap it with the piece in the new square
        # Make sure we really are dragging something
        if self.dragging is not False:
            # We have let go of the piece, but we are not on a square
            posi_from, posi_to = self.dragging, self.hiSq

            if posi_from % 8 <= 3 and posi_to % 8 <= 3:
                # 红色方布置
                print(("红色方布置grab from", posi_from, "release to", posi_to))
                pass
            elif posi_from % 8 >= 4 and posi_to % 8 >= 4:
                # 蓝色方布置
                print(("蓝色方布置grab from", posi_from, "release to", posi_to))
                pass
            else:
                # 不可跨界布置
                print(("不可跨界布置grab from", posi_from, "release to", posi_to))
                posi_to = False

            if posi_to is False:
                # hiSq位于棋盘外 不可放置
                self.pieces[posi_from].obj.setPos(
                    SquarePos(posi_from))
            else:
                # hiSq位于棋盘内 可以放置
                # Otherwise, swap the pieces
                self.swapPieces(posi_from, posi_to)

        # We are no longer dragging anything
        self.dragging = False

    def setupLights(self):  # This function sets up some default lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))


if __name__ == "__main__":
    # Do the main initialization and start 3D rendering
    demo = ChessboardDemo()
    demo.run()
