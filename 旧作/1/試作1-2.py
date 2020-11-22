# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math
import sys

TankSize = 15
CannonSize = 5

(w, h) = (640, 400)  # 画面サイズ
(x_player, y_player) = (w / 4, h / 2)  # 戦車の位置
(x_enemy, y_enemy) = (w * 3 / 4, h / 2)  # 戦車の位置
(x_cannon, y_cannon) = (0, 0)  # 砲弾の位置
(x_target, y_target) = (0, 0)  # 目標位置
(dx, dy) = (0, 0)  # 砲弾の向き
pygame.init()  # pygame初期化
pygame.display.set_mode((w, h), 0, 32)  # 画面設定
screen = pygame.display.get_surface()
player = pygame.image.load("player.jpg").convert_alpha()  # プレイヤー画像の取得


# 戦車
class Tank:
    (x, y) = (0, 0)
    CannonList = []

    def __init__(self, x, y):
        self.x = x
        self.y = y


# 砲弾
class Cannon:
    (x, y) = (0, 0)
    (dx, dy) = (0, 0)

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy


def GetCannonAngle(x1, y1, x2, y2):
    return math.atan2(x1 - x2, y1 - y2)


def GetVelocity(r, v):
    return math.sin(r) * v, math.cos(r) * v


def CannonBehavior():
    return 0


# 初期化
player1 = Tank(w / 4, h / 2)
enemy1 = Tank(w * 3 / 4, h / 2)


while 1:
    # キーイベント処理(キャラクタ画像の移動)
    pressed_key = pygame.key.get_pressed()
    if pressed_key[K_LEFT]:
        x_player -= 2
    if pressed_key[K_RIGHT]:
        x_player += 2
    if pressed_key[K_UP]:
        y_player -= 2
    if pressed_key[K_DOWN]:
        y_player += 2

    pygame.display.update()  # 画面更新
    pygame.time.wait(30)  # 更新時間間隔
    screen.fill((0, 20, 0, 0))  # 画面の背景色
    # playerを描画
    pygame.draw.circle(screen, (0, 200, 0), (int(x_player), int(y_player)), TankSize)
    # enemyを描画
    pygame.draw.rect(screen, (0, 200, 0), Rect(int(x_enemy), int(y_enemy), TankSize, TankSize))
    # 砲弾の反射・当たり判定
    CannonBehavior()
    # 砲弾を描画
    x_cannon += dx
    y_cannon += dy
    pygame.draw.circle(screen, (0, 200, 0), (int(x_cannon), int(y_cannon)), CannonSize)

    # イベント処理
    for event in pygame.event.get():
        # マウスクリックで砲弾発射
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            x_target, y_target = event.pos
            x_cannon = x_player
            y_cannon = y_player
            rad = GetCannonAngle(x_target, y_target, x_player, y_player)
            dx, dy = GetVelocity(rad, 3)

        # 終了用のイベント処理
        if event.type == QUIT:  # 閉じるボタンが押されたとき
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # キーを押したとき
            if event.key == K_ESCAPE:  # Escキーが押されたとき
                pygame.quit()
                sys.exit()
