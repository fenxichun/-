import requests
import re
from cookies import cookies
from cookies import headers
from cookies import json_data
import time
import random
import json

#参考网址
#大页面：全部和图文没有区别
#https://www.xiaohongshu.com/search_result/?keyword=%25E4%25BA%258C%25E6%25AC%25A1%25E5%2585%2583&source=unknown&type=51
#数据包
#https://edith.xiaohongshu.com/api/sns/web/v1/search/notes
#帖子
# 1 https://www.xiaohongshu.com/explore/66e98abf0000000027004b5a?xsec_token=ABWF6ORf4h2lT2ksZbRC_22EPzQONEczamyJdmVn_T69o=&xsec_source=pc_search&source=unknown
# 2 https://www.xiaohongshu.com/explore/66c9c66d000000001f03a2ea?xsec_token=ABBiCSi_0Mfr33BueRcR6HaMcq_imsW-Sxy9CDqcWvQTU=&xsec_source=pc_search&source=unknown
#封面图片（一般封面图片后面就是这个帖子其它的图片）
# 1 https://sns-webpic-qc.xhscdn.com/202601182051/070f9a38b9f5568697ef50278d2ff261/1040g008317rodoaik6005opd7d7ovc2li1bajv8!nd_prv_wlteh_webp_3
# 2 https://sns-webpic-qc.xhscdn.com/202601182100/5f1ecdd1da7dbcbbbab06e29c106f122/1040g2sg316snmt6ik4dg43miurbrkgiiv5tckr0!nd_prv_wlteh_webp_3
#图片等的数据包（就是帖子的url）
# 1 https://www.xiaohongshu.com/explore/66e98abf0000000027004b5a?xsec_token=ABWF6ORf4h2lT2ksZbRC_22EPzQONEczamyJdmVn_T69o=&xsec_source=pc_search&source=unknown
# 2 https://www.xiaohongshu.com/explore/66c9c66d000000001f03a2ea?xsec_token=ABBiCSi_0Mfr33BueRcR6HaMcq_imsW-Sxy9CDqcWvQTU=&xsec_source=pc_search&source=unknown
#信息匹配：
#

#所以在大页面的数据包里找到帖子的url，然后挨个访问然后匹配出数据就行

# 正则表达式：匹配最外层的 id 和 xsec_token
def extract_outer_id_and_token(data):
    """
    先剔除note_card及其内部内容，再提取最外层的id和xsec_token
    :param data: 原始JSON字符串数据
    :return: 提取到的(id, xsec_token)列表
    """
    # ========== 第一步：剔除note_card及其内部所有内容 ==========
    note_card_pattern = r'"note_card":\s*\{(?:[\s\S]*?)\}'
    cleaned_data = re.sub(note_card_pattern, '', data, flags=re.DOTALL)

    # ========== 第二步：提取最外层的id和xsec_token ==========
    target_pattern = r'\{\s*"id":\s*"([^"]+)"[,}].*?"xsec_token":\s*"([^"]+)"'
    matches = re.findall(target_pattern, cleaned_data, flags=re.DOTALL)

    return matches


def insect(urls):
    """
    访问传入的URL列表，打印每个URL的访问结果
    :param urls: 小红书URL列表（字符串列表）
    """
    # 设置请求头：模拟浏览器访问，避免被小红书反爬（关键！）
    response = requests.post(
        'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    for idx, url in enumerate(urls, 1):
        # 1. 生成随机时间间隔（2-5秒，可根据需要调整）
        # 随机间隔比固定间隔更像真人（避免被识别为爬虫）
        sleep_time = random.uniform(2, 5)
        print(f"\n【第{idx}个URL】: {url}")
        print(f"⏳ 等待 {sleep_time:.2f} 秒后访问...")

        # 2. 执行时间间隔
        time.sleep(sleep_time)

    if not urls:
        print("❌ 没有可访问的URL！")
        return

    print("\n========== 开始访问小红书URL ==========")
    for idx, url in enumerate(urls, 1):
        print(f"\n【第{idx}个URL】: {url}")
        try:
            # 发送GET请求，设置超时时间（避免卡壳）
            response = requests.get(url, headers=headers, timeout=10)

            # 检查请求是否成功（状态码200表示成功）
            if response.status_code == 200:
                print(f"✅ 访问成功！响应状态码：{response.status_code}")
                # 可选：打印响应内容的前500个字符（预览）
                # print(f"响应内容预览：{response.text[:500]}")
            else:
                print(f"❌ 访问失败！响应状态码：{response.status_code}")

        except requests.exceptions.Timeout:
            print(f"❌ 访问超时！（超过10秒未响应）")
        except requests.exceptions.ConnectionError:
            print(f"❌ 网络连接错误！（可能是网络不通/URL无效）")
        except Exception as e:
            print(f"❌ 访问出错：{str(e)}")


if __name__ == "__main__":
    # 1. 读取文件（替换为你的实际文件路径）
    file_path = r"xiaohongshu_data.txt"
    raw_data = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}，请检查路径！")
        # 若文件不存在，使用示例数据测试
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

    # 2. 提取id和xsec_token
    result = extract_outer_id_and_token(raw_data)

    # 3. 拼接URL列表
    xhs_urls = []
    if result:
        print("✅ 提取到最外层的id和xsec_token：")
        for idx, (item_id, xsec_token) in enumerate(result, 1):
            print(f"\n第{idx}条：")
            print(f"id: {item_id}")
            print(f"xsec_token: {xsec_token}")
            # 拼接URL并加入列表
            xhs_url = f"https://www.xiaohongshu.com/explore/{item_id}?xsec_token={xsec_token}"
            print(f"小红书链接: {xhs_url}")
            xhs_urls.append(xhs_url)
    else:
        print("❌ 未提取到任何数据，请检查原始数据格式！")

    # 4. 调用insect函数访问所有URL
    insect(xhs_urls)