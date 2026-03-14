import os
import sys
import random
import time
import ctypes
from pathlib import Path

# Windows API 常量
SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

# 支持的图片格式
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}


def get_script_directory():
    """获取程序自身所在目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行
        return os.path.dirname(os.path.abspath(__file__))


def collect_images(directory):
    """递归收集目录及子目录下的所有图片"""
    images = []
    path = Path(directory)

    for ext in SUPPORTED_EXTENSIONS:
        # 使用 rglob 递归查找所有子目录
        images.extend(path.rglob(f'*{ext}'))
        # 同时查找大写扩展名
        images.extend(path.rglob(f'*{ext.upper()}'))

    # 去重并转换为绝对路径字符串
    unique_images = list(set([str(img.resolve()) for img in images]))
    return unique_images


def set_wallpaper(image_path):
    """使用Windows API设置壁纸"""
    try:
        # 将路径转换为Windows格式
        abs_path = os.path.abspath(image_path)

        # 使用SystemParametersInfoW设置壁纸 (支持Unicode)
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )

        if result:
            #print(f"✓ 壁纸已切换为: {os.path.basename(abs_path)}")
            #print(f"  完整路径: {abs_path}")
            return True
        else:
            #print("✗ 设置壁纸失败")
            return False

    except Exception as e:
        #print(f"✗ 设置壁纸时出错: {e}")
        return False


def main():
    """主循环"""
    script_dir = get_script_directory()
    #print(f"程序所在目录: {script_dir}")
    #print("=" * 50)

    # 首次运行收集图片
    images = collect_images(script_dir)

    if not images:
        #print("错误: 未在程序目录及其子目录下找到任何图片")
        #print(f"支持的格式: {', '.join(SUPPORTED_EXTENSIONS)}")
        #input("按回车键退出...")
        return

    #print(f"找到 {len(images)} 张图片")
    #print("=" * 50)

    # 主循环
    while True:
        # 每次切换前重新扫描（可能新增图片）
        images = collect_images(script_dir)

        if not images:
            #print("警告: 未找到可用图片，等待下次扫描...")
            time.sleep(600)  # 10分钟后重试
            continue

        # 随机选择一张图片
        selected = random.choice(images)

        # 设置壁纸
        set_wallpaper(selected)

        #print(f"\n下次切换时间: 10分钟后 ({time.strftime('%H:%M:%S', time.localtime(time.time() + 600))})")
        #print("-" * 50)

        # 等待10分钟
        time.sleep(600)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
        #print("\n\n程序已手动停止")
    except Exception as e:
        pass
        #print(f"\n程序发生错误: {e}")
        #input("按回车键退出...")