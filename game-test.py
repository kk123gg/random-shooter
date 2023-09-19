import pygame
import time
from datetime import datetime as dt
from datetime import timedelta as td
from random import randint


class Monster:
    id = 0

    @classmethod
    def get_id(cls):
        Monster.id += 1
        return Monster.id

    def __init__(self, level: int):
        self.id = Monster.get_id()

        self.level = level

        if self.level < 3:
            self.stationary = True
        else:
            self.stationary = False
            self.velocity = level
            self.move_start = randint(0, Game.size()[0]/2)
            self.move_end = self.move_start + Game.size()[0]/2

        self.width = pygame.image.load('monster.png').get_width()
        self.height = pygame.image.load('monster.png').get_height()

        self.bullet_width = pygame.image.load('coin.png').get_width()
        self.bullet_height = pygame.image.load('coin.png').get_height()

        self.x = randint(0, Game.size()[0] - self.width)
        self.y = randint(-1000, 0 - self.height)

        self.bullets = []
        self.bullet_speed = level

        self.count = -1
        self.time = dt.now().second

    def spawn(self):
        if self.y + self.height < 0:
            return

        self.x = randint(0, Game.size()[0] - self.width)
        self.y = randint(-1000, 0 - self.height)

    def move(self):
        if self.y < 0:
            self.y += 1
            return

        if not self.stationary:
            self.x += self.velocity
            if self.velocity < 0:
                self.x = max(self.x, self.move_start)
            else:
                self.x = min(self.x, self.move_end)
            if self.x == self.move_start or self.x == self.move_end:
                self.velocity = -self.velocity

    def shoot(self):
        if self.y < 0:
            return

        # Shoot every 5 seconds
        if self.count == -1:
            self.bullets.append([self.x + self.width/2 - self.bullet_width/2, self.y + self.height])
            self.count = 0
            return

        if dt.now().second != self.time:
            self.time = dt.now().second
            self.count += 1
        
        if self.count == 5:
            self.bullets.append([self.x + self.width/2 - self.bullet_width/2, self.y + self.height])
            self.count = 0
            
        # Remove bullets that are out of screen
        remove_bullets = []
        for bullet in self.bullets:
            if bullet[1] > Game.size()[1]:
                remove_bullets.append(bullet)
        
        for bullet in remove_bullets:
            self.bullets.remove(bullet)


class Player:
    def __init__(self):
        self.lives = 5

        self.width = pygame.image.load('robot.png').get_width()
        self.height = pygame.image.load('robot.png').get_height()

        self.bullet_width = pygame.image.load('coin.png').get_width()
        self.bullet_height = pygame.image.load('coin.png').get_height()

        self.x = Game.size()[0]/2 - self.width/2
        self.y = Game.size()[1]/2 - self.height/2

        self.to_left = False
        self.to_right = False
        self.to_up = False
        self.to_down = False
        self.shooting = False

        self.velocity = 5
        self.bullet_speed = 5

        self.bullets = []

        self.last_death = None
    
    def spawn(self):
        # Add death protection for 1 second
        if self.last_death != None and dt.now() < self.last_death + td(seconds=1):
            return
        
        self.last_death = dt.now()

        self.x = Game.size()[0]/2 - self.width/2
        self.y = Game.size()[1]/2 - self.height/2

        self.lives -= 1

    def move(self):
        if self.to_left:
            self.x -= self.velocity
            self.x = max(0, self.x)
        if self.to_right:
            self.x += self.velocity
            self.x = min(self.x, Game.size()[0] - self.width)
        if self.to_up:
            self.y -= self.velocity
            self.y = max(0, self.y)
        if self.to_down:
            self.y += self.velocity
            self.y = min(self.y, Game.size()[1] - self.height)

    def shoot(self):
        if self.shooting:
            self.bullets.append([self.x + self.width/2 - self.bullet_width/2, self.y - self.bullet_height/2])
            self.shooting = False

        # Remove bullets that are out of screen
        remove_bullets = []
        for bullet in self.bullets:
            if bullet[1] + self.bullet_height < 0:
                remove_bullets.append(bullet)
        
        for bullet in remove_bullets:
            self.bullets.remove(bullet)


class LifePack:
    def __init__(self):
        self.width = pygame.image.load('door.png').get_width()
        self.height = pygame.image.load('door.png').get_height()

        self.spawn()

    def spawn(self):
        self.x = randint(0, Game.size()[0] - self.width)
        self.y = -100
        self.drop = False
    
    def move(self):
        if self.drop:
            self.y += 1
        
        if self.y > Game.size()[1]:
            self.spawn()


