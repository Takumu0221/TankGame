import csv

import gym.spaces

from tank.tank_game.func import *

__all__ = [
    'Map',
    'TankEnv',
    'Player',
    'Wall',
    'Cannon',
    'Object',
    'Tank',
    'InnerWall',
    'OuterWall',
    'Enemy_Manual',
    'MovingObject',
    'Enemy_Learn',
]


# マップ
class Map:
    # マップデータ
    with open("../../map/map01.csv") as f:
        reader = csv.reader(f)
        map = [[int(x) for x in row] for row in reader]

    row, col = len(map), len(map[0])  # マップの行数,列数を取得
    images = [None] * 256  # マップチップ
    m_size = 40  # 1マスの画像サイズ


# オブジェクト
class Object(pygame.sprite.Sprite):
    # 初期化
    def __init__(self, filename, x, y, w, h):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.containers = None
        self.image = load_img(filename)
        self.filename = filename
        self.x = x  # x座標　（小数点以下まで含む）
        self.y = y  # y座標　（小数点以下まで含む）
        width = self.image.get_width()  # 横幅
        height = self.image.get_height()  # 縦幅
        self.rect = Rect(x, y, width, height)  # 四角形の宣言

        self.w = w  # mapの横幅
        self.h = h  # mapの縦幅

    def draw(self, Screen):
        Screen.blit(self.image, self.rect)

    # 直線とオブジェクトが交わるか判定
    def DetectIntersection(self, P0, P1):
        corners = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]

        points = [0, 0, 0, 0]
        for i in range(len(corners)):
            p = line_cross_point(corners[i], corners[(i + 1) % 4], P0, P1)  # 引数で指定された線分と壁の端との交点を求める

            if p is not None:  # 交わるとき，交点を追加
                points[i] = p

        return points  # 交点のリストを返す


# 壁オブジェクト
class Wall(Object):
    # 初期化
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, Screen):
        Screen.blit(self.image, self.rect)


class InnerWall(Wall):
    # 初期化
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OuterWall(Wall):
    # 初期化
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.corners = [[40, 40], [self.w - 40, 40], [40, self.h - 40], [self.w - 40, self.h - 40]]  # 四隅の座標（左上，右上，左下，右下）


# 移動オブジェクト
class MovingObject(Object):
    # 初期化
    def __init__(self, *args, v, **kwargs):  # イメージファイル名・x座標・y座標・速さ
        super().__init__(*args, **kwargs)
        self.v = v

    # 描画
    def draw(self, Screen):
        Screen.blit(self.image, self.rect)

    # 当たり判定
    def DetectCollision(self):
        result = [0, [0, 0, 0, 0], [0, 0, 0, 0]]
        objects = self.GetAllObjects()

        # print(self.groups())

        for object_collied in pygame.sprite.spritecollide(self, objects, False):
            # 対象との各座標の差
            difference = [(object_collied.x + 0.5 * object_collied.rect.width) - (self.x + 0.5 * self.rect.width),
                          (object_collied.y + 0.5 * object_collied.rect.height) - (self.y + 0.5 * self.rect.height)]

            if self != object_collied:  # 自分自身と異なるとき
                # 砲弾との判定
                if type(object_collied) is Cannon:
                    object_collied.kill()
                    Enemy_pos_res()
                    result[0] = 1

                # 戦車との判定
                if type(object_collied) is Player or type(object_collied) is Enemy_Manual \
                        or type(object_collied) is Enemy_Learn:
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

                    # selfが砲弾の時，戦車をkill
                    if type(self) is Cannon:
                        object_collied.kill()
                        Enemy_pos_res()

                # 壁との判定
                if type(object_collied) is InnerWall or type(object_collied) is OuterWall:
                    wall_collied = pygame.sprite.spritecollide(self, walls, False)
                    if len(wall_collied) >= 2:  # 2つ以上の壁と接触しているとき
                        for i in range(len(wall_collied)):
                            if wall_collied[i].rect.x == \
                                    wall_collied[(i + 1) % len(wall_collied)].rect.x:  # 2つの壁のy座標が等しいとき
                                if self.rect.centerx <= wall_collied[i].rect.centerx:  # 壁の左に自分がいるとき（東方向の接触）
                                    result[2][0] = 1
                                    self.x = wall_collied[i].x - self.rect.width  # 位置補正
                                else:  # 壁の右に自分がいるとき（西方向の接触）
                                    result[2][1] = 1
                                    self.x = wall_collied[i].x + object_collied.rect.width  # 位置補正

                            elif wall_collied[i].rect.y == \
                                    wall_collied[(i + 1) % len(wall_collied)].rect.y:  # 2つの壁のx座標が等しいとき
                                if self.rect.centery <= wall_collied[i].rect.centery:  # 壁の上に自分がいるとき（南方向の接触）
                                    result[2][2] = 1
                                    self.y = wall_collied[i].y - self.rect.height  # 位置補正
                                else:  # 壁の下に自分がいるとき（北方向の接触）
                                    result[2][3] = 1
                                    self.y = wall_collied[i].y + wall_collied[i].rect.height  # 位置補正

                    else:  # 1つの壁と接触しているとき
                        # 衝突判定の閾値
                        threshold = [0.5 * (object_collied.rect.width + self.rect.width) - self.v - 1,
                                     0.5 * (object_collied.rect.height + self.rect.height) - self.v - 1]

                        if difference[0] >= threshold[0]:  # 東方向の壁
                            self.x = object_collied.x - self.rect.width  # 位置補正
                            result[2][0] = 1
                        elif difference[0] <= -threshold[0]:  # 西方向の壁
                            self.x = object_collied.x + object_collied.rect.width  # 位置補正
                            result[2][1] = 1
                        elif difference[1] >= threshold[1]:  # 南方向の壁
                            self.y = object_collied.y - self.rect.height  # 位置補正
                            result[2][2] = 1
                        elif difference[1] <= -threshold[1]:  # 北方向の壁
                            self.y = object_collied.y + object_collied.rect.height  # 位置補正
                            result[2][3] = 1
                        else:  # 壁に入り込んでいるとき
                            self.kill()

                    break

        return result

    def GetAllObjects(self):  # 所属するworldのall_objectを取得
        result = pygame.sprite.Group()
        for g in self.groups():
            if len(result) < len(g):
                result = g

        return result


