# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import numpy as np
import math
import sys

import time
import random

(w, h) = (640, 480)  # 画面サイズ

(x_target, y_target) = (0, 0)  # 目標位置

# 敵戦車移動に関するウェイト(0→移動に影響しない)
AD   = 0     #味方との距離の重視度合い(AiiesDistance)
ED   = 1     #敵との距離の重視度合い(EnemyDistance)
WD   = 2     #壁との距離の重視度合い(WallsDistance)
AC   = 4     #弾丸回避の重要度合い(AvoidingCannon)
# プレイヤー戦車と敵戦車の心地よい距離(GoodDistance)
GD   = 240   



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
    CannonW = 10  # 砲弾の幅と高さ
    CannonH = 10

    def __init__(self, filename, x, y, v):
        super().__init__(filename, x, y, v)
        self.CannonList = []  # 砲弾のリスト
        # 射撃砲台の長さを求める
        self.radius = GetDistance(self.x, self.y, self.x + 0.5 * (self.rect.width + self.CannonW),
                                  self.y + 0.5 * (self.rect.height + self.CannonH))
        self.GunDirection = 0  # 射撃口の向き
        self.shot_x = self.x + 0.5 * (self.rect.width - self.CannonW) - self.radius * math.sin(
            math.pi * 0.5)  # 射撃位置のx座標
        self.shot_y = self.y + 0.5 * (self.rect.height - self.CannonH) - self.radius * math.cos(
            math.pi * 0.5)  # 射撃位置のy座標

        self.log = []  # 位置のログ

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
        # 座標の記録
        self.log.insert(0, [self.x, self.y])

        # マウスカーソルの位置を取得
        mouse_pos = pygame.mouse.get_pos()
        # 戦車の中心とマウスカーソルとの角度を求める
        self.GunDirection = GetCannonAngle(int(mouse_pos[0]), int(mouse_pos[1]),
                                           self.x + 0.5 * self.rect.width, self.y + 0.5 * self.rect.height)
        # 射撃口の描画
        self.DrawGun()

    def Shot(self):
        # マウスクリックで砲弾発射
        # 砲弾の角度を求める
        rad = GetCannonAngle(x_target, y_target, self.x, self.y)
        dx, dy = GetVelocity(rad, self.CannonSpeed)
        # 戦車に追加
        if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
            self.CannonList.append(Cannon("cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))

    # KILLされた砲弾を整理
    def AdjustCannonList(self):
        new_list = []
        for cannon in self.CannonList:
            if cannon.alive():  # 砲弾が崩壊していなければリストに追加
                new_list.append(cannon)

        self.CannonList = new_list

    # 射撃砲台の描画
    def DrawGun(self):
        # 射撃ポイントを求める
        self.shot_x = self.x + 0.5 * (self.rect.width - self.CannonW) + self.radius * math.sin(self.GunDirection)
        self.shot_y = self.y + 0.5 * (self.rect.height - self.CannonH) + self.radius * math.cos(self.GunDirection)

        shot_x = self.shot_x + 0.5 * self.CannonW
        shot_y = self.shot_y + 0.5 * self.CannonH

        # 射撃砲台は線と丸で表現(仮)
        if all_object.has(self):
            pygame.draw.circle(screen, (0, 0, 0), (int(shot_x), int(shot_y)), int(0.5 * self.CannonW))
            pygame.draw.line(screen, (0, 0, 0),
                             (int(self.x + 0.5 * self.rect.width), int(self.y + 0.5 * self.rect.height)),
                             (int(shot_x), int(shot_y)), int(0.5 * self.CannonW))

# 敵戦車
class Enemy(Tank):
    CannonSpeed = 2.0

    def __init__(self, filename, x, y, v, dx, dy, firetime):
        super().__init__(filename, x, y, v)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.firetime = firetime  # 前回発射時間
        width = self.rect.width
        height = self.rect.height
        self.serch = Rect(x - 1.5 * width, y - 1.5 * height, 4 * width, 4 * height)  # 感知範囲
        self.frames = 0  # 射撃間隔を測る際に使用
        self.CD_list = []       #移動方向を決定するリスト

    def update(self):
        if all_object.has(player):

            self.Move()  # 戦車の移動

            # 砲弾の発射
            self.Shot()
            # 砲弾の整理
            self.AdjustCannonList()

            # 座標の更新
            self.rect.x = self.x
            self.rect.y = self.y
            # 座標の記録
            self.log.insert(0, [self.x, self.y])
    ###################### プレイヤーとの距離感に対するバネの力の方向 ##################
    def Sense_of_Distance(self):
        distance = GetDistance(player.sprite.x, player.sprite.y, self.x, self.y)
        change = distance - GD
        if change > 0:
            return 1
        else:
            return -1

    ###################### どの方向に移動するか決定する行列に要素を追加 #################
    def Add_CD_list(self,weight,dx,dy):
        self.CD_list.append([weight,dx,dy])

    # 敵戦車の移動
    def Move(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()

        ##################### ここら辺に移動戦略関数 ########################
        #初期化
        self.CD_list = []
        
        #プレイヤー向きの方向ベクトルを算出
        angle = GetCannonAngle(player.sprite.x, player.sprite.y, self.x, self.y)
        dx, dy = GetVelocity(angle,self.v)
        #方向ベクトルを正規化
        dev = math.sqrt(dx**2 + dy**2)
        dx = dx/dev
        dy = dy/dev
        #重みの導出 (プレイヤーの現在地-心地よい距離GD)*ED
        weight = ED * self.Sense_of_Distance()
        #移動先を決定する行列に追加
        self.Add_CD_list(weight,dx,dy)

        #まっつん追加スペース
        # 弾避けベクトルを求める
        for c in cannons:
                nx, ny, d = self.CannonDodge(c)
                if nx == -1 and ny == -1 and d == -1:
                    continue
                else:
                    weight = AC * 1/d
                    self.Add_CD_list(weight, nx, ny)

        # 壁避けベクトルを求める
        for w in walls:
            wx, wy, d = self.WallDodge(w)
            if wx == -1 and wx == -1 and d == -1:
                continue
            else:
                weight = WD * 1/d
                self.Add_CD_list(1/d, wx, wy)



        #各戦車の移動を計算
        #self.dx, self.dy = GetSpeed(self.CD_list)
        vx, vy = GetSpeed(self.CD_list)
        self.GetSpeed2(vx,vy)

        # 戦車との当たり判定
        if result[1][0] > 0 and self.dx > 0 or result[1][1] > 0 and self.dx < 0:
            self.dx = 0
        if result[1][2] > 0 and self.dy > 0 or result[1][3] > 0 and self.dy < 0:
            self.dy = 0

        # 壁との当たり判定
        while result[2][0] > 0 and self.dx > 0 or result[2][1] > 0 and self.dx < 0:
            self.dx = ((int(random.random() * 1000) % 3) - 1) * self.v
            result = self.DetectCollision()
        while result[2][2] > 0 and self.dy > 0 or result[2][3] > 0 and self.dy < 0:
            self.dy = ((int(random.random() * 1000) % 3) - 1) * self.v
            result = self.DetectCollision()

        # 速度を加算
        self.x += self.dx
        self.y += self.dy
        self.serch = Rect(self.x - 1.5 * self.rect.width, self.y - 1.5 * self.rect.height, 4 * self.rect.width,
                          4 * self.rect.height)

    # 射撃の管理
    def Shot(self):
        self.frames += 1

        if self.frames > 30:  # 30フレームごとに射撃可能
            self.frames = 0
            rad = self.ShotStrategy(player.sprite)  # 射撃する角度を求める

            # 指定された方向に撃つ
            if rad:
                # 射撃ポイントを求める
                self.shot_x = self.x + 0.5 * (self.rect.width - self.CannonW) + self.radius * math.sin(rad)
                self.shot_y = self.y + 0.5 * (self.rect.height - self.CannonH) + self.radius * math.cos(rad)

                dx, dy = GetVelocity(rad, self.CannonSpeed)  # 砲弾の速度（x方向・y方向）を求める

                if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                    self.CannonList.append(Cannon("cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))
                self.GunDirection = rad  # 射撃口の向きを更新

        # 射撃口の描画
        self.DrawGun()

    # 射撃の戦術アルゴリズム
    def ShotStrategy(self, target):
        cannon_num = len(self.CannonList)  # 現在保有する砲弾の数
        (x, y) = (0, 0)  # 射撃位置

        if cannon_num == 0:  # 相手の今いる位置に射撃
            (x, y) = (player.sprite.x, player.sprite.y)

        elif cannon_num == 1:  # 偏差射撃（逆）
            x, y = self.GetDeviationPosition(target)
            x = player.sprite.x * 2 - x
            y = player.sprite.x * 2 - y

        elif cannon_num == 2:  # 偏差射撃
            x, y = self.GetDeviationPosition(target)

        elif 3 <= cannon_num < 5:  # 残りの砲弾
            dis = GetDistance(self.x, self.y, player.sprite.x, player.sprite.y)  # プレイヤーとの距離を測定

            if dis < 60:  # プレイヤーとの距離が近い場合
                (x, y) = (player.x, player.y)  # 相手の今いる位置に射撃
            else:
                return 0

        rad = self.GetShotAngle(x, y)

        return rad

    # 偏差位置を求める
    def GetDeviationPosition(self, target):
        dis = 20  # 偏差距離
        (x_now, y_now) = (target.log[0][0], target.log[0][1])  # 現在の位置
        (x_prev, y_prev) = (target.log[1][0], target.log[1][1])  # 一フレーム前の位置

        # 標的の進む方向を得る
        rad = GetCannonAngle(x_now, y_now, x_prev, y_prev)

        # 偏差位置を計算
        if rad:
            (x, y) = (x_now + dis * math.cos(rad), y_now + dis * math.sin(rad))
        else:
            (x, y) = (x_now, y_now)

        return x, y

    # どの方向に射撃するかを決定する
    def GetShotAngle(self, x, y):
        rad = GetCannonAngle(x, y, self.x, self.y)

        return rad

    # 敵戦車弾除けベクトル(法線ベクトル)返還
    def CannonDodge(self, c):
        # 感知範囲との接触判定
        if self.serch.collidepoint(c.x, c.y):
            # 近づく弾かどうか
            if GetDistance(self.rect.centerx, self.rect.centery, c.x, c.y) > GetDistance(self.rect.centerx, self.rect.centery, c.x + c.dx, c.y + c.dy):
                # 法線＝(c.dy/c.dx, -1) or c.dxが0のとき(1,0)
                if c.dx == 0:
                    nx = -1
                    ny = 0
                else:
                    nx = c.dy/c.dx
                    ny = -1
                # 正規化
                d = math.sqrt(nx ** 2 + ny ** 2)
                nx = nx / d
                ny = ny / d

                r = GetCannonAngle(self.rect.centerx, self.rect.centery, c.x, c.y)
                vx, vy = GetVelocity(r, 1)
                direction = c.dx * vy - c.dy * vx  # 法線の方向決定
                distance = abs(direction) / math.sqrt(c.dx ** 2 + c.dy ** 2)  # 戦車の中心と弾道との距離
                # 弾道に近づかないように
                if (direction >= 0 or c.dx < 0) and not (direction >= 0 and c.dx < 0):
                    nx = -nx
                    ny = -ny
                return nx, ny, distance
            else:
                return -1, -1, -1
        else:
            return -1, -1, -1

    # 敵戦車の壁避けベクトル返還
    def WallDodge(self, w):
        dx = 0
        dy = 0
        if self.serch.colliderect(w.rect):  # 感知範囲との接触判定
            wt_x = self.x - w.x  # 戦車と壁とのx、yの直線距離
            wt_y = self.y - w.y  
            if abs(wt_x) >= abs(wt_y):  # 戦車と壁がx、y方向でどちらが大きく離れてるか(離れてる方向が壁と接触してる)
                dx = int(math.copysign(self.v, wt_x))
            else:
                dy = int(math.copysign(self.v, wt_y))
            return dx, dy, GetDistance(self.x, self.y, w.x, w.y)
        else:
            return -1, -1, -1

    def GetSpeed2(self, vx, vy):
        # 最終的な移動方向決定
        # 単位円を考えたときにそのx，y方向を1とするか0とするか
        if abs(vx) >= math.cos(3 * math.pi / 8):
            self.dx = int(math.copysign(self.v, vx))
        else:
            self.dx = 0

        if abs(vy) >= math.sin(math.pi / 8):
            self.dy = int(math.copysign(self.v, vy))
        else:
            self.dy = 0


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

############### 行列を計算して速度を得る ################
def GetSpeed(List):
    result=[0.0, 0.0]
    for i in List:
        result[0] += i[0]*i[1]
        result[1] += i[0]*i[2]
    dev = math.sqrt(result[0]**2 + result[1]**2)
    if not dev == 0:
        result[0] = result[0]/dev   #正規化
        result[1] = result[1]/dev   #正規化
    else:
        result[0]=0
        result[1]=0
    return result[0], result[1]
    

# 砲弾の角度を得る（1：対象物　2：発射点）
def GetCannonAngle(x1, y1, x2, y2):
    return math.atan2(x1 - x2, y1 - y2)


# 2点間の距離を求める
def GetDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 角度から縦・横方向成分を求める
def GetVelocity(r, v):
    return math.sin(r) * math.sqrt(v), math.cos(r) * math.sqrt(v)

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
            if m.map[i][j]:
                Wall(m.images[1], j * m.m_size, i * m.m_size)


# 床の描画
def DrawTiles(m):
    for i in range(m.row):
        for j in range(m.col):
            screen.blit(m.images[0], (j * m.m_size, i * m.m_size))


# pygameの準備
pygame.init()  # pygame初期化
pygame.display.set_mode((w, h), 0, 32)  # 画面設定
pygame.display.set_caption("TANK GAME")
screen = pygame.display.get_surface()

# フォント
font = pygame.font.SysFont(None, 60)
text1 = font.render("   You Win!   ", True, (255, 255, 0))
text2 = font.render("You Exploded!", True, (255, 64, 64))

# グループの準備
player = pygame.sprite.GroupSingle(None)
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
    # 終了フラグ
    FinishFlag = False

    # 戦車の準備
    global y_target, x_target
    Tank("tank_0.png", w / 4, h / 2, 1)

    for i in range(1, 4):
        Enemy("tank_1.png", w * 3 / 4, h * i / 4, 1, 0, 0, time.time())

    # オブジェクト生成
    Map.images[0] = load_img("tile.png")  # 地面
    Map.images[1] = load_img("wall.png")  # 壁
    m = Map()
    MakeWalls(m)  # 壁を生成

    #敵戦車のウェイトを表示
    print('Weight of Allies Distance:')
    print(AD)
    print('Weight of Enemy  Distance:')
    print(ED)
    print('Weight of Walls  Distance:')
    print(WD)
    print('Weight of Avoiding Cannon:')
    print(AC)
    print('Comfortable Distance:')
    print(GD)

    while 1:
        pygame.time.wait(10)  # 更新時間間隔

        # 終了フラグが立ってないときに更新
        if not FinishFlag:
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            all_object.update()  # すべて更新
            # print(player, enemies, cannons, walls)

        # プレイヤーがいなくなったとき
        if not all_object.has(player):
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            enemies.update()
            screen.blit(text2, (w / 4, h / 4))
            FinishFlag = True

        # 敵がいなくなったとき
        if not all_object.has(enemies):
            DrawTiles(m)  # 背景として床を描画
            all_object.draw(screen)  # すべて描写
            player.sprite.DrawGun()
            screen.blit(text1, (w / 4, h / 4))
            FinishFlag = True

        pygame.display.update()  # 画面更新

        # イベント処理
        for event in pygame.event.get():
            # マウスクリックで砲弾発射
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


if __name__ == '__main__': main()
