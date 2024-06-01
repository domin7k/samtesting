import subprocess


for l in range(10):
    for t in [1, 2, 4, 8, 16]:
        result = subprocess.run(
            "../htslib/bgzip -c -@ "
            + str(t)
            + " -l "
            + str(l)
            + " ../sorted/compressed/sorteduncomp.bam | pv -f > /dev/null",
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
            + str(result.stderr.decode("ascii"))
        )
