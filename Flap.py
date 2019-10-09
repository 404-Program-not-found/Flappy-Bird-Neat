import random
import pygame
import sys
import neat
import os


class Game:
    def __init__(self):
        self.list = []
        self.gravity = 0.25
        self.fps = 60
        self.vec = pygame.math.Vector2
        pygame.init()
        pygame.display.init()
        pygame.mixer.init()
        self.width, self.height = 144 * 3, 206 * 3
        self.playSurface = pygame.display.set_mode([self.width, self.height])
        pygame.display.set_caption('Flappy AI')
        self.SpriteSheeet = pygame.image.load('Flappy_Bird_Spritesheet.png').convert()
        self.Green = [0, 255, 0]
        self.Red = [255, 0, 0]
        self.Black = [0, 0, 0]
        self.White = [255, 255, 255]

    def new(self, genomes, config):
        self.wall = []
        self.list = []
        self.genomes = genomes
        self.config = config
        self.nets = []
        self.ge = []
        for genomeid, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            self.nets.append(net)
            g.fitness = 0
            self.ge.append(g)
            self.list.append(net)
        self.walls = pygame.sprite.Group()
        self.Clock = pygame.time.Clock()
        self.fpsController = pygame.time.Clock()
        self.stop = False
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.flappy = pygame.sprite.Group()
        self.walls_upper = walls_upper(self)
        self.wall.append(self.walls_upper)
        self.walls.add(self.walls_upper)
        self.walls_lower = walls_lower(self, self.walls_upper.y_level)
        self.walls.add(self.walls_lower)
        self.wall.append(self.walls_lower)
        self.ground = Floor(self)
        for i in range(0, len(self.list)):
            self.player = Bird(self, self.list[i])
            self.all_sprites.add(self.player)
            self.flappy.add(self.player)
        self.image = pygame.Surface([114 * 3, 206 * 3])
        self.update_count = 0
        self.run()

    def run(self):
        self.stop = False
        self.update()

    def update(self):
        self.playSurface.fill(self.Black)
        while not self.stop:
            kill_list = []
            self.Clock.tick(self.fps)
            if len(self.flappy) == 0:
                self.stop = True
            pipe_ind = 0
            if self.wall[0].pos.x < -40:
                self.wall.pop(0)
                self.wall.pop(0)
            if len(self.walls) > 1 and 114 * 3 / 4 > self.wall[0].pos.x:
                pipe_ind = 1
            for x, bird in enumerate(self.flappy):
                if pygame.sprite.collide_mask(bird, self.wall[0]) or pygame.sprite.collide_mask(bird,
                                                                                                    self.wall[1]):
                    self.ge[x].fitness -= 1
                    pygame.sprite.Sprite.kill(bird)
                    kill_list.append(x)
                elif bird.pos.y >= 559:
                    self.ge[x].fitness -= 1
                    pygame.sprite.Sprite.kill(bird)
                    kill_list.append(x)
                elif bird.pos.y <= 48:
                    self.ge[x].fitness -= 1
                else:
                    self.ge[x].fitness += 0.1
            kill_list.reverse()
            for kill_id, kill in enumerate(kill_list):
                self.ge.pop(kill)
                self.nets.pop(kill)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop = True
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_EQUALS:
                        self.fps += 10
                    if event.key == pygame.K_MINUS:
                        self.fps -= 10
            self.all_sprites.update(self.wall[0])
            if self.update_count != 280:
                self.update_count += 1
            else:
                for g in self.ge:
                    g.fitness += 5
                self.update_count = 0
                self.walls_upper = walls_upper(self)
                self.wall.append(self.walls_upper)
                self.walls.add(self.walls_upper)
                self.walls_lower = walls_lower(self, self.walls_upper.y_level)
                self.walls.add(self.walls_lower)
                self.wall.append(self.walls_lower)
            self.walls.update()
            self.draw()

    def draw(self):
        self.image.blit(self.SpriteSheeet, (0, 0), (0, 50, 144, 206))
        self.playSurface.blit(pygame.transform.scale(self.image, (144 * 9, 206 * 9)), (0, 0))
        self.walls.draw(self.playSurface)
        self.all_sprites.draw(self.playSurface)
        self.ground.update()
        pygame.display.update()


class Floor():
    def __init__(self, game):
        self.x = 110
        self.game = game
        self.image = pygame.Surface([114 * 5, 56 * 2])
        self.ground = pygame.Surface([168, 56])
        self.ground.set_colorkey((255, 255, 255))
        self.ground.blit(self.game.SpriteSheeet, (0, 0), (292, 0, 168, 56))
        self.ground = pygame.transform.scale(self.ground, (114 * 5, 56 * 2))

    def update(self):
        self.rel_x = self.x % self.image.get_rect().width
        self.game.playSurface.blit(self.ground, (self.rel_x - self.ground.get_rect().width, 206 * 3 - 50))
        if self.rel_x < 114 * 3 + 80:
            self.game.playSurface.blit(self.ground, (self.rel_x, 206 * 3 - 50))
        self.x -= 1.5


