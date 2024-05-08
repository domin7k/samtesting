import subprocess


methods = {
    "zlib": [1, 6],
    # "7zip": [1, 6],
    "miniz": [1, 6],
    "slz": [1],
    "libdeflate": [1, 6],
    "zlibng": [1, 6],
    "igzip": [1, 3],
    "zopfli": [1, 6],
    # "cryptopp": [1, 6],
}

for method in methods.keys():
    for i in range(len(methods[method])):
        # subprocess.run("python3 setup.py", shell=True)
        name = method + str(methods[method][i])
        subprocess.run(
            "python3 tests.py 3 -d "
            + name
            + "smallFile"
            + ' -ld "BGZF_METHOD='
            + name
            + ' LD_PRELOAD=/home/extsiebe/siebelt/7bgzf/7bgzf.so "',
            shell=True,
        )
# print(
#     "&& ".join(
#         [
#             "BGZF_METHOD="
#             + method
#             + str(methods[method][i])
#             + " LD_PRELOAD=/home/extsiebe/siebelt/7bgzf/7bgzf.so ./samtools sort -@ 16 -m 3G ../unsorted_bam_files/onepercent.bam -o ../sorted/outputOfTest/sorted"
#             + method
#             + str(methods[method][i])
#             + ".bam "
#             for method in methods.keys()
#             for i in range(len(methods[method]))
#         ]
#     ),
# )
