import os
import shutil
import config 
filename = 'samparams'

def make_unambigous():
    # checks the dirs in the -o parameter and makes them unambigous
    # list of previous directories
    prev_dirs = []
    lines = []
    with open(filename, 'r') as file:
        for line in file:
            if line.strip() == '':
                continue
            line = line.strip()
            out_line = line
            if '-o' in line:
                output_dir = os.path.dirname(line.split('-o')[1].strip().split(' ')[0])
                start_dir = output_dir
                while output_dir in prev_dirs:
                    print(f"Directory '{output_dir}' already exists in the samparams file.")
                    # look if the directory has a _nuber at the end and if it has, increase the number
                    # if not, add _1 to the directory
                    if (len(output_dir.split("_"))) == 1:
                        output_dir += "_1"
                    else:
                        output_dir = output_dir.split("_")[0] + f"_{int(output_dir.split('_')[1]) + 1}"
                print(f"Changed to: {output_dir}")
                # add the directory to the list of previous directories and write the line to the file
                prev_dirs.append(output_dir)
                out_line = line.replace(start_dir, output_dir)
                print(f"Changed line: {line} to {out_line}")
            lines.append(out_line)

    with open(config.TEMP_SAMPARAMS, 'w') as file:
        for line in lines:
            file.write(line + '\n')

           
make_unambigous()
with open(config.TEMP_SAMPARAMS, 'r') as file:
    for line in file:
        line = line.strip()
        if '-o' in line:
            output_dir = os.path.dirname(line.split('-o')[1].strip().split(' ')[0])
            if os.path.exists(output_dir):
                choice = input(f"The directory '{output_dir}' already exists. Do you want to delete it? (y/n): ")
                if choice.lower() == 'y':
                    shutil.rmtree(output_dir)
                    print(f"Deleted directory: {output_dir}")
                    os.makedirs(output_dir)
                else:
                    print(f"Skipping directory: {output_dir}")
            else:
                os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")


