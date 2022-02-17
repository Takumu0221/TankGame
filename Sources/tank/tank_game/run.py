# -*- coding: utf-8 -*-
import random
import sys
import time

import pygame
from pygame.locals import *


def main():
    # 終了フラグ
    FinishFlag = False
    TimeFlag = True

    # 戦車の準備
    global y_target, x_target
    Player("../../images/tank_0.png", - w / 4, h / 2, 1.0)

    for i in range(1, Enemy_num + 1):  # 敵戦車（手動）
        Enemy_Manual("../../images/tank_1.png", w * 5 / 6 + random.random() * 10,
                     h * i / (Enemy_num + 1) + random.random() * 10, 1, 0, 0, time.time(), i - 1)
        Enemy_pos_manual[2 * (i - 1)] = w * 3 / 4
        Enemy_pos_manual[2 * (i - 1) + 1] = h * i / (Enemy_num + 1)

    for i in range(1, Enemy_num + 1):  # 敵戦車（強化学習）
        Enemy_Learn("../../images/tank_0.png", w * 1 / 6 - random.random() * 10
                    , h * i / (Enemy_num + 1) - random.random() * 10, 1, 0, 0, time.time(), i - 1)
        Enemy_pos_learn[2 * (i - 1)] = w * 3 / 4
        Enemy_pos_learn[2 * (i - 1) + 1] = h * i / (Enemy_num + 1)

    # オブジェクト生成
    Map.images[0] = load_img("../../images/tile.png")  # 地面
    Map.images[1] = load_img("../../images/wall.png")  # 壁
    m = Map()
    MakeWalls(m)  # 壁を生成
    # MakeFalseImage()  # 虚像オブジェクトの生成

    global distance_matrix  # 経路的な距離行列
    distance_matrix = MakeDistanceMatrix()  # 距離行列の作成

    # 敵戦車のウェイトを表示
    """print('Weight of Allies Distance:')
    print(AD)
    print('Weight of Enemy  Distance:')
    print(ED)
    print('Weight of Walls  Distance:')
    print(WD)
    print('Weight of Avoiding Cannon:')
    print(AC)
    print('Comfortable Distance:')
    print(GD)
    print('Repulsive Force Distance')
    print(RFD)"""

    # 準備画面
    screen.blit(text_ready, (w / 3, h / 4))
    screen.blit(text_click, (w / 3 + 20, h / 3 + 30))
    screen.blit(text_move, (w / 4 + 10, 3 * h / 4))
    pygame.display.update()

    # スタート画面でキー入力を待機
    DrawTiles(m)
    all_object.draw(screen)  # すべて描写
    img_start = pygame.image.load("../../images/Start_menu.png")
    screen.blit(img_start, (100, 100))
    font_start = pygame.font.SysFont("None", 30)
    text_start = font_start.render("User Guide", True, (255, 255, 255))
    img_how = pygame.image.load("../../images/how_con.png")
    screen.blit(img_how, (200, 400))
    screen.blit(text_start, (200, 360))
    font_start = pygame.font.SysFont("None", 50)
    text_start1 = font_start.render("1: Level 1", True, (255, 255, 255))
    text_start2 = font_start.render("2: Level 2", True, (255, 255, 255))
    text_start3 = font_start.render("3: Level 3", True, (255, 255, 255))
    screen.blit(text_start1, (450, 360))
    screen.blit(text_start2, (450, 400))
    screen.blit(text_start3, (450, 440))
    pygame.display.update()  # 描画処理を実行

    ReadyFlag = True

    # レベル設定(最強:3, 協調抜き:2, ベーシック:1)
    global Level
    Level = 1
    while ReadyFlag:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed_key = pygame.key.get_pressed()
                if pressed_key[pygame.K_0]:
                    Level = 0
                    ReadyFlag = False
                if pressed_key[pygame.K_1]:
                    Level = 1
                    ReadyFlag = False
                if pressed_key[pygame.K_2]:
                    Level = 2
                    ReadyFlag = False
                if pressed_key[pygame.K_3]:
                    Level = 3
                    ReadyFlag = False

            # 終了用のイベント処理
            if event.type == QUIT:  # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:  # キーを押したとき
                if event.key == K_ESCAPE:  # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()

    pygame.time.wait(300)

    # レベルに応じたWeightの変更
    global AD_level  # 味方との距離の重視度合い(AIDistance)
    global ED_level  # 敵との距離の重視度合い(EnemyDistance)
    global WD_level  # 壁との距離の重視度合い(WallsDistance)

    if Level == 3:
        AD_level = 1
        ED_level = 6
        WD_level = 7
    elif Level == 2:
        AD_level = 0
        ED_level = 6
        WD_level = 7
    else:
        AD_level = 0
        ED_level = 0
        WD_level = 0

    start = pygame.time.get_ticks()  # 開始時間を記録

    while 1:
        pygame.time.wait(10)  # 更新時間間隔

        # 終了フラグが立ってないときに更新
        if not FinishFlag:
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            all_object.update()  # すべて更新
            # false_image.draw(screen)
            # print(player, enemies, cannons, walls)

        # 敵(learn)がいなくなったとき
        if not all_object.has(enemies_learn):
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            enemies_manual.update()
            screen.blit(text2, (w / 4, h / 4))
            FinishFlag = True

        # 敵(manual)がいなくなったとき
        if not all_object.has(enemies_manual):
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            player.sprite.DrawGun()
            screen.blit(text1, (0, h / 4))
            FinishFlag = True

        # if FinishFlag and TimeFlag:
        #     finish = pygame.time.get_ticks()
        #     dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        #     with open("{}.txt".format(dt), 'w') as f:
        #         print((finish - start) / 1000, file=f)
        #     TimeFlag = False

        pygame.display.update()  # 画面更新

        # イベント処理
        for event in pygame.event.get():
            # 終了フラグが立ってるときはクリックで終了
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if FinishFlag:
                    pygame.quit()
                    sys.exit()
                else:
                    x_target, y_target = event.pos
                    player.sprite.Shot()

            # 終了用のイベント処理
            if event.type == QUIT:  # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:  # キーを押したとき
                if event.key == K_ESCAPE:  # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()


if __name__ == '__main__':
    main()
