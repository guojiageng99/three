from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_DIR = ROOT / "submission_docs"
SOURCE_PPT = SUBMISSION_DIR / "generative agents.pptx"
OUTPUT_PPT = SUBMISSION_DIR / "generative agents_最终版.pptx"

RED = RGBColor(192, 0, 0)
LINE_RED = RGBColor(235, 76, 96)
BLUE = RGBColor(28, 68, 145)
BLACK = RGBColor(32, 32, 32)
WHITE = RGBColor(255, 255, 255)
LIGHT = RGBColor(248, 248, 248)

FONT = "Microsoft YaHei"
TITLE_FONT = "SimHei"


SLIDES = [
    {
        "title": "论文复现补充",
        "section": "核心认知闭环",
        "cards": [
            ("观察", "读取环境与相遇"),
            ("记忆", "写入经历"),
            ("检索", "召回相关记忆"),
            ("反思", "形成高层认知"),
        ],
        "box_title": "复现机制总览",
        "box_lines": [
            "环境感知 -> 记忆检索 -> 计划驱动 -> 行动/对话",
            "记忆更新 -> 反思形成",
            "本项目保留论文中最核心的生成式智能体闭环。",
        ],
    },
    {
        "title": "双模式设计",
        "section": "规则演示与 LLM 增强",
        "cards": [
            ("规则模式", "稳定演示"),
            ("LLM 模式", "模型生成"),
            ("失败回退", "接口异常"),
            ("证据记录", "状态可解释"),
        ],
        "box_title": "为什么这样设计",
        "box_lines": [
            "规则模式：适合录屏和答辩，传播链稳定可复现。",
            "LLM 模式：让模型参与计划、行动、对话和反思生成。",
            "接口失败时自动回退，避免现场 demo 中断。",
        ],
    },
    {
        "title": "LLM 演示路线",
        "section": "按时间书签讲清楚",
        "cards": [
            ("08:00", "初始态"),
            ("10:00", "Alice -> Bob"),
            ("14:00", "Bob -> Carol"),
            ("14:30", "反思生成"),
        ],
        "box_title": "讲解顺序",
        "box_lines": [
            "08:00：展示 persona、初始记忆和计划。",
            "10:00：展示对话如何改写 Bob 的内部状态。",
            "14:00：展示局部互动如何形成传播链。",
            "14:30：展示记忆重要性超过阈值后的高层反思。",
        ],
    },
    {
        "title": "机制对应关系",
        "section": "代码现象对应论文模块",
        "cards": [
            ("记忆流", "Memory Stream"),
            ("检索", "Retrieval"),
            ("计划", "Planning"),
            ("反思", "Reflection"),
        ],
        "box_title": "论文机制映射",
        "box_lines": [
            "观察、行动、对话和反思都写入统一记忆流。",
            "检索按重要性、近因、地点、社交关系和相关性打分。",
            "计划提供日程骨架，检索记忆影响当前行动。",
        ],
    },
    {
        "title": "局限与改进",
        "section": "课程复现与原论文差距",
        "cards": [
            ("规模", "3 个角色"),
            ("世界", "4 个地点"),
            ("检索", "待接 embedding"),
            ("计划", "待扩展多日"),
        ],
        "box_title": "后续方向",
        "box_lines": [
            "当前是课程作业级复现，不是 Stanford Smallville 全量工程。",
            "后续可扩展 25 个 agent 与多日长期计划。",
            "检索可进一步接入 embedding retrieval。",
            "也可以加入更丰富的社交关系和开放式事件解析。",
        ],
    },
]


def add_textbox(slide, left, top, width, height, text, size=22, color=BLACK, bold=False, align=None):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    clear_shape_effects(shape)
    tf = shape.text_frame
    tf.clear()
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    p = tf.paragraphs[0]
    if align is not None:
        p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return shape


def clear_shape_effects(shape) -> None:
    sp_pr = getattr(shape._element, "spPr", None)
    if sp_pr is None:
        return
    for child in list(sp_pr):
        if child.tag.endswith("}effectLst") or child.tag.endswith("}effectDag"):
            sp_pr.remove(child)
    sp_pr.append(OxmlElement("a:effectLst"))


