import html
import os
import re

MARK_PATTERN = re.compile(r'<mark\b([^>]*)>([\s\S]*?)</mark>', re.IGNORECASE)
SPAN_PATTERN = re.compile(r'<span\b[^>]*>([\s\S]*?)</span>', re.IGNORECASE)
STYLE_PATTERN = re.compile(r'style\s*=\s*(["\'])([\s\S]*?)\1', re.IGNORECASE)
BACKGROUND_PATTERN = re.compile(
    r'background(?:-color)?\s*:\s*(rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}|var\([^)]*\)|[^;]+)',
    re.IGNORECASE,
)


def strip_html_tags(text):
    text = MARK_PATTERN.sub(lambda match: strip_html_tags(match.group(2)), text)
    text = SPAN_PATTERN.sub(lambda match: strip_html_tags(match.group(1)), text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def strip_highlight_wrappers(text):
    text = MARK_PATTERN.sub(lambda match: strip_html_tags(match.group(2)), text)
    text = SPAN_PATTERN.sub(lambda match: strip_html_tags(match.group(1)), text)
    text = re.sub(r'\*\*([\s\S]*?)\*\*', r'\1', text)
    text = re.sub(r'==([\s\S]*?)==', r'\1', text)
    return text


def normalize_color(color):
    if not color:
        return '__no_color__'
    return re.sub(r'\s+', '', color).lower()


def extract_background_color(attrs):
    style_match = STYLE_PATTERN.search(attrs)
    if not style_match:
        return ''

    style = style_match.group(2)
    background_match = BACKGROUND_PATTERN.search(style)
    if not background_match:
        return ''

    return background_match.group(1).strip()


def extract_mark_items(content):
    items = []
    for match in MARK_PATTERN.finditer(content):
        attrs = match.group(1)
        inner_html = match.group(2)
        text = strip_html_tags(inner_html)
        if not text:
            continue

        items.append({
            'text': text,
            'color': normalize_color(extract_background_color(attrs)),
            'position': match.start(),
        })
    return items


def group_marks_by_color_level(mark_items):
    color_levels = {}
    grouped_items = []

    for item in mark_items:
        color = item['color']
        if color not in color_levels:
            color_levels[color] = len(color_levels) + 1

        grouped_items.append({
            **item,
            'level': color_levels[color],
        })

    return grouped_items, color_levels


def extract_progressive_summary(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    layer1_text = strip_highlight_wrappers(content)

    layer2_items = [strip_html_tags(item) for item in re.findall(r'\*\*([\s\S]*?)\*\*', content)]
    layer3_items = [strip_html_tags(item) for item in re.findall(r'==([\s\S]*?)==', content)]

    mark_items = extract_mark_items(content)
    grouped_mark_items, color_levels = group_marks_by_color_level(mark_items)

    lines = []
    lines.append("#### 第一层：原文")
    lines.append(layer1_text.strip())
    lines.append("")
    lines.append("#### 第二层：重点摘要")
    if layer2_items:
        for item in layer2_items:
            lines.append(f"- **{item}**")
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("#### 第三层：高亮摘要")
    if layer3_items:
        for item in layer3_items:
            lines.append(f"- {item}")
    else:
        lines.append("（无）")
    lines.append("")

    if color_levels:
        max_level = max(color_levels.values())
        for level in range(1, max_level + 1):
            lines.append(f"#### 第{level + 3}层：HiNote 颜色等级 {level}")
            level_items = [item for item in grouped_mark_items if item['level'] == level]
            if level_items:
                for item in sorted(level_items, key=lambda value: value['position']):
                    lines.append(f"- {item['text']}")
            else:
                lines.append("（无）")
            lines.append("")
    else:
        lines.append("#### 第四层：HiNote 颜色等级 1")
        lines.append("（无）")
        lines.append("")

    lines.append("#### 最后层：总结")
    summary_placeholder = "总结："
    lines.append(summary_placeholder)

    output_content = "\n".join(lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"成功提取，结果已保存至：{output_file}")


if __name__ == '__main__':
    input_path = '示例.md'
    output_path = '示例_提取结果.md'
    if os.path.exists(input_path):
        extract_progressive_summary(input_path, output_path)
    else:
        print(f"找不到文件：{input_path}")
