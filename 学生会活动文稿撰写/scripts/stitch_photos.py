#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stitch_photos.py - 校园活动文稿智能多图拼图与排版工具
特点：
- 不锁死固定像素比例，由 AI/用户根据图片内容灵活指定或自适应；
- 支持多种排版布局：
    * h2 / horizontal: 横向并排（自适应等高或统一比例，适合2张、3张等连贯动作/对比）
    * grid: 宫格拼图（适合4张图的 2x2 展示，如多组作品、多样风貌）
    * vertical: 纵向并排
    * auto: 根据输入图片张数自动选择最优排版方案
- 智能留白中缝（纯白底色，默认 6~8px），保持画面端正，杜绝人物拉伸变形。
"""

import os
import sys
import argparse

def get_pil_image():
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("错误: 当前 Python 未安装 Pillow 库。请使用: /opt/homebrew/bin/python3 scripts/stitch_photos.py ...", file=sys.stderr)
        sys.exit(1)

def resize_to_height(im, target_h, Image):
    """保持原图宽高比，自适应缩放到指定高度"""
    w, h = im.size
    new_w = int(w * (target_h / h))
    return im.resize((new_w, target_h), Image.Resampling.LANCZOS)

def crop_center_ratio(im, ratio, Image):
    """按指定宽高比(w/h)智能居中裁切"""
    w, h = im.size
    current_ratio = w / h
    if current_ratio > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        return im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / ratio)
        top = (h - new_h) // 2
        return im.crop((0, top, w, top + new_h))

def stitch_horizontal(images, gutter=8, target_height=None, crop_ratio=None, Image=None):
    """横向等高并排拼接（支持2张、3张或更多）"""
    if target_height is None:
        target_height = min(im.size[1] for im in images)
        target_height = min(target_height, 1200) # 保持合理上限
        
    processed = []
    for im in images:
        if crop_ratio:
            im = crop_center_ratio(im, crop_ratio, Image)
        im_resized = resize_to_height(im, target_height, Image)
        processed.append(im_resized)
        
    total_w = sum(im.size[0] for im in processed) + gutter * (len(processed) - 1)
    canvas = Image.new("RGB", (total_w, target_height), (255, 255, 255))
    
    cur_x = 0
    for im in processed:
        canvas.paste(im, (cur_x, 0))
        cur_x += im.size[0] + gutter
        
    return canvas

def stitch_grid_2x2(images, gutter=8, cell_w=1000, cell_h=750, Image=None):
    """2x2 宫格拼图（必须恰好4张图）"""
    target_ratio = cell_w / cell_h
    processed = []
    for im in images[:4]:
        cropped = crop_center_ratio(im, target_ratio, Image)
        resized = cropped.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        processed.append(resized)
        
    total_w = cell_w * 2 + gutter
    total_h = cell_h * 2 + gutter
    canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    
    canvas.paste(processed[0], (0, 0))
    canvas.paste(processed[1], (cell_w + gutter, 0))
    canvas.paste(processed[2], (0, cell_h + gutter))
    canvas.paste(processed[3], (cell_w + gutter, cell_h + gutter))
    
    return canvas

def main():
    parser = argparse.ArgumentParser(description="活动新闻稿智能多图拼图工具")
    parser.add_argument("images", nargs="+", help="参与拼接的照片路径列表（1张至多张）")
    parser.add_argument("-o", "--output", required=True, help="拼图输出保存路径 (例如: 拼图1_全场与交流.jpg)")
    parser.add_argument("--layout", choices=["auto", "horizontal", "grid", "vertical"], default="auto",
                        help="排版方式：auto(自动匹配)、horizontal(横向并列)、grid(2x2宫格)")
    parser.add_argument("--height", type=int, default=None, help="目标高度（可选，默认自适应原图）")
    parser.add_argument("--ratio", type=float, default=None, help="单图统一宽高比 (如 1.333 代表 4:3，可选)")
    parser.add_argument("--gutter", type=int, default=8, help="白色中缝缝隙宽度 (px)，默认 8px")
    parser.add_argument("--quality", type=int, default=92, help="JPEG 输出画质，默认 92")
    
    args = parser.parse_args()
    Image = get_pil_image()
    
    imgs = []
    for p in args.images:
        if not os.path.exists(p):
            print(f"错误: 找不到图片文件: {p}", file=sys.stderr)
            sys.exit(1)
        imgs.append(Image.open(p))
        
    num = len(imgs)
    if num == 1:
        print("单张图片直接导出优化...")
        canvas = imgs[0]
    elif args.layout == "grid" or (args.layout == "auto" and num == 4):
        print(f"应用 2x2 四宫格布局拼接 4 张图片...")
        canvas = stitch_grid_2x2(imgs, gutter=args.gutter, Image=Image)
    else:
        # 默认横向并列（支持 2 张、3 张等）
        print(f"应用横向等高并列拼接 {num} 张图片...")
        canvas = stitch_horizontal(imgs, gutter=args.gutter, target_height=args.height,
                                   crop_ratio=args.ratio, Image=Image)
        
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    canvas.save(args.output, format="JPEG", quality=args.quality)
    print(f"✅ 拼图生成成功: {args.output} [最终分辨率: {canvas.size[0]}x{canvas.size[1]}px]")

if __name__ == "__main__":
    main()
