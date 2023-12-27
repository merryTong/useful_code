import os

def find_image(path):
    name_list = []
    for maindir, subdir, sonpath_list in os.walk(path):
        for sonpath in sonpath_list:
            sonpath_full = os.path.join(maindir, sonpath)
            print(sonpath_full)
            if sonpath_full.rsplit(".",1)[1].lower() in set(["jpg", "jpeg", "png"]):
                name_list.append(sonpath_full)
    return name_list