import pygame
import sys
from pygame.locals import *
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
TAN = (210, 180, 140)
RABBIT_COLOR = (255, 100, 100)
WOLF_COLOR = (100, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rabbit and Wolves")

FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 72)


class Board:
    def __init__(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.rabbit = (ROWS - 1, COLS // 2)
        self.wolves = [(0, i * 2 + 1) for i in range(4)]

    def draw(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = TAN if (row + col) % 2 == 0 else BROWN
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        for wolf in self.wolves:
            pygame.draw.circle(screen, WOLF_COLOR, self._to_pixel(wolf), SQUARE_SIZE // 2 - 10)

        pygame.draw.circle(screen, RABBIT_COLOR, self._to_pixel(self.rabbit), SQUARE_SIZE // 2 - 10)

    def _to_pixel(self, pos):
        row, col = pos
        return col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2

    def move_rabbit(self, new_pos):
        self.rabbit = new_pos

    def move_wolf(self, wolf_index, new_pos):
        self.wolves[wolf_index] = new_pos

    def get_valid_moves(self, pos, is_rabbit=False):
        row, col = pos
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_rabbit else [(1, -1), (1, 1)]
        valid_moves = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < ROWS and 0 <= new_col < COLS and not self.is_occupied((new_row, new_col)):
                valid_moves.append((new_row, new_col))
        return valid_moves

    def is_occupied(self, pos):
        return pos == self.rabbit or pos in self.wolves

    def is_rabbit_won(self):
        return self.rabbit[0] == 0

    def is_wolves_won(self):
        return len(self.get_valid_moves(self.rabbit, is_rabbit=True)) == 0


class RabbitAI:
    def __init__(self, difficulty):
        self.depth = {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]

    def get_best_move(self, board):
        def minimax(position, depth, alpha, beta, maximizing):
            if depth == 0 or board.is_wolves_won() or board.is_rabbit_won():
                return self.evaluate(board)

            valid_moves = board.get_valid_moves(position, is_rabbit=maximizing)

            if maximizing:
                max_eval = float('-inf')
                best_move = None
                for move in valid_moves:
                    original_pos = board.rabbit
                    board.move_rabbit(move)
                    eval = minimax(board.rabbit, depth - 1, alpha, beta, False)
                    board.move_rabbit(original_pos)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval if depth != self.depth else best_move
            else:
                min_eval = float('inf')
                for wolf in board.wolves:
                    valid_wolf_moves = board.get_valid_moves(wolf)
                    for move in valid_wolf_moves:
                        original_pos = wolf
                        wolf_index = board.wolves.index(wolf)
                        board.move_wolf(wolf_index, move)
                        eval = minimax(board.rabbit, depth - 1, alpha, beta, True)
                        board.move_wolf(wolf_index, original_pos)
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
                return min_eval

        return minimax(board.rabbit, self.depth, float('-inf'), float('inf'), True)

    def evaluate(self, board):
        return -board.rabbit[0]


class Game:
    def __init__(self, difficulty):
        self.board = Board()
        self.turn = "Rabbit"
        self.selected_wolf = None
        self.rabbit_ai = RabbitAI(difficulty)

    def draw(self):
        self.board.draw()
        self._draw_turn()

    def _draw_turn(self):
        turn_text = FONT.render(f"Turn: {self.turn}", True, BLACK)
        screen.blit(turn_text, (10, HEIGHT - 40))

    def select_wolf(self, pos):
        if pos in self.board.wolves:
            self.selected_wolf = self.board.wolves.index(pos)

    def move_selected_wolf(self, new_pos):
        if self.selected_wolf is not None:
            valid_moves = self.board.get_valid_moves(self.board.wolves[self.selected_wolf])
            if new_pos in valid_moves:
                self.board.move_wolf(self.selected_wolf, new_pos)
                self.turn = "Rabbit"
                self.selected_wolf = None

    def rabbit_move(self):
        valid_moves = self.board.get_valid_moves(self.board.rabbit, is_rabbit=True)
        if not valid_moves:
            return
        best_move = self.rabbit_ai.get_best_move(self.board)
        if best_move:
            self.board.move_rabbit(best_move)
        self.turn = "Wolves"

    def check_game_over(self):
        if self.board.is_rabbit_won():
            return "Rabbit wins!"
        elif self.board.is_wolves_won():
            return "Wolves win!"
        return None

    def display_winner(self, winner):
        screen.fill(WHITE)
        message = LARGE_FONT.render(winner, True, BLACK)
        screen.blit(message, (WIDTH // 4, HEIGHT // 2 - 50))
        pygame.display.flip()
        pygame.time.wait(3000)


def menu_screen():
    while True:
        screen.fill(WHITE)
        title = LARGE_FONT.render("Rabbit and Wolves", True, BLACK)
        screen.blit(title, (WIDTH // 8, HEIGHT // 4))

        easy_button = FONT.render("1. Easy", True, BLACK)
        medium_button = FONT.render("2. Medium", True, BLACK)
        hard_button = FONT.render("3. Hard", True, BLACK)

        screen.blit(easy_button, (WIDTH // 3, HEIGHT // 2))
        screen.blit(medium_button, (WIDTH // 3, HEIGHT // 2 + 40))
        screen.blit(hard_button, (WIDTH // 3, HEIGHT // 2 + 80))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    return "Easy"
                elif event.key == K_2:
                    return "Medium"
                elif event.key == K_3:
                    return "Hard"


def main():
    difficulty = menu_screen()
    game = Game(difficulty)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and game.turn == "Wolves":
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if game.selected_wolf is None:
                    game.select_wolf((row, col))
                else:
                    game.move_selected_wolf((row, col))

        if game.turn == "Rabbit":
            game.rabbit_move()

        game_over = game.check_game_over()
        if game_over:
            game.display_winner(game_over)
            pygame.quit()
            sys.exit()

        screen.fill(WHITE)
        game.draw()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