# 戦車
class Tank(MovingObject):
    CannonNum = 5  # 砲弾数
    CannonW = 10  # 砲弾の幅と高さ
    CannonH = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CannonList = []  # 砲弾のリスト
        # 射撃砲台の長さを求める
        self.radius = GetDistance(self.x, self.y, self.x + 0.6 * (self.rect.width + self.CannonW),
                                  self.y + 0.6 * (self.rect.height + self.CannonH))
        self.GunDirection = 0  # 射撃口の向き
        self.shot_x = self.x + 0.5 * (self.rect.width - self.CannonW) - self.radius * math.cos(
            math.pi * 0.5)  # 射撃位置のx座標
        self.shot_y = self.y + 0.5 * (self.rect.height - self.CannonH) - self.radius * math.sin(
            math.pi * 0.5)  # 射撃位置のy座標

        self.log = []  # 位置のログ

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
        self.shot_x, self.shot_y = self.GetShotPoint(self.GunDirection)

        shot_x = self.shot_x + 0.5 * self.CannonW
        shot_y = self.shot_y + 0.5 * self.CannonH

        # 射撃砲台は線と丸で表現(仮)
        if all_object.has(self):
            pygame.draw.circle(screen, (0, 0, 0), (int(shot_x), int(shot_y)), int(0.5 * self.CannonW))
            pygame.draw.line(screen, (0, 0, 0),
                             (int(self.x + 0.5 * self.rect.width), int(self.y + 0.5 * self.rect.height)),
                             (int(shot_x), int(shot_y)), int(0.5 * self.CannonW))

    # 射撃ポイントを求める
    def GetShotPoint(self, rad):
        x = self.x + 0.5 * (self.rect.width - self.CannonW) + self.radius * math.cos(rad)
        y = self.y + 0.5 * (self.rect.height - self.CannonH) + self.radius * math.sin(rad)

        return x, y


