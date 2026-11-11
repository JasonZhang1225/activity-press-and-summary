#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
word_count.py - 校园活动文稿专业字数与分块结构统计工具
完全对齐 Microsoft Word / WPS Office 底层统计标准（字符数不计空格、字数、纯汉字数）。
原生支持 .md 与 .docx（零外部第三方依赖，标准库 zipfile 解析）。

支持能力：
  1. Office Word / WPS 底层一致的“字符数（不计空格）”计算
  2. 新闻稿分段/分块精细化切片分析（导语、主体过程、成果、展望各段字数与正文占比）
  3. 过程段占比（是否超 30% 上限红线）智能诊断
  4. 工作总结八大模块分章节字数统计
  5. 双轨对照分析：彻底揭示 AI 宣称字数（纯汉字）与 Word 实际字数（非空白字符）的偏差根源
"""

import sys
import os
import re
import argparse
import zipfile
import xml.etree.ElementTree as ET

def count_pure_chinese(text):
    """纯汉字字符数 [\u4e00-\u9fa5]"""
    return len(re.findall(r'[\u4e00-\u9fa5]', text))

def count_word_characters(text):
    """
    对齐 Microsoft Word / WPS Office 的“字符数（不计空格）”：
    统计所有非空白字符，包含汉字、全半角标点符号、英文字母、阿拉伯数字。
    这是体制内高校公文与老师肉眼审核的最权威标准！
    """
    return len(re.findall(r'\S', text))

def count_office_words(text):
    """
    模拟 Office Word 状态栏默认显示的“字数 (Words)”：
    汉字每个算 1 个字；英文单词以空格/标点分界算 1 个词；连续数字算 1 个词。
    """
    en_words = re.findall(r'[A-Za-z]+', text)
    num_words = re.findall(r'\d+', text)
    cn_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    return len(cn_chars) + len(en_words) + len(num_words)

def read_text_from_file(filepath):
    """从 .md, .txt 或 .docx 读取文本段落列表"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".docx":
        paragraphs = []
        try:
            with zipfile.ZipFile(filepath) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                    texts = [
                        node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                        if node.text
                    ]
                    line = "".join(texts).strip()
                    if line:
                        paragraphs.append(line)
            return "\n\n".join(paragraphs), paragraphs
        except Exception as e:
            print(f"解析 .docx 失败: {e}，尝试普通文本读取...")
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return content, [line.strip() for line in content.splitlines() if line.strip()]
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content, [line.strip() for line in content.splitlines() if line.strip()]

def parse_news_blocks(lines):
    """解析新闻稿的结构分块"""
    title = ""
    info_block = ""
    picture_tags = []
    body_paragraphs = []

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") and not title:
            title = s.lstrip("#").strip()
        elif any(k in s for k in ["公告版块", "发布部门", "发布范围", "发布时间", "信息发布"]):
            info_block = s
        elif s.startswith("【配图") or s.startswith("![") or s.startswith("[配图") or re.match(r'^图\d+\s+', s):
            picture_tags.append(s)
        elif not title and len(s) < 45 and ("举办" in s or "开展" in s or "举行" in s or "团辅" in s or "活动" in s) and len(body_paragraphs) == 0:
            title = s
        else:
            body_paragraphs.append(s)

    blocks = []
    n = len(body_paragraphs)
    if n == 0:
        pass
    elif n == 1:
        blocks.append(("正文合并段", body_paragraphs[0]))
    elif n == 4:
        blocks.append(("一、导语段", body_paragraphs[0]))
        blocks.append(("二、主体过程段", body_paragraphs[1]))
        blocks.append(("三、成果展示段", body_paragraphs[2]))
        blocks.append(("四、意义展望段", body_paragraphs[3]))
    elif n == 3:
        blocks.append(("一、导语段", body_paragraphs[0]))
        blocks.append(("二、主体过程与成果", body_paragraphs[1]))
        blocks.append(("三、意义展望段", body_paragraphs[2]))
    elif n == 5:
        blocks.append(("一、导语段", body_paragraphs[0]))
        blocks.append(("二、过程段(1)", body_paragraphs[1]))
        blocks.append(("二、过程段(2)", body_paragraphs[2]))
        blocks.append(("三、成果展示段", body_paragraphs[3]))
        blocks.append(("四、意义展望段", body_paragraphs[4]))
    else:
        for idx, p in enumerate(body_paragraphs):
            blocks.append((f"第 {idx+1} 自然段", p))

    return title, info_block, picture_tags, blocks

def parse_summary_blocks(content):
    """解析工作总结的八大模块分块"""
    sections = []
    current_title = "前言/引言"
    current_lines = []

    for line in content.splitlines():
        s = line.strip()
        if re.match(r'^(#{1,3}\s+)?[一二三四五六七八0-9]、', s):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines)))
                current_lines = []
            current_title = s.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines)))

    return sections

