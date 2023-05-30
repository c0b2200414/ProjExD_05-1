import sys
import time
import random

import pygame as pg


WIDTH = 1600  # 画面の横幅
HEIGHT = 900  # 画面の縦幅


class Player(pg.sprite.Sprite):
    """
    操作キャラクターに関するクラス
    """
    
    def __init__(self):
        """
        初期化メソッド
        """
        super().__init__()
        self.imgs = [pg.transform.rotozoom(pg.image.load(f"ex05/fig/run{i}.png"), 0, 0.4) for i in range(1, 4)]  # アクションに合わせた画像をすべて読み込む
        self.img = self.imgs[0]  # 描画画像の初期化
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.image = pg.Surface((self.width*3/4, self.height))  # キャラ画像とは別に当たり判定を設定
        pg.Surface.fill(self.image, (100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 174
        self.rect.centerx = WIDTH/2
        self.num_r = 0  # 走行に合わせて周期的に画像を変更するための変数
        self.tmr = 0  # 走行時間を格納する変数
        self.jump = False  # ジャンプ中か否かの変数
        self.jump_tmr = 0  # ジャンプ時間を格納する変数
        self.sliding = False #スライディング中か否かの変数
    
    def update(self, screen: pg.Surface):
        """
        画像を更新，描画するメソッド
        引数：画面Surface
        """
        if self.jump:  # ジャンプ中の動作
            self.tmr = 0
            if self.jump_tmr < 20: 
                self.rect.move_ip(0, -15)
            else:
                self.rect.move_ip(0, 15)
            self.jump_tmr += 1
            if self.jump_tmr >= 40:
                self.jump = False
                self.jump_tmr = 0
            screen.blit(self.img, self.rect)

        elif self.sliding:
            self.image = self.imgs[2]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT-185
            self.sliding_tmr = 0
            screen.blit(self.image, self.rect) #スライディングしているキャラクターを描画
                
        else:  # 走行中の動作
            self.image = pg.Surface((self.width*3/4, self.height))  # キャラ画像とは別に当たり判定を設定
            pg.Surface.fill(self.image, (100, 100, 100))
            self.tmr += 1
            if self.tmr % 5 == 0:  # 画像を0.1秒ごとに切り替え
                self.num_r += 1
                self.img = self.imgs[self.num_r%2]
            self.rect = self.image.get_rect()
            self.rect.bottom = HEIGHT - 174
            self.rect.centerx = WIDTH/2
            screen.blit(self.img, self.rect)


class Object(pg.sprite.Sprite):
    """
    障害物に関するクラス
    """
    
    def __init__(self):
        """
        初期化メソッド
        """
        super().__init__()
        self.image = pg.Surface((50, 100))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 194
        self.rect.left = WIDTH
        
    def update(self, screen: pg.Surface):
        """
        障害物を移動，描画するメソッド
        引数：画面Surface
        """
        self.rect.move_ip(-10, 0)
        screen.blit(self.image, self.rect)
        if self.rect.right < 0:  # 画面左に到達したとき
            self.kill()  # グループ内が増えすぎないようにグループから削除

class Object2(pg.sprite.Sprite):
    """
    障害物2(空中)に関するクラス
    """
    
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((50, 100))
        pg.draw.rect(self.image, (0, 0, 0), pg.Rect(0, 0, 50, 100))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 350
        self.rect.left = WIDTH
        
    def update(self, screen: pg.Surface):
        self.rect.move_ip(-10, 0) #障害物2を動かす
        screen.blit(self.image, self.rect) #障害物2を描画
        if self.rect.right < 0:  # 画面左に到達したとき
            self.kill()  # グループ内が増えすぎないようにグループから削除


class Object_ball(pg.sprite.Sprite):
    """
    柵の上を跳ねるボール状の障害物に関するメソッド
    """
    
    def __init__(self):
        """
        初期化メソッド
        """
        super().__init__()
        self.image = pg.Surface((60, 60))
        pg.draw.circle(self.image, (0, 200, 100), (30, 30), 30)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH, (HEIGHT - 194) // 2)  # 初期位置を画面右上端に設定
        self.vx = -15
        self.vy = 0
        self.tmr = 0  # ボールの落下の時間
        self.bounce = False  # ボールが柵と衝突したか否かを格納する変数
    
    def update(self, screen: pg.Surface):
        """
        ボールを移動，描画するメソッド
        引数：画面Surface
        """
        self.vy = int((self.tmr / 4 ** 2) * 9.8 / 2)  # ボールを水平投射
        if self.rect.bottom >= (HEIGHT - 200):  # 柵との衝突判定
            self.bounce = True
        if self.bounce:
            self.vy *= -1
            self.tmr -= 1
        else:
            self.tmr += 1
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.image, self.rect)
        if self.rect.right <= 0:  # ボールが画面左端に到達したらグループから削除
            self.kill()


class Time:
    """
    経過時間を表示するクラス
    """
    
    def __init__(self):
        """
        初期化メソッド
        """
        self.time = 0
    
    def update(self, screen: pg.Surface, tmr: int):
        """
        時間を更新，描画するメソッド
        引数1：画面Surface
        引数2：経過時間(tick)を格納した変数tmr
        """
        self.time = tmr // 50  # 50tick(1秒)ごとに1加算
        fonto = pg.font.Font(None, 100)
        if self.time % 10 == 0 and self.time != 0:  # 10秒ごとに数字の色を黄色に変化
            txt = fonto.render(f"{self.time}", True, (191, 181, 73)) 
        else:  # それ以外は数字の色を赤で描画
            txt = fonto.render(f"{self.time}", True, (191, 73, 83))
        screen.blit(txt, [100, 100])



def main():
    clock = pg.time.Clock()
    pg.display.set_caption("Run on Fence")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bgs = [pg.transform.rotozoom(pg.image.load("ex05/fig/background.png"), 0, 1.25) for i in range(3)]  # 背景を滑らかに動かすため複数枚読み込む
    fences = [pg.transform.rotozoom(pg.image.load("ex05/fig/fence.png"), 0, 1.25) for i in range(3)]  # 柵を滑らかに動かすために複数枚読み込む
    fence_rect = fences[0].get_rect()  # 柵の大きさを取得する
    tmr = 0
    
    objs = pg.sprite.Group()
    player = Player()
    timer = Time()
    
    while True:
        bg_x = tmr % 3200
        fence_x = (tmr % 160) * 10  # 障害物の進む速度に合わせて移動
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # SPACEキーを押すとジャンプ
                    player.jump = True
                if event.key == pg.K_DOWN:
                    player.sliding = True #下キーでスライディング
            else:
                player.sliding = False
        
        for i in range(len(bgs)):  # 背景画像を複数枚同時に処理
            screen.blit(bgs[i], [WIDTH*i-bg_x, 0])
        for i in range(len(fences)):  # 柵画像を複数枚同時に処理
            screen.blit(fences[i], [WIDTH*i-fence_x, HEIGHT-fence_rect.height])
        
        if tmr % 150 == 0:  # 3~5秒のランダムな間隔で障害物を生成
            n = tmr
            r = random.randint(0, 100)
        if tmr - n  == r and tmr != 0:
            r2 = random.randint(0, 100)
            if r2 <= 10:  # 10%の確率でボール状の障害物
                objs.add(Object_ball())
            elif r2 <= 30:
                objs.add(Object2())
            else:  # 90%の確率で通常の長方形の障害物
                objs.add(Object())
        
        for obj in objs:  # 複数の障害物を同時に処理
            obj.update(screen)
        
        for obj in pg.sprite.spritecollide(player, objs, True):  # キャラの当たり判定と障害物の衝突判定
            time.sleep(2)
            return

        player.update(screen)
        timer.update(screen, tmr)
        pg.display.update()
        tmr += 1
        clock.tick(50)
        
        

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()