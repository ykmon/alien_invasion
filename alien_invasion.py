import sys                                                   # 导入sys模块(退出游戏
from time import sleep
import pygame                                                   # 导入pygame模块(开发游戏
from random import randint

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star

class AlienInvasion:
    """管理游戏资源和行为的类"""
    
    def __init__(self):
        """初始化游戏并创建游戏资源."""
        pygame.init()
        self.settings = Settings()                              # 创建实例
        # 创建一个窗口,赋给属性self.screen的对象是一个'surface','surface'是屏幕的一部分,用于显示游戏元素
        # display.set_mode()返回的'surface'表示整个游戏窗口,激活游戏的动画循环后,没经过一次循环都会自动重绘这个'surface'
            
            # 按照settings设置的分辨率显示屏幕
        self.screen = pygame.display.set_mode((     
            self.settings.screen_width, self.settings.screen_height))  
        
        #     # 全屏显示
        # self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        
        pygame.display.set_caption("外星人入侵")
        
        # 创建一个用于存储游戏统计信息的实例
        #   并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)                                  # 创建Ship实例
        self.bullets = pygame.sprite.Group()                    # 创建存储子弹的编组
        self.aliens = pygame.sprite.Group()                     # 创建存储外星人的编组
        self.stars = pygame.sprite.Group()
        
        self._create_group_star()
        self._create_fleet()
        
        # 创建Play按钮
        self.play_button = Button(self,"Play")
        
        # 设置背景色
        self.bg_color = (self.settings.bg_color)
        
    def run_game(self):                                         # 这个游戏由run_game()控制
        """开始游戏的主循环"""
        while True:                                             # '事件'循环
            self._check_events()                                # 调用的方法在后面定义
            if self.stats.game_active:
                self.ship.update()                                  # ship没有父类
                self._update_bullets()
                self._update_aliens()
            self._update_screen()                               # 更新屏幕永远是最后一步
            
            
    def _check_events(self):                                # 辅助方法的名称用_下划线打头
        """响应按键和鼠标事件"""
        for event in pygame.event.get():                    # pygame.event.get()返回一个列表,其中包含它在上一次被调用后发生的所有'事件'(所有的键盘鼠标'事件'
            if event.type == pygame.QUIT:                   # 玩家单机关闭按钮,调用sys.exit()退出游戏
                sys.exit()
            elif event.type == pygame.KEYDOWN:              # event关键词都是黑盒函数
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    def _check_play_button(self, mouse_pos):
        """在玩家单机Play时开始"""
        if self.play_button.rect.collidepoint(mouse_pos):
            """玩家单击Play按钮时开始新游戏"""
            button_clicked = self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.stats.game_active:   # 游戏仅在game_active为False时开始
                # 重置游戏设置
                self.settings.initialize_dynamic_settings()
                # 重置游戏统计信息
                self.stats.reset_stats()
                self.stats.game_active = True
                self.sb.prep_score()
                # 清空余下的外星人和子弹
                self.aliens.empty()
                self.bullets.empty()
                # 创建一群新的外星人并让飞船居中
                self._create_fleet()
                self.ship.center_ship()
                # 隐藏鼠标光标
                pygame.mouse.set_visible(False)
            
    def _check_keydown_events(self,event):
        """响应按键"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    def _fire_bullet(self):
        """创建一颗子弹,并将其加入编组bullets中"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():                  # 复制子弹编组,遍历每一个检查位置
            if bullet.rect.bottom <= 0:                     # 是否从屏幕顶端消失
                self.bullets.remove(bullet)                 # 把这些子弹从编组删除
        print(len(self.bullets))                            # 显示屏幕上有多少子弹
    
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        # 检查是否有子弹击中了外星人
        #   如果是 就删除相应的子弹和外星人
        # groupcollide()返回的是键对值
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
        if not self.aliens:                                 # 空编组相当于False
            # 删除现有的子弹并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings._increase_speed()
    
    def _update_aliens(self):
        """检查是否有外星人在屏幕边缘并更新整群位置"""
        self._check_fleet_edges()
        self.aliens.update()
        # 检测外星人和飞船之间的碰撞
        # spritecollideany() 接受两个实参,一个'精灵'和一个'编组'
        #   ,检查'编组'(self.aliens)是否有成员与'精灵'碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens): # 没有发生碰撞的话返回None 如果碰撞了就返回'编组'(self.aliens)
            self._ship_hit()
        # 检查是否有外星人到达屏幕底端
        self._check_aliens_bottom()
            
    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ships_left > 0:
            # 将ship_left(飞船生命)减1
            self.stats.ships_left -= 1
            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            # 创建一群新的外星人,并将飞船放到屏幕低端的中央
            self._create_fleet
            self.ship.center_ship()
            # 暂停0.5秒
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)  # 显示鼠标光标
        
    def _create_fleet(self):
        """创建外星人群"""
        # 创建一个外星人并计算一行可容纳多少个外星人.
        # 外星人的间距为外星人的宽度    ## 这一部分只获取属性,不添加到编组里
        alien = Alien(self)
        # 计算屏幕内一行可以容纳多少个外星人
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # 计算屏幕可以容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)
        
        # 嵌套循环 逐行挨个生成每个外星人的位置
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
            
    def _create_alien(self,alien_number, row_number):
        """创建一个外星人并将其放入指定行"""
        alien = Alien(self)                                    # 创建外星人
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number # 循环计算递增外星人的x坐标
        alien.y = alien_height + 2 * alien_height * row_number
        alien.rect.x = alien.x                                 # 计算完之后设置坐标
        alien.rect.y = alien.y
        self.aliens.add(alien)                                 # 加入编组
    
    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕边缘"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break
        
    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():                    # 遍历外星人群
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """将整群外星人下移,并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _create_group_star(self):
        star = Star(self)
        star_width, star_height = star.rect.size
        available_space_x = self.settings.screen_width - (2 * star_width)
        star_column = available_space_x // (2 * star_width)
        
        available_space_y = self.settings.screen_height - (2 * star_height)
        star_row = available_space_y // (2 * star_height)
        
        for row_star in range(star_row):
            for column_star in range(star_column):
                rand_num = randint(-3,3)
                self._create_star(column_star, row_star, rand_num)
                
    def _create_star(self,star_column, star_row, rand_num = ''):
        star = Star(self)
        star_width = star.rect.width
        star_height = star.rect.height
        star.x = star_width + rand_num * star_width * star_column 
        star.y = star_height + rand_num * star_height * star_row 
        star.rect.x = star.x
        star.rect.y = star.y
        self.stars.add(star)
    
    def _update_screen(self):
        """更新屏幕上的图像,并切换到新屏幕"""
        self.screen.fill(self.bg_color)
        self.stars.draw(self.screen)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        # 如果游戏处于非活动状态就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()
        # 让最近绘制的屏幕可见
        pygame.display.flip()                               # 每次while循环都绘制一个空屏幕并擦去旧屏幕(移动游戏元素时,pygame.display.flip()将不断更新屏幕
            
            
            
if __name__ == '__main__':                                      # 仅当直接运行该文件时,它才会执行
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()                                               