import os
from os import scandir, rename
from os.path import splitext, exists, join
import shutil as sh
# from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ! FILL IN BELOW
# ? folder to track e.g. Windows: "C:\\Users\\UserName\\Downloads"
source_dir = "/home/public/torrents"


def is_sub_folder(name):
    boolean = name.lower().find("суб") + name.lower().find("sub")
    return True if boolean >= -1 else False


def move_subs(dest):
#     final_dest = dest + '/' + entry.name
    with os.scandir(dest) as entries:
        for entry in entries:
            if entry.is_dir():
                final_dest = dest + '/' + entry.name
                with os.scandir(final_dest) as inner_entries:
                    for inner_entry in inner_entries:
                        if inner_entry.is_dir() and is_sub_folder(inner_entry.name):
                            with os.scandir(final_dest + '/' + inner_entry.name) as inner_inner_entries:
                                for inner_inner_entry in inner_inner_entries:
                                    temp_dest = final_dest + '/' + inner_entry.name + '/' + inner_inner_entry.name
#                                     print(inner_inner_entry.name)
                                    if inner_inner_entry.is_dir() and inner_inner_entry.name != '.DS_Store':
                                        with os.scandir(temp_dest) as inner_inner_inner_entries:
                                            for inner_inner_inner_entry in inner_inner_inner_entries:
                                                if not inner_inner_inner_entry.is_dir():
                                                    sh.move(temp_dest + '/' + inner_inner_inner_entry.name, final_dest)

                                    else:
                                        if inner_inner_entry.name != '.DS_Store':
                                            sh.move(temp_dest, final_dest)


# def make_unique(dest, name):
#     filename, extension = splitext(name)
#     counter = 1
#     # * IF FILE EXISTS, ADDS NUMBER TO THE END OF THE FILENAME
#     while exists(f"{dest}/{name}"):
#         name = f"{filename}({str(counter)}){extension}"
#         counter += 1
#
#     return name
#
#
# def move_file(dest, entry, name):
#     if exists(f"{dest}/{name}"):
#         unique_name = make_unique(dest, name)
#         oldName = join(dest, name)
#         newName = join(dest, unique_name)
#         rename(oldName, newName)
#     move(entry, dest)


def remove_absent_files(dest):
    cwd = os.getcwd()
    try:
        with open(cwd + "/files_downloaded.json", "r") as outfile:
            files = json.load(outfile)
    except E as Exc:
        print(Exc)
        return
    current_file_names = []
    with os.scandir(dest) as entries:
        for entry in entries:
            current_file_names.append(entry.name)
    keys = list(files.keys())
    for key in keys:
        if key not in current_file_names:
            del (files[key])
    with open(cwd + "/files_downloaded.json", "w") as outfile:
        json.dump(files, outfile)


def in_folder(dest):
    cwd = os.getcwd()
    if not os.path.exists(cwd + "/files_downloaded.json"):
        f = open("files_downloaded.json", "w+")
        f.close()
    file_entries = {}
    with os.scandir(dest) as entries:
        for entry in entries:
            if entry.name not in file_entries:
                file_entries[entry.name] = {
                    'date_scanned': dtt.now().strftime('%D'),
                    'is_dir': (1 if entry.is_dir() else 0)
                }
    with open(cwd + "files_downloaded.json", "a+") as outfile:
        # outfile.write(file_entries)
        json.dump(file_entries, outfile)


class MoverHandler(FileSystemEventHandler):
    # ? THIS FUNCTION WILL RUN WHENEVER THERE IS A CHANGE IN "source_dir"
    # ? .upper is for not missing out on files with uppercase extensions
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                # name = entry.name
                self.move()
                # self.check_audio_files(entry, name)
                # self.check_video_files(entry, name)
                # self.check_image_files(entry, name)
                # self.check_document_files(entry, name)

    def move(self):
        move_subs(source_dir)

    def check_files(self):
        in_folder(source_dir)
        remove_absent_files(source_dir)
    #
    # def check_video_files(self, entry, name):  # * Checks all Video Files
    #     for video_extension in video_extensions:
    #         if name.endswith(video_extension) or name.endswith(video_extension.upper()):
    #             move_file(dest_dir_video, entry, name)
    #             logging.info(f"Moved video file: {name}")


# ! NO NEED TO CHANGE BELOW CODE
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