def analyze_news(content, paragraphs, filepath=""):
    title, info_block, picture_tags, blocks = parse_news_blocks(paragraphs)

    body_total_word_chars = 0
    body_total_pure_cn = 0

    block_stats = []
    for label, text in blocks:
        wc = count_word_characters(text)
        cn = count_pure_chinese(text)
        punct_num = wc - cn
        body_total_word_chars += wc
        body_total_pure_cn += cn
        block_stats.append({
            "label": label,
            "text": text,
            "word_chars": wc,
            "pure_cn": cn,
            "punct_num": punct_num
        })

    title_wc = count_word_characters(title) if title else 0
    title_cn = count_pure_chinese(title) if title else 0
    info_wc = count_word_characters(info_block) if info_block else 0
    info_cn = count_pure_chinese(info_block) if info_block else 0
    pics_wc = sum(count_word_characters(p) for p in picture_tags)
    pics_cn = sum(count_pure_chinese(p) for p in picture_tags)

    full_doc_wc = body_total_word_chars + title_wc + info_wc + pics_wc
    full_doc_cn = body_total_pure_cn + title_cn + info_cn + pics_cn
    full_doc_words = count_office_words(content)

    print("\n" + "=" * 68)
    print(f"📊 新闻稿专业字数与结构分块分析报告")
    if filepath:
        print(f"   文件路径: {filepath}")
    print("=" * 68)

    print(f"\n【一、Office Word 真实字数总览（权威把关）】")
    print(f"  • Office 字符数（不计空格·整篇文档）: {full_doc_wc:4d} 字符  (老师看全文左下角显示的数字)")
    print(f"  • Office 字符数（不计空格·仅正文段）: {body_total_word_chars:4d} 字符  (剔除标题/发布栏后的真实正文)")
    print(f"  • 纯汉字数（仅正文·代码算法统计）   : {body_total_pure_cn:4d} 字   (不含标点符号与阿拉伯数字)")
    print(f"  • 标点与数字字符数（仅正文）         : {body_total_word_chars - body_total_pure_cn:4d} 字符")
    print(f"  • Office 状态栏字数 (Words 模拟)    : {full_doc_words:4d} 词/字")

    print(f"\n【二、新闻稿分块/分段精细化结构统计】")
    print(f" ┌─────────────────────┬──────────────┬──────────┬──────────┬──────────┐")
    print(f" │ 结构板块            │ Word字符数   │ 纯汉字数 │ 标点数字 │ 正文占比 │")
    print(f" ├─────────────────────┼──────────────┼──────────┼──────────┼──────────┤")

    process_wc = 0
    for b in block_stats:
        ratio = (b["word_chars"] / body_total_word_chars * 100) if body_total_word_chars > 0 else 0
        if "过程" in b["label"]:
            process_wc += b["word_chars"]
        print(f" │ {b['label']:<19} │ {b['word_chars']:10d}字 │ {b['pure_cn']:7d}字 │ {b['punct_num']:7d}字 │ {ratio:7.1f}% │")

    print(f" ├─────────────────────┼──────────────┼──────────┼──────────┼──────────┤")
    print(f" │ 正文各段合计        │ {body_total_word_chars:10d}字 │ {body_total_pure_cn:7d}字 │ {body_total_word_chars - body_total_pure_cn:7d}字 │   100.0% │")
    print(f" ├─────────────────────┼──────────────┼──────────┼──────────┼──────────┤")
    if title:
        print(f" │ 附加：新闻稿标题    │ {title_wc:10d}字 │ {title_cn:7d}字 │ {title_wc - title_cn:7d}字 │    ——    │")
    if info_block:
        print(f" │ 附加：工作简报栏    │ {info_wc:10d}字 │ {info_cn:7d}字 │ {info_wc - info_cn:7d}字 │    ——    │")
    if picture_tags:
        print(f" │ 附加：配图占位说明  │ {pics_wc:10d}字 │ {pics_cn:7d}字 │ {pics_wc - pics_cn:7d}字 │    ——    │")
    print(f" └─────────────────────┴──────────────┴──────────┴──────────┴──────────┘")

    # 红线诊断
    print(f"\n【三、新闻稿质量红线合规诊断】")
    errors = []
    warnings = []

    # 1. 正文字数把关
    if body_total_word_chars > 540:
        errors.append(f"正文 Word 字符数达 {body_total_word_chars} 字，突破 540 字上限（标准 500—520 字）！超长约 {body_total_word_chars - 520} 字。")
    elif body_total_word_chars < 490:
        errors.append(f"正文 Word 字符数仅 {body_total_word_chars} 字，低于 490 字下限（标准 500—520 字）！偏短约 {500 - body_total_word_chars} 字。")
    else:
        print(f"  ✅ 正文字数完美达标: {body_total_word_chars} 字符（受控在 500—520 字黄金区间，容差 [490, 540]）")

    # 2. 过程段占比
    proc_ratio = (process_wc / body_total_word_chars * 100) if body_total_word_chars > 0 else 0
    if proc_ratio > 30.5:
        errors.append(f"过程段占比达 {proc_ratio:.1f}%（{process_wc}字），超过 30% 上限红线！活动流程过于冗长，必须精炼打包归并！")
    else:
        print(f"  ✅ 过程段占比控制达标: {proc_ratio:.1f}%（{process_wc}字，标准：不超过 30%、140—160 字以内）")

    # 3. 全文字符数提示
    if full_doc_wc > 620:
        warnings.append(f"整篇文档含标题/发布栏已达 {full_doc_wc} 字符。老师若看 Word 左下角整篇统计会看到 600+，建议将正文压缩至 480—500 字符更稳妥。")

    if errors:
        print("\n  ❌ 体检未通过项:")
        for e in errors:
            print(f"     • {e}")
    if warnings:
        print("\n  ⚠️ 优化建议项:")
        for w in warnings:
            print(f"     • {w}")
    if not errors and not warnings:
        print("\n  🎉 完美合规！正文字数与分块比例均符合学院最佳标准！")

    print("=" * 68 + "\n")
    return len(errors) == 0

