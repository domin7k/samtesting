import argparse
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

PARAM = "-@"

# ArgumentParser erstellen und Argument hinzufügen
parser = argparse.ArgumentParser(description='Plot.')
parser.add_argument('filename', type=str, help='The filename to get the csv data from.')
args = parser.parse_args()

# Read the CSV file
df = pd.read_csv(args.filename)

# print all possible keys
print(df.keys())


def extractParam(param_string):
    return param_string.strip().split("-@")[1].strip().split(" ")[0]


df[PARAM] = df['params'].apply(extractParam)
# print the mem column
print(df[PARAM])

# Plot the execution time against the 'mem' column
ax = df.plot(x=PARAM, y="execution_time", kind='line')

# Add labels and title
plt.xlabel(PARAM)
plt.ylabel('Execution Time')
plt.title(f'Execution Time vs {PARAM}')

# Set xticks
ax.set_xticks(df.index)
ax.set_xticklabels(df[PARAM])

# Show the plot
plt.show()