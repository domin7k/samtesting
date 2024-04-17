import subprocess


for l in range(9):
    for t in [1, 2, 4, 8, 16]:
        result = subprocess.run(
            "../htslib/.bgzip -c -@ "
            + str(t)
            + " -l "
            + str(l)
            + " ../sorted/outputOfTest_1/unsortedLevel0.bam | pv > /dev/null",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        print(
            "Level: "
            + str(l)
            + " Threads: "
            + str(t)
            + " Time: "
            + str(result.stdout.decode("ascii"))
        )
