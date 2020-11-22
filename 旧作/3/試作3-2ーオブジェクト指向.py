# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import math
import sys

import time
import random

(w, h) = (640, 480)  # 画面サイズ

(x_target, y_target) = (0, 0)  # 目標位置

# player = pygame.image.load("player.jpg").convert_alpha()  # プレイヤー画像の取得


# マップ
class Map:
    # マップデータ
    map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    row, col = len(map), len(map[0])  # マップの行数,列数を取得
    images = [None] * 256  # マップチップ
    m_size = 40  # 1マスの画像サイズ


# 壁オブジェクト
class Wall(pygame.sprite.Sprite):
    # 初期化
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.containers = None
        self.image = img
        self.x = x
        self.y = y
        width = self.image.get_width()  # 横幅
        height = self.image.get_height()  # 縦幅
        self.rect = Rect(x, y, width, height)  # 四角形の宣言

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# 移動オブジェクト
class MovingObject(pygame.sprite.Sprite):
    # 初期化
    def __init__(self, filename, x, y, v):  # イメージファイル名・x座標・y座標・速さ
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.containers = None
        self.image = load_img(filename)
        self.x = x  # x座標　（小数点以下まで含む）
        self.y = y  # y座標　（小数点以下まで含む）
        width = self.image.get_width()  # 横幅
        height = self.image.get_height()  # 縦幅
        self.rect = Rect(x, y, width, height)  # 四角形の宣言
        self.v = v

    # 描画
    def draw(self, Screen):
        Screen.blit(self.image, self.rect)

    # 当たり判定
    def DetectCollision(self):
        result = [0, [0, 0, 0, 0], [0, 0, 0, 0]]

        for object_collied in pygame.sprite.spritecollide(self, all_object, False):
            # 対象との各座標の差
            difference = [(object_collied.x + 0.5 * object_collied.rect.width) - (self.x + 0.5 * self.rect.width),
                          (object_collied.y + 0.5 * object_collied.rect.height) - (self.y + 0.5 * self.rect.height)]

            if self != object_collied:  # 自分自身と異なるとき
                # 砲弾との判定
                if type(object_collied) is Cannon:
                    object_collied.kill()
                    result[0] = 1

                # 戦車との判定
                if type(object_collied) is Tank:
                    # 衝突判定の閾値
                    threshold = [0.5 * (object_collied.rect.width + self.rect.width) - (object_collied.v + self.v),
                                 0.5 * (object_collied.rect.height + self.rect.height) - (object_collied.v + self.v)]

                    if difference[0] >= threshold[0]:  # 東方向
                        self.x = object_collied.x - self.rect.width  # 位置補正
                        result[1][0] = 1
                    if difference[0] <= -threshold[0]:  # 西方向
                        self.x = object_collied.x + object_collied.rect.width  # 位置補正
                        result[1][1] = 1
                    if difference[1] >= threshold[1]:  # 南方向
                        self.y = object_collied.y - self.rect.height  # 位置補正
                        result[1][2] = 1
                    if difference[1] <= -threshold[1]:  # 北方向
                        self.y = object_collied.y + object_collied.rect.height  # 位置補正
                        result[1][3] = 1

                # 壁との判定
                if type(object_collied) is Wall:
                    # 衝突判定の閾値
                    threshold = [0.5 * (object_collied.rect.width + self.rect.width) - self.v - 1,
                                 0.5 * (object_collied.rect.height + self.rect.height) - self.v - 1]

                    if difference[0] >= threshold[0]:  # 東方向の壁
                        self.x = object_collied.x - self.rect.width  # 位置補正
                        result[2][0] = 1
                    if difference[0] <= -threshold[0]:  # 西方向の壁
                        self.x = object_collied.x + object_collied.rect.width  # 位置補正
                        result[2][1] = 1
                    if difference[1] >= threshold[1]:  # 南方向の壁
                        self.y = object_collied.y - self.rect.height  # 位置補正
                        result[2][2] = 1
                    if difference[1] <= -threshold[1]:  # 北方向の壁
                        self.y = object_collied.y + object_collied.rect.height  # 位置補正
                        result[2][3] = 1

        return result


