import sys
import os
import hashlib
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

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


def mt_content(url, num_threads=4, timeout=30, headers=None, **kwargs):
    """
    多线程下载，直接替代 requests.get(url).content

    参数:
        url: 下载链接
        num_threads: 线程数（默认4）
        timeout: 超时时间
        headers: 请求头
        **kwargs: 传递给 requests 的其他参数

    返回:
        bytes: 文件内容（与 requests.content 相同类型）

    使用示例:
        # 原来: data = requests.get(url).content
        # 现在: data = mt_content(url)
    """

    session = requests.Session()
    request_headers = headers or {}

    # 1. 获取文件大小
    try:
        resp = session.head(url, headers=request_headers, timeout=timeout, allow_redirects=True, **kwargs)
        file_size = int(resp.headers.get('content-length', 0))
        accept_ranges = resp.headers.get('accept-ranges', '')
    except Exception as e:
        file_size = 0
        accept_ranges = ''

    # 如果文件太小或服务器不支持Range， fallback 到单线程
    if file_size < 1024 * 1024 or 'bytes' not in accept_ranges.lower():
        return session.get(url, headers=request_headers, timeout=timeout, **kwargs).content

    # 2. 多线程下载
    chunk_size = file_size // num_threads
    chunks = {}  # {index: bytes}
    lock = threading.Lock()

    def download_range(start, end, idx):
        """下载指定字节范围"""
        range_headers = {**request_headers, 'Range': f'bytes={start}-{end}'}
        resp = session.get(url, headers=range_headers, timeout=timeout, stream=True, **kwargs)
        data = resp.content
        with lock:
            chunks[idx] = data

    # 3. 启动线程池
    threads = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(num_threads):
            start = i * chunk_size
            end = (start + chunk_size - 1) if i < num_threads - 1 else file_size - 1
            futures.append(executor.submit(download_range, start, end, i))

        # 等待所有完成
        for future in as_completed(futures):
            future.result()  # 触发异常如果发生错误

    # 4. 按顺序合并
    buffer = BytesIO()
    for i in range(num_threads):
        buffer.write(chunks[i])

    return buffer.getvalue()


if __name__ == '__main__':
    run_as_admin()
    j = requests.get("https://mengyu-awa.github.io/wallpaper/website/sha.json").json()
    paths = []
    for i in j["files"]:
        paths.append(i["path"])
    for root, dirs, files in os.walk("D:\\Program Files\\Programs\\WallPaper"):
        for file in files:
            if file.lower().endswith('.png') or file.lower().endswith('.jpg'):
                if not os.path.join(root, file) in paths:
                    os.remove(os.path.join(root, file))
                else:
                    if get_file_sha256(os.path.join(root, file)) != j["files"][os.path.join(root, file)]["sha256"]:
                        pass


