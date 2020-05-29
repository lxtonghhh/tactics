import time, random

CHAMPION_DICT = {
    "Lucian": dict(
        quality=2,
        character="shooter",
        AD=[50, 100, 180],
        AP=[0, 0, 0],
        DEF=[25, 25, 25],
        RES=[20, 20, 20],
        ASP=[0.7, 0.7, 0.7],
        CRT=[0.25, 0.25, 0.25],
        HP=[500, 900, 1600],
        MP=[30, 30, 30],
        range=[3, 3, 3],
        speed=[1, 1, 1],
    ),
    "Yasso": dict(
        quality=2,
        character="shooter",
        AD=[50, 90, 160],
        AP=[0, 0, 0],
        DEF=[30, 30, 30],
        RES=[20, 20, 20],
        ASP=[0.8, 0.8, 0.8],
        CRT=[0.25, 0.25, 0.25],
        HP=[600, 1100, 2000],
        MP=[100, 100, 100],
        range=[1, 1, 1],
        speed=[1, 1, 1],
    ),
    "Ali": dict(
        quality=2,
        character="mage",
        AD=[40, 80, 150],
        AP=[0, 0, 0],
        DEF=[20, 20, 20],
        RES=[20, 20, 20],
        ASP=[0.7, 0.7, 0.7],
        CRT=[0, 0, 0],
        HP=[600, 1000, 1900],
        MP=[80, 80, 80],
        range=[3, 3, 3],
        speed=[1, 1, 1],
    ),
    "Blank": dict(  # 空英雄
        quality=2,
        character="shooter",
        AD=[50, 90, 160],
        AP=[0, 0, 0],
        DEF=[30, 30, 30],
        RES=[20, 20, 20],
        ASP=[0.8, 0.8, 0.8],
        CRT=[0.25, 0.25, 0.25],
        HP=[600, 1100, 2000],
        MP=[100, 100, 100],
        range=[1, 1, 1],
        speed=[1, 1, 1],
    ),
}


class Champion(object):
    def __init__(self, name, quality, level, character, AD, AP, DEF, RES, ASP, CRT, HP, MP, range, speed):
        """
        quality 棋子品质1-5
        level 棋子星级1-3
        character 羁绊
        物理攻击 决定普通攻击造成的伤害 AD
        法术强度 决定释放技能的效果 AP
        物理护甲 百分比减少物理伤害 DEF
        魔法抗性 百分比减少魔法伤害 RES magic resist
        攻击速度 每秒攻击次数 ASP attack speed
        暴击率 普通攻击造成双倍伤害的概率 CRT critical ratio
        最大生命值 生命值归零该棋子死亡 HP
        最大能量值 能量值积蓄满时可以施法一次技能随后清零 通过以下方式可以积蓄能量值：时间自然增长,受到伤害，造成伤害 MP

        射程 结合与目标棋子的距离判断是否能够对目标棋子进行普通攻击 range
        移动速度 棋盘上移动速度 speed

        idx 战斗序列中的idx

        """
        self.name = name
        self.quality = quality
        self.level = level
        self.character = character
        self.AD = AD
        self.AP = AP
        self.DEF = DEF
        self.RES = RES

        self.set_ASP(ASP)

        self.CRT = CRT
        self.HP = HP
        self.HP_MAX = HP
        self.MP = MP
        self.range = range
        self.speed = speed

        self.ALIVE = True
        # 记录上一次普攻的time
        self.attack_timer = 0
        # 记录上一次移动的time
        self.move_timer = 0
        # 移动间隔时间0.5s
        self.move_interval = 0.5

        # 战斗序列
        self.idx = -1

    def set_idx(self, idx):
        self.idx = idx

    def set_ASP(self, ASP):
        self.ASP = ASP
        self.attack_interval = 1 / ASP

    def set_HP(self, HP):
        self.HP = HP

    def check_attack(self):
        return time.time() - self.attack_timer > self.attack_interval

    def check_move(self):
        return time.time() - self.move_timer > self.move_interval

    def check_critical(self):
        return random.random() <= self.CRT

    def update_attack_timer(self):
        self.attack_timer = time.time()

    def update_move_timer(self):
        self.move_timer = time.time()

    def attack(self, target):
        dealt_damage = self.AD if not self.check_critical() else self.AD * 2
        target.undertake_attack_damage(dealt_damage)

    def undertake_attack_damage(self, damage):
        actual_damage = damage / (1 + self.DEF / 100)
        self.set_HP(self.HP - actual_damage)
        print(self.name, "受到伤害： ", actual_damage, "剩余生命值： ", self.HP)
        self.check_alive()
        return actual_damage

    def check_alive(self):
        if self.HP <= 0:
            self.ALIVE = False
            print(self.name, "阵亡")
            return False
        else:
            return True


def make_champion(name, level):
    info = CHAMPION_DICT[name]
    base = dict(name=name, level=level, quality=info['quality'], character=info['character'])
    detail = {key: info[key][level - 1] for key in
              ["AD", "AP", "DEF", "RES", "ASP", "CRT", "HP", "MP", "range", "speed", ]}
    champion_info = {**base, **detail}
    # print(champion_info)
    obj = Champion(**champion_info)
    return obj
def make_champions(name, num):
    return [make_champion(name, 2) for i in range(num)]
