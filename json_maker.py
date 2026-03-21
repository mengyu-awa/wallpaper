import hashlib
import os
import json

def get_file_sha256(file_path, chunk_size=8192):
    """
    计算文件的 SHA256 哈希值（支持大文件，内存友好）
    :param file_path: 文件路径
    :param chunk_size: 分块读取大小（默认 8KB）
    :return: SHA256 十六进制字符串，失败返回 None
    """
    try:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    except FileNotFoundError:
        return None  # 文件不存在，返回None以便重新安装
    except PermissionError:
        return None
    except Exception as e:
        return None

path = input("文件路径:")
dic = {"files":[]}
for root, dirs, files in os.walk(path):
    print(root)
    for file in files:
        print(file)
        dic["files"].append({"path":os.path.join(root, file), "sha256":get_file_sha256(os.path.join(root, file))})

with open("sha.json","w") as file:
    file.write(json.dumps(dic, ensure_ascii=False, indent=2))