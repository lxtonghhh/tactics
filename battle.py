from tactics.common import Position, TEAM_B, TEAM_A
from tactics.champion import make_champion
from tactics.model import load_champion


class BattleController(object):
    def __init__(self, pieces, championsA, championsB):
        """

        :param pieces: 棋子模型对象数组
        :param championsA:
        :param championsB:
        """
        self.pieces = pieces
        self.battle_queue = []
        self.position_queue = []
        self.alive_queue = []
        self.board = [0] * 64  # 记录64个格子是否被占用
        if len(championsA) < len(championsB):
            num = len(championsA)
            for i in range(0, num):
                self.battle_queue.append(championsA[i])
                self.battle_queue.append(championsB[i])
                championsA[i].set_idx(i * 2 + 0)
                championsB[i].set_idx(i * 2 + 1)
                self.position_queue.append(Position(-1, -1))
                self.position_queue.append(Position(-1, -1))
                self.alive_queue.append(True)
                self.alive_queue.append(True)
            for i in range(num, len(championsB)):
                self.battle_queue.append(make_champion(name="Blank", level=2))
                self.battle_queue.append(championsB[i])
                # championsA[i].set_idx(i * 2 + 0)
                championsB[i].set_idx(i * 2 + 1)
                self.position_queue.append(None)
                self.position_queue.append(Position(-1, -1))
                self.alive_queue.append(False)
                self.alive_queue.append(True)

        elif len(championsA) > len(championsB):
            num = len(championsB)
            for i in range(0, num):
                self.battle_queue.append(championsA[i])
                self.battle_queue.append(championsB[i])
                championsA[i].set_idx(i * 2 + 0)
                championsB[i].set_idx(i * 2 + 1)
                self.position_queue.append(Position(-1, -1))
                self.position_queue.append(Position(-1, -1))
                self.alive_queue.append(True)
                self.alive_queue.append(True)
            for i in range(num, len(championsA)):
                self.battle_queue.append(championsA[i])
                self.battle_queue.append(make_champion(name="Blank", level=2))
                championsA[i].set_idx(i * 2 + 0)
                # championsB[i].set_idx(i * 2 + 1)
                self.position_queue.append(Position(-1, -1))
                self.position_queue.append(None)
                self.alive_queue.append(True)
                self.alive_queue.append(False)
        else:
            # idx偶数为A方（近） idx奇数为B方（远）
            num = len(championsA)
            for i in range(0, num):
                self.battle_queue.append(championsA[i])
                self.battle_queue.append(championsB[i])
                championsA[i].set_idx(i * 2 + 0)
                championsB[i].set_idx(i * 2 + 1)
                self.position_queue.append(Position(-1, -1))
                self.position_queue.append(Position(-1, -1))
                self.alive_queue.append(True)
                self.alive_queue.append(True)

    def update_render(self, event, info):
        # todo 渲染接口本应该在渲染管理器中实现
        if event == "death":
            old_pos = info["pos"]
            self.pieces[old_pos.idx].delete()
            self.pieces[old_pos.idx] = None
        elif event == "movement":
            idx, old_pos, new_pos, name = info["idx"], info["old_pos"], info["new_pos"], info["name"]
            if new_pos is None:
                # 未发生移动
                pass
            else:
                self.pieces[old_pos.idx].delete()
                self.pieces[old_pos.idx] = None
                if idx % 2 == 0:
                    self.pieces[new_pos.idx] = load_champion(name=name, posi=new_pos.idx, heading=90, color=TEAM_A)
                else:
                    self.pieces[new_pos.idx] = load_champion(name=name, posi=new_pos.idx, heading=-90, color=TEAM_B)
        else:
            pass

    def get_champion(self, idx):
        return self.battle_queue[idx]

    def get_position(self, idx):
        pos = self.position_queue[idx]
        if pos:
            return "({0},{1})".format(pos.x, pos.y)
        else:
            return None

    def set_position(self, idx, x, y):
        pos = self.position_queue[idx]
        if pos:
            pos.update(x, y)
            if idx % 2 == 0:
                self.board[pos.idx] = 1
            else:
                self.board[pos.idx] = -1
        else:
            pass

    def _occupied(self, idx):
        if not idx:
            return True
        else:
            return self.board[idx]

    def _get_distance(self, pos1: Position, pos2: Position):
        return max(abs(pos1.x - pos2.x), abs(pos1.y - pos2.y))

    def _get_distance_geometry(self, pos1: Position, pos2: Position):
        return ((pos1.x - pos2.x) ** 2, (pos1.y - pos2.y) ** 2) ** 0.5

    def _get_enemy_in_distance(self, idx, distance: int):
        """
        寻找存活且在当前角色距离内的敌人
        :param idx:
        :param distance:
        :return:
        """
        targets = []
        if idx % 2 == 1:
            # 我为B奇数敌人为A偶数
            for j in range(0, len(self.position_queue), 2):
                if self.alive_queue[j]:
                    dis = self._get_distance(self.position_queue[idx], self.position_queue[j])
                    if dis <= distance:
                        targets.append(self.battle_queue[j])
                    else:
                        pass
                else:
                    pass
        else:
            # 我为A偶数敌人为B奇数
            for j in range(1, len(self.position_queue), 2):
                if self.alive_queue[j]:
                    dis = self._get_distance(self.position_queue[idx], self.position_queue[j])
                    if dis <= distance:
                        targets.append(self.battle_queue[j])
                    else:
                        pass
                else:
                    pass
        return targets

    def _find_most_valuable_enemy(self, idx, targets):
        """
        当前角色idx从目标敌人targets中依据一定标准选择最佳攻击目标
        :param idx:
        :param targets:
        :return:
        """
        # 根据AD选择
        if targets:
            targets.sort(key=lambda c: c.AD)
            return targets[0].idx
        else:
            return -1

    def search_target(self, idx, distance: int) -> int:
        """
        mve most_valuable_enemy
        :return: idx
        """
        targets = self._get_enemy_in_distance(idx, distance)
        print("-->有以下目标： ")
        for item in targets:
            print(item.name, self.get_position(item.idx))
        mve = self._find_most_valuable_enemy(idx, targets)
        return mve

    def _get_enemy_all(self, idx):
        """
        寻找所有存活敌人
        :param idx:
        :param distance:
        :return:
        """
        targets = []
        if idx % 2 == 1:
            # 我为B奇数敌人为A偶数
            for j in range(0, len(self.position_queue), 2):
                if self.alive_queue[j]:
                    targets.append(self.battle_queue[j])
                else:
                    pass
        else:
            # 我为A偶数敌人为B奇数
            for j in range(1, len(self.position_queue), 2):
                if self.alive_queue[j]:
                    targets.append(self.battle_queue[j])
                else:
                    pass
        return targets

    def move_champion(self, idx, speed):
        """
        移动算法 1.向着mve移动 2.新位置不可有人
        :param idx:
        :param speed:
        :return:
        """

        # 速度默认为1
        speed = 1
        targets = self._get_enemy_all(idx)
        mve = self._find_most_valuable_enemy(idx, targets)
        if mve < 0:
            print("未找到目标 暂时不移动".format())
            return None
        pos_now = self.position_queue[idx]
        pos_tar = self.position_queue[mve]
        print("now: ", pos_now, "mve: ", mve, pos_tar)
        vec = (pos_tar.x - pos_now.x, pos_tar.y - pos_now.y)

        # 两个备选位置
        if vec[0] > 0:
            pos1 = Position(pos_now.x + 1, pos_now.y)
            pos1i = pos1.idx
        elif vec[0] < 0:
            pos1 = Position(pos_now.x - 1, pos_now.y)
            pos1i = pos1.idx
        else:
            pos1i = None
        if vec[1] > 0:
            pos2 = Position(pos_now.x, pos_now.y + 1)
            pos2i = pos2.idx
        elif vec[1] < 0:
            pos2 = Position(pos_now.x, pos_now.y - 1)
            pos2i = pos2.idx
        else:
            pos2i = None
        if pos1i and pos2i:
            # 选择最佳 向着最远的方向移动
            if abs(vec[0]) < abs(vec[1]):
                pos1, pos2 = pos2, pos1
                pos1i, pos2i = pos2i, pos1i
            pass
        else:
            pass
        if not self._occupied(pos1i):
            self.board[pos_now.idx] = 0
            self.set_position(idx=idx, x=pos1.x, y=pos1.y)
            print("{0}移动至{1}".format(pos_now.idx, self.get_position(idx)))
            return pos1
        elif not self._occupied(pos2i):
            self.board[pos_now.idx] = 0
            self.set_position(idx=idx, x=pos2.x, y=pos2.y)
            print("移动至{0}".format(self.get_position(idx)))
            return pos2
        else:
            pass
            print("未发生移动".format())
            return None

    def fight(self):
        """
        阵亡或者移动位置
        (idx,old_pos,new_pos) new_pos为None表示未移动
        :return:
        """
        # todo 不应该在遍历中有返回
        bq = self.battle_queue
        num = len(bq)
        for i in range(num):
            if not self.alive_queue[i]:
                continue
            else:
                pass
            champion = self.battle_queue[i]

            print("->现在轮到{0} {1} 位置{2}".format(i, champion.name, self.get_position(idx=i)))
            mve = self.search_target(idx=i, distance=champion.range)  # champion.range
            if mve >= 0:
                target = self.battle_queue[mve]
                print("-->找到攻击目标{0} {1} 位置{2}".format(mve, target.name, self.get_position(idx=mve)))
                if champion.check_attack():
                    champion.update_attack_timer()
                    print("--->进行攻击".format())
                    champion.attack(target)
                    if target.check_alive():
                        pass
                    else:
                        # 目标阵亡
                        print("---->目标{0} {1}阵亡".format(mve, target.name, ))
                        self.alive_queue[mve] = False
                        # 移出
                        pos = self.position_queue[mve]
                        self.board[pos.idx] = 0
                        self.position_queue[mve] = None
                        # 调用更新渲染状态接口
                        self.update_render(event="death", info=dict(idx=mve, pos=pos))
                        # return (mve, pos, None)

                else:
                    # 攻击尚未冷却
                    print("--->攻击尚未冷却".format())
                    pass
            else:
                print("-->未找到攻击目标 开始移动".format())

                if champion.check_move():
                    champion.update_move_timer()
                    print("--->进行移动".format())
                    old_pos = self.position_queue[i]
                    old_pos = Position(old_pos.x, old_pos.y)
                    new_pos = self.move_champion(idx=i, speed=champion.speed)
                    # 调用更新渲染状态接口
                    self.update_render(event="movement",
                                       info=dict(idx=i, old_pos=old_pos, new_pos=new_pos, name=champion.name))
                    # return (i, old_pos, new_pos)
                else:
                    # 移动尚未冷却
                    print("--->移动尚未冷却".format())
                    pass

    def show_alive_queue(self):
        print(self.alive_queue)

    def show_postion_queue(self):
        for i, pos in enumerate(self.position_queue):
            if pos:
                print(i, "({0},{1})".format(pos.x, pos.y))
            else:
                print(i, None)

    def show_board(self):
        p2i = lambda x, y: (y * 8 + x)
        for y in range(7, -1, -1):
            row = ""
            for x in range(8):
                if self.board[p2i(x, y)] == -1:
                    row += "b "
                elif self.board[p2i(x, y)] == 0:
                    row += "+ "
                elif self.board[p2i(x, y)] == 1:
                    row += "a "
                else:
                    raise Exception
            print(row)
