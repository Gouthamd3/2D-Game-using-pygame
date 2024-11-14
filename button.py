import pygame,sys
import matplotlib.pyplot as plt
import mysql.connector as conn
pygame.init()


player_name_ = ''
#button class
class Button():
    def __init__(self,x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

'''
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
                if event.key == pygame.K_RETURN:
                    #print(self.text)
                    #print(self.text)
                    player_name_ = self.text
                    #print(player_name_)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
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
'''

#BUTTON FOR MATPLOTLIB
class Graph_Button():
    def __init__(self,x, y, image, scale,name):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.player_name = name

    def draw(self, surface):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action, self.player_name
#return player name

#print(player_name_)

'''

def to_sql(self, souls, level):
        sql_con = mysql.connect(user ='root', password='sairam', database='Swordigo')
        cursor = sql_con.cursor()
        if self.text == '':
            cursor.execute(f"insert into player values('abc', {souls}, {level}, now())")
        else:
            cursor.execute(f"insert into player values({self.text}, {souls}, {level}, now())")
        sql_con.close()

sql_con = mysql.connect(user ='root', password='sairam', database='Swordigo')
                cursor = sql_con.cursor()
                if self.text == '':
                    cursor.execute(f"insert into player values('abc', {souls}, {level}, now())")
                else:
                    cursor.execute(f"insert into player values({self.text}, {souls}, {level}, now())")
                sql_con.close()

'''

'''

if press_over: #displaying graph here
db = conn.connect(host="localhost", user="root", password="sairam",database="swordigo")
cursor = db.cursor()
playername = name_button.text
query = "select max(diamonds),player_name from player where player_name group by player_name"
cursor.execute(query)
records = cursor.fetchall()
dict1 = {}
for i in records:
    dict1[i[1]] = i[0]
plt.plot(dict1.keys(),dict1.values(), 'ro-')
plt.show()
'''