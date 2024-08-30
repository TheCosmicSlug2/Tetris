import pygame as pg
from random import choice, randint
from sys import exit as sysexit

# ajouter changement de couleur possible + next + held ?

# Initialisation de Pygame
pg.init()

# Initialisation de la matrice et du buffer
buffer = [[0 for _ in range(10)] for _ in range(2)]
matrice = [[0 for _ in range(10)] for _ in range(20)]

# Configuration de l'écran
screen_width, screen_height = 600, 600
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption('Tetris')

font = pg.font.Font(None, 36)

try:
    pg.mixer.music.load(r"ressources/sfx/tetris.mp3") # Jouer la musique en boucle (-1 indique la lecture en boucle)
    pg.mixer.music.play(-1)
except Exception as e:
    print(e)


# Définition des couleurs et des FPS
clock = pg.time.Clock()
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
red = (255, 0, 0)
fps = 3
cell_size = 20
SPAWN = "YES"
current_piece = None
score = 0

background_color = black
still_pieces_color = black
falling_pieces_color = red
empty_cell_color = grey
text_color = white

# Fonction pour afficher la matrice
def render_matrice():

    """ Dessine la grille """

    marge = 2
    largeur_container_col = cell_size * len(matrice[0]) + marge * (len(matrice[0]) + 1)
    largeur_container_row = cell_size * len(matrice) + marge * (len(matrice) + 1)
    x_haut_gauche = screen_width / 2 - (largeur_container_col / 2)
    y_haut_gauche = screen_height / 2 - (largeur_container_row / 2)
    pg.draw.rect(screen, white, (x_haut_gauche - marge, y_haut_gauche - marge, largeur_container_col, largeur_container_row))
    for (row_idx, row) in enumerate(matrice):
        for (cell_idx, cell) in enumerate(row):
            color = empty_cell_color if cell == 0 else (still_pieces_color if cell == 1 else falling_pieces_color)
            pg.draw.rect(screen, color, (x_haut_gauche + (marge * cell_idx) + (cell_idx * cell_size),
                                             y_haut_gauche + (marge * row_idx) + (row_idx * cell_size), cell_size,
                                             cell_size))

    score_text = font.render(f"Score : {score}", True, text_color)
    color_text1 = font.render(f"\"Q\" pour changer", True, text_color)
    color_text2 = font.render(f"la couleur", True, text_color)
    next_piece_text = font.render(f"Prochain : \"{next_pieces[0]}\"", True, text_color)

    # Dessin du texte du score sur l'écran
    screen.blit(score_text,
                (cell_size + score_text.get_width() // 2, cell_size + score_text.get_height() // 2))

    screen.blit(color_text1,
                (screen_width / 2 + 20, cell_size + color_text1.get_height() // 2))

    screen.blit(color_text2,
                (screen_width / 2 + 120, cell_size + (color_text2.get_height() * 2)))

    screen.blit(next_piece_text,
                (screen_width / 2 + 120, cell_size + (next_piece_text.get_height() * 8)))

    pg.display.update()


def random_piece():

    """ Choisir une pièce au hasard """

    liste_pieces = ["I", "O", "T", "S", "Z", "J", "L"]
    return choice(liste_pieces)


def spawn_piece(piece=None):

    """ Générer une pièce aléatoire """

    piece_name = piece
    dic_pieces = {
        "I": [[0, 0, 0, 0], [2, 2, 2, 2]],
        "O": [[0, 2, 2, 0], [0, 2, 2, 0]],
        "T": [[2, 2, 2, 0], [0, 2, 0, 0]],
        "S": [[0, 2, 2, 0], [2, 2, 0, 0]],
        "Z": [[0, 2, 2, 0], [0, 0, 2, 2]],
        "J": [[2, 2, 2, 0], [2, 0, 0, 0]],
        "L": [[0, 2, 2, 2], [0, 0, 0, 2]]
    }
    if piece_name is None:
        piece_name = random_piece()

    piece_data = dic_pieces[piece_name]
    for (row_idx, row) in enumerate(piece_data):
        cell_idx = 3
        for data in row:
            buffer[row_idx][cell_idx] = data
            cell_idx += 1
    return piece_name


def descendre_piece():

    """ Faire descendre une pièce """

    global SPAWN, score

    def convert_to_immovable():
        global SPAWN, score
        for (row_idx, row) in enumerate(matrice):
            for (cell_idx, cell) in enumerate(row):
                if cell == 2:
                    matrice[row_idx][cell_idx] = 1
        score += check_line_cleared()
        SPAWN = "YES"

    def check_all_collisions():
        loc_collisions = 0
        for row_idx in range(len(matrice) - 1, -1, -1):
            for (cell_idx, cell) in enumerate(matrice[row_idx]):
                if cell == 2:
                    if matrice[row_idx + 1][cell_idx] == 1:
                        loc_collisions += 1
        return loc_collisions
    
    try:
        collisions = check_all_collisions()
        if collisions == 0:
            for row_idx in range(len(matrice) - 1, -1, -1):
                for (cell_idx, cell) in enumerate(matrice[row_idx]):
                    if cell == 2:
                        matrice[row_idx][cell_idx] = 0
                        matrice[row_idx + 1][cell_idx] = 2
        else:
            convert_to_immovable()
    except:
        convert_to_immovable()
    
    for cell_idx in range(len(buffer[1])):
        if buffer[1][cell_idx] == 2:
            matrice[0][cell_idx] = 2
            buffer[1][cell_idx] = 0
    
    for cell_idx in range(len(buffer[0])):
        if buffer[0][cell_idx] == 2:
            buffer[1][cell_idx] = 2
            buffer[0][cell_idx] = 0


def shift(side):

    """ Déplace une pièce à gauche ou à droite """

    if side == "right":
        side_value = 1
    elif side == "left":
        side_value = -1
    else:
        raise ValueError("Invalid side. Use 'right' or 'left'.")
    for row in matrice:
        if side_value == -1:
            for cell_idx in range(len(row)):
                if row[cell_idx] == 2:
                    new_idx = cell_idx + side_value
                    if 0 <= new_idx < len(row):
                        row[new_idx] = 2
                        row[cell_idx] = 0
                    else:
                        return
        else:
            for cell_idx in range(len(row) - 1, -1, -1):
                if row[cell_idx] == 2:
                    new_idx = cell_idx + side_value
                    if 0 <= new_idx < len(row):
                        row[new_idx] = 2
                        row[cell_idx] = 0
                    else:
                        return

# Fonction pour effectuer la rotation d'une pièce
def rotate(piece, state):
    dic_pieces = {
        "I": [[0, 0, 0, 0], [2, 2, 2, 2]],
        "O": [[0, 2, 2, 0], [0, 2, 2, 0]],
        "T": [[2, 2, 2, 0], [0, 2, 0, 0]],
        "S": [[0, 2, 2, 0], [2, 2, 0, 0]],
        "Z": [[0, 2, 2, 0], [0, 0, 2, 2]],
        "J": [[2, 2, 2, 0], [2, 0, 0, 0]],
        "L": [[0, 2, 2, 2], [0, 0, 0, 2]]
    }
    shape = dic_pieces[piece]
    for _ in range(state % 4):
        shape = [list(row) for row in zip(*shape[::-1])]
    for row_idx in range(len(matrice)): # ON SUPPRIME LES LIGNES QUI BOUGENT
        for cell_idx in range(len(matrice[row_idx])):
            if matrice[row_idx][cell_idx] == 2:
                matrice[row_idx][cell_idx] = 0
    for row_idx, row in enumerate(shape): # ON LA FAIT RESPAWN EN H A U T : C'EST DU GENIEEEEEEEEE
        cell_idx = 3
        for data in row:
            if data == 2:
                matrice[row_idx][cell_idx] = data
            cell_idx += 1


def change_color():

    global empty_cell_color, falling_pieces_color, still_pieces_color, background_color, text_color

    def get_3_random_nbs():
        a = randint(0, 255)
        b = randint(0, 255)
        c = randint(0, 255)

        return a, b, c

    empty_cell_color = get_3_random_nbs()
    falling_pieces_color = get_3_random_nbs()
    still_pieces_color = get_3_random_nbs()
    background_color = get_3_random_nbs()
    text_color = get_3_random_nbs()


def check_line_cleared():

    """ Vérifie si une ligne est complète """

    loc_score = 0
    for (row_idx, row) in enumerate(matrice):
        if set(row) == {1}:
            matrice.pop(row_idx)
            matrice.insert(0, [0 for _ in range(10)])
            loc_score += 10
    return loc_score


def check_game_failed():

    """ Checke la fin du jeu en regardant la première ligne de la grille """

    for cell in matrice[0]:
        if cell == 1:
            return False
    return True

gen = 1
running = True
state = 0


# Boucle principale du jeu
next_pieces = [random_piece(), random_piece()]
while running:
    screen.fill(background_color)


    for event in pg.event.get():
        if event.type == pg.QUIT:
            sysexit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                shift(side="right")
            if event.key == pg.K_LEFT:
                shift(side="left")
            if event.key == pg.K_UP:
                state += 1
                rotate(current_piece, state)
            if event.key == pg.K_DOWN:
                fps += 10
            if event.key == pg.K_q:
                change_color()

    if SPAWN == "YES": # ajouter pièce suivante
        current_piece = spawn_piece(next_pieces[0])
        next_pieces.pop(0)
        next_pieces.append(random_piece())
        state = 0
        SPAWN = "NO"
    descendre_piece()
    render_matrice()
    gen += 1
    clock.tick(fps)
    fps = 5
    running = check_game_failed()


pg.quit()
