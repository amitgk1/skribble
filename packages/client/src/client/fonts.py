import pygame

pygame.font.init()
font = "comicsansms"
if not pygame.font.match_font("comicsansms"):
    font = "ubuntusans"
FONT_SM = pygame.font.SysFont(font, 12)
FONT_MD = pygame.font.SysFont(font, 18)
FONT_LG = pygame.font.SysFont(font, 24)
FONT_TITLE = pygame.font.SysFont(font, 64, bold=True)
