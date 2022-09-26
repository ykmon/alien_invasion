import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """管理飞船所发射子弹的类"""
    
    def __init__(self, ai_game):
        """在飞船当前位置创建一个子弹对象"""
        super().__init__()      # super().__init__(),就是继承父类的init方法,同样可以使用super()去继承其他方法.
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        
        # 在(0,0)处创建一个表示子弹的矩形,再设置正确的位置
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop     # 子弹的初始位置位于当前飞船的位置
        
        # 存储用小数表示的子弹位置
        self.y = float(self.rect.y)
    
    def update(self):
        """更新子弹的位置,并删除消失的子弹"""
        # 更新表示子弹位置的小数值
        self.y -= self.settings.bullet_speed
        # 更新表示子弹的rect的位置
        self.rect.y = self.y
            
        
    def draw_bullet(self):
        """在屏幕上绘制子弹"""
        # 在screen上的rect位置绘制color颜色
        pygame.draw.rect(self.screen, self.color, self.rect)