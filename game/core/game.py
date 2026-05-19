import pygame
import os
from pathlib import Path

from game.world.map import GameMap
from game.core.camera import Camera
from game.entities.nexus import Nexus
from game.entities.projectile import Projectile
from game.entities.minions import Minion
from game.entities.enemy import Enemy
from game.ui.end_screen import EndScreen
from game.reseau.network import Network


class Game():
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.net = Network()
        self.my_id = self.net.player_id
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.nexuses = pygame.sprite.Group()
        project_root = Path(__file__).parent.parent.parent
        map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")
        self.game_map = GameMap(map_path)
        self.camera = Camera(screen.get_width(), screen.get_height(), self.game_map.map_width, self.game_map.map_height)
        self.collisions_rects = self.game_map.get_collision_rects()
        #Nico ajout team nexus
        self.nexus_r = Nexus(253, 1240, 100, 100, "sprite/nexus_r.png", "blue", hp=1000,)
        self.nexus_v = Nexus(1232, 220, 128, 128, "sprite/nexus_v.png", "red", hp=1000,)
        #Nico fin
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])
        self.player = None
        self.dt = 0
        #Nico spawn minions
        self.spawn_timer = 0
        self.wave_timer = 0
        self.minions_spawned_in_wave = 0
        self.wave_size = 4
        self.is_wave_active = True
        self.blue_minion_img = pygame.image.load("sprite/test_sbire_blue.png").convert_alpha()
        self.red_minion_img = pygame.image.load("sprite/test_sbire_red.png").convert_alpha()
        #fin
    
    def add_entity(self, entity, groups=[]):
        if isinstance(entity, pygame.sprite.Sprite):
            self.all_sprites.add(entity)
            for group in groups:
                group.add(entity)
        else:
            print(f"Attention: {type(entity)} n'est pas un Sprite Pygame !")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_a:
                    proj_data = self.player.attack(self.camera)
                    if proj_data:
                        self.add_entity(proj_data, [self.projectiles])
    
    def update(self):
        self.dt = self.clock.tick(60) / 1000.0
        #Nico Modif 
        self.spawn_timer += self.dt * 1000
        if self.is_wave_active and self.minions_spawned_in_wave < self.wave_size:
            if self.spawn_timer > 800:
                blue_minion = Minion(253, 1240, 32, 32, self.blue_minion_img, "blue")
                self.add_entity(blue_minion, [self.enemies])
                
                red_minion = Minion(1232, 220, 32, 32, self.red_minion_img, "red")
                self.add_entity(red_minion, [self.enemies])
                
                self.minions_spawned_in_wave += 1
                self.spawn_timer = 0
        elif self.minions_spawned_in_wave >= self.wave_size:
            self.is_wave_active = False
            self.wave_timer += self.dt
            if self.wave_timer > 30: # 30 secondes
                self.wave_timer = 0
                self.minions_spawned_in_wave = 0
                self.is_wave_active = True
        #Nico fin modif
        obstacles = self.collisions_rects + [n.get_rect() for n in self.nexuses]
        self.all_sprites.update(None, obstacles, list(self.all_sprites))
        #self.all_sprites.update(self.dt, obstacles) TEST NICO
        for proj in self.projectiles:
            hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage(proj.damage)
                proj.alive = False
            if proj.rect.colliderect(self.nexus_v.rect):
                self.nexus_v.take_damage(proj.damage)
                proj.alive = False
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.player.take_damage(10) 
        for entity in list(self.all_sprites):
            if hasattr(entity, 'alive') and not entity.alive:
                entity.kill()
        self.camera.follow(self.player.get_rect())
        if not self.nexus_v.alive or not self.nexus_r.alive or not self.player.alive:
            self.running = False
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.all_sprites:
            entity.draw(self.screen, self.camera)
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            if not self.nexus_v.alive or not self.nexus_r.alive:
                winner = "VICTORY" if not self.nexus_v.alive else "DEFEAT"
                end = EndScreen(self.screen, winner)
                end.draw()
                result = end.run()
                return result
            self.clock.tick()
        return "QUIT"