class Bird(pygame.sprite.Sprite):
    def __init__(self, game, input):
        self.input = input
        self.mainstuff = game
        self.vec = pygame.Vector2
        self.all_sprite = self.mainstuff.all_sprites
        self.bird = pygame.Surface((19, 14.5))
        self.image = pygame.Surface((19 * 3, 14.5 * 3))
        self.rect = self.image.get_rect()
        pygame.sprite.Sprite.__init__(self)
        self.rect.center = (114 * 3 / 4, 206 * 3 / 2)
        self.pos = self.vec(114 * 3 / 4, 206 * 3 / 2)
        self.vel = self.vec(0, 0)
        self.bird_image = [(3, 490, 20, 15), (31, 490, 20, 15), (59, 490, 20, 15)]
        self.foo = 1
        self.foo2 = 0
        self.angle = 0

    def jump(self):
        self.vel.y = -5

    def update(self, walls):
        self.ypos = walls.y_level
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.bird.blit(self.mainstuff.SpriteSheeet, (0, 0), (self.bird_image[self.foo]))
        self.bird.set_colorkey((255, 255, 255))
        self.acc = self.vec(0, self.mainstuff.gravity)
        keys = pygame.key.get_pressed()
        output = self.input.activate((self.pos.y, self.ypos, abs(self.ypos + 110), abs(self.pos.x - walls.pos.x)))
        if output[0] > 0.5:
            self.jump()
        if keys[pygame.K_KP_PLUS]:
            self.mainstuff.gravity += 0.01
        elif keys[pygame.K_KP_MINUS]:
            self.mainstuff.gravity -= 0.01
        if self.rect.midtop[1] <= 0:
            self.vel.y = 0
            self.pos.y = 48
        elif not self.pos.y > 559:
            self.vel.y += self.acc.y
            self.pos.y += self.vel.y + 0.2 * self.acc.y
        else:
            self.death()

        self.rect.midbottom = self.pos
        self.image.blit(pygame.transform.scale(self.bird, (20 * 3, 15 * 3)), (0, 0))
        pygame.mask.from_surface(self.image)
        if self.foo2 != 15:
            self.foo2 += 1
        else:
            self.foo = self.foo + 1 if self.foo < 2 else 0
            self.foo2 = 0

    def death(self):
        self.kill()
        if len(self.mainstuff.flappy) == 0:
            self.mainstuff.stop = True


class WallsBasic(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.y_level = random.randint(50, 350)
        self.vec = pygame.Vector2
        self.pipe = pygame.Surface((26, 160))
        self.image = pygame.Surface((26 * 3, 160 * 3))
        self.game = game
        self.all_sprites = game.all_sprites
        self.rect = self.image.get_rect()

    def update_walls(self):
        self.image.set_colorkey((0, 0, 0))

        self.pipe.blit(self.game.SpriteSheeet, (0, 0), self.area)
        self.pipe.set_colorkey((255, 255, 255))
        self.image.blit(pygame.transform.scale(self.pipe, (26 * 3, 160 * 3)), (0, 0))
        self.pos.x -= 1.5


class walls_lower(WallsBasic):
    def __init__(self, game, y_level):
        level = 110
        super().__init__(game)
        self.rect.midtop = self.vec(114 * 3 + 50, y_level + level)
        self.pos = self.vec(114 * 4 + 50, y_level + level)
        self.area = (84, 323, 26, 160)

    def update(self):
        self.update_walls()
        self.rect.midtop = self.pos
        pygame.mask.from_surface(self.image)
        if self.pos.x < -40:
            pygame.sprite.Sprite.kill(self)


class walls_upper(WallsBasic):

    def __init__(self, game):
        super().__init__(game)
        self.rect.midbottom = self.vec(114 * 3 + 50, self.y_level)
        self.pos = self.vec(114 * 4 + 50, self.y_level)
        self.area = (56, 323, 26, 160)

    def update(self):
        self.update_walls()
        self.rect.midbottom = self.pos
        pygame.mask.from_surface(self.image)
        if self.pos.x < -40:
            pygame.sprite.Sprite.kill(self)

        elif self.pos.x == 9.5:
            self.game.score += 1
            print(self.game.score)

def run(config_file):
    maingame = Game()
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(maingame.new, 1000)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    run(config_path)
