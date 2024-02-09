from matplotlib import cm
import matplotlib.pyplot as plt
import json
import numpy as np
from helpers.formating import HumanBytes

# add command line argument for input file
import argparse
parser = argparse.ArgumentParser(description='Plot the file sizes and creation times')
parser.add_argument('input', type=str, help='The input file')
args = parser.parse_args()



# Load the JSON data
with open(args.input) as f:
    data = json.load(f)

# Prepare the event plot data
lines = []
legendLabels = []
for idx, (file, file_data) in enumerate(data.items()):
    for i, (process, process_data) in enumerate(file_data.items()):
        creation_time = process_data['creation_time']
        last_modified = process_data['last_modified']
        size = process_data['size']
        deleted = process_data['deleted']
        if i >= len(lines):
            lines.append([])
        lines[i].append([creation_time, last_modified, size, deleted, file])
        legendLabels.append(process.split('-o')[0].strip())


colors = iter(cm.tab20b(np.linspace(0, 1, len(lines))))

all_ys = []
all_xs = []
all_color = []
all_size = []
max_time_span = 0
legendColors = []
ticks = []
ticks_idx = []
sizes_human_readable = []
for i, process in enumerate(lines):
    color = next(colors)

    min_time = min([line[0] for line in process])
    max_time = max(max([line[3] for line in process]), max([line[1] for line in process]))
    max_time_span = max(max_time_span, max_time-min_time)

    active_ys = range(i, len(process) * (len(lines) +1), len(lines) + 1)
    active_xs = [[line[0] - min_time, line[1] - min_time] for line in process]
    #bar_texts = [r'H$\alpha$',r'H$\beta$']
    active_color = [color for line in process]
    active_size = [3 for line in process]
    a_ticks = [line[4] for line in process]
    a_sizes = [HumanBytes.format(line[2]) for line in process]

    ondisk_xs = [[line[1] - min_time, (line[3] if line[3] > 0 else max_time)- min_time] for line in process]
    ondisk_color = ['k' for _ in process]
    inactive_size = [1 for _ in process]

    all_ys = all_ys + list(active_ys) + list(active_ys)
    all_xs = all_xs + active_xs + ondisk_xs
    all_color = all_color +active_color + ondisk_color
    all_size = all_size + active_size + inactive_size
    ticks_idx = ticks_idx + list(active_ys)
    sizes_human_readable = sizes_human_readable + a_sizes + a_sizes # two times to keep length consistent
    ticks = ticks + a_ticks
    legendColors.append(color)
   

plt.figure()
plt.xticks(fontsize = 12)
plt.yticks(ticks_idx, ticks, fontsize = 8)
plt.xlim(-max_time_span*0.1, max_time_span)
plt.ylim(-0.5, max(all_ys) + 1)
plt.xlabel('time (s)', fontsize = 12)
plt.ylabel('Files', fontsize = 12)
plt.legend(handles=[plt.Line2D([0], [0], linewidth=3, color=c, label=legendLabels[process]) for process, c  in enumerate(legendColors)] + [plt.Line2D([0], [0], linewidth=1, color="k", label="file not modified but on disk")], loc='lower right')


for y,xs,c,s,t in zip(all_ys,all_xs,all_color, all_size, sizes_human_readable):
    plt.annotate('', xy = (xs[0],y), xycoords='data', xytext=(xs[1],y),
                 arrowprops=dict(arrowstyle='-', color=c, lw=s, shrinkA=0, shrinkB=0))
    if (type(c) != str): #filter inactive
        plt.annotate(t, xy = (xs[0],y), xycoords='data', xytext=(-2,0), textcoords='offset points',
                 fontsize = 8, va="center", ha='right', color=c)
plt.show()