# 戦車
class Tank(MovingObject):
    CannonNum = 5  # 砲弾数
    CannonSpeed = 2.0  # 砲弾速度

    def __init__(self, filename, x, y, v):
        super().__init__(filename, x, y, v)
        self.CannonList = []  # 砲弾のリスト

    def update(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()

        # キーイベント処理(キャラクタ画像の移動)
        pressed_key = pygame.key.get_pressed()
        if result[1][0] == 0 and result[2][0] == 0:
            if pressed_key[K_RIGHT]:
                self.x += self.v
        if result[1][1] == 0 and result[2][1] == 0:
            if pressed_key[K_LEFT]:
                self.x -= self.v
        if result[1][2] == 0 and result[2][2] == 0:
            if pressed_key[K_DOWN]:
                self.y += self.v
        if result[1][3] == 0 and result[2][3] == 0:
            if pressed_key[K_UP]:
                self.y -= self.v

        # 砲弾の整理
        self.AdjustCannonList()
        # 座標の更新
        self.rect.x = self.x
        self.rect.y = self.y

    def Shot(self):
        # マウスクリックで砲弾発射
        # 砲弾の角度を求める
        rad = GetCannonAngle(x_target, y_target, self.x, self.y)
        dx, dy = GetVelocity(rad, self.CannonSpeed)
        # 戦車に追加
        if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
            self.CannonList.append(Cannon("cannon.png", self.x + self.rect.width + 5, self.y, self.CannonSpeed, dx, dy))

    # KILLされた砲弾を整理
    def AdjustCannonList(self):
        new_list = []
        for cannon in self.CannonList:
            if cannon.alive():  # 砲弾が崩壊していなければリストに追加
                new_list.append(cannon)

        self.CannonList = new_list


# 敵戦車
class Enemy(Tank):
    CannonSpeed = 2.0

    def __init__(self, filename, x, y, v, dx, dy, firetime):
        super().__init__(filename, x, y, v)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.firetime = firetime  # 前回発射時間

    def update(self):
        self.Move()  # 戦車の移動

        # 座標の更新
        self.rect.x = self.x
        self.rect.y = self.y

        # 約3秒毎に行動
        if time.time() - self.firetime >= 3:  # 経過時間計算
            # 時間保存
            self.firetime = time.time()

            # 1，0，－1のどれかを得る
            self.dx = ((int(random.random() * 1000) % 3) - 1) * 1
            self.dy = ((int(random.random() * 1000) % 3) - 1) * 1
            self.v = self.dx ** 2 + self.dy ** 2

            # 砲弾の発射
            self.Shot()
            # 砲弾の整理
            self.AdjustCannonList()

    # 敵戦車の移動
    def Move(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()

        # 戦車との当たり判定
        if result[1][0] > 0 and self.dx > 0 or result[1][1] > 0 and self.dx < 0:
            self.dx = 0
        if result[1][2] > 0 and self.dy > 0 or result[1][3] > 0 and self.dy < 0:
            self.dy = 0

        # 壁との当たり判定
        if result[2][0] > 0 and self.dx > 0 or result[2][1] > 0 and self.dx < 0:
            self.dx = 0
        if result[2][2] > 0 and self.dy > 0 or result[2][3] > 0 and self.dy < 0:
            self.dy = 0

        # 速度を加算
        self.x += self.dx
        self.y += self.dy

    # 砲弾の発射
    def Shot(self):
        target = player.sprite
        # マウスクリック時と同様
        # プレイヤーへ向かって撃つ
        if target:
            rad = GetCannonAngle(target.x, target.y, self.x, self.y)
            dx, dy = GetVelocity(rad, self.CannonSpeed)
            # if len(enemy.CannonList) <= 99:  # フィールド上には最大99発
            if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                self.CannonList.append(Cannon("cannon.png", self.x - self.rect.width - 5, self.y, self.CannonSpeed, dx, dy))


# 砲弾
class Cannon(MovingObject):

    def __init__(self, filename, x, y, v, dx, dy):
        super().__init__(filename, x, y, v)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.bounds = 0  # 反射回数

    # 砲弾の振る舞いの管理
    def update(self):
        # 当たり判定
        result = self.DetectCollision()
        # print(result)      #デバッグ用

        # 戦車・砲弾と衝突
        if result[0] + sum(result[1]) > 0:
            self.kill()
        # 壁との衝突
        elif sum(result[2]) > 0:
            # 2回目の反射なら消滅
            self.bounds += 1
            if self.bounds > 1:
                self.kill()

            # x方向の反射
            elif result[2][0] + result[2][1] > 0:
                self.dx *= -1
            # y方向の反射
            elif result[2][2] + result[2][3] > 0:
                self.dy *= -1

        # 速度を座標に加算
        self.x += self.dx
        self.y += self.dy
        # print(self.x, self.y)
        # 座標の更新
        self.rect.x = self.x
        self.rect.y = self.y


# 画像の読み込み
def load_img(filename, colorkey=None):
    img = pygame.image.load(filename)
    img = img.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey, RLEACCEL)
    return img


# 砲弾の角度を得る
def GetCannonAngle(x1, y1, x2, y2):
    return math.atan2(x1 - x2, y1 - y2)


# 2点間の距離を求める
def GetDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 角度から縦・横方向成分を求める
def GetVelocity(r, v):
    return math.sin(r) * math.sqrt(v), math.cos(r) * math.sqrt(v)


# 壁を配置
def MakeWalls(m):
    for i in range(m.row):
        for j in range(m.col):
            if m.map[i][j]:
                Wall(m.images[1], j * m.m_size, i * m.m_size)


# font = pygame.font.SysFont(None, 50)
# text1 = ("You Win",True,(238,238,238))
# text2 = ("You Loose",True,(238,238,238))

# pygameの準備
pygame.init()  # pygame初期化
pygame.display.set_mode((w, h), 0, 32)  # 画面設定
pygame.display.set_caption("TANK GAME")
screen = pygame.display.get_surface()

# グループの準備
player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
cannons = pygame.sprite.Group()
walls = pygame.sprite.Group()
all_object = pygame.sprite.RenderUpdates()

# グループ分け
Tank.containers = all_object, player
Enemy.containers = all_object, enemies
Cannon.containers = all_object, cannons
Wall.containers = all_object, walls


def main():
    # 戦車の準備
    global y_target, x_target
    Tank("tank_0.png", w / 4, h / 2, 1)
    for i in range(1, 3):
        Enemy("tank_1.png", w * 3 / 4, h * i / 3, 1, 0, 0, time.time())

    # オブジェクト生成
    Map.images[0] = load_img("tile.png")  # 地面
    Map.images[1] = load_img("wall.png")  # 壁
    m = Map()
    MakeWalls(m)  # 壁を生成

    while 1:
        pygame.time.wait(10)  # 更新時間間隔
        screen.fill((0, 0, 0, 0))  # 画面の背景色

        all_object.update()  # すべて更新
        # print(player, enemies, cannons, walls)
        all_object.draw(screen)  # すべて描写

        pygame.display.update()  # 画面更新

        # イベント処理
        for event in pygame.event.get():
            # マウスクリックで砲弾発射
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
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


if __name__ == '__main__': main()
