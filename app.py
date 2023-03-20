import random
import sys
import matplotlib.pyplot as plt
from base import *
from defines import *

class Container:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rectangles = []

    def place_rectangle(self, rectangle):
        if self.width < rectangle.width or self.height < rectangle.height:
            return False  # Rectangle is too large to fit

        x, y = self.policy(rectangle)

        if x is None or y is None:
            return False
        
        if x + rectangle.width > self.width or \
            y + rectangle.height > self.height:
            return False  # Rectangle is too wide to fit
        
        self.rectangles.append(Rectangle(x, y, rectangle.width, rectangle.height))
        return True

    def visualize(self):
        fig, ax = plt.subplots()

        # Draw container
        ax.add_patch(plt.Rectangle((0, 0), self.width, self.height, linewidth=1, edgecolor='black', facecolor='none'))

        # Draw rectangles
        for i,rect in enumerate(self.rectangles):
            ax.add_patch(plt.Rectangle((rect.x, rect.y), rect.width, rect.height, linewidth=1, edgecolor='black', facecolor=(float(i/len(self.rectangles)),0,0)))

        # Set axis limits
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])

        # Show plot
        plt.show()

    def generate_frames(self):
        '''
        Generates an image everytime a rect is placed
        '''
        for i in range(len(self.rectangles)):
            fig, ax = plt.subplots()

            # Draw container
            ax.add_patch(plt.Rectangle((0, 0), self.width, self.height, linewidth=1, edgecolor='black', facecolor='none'))

            # Draw rectangles
            for i,rect in enumerate(self.rectangles[0:i]):
                ax.add_patch(plt.Rectangle((rect.x, rect.y), rect.width, rect.height, linewidth=1, edgecolor='black', facecolor=(float(i/len(self.rectangles)),0,0)))

            # Set axis limits
            ax.set_xlim([0, self.width])
            ax.set_ylim([0, self.height])

            # Save frame
            plt.savefig(f"out/frames/frame_{i}.png")

    def calculate_utilization(self):
        used_area = 0
        for rectangle in self.rectangles:
            used_area += rectangle.width * rectangle.height
        total_area = self.width * self.height
        utilization_percentage = (used_area / total_area) * 100

        self.utilization_percentage = utilization_percentage
        self.num_of_placed_rect = len(self.rectangles)
        print(f"Num={self.num_of_placed_rect}, {utilization_percentage=}")

def generate_random_rectangles(num_rectangles, min_width, max_width, min_height, max_height):
    rectangles = []
    for i in range(num_rectangles):
        width = random.randint(min_width, max_width)
        height = random.randint(min_height, max_height)
        rectangles.append(Rectangle(0, 0, width, height))
    return rectangles

def set_seed(s=None):
    seed = random.randrange(sys.maxsize) if s==None else s
    random.seed(seed)
    print("Seed is :", seed)
    return seed

def run(visualize=True, seed=None):
    SEED = set_seed(seed)

    container = placement_policy(container_width, container_height)
    rectangles = generate_random_rectangles(num_rectangles, min_rect_width, max_rect_width, min_rect_height, max_rect_height)
    
    strike_one = True
    for rect in rectangles:
        is_placed = container.place_rectangle(rect)
        if is_placed is False:
            if strike_one is False:
                print(f"Couldn't find solution - HIT 1")
                strike_one = True
            else:
                print(f"Couldn't find solution - HIT 2. Ending")
                break
        elif strike_one is True:
            strike_one = False

    container.calculate_utilization()
    if visualize is True:
        container.visualize()
    # print(container.perf_counters)
    perf_counters = [container.perf_counters['EQUIFILL']['ADD_AND_COMP'], \
                     container.perf_counters['ALTERNATE']['ADD_AND_COMP'],
                     container.perf_counters['ALTERNATE']['MAX_OPERATION']]

    return [SEED, container.utilization_percentage, container.num_of_placed_rect] + perf_counters

def plot_stats(stats):
    util = [stat[1] for stat in stats]
    num  = [stat[2] for stat in stats]

    mean_util = sum(util) / len(util)
    mean_num  = sum(num)  / len(num)

    fig = plt.scatter(util, num, s=50, alpha=0.5)
    fig = plt.scatter([mean_util], [mean_num], s=50, alpha=0.5, color='red')
    plt.title(f"{placement_policy.name}")
    plt.xlabel("utilization")
    plt.ylabel("Num of rectangles")
    plt.savefig(f"out/{placement_policy.name}_plot.png")
    plt.show()

def dump_stats(stats):
    import csv
    with open(f"out/{placement_policy.name}_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stats)

def multiple_runs(NUM_RUNS=None):
    iter = NUM_RUNS if NUM_RUNS is not None else ITERATIONS
    stats = []

    for i in range(iter):
        stat = run(visualize=False)
        stats.append(stat)
    
    stats.sort(key=lambda x: x[1], reverse=True)

    print(stats)
    plot_stats(stats)
    dump_stats(stats)

if __name__ == '__main__':
    run(visualize=True, seed=8027613686809405079)
    # multiple_runs()