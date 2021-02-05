import pygame
import time
import os

time_ms = lambda: int(round(time.time() * 1000))

class Button:
    def __init__(self, 
        translate=[0,0],
        position=[0,0],
        size=[100,100],
        text="DEFAULT",
        border=True,
        color_text=(255,255,255),
        color_background=(0,0,0),
        color_border=(100,100,100),
        color_hover=(150,150,150),
        color_click=(200,200,200),
        text_size=30):
        
        self.translate = translate
        self.position = position
        self.size = size
        self.x = self.position[0] 
        self.y = self.position[1]
        self.border = border     
        self.color_text = color_text
        self.color_background = color_background
        self.color_border = color_border
        self.color_hover = color_hover
        self.color_click = color_click

        self.color = color_background

        self.font = pygame.font.Font(None, text_size)     
        self.text = text
        self.text_box = self.font.render(bytes(str(self.text), encoding='utf8'), True, self.color_text)
        self.text_size = text_size
        self.text_rect = self.text_box.get_rect()  
        self.text_rect.center = (self.x + self.size[0]/2, self.y + self.size[1]/2)
        
        self.state = 0
        
        self.click_time = time_ms()
            
    def display(self, surface):
        if self.border:
            pygame.draw.rect(surface, self.color_border, [self.x, self.y, self.size[0], self.size[1]])      

        if self.state == 1:
            self.color = self.color_click 
        elif self.hover():        
            self.color = self.color_hover         
        else:
            self.color = self.color_background    
            
        pygame.draw.rect(surface, self.color, [self.x+5, self.y+5, self.size[0]-10, self.size[1]-10])
        surface.blit(self.text_box, self.text_rect)

    def hover(self):
        mouse = pygame.mouse.get_pos()
        if self.x + self.translate[0] < mouse[0] < self.x + self.size[0] + self.translate[0]:
            if self.y + self.translate[1] < mouse[1] < self.y + self.size[1] + self.translate[1]:
                return True      
        return False
            
    def click(self):
        if self.hover():
            if self.click_time + 100 < time_ms():
                if pygame.mouse.get_pressed()[0]:
                    self.click_time = time_ms()
                    return True
        return False
        
class TextArea:
    def display(self, surface, position, size):
        pygame.draw.rect(surface, (100,100,100), [position[0], position[1], size[0], size[1]])    
        pygame.draw.rect(surface, (0,0,0), [position[0]+5, position[1]+5, size[0]-10, size[1]-10]) 
            
class Text:
    def __init__(self, position=[0,0], size=[100,100], text="", border=True, back=False, color_text=(255,255,255), color_background=(0,0,0), color_border=(100,100,100), text_size=30, font=None):
        self.position = position
        self.size = size
        self.x = position[0]
        self.y = position[1]
        self.border = border
        self.back = back
        self.color_text = color_text 
        self.color_background = color_background
        self.color_border = color_border

        self.font = pygame.font.Font(font, text_size) 
        self.text = text
        self.text_box = self.font.render(bytes(str(self.text), encoding='utf8'), True, self.color_text)
        self.text_size = text_size
        self.text_rect = self.text_box.get_rect()
        self.text_rect.center = (self.x + self.size[0]/2, self.y + self.size[1]/2)
       
    def display(self, surface, position=None):
        x = self.x
        y = self.y        
        if position is not None: 
            x = position[0]
            y = position[1]            
            self.text_rect = self.text_box.get_rect() 
            self.text_rect.center = (x,y)
            
        if self.border:
            pygame.draw.rect(surface, self.color_border, [self.x, self.y, self.size[0], self.size[1]])    
            pygame.draw.rect(surface, self.color_background, [self.x+5, self.y+5, self.size[0]-10, self.size[1]-10]) 
        
        if self.back:
            width = self.text_box.get_width() + 8
            pygame.draw.rect(surface, self.color_background, [x - width/2, y - self.size[1]/2+2, width, self.size[1]]) 
            
        surface.blit(self.text_box, self.text_rect)
            
    def change_text(self, text):
        self.text = text
        self.text_box = self.font.render(bytes(str(self.text), encoding='utf8'), True, self.color_text)
        self.text_rect = self.text_box.get_rect()
        self.text_rect.center = (self.x + self.size[0]/2, self.y + self.size[1]/2)