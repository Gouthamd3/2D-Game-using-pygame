import pygame, os, random, csv, button, sys
#from pygame import mixer
#from modules import *
import mysql.connector as sqlConn 
import matplotlib.pyplot as plt


pygame.init()


#screen variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Swordigo')

#set frame rate
clock = pygame.time.Clock()
FPS = 60


#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
#print(TILE_SIZE)
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False
start_intro = False
player_name_ = ''


#define player action variables
moving_left = False
moving_right = False
hit = False
player_sword_hit = False
player_hurt = False


#load images
#button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
graph_img = pygame.image.load('img/graph_img.png').convert_alpha()
 
#background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#magic
magic_img = pygame.image.load('img/icons/magic.png').convert_alpha()
magic_img = pygame.transform.scale(magic_img, (20,20 ))
#pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
magic_box_img = pygame.image.load('img/icons/magic_box.png').convert_alpha()
#soul == coins
soul_box_img = pygame.image.load('img/icons/soul_box.png').convert_alpha()
soul_box_img = pygame.transform.scale(soul_box_img, (25,25))
item_boxes = {
	'Health'	: health_box_img,
	'Magic'		: magic_box_img,
	'Soul'	    : soul_box_img
}


#define colours
BG = (144, 201, 120)
BG = (47, 132, 47)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)


#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.fill((0,0,0))
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


#function to reset level
def reset_level():
	enemy_group.empty()
	#bullet_group.empty()
	magic_group.empty()
	#explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#create empty tile list
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)
	return data

class Character(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, magic,name=''):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		#for max hit of 2
		self.hit_cooldown = 0
		self.magic = magic
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		#to check whether the enmy has hit or not
		self.enemy_hit = False
		self.name = name
		self.Soul = 0
		
		#load all images for the players
		animation_types = ['Idle', 'Run', 'Jump', 'Death','Hit','Hurt']
		for animation in animation_types:
			#reseting all temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale)-4, int(img.get_height() * scale + 6))) #-14, -31
				#print('Player dimesnions:',img.get_width()*scale,img.get_height())
	
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.hit_cooldown > 0:
			self.hit_cooldown -= 1


	def move(self, moving_left, moving_right):
		#reseting movement variables
		
		#global screen_scroll
		screen_scroll = 0
		dx = 0
		dy = 0

		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		#applying gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y



		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#print(self.rect.x,'   ', tile[1])
				#if the ai has hit a wall then make it turn around
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		#check for collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			player_hurt = True
			self.health = 0

		#check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		#check if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			player_hurt = True
			self.health = 0


		#check if going off the edges of the screen
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy


		#update scroll based on player position #check this out
		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete
		#print(screen_scroll)

#Dooooo tthissssss
	def Player_Sword_Hit(self):
		if self.hit_cooldown == 0:
			self.hit_cooldown = 2
			#if player_sword_hit == True:
			#if self.action == 4:
			#if self.rect.colliderect(self.rect):
			#if pygame.sprite.spritecollide(self, magic_group, False):
			#	enemy_hit = True
				#if self.rect.colliderect(self.image.get_rect()):					
	
	def hit(self):
		if self.hit_cooldown == 0:
			self.hit_cooldown = 20
			magic = Magic(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			magic_group.add(magic)
			self.magic -=1


	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#check if the ai in near the player
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.update_action(0)#0: idle
				#hit
				self.hit()
				#self.magic_hit()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					#update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		#update animation
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()


	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = Character('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = Character('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.40, 2, 20)
						enemy_group.add(enemy)
					elif tile == 17:#create souls box
						item_box = ItemBox('Soul', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:#create magic_box_img box
						item_box = ItemBox('Magic', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar

	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])
			#print(tile)


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += screen_scroll
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Magic':
				player.magic += 10
			elif self.item_type == 'Soul':
				player.Soul += 1
			#delete the item box
			self.kill()


COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
class InputBox():
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event): #souls, level
        global player_name_
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                            
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)
        #return self.text
    
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