class Game:
    @classmethod
    def size(cls):
        return 1024, 768

    def __init__(self):
        pygame.init()

        self.width = Game.size()[0]
        self.height = Game.size()[1]

        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Shooter')

        self.robot = pygame.image.load('robot.png')
        self.monster = pygame.image.load('monster.png')
        self.coin = pygame.image.load('coin.png')
        self.door = pygame.image.load('door.png')

        self.clock = pygame.time.Clock()
        
        self.start_screen()
        self.new_game()
        self.main_loop()

    def start_screen(self):
        font = pygame.font.SysFont('Arial', 30)
        text = font.render('Press ENTER to start the game', True, (255, 0, 0))

        while True:
            self.window.fill((0, 0, 0))
            self.window.blit(text, (self.width/2 - text.get_width()/2, self.height/2 - text.get_height()/2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()

                    if event.key == pygame.K_RETURN:
                        self.window.fill((128, 128, 128))
                        text1 = font.render('Kill:', True, (255, 0, 0))
                        text2 = font.render('X to shoot', True, (255, 0, 0))
                        text3 = font.render('F2 for new game', True, (255, 0, 0))
                        text4 = font.render('ESC to quit', True, (255, 0, 0))

                        self.window.blit(text1, (self.width/2 - text1.get_width(), self.height/4 - text1.get_height()/2))
                        self.window.blit(self.monster, (self.width/2, self.height/4 - self.monster.get_height()/2))
                        self.window.blit(text2, (self.width/2 - text2.get_width()/2, self.height/2 - text2.get_height()/2))
                        self.window.blit(text3, (self.width/2 - text3.get_width()/2, self.height/2 + text3.get_height()/2))
                        self.window.blit(text4, (self.width/2 - text4.get_width()/2, self.height/2 + text4.get_height()*3/2))

                        pygame.display.flip()
                        time.sleep(3)
                        return

    def new_game(self):
        self.score = 0
        self.kills = 0

        self.player = Player()
        self.monsters = [Monster(1)]
        self.life_pack = LifePack()

    def main_loop(self):
        while True:
            self.check_events()
            self.move()
            self.shoot()
            self.check_hit()
            self.draw_window()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_F2:
                    self.new_game()

                if event.key == pygame.K_LEFT:
                    self.player.to_left = True
                if event.key == pygame.K_RIGHT:
                    self.player.to_right = True
                if event.key == pygame.K_UP:
                    self.player.to_up = True
                if event.key == pygame.K_DOWN:
                    self.player.to_down = True

                if event.key == pygame.K_x:
                    self.player.shooting = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.to_left = False
                if event.key == pygame.K_RIGHT:
                    self.player.to_right = False
                if event.key == pygame.K_UP:
                    self.player.to_up = False
                if event.key == pygame.K_DOWN:
                    self.player.to_down = False

    def move(self):
        self.player.move()

        for monster in self.monsters:
            monster.move()

        self.life_pack.move()

    def shoot(self):
        self.player.shoot()

        for monster in self.monsters:
            monster.shoot()

    def check_hit(self):
        # Check if player hits a monster
        for bullet in self.player.bullets:
            for monster in self.monsters:
                if monster.y + monster.height < 0:
                    continue
                if ((monster.x <= bullet[0] <= monster.x + monster.width
                        or monster.x <= bullet[0] + self.player.bullet_width <= monster.x + monster.width)
                    and monster.y <= bullet[1] + self.player.bullet_height <= monster.y + monster.height):
                    monster.spawn()
                    self.score += 1
                    if self.score == 3 or self.score % 5 == 0:
                        self.add_monster()
                    if self.score % 15 == 0:
                        self.life_pack.drop = True

        # Check if a monster hits the player
        for monster in self.monsters:
            for bullet in monster.bullets:
                if ((self.player.x <= bullet[0] <= self.player.x + self.player.width
                        or self.player.x <= bullet[0] + monster.bullet_width <= self.player.x + self.player.width)
                    and (self.player.y <= bullet[1] <= self.player.y + self.player.height
                        or self.player.y <= bullet[1] + monster.bullet_height <= self.player.y + self.player.height)):
                    self.player.spawn()

            if ((monster.x <= self.player.x <= monster.x + monster.width
                    or monster.x <= self.player.x + self.player.width <= monster.x + monster.width)
                and (monster.y <= self.player.y <= monster.y + monster.height
                    or monster.y <= self.player.y + self.player.height <= monster.y + monster.height)):
                self.player.spawn()

        # Check if player collects the life pack
        if ((self.player.x <= self.life_pack.x <= self.player.x + self.player.width
                or self.player.x <= self.life_pack.x + self.life_pack.width <= self.player.x + self.player.width)
            and (self.player.y <= self.life_pack.y <= self.player.y + self.player.height
                or self.player.y <= self.life_pack.y + self.life_pack.height <= self.player.y + self.player.height)):
            self.player.lives += 1
            self.life_pack.spawn()

        # Game over if 0 lives left
        if self.player.lives <= 0:
            self.game_over()

    def draw_window(self):
        self.window.fill((128, 128, 128))

        self.window.blit(self.robot, (self.player.x, self.player.y))

        for monster in self.monsters:
            self.window.blit(self.monster, (monster.x, monster.y))

        for i, bullet in enumerate(self.player.bullets):
            self.window.blit(self.coin, (bullet[0], bullet[1]))
            self.player.bullets[i][1] -= self.player.bullet_speed

        for monster in self.monsters:
            for i, bullet in enumerate(monster.bullets):
                self.window.blit(self.coin, (bullet[0], bullet[1]))
                monster.bullets[i][1] += monster.bullet_speed

        self.window.blit(self.door, (self.life_pack.x, self.life_pack.y))

        font = pygame.font.SysFont('Arial', 20)
        lives_text = font.render(f'Lives: {self.player.lives}', True, (255, 0, 0))
        score_text = font.render(f'Score: {self.score}', True, (255, 0, 0))

        self.window.blit(lives_text, (0, 0))
        self.window.blit(score_text, (self.width - score_text.get_width(), 0))

        pygame.display.flip()

        self.clock.tick(60)

    def add_monster(self):

        level = min(5, self.score // 10 + 1)
        self.monsters.append(Monster(level))

    def game_over(self):
        font1 = pygame.font.SysFont('Arial', 50)
        font2 = pygame.font.SysFont('Arial', 30)
        text1 = font1.render('Game Over', True, (255, 0, 0))
        text2 = font2.render('Press F2 to start a new game', True, (255, 0, 0))

        self.window.blit(text1, (self.width/2 - text1.get_width()/2, self.height/2 - text1.get_height()))
        self.window.blit(text2, (self.width/2 - text2.get_width()/2, self.height/2))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()

                    if event.key == pygame.K_F2:
                        self.new_game()
                        return


if __name__ == '__main__':
    Game()