def analyze_summary(content, filepath=""):
    sections = parse_summary_blocks(content)
    total_wc = count_word_characters(content)
    total_cn = count_pure_chinese(content)

    print("\n" + "=" * 68)
    print(f"📋 工作总结专业字数与八大模块统计报告")
    if filepath:
        print(f"   文件路径: {filepath}")
    print("=" * 68)

    print(f"\n【一、Office Word 真实字数总览】")
    print(f"  • Office 字符数（不计空格）: {total_wc:4d} 字符  (标准区间：800—2000 字)")
    print(f"  • 纯汉字数                  : {total_cn:4d} 字")

    print(f"\n【二、各章节模块字数分布切片】")
    print(f" ┌────────────────────────────────────┬──────────────┬──────────┬──────────┐")
    print(f" │ 模块标题                           │ Word字符数   │ 纯汉字数 │ 全篇占比 │")
    print(f" ├────────────────────────────────────┼──────────────┼──────────┼──────────┤")

    for title, sec_content in sections:
        sec_wc = count_word_characters(sec_content)
        sec_cn = count_pure_chinese(sec_content)
        ratio = (sec_wc / total_wc * 100) if total_wc > 0 else 0
        display_title = title if len(title) <= 16 else title[:15] + "…"
        print(f" │ {display_title:<32} │ {sec_wc:10d}字 │ {sec_cn:7d}字 │ {ratio:7.1f}% │")

    print(f" ├────────────────────────────────────┼──────────────┼──────────┼──────────┤")
    print(f" │ 全篇合计                           │ {total_wc:10d}字 │ {total_cn:7d}字 │   100.0% │")
    print(f" └────────────────────────────────────┴──────────────┴──────────┴──────────┘")

    print(f"\n【三、工作总结篇幅红线诊断】")
    if total_wc < 800:
        print(f"  ❌ 字数偏少: 当前仅 {total_wc} 字符，低于 800 字底线要求，八大模块复盘不够充分！")
        return False
    elif total_wc > 2000:
        print(f"  ❌ 篇幅超长: 当前高达 {total_wc} 字符，已突破 2000 字上限！篇幅过于冗长拖沓，请删去冗余碎碎念或长表格！")
        return False
    else:
        print(f"  ✅ 字数完全合规: {total_wc} 字符（受控在 800—2000 字最佳区间，复盘深入且不拖沓）")
        print("=" * 68 + "\n")
        return True

def main():
    parser = argparse.ArgumentParser(description="校园活动文稿 Word 真实字数与分块切片统计工具（支持 .md 与 .docx）")
    parser.add_argument("file", help="待检测的 Markdown、Word(.docx) 或文本文件路径")
    parser.add_argument("--type", choices=["news", "summary", "auto"], default="auto", help="文稿类型：news(新闻稿)、summary(工作总结)、auto(自动识别)")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"错误: 找不到文件 {args.file}")
        sys.exit(1)

    content, paragraphs = read_text_from_file(args.file)

    doc_type = args.type
    if doc_type == "auto":
        if "新闻稿" in args.file or len(content) < 1200:
            doc_type = "news"
        else:
            doc_type = "summary"

    if doc_type == "news":
        passed = analyze_news(content, paragraphs, args.file)
    else:
        passed = analyze_summary(content, args.file)

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
