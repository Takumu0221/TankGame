import itertools
import math

import numpy as np
import pygame
from pygame.locals import *
from scipy.sparse.csgraph import shortest_path


# 画像の読み込み
def load_img(filename, colorkey=None):
    img = pygame.image.load(filename)
    img = img.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey, RLEACCEL)
    return img


############### 行列を計算して速度を得る ################
def GetSpeed(List):
    result = [0.0, 0.0]
    for i in List:
        result[0] += i[0] * i[1]
        result[1] += i[0] * i[2]
    dev = math.sqrt(result[0] ** 2 + result[1] ** 2)
    # しきい値を設定
    if dev < 0.6:
        result[0] = 0
        result[1] = 0
    else:
        result[0] = result[0] / dev  # 正規化
        result[1] = result[1] / dev  # 正規化

    # 最終的な移動方向決定
    # 単位円を考えたときにそのx，y方向を1とするか0とするか
    if abs(result[0]) >= math.cos(3 * math.pi / 8):
        result[0] = int(math.copysign(1, result[0]))  # copysign(大きさ、符号)
    else:
        result[0] = 0

    if abs(result[1]) >= math.sin(math.pi / 8):
        result[1] = int(math.copysign(1, result[1]))
    else:
        result[1] = 0
    return result[0], result[1]


# 砲弾の角度を得る（1：対象物　2：発射点）
def GetCannonAngle(x1, y1, x2, y2):
    return math.atan2(y1 - y2, x1 - x2)


# 2点間の距離を求める
def GetDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 角度から縦・横方向成分を求める
def GetVelocity(r, v):
    return math.cos(r) * math.sqrt(v), math.sin(r) * math.sqrt(v)


# 2点間の経路的な距離を求める
def GetPathDistance(P0, P1):
    # 与えられた座標がどのブロックに該当するかを計算
    P0_block = [int(x / Map.m_size) for x in P0]
    P1_block = [int(x / Map.m_size) for x in P1]

    # distance_matrixを用いて経路長を計算（参照する）
    map_shape = np.array(Map.map).shape
    distance_block = distance_matrix[map_shape[1] * P0_block[1] + P0_block[0]][
        map_shape[1] * P1_block[1] + P1_block[0]]

    # 経路長（ブロック数×40）と（できれば）ブロックの中心からの距離を足して返す
    distance = distance_block * Map.m_size + \
               GetDistance(P0[0], P0[1], (P0_block[0] + 0.5) * Map.m_size, (P0_block[1] + 0.5) * Map.m_size) + \
               GetDistance(P1[0], P1[1], (P1_block[0] + 0.5) * Map.m_size, (P1_block[1] + 0.5) * Map.m_size)

    return distance


# 線分の交点を求める
def line_cross_point(P0, P1, Q0, Q1):
    x0, y0 = P0
    x1, y1 = P1
    x2, y2 = Q0
    x3, y3 = Q1
    a0 = x1 - x0
    b0 = y1 - y0
    a2 = x3 - x2
    b2 = y3 - y2

    d = a0 * b2 - a2 * b0
    if d == 0:
        # two lines are parallel
        return None

    sn = b2 * (x2 - x0) - a2 * (y2 - y0)
    s = sn / d
    tn = b0 * (x2 - x0) - a0 * (y2 - y0)
    t = tn / d

    if 0 <= s <= 1 and 0 <= t <= 1:
        return [x0 + a0 * sn / d, y0 + b0 * sn / d]
    else:
        return None


# ある軸において対称な点を返す
def GetLineSymmetricPoint(P, axis_x, axis_y):
    if axis_x is not None:  # x軸
        return [2 * axis_x - P[0], P[1]]
    elif axis_y is not None:  # y軸
        return [P[0], 2 * axis_y - P[1]]


# 残り敵数を返す関数
def Aliving(enemies):
    enemy_alive = 0
    for e in enemies.sprites():
        if e.alive():
            enemy_alive += 1
    return enemy_alive


