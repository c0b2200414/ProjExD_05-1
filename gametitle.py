import sys
import time
import random

import pygame as pg


WIDTH = 1600
HEIGHT = 900


class Player:
    """
    操作キャラクターに関するクラス
    """
    
    def __init__(self):
        self.imgs = [pg.transform.rotozoom(pg.image.load(f"ex05/fig/run{i}.png"), 0, 0.4) for i in range(1, 3)]
        self.num = 1
        self.img = self.imgs[self.num]
        width = self.img.get_width()
        height = self.img.get_height()
        self.image = pg.Surface((width*3/4, height))
        pg.Surface.fill(self.image, (100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 185
        self.rect.centerx = WIDTH/2
        self.num_r = 0
        self.tmr = 0
        self.jump = False
        self.jump_tmr = 0
    
    def update(self, screen: pg.Surface):
        if self.jump:
            if self.jump_tmr < 20: 
                self.rect.move_ip(0, -15)
            else:
                self.rect.move_ip(0, 15)
            self.jump_tmr += 1
            if self.jump_tmr >= 40:
                self.jump = False
                self.jump_tmr = 0
            screen.blit(self.img, self.rect)
                
        else:
            self.tmr += 1
            if self.tmr % 5 == 0:
                self.num_r += 1
                self.img = self.imgs[self.num_r%2]
            screen.blit(self.img, self.rect)


class Object(pg.sprite.Sprite):
    """
    障害物に関するクラス
    """
    
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((50, 100))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 194
        self.rect.left = WIDTH
        
    def update(self, screen: pg.Surface):
        self.rect.move_ip(-10, 0)
        screen.blit(self.image, self.rect)
        if self.rect.right < 0:
            self.kill()


class Time:
    """
    経過時間を表示するクラス
    """
    def __init__(self):
        self.time = 0
    
    def update(self, screen: pg.Surface, tmr: int):
        self.time = tmr // 50
        fonto = pg.font.Font(None, 100)
        if self.time % 10 == 0 and self.time != 0:
            txt = fonto.render(f"{self.time}", True, (191, 181, 73)) 
        else:           
            txt = fonto.render(f"{self.time}", True, (191, 73, 83))
        screen.blit(txt, [100, 100])



def main():
    clock = pg.time.Clock()
    pg.display.set_caption("Run on Fence")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bgs = [pg.transform.rotozoom(pg.image.load("ex05/fig/background.png"), 0, 1.25) for i in range(3)]
    fences = [pg.transform.rotozoom(pg.image.load("ex05/fig/fence.png"), 0, 1.25) for i in range(3)]
    fence_rect = fences[0].get_rect()
    tmr = 0
    
    objs = pg.sprite.Group()
    player = Player()
    timer = Time()
    
    while True:
        bg_x = tmr % 3200
        fence_x = (tmr % 160) * 10
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    player.jump = True
        
        for i in range(len(bgs)):
            screen.blit(bgs[i], [WIDTH*i-bg_x, 0])
        for i in range(len(fences)):
            screen.blit(fences[i], [WIDTH*i-fence_x, HEIGHT-fence_rect.height])
        
        if tmr % 150 == 0:
            n = tmr
            r = random.randint(0, 100)
        if tmr - n  == r:
            objs.add(Object())
        
        for obj in objs:
            obj.update(screen)
        
        for obj in pg.sprite.spritecollide(player, objs, True):
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