import pygame
import math
# Assure-toi d'importer ta classe Entity de base
from game.entities.entity import Entity 

class Tower(Entity):
    def __init__(self, x, y, sprite, team, hp):
        # Une tourelle fait par exemple 64x64 pixels
        super().__init__(x, y, 64, 64, sprite, hp)
        
        self.team = team
        self.hp = 2000          # Points de vie de la tourelle
        self.max_hp = 2000
        self.alive = True
        
        # Caractéristiques de combat
        self.range = 250         # Rayon de la portée d'attaque
        self.damage = 40         # Dégâts par tir
        self.attack_cooldown = 1200  # Vitesse d'attaque (1.2 seconde)
        self.last_attack_time = 0
        self.target = None

    def update(self, event, collision_rects, entities):
        super().update(event, collision_rects, entities)
        
        if not self.alive:
            return

        # 1. Vérifier si la cible actuelle est toujours valide
        if self.target:
            if not self.target.alive or self.get_distance(self.target) > self.range:
                self.target = None # La cible est morte ou sortie de la zone

        # 2. Si pas de cible, en chercher une nouvelle
        if self.target is None:
            self.target = self.find_target(entities)

        # 3. Attaquer la cible si le cooldown est prêt
        if self.target:
            self.attack()

    def find_target(self, entities):
        best_target = None
        min_dist = self.range
        
        for entity in entities:
            # On cible uniquement les ennemis vivants qui ont une équipe
            if hasattr(entity, 'team') and entity.team != self.team and entity.alive:
                dist = self.get_distance(entity)
                if dist < min_dist:
                    # Optionnel (style LoL) : Prioriser les sbires avant le joueur
                    best_target = entity
                    min_dist = dist
                    
        return best_target

    def get_distance(self, entity):
        # Calcule la distance entre le centre de la tourelle et le centre de l'entité
        return pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            # Option A Simple : Applique les dégâts instantanément (façon laser)
            if hasattr(self.target, 'take_damage'):
                self.target.take_damage(self.damage)
            else:
                self.target.hp -= self.damage
                if self.target.hp <= 0:
                    self.target.alive = False
            
            self.last_attack_time = current_time
            print(f"La tourelle {self.team} tire sur une cible ! HP restant : {self.target.hp}")

    def take_damage(self, amount):
        if self.alive:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                self.alive = False
                self.kill() # Retire le sprite de tous les groupes Pygame automatiquement
                print(f"Une tourelle {self.team} a été détruite !")