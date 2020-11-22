# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math
import sys

import time
import random

TankSize = 20  # 戦車サイズ
CannonSize = 5  # 砲弾サイズ
CannonNum = 5  # 砲弾数

(w, h) = (960, 720)  # 画面サイズ
(x_target, y_target) = (0, 0)  # 目標位置

pygame.init()  # pygame初期化
pygame.display.set_mode((w, h), 0, 32)  # 画面設定
pygame.display.set_caption("TANK GAME")
screen = pygame.display.get_surface()


# player = pygame.image.load("player.jpg").convert_alpha()  # プレイヤー画像の取得


# 戦車
class Tank:
    CannonList = []  # 砲弾のリスト
    size = TankSize  # 大きさ

    def __init__(self, x, y):
        self.x = x  # x座標
        self.y = y  # y座標


# 敵戦車 速度が欲しかったため
class Enemy:
    CannonList = []  # 砲弾のリスト
    size = TankSize  # 大きさ

    def __init__(self, x, y, dx, dy, firetime):
        self.x = x  # x座標
        self.y = y  # y座標
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.firetime = firetime  # 前回発射時間


# 砲弾
class Cannon:
    bounds = 0  # 反射回数
    size = CannonSize  # 大きさ

    def __init__(self, x, y, dx, dy):
        self.x = x  # x座標
        self.y = y  # y座標
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度


# 砲弾の角度を得る
def GetCannonAngle(x1, y1, x2, y2):
    return math.atan2(x1 - x2, y1 - y2)


# 2点間の距離を求める
def GetDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 角度から縦・横方向成分を求める
def GetVelocity(r, v):
    return math.sin(r) * v, math.cos(r) * v


# 当たり判定
def DetectCollision(c):
    result = [[0, 0, 0, 0], [0]]
    # 壁との判定
    if c.x + c.size >= w:  # 東方向の壁
        result[0][0] = 1
    if c.x - c.size <= 0:  # 西方向の壁
        result[0][1] = 1
    if c.y + c.size >= h:  # 南方向の壁
        result[0][2] = 1
    if c.y - c.size <= 0:  # 北方向の壁
        result[0][3] = 1

    # 戦車との判定
    if GetDistance(c.x, c.y, player.x, player.y) < TankSize + c.size:  # プレイヤーと衝突
        result[1] = -1
    for e in enemies:
        if GetDistance(c.x, c.y, e.x, e.y) < TankSize + c.size:  # 敵と衝突
            result[1] = 1

    return result


# 砲弾の振る舞いの管理
def CannonBehavior(tank):
    c_list = tank.CannonList
    i = 0
    while len(c_list) > i >= 0:
        # 当たり判定
        result = DetectCollision(c_list[i])
        # print(result)      #デバッグ用

        # 敵の弾かどうかの判定
        if type(tank) == Enemy:
            if result[1] == -1:
                result[1] = 1
            elif result[1] == 1:
                result[1] = 0

        # 戦車と衝突
        if result[1] == 1:
            c_list.pop(i)
            i -= 1
            continue
        elif sum(result[0]) > 0:
            # 2回目の反射なら消滅
            c_list[i].bounds += 1
            if c_list[i].bounds > 1:
                c_list.pop(i)
                i -= 1
                continue
            # x方向の反射
            if result[0][0] + result[0][1] > 0:
                c_list[i].dx *= -1
            # y方向の反射
            if result[0][2] + result[0][3] > 0:
                c_list[i].dy *= -1

        # 速度を座標に加算
        c_list[i].x += c_list[i].dx
        c_list[i].y += c_list[i].dy
        i += 1

    return c_list


