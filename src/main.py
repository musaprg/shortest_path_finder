from enum import Enum
from pprint import pprint
from math import sqrt
import time
import copy
from itertools import groupby
from operator import itemgetter

class Map(Enum):
    NONE    = 0 # 何もない
    TRIED   = 1 # 探索済
    ROUTE   = 2 # ルートとして選択
    WALL    = 3 # 壁
    START   = 4 # スタート地点
    GOAL    = 5 # ゴール地点


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def ed(self, other):
        """
        euclid距離を算出
        """
        diff = self - other
        return sqrt(diff.x**2 + diff.y**2)

    def up(self):
        return self + Pos(0, -1)

    def down(self):
        return self + Pos(0, 1)

    def left(self):
        return self + Pos(-1, 0)

    def right(self):
        return self + Pos(1, 0)
    
    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other):
        if other is None or type(self) != type(other): return False
        return self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return "<Pos (%d,%d)>" % (self.x, self.y)


class MapField:
    def __init__(self, fieldmap, w, h, spos, gpos):
        self._map = fieldmap
        self.width = w
        self.height = h
        self.start = spos
        self.goal = gpos

    def get_mapobj(self, pos):
        return self._map[pos.y][pos.x]
    
    def set_mapobj(self, pos, mapobj):
        """
        Modify map object to mapobj at (x,y)
        """
        self._map[pos.y][pos.x] = mapobj
    
    def __str__(self):
        """
        print map structure
        """
        mapobj = {}
        mapobj[Map.NONE]    = "-"
        mapobj[Map.TRIED]   = "*"
        mapobj[Map.ROUTE]   = "+"
        mapobj[Map.WALL]    = "■"
        mapobj[Map.START]   = "S"
        mapobj[Map.GOAL]    = "G"
        output = ""
        for py, y in enumerate(self._map):
            for px, x in enumerate(y):
                if self.start.x == px and self.start.y == py:
                    output += mapobj[Map.START] + " "
                    continue
                elif self.goal.x == px and self.goal.y == py:
                    output += mapobj[Map.GOAL] + " "
                    continue
                output += mapobj[x] + " "
            output += "\n"
        return output


class Player:
    def __init__(self, fieldmap):
        self._map = fieldmap
        self.pos = self._map.start # 現在位置
        self.openlist = [(self._map.start, None, self._map.start.ed(self._map.goal))]
        self.closelist = []
        self.g = 0

    def update_openlist(self):
        pass

    def pick_route_from_openlist(self):
        pass

    def move(self, pos) -> None:
        # print("Move to ", pos)
        self.pos = pos
        self._map.set_mapobj(pos, Map.ROUTE)
        self.g += 1


