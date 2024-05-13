import pandas as pd

import matplotlib.pyplot as plt

folders = [
    "2024-05-09T07:09:31.059725igzip3BigFile",
    "2024-05-09T06:39:14.723515igzip1BigFile",
    "2024-05-09T06:07:02.477866zlibng6BigFile",
    "2024-05-09T05:36:47.239072zlibng1BigFile",
    "2024-05-09T05:06:28.728813libdeflate6BigFile",
    "2024-05-09T04:36:44.958399libdeflate1BigFile",
    "2024-05-09T04:06:25.544676slz1BigFile",
    "2024-05-09T02:03:53.703192zlib6BigFile",
    "2024-05-09T01:33:22.351211zlib1BigFile",
]

execution_times = []

for folder in folders:
    file_path = f"/home/dominik/fusessh/{folder}/results.csv"  # Replace with the actual file path
    df = pd.read_csv(file_path)
    avg_execution_time = df["io_wait"].mean()
    execution_times.append(avg_execution_time)

plt.bar(folders, execution_times)
plt.xlabel("Folders")
plt.ylabel("Average Execution Time")
plt.title("Average Execution Time in Folders")
plt.xticks(rotation=90)
plt.show()
