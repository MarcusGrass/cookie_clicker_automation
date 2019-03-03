import os

PATH = os.path.dirname(os.path.realpath(__file__))


def scan_dir():
    save_file_dir = os.path.join(PATH, "save_files")
    print(os.listdir(save_file_dir))


if __name__ == "__main__":
    scan_dir()
