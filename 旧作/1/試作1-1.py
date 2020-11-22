# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys


def main():
    (w,h) = (640,400)   # 画面サイズ
    (x,y) = (w/2, h/2)
    pygame.init()       # pygame初期化
    pygame.display.set_mode((w, h), 0, 32)  # 画面設定
    screen = pygame.display.get_surface()
    player = pygame.image.load("player.jpg").convert_alpha()    # プレイヤー画像の取得
    (x, y) = (200, 200)
    while (1):
        pygame.display.update()             # 画面更新
        pygame.time.wait(30)                # 更新時間間隔
        screen.fill((0, 20, 0, 0))          # 画面の背景色
        screen.blit(player, (x, y))    # プレイヤー画像の描画

        for event in pygame.event.get():
            # マウスクリックで画像移動
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                x -= player.get_width() / 2
                y -= player.get_height() / 2
        # 終了用のイベント処理
            if event.type == QUIT:          # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:       # キーを押したとき
                if event.key == K_ESCAPE:   # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
        main()