# プレイヤー戦車
class Player(Tank):
    CannonSpeed = 2.0  # 砲弾速度

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()

        # キーイベント処理(キャラクタ画像の移動)
        pressed_key = pygame.key.get_pressed()
        if result[1][0] == 0 and result[2][0] == 0:
            if pressed_key[K_RIGHT] or pressed_key[K_d]:
                self.x += self.v
        if result[1][1] == 0 and result[2][1] == 0:
            if pressed_key[K_LEFT] or pressed_key[K_a]:
                self.x -= self.v
        if result[1][2] == 0 and result[2][2] == 0:
            if pressed_key[K_DOWN] or pressed_key[K_s]:
                self.y += self.v
        if result[1][3] == 0 and result[2][3] == 0:
            if pressed_key[K_UP] or pressed_key[K_w]:
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
        pygame.draw.circle(screen, (108, 134, 79), (int(self.x) + 20, int(self.y) + 20), 16)

    def Shot(self):
        # マウスクリックで砲弾発射
        # 砲弾の角度を求める
        rad = GetCannonAngle(x_target, y_target, self.rect.centerx, self.rect.centery)
        dx, dy = GetVelocity(rad, self.CannonSpeed)
        # 戦車に追加
        if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
            self.CannonList.append(
                Cannon("../../images/cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))


# 敵戦車（パラメタを手動で調整）
class Enemy_Manual(Tank):
    CannonSpeed = 2.0

    def __init__(self, *args, dx, dy, firetime, num, **kwargs):
        super().__init__(*args, **kwargs)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.firetime = firetime  # 前回発射時間
        self.num = num
        width = self.rect.width
        height = self.rect.height
        self.serch = Rect(x - 1.5 * width, y - 1.5 * height, 4 * width, 4 * height)  # 感知範囲
        self.frames = 0  # 射撃間隔を測る際に使用
        self.CD_list = []  # 移動方向を決定するリスト
        self.burst = 0  # 3点バーストにするための変数
        self.Shotlog = [1] * 10

    def update(self):
        global Level
        if all_object.has(enemies_learn):
            UpdateWeight(enemies_learn)  # ウェイトの更新

            # 砲弾の発射
            if Level == 1:
                self.Shot_basic()
            else:
                if not Level == 0:
                    self.Shot()
            # 砲弾の整理
            self.AdjustCannonList()

            self.Move()  # 戦車の移動

            # 座標の更新
            self.rect.x = self.x
            self.rect.y = self.y
            # 座標の記録
            self.log.insert(0, [self.x, self.y])

        # 射撃口の描画
        self.DrawGun()
        pygame.draw.circle(screen, (112, 78, 125), (int(self.x) + 20, int(self.y) + 20), 16)

    ###################### ある戦車に対する各敵戦車間の斥力をリストに追加 ###############
    def RepilsiveForce(self):
        for i in range(Enemy_num):
            if not self.num == i:
                # 既に爆破されている戦車は考慮しない(死戦車はx座標の数値のみ0)
                if not Enemy_pos_manual[2 * i] == 0:
                    angle = GetCannonAngle(Enemy_pos_manual[2 * i], Enemy_pos_manual[2 * i + 1], self.x, self.y)
                    dx, dy = GetVelocity(angle, self.v)
                    # 方向ベクトルを正規化
                    dev = math.sqrt(dx ** 2 + dy ** 2)
                    dx = dx / dev
                    dy = dy / dev
                    # 斥力が働くか否かを判定(斥力が働く範囲に入っているか)
                    distance = GetDistance(Enemy_pos_manual[2 * i], Enemy_pos_manual[(2 * i) + 1], self.x, self.y)
                    change = distance - RFD * (1 - self.Shotlog.count(0) / 20)
                    if change < 0:
                        weight = (-1) * AD
                        # 発生する斥力をリストに追加
                        self.CD_list.append([weight, dx, dy])

    ###################### プレイヤーとの距離感に対するバネの力の方向 ##################
    def Sense_of_Distance(self):
        # distance = GetDistance(player.sprite.x, player.sprite.y, self.x, self.y)
        for enemy in enemies_learn.sprites():
            distance = GetPathDistance(self.rect.center, enemy.rect.center)
            change = distance - GD * (1 - self.Shotlog.count(0) / 20)
            if change > 0:
                return 1
            elif change == 0:
                return 0
            else:
                return -1

    ###################### どの方向に移動するか決定する行列に要素を追加 #################
    def Add_CD_list(self, weight, dx, dy):
        self.CD_list.append([weight, dx, dy])

    # 敵戦車の移動
    def Move(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()
            Enemy_pos_res()

        ##################### ここら辺に移動戦略関数 ########################
        # 初期化
        self.CD_list = []

        # 敵向きの方向ベクトルを算出
        for enemy in enemies_learn.sprites():
            angle = GetCannonAngle(enemy.rect.centerx, enemy.rect.centery, self.x, self.y)
            dx, dy = GetVelocity(angle, self.v)
            # 方向ベクトルを正規化
            dev = math.sqrt(dx ** 2 + dy ** 2)
            dx = dx / dev
            dy = dy / dev
            dx, dy = self.GetPathVelocity(enemy)
            # 重みの導出 (プレイヤーの現在地-心地よい距離GD)*ED
            weight = ED * self.Sense_of_Distance()
            # 移動先を決定する行列に追加
            self.Add_CD_list(weight, dx, dy)

        # 斥力を求める
        self.RepilsiveForce()

        # 弾避けベクトルを求める
        for c in cannons.sprites():
            nx, ny, d = self.CannonDodge(c)
            if nx == -1 and ny == -1 and d == -1:
                continue
            else:
                weight = AC * 1 / d
                self.Add_CD_list(weight, nx, ny)

        # 壁避けベクトルを求める
        for w in walls:
            wx, wy, d = self.WallDodge(w)
            if wx == -1 and wx == -1 and d == -1:
                continue
            else:
                weight = WD * 1 / (d ** 2) * math.ceil(1 - self.Shotlog.count(0) / 10)
                self.Add_CD_list(weight, wx, wy)

        # 各戦車の移動を計算
        self.dx, self.dy = GetSpeed(self.CD_list)
        self.dx = self.dx * self.v
        self.dy = self.dy * self.v

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
        # 敵戦車の位置を記録するリストを更新
        Enemy_pos_manual[2 * self.num] = self.x
        Enemy_pos_manual[2 * self.num + 1] = self.y
        # print(Enemy_pos)
        self.serch = Rect(self.x - 1.5 * self.rect.width, self.y - 1.5 * self.rect.height, 4 * self.rect.width,
                          4 * self.rect.height)

    # 射撃の管理
    def Shot(self):
        self.frames += 1

        if self.frames > 30:  # 30フレームごとに射撃可能
            self.frames = 0
            rad = self.ShotStrategy()  # 射撃する角度を求める

            # 指定された方向に撃つ
            if rad:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(1)  # 値の1
                self.GunDirection = rad  # 射撃口の向きを更新
                self.shot_x, self.shot_y = self.GetShotPoint(rad)  # 射撃ポイントを求める

                dx, dy = GetVelocity(rad, self.CannonSpeed)  # 砲弾の速度（x方向・y方向）を求める

                if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                    self.CannonList.append(
                        Cannon("../../images/cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))
            else:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(0)  # 値の0

    # 射撃の管理(ベーシック)
    def Shot_basic(self):
        self.frames += 1

        if self.frames > 200:  # 2秒ごとにプレイヤー方向に射撃
            self.frames = 0
            enemy = enemies_learn.sprites()[0]
            rad = GetCannonAngle(enemy.rect.centerx, enemy.rect.centery, self.rect.centerx,
                                 self.rect.centery)  # 射撃する角度を求める

            # 指定された方向に撃つ
            if rad:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(1)  # 値の1
                self.GunDirection = rad  # 射撃口の向きを更新
                self.shot_x, self.shot_y = self.GetShotPoint(rad)  # 射撃ポイントを求める

                dx, dy = GetVelocity(rad, self.CannonSpeed)  # 砲弾の速度（x方向・y方向）を求める

                if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                    self.CannonList.append(
                        Cannon("../../images/cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))
            else:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(0)  # 値の0

    # 射撃の戦術アルゴリズム
    def ShotStrategy(self):
        cannon_num = len(self.CannonList)  # 現在保有する砲弾の数
        (x, y) = (0, 0)  # 射撃位置
        dev_dis = 50  # 偏差距離
        target = None

        # 最も距離の近い敵を求める
        min_dis = 1000
        for enemy in enemies_learn.sprites():
            dis = GetDistance(self.x, self.y, enemy.rect.centerx, enemy.rect.centery)  # プレイヤーとの距離を測定
            if min_dis > dis:
                min_dis = dis
                target = enemy

        if cannon_num == 0:  # 相手の今いる位置に射撃
            if min_dis <= GD + 40:
                x, y = self.GetDeviationPosition(target, dev_dis)
                self.burst = 1

        elif cannon_num == 1:  # 偏差射撃（1.5倍）
            if self.burst:
                x, y = self.GetDeviationPosition(target, dev_dis * 1.5)
                # x = player.sprite.rect.centerx * 2 - x
                # y = player.sprite.rect.centery * 2 - y
            else:
                if min_dis <= GD_origin * 0.8:
                    (x, y) = target.rect.center

        elif cannon_num == 2:  # 偏差射撃
            if self.burst:
                (x, y) = target.rect.center
                self.burst = 0
            else:
                if min_dis <= GD_origin * 0.7:
                    (x, y) = target.rect.center

        elif 3 <= cannon_num:  # 残りの砲弾
            if min_dis < GD_origin * 0.6:  # プレイヤーとの距離が近い場合
                (x, y) = target.rect.center  # 相手の今いる位置に射撃
            else:
                return 0

        if x == 0 and y == 0:
            return 0
        rad = self.GetShotAngle(x, y, target)
        return rad

    # 偏差位置を求める
    @staticmethod
    def GetDeviationPosition(target, dis):
        (x_now, y_now) = (target.log[0][0], target.log[0][1])  # 現在の位置
        (x_prev, y_prev) = (target.log[1][0], target.log[1][1])  # 一フレーム前の位置

        # 偏差位置を計算
        if x_now - x_prev or y_now - y_prev:  # 速度が0より大きいとき
            rad = GetCannonAngle(x_now, y_now, x_prev, y_prev)  # 標的の進む方向を得る
            (x, y) = (target.rect.centerx + dis * math.cos(rad), target.rect.centery + dis * math.sin(rad))

        else:  # 静止しているとき
            (x, y) = target.rect.center  # 相手のいる位置を狙う

        return x, y

    # どの方向に射撃するかを決定する
    def GetShotAngle(self, x, y, target):
        # 直接狙えるか判定
        rad = GetCannonAngle(x, y, self.rect.centerx, self.rect.centery)

        if self.JudgeAim(rad, target):
            return rad

        #         # 反射で狙えるか判定
        # rad = self.ReflectionOuterWall()
        # # print(rad)
        # if rad is not None:
        #     return rad
        #
        # # 反射で狙えるか判定
        # rad -= math.pi * 0.5
        # parts = 18
        # for rad in [rad + math.pi * x / parts for x in range(1, parts)]:
        #     if self.JudgeAim(rad):
        #         return rad

        # 反射で狙えるか判定
        rad = self.ReflectionWall(x, y)
        if rad is not None:
            return rad

        return 0

    # 狙えるか判定する
    def JudgeAim(self, rad, target):
        # shot_x, shot_y = self.GetShotPoint(rad)
        # dx, dy = GetVelocity(rad, self.CannonSpeed)
        #
        # # シミュレーションを行う
        # result_direct = self.MoveSimulation(Cannon("cannon.png", shot_x, shot_y, self.CannonSpeed, dx, dy))
        # if type(result_direct[0]) is Player:  # シミュレーションした結果、プレイヤーに当たる時
        #     return True
        # else:
        #     return False

        # シミュレーションを行う
        start_x, start_y = self.rect.center
        length = max(w, h)  # 画面の縦と横の内大きい方
        end_x = start_x + length * math.cos(rad)
        end_y = start_y + length * math.sin(rad)

        line = [[start_x, start_y], [end_x, end_y]]  # radで指定された方向の直線（線分）a
        dis_p = GetDistance(self.rect.centerx, self.rect.centery,  # プレイヤーと自分との距離
                            target.rect.centerx, target.rect.centery)

        for o in all_object.sprites():
            points = o.DetectIntersection(line[0], line[1])
            if points != [0, 0, 0, 0]:  # 交点が存在する
                if enemies_manual.has(o) and o is not self or walls.has(o):
                    dis_o = GetDistance(self.rect.centerx, self.rect.centery,  # オブジェクトと自分との距離
                                        o.rect.centerx, o.rect.centery)
                    if dis_p > dis_o:
                        return False

        return True

    # 砲弾などの移動シミュレーション
    @staticmethod
    def MoveSimulation(o):
        o.kill()  # 作成した時点でグループに入ってしまうので除外
        objects = CopyWorld()  # シミュレーション用にworldを複製
        objects_copy = [x for x in objects.sprites()]  # worldのコピー
        objects.add(o)  # シミュレーション用の世界に対象を追加
        collided_object = 0  # 衝突したオブジェクト
        t = 0  # 繰り返し回数

        while 1:
            # コピーを作成
            o_copy = o

            o.update()
            if not objects.has(o_copy):  # 消滅したとき
                # print(objects, objects_copy)
                # 何と衝突して消滅したかを調べる
                for a in objects_copy:
                    if not a.alive():
                        collided_object = a

                # 座標を記録
                (x, y) = (o_copy.x, o_copy.y)

                break

            t += 1

        # シミュレーション用worldを削除
        for a in objects.sprites():
            a.kill()

        if collided_object:  # 戦車や砲弾と衝突したとき
            return [collided_object, [x, y]]

        else:  # 対象の他に消滅した物体が無ければ壁と衝突したと判定
            # 消滅した地点から最も近い壁を返す
            result = Wall("../../images/wall.png", -1, -1)
            result.kill()
            for wall in walls.sprites():
                if GetDistance(result.rect.centerx, result.rect.centery, x, y) \
                        > GetDistance(wall.rect.centerx, wall.rect.centery, x, y):
                    result = wall

            return [result, [x, y]]

    # 外壁で反射できるかどうかの判定
    def ReflectionOuterWall(self):

        UpdateFalseImage()  # 虚像の位置を更新

        # 虚像のplayerを取得
        players = []
        for o in false_image.sprites():
            if type(o) is Player:
                players.append(o)

        # 外壁での反射で狙えるかの判定
        # enemy_tanks = enemies.sprites() + [x for x in false_image if type(x) is Enemy]
        rad = None
        # print(enemy_tanks)
        for p in players:
            flag = 1
            for o in innerwalls.sprites():
                # print(self.rect.center, p.rect.center)
                points = o.DetectIntersection(self.rect.center, p.rect.center)  # 内壁の虚像の内，プレイヤーとプレイヤーの虚像を結んだ直線と交わるか判定
                # print(points)

                if points != [0, 0, 0, 0]:  # 交わるとき
                    flag = 0
                    break

            if flag:  # 外壁で反射した後、内壁の虚像に当たらないとき
                rad = GetCannonAngle(p.rect.x, p.rect.y, self.x, self.y)
                break
            else:  # 外壁で反射した後，内壁に当たるとき
                rad = None

        return rad

    # 壁で反射できるかどうかの判定（内壁・外壁）
    def ReflectionWall(self, x, y):
        # 引数の示す座標に疑似プレイヤーオブジェクトを配置
        width = player.sprite.rect.width / 2
        height = player.sprite.rect.height / 2
        Player.containers = all_object
        p = Player("../../images/tank_0.png", x - width, y - height, 1)
        Player.containers = all_object, player

        # 自分からn方向への直線を得る（始点と終点で定義）（終点は始点からw×2先の点）
        line_list = []  # 直線のリスト
        rad_player = GetCannonAngle(x, y, self.rect.centerx, self.rect.centery)  # 自分とプレイヤーとの角度
        rad_player -= math.pi * 0.5
        parts = 36
        length = max(w, h)  # 画面の縦と横の内大きい方
        start_x, start_y = self.rect.center
        for r in [rad_player + math.pi * x / parts for x in range(1, parts)]:
            end_x = start_x + 2 * length * math.cos(r)
            end_y = start_y + 2 * length * math.sin(r)

            line_list.append([[start_x, start_y], [end_x, end_y]])  # リストに追加

        # 壁を自分から近い順に並び替え
        objects = {}
        for o in all_object.sprites():
            if o is not self:
                if walls.has(o) or enemies_manual.has(o):
                    objects.setdefault(o, GetDistance(self.rect.centerx, self.rect.centery, o.rect.centerx,
                                                      o.rect.centery))  # enemyとwallを追加

        objects_sorted = sorted(objects.items(), key=lambda a: a[1])  # プレイヤーとの距離で昇順に並び替え

        # それぞれの壁について
        L = 1000  # 十分大きい数
        reflected_line_list = []  # 1回反射させた直線のリスト
        for o in [i[0] for i in objects_sorted]:
            # n方向の直線と交わるか判定
            i = 0
            while i < len(line_list):
                line = line_list[i]
                # 交われば直線を反転させる（交点を始点,終点は対称移動で得る）
                points = o.DetectIntersection(line[0], line[1])
                if points != [0, 0, 0, 0]:  # 交点が存在する
                    if walls.has(o):  # 交点の存在するオブジェクトが壁の時
                        points_dis = [GetDistance(self.rect.centerx, self.rect.centery, x[0], x[1])
                                      if x != 0 else L for x in points]  # 交点と自分との距離を求める
                        points_dis_sorted = sorted(points_dis)  # 昇順に並び替え

                        # 最も近い交点で反射
                        p_i = points_dis.index(points_dis_sorted[0])  # 最も近い交点のインデックス
                        reflect_point = points[p_i]
                        if p_i == 1 or p_i == 3:  # 壁の左右のどちらかで反射する場合
                            reflected_line = [reflect_point, GetLineSymmetricPoint(line[1], reflect_point[0], None)]
                        else:  # 壁の上下で反射する場合
                            reflected_line = [reflect_point, GetLineSymmetricPoint(line[1], None, reflect_point[1])]

                        line_list.remove(line)  # 反射前の直線のリストから削除
                        reflected_line_list.append(reflected_line)  # リストに追加

                    else:  # 交点の存在するオブジェクトが敵の時
                        line_list.remove(line)  # 反射前の直線のリストから削除

                else:  # 交点が存在しない場合
                    i += 1

            # すべての直線を一度反転させたら終了
            if len(line_list) == 0:
                break

        # 反転させた直線について,プレイヤーと交わる物を得る
        Shot_line_list = []
        for line in reflected_line_list:
            points = p.DetectIntersection(line[0], line[1])  # プレイヤーとの交点を求める
            if points != [0, 0, 0, 0]:  # 交点が存在するとき
                player_dis = GetDistance(player.sprite.rect.centerx, player.sprite.rect.centery,
                                         line[0][0], line[0][1])  # プレイヤーと反射点の距離
                # その中からエネミーや壁に交わる物を除外
                flag = 1
                for o in [x for x in all_object.sprites() if innerwalls.has(x) or enemies_manual.has(x)]:
                    # 交点が存在し，反射点との距離がプレイヤーとのよりも短い場合
                    if o.DetectIntersection(line[0], line[1]) != [0, 0, 0, 0] \
                            and player_dis > GetDistance(o.rect.centerx, o.rect.centery, line[0][0], line[0][1]):
                        flag = 0
                if flag:
                    Shot_line_list.append(line)  # リストに追加
                    # print(line)

        # 疑似プレイヤーオブジェクトを削除
        p.kill()

        # 角度を返す
        if len(Shot_line_list) > 0:  # リストが空でないとき
            return GetCannonAngle(Shot_line_list[0][0][0], Shot_line_list[0][0][1], self.rect.centerx,
                                  self.rect.centery)
        else:  # リストが空の時
            return None

    # 敵戦車弾除けベクトル(法線ベクトル)返還
    def CannonDodge(self, c):
        # 感知範囲との接触判定
        if self.serch.collidepoint(c.x, c.y):
            # 近づく弾かどうか
            if GetDistance(self.rect.centerx, self.rect.centery, c.x, c.y) > GetDistance(self.rect.centerx,
                                                                                         self.rect.centery, c.x + c.dx,
                                                                                         c.y + c.dy):
                # 法線＝(c.dy/c.dx, -1) or c.dxが0のとき(1,0)
                if c.dx == 0:
                    nx = -1
                    ny = 0
                else:
                    nx = c.dy / c.dx
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
                dx = math.copysign(self.v, wt_x)
            else:
                dy = math.copysign(self.v, wt_y)
            return dx, dy, GetDistance(self.x, self.y, w.x, w.y) / 45
        else:
            return -1, -1, -1

    # target（座標）までの経路的な距離が近くなるような方向を求める
    def GetPathVelocity(self, target):
        # 自分の周囲のブロックを検査し，最も経路的な距離が短くなるようなブロックを求める
        result = [GetPathDistance(self.rect.center, target.rect.center), self.rect.center]  # 経路的な距離・座標
        m = Map.m_size
        for delta in [(-m, 0), (0, m), (m, 0), (0, -m), (-m, -m), (m, m), (-m, m), (m, -m)]:
            x = self.rect.centerx + delta[0]
            y = self.rect.centery + delta[1]
            dis = GetPathDistance([x, y], target.rect.center)

            if result[0] > dis != math.inf:  # 現在地よりも経路的な距離が短い場合
                result = [dis, [x, y]]

        # 求めたブロックへの方向ベクトルを計算
        dx = (result[1][0] - self.rect.centerx) / m
        dy = (result[1][1] - self.rect.centery) / m

        if dx == 0 and dy == 0:  # 現在地が経路的な距離が最も近い
            return 0, 0
        else:  # 経路的な距離が短くなるような方向ベクトルを返す
            return dx, dy


# 敵戦車（教科学習）
class Enemy_Learn(Tank):
    CannonSpeed = 2.0

    def __init__(self, *args, dx, dy, firetime, num, **kwargs):
        super().__init__(*args, **kwargs)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.firetime = firetime  # 前回発射時間
        self.num = num
        width = self.rect.width
        height = self.rect.height
        self.serch = Rect(x - 1.5 * width, y - 1.5 * height, 4 * width, 4 * height)  # 感知範囲
        self.frames = 0  # 射撃間隔を測る際に使用
        self.CD_list = []  # 移動方向を決定するリスト
        self.burst = 0  # 3点バーストにするための変数
        self.Shotlog = [1] * 10

    def update(self):
        global Level
        if all_object.has(enemies_manual):
            UpdateWeight(enemies_manual)  # ウェイトの更新

            # 砲弾の発射
            if Level == 1:
                self.Shot_basic()
            else:
                if not Level == 0:
                    self.Shot()
            # 砲弾の整理
            self.AdjustCannonList()

            self.Move()  # 戦車の移動

            # 座標の更新
            self.rect.x = self.x
            self.rect.y = self.y
            # 座標の記録
            self.log.insert(0, [self.x, self.y])

        # 射撃口の描画
        self.DrawGun()
        pygame.draw.circle(screen, (112, 78, 125), (int(self.x) + 20, int(self.y) + 20), 16)

    ###################### ある戦車に対する各敵戦車間の斥力をリストに追加 ###############
    def RepilsiveForce(self):
        for i in range(Enemy_num):
            if not self.num == i:
                # 既に爆破されている戦車は考慮しない(死戦車はx座標の数値のみ0)
                if not Enemy_pos_learn[2 * i] == 0:
                    angle = GetCannonAngle(Enemy_pos_learn[2 * i], Enemy_pos_learn[2 * i + 1], self.x, self.y)
                    dx, dy = GetVelocity(angle, self.v)
                    # 方向ベクトルを正規化
                    dev = math.sqrt(dx ** 2 + dy ** 2)
                    dx = dx / dev
                    dy = dy / dev
                    # 斥力が働くか否かを判定(斥力が働く範囲に入っているか)
                    distance = GetDistance(Enemy_pos_learn[2 * i], Enemy_pos_learn[(2 * i) + 1], self.x, self.y)
                    change = distance - RFD * (1 - self.Shotlog.count(0) / 20)
                    if change < 0:
                        weight = (-1) * AD
                        # 発生する斥力をリストに追加
                        self.CD_list.append([weight, dx, dy])

    ###################### プレイヤーとの距離感に対するバネの力の方向 ##################
    def Sense_of_Distance(self):
        # distance = GetDistance(player.sprite.x, player.sprite.y, self.x, self.y)
        for enemy in enemies_manual.sprites():
            distance = GetPathDistance(self.rect.center, enemy.rect.center)
            change = distance - GD * (1 - self.Shotlog.count(0) / 20)
            if change > 0:
                return 1
            elif change == 0:
                return 0
            else:
                return -1

    ###################### どの方向に移動するか決定する行列に要素を追加 #################
    def Add_CD_list(self, weight, dx, dy):
        self.CD_list.append([weight, dx, dy])

    # 敵戦車の移動
    def Move(self):
        result = self.DetectCollision()

        # 砲弾と衝突した時
        if result[0] == 1:
            self.kill()
            Enemy_pos_res()

        ##################### ここら辺に移動戦略関数 ########################
        # 初期化
        self.CD_list = []

        # 敵向きの方向ベクトルを算出
        for enemy in enemies_manual.sprites():
            angle = GetCannonAngle(enemy.rect.centerx, enemy.rect.centery, self.x, self.y)
            dx, dy = GetVelocity(angle, self.v)
            # 方向ベクトルを正規化
            dev = math.sqrt(dx ** 2 + dy ** 2)
            dx = dx / dev
            dy = dy / dev
            dx, dy = self.GetPathVelocity(enemy)
            # 重みの導出 (プレイヤーの現在地-心地よい距離GD)*ED
            weight = ED * self.Sense_of_Distance()
            # 移動先を決定する行列に追加
            self.Add_CD_list(weight, dx, dy)

        # 斥力を求める
        self.RepilsiveForce()

        # 弾避けベクトルを求める
        for c in cannons.sprites():
            nx, ny, d = self.CannonDodge(c)
            if nx == -1 and ny == -1 and d == -1:
                continue
            else:
                weight = AC * 1 / d
                self.Add_CD_list(weight, nx, ny)

        # 壁避けベクトルを求める
        for w in walls:
            wx, wy, d = self.WallDodge(w)
            if wx == -1 and wx == -1 and d == -1:
                continue
            else:
                weight = WD * 1 / (d ** 2) * math.ceil(1 - self.Shotlog.count(0) / 10)
                self.Add_CD_list(weight, wx, wy)

        # 各戦車の移動を計算
        self.dx, self.dy = GetSpeed(self.CD_list)
        self.dx = self.dx * self.v
        self.dy = self.dy * self.v

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
        # 敵戦車の位置を記録するリストを更新
        Enemy_pos_learn[2 * self.num] = self.x
        Enemy_pos_learn[2 * self.num + 1] = self.y
        # print(Enemy_pos)
        self.serch = Rect(self.x - 1.5 * self.rect.width, self.y - 1.5 * self.rect.height, 4 * self.rect.width,
                          4 * self.rect.height)

    # 射撃の管理
    def Shot(self):
        self.frames += 1

        if self.frames > 30:  # 30フレームごとに射撃可能
            self.frames = 0
            rad = self.ShotStrategy()  # 射撃する角度を求める

            # 指定された方向に撃つ
            if rad:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(1)  # 値の1
                self.GunDirection = rad  # 射撃口の向きを更新
                self.shot_x, self.shot_y = self.GetShotPoint(rad)  # 射撃ポイントを求める

                dx, dy = GetVelocity(rad, self.CannonSpeed)  # 砲弾の速度（x方向・y方向）を求める

                if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                    self.CannonList.append(
                        Cannon("../../images/cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))
            else:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(0)  # 値の0

    # 射撃の管理(ベーシック)
    def Shot_basic(self):
        self.frames += 1

        if self.frames > 200:  # 2秒ごとにプレイヤー方向に射撃
            self.frames = 0
            enemy = enemies_manual.sprites()[0]
            rad = GetCannonAngle(enemy.rect.centerx, enemy.rect.centery, self.rect.centerx,
                                 self.rect.centery)  # 射撃する角度を求める

            # 指定された方向に撃つ
            if rad:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(1)  # 値の1
                self.GunDirection = rad  # 射撃口の向きを更新
                self.shot_x, self.shot_y = self.GetShotPoint(rad)  # 射撃ポイントを求める

                dx, dy = GetVelocity(rad, self.CannonSpeed)  # 砲弾の速度（x方向・y方向）を求める

                if len(self.CannonList) <= self.CannonNum - 1:  # フィールド上には最大5発
                    self.CannonList.append(
                        Cannon("../../images/cannon.png", self.shot_x, self.shot_y, self.CannonSpeed, dx, dy))
            else:
                self.Shotlog.pop(0)  # 要素数の0
                self.Shotlog.append(0)  # 値の0

    # 射撃の戦術アルゴリズム
    def ShotStrategy(self):
        cannon_num = len(self.CannonList)  # 現在保有する砲弾の数
        (x, y) = (0, 0)  # 射撃位置
        dev_dis = 50  # 偏差距離
        target = None

        # 最も距離の近い敵を求める
        min_dis = 1000
        for enemy in enemies_manual.sprites():
            dis = GetDistance(self.x, self.y, enemy.rect.centerx, enemy.rect.centery)  # プレイヤーとの距離を測定
            if min_dis > dis:
                min_dis = dis
                target = enemy

        if cannon_num == 0:  # 相手の今いる位置に射撃
            if min_dis <= GD + 40:
                x, y = self.GetDeviationPosition(target, dev_dis)
                self.burst = 1

        elif cannon_num == 1:  # 偏差射撃（1.5倍）
            if self.burst:
                x, y = self.GetDeviationPosition(target, dev_dis * 1.5)
                # x = player.sprite.rect.centerx * 2 - x
                # y = player.sprite.rect.centery * 2 - y
            else:
                if min_dis <= GD_origin * 0.8:
                    (x, y) = target.rect.center

        elif cannon_num == 2:  # 偏差射撃
            if self.burst:
                (x, y) = target.rect.center
                self.burst = 0
            else:
                if min_dis <= GD_origin * 0.7:
                    (x, y) = target.rect.center

        elif 3 <= cannon_num:  # 残りの砲弾
            if min_dis < GD_origin * 0.6:  # プレイヤーとの距離が近い場合
                (x, y) = target.rect.center  # 相手の今いる位置に射撃
            else:
                return 0

        if x == 0 and y == 0:
            return 0
        rad = self.GetShotAngle(x, y, target)
        return rad

    # 偏差位置を求める
    @staticmethod
    def GetDeviationPosition(target, dis):
        (x_now, y_now) = (target.log[0][0], target.log[0][1])  # 現在の位置
        (x_prev, y_prev) = (target.log[1][0], target.log[1][1])  # 一フレーム前の位置

        # 偏差位置を計算
        if x_now - x_prev or y_now - y_prev:  # 速度が0より大きいとき
            rad = GetCannonAngle(x_now, y_now, x_prev, y_prev)  # 標的の進む方向を得る
            (x, y) = (target.rect.centerx + dis * math.cos(rad), target.rect.centery + dis * math.sin(rad))

        else:  # 静止しているとき
            (x, y) = target.rect.center  # 相手のいる位置を狙う

        return x, y

    # どの方向に射撃するかを決定する
    def GetShotAngle(self, x, y, target):
        # 直接狙えるか判定
        rad = GetCannonAngle(x, y, self.rect.centerx, self.rect.centery)

        if self.JudgeAim(rad, target):
            return rad

        #         # 反射で狙えるか判定
        # rad = self.ReflectionOuterWall()
        # # print(rad)
        # if rad is not None:
        #     return rad
        #
        # # 反射で狙えるか判定
        # rad -= math.pi * 0.5
        # parts = 18
        # for rad in [rad + math.pi * x / parts for x in range(1, parts)]:
        #     if self.JudgeAim(rad):
        #         return rad

        # 反射で狙えるか判定
        rad = self.ReflectionWall(x, y)
        if rad is not None:
            return rad

        return 0

    # 狙えるか判定する
    def JudgeAim(self, rad, target):
        # shot_x, shot_y = self.GetShotPoint(rad)
        # dx, dy = GetVelocity(rad, self.CannonSpeed)
        #
        # # シミュレーションを行う
        # result_direct = self.MoveSimulation(Cannon("cannon.png", shot_x, shot_y, self.CannonSpeed, dx, dy))
        # if type(result_direct[0]) is Player:  # シミュレーションした結果、プレイヤーに当たる時
        #     return True
        # else:
        #     return False

        # シミュレーションを行う
        start_x, start_y = self.rect.center
        length = max(w, h)  # 画面の縦と横の内大きい方
        end_x = start_x + length * math.cos(rad)
        end_y = start_y + length * math.sin(rad)

        line = [[start_x, start_y], [end_x, end_y]]  # radで指定された方向の直線（線分）a
        dis_p = GetDistance(self.rect.centerx, self.rect.centery,  # プレイヤーと自分との距離
                            target.rect.centerx, target.rect.centery)

        for o in all_object.sprites():
            points = o.DetectIntersection(line[0], line[1])
            if points != [0, 0, 0, 0]:  # 交点が存在する
                if enemies_manual.has(o) and o is not self or walls.has(o):
                    dis_o = GetDistance(self.rect.centerx, self.rect.centery,  # オブジェクトと自分との距離
                                        o.rect.centerx, o.rect.centery)
                    if dis_p > dis_o:
                        return False

        return True

    # 砲弾などの移動シミュレーション
    @staticmethod
    def MoveSimulation(o):
        o.kill()  # 作成した時点でグループに入ってしまうので除外
        objects = CopyWorld()  # シミュレーション用にworldを複製
        objects_copy = [x for x in objects.sprites()]  # worldのコピー
        objects.add(o)  # シミュレーション用の世界に対象を追加
        collided_object = 0  # 衝突したオブジェクト
        t = 0  # 繰り返し回数

        while 1:
            # コピーを作成
            o_copy = o

            o.update()
            if not objects.has(o_copy):  # 消滅したとき
                # print(objects, objects_copy)
                # 何と衝突して消滅したかを調べる
                for a in objects_copy:
                    if not a.alive():
                        collided_object = a

                # 座標を記録
                (x, y) = (o_copy.x, o_copy.y)

                break

            t += 1

        # シミュレーション用worldを削除
        for a in objects.sprites():
            a.kill()

        if collided_object:  # 戦車や砲弾と衝突したとき
            return [collided_object, [x, y]]

        else:  # 対象の他に消滅した物体が無ければ壁と衝突したと判定
            # 消滅した地点から最も近い壁を返す
            result = Wall("../../images/wall.png", -1, -1)
            result.kill()
            for wall in walls.sprites():
                if GetDistance(result.rect.centerx, result.rect.centery, x, y) \
                        > GetDistance(wall.rect.centerx, wall.rect.centery, x, y):
                    result = wall

            return [result, [x, y]]

    # 外壁で反射できるかどうかの判定
    def ReflectionOuterWall(self):

        UpdateFalseImage()  # 虚像の位置を更新

        # 虚像のplayerを取得
        players = []
        for o in false_image.sprites():
            if type(o) is Player:
                players.append(o)

        # 外壁での反射で狙えるかの判定
        # enemy_tanks = enemies.sprites() + [x for x in false_image if type(x) is Enemy]
        rad = None
        # print(enemy_tanks)
        for p in players:
            flag = 1
            for o in innerwalls.sprites():
                # print(self.rect.center, p.rect.center)
                points = o.DetectIntersection(self.rect.center, p.rect.center)  # 内壁の虚像の内，プレイヤーとプレイヤーの虚像を結んだ直線と交わるか判定
                # print(points)

                if points != [0, 0, 0, 0]:  # 交わるとき
                    flag = 0
                    break

            if flag:  # 外壁で反射した後、内壁の虚像に当たらないとき
                rad = GetCannonAngle(p.rect.x, p.rect.y, self.x, self.y)
                break
            else:  # 外壁で反射した後，内壁に当たるとき
                rad = None

        return rad

    # 壁で反射できるかどうかの判定（内壁・外壁）
    def ReflectionWall(self, x, y):
        # 引数の示す座標に疑似プレイヤーオブジェクトを配置
        width = player.sprite.rect.width / 2
        height = player.sprite.rect.height / 2
        Player.containers = all_object
        p = Player("../../images/tank_0.png", x - width, y - height, 1)
        Player.containers = all_object, player

        # 自分からn方向への直線を得る（始点と終点で定義）（終点は始点からw×2先の点）
        line_list = []  # 直線のリスト
        rad_player = GetCannonAngle(x, y, self.rect.centerx, self.rect.centery)  # 自分とプレイヤーとの角度
        rad_player -= math.pi * 0.5
        parts = 36
        length = max(w, h)  # 画面の縦と横の内大きい方
        start_x, start_y = self.rect.center
        for r in [rad_player + math.pi * x / parts for x in range(1, parts)]:
            end_x = start_x + 2 * length * math.cos(r)
            end_y = start_y + 2 * length * math.sin(r)

            line_list.append([[start_x, start_y], [end_x, end_y]])  # リストに追加

        # 壁を自分から近い順に並び替え
        objects = {}
        for o in all_object.sprites():
            if o is not self:
                if walls.has(o) or enemies_manual.has(o):
                    objects.setdefault(o, GetDistance(self.rect.centerx, self.rect.centery, o.rect.centerx,
                                                      o.rect.centery))  # enemyとwallを追加

        objects_sorted = sorted(objects.items(), key=lambda a: a[1])  # プレイヤーとの距離で昇順に並び替え

        # それぞれの壁について
        L = 1000  # 十分大きい数
        reflected_line_list = []  # 1回反射させた直線のリスト
        for o in [i[0] for i in objects_sorted]:
            # n方向の直線と交わるか判定
            i = 0
            while i < len(line_list):
                line = line_list[i]
                # 交われば直線を反転させる（交点を始点,終点は対称移動で得る）
                points = o.DetectIntersection(line[0], line[1])
                if points != [0, 0, 0, 0]:  # 交点が存在する
                    if walls.has(o):  # 交点の存在するオブジェクトが壁の時
                        points_dis = [GetDistance(self.rect.centerx, self.rect.centery, x[0], x[1])
                                      if x != 0 else L for x in points]  # 交点と自分との距離を求める
                        points_dis_sorted = sorted(points_dis)  # 昇順に並び替え

                        # 最も近い交点で反射
                        p_i = points_dis.index(points_dis_sorted[0])  # 最も近い交点のインデックス
                        reflect_point = points[p_i]
                        if p_i == 1 or p_i == 3:  # 壁の左右のどちらかで反射する場合
                            reflected_line = [reflect_point, GetLineSymmetricPoint(line[1], reflect_point[0], None)]
                        else:  # 壁の上下で反射する場合
                            reflected_line = [reflect_point, GetLineSymmetricPoint(line[1], None, reflect_point[1])]

                        line_list.remove(line)  # 反射前の直線のリストから削除
                        reflected_line_list.append(reflected_line)  # リストに追加

                    else:  # 交点の存在するオブジェクトが敵の時
                        line_list.remove(line)  # 反射前の直線のリストから削除

                else:  # 交点が存在しない場合
                    i += 1

            # すべての直線を一度反転させたら終了
            if len(line_list) == 0:
                break

        # 反転させた直線について,プレイヤーと交わる物を得る
        Shot_line_list = []
        for line in reflected_line_list:
            points = p.DetectIntersection(line[0], line[1])  # プレイヤーとの交点を求める
            if points != [0, 0, 0, 0]:  # 交点が存在するとき
                player_dis = GetDistance(player.sprite.rect.centerx, player.sprite.rect.centery,
                                         line[0][0], line[0][1])  # プレイヤーと反射点の距離
                # その中からエネミーや壁に交わる物を除外
                flag = 1
                for o in [x for x in all_object.sprites() if innerwalls.has(x) or enemies_manual.has(x)]:
                    # 交点が存在し，反射点との距離がプレイヤーとのよりも短い場合
                    if o.DetectIntersection(line[0], line[1]) != [0, 0, 0, 0] \
                            and player_dis > GetDistance(o.rect.centerx, o.rect.centery, line[0][0], line[0][1]):
                        flag = 0
                if flag:
                    Shot_line_list.append(line)  # リストに追加
                    # print(line)

        # 疑似プレイヤーオブジェクトを削除
        p.kill()

        # 角度を返す
        if len(Shot_line_list) > 0:  # リストが空でないとき
            return GetCannonAngle(Shot_line_list[0][0][0], Shot_line_list[0][0][1], self.rect.centerx,
                                  self.rect.centery)
        else:  # リストが空の時
            return None

    # 敵戦車弾除けベクトル(法線ベクトル)返還
    def CannonDodge(self, c):
        # 感知範囲との接触判定
        if self.serch.collidepoint(c.x, c.y):
            # 近づく弾かどうか
            if GetDistance(self.rect.centerx, self.rect.centery, c.x, c.y) > GetDistance(self.rect.centerx,
                                                                                         self.rect.centery, c.x + c.dx,
                                                                                         c.y + c.dy):
                # 法線＝(c.dy/c.dx, -1) or c.dxが0のとき(1,0)
                if c.dx == 0:
                    nx = -1
                    ny = 0
                else:
                    nx = c.dy / c.dx
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
                dx = math.copysign(self.v, wt_x)
            else:
                dy = math.copysign(self.v, wt_y)
            return dx, dy, GetDistance(self.x, self.y, w.x, w.y) / 45
        else:
            return -1, -1, -1

    # target（座標）までの経路的な距離が近くなるような方向を求める
    def GetPathVelocity(self, target):
        # 自分の周囲のブロックを検査し，最も経路的な距離が短くなるようなブロックを求める
        result = [GetPathDistance(self.rect.center, target.rect.center), self.rect.center]  # 経路的な距離・座標
        m = Map.m_size
        for delta in [(-m, 0), (0, m), (m, 0), (0, -m), (-m, -m), (m, m), (-m, m), (m, -m)]:
            x = self.rect.centerx + delta[0]
            y = self.rect.centery + delta[1]
            dis = GetPathDistance([x, y], target.rect.center)

            if result[0] > dis != math.inf:  # 現在地よりも経路的な距離が短い場合
                result = [dis, [x, y]]

        # 求めたブロックへの方向ベクトルを計算
        dx = (result[1][0] - self.rect.centerx) / m
        dy = (result[1][1] - self.rect.centery) / m

        if dx == 0 and dy == 0:  # 現在地が経路的な距離が最も近い
            return 0, 0
        else:  # 経路的な距離が短くなるような方向ベクトルを返す
            return dx, dy


# 砲弾
class Cannon(MovingObject):

    def __init__(self, *args, dx, dy, **kwargs):
        super().__init__(*args, **kwargs)
        self.dx = dx  # x方向速度
        self.dy = dy  # y方向速度
        self.bounds = 0  # 反射回数

    # 砲弾の振る舞いの管理
    def update(self):
        # 当たり判定
        result = self.DetectCollision()
        # print(result)  # デバッグ用

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


class TankEnv(gym.Env):
    (w, h) = (800, 600)  # 画面サイズ

    (x_target, y_target) = (0, 0)  # 目標位置

    Enemy_num = 3  # 敵戦車の数
    Enemy_pos_manual = [0] * (2 * Enemy_num)  # 各敵戦車の位置を記録するリスト
    Enemy_pos_learn = [0] * (2 * Enemy_num)

    distance_matrix = 0  # 経路的な距離行列

    # pygameの準備
    pygame.init()  # pygame初期化
    pygame.display.set_mode((w, h), 0, 32)  # 画面設定
    pygame.display.set_caption("TANK GAME")
    screen = pygame.display.get_surface()

    # フォント
    font = pygame.font.SysFont(None, 80)
    text1 = font.render(" Reinforcement Learning \nEnemies Win ", True, (255, 255, 0))
    text2 = font.render(" Manual Win", True, (255, 64, 64))

    font2 = pygame.font.SysFont(None, 80)
    text_ready = font2.render("Ready...?", True, (255, 255, 255))

    font3 = pygame.font.SysFont(None, 35)
    text_move = font3.render("move to WASD or Arrow Key", True, (255, 255, 255))
    text_click = font3.render("click to START", True, (255, 255, 255))

    # グループの準備
    player = pygame.sprite.GroupSingle(None)
    enemies_manual = pygame.sprite.Group()
    enemies_learn = pygame.sprite.Group()
    cannons = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    innerwalls = pygame.sprite.Group()
    outerwalls = pygame.sprite.Group()
    all_object = pygame.sprite.RenderUpdates()
    false_image = pygame.sprite.Group()

    # グループ分け
    Player.containers = all_object, player
    Enemy_Manual.containers = all_object, enemies_manual
    Enemy_Learn.containers = all_object, enemies_learn
    Cannon.containers = all_object, cannons
    Wall.containers = all_object, walls
    InnerWall.containers = all_object, walls, innerwalls
    OuterWall.containers = all_object, walls, outerwalls

    def __init__(self):
        super().__init__()
