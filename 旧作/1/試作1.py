# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math
import sys


def main():
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

    while (1):
        # キーイベント処理(キャラクタ画像の移動)
        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_LEFT]:
            x_player -= 1
        if pressed_key[K_RIGHT]:
            x_player += 1
        if pressed_key[K_UP]:
            y_player -= 1
        if pressed_key[K_DOWN]:
            y_player += 1

        pygame.display.update()  # 画面更新
        pygame.time.wait(30)  # 更新時間間隔
        screen.fill((0, 20, 0, 0))  # 画面の背景色
        # playerを描画
        pygame.draw.circle(screen, (0, 200, 0), (int(x_player), int(y_player)), 15)
        # enemyを描画
        pygame.draw.rect(screen, (0, 200, 0), Rect(int(x_enemy), int(y_enemy), 15, 15))
        # 砲弾を描画
        x_cannon += dx
        y_cannon += dy
        pygame.draw.circle(screen, (0, 200, 0), (int(x_cannon), int(y_cannon)), 5)
        # イベント処理
        for event in pygame.event.get():
            # 画面の閉じるボタンを押したとき
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # キーを押したとき
            if event.type == KEYDOWN:
                # ESCキーなら終了
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            # マウスクリックで画像移動
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x_target, y_target = event.pos
                x_cannon = x_player
                y_cannon = y_player
                rad = math.atan2(x_target - x_player, y_target - y_player)
                dx = math.sin(rad) * 3
                dy = math.cos(rad) * 3

            # 終了用のイベント処理
            if event.type == QUIT:  # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:  # キーを押したとき
                if event.key == K_ESCAPE:  # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main()
