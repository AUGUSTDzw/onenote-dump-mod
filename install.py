import subprocess
import sys
import requests
from urllib.parse import urlparse
import time

def test_mirror_availability(mirror_url, timeout=3):
    """测试镜像源可用性"""
    try:
        test_url = mirror_url.rstrip('/') + '/pip/'  # 测试标准路径
        response = requests.get(test_url, timeout=timeout)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

def select_available_mirror(mirrors):
    """选择第一个可用的镜像源"""
    for mirror in mirrors:
        print(f"测试镜像源: {mirror}...")
        if test_mirror_availability(mirror):
            print(f"✅ 镜像源可用: {mirror}")
            return mirror
        print(f"⛔ 镜像源不可用: {mirror}")
    
    print("⚠️ 所有镜像源均不可用，使用官方源")
    return "https://pypi.org/simple"

if __name__ == "__main__":
    # 镜像源列表（按优先级排序）
    MIRRORS = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",  # 清华
        "https://mirrors.aliyun.com/pypi/simple/",   # 阿里
        "https://pypi.mirrors.ustc.edu.cn/simple/",  # 中科大
        "https://mirrors.cloud.tencent.com/pypi/simple",  # 腾讯
        "https://repo.huaweicloud.com/repository/pypi/simple",  # 华为
        "https://pypi.douban.com/simple/"  # 豆瓣
    ]
    
    # 1. 选择可用镜像源
    selected_mirror = select_available_mirror(MIRRORS)
    trusted_host = urlparse(selected_mirror).netloc
    
    print(f"\n开始安装，使用镜像源: {selected_mirror}")
    print("=" * 50)
    
    # 2. 安装依赖包（跳过错误）
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    with open("requirements-pure.txt", "r") as f:
        for line in f:
            package = line.strip()
            if not package or package.startswith("#"):
                continue  # 跳过空行和注释
                
            try:
                command = [
                    sys.executable, "-m", "pip", "install", 
                    package, "--upgrade", 
                    "-i", selected_mirror,
                    "--trusted-host", trusted_host
                ]
                result = subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"✅ 成功安装: {package}")
                success_count += 1
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else "未知错误"
                print(f"⛔ 安装失败: {package}")
                print(f"   错误信息: {error_msg.splitlines()[-1]}")
                fail_count += 1
    
    # 3. 输出统计信息
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"安装完成! 用时: {elapsed_time:.2f}秒")
    print(f"成功: {success_count} 个, 失败: {fail_count} 个")
    print(f"使用的镜像源: {selected_mirror}")
    
    if fail_count > 0:
        print("\n⚠️ 有依赖安装失败，请检查以下包:")
        print("   - 尝试单独安装: pip install <包名> -i <镜像源>")
        print("   - 检查包名拼写是否正确")
        print("   - 确认包在当前Python版本下可用")