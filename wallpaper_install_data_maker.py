import os
import json

dic = {"files":[]}
for root, dirs, files in os.walk(r"D:\Program Files\Programs\WallPaper"):
    for file in files:
        if file.lower().endswith('.png') or file.lower().endswith('.jpg'):
            dic["files"].append({"path":os.path.join(root, file)})
            with open(os.path.join(root, file), "rb") as f:
                dic["files"][len(dic["files"]) - 1]["content"] = f.read()

with open("wallpaper_install_data.py", "w") as file:
    file.write("dic = "+str(dic))