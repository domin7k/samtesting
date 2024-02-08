import argparse
import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

PARAM = "-@"

def extractParam(param_string):
    if type(param_string) is not str:
        return "No Param"
    return param_string.strip().split("-@")[1].strip().split(" ")[0]

# ArgumentParser erstellen und Argument hinzufügen
parser = argparse.ArgumentParser(description='Plot.')
parser.add_argument('filename', type=str, help='The filename to get the csv data from.')
parser.add_argument("-d1",dest='desciption1', type=str, help='The description of the first csv file.', default=None, nargs='?')
parser.add_argument("-d2",dest='desciption2', type=str, help='The description of the second csv file.', default=None, nargs='?')
# optionales zweites argument für zweites input csv
parser.add_argument('-f', dest="filename2",type=str, help='The filename to get the csv data from.', default=None, nargs='?')


args = parser.parse_args()



# Read the CSV file
df = pd.read_csv(args.filename)

if args.filename2:
    df2 = pd.read_csv(args.filename2)
    df2[PARAM] = df2['params'].apply(extractParam)
    df2 = df2.sort_values(by=[PARAM])

print(df['params'])

df[PARAM] = df['params'].apply(extractParam)

df = df.sort_values(by=[PARAM])
# print the mem column
print(df[PARAM])

# Plot the execution time against the 'mem' column

plt.plot(df[PARAM].to_numpy(), df['execution_time'].to_numpy())
if args.filename2:
    plt.plot(df2[PARAM].to_numpy(), df2['execution_time'].to_numpy())
# Add labels and title
plt.xlabel(PARAM)
plt.ylabel('Execution Time')
plt.title(f'Execution Time vs {PARAM}')

# Set xticks
plt.xticks(df[PARAM])

if args.desciption1 and args.desciption2:
    plt.legend([args.desciption1, args.desciption2])

fig1 = plt.gcf()
# Show the plot
plt.show()
if(input("Do you want to save the plot? (y/n) ").lower() == "y"):
    if (args.filename2):
        
        fig1.savefig(f"{os.path.dirname(args.filename)+'/'+os.path.basename(args.filename)}_vs_{args.filename2.split('/')[-2]}_plot.png")
    else:
        fig1.savefig(f"{os.path.dirname(args.filename) +'/'+ os.path.basename(args.filename).split('.')[0]}_plot.png")