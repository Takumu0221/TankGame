# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math
import sys

TankSize = 20  # 戦車サイズ
CannonSize = 5   # 砲弾サイズ
CannonNum = 5    # 砲弾数

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

    def __init__(self, x, y):
        self.x = x  # x座標
        self.y = y  # y座標


# 砲弾
class Cannon:
    bounds = 0  # 反射回数

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
    # 戦車との判定
    if GetDistance(c.x, c.y, player.x, player.y) < TankSize + CannonSize:  # プレイヤーと衝突
        return 0
    for e in enemies:
        if GetDistance(c.x, c.y, e.x, e.y) < TankSize + CannonSize:  # 敵と衝突
            return 1
    # 壁との判定
    if c.x + CannonSize >= w or c.x - CannonSize <= 0:  # x方向の壁
        return 2
    if c.y + CannonSize >= h or c.y - CannonSize <= 0:  # y方向の壁
        return 3

    return 0


# 砲弾の振る舞いの管理
def CannonBehavior(tank):
    c_list = tank.CannonList
    i = 0
    while len(c_list) > i >= 0:
        # 当たり判定
        result = DetectCollision(c_list[i])
        # print(result)      #デバッグ用
        # 戦車と衝突
        if result == 1:
            c_list.pop(i)
            i -= 1
            continue
        elif result > 0:
            # 2回目の反射なら消滅
            c_list[i].bounds += 1
            if c_list[i].bounds > 1:
                c_list.pop(i)
                i -= 1
                continue
            # x方向の反射
            if result == 2:
                c_list[i].dx *= -1
            # y方向の反射
            if result == 3:
                c_list[i].dy *= -1

        # 速度を座標に加算
        c_list[i].x += c_list[i].dx
        c_list[i].y += c_list[i].dy
        i += 1
        
    return c_list


# 戦車の準備
player = Tank(w / 4, h / 2)
enemies = [Tank(w * 3 / 4, h / 3), Tank(w * 3 / 4, h * 2 / 3)]

while 1:
    # キーイベント処理(キャラクタ画像の移動)
    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_LEFT]:
        player.x -= 2
    if pressed_key[K_RIGHT]:
        player.x += 2
    if pressed_key[K_UP]:
        player.y -= 2
    if pressed_key[K_DOWN]:
        player.y += 2

    pygame.time.wait(10)  # 更新時間間隔
    # screen.fill((0, 0, 0, 0))  # 画面の背景色

    # playerを描画
    pygame.draw.circle(screen, (0, 200, 0), (int(player.x), int(player.y)), TankSize)
    # enemyを描画
    for enemy in enemies:
        pygame.draw.circle(screen, (0, 0, 200), (int(enemy.x), int(enemy.y)), TankSize)
    # 砲弾を描画
    for cannon in player.CannonList:
        # print(cannon.x,cannon.y)   #デバッグ用
        pygame.draw.circle(screen, (200, 0, 0), (int(cannon.x), int(cannon.y)), CannonSize) 
     
    # 砲弾の反射・当たり判定
    player.CannonList = CannonBehavior(player)
    
    pygame.display.update()  # 画面更新

    # イベント処理
    for event in pygame.event.get():
        # マウスクリックで砲弾発射
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            x_target, y_target = event.pos
            # 砲弾の角度を求める
            rad = GetCannonAngle(x_target, y_target, player.x, player.y)
            dx, dy = GetVelocity(rad, 5)
            # 戦車に追加
            if len(player.CannonList) <= CannonNum-1:   # フィールド上には最大5発
                player.CannonList.append(Cannon(player.x, player.y, dx, dy))

        # 終了用のイベント処理
        if event.type == QUIT:  # 閉じるボタンが押されたとき
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # キーを押したとき
            if event.key == K_ESCAPE:  # Escキーが押されたとき
                pygame.quit()
                sys.exit()