class GPlayer(Player):
    """
    Greedy
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap)

    def play(self) -> bool:
        while True:
            # print(self._map)
            if len(self.openlist) == 0:
                print("Failed")
                return False
            node = self.pick_route_from_openlist()
            # print("Wanna go ", node[0])
            if node[0] == self._map.goal:
                print("Success")
                return True
            self.move(node[0])
            self.update_openlist()

    def update_openlist(self) -> None:
        """
        動ける範囲を返す
        """
        self.openlist = []
        candidates = [self.pos.up(), self.pos.down(), self.pos.left(), self.pos.right()]
        candidates = list(filter(lambda pos: pos.x >= 0 and pos.x < self._map.width and pos.y >= 0 and pos.y < self._map.height, candidates))
        for c in candidates:
            # print(c, " ", c.ed(self._map.goal))
            if self._map.get_mapobj(c) != Map.WALL and c not in self.closelist:
                self.openlist.append((c, self.pos, c.ed(self._map.goal)))
                self._map.set_mapobj(c, Map.TRIED)

    def pick_route_from_openlist(self):
        self.openlist.sort(key=lambda x: x[2])
        self.openlist.reverse()
        route = self.openlist.pop()
        self.closelist.append(route[0])
        return route

    def result(self):
        print(self._map)

class APlayer(Player):
    """
    A*
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap)
        self.g = {}
        self.g[str(self._map.start)] = 0

    def move(self, pos) -> None:
        # print("Move to ", pos)
        # if str(pos) not in self.g.keys() or self.g[str(pos)] > self.g[str(self.pos)] + 1:
        #     self.g[str(pos)] = self.g[str(self.pos)] + 1
        self.pos = pos
        self._map.set_mapobj(pos, Map.TRIED)

    def play(self) -> bool:
        while True:
            # print(self._map)
            if len(self.openlist) == 0:
                print("Failed")
                return False
            node = self.pick_route_from_openlist()
            # print("Wanna go ", node[0])
            if node[0] == self._map.goal:
                print("Success")
                return True
            self.move(node[0])
            self.update_openlist() # 子ノード展開
            # pprint(self.g)
            # time.sleep(0.5)

    def update_openlist(self):
        """
        動ける範囲を返す
        """
        # self.openlist = []
        candidates = [self.pos.up(), self.pos.down(), self.pos.left(), self.pos.right()]
        candidates = list(
            filter(lambda pos: pos.x >= 0 and pos.x < self._map.width and pos.y >= 0 and pos.y < self._map.height,
                   candidates))

        # gの更新
        for c in candidates:
            if str(c) not in self.g.keys() or self.g[str(c)] > self.g[str(self.pos)] + 1:
                self.g[str(c)] = self.g[str(self.pos)] + 1

        # 探索
        for c in candidates:
            # print(c, " ", c.ed(self._map.goal))
            if self._map.get_mapobj(c) != Map.WALL and c not in self.closelist:
                cnode = (c, self.pos, self.g[str(self.pos)] + c.ed(self._map.goal) + 1) # 追加候補ノード
                flag = False # スキップフラグ
                for n in self.openlist:
                    if n[0] == cnode[0]:
                        flag = True
                        if n[2] > cnode[2]: #n'がすでに存在かつ、候補ノードのほうがコスト低い場合
                            self.openlist.remove(n)
                            self._map.set_mapobj(n[0], Map.NONE)
                            self.openlist.append(cnode)
                            self._map.set_mapobj(cnode[0], Map.TRIED)
                            break
                if flag:
                    continue
                for n in self.closelist:
                    if n[0] == cnode[0]:
                        flag = True
                        if n[2] > cnode[2]:
                            self.closelist.remove(n)
                            self._map.set_mapobj(n[0], Map.NONE)
                            self.openlist.append(cnode)
                            self._map.set_mapobj(cnode[0], Map.TRIED)
                            break
                if flag:
                    continue
                self.openlist.append(cnode)
                self._map.set_mapobj(cnode[0], Map.TRIED)

    def pick_route_from_openlist(self):
        self.openlist.sort(key=lambda x: x[2])
        self.openlist.reverse()
        route = self.openlist.pop()
        self.closelist.append(route)
        # pprint([str(x[0]) for x in self.openlist])
        # print(len(self.openlist))
        # pprint([str(x[0]) for x in self.closelist])
        # print("Close list: ", len(self.closelist))
        return route

    def result(self):
        # print(self._map)
        shortest_path = self._result()
        mapobj = {}
        mapobj[Map.NONE] = "-"
        mapobj[Map.TRIED] = "*"
        mapobj[Map.ROUTE] = "+"
        mapobj[Map.WALL] = "■"
        mapobj[Map.START] = "S"
        mapobj[Map.GOAL] = "G"
        output = ""
        for y in range(self._map.height):
            for x in range(self._map.width):
                if self._map.start.x == x and self._map.start.y == y:
                    output += mapobj[Map.START] + " "
                    continue
                elif self._map.goal.x == x and self._map.goal.y == y:
                    output += mapobj[Map.GOAL] + " "
                    continue
                elif Pos(x, y) in shortest_path:
                    output += mapobj[Map.ROUTE] + " "
                    continue
                output += mapobj[self._map.get_mapobj(Pos(x,y))] + " "
            output += "\n"
        print(output)

    def _result(self):
        cpos = self._map.goal
        res = []
        res.append(cpos)
        while cpos != self._map.start:
            for x in self.closelist:
                if x[0] == cpos:
                    cpos = x[1]
                    res.append(cpos)
        return res

    # def _result(self):
    #     goalcost = self.g[str(self._map.goal)]
    #     gs = sorted(self.g.items(), key=itemgetter(1))
    #     gs.reverse()
    #     cpos = self._map.goal  # current position
    #     res = []
    #     res.append(cpos)
    #     for (k, g) in groupby(gs, key=itemgetter(1)):
    #         if k >= goalcost:
    #             continue
    #         # print("Checking key: ",k)
    #         ms = [cpos.up(), cpos.down(), cpos.left(), cpos.right()]
    #         ms = list(
    #             filter(lambda pos: pos.x >= 0 and pos.x < self._map.width and pos.y >= 0 and pos.y < self._map.height,
    #                    ms))
    #         # pprint(ms)
    #         for m in g:
    #             if m[0] in ms:
    #                 res.append(m[0])
    #                 cpos = m[0]
    #                 break
    #     return res


def get_map(w, h, spos, gpos):
    return MapField([[Map.NONE for x in range(w)] for y in range(h)], w, h, spos, gpos)

def part1():
    print("Loading Maps...")
    _map = get_map(13, 11, Pos(5, 9), Pos(5, 0))
    for i in range(3, 8):
        _map.set_mapobj(Pos(i, 2), Map.WALL)
    print("Loaded.")
    print(_map)

    print("====================================")

    print("[1] Trying Greedy...")
    p1 = GPlayer(copy.deepcopy(_map))
    start = time.time()
    p1.play()
    elapsed_time = time.time() - start
    p1.result()
    print("Elapsed time: %f [sec]" % elapsed_time)

    print("====================================")

    print("[2] Trying A*...")
    p2 = APlayer(copy.deepcopy(_map))
    start = time.time()
    p2.play()
    elapsed_time = time.time() - start
    p2.result()
    print("Elapsed time: %f [sec]" % elapsed_time)

def part2():
    print("Loading Maps...")
    _map = get_map(30, 30, Pos(0, 29), Pos(29, 0))
    for i in range(10, 25):
        _map.set_mapobj(Pos(i, 19), Map.WALL)
    for i in range(5, 25):
        _map.set_mapobj(Pos(10, i), Map.WALL)
    for i in range(1,11):
        _map.set_mapobj(Pos(i, 14), Map.WALL)
    print("Loaded.")
    print(_map)

    print("====================================")

    print("[1] Trying Greedy...")
    p1 = GPlayer(copy.deepcopy(_map))
    start = time.time()
    p1.play()
    elapsed_time = time.time() - start
    p1.result()
    print("Elapsed time: %f [sec]" % elapsed_time)

    print("====================================")

    print("[2] Trying A*...")
    p2 = APlayer(copy.deepcopy(_map))
    start = time.time()
    p2.play()
    elapsed_time = time.time() - start
    p2.result()
    print("Elapsed time: %f [sec]" % elapsed_time)

if __name__ == '__main__':
    # part1()
    part2()
