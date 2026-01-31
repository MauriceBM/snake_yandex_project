import pygame
from random import randint
from typing import List, Tuple, Optional

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR: Tuple[int, int, int] = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

# Словарь для обработки поворотов змейки
TURN_MAP = {
    (pygame.K_UP, DOWN): None,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, UP): None,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, RIGHT): None,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, LEFT): None,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color: Tuple[int, int, int] = SNAKE_COLOR) -> None:
        """Инициализирует игровой объект.
        Args:
            body_color: Цвет объекта в формате RGB.
        """
        self.position: Tuple[int, int] = (SCREEN_WIDTH // 2,
                                          SCREEN_HEIGHT // 2)
        self.body_color: Tuple[int, int, int] = body_color

    def draw_cell(self,
                  position: Tuple[int, int],
                  color: Optional[Tuple[int, int, int]] = None) -> None:
        """Отрисовывает одну ячейку на экране.

        Args:
            position: Позиция ячейки.
            color: Цвет ячейки. Если None, используется цвет объекта.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        draw_color = color or self.body_color
        pygame.draw.rect(screen, draw_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Отрисовывает объект на экране."""


class Apple(GameObject):
    """Представляющий яблоко в игре."""

    def __init__(self) -> None:
        """Инициализирует яблоко со случайной позицией."""
        super().__init__(APPLE_COLOR)
        initial_snake_position = [
            (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
        ]
        self.randomize_position(initial_snake_position)

    def randomize_position(self,
                           snake_positions: List[Tuple[int, int]]) -> None:
        """Устанавливает случайную позицию для яблока.
        Args:
            snake_positions: Список позиций, занятых змейкой.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in snake_positions:
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на экране."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Представляющий змейку в игре."""

    def __init__(self) -> None:
        """Инициализирует змейку с начальными параметрами."""
        super().__init__(SNAKE_COLOR)
        self.reset()

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        # Si vous utilisez next_direction
        if hasattr(self, 'next_direction') and self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Сбрасывает состояние змейки к начальному."""
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [
            (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
        ]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.last: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки.
        Returns:
            tuple: Координаты головы змейки.
        """
        return self.positions[0]

    def move(self, new_direction: Optional[Tuple[int, int]] = None) -> None:
        """Перемещает змейку в текущем направлении."""
        self.last = self.positions[-1]

        if new_direction:
            self.direction = new_direction

        head_x, head_y = self.get_head_position()

        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT

        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку на экране."""
        for position in self.positions[1:]:
            self.draw_cell(position)

        head_position = self.get_head_position()
        self.draw_cell(head_position)

        if self.last:
            rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def grow(self) -> None:
        """Увеличивает длину змейки на 1."""
        self.length += 1

    def check_collision(self) -> bool:
        """Проверяет столкновение головы змейки с телом.
        Returns:
            bool: True если произошло столкновение, иначе False.
        """
        head = self.get_head_position()
        return head in self.positions[1:]


def handle_keys(snake: Snake) -> Optional[Tuple[int, int]]:
    """Обрабатывает нажатия клавиш.
    Args:
        snake: Объект змейки для управления.

    Returns:
        Новое направление движения или None.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            new_direction = TURN_MAP.get((event.key, snake.direction))
            if new_direction is not None:
                return new_direction
    return None


def main() -> None:
    """Основная функция игры."""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()

    needs_background_redraw = True

    while True:
        clock.tick(SPEED)

        new_direction = handle_keys(snake)
        if new_direction:
            snake.move(new_direction)
        else:
            snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        if snake.check_collision():
            snake.reset()
            apple.randomize_position(snake.positions)
            needs_background_redraw = True

        if needs_background_redraw:
            screen.fill(BOARD_BACKGROUND_COLOR)
            needs_background_redraw = False

        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
