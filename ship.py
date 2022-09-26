import pygame

class Ship:
    """管理飞船的类"""
    
    def __init__(self,ai_game):
        """初始化飞船并设置其初始设置"""
        self.settings = ai_game.settings
        # 加载屏幕图像并获取其外接矩形
        self.screen = ai_game.screen                            # 将屏幕赋给了Ship的而一个属性
        self.screen_rect = ai_game.screen.get_rect()            # get_rect()访问屏幕的属性(让飞船放到屏幕的正确位置
        
        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load('images/ship.bmp')       # pygame.image.load()加载图像
        self.rect = self.image.get_rect()                 # 获取到图像后get_rect()获取相应'surface'的属性'rect'(指定飞船的位置
        
        # 对于每艘新飞船,都将其放在屏幕底部的中央
        self.rect.midbottom = self.screen_rect.midbottom  # 将飞船位置传到屏幕   ##飞船的中底部放在屏幕矩形的中底部
        
        # 让飞船的位置属性x中能存储浮点数值
        self.x = float(self.rect.x)
        
        # 移动标志
        self.moving_right = False
        self.moving_left = False
        
    def update(self):
        """根据移动标志调整飞船的位置"""
        if self.moving_right and self.rect.right < self.screen_rect.right:# 确保飞船在屏幕内才调整self.x
            self.x += self.settings.ship_speed             # 获取settings里的ship_speed
        elif self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        
        # 根据self.x更新rect对象   ## 修改了self.rect的x分量
        self.rect.x = self.x
            
    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image, self.rect)            # 将图像绘制到self.rect指定的位置   ##把bmp图像放到指定位置
        
    def center_ship(self):
        """让飞船在屏幕底端居中"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)