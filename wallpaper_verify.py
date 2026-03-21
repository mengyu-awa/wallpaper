import sys
import os
import hashlib

def is_admin():
    """
    检查当前是否以管理员权限运行
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """
    以管理员权限重新启动程序
    """
    if not is_admin():
        import ctypes
        # 获取当前脚本的完整路径
        script = os.path.abspath(sys.argv[0])
        # 使用 ShellExecuteW 以管理员权限运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        sys.exit(0)

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

