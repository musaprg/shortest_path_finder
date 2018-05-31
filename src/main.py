from enum import Enum
from pprint import pprint
from math import sqrt
import time
import copy


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
            print(self._map)
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
        # self.openlist = []
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

    def play(self) -> bool:
        while True:
            print(self._map)
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

    def update_openlist(self):
        """
        動ける範囲を返す
        """
        # self.openlist = []
        candidates = [self.pos.up(), self.pos.down(), self.pos.left(), self.pos.right()]
        candidates = list(
            filter(lambda pos: pos.x >= 0 and pos.x < self._map.width and pos.y >= 0 and pos.y < self._map.height,
                   candidates))
        for c in candidates:
            # print(c, " ", c.ed(self._map.goal))
            if self._map.get_mapobj(c) != Map.WALL and c not in self.closelist:
                cnode = (c, self.pos, self.g + c.ed(self._map.goal)) # 追加候補ノード
                flag = False # スキップフラグ
                for n in self.openlist:
                    if n[0] == cnode[0] and n[2] > cnode[2]: #n'がすでに存在かつ、候補ノードのほうがコスト低い場合
                        flag = True
                        self.openlist.remove(n)
                        self._map.set_mapobj(n[0], Map.NONE)
                        self.openlist.append(cnode)
                        self._map.set_mapobj(cnode, Map.TRIED)
                if flag:
                    continue
                self.openlist.append(cnode)
                self._map.set_mapobj(c, Map.TRIED)

    def pick_route_from_openlist(self):
        self.openlist.sort(key=lambda x: x[2])
        self.openlist.reverse()
        route = self.openlist.pop()
        self.closelist.append(route[0])
        return route

    def result(self):
        print(self._map)
        print(self.closelist)

def get_map(w, h, spos, gpos):
    return MapField([[Map.NONE for x in range(w)] for y in range(h)], w, h, spos, gpos)


if __name__ == '__main__':
    print("Loading Maps...")
    _map = get_map(13, 11, Pos(5,9), Pos(5,0))
    for i in range(3,8):
        _map.set_mapobj(Pos(i, 2), Map.WALL)
    print("Loaded.")
    print(_map)

    # print("====================================")
    #
    # print("[1] Trying Greedy...")
    # p1 = GPlayer(copy.deepcopy(_map))
    # start = time.time()
    # p1.play()
    # elapsed_time = time.time() - start
    # p1.result()
    # print("Elapsed time: %f [sec]" % elapsed_time)

    print("====================================")

    print("[2] Trying A*...")
    p2 = APlayer(copy.deepcopy(_map))
    start = time.time()
    p2.play()
    elapsed_time = time.time() - start
    p2.result()
    print("Elapsed time: %f [sec]" % elapsed_time)