# 敵戦車の挙動
def EnemyBehavior(enemy):
    # 砲弾を描画
    for c_e in enemy.CannonList:
        pygame.draw.circle(screen, (0, 200, 0), (int(c_e.x), int(c_e.y)), CannonSize)

    # 戦車の移動
    enemy = EnemyMove(enemy)

    # 約3秒毎に行動
    if time.time() - enemy.firetime >= 3:  # 経過時間計算
        # 時間保存
        enemy.firetime = time.time()

        # 2，0，－2のどれかを得る
        enemy.dx = ((int(random.random() * 1000) % 3) - 1) * 2
        enemy.dy = ((int(random.random() * 1000) % 3) - 1) * 2

        # マウスクリック時と同様
        # プレイヤーへ向かって撃つ
        rad = GetCannonAngle(player.x, player.y, enemy.x, enemy.y)
        dx, dy = GetVelocity(rad, 3)
        if len(enemy.CannonList) <= CannonNum - 1:  # フィールド上には最大5発
            enemy.CannonList.append(Cannon(enemy.x, enemy.y, dx, dy))


# 自戦車の移動
def PlayerMove():
    result = DetectCollision(player)
    PlayerSpeed = 2

    # キーイベント処理(キャラクタ画像の移動)
    pressed_key = pygame.key.get_pressed()
    if result[0][0] == 0:
        if pressed_key[K_RIGHT]:
            player.x += PlayerSpeed
    if result[0][1] == 0:
        if pressed_key[K_LEFT]:
            player.x -= PlayerSpeed
    if result[0][2] == 0:
        if pressed_key[K_DOWN]:
            player.y += PlayerSpeed
    if result[0][3] == 0:
        if pressed_key[K_UP]:
            player.y -= PlayerSpeed


# 敵戦車の移動
def EnemyMove(e):
    result = DetectCollision(e)

    # 壁や戦車との当たり判定
    if result[0][0] > 0 and e.dx > 0 or result[0][1] > 0 and e.dx < 0:
        e.dx = 0
    if result[0][2] > 0 and e.dy > 0 or result[0][3] > 0 and e.dy < 0:
        e.dy = 0

    # 速度を加算
    e.x += e.dx
    e.y += e.dy

    return e


# 戦車の準備
player = Tank(w / 4, h / 2)

enemies = [Enemy(w * 3 / 4, h / 3, 0, 0, time.time()), Enemy(w * 3 / 4, h * 2 / 3, 0, 0, time.time())]

while 1:
    PlayerMove()  # 自戦車の移動

    pygame.time.wait(10)  # 更新時間間隔
    screen.fill((0, 0, 0, 0))  # 画面の背景色

    # playerを描画
    pygame.draw.circle(screen, (0, 200, 0), (int(player.x), int(player.y)), TankSize)
    # enemyを描画
    for enemy in enemies:
        pygame.draw.circle(screen, (0, 0, 200), (int(enemy.x), int(enemy.y)), TankSize)
    # 砲弾を描画
    for cannon in player.CannonList:
        # print(cannon.x,cannon.y)   #デバッグ用
        pygame.draw.circle(screen, (200, 0, 0), (int(cannon.x), int(cannon.y)), CannonSize)

    # 敵の挙動
    for enemy in enemies:
        EnemyBehavior(enemy)

    # 砲弾の反射・当たり判定
    player.CannonList = CannonBehavior(player)
    enemies[0].CannonList = CannonBehavior(enemies[0])

    pygame.display.update()  # 画面更新

    # イベント処理
    for event in pygame.event.get():
        # マウスクリックで砲弾発射
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            x_target, y_target = event.pos
            # 砲弾の角度を求める
            rad = GetCannonAngle(x_target, y_target, player.x, player.y)
            dx, dy = GetVelocity(rad, 3)
            # 戦車に追加
            if len(player.CannonList) <= CannonNum - 1:  # フィールド上には最大5発
                player.CannonList.append(Cannon(player.x, player.y, dx, dy))

        # 終了用のイベント処理
        if event.type == QUIT:  # 閉じるボタンが押されたとき
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # キーを押したとき
            if event.key == K_ESCAPE:  # Escキーが押されたとき
                pygame.quit()
                sys.exit()
