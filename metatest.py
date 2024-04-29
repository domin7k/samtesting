import subprocess


methods = {
    "zlib": [1, 6],
    # "7zip": [1, 6],
    "zopfli": [1, 6],
    "miniz": [1, 6],
    "slz": [1],
    "libdeflate": [1, 6],
    "zlibng": [1, 6],
    "igzip": [1, 3],
    # "cryptopp": [1, 6],
}

for method in methods.keys():
    for i in range(2):
        subprocess.run("python3 setup.py", shell=True)
        name = method + str(methods[method][i])
        subprocess.run(
            "python3 tests.py 1 -d "
            + name
            + ' -ld "BGZF_METHOD='
            + name
            + ' LD_PRELOAD=/home/extsiebe/siebelt/7bgzf/7bgzf.so "',
            shell=True,
        )
