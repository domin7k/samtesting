import argparse


def open_files(n, listen):
    a = []
    if listen:
        for i in range(n):
            input("Press Enter to open the next file...")
            print(f"Opening file {i+1}")
            a.append(open(f"./files/file_{i+1}.txt", "w"))
            a.append(open(f"./files/file_{i+1}_1.txt", "w"))
    else:
        for i in range(n):
            print(f"Opening file {i+1}")
            a.append(open(f"./files/file_{i+1}.txt", "w"))
    for file in a:
        file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, help="Number of files to open")
    parser.add_argument(
        "-l", action="store_true", help="Listen for input to open files"
    )
    args = parser.parse_args()

    if args.n is None:
        print("Please provide the number of files to open using the -n parameter.")
    else:
        open_files(args.n, args.l)
