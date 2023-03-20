import matplotlib.pyplot as plt
from defines import *
import csv

def plot_stats(stats, index, name, policy_name='Custom'):
    util = [stat[index] for stat in stats]
    num  = [stat[2] for stat in stats]

    mean_stat = sum(util) / len(util)
    mean_num  = sum(num)  / len(num)

    print(f"{name}: NUM:{mean_num}, STAT:{mean_stat}, RATIO:{mean_stat/mean_num}")
    fig = plt.scatter(util, num, s=50, alpha=0.5)
    fig = plt.scatter([mean_stat], [mean_num], s=50, alpha=0.5, color='red')
    plt.title(f"{policy_name} policy - {name}")
    plt.xlabel(f"{name}")
    plt.ylabel("Num of rectangles")
    plt.savefig(f"out/{policy_name}_perf_plot_{name}.png")
    plt.show()

def read_stats_from_file(file):
    with open(file, newline='') as csvfile:
        stats = []
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            new_row = [float(element) for element in row]
            stats.append(new_row)

        return stats
    
if __name__ == '__main__':
    FILE_NAME = 'out/custom_data.csv'

    stats = read_stats_from_file(FILE_NAME)

    if stats is not None:
        plot_stats(stats, 3, 'equifill_add_n_comp')
        plot_stats(stats, 4, 'alternate_add_n_comp')
        plot_stats(stats, 5, 'alternate_max')