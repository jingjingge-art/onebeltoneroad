import requests
import re
from collections import defaultdict

# 远程源列表
SOURCE_URLS = [
    "https://raw.githubusercontent.com/djshxjsh233/migu/refs/heads/main/live.txt",
    "https://raw.githubusercontent.com/willisfeng/migu/refs/heads/main/migu.m3u",
    "https://raw.githubusercontent.com/ioptu/migu-video/refs/heads/main/migu.m3u",
    "https://raw.githubusercontent.com/DEvmIb/famelack-channels-m3u/refs/heads/main/m3u/hk.m3u",
    "https://raw.githubusercontent.com/DEvmIb/famelack-channels-m3u/refs/heads/main/m3u/my.m3u",
    "https://raw.githubusercontent.com/DEvmIb/famelack-channels-m3u/refs/heads/main/m3u/tw.m3u"
]

# 国内省份关键词库
PROVINCE_KEYWORDS = {
    "北京": ["北京"],
    "上海": ["上海"],
    "广东": ["广东", "广州", "深圳"],
    "江苏": ["江苏", "南京", "苏州"],
    "浙江": ["浙江", "杭州"],
    "山东": ["山东", "济南", "青岛"],
    "四川": ["四川", "成都"],
    "河南": ["河南"],
    "河北": ["河北"],
    "湖南": ["湖南"],
    "湖北": ["湖北", "武汉"],
    "福建": ["福建", "厦门", "福州"],
    "安徽": ["安徽"],
    "辽宁": ["辽宁"],
    "陕西": ["陕西", "西安"],
    "重庆": ["重庆"],
    "天津": ["天津"],
    "广西": ["广西"],
    "江西": ["江西"],
    "云南": ["云南"],
    "贵州": ["贵州"],
    "甘肃": ["甘肃"],
    "海南": ["海南"],
    "宁夏": ["宁夏"],
    "青海": ["青海"],
    "西藏": ["西藏"],
    "新疆": ["新疆"],
    "内蒙古": ["内蒙古"],
    "黑龙江": ["黑龙江"],
    "吉林": ["吉林"],
    "山西": ["山西"],
    "香港": ["香港"],
    "澳门": ["澳门"],
    "台湾": ["台湾"]
}


def is_all_english(text: str) -> bool:
    if not text:
        return False
    clean = re.sub(r'[\s\-_0-9]', '', text)
    if len(clean) == 0:
        return False
    eng_count = sum(1 for c in clean if c.isalpha() and c.isascii())
    return eng_count / len(clean) > 0.7


def detect_group(channel_name: str) -> str:
    for group_name, keywords in PROVINCE_KEYWORDS.items():
        for kw in keywords:
            if kw in channel_name:
                return group_name
    if is_all_english(channel_name):
        return "一带一路"
    return "地下党"


def parse_m3u(content: str):
    results = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            name_match = re.search(r',([^,]+)$', line)
            if name_match:
                name = name_match.group(1).strip()
                i += 1
                while i < len(lines) and lines[i].strip().startswith("#"):
                    i += 1
                if i < len(lines):
                    url = lines[i].strip()
                    if url.startswith("http"):
                        results.append((name, url))
        elif line.startswith("http"):
            name = f"直播_{line[-30:]}"
            results.append((name, line))
        i += 1
    return results


def main():
    group_data = defaultdict(list)
    for url in SOURCE_URLS:
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            items = parse_m3u(resp.text)
            for ch_name, ch_url in items:
                group = detect_group(ch_name)
                group_data[group].append((ch_name, ch_url))
        except Exception as e:
            print(f"拉取 {url} 失败: {str(e)}")

    # 生成 merged_live.m3u
    output_m3u = ["#EXTM3U"]
    for group_name, channels in sorted(group_data.items()):
        output_m3u.append(f"#EXTINF:-1 group-title=\"{group_name}\",=====【{group_name}】=====")
        output_m3u.append("http://#")
        for ch_name, ch_url in channels:
            output_m3u.append(f'#EXTINF:-1 group-title="{group_name}",{ch_name}')
            output_m3u.append(ch_url)

    with open("merged_live.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output_m3u))
    print("✅ merged_live.m3u 生成成功")

    # ========== 仓库根目录生成【大陆电视直播.txt】 ==========
    txt_lines = []
    for group_name, channels in sorted(group_data.items()):
        txt_lines.append(f"=====【{group_name}】=====")
        for ch_name, ch_url in channels:
            txt_lines.append(f"{ch_name},{ch_url}")
        txt_lines.append("")

    with open("大陆电视直播.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
    print("✅ 大陆电视直播.txt 在根目录生成成功！")


if __name__ == "__main__":
    main()
