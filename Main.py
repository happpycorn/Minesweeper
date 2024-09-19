# Import

import turtle
import random
import time

# Constant

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# World Set

class World:

    def __init__(
            self,
            block_count=20, block_size=20
            ) -> None:
        
        self.block_count = block_count
        self.block_size = block_size
        self.boom_count = (block_count**2) // 5
        self.screen = self.screenSet()
        self.needSet = True
        self.gg = False
        self.open_count = 0
        self.canvas = self.screen.getcanvas()

        self.block_map = [[Block(i, j) for j in range(self.block_count)] for i in range(self.block_count)]

        for row in self.block_map:
            for block in row:
                block.drawSquare()

    def screenSet(self):

        screen_gap = 2
        screen_size = self.block_size * (self.block_count + screen_gap * 2)

        screen = turtle.Screen()
        screen.setup(width=screen_size, height=screen_size)
        screen.setworldcoordinates(-screen_gap, self.block_count+screen_gap, self.block_count+screen_gap, -screen_gap)
        screen.tracer(0)
        screen.delay(0)
        turtle.ht()

        return screen

    def boomGenerate(self, generateNumber):

        # avoid click pos

        avoidRange = [generateNumber + i for i in range(-1, 2)] + \
                    [generateNumber + i + self.block_count for i in range(-1, 2)] + \
                    [generateNumber + i - self.block_count for i in range(-1, 2)]
        generateRange = [i for i in range(self.block_count**2) if i not in avoidRange]

        # random generate

        boom_numbers = random.sample(generateRange, self.boom_count)
        boom_map = [[1 if i*self.block_count+j in boom_numbers else 0 for j in range(self.block_count)] for i in range(self.block_count)]

        def countBoom(x, y):

            if boom_map[x][y] == 1:
                return -1

            count = 0

            for dr, dc in DIRECTIONS:
                r, c = x + dr, y + dc
                if 0 <= r < self.block_count and 0 <= c < self.block_count and boom_map[r][c] == 1:
                    count += 1
            
            return count
        
        return countBoom
    
    def flagCount(self, x, y):
        flag = 0
        for dr, dc in DIRECTIONS:
            r, c = x + dr, y + dc
            if 0 <= r < self.block_count and 0 <= c < self.block_count and self.block_map[r][c].flag:
                flag += 1
        return flag

    def firstClick(self, x, y):

        number = x*self.block_count + y

        counter = world.boomGenerate(number)

        for i in range(self.block_count):
            for j in range(self.block_count):
                self.block_map[i][j].setNumber(counter(i, j))
        
        self.start_time = time.time()
    
    def click(self, x, y, flag=False, updata=True):

        if not (0 <= x < self.block_count and 0 <= y < self.block_count):
            return
        
        x = int(x) ; y = int(y)
        block = self.block_map[x][y]
        
        if self.needSet:
            self.firstClick(x, y)
            self.needSet = False

        if self.gg:
            return

        if flag:
            if block.isOpen:
                return
            block.drawFlag()
            return
        
        if block.flag:
            return

        if block.isOpen:

            if self.flagCount(x, y) != block.number:
                return
            
            for dr, dc in DIRECTIONS:
                r, c = x + dr, y + dc
                if 0 <= r < self.block_count and 0 <= c < self.block_count and not self.block_map[r][c].flag and not self.block_map[r][c].isOpen:
                    self.click(r, c, updata=False)
            
            return
        
        block.open()
        self.open_count += 1

        if self.open_count == self.block_count**2 - self.boom_count:
            self.gg = True
            print(f"you win, use time {int(time.time()-self.start_time)}")
            return


        if block.number == -1:
            self.gg = True
            print("you lose")
            return

        if block.number == 0:
            for dr, dc in DIRECTIONS:
                r, c = x + dr, y + dc
                if 0 <= r < self.block_count and 0 <= c < self.block_count and not self.block_map[r][c].isOpen:
                    self.click(r, c, updata=False)

        if updata:
            self.screen.update()
    
    def restart(self):

        self.needSet = True
        self.gg = False
        self.open_count = 0

        for row in self.block_map:
            for block in row:
                block.turtle.clear()
                block.isOpen = False
                block.flag = False
                block.drawSquare()
        
        self.screen.update()

# Block

class Block:

    def __init__(
            
            self, x:int, y:int, size=1, 
            surface_color=(200, 200, 200), side_color=(100, 100, 100), line_color=(0, 0, 0), flag_color=(255, 0, 0)

            ) -> None:
        
        self.size = size
        self.isOpen = False
        self.flag = False
        self.x, self.y = x, y
        self.center_x = self.x + self.size / 2
        self.center_y = self.y + (self.size / 2) + 0.4 # 字體偏移
        self.colors = {"surface" : surface_color, "side" : side_color, "line" : line_color, "flag" : flag_color}
        
        # Turtle Set
        
        self.turtle = turtle.Turtle()
        self.turtle.speed(0) ; self.turtle.up() ; self.turtle.ht()

        self.turtle.goto(self.x, self.y)
    
    def __setColor__(self, *args) -> None:
        rgb_colors = [self.colors[i] for i in args]
        turtle_colors = [tuple(c / 255 for c in rgb) for rgb in rgb_colors]
        self.turtle.color(*turtle_colors)
    
    def setNumber(self, number):
        txt_color = [
            (0, 255, 0),(85, 255, 0),(170, 255, 0),
            (255, 255, 0),(255, 170, 0),(255, 85, 0),
            (255, 0, 0),(255, 0, 85),(255, 0, 170),(255, 0, 255)
        ]

        self.number = number
        self.colors["txt"] = txt_color[self.number]
    
    def drawSquare(self) -> None:

        if self.isOpen:
            self.__setColor__("line", "side")
        elif self.flag:
            self.__setColor__("line", "flag")
        else:
            self.__setColor__("line", "surface")
            
        self.turtle.goto(self.x, self.y)
        self.turtle.down()
        self.turtle.begin_fill()

        for _ in range(4):
            self.turtle.forward(self.size)
            self.turtle.lt(90)
        
        self.turtle.end_fill()
        self.turtle.up()

        if self.isOpen:

            if self.number == 0:
                return

            self.__setColor__("txt")
            self.turtle.goto(self.center_x, self.center_y)

            if self.number == -1:
                self.turtle.write("X", align="center")
            else:
                self.turtle.write(self.number, align="center")

    def open(self):
        self.isOpen = True
        self.drawSquare()
    
    def drawFlag(self):
        self.flag = not self.flag
        self.drawSquare()

# Init

world = World()

world.screen.update()

world.screen.onclick(lambda x, y: world.click(x, y), btn=1)
world.screen.onclick(lambda x, y: world.click(x, y, flag=True), btn=3)

world.screen.onkeypress(world.restart, "r")

world.screen.listen()
world.screen.mainloop()