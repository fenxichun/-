import re
import requests
import time
import random
import os  # 新增：处理文件夹/路径
from bs4 import BeautifulSoup


def extract_outer_id_and_token(data):
    """
    先剔除note_card及其内部内容，再提取最外层的id和xsec_token
    :param data: 原始JSON字符串数据
    :return: 提取到的(id, xsec_token)列表
    """
    note_card_pattern = r'"note_card":\s*\{(?:[\s\S]*?)\}'
    cleaned_data = re.sub(note_card_pattern, '', data, flags=re.DOTALL)
    target_pattern = r'\{\s*"id":\s*"([^"]+)"[,}].*?"xsec_token":\s*"([^"]+)"'
    matches = re.findall(target_pattern, cleaned_data, flags=re.DOTALL)
    return matches


# ========== 合并后的核心函数 ==========
def save_content(desc_text, image_url, headers, root_data_path="data"):
    """
    合并文本保存+图片访问/下载逻辑：
    1. 在root_data_path下创建序列文件夹（data_1、data_2...）
    2. 保存描述文本到该文件夹的txt文件
    3. 访问并下载图片到该文件夹
    :param desc_text: 提取到的描述文本
    :param image_url: 提取到的图片URL
    :param headers: 请求头（和网页访问一致）
    :param root_data_path: 根数据文件夹（默认工程下的data）
    """
    # 确保根data文件夹存在
    if not os.path.exists(root_data_path):
        os.makedirs(root_data_path)
        print(f"📁 根文件夹 {root_data_path} 不存在，已创建")

    # 生成序列文件夹名
    existing_folders = []
    for folder in os.listdir(root_data_path):
        folder_path = os.path.join(root_data_path, folder)
        if os.path.isdir(folder_path) and folder.startswith("data_"):
            try:
                folder_num = int(folder.split("_")[1])
                existing_folders.append(folder_num)
            except (IndexError, ValueError):
                continue

    new_folder_num = max(existing_folders) + 1 if existing_folders else 1
    new_folder_name = f"data_{new_folder_num}"
    new_folder_path = os.path.join(root_data_path, new_folder_name)

    # 创建新序列文件夹
    try:
        os.makedirs(new_folder_path)
        print(f"\n📁 已创建序列文件夹：{new_folder_path}")
    except Exception as e:
        print(f"❌ 创建序列文件夹失败：{str(e)}")
        return

    # 保存描述文本
    txt_file_path = os.path.join(new_folder_path, "description.txt")
    try:
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(desc_text)
        print(f"📝 描述文本已保存到：{txt_file_path}")
    except Exception as e:
        print(f"❌ 保存描述文本失败：{str(e)}")

    # 下载图片
    if not image_url:
        print("❌ 无图片URL，跳过图片下载")
        return

    sleep_time = random.uniform(1, 3)
    print(f"\n🖼️ 准备访问图片URL：{image_url}")
    print(f"⏳ 等待 {sleep_time:.2f} 秒后下载...")
    time.sleep(sleep_time)

    # 生成图片文件名
    img_suffix = image_url.split(".")[-1].split("!")[0]
    if img_suffix not in ["jpg", "png", "webp", "jpeg"]:
        img_suffix = "jpg"
    img_file_name = f"image_{random.randint(1000, 9999)}.{img_suffix}"
    img_file_path = os.path.join(new_folder_path, img_file_name)

    try:
        response = requests.get(image_url, headers=headers, timeout=10, stream=True)
        if response.status_code == 200:
            with open(img_file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ 图片已下载到：{img_file_path}")
        else:
            print(f"❌ 图片URL访问失败！状态码：{response.status_code}")
    except requests.exceptions.Timeout:
        print(f"❌ 图片URL访问超时！")
    except requests.exceptions.ConnectionError:
        print(f"❌ 图片URL网络连接错误！")
    except Exception as e:
        print(f"❌ 图片下载出错：{str(e)}")


def insect(urls):
    """
    访问URL列表，提取description和preload图片URL，调用save_content保存到序列文件夹
    :param urls: 小红书URL列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.xiaohongshu.com/"
    }

    if not urls:
        print("❌ 没有可访问的URL！")
        return

    print("\n========== 开始访问小红书URL（模拟真人节奏） ==========")
    for idx, url in enumerate(urls, 1):
        # 网页访问间隔（2-5秒随机）
        sleep_time = random.uniform(2, 5)
        print(f"\n【第{idx}个URL】: {url}")
        print(f"⏳ 等待 {sleep_time:.2f} 秒后访问...")
        time.sleep(sleep_time)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ 网页访问成功！响应状态码：{response.status_code}")

                # 解析HTML提取目标内容
                soup = BeautifulSoup(response.text, 'lxml')

                # 提取description文本
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                desc_text = desc_tag['content'] if (desc_tag and 'content' in desc_tag.attrs) else "未提取到描述文本"
                print(f"\n📄 提取到的描述文本：{desc_text}")

                # 提取preload图片URL
                preload_img_tag = soup.find('link', attrs={'rel': 'preload', 'as': 'image'})
                img_url = preload_img_tag['href'] if (preload_img_tag and 'href' in preload_img_tag.attrs) else ""
                if img_url:
                    print(f"🔗 提取到的预加载图片URL：{img_url}")
                else:
                    print(f"❌ 未提取到preload图片URL")

                # 调用合并后的函数，保存文本+图片到序列文件夹
                save_content(desc_text, img_url, headers)

            elif response.status_code == 403:
                print(f"❌ 网页访问被拒绝（403）：建议增大间隔或更换UA")
            elif response.status_code == 404:
                print(f"❌ 网页URL无效（404）：{url}")
            else:
                print(f"❌ 网页访问失败！状态码：{response.status_code}")

        except requests.exceptions.Timeout:
            print(f"❌ 网页访问超时！")
        except requests.exceptions.ConnectionError:
            print(f"❌ 网页网络连接错误！")
        except Exception as e:
            print(f"❌ 网页访问/解析出错：{str(e)}")


if __name__ == "__main__":
    # 1. 读取数据文件
    file_path = r"xiaohongshu_data.txt"
    raw_data = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}，请检查路径！")
        # 示例数据兜底
        raw_data = """
        {
            "id": "67d25423000000000901413b",
            "model_type": "note",
            "note_card": {...},
            "xsec_token": "ABoVoOTZNOT5_vDnmGeWb7XQKF7ZJzMeFTIYEL321cWrM="
        },
        {
            "id": "66e98abf0000000027004b5a",
            "model_type": "note",
            "note_card": {...},
            "xsec_token": "ABWF6ORf4h2lT2ksZbRC_22EPzQONEczamyJdmVn_T69o="
        }
        """

    # 2. 提取id和xsec_token，拼接URL
    result = extract_outer_id_and_token(raw_data)
    xhs_urls = []
    if result:
        print("✅ 提取到最外层的id和xsec_token：")
        for idx, (item_id, xsec_token) in enumerate(result, 1):
            print(f"\n第{idx}条：")
            print(f"id: {item_id}")
            print(f"xsec_token: {xsec_token}")
            xhs_url = f"https://www.xiaohongshu.com/explore/{item_id}?xsec_token={xsec_token}"
            print(f"小红书链接: {xhs_url}")
            xhs_urls.append(xhs_url)
    else:
        print("❌ 未提取到任何数据！")

    # 3. 访问URL并保存内容到序列文件夹
    insect(xhs_urls)