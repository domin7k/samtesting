import subprocess

subprocess.run(["git", "pull"])
subprocess.run(["(cd ../samtools/ && git pull)"], shell=True)
subprocess.run(["(cd ../htslib/ && git pull"], shell=True)
subprocess.run(["(cd ../samtools/ && make clean)"], shell=True)
subprocess.run(["(cd ../samtools/ && make)"], shell=True)
subprocess.run(["(cd ../htslib/ && make clean)"], shell=True)
subprocess.run(["(cd ../htslib/ && make)"], shell=True)

subprocess.run(["python3", "prepare_dirs.py"])