def add_title(slide, title: str):
    shape = add_textbox(slide, 0.62, 0.22, 7.2, 0.72, title, size=34, color=RED, bold=True)
    for run in shape.text_frame.paragraphs[0].runs:
        run.font.name = TITLE_FONT
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.15), Inches(1.08), Inches(13.0), Inches(0.04))
    clear_shape_effects(line)
    line.fill.solid()
    line.fill.fore_color.rgb = LINE_RED
    line.line.color.rgb = LINE_RED


def add_section(slide, text: str, top: float):
    square = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(top + 0.08), Inches(0.16), Inches(0.16))
    clear_shape_effects(square)
    square.fill.solid()
    square.fill.fore_color.rgb = BLUE
    square.line.color.rgb = BLUE
    add_textbox(slide, 0.82, top - 0.02, 5.7, 0.48, text, size=24, color=RED, bold=True)


def add_card(slide, left: float, top: float, width: float, title: str, desc: str):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(1.05))
    clear_shape_effects(card)
    card.fill.solid()
    card.fill.fore_color.rgb = LIGHT
    card.line.color.rgb = RED
    card.line.width = Pt(1.4)
    tf = card.text_frame
    tf.clear()
    tf.margin_left = Inches(0.13)
    tf.margin_right = Inches(0.13)
    tf.margin_top = Inches(0.12)
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = title
    r1.font.name = FONT
    r1.font.size = Pt(17)
    r1.font.bold = True
    r1.font.color.rgb = BLACK
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = desc
    r2.font.name = FONT
    r2.font.size = Pt(15)
    r2.font.color.rgb = BLACK


def add_connector(slide, x1: float, y: float, x2: float):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y), Inches(x2), Inches(y))
    clear_shape_effects(line)
    line.line.color.rgb = RED
    line.line.width = Pt(1.4)


def add_black_box(slide, title: str, lines: list[str]):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.35), Inches(4.18), Inches(5.35), Inches(1.72))
    clear_shape_effects(box)
    box.fill.solid()
    box.fill.fore_color.rgb = BLACK
    box.line.color.rgb = BLACK
    tf = box.text_frame
    tf.clear()
    tf.margin_left = Inches(0.22)
    tf.margin_right = Inches(0.22)
    tf.margin_top = Inches(0.16)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.name = FONT
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = WHITE
    for line in lines:
        p = tf.add_paragraph()
        r = p.add_run()
        r.text = line
        r.font.name = FONT
        r.font.size = Pt(12)
        r.font.color.rgb = WHITE


def add_note_block(slide, lines: list[str]):
    add_section(slide, "说明", 3.62)
    for index, line in enumerate(lines):
        add_textbox(slide, 0.82, 4.18 + index * 0.35, 5.9, 0.3, line, size=15, color=BLACK)


def add_slide(prs: Presentation, payload: dict) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(slide, payload["title"])
    add_section(slide, payload["section"], 1.48)

    lefts = [0.75, 4.0, 7.85, 11.0]
    widths = [1.75, 2.1, 2.15, 1.82]
    for i, ((title, desc), left, width) in enumerate(zip(payload["cards"], lefts, widths)):
        add_card(slide, left, 2.03, width, title, desc)
        if i < 3:
            add_connector(slide, left + width, 2.55, lefts[i + 1])

    box_lines = payload["box_lines"]
    add_note_block(slide, box_lines[:3])
    add_black_box(slide, payload["box_title"], box_lines)


def build_final_ppt() -> None:
    if not SOURCE_PPT.exists():
        raise FileNotFoundError(f"Missing group PPT: {SOURCE_PPT}")
    prs = Presentation(str(SOURCE_PPT))
    for payload in SLIDES:
        add_slide(prs, payload)
    OUTPUT_PPT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PPT))
    print(f"Wrote {OUTPUT_PPT.relative_to(ROOT)}")


if __name__ == "__main__":
    build_final_ppt()
