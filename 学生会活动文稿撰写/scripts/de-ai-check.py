#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
de-ai-check.py - 校园活动文稿 AI 痕迹与风味自检工具
参考 Humanizer-zh, de-AI-writing 与 humanizer 的核心过滤规则，
针对校园新闻稿（严控550-600字、去浮夸升华）和工作总结（务实复盘）进行自动化体检。
"""

import sys
import re
import argparse

# 1. 浮夸拔高与煽情空话（高校活动严厉禁止的 AI 词汇）
INFLATED_WORDS = [
    "谱写华章", "谱写新篇章", "画卷", "犹如一场盛宴", "饕餮盛宴", "润物细无声",
    "注入灵魂", "重头戏", "激荡起", "熠熠生辉", "燃爆", "盛况空前", "灵魂深处",
    "浓墨重彩", "铸就", "筑牢根基", "精神洗礼", "点亮心灯", "拨动心弦", "洗礼",
    "不可磨灭", "照亮前行之路", "奏响华彩乐章", "推向了新高潮", "掀起热潮"
]

# 2. 机械路标词与假深沉过渡（AI 习惯性填空词）
ROADMAP_WORDS = [
    "值得注意的是", "值得一提的是", "毋庸置疑", "显而易见", "总而言之", "综上所述",
    "换句话说", "不言而喻", "正所谓", "由此可见", "毋庸置疑", "理所当然",
    "诚然", "不难发现", "正如所料", "正如前述", "回望过去", "放眼未来"
]

# 3. 虚假概括与偷懒陈述（缺少实际动作与细节证据的空话）
LAZY_GENERALIZATIONS = [
    "纷纷表示受益匪浅", "引起了强烈反响", "获得了一致好评", "大家热情高涨",
    "现场气氛异常热烈", "现场掌声雷动", "令人交口称赞"
]

# 4. 通用极端负面消极与市井不体面粗俗词汇（新闻稿坚决屏蔽的基础底线；防止过拟合，具体语义由苏格拉底独立审校把关）
NEWS_NEGATIVE_WORDS = [
    "吵架", "撕破脸", "恶心", "脏乱", "打架", "丢人", "互撕", "八卦", "极度失望",
    "怨声载道", "破烂", "低俗", "发臭", "难闻", "恶习"
]

# 5. 句式结构痕迹（正则模式）
SYNTAX_PATTERNS = [
    (r"不是[^，。！？]+，?而是[^，。！？]+", "二分对照壳（“不是……而是……”）"),
    (r"不仅是一[次场个][^，。！？]+，?更是[^，。！？]+", "过度拔高二分结构（“不仅是一次……更是一场……”）"),
    (r"把[^，。！？]+(说完|理完|讲完|做完)，?再[^，。！？]+", "步骤过渡指示句（请直接从事实起笔）"),
    (r"既[^，。！？]+，?又[^，。！？]+，?还[^，。！？]+", "刻板三凑三排比（全文避免机械罗列）"),
    (r"那么，?[^，。！？]+呢[？?]", "假互动设问句（公文新闻稿避免自问自答）"),
]

def clean_press_body(text):
    """去除标题、发布信息栏、配图占位等，提取新闻稿正文纯汉字计数"""
    lines = text.splitlines()
    body_lines = []
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("#") or line_s.startswith("【配图") or line_s.startswith("!["):
            continue
        if "公告版块" in line_s or "发布部门" in line_s or "发布时间" in line_s:
            continue
        body_lines.append(line_s)
    return "\n".join(body_lines)

def count_chinese_chars(text):
    """统计汉字字符数"""
    return len(re.findall(r'[\u4e00-\u9fa5]', text))

def count_word_characters(text):
    """对齐 Microsoft Word / WPS Office 的'字符数（不计空格）'统计标准（含汉字、标点符号、英文字母与数字）"""
    return len(re.findall(r'\S', text))

def check_text(text, doc_type="news"):
    findings = []
    
    # 检查对外新闻稿中的负面不体面词汇与对内问卷明细
    if doc_type == "news":
        trivial_found = [w for w in NEWS_NEGATIVE_WORDS if w in text]
        if trivial_found:
            findings.append({
                "level": "ERROR",
                "category": "新闻稿负面不体面词汇违规",
                "message": f"对外新闻稿严禁出现市井口角或不体面消极词汇：{trivial_found}。必须做公文高阶抽象与雅化！"
            })
        if re.search(r'(回收.*问卷|问卷.*份|问卷.*建议)', text):
            findings.append({
                "level": "ERROR",
                "category": "新闻稿问卷明细违规",
                "message": "对外新闻稿严禁堆砌问卷回收份数、批评或下期整改建议等对内指标，请转入对内工作总结中呈现。"
            })
    
    # 检查浮夸煽情词
    inflated_found = [w for w in INFLATED_WORDS if w in text]
    if inflated_found:
        findings.append({
            "level": "WARN",
            "category": "空泛拔高词",
            "message": f"发现浮夸煽情/空洞拔高修辞：{inflated_found}。建议改用具体动作与客观事实替代。"
        })
    
    # 检查机械路标词
    roadmap_found = [w for w in ROADMAP_WORDS if w in text]
    if roadmap_found:
        findings.append({
            "level": "WARN",
            "category": "机械路标词",
            "message": f"发现 AI 模板化过渡词：{roadmap_found}。建议直接删去或顺接自然语义。"
        })
        
    # 检查偷懒空泛概括
    lazy_found = [w for w in LAZY_GENERALIZATIONS if w in text]
    if lazy_found:
        findings.append({
            "level": "WARN",
            "category": "虚假概括",
            "message": f"发现无事实支撑的空泛套话：{lazy_found}。建议用具体动作、问卷数据或具体作品样态替换。"
        })
        
    # 检查句式模板
    for pat, desc in SYNTAX_PATTERNS:
        matches = re.findall(pat, text)
        if matches:
            findings.append({
                "level": "WARN",
                "category": "模板句式",
                "message": f"命中{desc}，样例：'{matches[0]}'。建议拆为自然断句或客观陈述。"
            })
            
    # 新闻稿字数约束核查（对齐 Office Word 字符数不计空格：500—520 字，容差 480—540 字）
    if doc_type == "news":
        body_text = clean_press_body(text)
        word_chars = count_word_characters(body_text)
        pure_cn = count_chinese_chars(body_text)
        if word_chars < 480 or word_chars > 540:
            findings.append({
                "level": "ERROR",
                "category": "字数红线超限",
                "message": f"新闻稿正文 Word 字符数（不计空格）为 {word_chars} 字符（纯汉字 {pure_cn} 字，标点数字 {word_chars - pure_cn} 字符），未落在 [480, 540] 字符容差区间内（目标区间：500—520 字符）！请注意：Office Word/WPS 严格统计标点与数字，不能仅凭纯汉字蒙混过关！"
            })
        else:
            findings.append({
                "level": "INFO",
                "category": "字数核验达标",
                "message": f"新闻稿正文 Word 字符数：{word_chars} 字符（纯汉字：{pure_cn} 字，标点数字：{word_chars - pure_cn} 字符，对齐 Office 统计标准）。"
            })
    # 工作总结字数约束核查（严格控制 Word 字符数 800—2000 字符，防冗长拖沓）
    elif doc_type == "summary":
        word_chars = count_word_characters(text)
        pure_cn = count_chinese_chars(text)
        if word_chars < 800:
            findings.append({
                "level": "ERROR",
                "category": "工作总结字数过短",
                "message": f"工作总结 Word 字符数（不计空格）为 {word_chars} 字符（纯汉字 {pure_cn} 字），低于 800 字符底线要求，八大模块复盘不够充分！"
            })
        elif word_chars > 2000:
            findings.append({
                "level": "ERROR",
                "category": "工作总结字数超长冗长",
                "message": f"工作总结 Word 字符数（不计空格）为 {word_chars} 字符（纯汉字 {pure_cn} 字），已突破 2000 字符上限（标准区间：800—2000 字符）！篇幅过于冗长拖沓，请删去冗余碎碎念或长表格，提炼核心结论与实招对策！"
            })
        else:
            findings.append({
                "level": "INFO",
                "category": "字数核验达标",
                "message": f"工作总结 Word 字符数：{word_chars} 字符（纯汉字：{pure_cn} 字，严格控制在 800—2000 字符内）。"
            })
            
    return findings

def main():
    parser = argparse.ArgumentParser(description="校园活动文稿 AI 痕迹与风味自检脚本")
    parser.add_argument("file", help="待检测的文稿文件路径（Markdown 或文本文件）")
    parser.add_argument("--type", choices=["news", "summary"], default="news", help="文稿类型：news(新闻稿) 或 summary(工作总结)")
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)
        
    findings = check_text(content, doc_type=args.type)
    
    print("=" * 60)
    print(f"文稿体检报告 [{args.type.upper()}]: {args.file}")
    print("=" * 60)
    
    has_error = False
    for item in findings:
        tag = f"[{item['level']}]"
        print(f"{tag:<8} {item['category']}: {item['message']}")
        if item['level'] == "ERROR":
            has_error = True
            
    print("-" * 60)
    if has_error:
        print("❌ 自检未通过，存在质量红线或人称违规项，请根据上述提示修改。")
        sys.exit(1)
    else:
        print("✅ 自检通过，无高危 AI 痕迹。")
        sys.exit(0)

if __name__ == "__main__":
    main()
