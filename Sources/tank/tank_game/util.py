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
