import random
from base import *
from app import Container

class RandomizedPolicy(Container):
    name = "random"
    def __init__(self, *args, **kwargs):
        self.policy = self.randomized_policy
        self.MAX_ITER=5000
        super(RandomizedPolicy, self).__init__(*args, **kwargs)

    def randomized_policy(self, rectangle):
        max_x = self.width - rectangle.width
        max_y = self.height - rectangle.height

        if max_x < 0 or max_y < 0:
            return None, None  # Rectangle is too large to fit

        i=1
        while(True):
            x = random.randint(0, max_x)
            y = random.randint(0, max_y)

            for rect in self.rectangles:
                if rect.intersects(Rectangle(x, y, rectangle.width, rectangle.height)):
                    # if intersects, then break the loop and search again with new position
                    break
            else:
                # this block is only executed if the main for loop encountered no breaks 
                # which means that the new position of the rectangle is good to go
                break
            if (i%1000 ==0):
                print(f"#{len(self.rectangles)} LOOKING for {i}th time")
            i=i+1
            if (i>=self.MAX_ITER):
                return None, None
            
        return x, y

class FFDHPolicy(Container):
    '''
    FFDH packs the next item R (in non-increasing height) on the first level
    where R fits. If no level can accommodate R, a new level is created.
    Time complexity of FFDH: O(n·log n).
    '''
    name = "FFDH"
    def __init__(self, *args, **kwargs):
        self.policy = self.ffdh_packing
        self.strips = []

        self.NUM_STRIPS = 0
        self.LATEST_STRIP_OFF = 0
    
        super(FFDHPolicy, self).__init__(*args, **kwargs)

    def select_strip(self,rectangle):
        for strip_num, strip in enumerate(self.strips):
            strip_height, strip_height_off, occupied_strip_width = strip[0], strip[1], strip[2]

            # check if new rect is smaller than the first rectangle in the strip and
            # check if the strip has space
            if rectangle.height < strip_height and \
                rectangle.width < self.width - occupied_strip_width:
                return strip_num
        return None

    def ffdh_packing(self, rectangle):
        max_x = self.width - rectangle.width
        max_y = self.height - rectangle.height

        if max_x < 0 or max_y < 0:
            return None, None  # Rectangle is too large to fit

        strip_num = self.select_strip(rectangle)
        if strip_num is not None:
            # A strip is found.
            strip = self.strips[strip_num]
            strip_height_off, occupied_strip_width = strip[1], strip[2]
            strip[2] = occupied_strip_width + rectangle.width
            return occupied_strip_width, strip_height_off

        if self.LATEST_STRIP_OFF + rectangle.height > self.height:
            return None, None
        
        #make a new strip
        self.strips.append([rectangle.height, self.LATEST_STRIP_OFF, rectangle.width])
        self.NUM_STRIPS       = self.NUM_STRIPS + 1
        self.LATEST_STRIP_OFF = self.LATEST_STRIP_OFF + rectangle.height

        #add the new rectangle at the beginning of the strip
        return 0, self.LATEST_STRIP_OFF - rectangle.height
 
class BFDHPolicy(FFDHPolicy):
    '''
    BFDH packs the next item R (in non-increasing height) on the level,
    among those that can accommodate R, for which the residual horizontal
    space is the minimum. If no level can accommodate R, a new level is created.
    '''
    name = "BFDH"
    def __init__(self, *args, **kwargs):
        self.policy = self.ffdh_packing
        self.strips = []

        self.NUM_STRIPS = 0
        self.LATEST_STRIP_OFF = 0
        super(FFDHPolicy, self).__init__(*args, **kwargs)

    def select_strip(self,rectangle):
        minimum_residual_height = self.height
        chosen_strip_num = None
        for strip_num, strip in enumerate(self.strips):
            strip_height, strip_height_off, occupied_strip_width = strip[0], strip[1], strip[2]

            if strip_height > rectangle.height:
                if strip_height - rectangle.height < minimum_residual_height and \
                        rectangle.width < self.width - occupied_strip_width:
                    minimum_residual_height = strip_height - rectangle.height
                    chosen_strip_num = strip_num
        return chosen_strip_num

class BottomLeftPolicy(Container):
    def __init__(self, *args, **kwargs):
        self.policy = self.bottom_left_policy
        super(BottomLeftPolicy, self).__init__(*args, **kwargs)
    
    def bottom_left_policy(self, rectangle):
        x, y = 0, 0
        for rect in self.rectangles:
            if rect.x + rect.width > x:
                x = rect.x + rect.width
            if rect.y + rect.height > y:
                y = rect.y + rect.height
        return x, y
