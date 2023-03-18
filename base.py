class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def intersects(self, other):
        return not (self.x + self.width <= other.x or
                    self.y + self.height <= other.y or
                    self.x >= other.x + other.width or
                    self.y >= other.y + other.height)