# 壁を配置
def MakeWalls(m):
    for i in range(m.row):
        for j in range(m.col):
            if m.map[i][j] > 0:
                if m.map[i][j] == 1 and 0 < i < m.row - 1 and 0 < j < m.col - 1:
                    InnerWall("../../images/wall.png", j * m.m_size, i * m.m_size)
                else:
                    if m.map[i][j] == 2:
                        OuterWall("../../images/wall(W).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 3:
                        OuterWall("../../images/wall(W-T).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 4:
                        OuterWall("../../images/wall(W-S).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 5:
                        OuterWall("../../images/wall(H).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 6:
                        OuterWall("../../images/wall(H-T).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 7:
                        OuterWall("../../images/wall(L-U).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 8:
                        OuterWall("../../images/wall(R-U).png", j * m.m_size, i * m.m_size)
                    elif m.map[i][j] == 9:
                        OuterWall("../../images/wall(L-D).png", j * m.m_size, i * m.m_size)


# worldのコピー
def CopyWorld():
    objects = pygame.sprite.Group()  # 新しいworld
    # new_object = 0  # 新しく生成したオブジェクト

    # オブジェクトを一つ一つコピー
    for o in all_object:
        if type(o) is Player:
            Player.containers = all_object
            new_object = Player("../../images/tank_0.png", o.x, o.y, o.v)
            Player.containers = all_object, player
        elif type(o) is Enemy_Manual:
            new_object = Enemy_Manual("../../images/tank_1.png", o.x, o.y, o.v, o.dx, o.dy, o.firetime, 0)
        elif type(o) is InnerWall:
            new_object = InnerWall(o.filename, o.x, o.y)
        elif type(o) is OuterWall:
            new_object = OuterWall(o.filename, o.x, o.y)
        else:
            new_object = Cannon("../../images/cannon.png", o.x, o.y, o.v, o.dx, o.dy)

        if new_object:
            new_object.kill()
        objects.add(new_object)

    return objects


# ウェイトを更新する関数
def UpdateWeight(enemies):
    Remaining = max(5 * Aliving(enemies) - sum([len(x.CannonList) for x in enemies.sprites()]), 0)
    global AD  # 味方との距離の重視度合い(AIDistance)
    global ED  # 敵との距離の重視度合い(EnemyDistance)
    global WD  # 壁との距離の重視度合い(WallsDistance)
    global AC  # 弾丸回避の重要度合い(AvoidingCannon)
    global GD  # プレイヤー戦車と敵戦車の心地よい距離(GoodDistance)
    global RFD  # 斥力が働き合う距離(RepulsiveForceDistance)

    global AD_level  # 味方との距離の重視度合い(AIDistance)
    global ED_level  # 敵との距離の重視度合い(EnemyDistance)
    global WD_level  # 壁との距離の重視度合い(WallsDistance)

    AD = AD_level * Enemy_num
    # ED = max(0, ED_level * Aliving(enemies) - Remaining)
    ED = 4
    # WD = max(0, WD_level * Enemy_num - Remaining)
    WD = 5
    AC = 7
    # GD = GD_origin * (1 - ((5 * Aliving(enemies) - Remaining) / (10 * Aliving(enemies))))
    GD = GD_origin
    # RFD = RFD_origin * (1 - ((5 * Aliving(enemies) - Remaining) / (10 * Aliving(enemies))))
    RFD = RFD_origin


# 床の描画
def DrawTiles(m):
    for i in range(m.row):
        for j in range(m.col):
            screen.blit(m.images[0], (j * m.m_size, i * m.m_size))


# 虚像オブジェクトの配置
def MakeFalseImage():
    borders = [40, w - 40, 40, h - 40]  # 左，右，上，下の境界

    for o in all_object.sprites():
        if not type(o) is OuterWall:
            for i in range(len(borders)):
                (x, y) = o.x, o.y

                if i == 0 or i == 1:  # x方向の対称移動
                    x = 2 * borders[i] - o.rect.centerx - o.rect.width * 0.5
                else:  # y方向の対称移動
                    y = 2 * borders[i] - o.rect.centery - o.rect.height * 0.5

                # オブジェクトごとに虚像を作成
                if type(o) is Player:
                    Player.containers = all_object
                    new_object = Player("../../images/tank_0.png", x, y, o.v)
                    Player.containers = all_object, player
                    new_object.kill()
                elif type(o) is Enemy_Manual:
                    new_object = Enemy_Manual("../../images/tank_1.png", x, y, o.v, o.dx, o.dy, o.firetime, 0)
                    new_object.kill()
                else:
                    new_object = InnerWall(o.filename, x, y)
                    all_object.remove(new_object)

                # グループを整理
                false_image.add(new_object)


# 虚像オブジェクトの更新
def UpdateFalseImage():
    player_tanks = []
    enemy_tanks = []

    # 戦車の虚像を取得
    for o in false_image:
        if type(o) is Player:
            player_tanks.append(o)
        if type(o) is Enemy_Manual:
            enemy_tanks.append(o)

    # 位置を更新
    borders = [40, w - 40, 40, h - 40]  # 左，右，上，下の境界

    for i in range(len(borders)):  # プレイヤー
        if i == 0 or i == 1:  # x方向の対称移動
            player_tanks[i].rect.x = 2 * borders[i] - player.sprite.rect.centerx - player_tanks[1].rect.width * 0.5
            player_tanks[i].rect.y = player.sprite.rect.y
        else:  # y方向の対称移動
            player_tanks[i].rect.x = player.sprite.rect.x
            player_tanks[i].rect.y = 2 * borders[i] - player.sprite.rect.centery - player_tanks[1].rect.height * 0.5

    enemy_list = enemies_manual.sprites()
    for e in range(len(enemy_list)):
        for i in range(len(borders)):  # 敵
            if i == 0 or i == 1:  # x方向の対称移動
                enemy_tanks[e * 4 + i].rect.x = 2 * borders[i] - enemy_list[e].rect.centerx - enemy_tanks[
                    i].rect.width * 0.5
                enemy_tanks[e * 4 + i].rect.y = enemy_list[e].rect.y
            else:  # y方向の対称移動
                enemy_tanks[e * 4 + i].rect.x = enemy_list[e].rect.x
                enemy_tanks[e * 4 + i].rect.y = 2 * borders[i] - enemy_list[e].rect.centery - enemy_tanks[
                    1].rect.height * 0.5


# 経路的な距離行列の作成
def MakeDistanceMatrix():
    m = Map.map  # マップデータ

    map_size = np.array(m).size  # マップサイズ（ブロック数）
    map_shape = np.array(m).shape  # マップの形（ブロック数）

    adjacent = [[0 for _ in range(map_size)] for _ in range(map_size)]  # 隣接行列

    for i, xy in enumerate(itertools.product(range(map_shape[0]), range(map_shape[1]))):
        x, y = xy
        for delta in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nx = x + delta[0]
            ny = y + delta[1]
            if 0 <= nx < map_shape[0] and 0 <= ny < map_shape[1]:  # 隣接ブロックがマップ外でないとき
                if m[x][y] == 0 and m[nx][ny] == 0:  # 隣接ブロックが壁でないとき
                    adjacent[map_shape[1] * x + y][map_shape[1] * nx + ny] = 1

    # print("size " + str(np.array(shortest_path(np.array(adjacent))).shape))
    return shortest_path(np.array(adjacent))


# 敵戦車の位置を記録するリストの初期化(死んだ戦車の管理のため)
def Enemy_pos_res():
    global Enemy_pos_manual
    global Enemy_pos_learn
    for i in range(Enemy_num):  # 初期化
        Enemy_pos_manual[2 * i] = 0
        Enemy_pos_manual[2 * i + 1] = 0
        Enemy_pos_learn[2 * i] = 0
        Enemy_pos_learn[2 * i + 1] = 0