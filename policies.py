import random
from base import *
from app import Container
import numpy as np

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

class CustomPolicy(Container):
    '''
    Custom policy has specific lanes for each height
    '''
    name = "custom"
    def __init__(self, *args, **kwargs):
        self.policy = self.fixed_lane_packing

        self.strip_grouping   = [[12,4], [11,5], [10,6], [9,7], [8,8],  [16],[16],[16]]
        self.LARGEST_STRIP_GRP_INDEX = 5 # 16 blocks
        self.NUM_STRIP_GROUPS = 8

        self.strip_heights           = [ 12, 4,  11,  5,  10,  6,  9, 7,  8,  8, 16, 16,16]
        self.strip_alternate_heights = [[11],[],[10],[4],[9],[5],[8],[6],[7],[7], [],[],[]]

        self.strip_height_off = [0]+list(np.cumsum(self.strip_heights)[:-1])
        self.occupied_strip_width = [0 for _ in range(len(self.strip_heights))]
        self.invalid_range    = [None for _ in range(len(self.strip_heights))]
    
        self.NUM_STRIPS = len(self.strip_heights)
        self.LATEST_STRIP_OFF = 0

        self.perf_counters = {'EQUIFILL'  :{'ADD_AND_COMP':0, 'INVALID_2_OPS':0, 'NON-INVALID_1_OP':0, 'NATIVE':0, 'ALTERNATE':0}, 
                              'ALTERNATE' :{'ADD_AND_COMP':0, 'MAX_OPERATION':0}}
        super(CustomPolicy, self).__init__(*args, **kwargs)

    def native_search(self,rectangle):
        '''
        Returns if the rect can fit in (all of) its native rows 
        '''
        if rectangle.height in [13,14,15]:
            rec_height = 16
        else:
            rec_height = rectangle.height
        
        for strip_num, strip_h in enumerate(self.strip_heights):
            # if the height of the rectangle is the lane height and there is space to fit
            if (strip_h == rec_height):
                ret =  self.check_if_rect_fits_in_strip(strip_num, rectangle)
                if ret is not (None, None):
                    return ret

        return None, None

    def check_if_rect_fits_in_strip(self, strip_num, rectangle):
        '''
        for a given strip checks if the rectangle fits in the strip, with a consideration
        for invalid range in that strip
        '''
        if self.invalid_range[strip_num] is not None:
            self.perf_counters['EQUIFILL']['INVALID_2_OPS']      += 1
            #BEFORE THE INVALID BLOCK
            self.perf_counters['EQUIFILL']['ADD_AND_COMP'] += 1
            if(self.occupied_strip_width[strip_num] + rectangle.width <= self.invalid_range[strip_num][0]):
                return strip_num, -1
            #AFTER THE INVALID BLOCK
            self.perf_counters['EQUIFILL']['ADD_AND_COMP'] += 1
            if(self.invalid_range[strip_num][1] + rectangle.width <= self.width):
                return strip_num, 1
        else:
            self.perf_counters['EQUIFILL']['NON-INVALID_1_OP']  += 1
            #NO INVALID BLOCK PRESENT
            self.perf_counters['EQUIFILL']['ADD_AND_COMP'] += 1
            if(self.occupied_strip_width[strip_num] + rectangle.width <= self.width):
                return strip_num, None
        return None, None
    
    def equi_fill_search(self, rectangle):
        '''
        Returns if the rect can fit in (all of) its native rows and 
        the alternative height strips.
        Selects the one which is lesser filled globally 
        '''
        if rectangle.height in [13,14,15]:
            rec_height = 16
        else:
            rec_height = rectangle.height
        
        possible_strip_index = []
        #native strip heights SEARCH
        for strip_num, strip_h in enumerate(self.strip_heights):
            if strip_h == rec_height:
                self.perf_counters['EQUIFILL']['NATIVE']      += 1
                ret =  self.check_if_rect_fits_in_strip(strip_num, rectangle)
                if ret is not (None, None):
                    possible_strip_index.append(strip_num)
                
        #alternate strip heights SEARCH
        for strip_num, strip_h_l in enumerate(self.strip_alternate_heights):
            for strip_h in strip_h_l:
                if strip_h == rec_height:
                    self.perf_counters['EQUIFILL']['ALTERNATE']      += 1
                    ret =  self.check_if_rect_fits_in_strip(strip_num, rectangle)
                    if ret is not (None, None):
                        #ignore blocks in which invalid block is present - NOT NEEDED
                        # if (ret[1] is None or (ret[1] is not None and ret[1]<0)):
                        possible_strip_index.append(strip_num)
        
        if len(possible_strip_index) != 0:
            # EQUIFILL SEARCH SUCCESSFUL
            # compare fill percentage among options
            # get the strip with min fill percent
            min_strip_index = possible_strip_index[0]
            fill_precent    = self.occupied_strip_width[min_strip_index]
            for strip_num in possible_strip_index:
                if fill_precent > self.occupied_strip_width[strip_num]:
                    min_strip_index = strip_num
                    fill_precent    = self.occupied_strip_width[strip_num]

            return self.check_if_rect_fits_in_strip(min_strip_index, rectangle)

        return None, None

    def alternate_search(self, rectangle):
        '''
        Starting from the bottom, looks from a strip group (2 or 1 strip)
        where is enough width space to fit incoming rectangle
        '''
        for strip_grp_num, values_l in enumerate(self.strip_grouping):
            if len(values_l) == 2:
                # if even strip has invalid
                if self.invalid_range[strip_grp_num*2] is not None:
                    strip_occupied_e = self.invalid_range[strip_grp_num*2][1]
                else:
                    strip_occupied_e = self.occupied_strip_width[strip_grp_num*2]
                
                # if odd strip has invalid
                if self.invalid_range[strip_grp_num*2+1] is not None:
                    strip_occupied_o = self.invalid_range[strip_grp_num*2+1][1]
                else:
                    strip_occupied_o = self.occupied_strip_width[strip_grp_num*2+1]

                self.perf_counters['ALTERNATE']['MAX_OPERATION'] += 1
                max_occupied_width = max(strip_occupied_e, strip_occupied_o)
                self.perf_counters['ALTERNATE']['ADD_AND_COMP'] += 1
                if (rectangle.width <= self.width - max_occupied_width):
                    return strip_grp_num
            else: #fill into 16 blocks
                index = strip_grp_num - self.NUM_STRIP_GROUPS
                self.perf_counters['ALTERNATE']['ADD_AND_COMP'] += 1
                if (rectangle.width <= self.width - self.occupied_strip_width[index]):
                    print("placing in 16 blocks at ", index)
                    return strip_grp_num

        return None
    
    def fixed_lane_packing(self, rectangle):
        max_x = self.width - rectangle.width
        max_y = self.height - rectangle.height
        if max_x < 0 or max_y < 0:
            return None, None  # Rectangle is too large to fit

        # EQUIFILL - SEARCH
        strip_num, loc = self.equi_fill_search(rectangle)
        print(rectangle.height, strip_num)
        if strip_num is not None:
            # EQUIFILL - UPDATION
            if (loc == None or loc<0):
                # (1) there is no invalid range in the strip, place the rect regularly
                # (2) we are placing the new block before the invalid range
                occupied_strip_width = self.occupied_strip_width[strip_num]
                self.occupied_strip_width[strip_num] = self.occupied_strip_width[strip_num] + rectangle.width
                return occupied_strip_width, self.strip_height_off[strip_num]
            elif(loc>0):
                #extend the invalid range and dont change the occupied_strip_width for the strip
                starting_pt = self.invalid_range[strip_num][1]
                self.invalid_range[strip_num][1] = self.invalid_range[strip_num][1] + rectangle.width
                return starting_pt, self.strip_height_off[strip_num]


        # ALTERNATE - SEARCH
        strip_grp_num = self.alternate_search(rectangle)
        print("ALTERNATE", rectangle.height, strip_grp_num)
        if strip_grp_num is not None:
            # ALTERNATE - UPDATION
            if strip_grp_num < self.LARGEST_STRIP_GRP_INDEX:
                even_row_num, odd_row_num = 2*strip_grp_num, 2*strip_grp_num+1

                if self.occupied_strip_width[strip_grp_num*2] > self.occupied_strip_width[strip_grp_num*2+1]:
                    #even strip is longer
                    longer_strip = strip_grp_num*2
                    other_strip = strip_grp_num*2 + 1
                else:
                    #odd strip is longer
                    other_strip = strip_grp_num*2
                    longer_strip = strip_grp_num*2 + 1

                max_occupied_width = self.occupied_strip_width[longer_strip]

                if self.invalid_range[other_strip] is None:
                    #there was no invalid block in this strip, earlier
                    self.invalid_range[other_strip] = [max_occupied_width, max_occupied_width + rectangle.width]
                else:
                    self.invalid_range[other_strip][1] += rectangle.width
                self.occupied_strip_width[longer_strip] = max_occupied_width + rectangle.width

                return max_occupied_width, self.strip_height_off[even_row_num]
            else: # 16 blocks
                index = strip_grp_num - self.NUM_STRIP_GROUPS
                max_occupied_width = self.occupied_strip_width[index]
                self.occupied_strip_width[index] = max_occupied_width + rectangle.width
                return max_occupied_width, self.strip_height_off[index]

        # FAILED - couldn't place
        return None, None