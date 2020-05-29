from tactics.battle import BattleController
from tactics.champion import make_champion, make_champions
import time,random

def test():
    ca = make_champions("Lucian", 7)
    cb = make_champions("Yasso", 8)
    bc = BattleController(ca, cb)
    for j in range(0, len(bc.position_queue), 2):
        bc.set_position(j, j // 2, 0)
    for j in range(1, len(bc.position_queue), 2):
        bc.set_position(j, j // 2, 7)

    # 开始战斗环节
    tick = 0
    num = len(bc.battle_queue)
    while True:
        print("===本轮开始：", tick)
        bc.show_board()
        tick += 1
        # 判断阵营胜负
        Bwin = all([not bc.alive_queue[i] for i in range(0, num, 2)])
        Awin = all([not bc.alive_queue[i] for i in range(1, num, 2)])
        if Bwin or Awin:
            print("======结束======")
            break
        else:
            bc.fight()


def run():
    c1 = make_champion("Lucian", 2)
    c2 = make_champion("Yasso", 2)
    ll = [c1, c2]
    count, count1, count2, = 0, 0, 0
    while True:

        count += 1
        if c1.check_attack():
            print("Lucian->Yasso")
            c1.update_attack_timer()
            c1.attack(c2)
            count1 += 1
        else:
            pass
        if not c1.ALIVE or not c2.ALIVE:
            break
        if c2.check_attack():
            print("Yasso->Lucian")
            c2.update_attack_timer()
            c2.attack(c1)
            count2 += 1
        else:
            pass

        if not c1.ALIVE or not c2.ALIVE:
            break
    print(count, count1, count2)


def test_time(num=10):
    t1 = time.time()
    for i in range(num):
        test()
    t2 = time.time()
    print("运行{0}次 平均用时：{1} s".format(num, round((t2 - t1) / num, 4)), )

    exit()
if __name__ == "__main__":
    for i in [70, 130, 180]:
        print(i / 255)
    exit()
    test_time()
    test()