################################################
class Magic(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 7
		self.image = magic_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move magic
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check if magic has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, magic_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, magic_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete




#create screen fades
intro_fade = ScreenFade(1, (30,30,40), 4) #BLACK PINK
death_fade = ScreenFade(2, (20,200,120), 4)


#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
name_button = InputBox(308, 100, 140, 32)
Graph_Button = button.Graph_Button(300, 550, graph_img,2,name_button.text)

#create sprite groups
enemy_group = pygame.sprite.Group()
magic_group = pygame.sprite.Group()
#explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


while True:
	time_played = 0
	#Main Game Loop
	run = True
	while run:

		clock.tick(FPS)

		#print(player.enemy_hit)
		if start_game == False:
			#draw menu
			screen.fill((20,10,20)) #BG
			#add buttons
			if start_button.draw(screen):
				start_game = True
				start_intro = True

			if exit_button.draw(screen):
				run = False
				#print(name_button.text) #take text from here and add to mysql
			press_over, playername = Graph_Button.draw(screen)
			try:
				if press_over: #displaying graph here
					db = sqlConn.connect(host="localhost", user="root", password="sairam",database="swordigo")
					cursor = db.cursor()
					playername = name_button.text
					query = "select max(diamonds),player_name from player group by player_name"
					cursor.execute(query)
					records = cursor.fetchall()
					dict1 = {}
					for i in records:
					    dict1[i[1]] = i[0]
					plt.plot(dict1.keys(),dict1.values(), 'ro-')
					plt.xlabel("Player Name")
					plt.ylabel("Diamonds")
					plt.show()
			except:
				print("none")
			name_button.draw(screen)
			
			name_text = font.render("ENTER YOUR NAME HERE",0,(255,220,200))
			screen.blit(name_text,(280,70))
			pygame.display.update()

			
		else:
			#update background
			draw_bg()
			#draw world map
			world.draw()
			#show player health
			health_bar.draw(player.health)
			
			#magic of the player
			draw_text('MAGIC: ', font, WHITE, 10, 40)
			for x in range(player.magic):
				screen.blit(pygame.transform.scale(magic_img,(15,15)), (90 + (x * 10), 40))

			#Souls of the player --- diamonds
			draw_text('SOUL: ', font, WHITE, 10, 70)
			for x in range(player.Soul):
				screen.blit(pygame.transform.scale(soul_box_img, (18,18)) , (90 + (x * 10), 75))
			
			player.update()
			player.draw()

			for enemy in enemy_group:
				enemy.ai()
				enemy.update()
				enemy.draw()

			#update and draw groups
			magic_group.update()
			item_box_group.update()
			decoration_group.update()
			water_group.update()
			exit_group.update()
			magic_group.draw(screen)
			item_box_group.draw(screen)
			decoration_group.draw(screen)
			water_group.draw(screen)
			exit_group.draw(screen)

			#show intro
			if start_intro == True:
				if intro_fade.fade():
					start_intro = False
					intro_fade.fade_counter = 0


			#update player actions
			if player.alive:
				#print(player.rect.x+100)
				#release magic
				if hit:
					player.hit()
				
				if player_sword_hit:
					if player.rect.colliderect(enemy.rect):
						enemy.health -= 1.5
						print('enemy hit')
				

				if player.in_air:
					player.update_action(2)#2: jump
				elif moving_left or moving_right:
					player.update_action(1)#1: run
				elif player_sword_hit:
					player.update_action(4)#4: hit
				elif player_hurt:
					player.update_action(5)#5 : Hurt
				else:
					player.update_action(0)#0: idle
				
				screen_scroll, level_complete = player.move(moving_left, moving_right)
				bg_scroll -= screen_scroll
				#print('screen:' ,screen_scroll)
				
				#check if player has completed the level
				if level_complete:
					start_intro = True
					level += 1
					bg_scroll = 0
					world_data = reset_level()
					if level <= MAX_LEVELS:
						#load in level data and create world
						with open(f'level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)	
			else:
				screen_scroll = 0
				if death_fade.fade():
					if restart_button.draw(screen):
						death_fade.fade_counter = 0
						start_intro = True
						bg_scroll = 0
						world_data = reset_level()
						#load in level data and create world
						with open(f'level{level}_data.csv', newline='') as csvfile:
							reader = csv.reader(csvfile, delimiter=',')
							for x, row in enumerate(reader):
								for y, tile in enumerate(row):
									world_data[x][y] = int(tile)
						world = World()
						player, health_bar = world.process_data(world_data)


		for event in pygame.event.get():
			#quit game
			if event.type == pygame.QUIT:
				run = False
			#name_button.handle_event(event, 2, level)
			name_button.handle_event(event)

			#name_button.to_sql(player.Soul, level)
			#keyboard presses
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a:
					moving_left = True
				if event.key == pygame.K_d:
					moving_right = True
				if event.key == pygame.K_SPACE:
					hit = True
				if event.key == pygame.K_q:
					player_sword_hit = True
				if event.key == pygame.K_w and player.alive:
					player.jump = True
					#jump_fx.play()
				if event.key == pygame.K_ESCAPE:
					run = False


			#keyboard button released
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_a:
					moving_left = False
				if event.key == pygame.K_d:
					moving_right = False
				if event.key == pygame.K_SPACE:
					hit = False
				if event.key == pygame.K_q:
					player_sword_hit = False

		if start_game == True:
			time_played += 0.02

		score_value = font.render("Time : "+str(round(time_played))+"Sec",1,(255,153,52))
		screen.blit(score_value,(675,10))
		pygame.display.update()

	

		pygame.display.update()
	
	name = (name_button.text)
	print(name_button.text)
	import mysql.connector as conn
	db = conn.connect(
    	host='localhost',
    	user = 'root',
    	password='sairam',
    	database='swordigo')

	cur = db.cursor()
	query = "insert into player values ('" + name + "', " + str(player.Soul) +", " + str(level) + "," + 'now()'+')'


	cur.execute(query)


	db.commit()

	pygame.quit()
	sys.exit()





