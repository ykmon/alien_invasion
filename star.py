import pygame
from pygame.sprite import Sprite

class Star(Sprite):
    """表示单个星星的类"""
    
    def __init__(self,ai_game):
        """初始化星星并设置其起始位置"""
        super().__init__()
        self.screen = ai_game.screen
        
        self.image = pygame.image.load('images/star.bmp')
        self.rect = self.image.get_rect()
        
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        
        self.x = float(self.rect.x)
        
