import os
import re

THIS_PATH = os.path.dirname(os.path.abspath(__file__))


class SaveFileHandler(object):
    def __init__(self):
        self.save_file_path = None
        self.get_save_file_path()
        self.get_latest_save_file_name()

    def get_save_file_path(self):
        up_one_dir = os.path.dirname(THIS_PATH)
        correct_dir = os.path.join(up_one_dir, "save_files")
        self.save_file_path = correct_dir

    def get_latest_save_file_name(self):
        latest_file_number = self.get_higest_save_file_number()
        file_name = get_file_name_from_number(latest_file_number)
        complete_file_with_path = os.path.join(self.save_file_path, file_name)
        return complete_file_with_path

    def get_higest_save_file_number(self):
        save_files = os.listdir(self.save_file_path)
        if len(save_files) == 0:
            raise FileNotFoundError("No savefiles present.")
        tag_numbers = list()
        for filename in save_files:
            try:
                tag_number = int(re.sub("[^0-9]", "", filename))
                if tag_number == 7:
                    continue
                tag_numbers.append(tag_number)
            except ValueError:
                pass
        if len(tag_numbers) == 0:
            tag_numbers = None
        else:
            tag_numbers = max(tag_numbers)
        return tag_numbers


def get_file_name_from_number(number=None):
    if number is None:
        return "BagoolBakery.txt"
    else:
        return "BagoolBakery ({0}).txt".format(number)


if __name__ == "__main__":
    sfh = SaveFileHandler()

    print(sfh.get_latest_save_file_name())
    del sfh
