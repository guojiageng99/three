from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PPT_PATH = ROOT / "submission_docs" / "Generative_Agents_课程答辩稿.pptx"

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

NS = {
    "p": P_NS,
    "r": R_NS,
    "a": A_NS,
    "pr": PR_NS,
    "ct": CT_NS,
}

ET.register_namespace("", P_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("r", R_NS)


def remove_orphan_slides(work_dir: Path) -> None:
    presentation_path = work_dir / "ppt" / "presentation.xml"
    rels_path = work_dir / "ppt" / "_rels" / "presentation.xml.rels"
    content_types_path = work_dir / "[Content_Types].xml"

    presentation_root = ET.parse(presentation_path).getroot()
    rels_tree = ET.parse(rels_path)
    rels_root = rels_tree.getroot()
    content_types_tree = ET.parse(content_types_path)
    content_types_root = content_types_tree.getroot()

    active_slide_targets: set[str] = set()
    for slide_id in presentation_root.find("p:sldIdLst", NS):
        rel_id = slide_id.attrib[f"{{{R_NS}}}id"]
        for rel in rels_root.findall("pr:Relationship", NS):
            if rel.attrib.get("Id") == rel_id:
                active_slide_targets.add(rel.attrib["Target"].replace("\\", "/"))
                break

    all_slide_paths = sorted((work_dir / "ppt" / "slides").glob("slide*.xml"))
    all_slide_rel_paths = sorted((work_dir / "ppt" / "slides" / "_rels").glob("slide*.xml.rels"))

    for slide_path in all_slide_paths:
        relative_target = f"slides/{slide_path.name}"
        if relative_target in active_slide_targets:
            continue
        rel_path = work_dir / "ppt" / "slides" / "_rels" / f"{slide_path.name}.rels"
        notes_path = work_dir / "ppt" / "notesSlides" / slide_path.name.replace("slide", "notesSlide")
        notes_rel_path = work_dir / "ppt" / "notesSlides" / "_rels" / f"{notes_path.name}.rels"
        for path in (slide_path, rel_path, notes_path, notes_rel_path):
            if path.exists():
                path.unlink()

    active_targets_with_prefix = {f"/ppt/{target}" for target in active_slide_targets}
    for rel in list(rels_root.findall("pr:Relationship", NS)):
        target = rel.attrib.get("Target", "").replace("\\", "/")
        if target.startswith("slides/") and target not in active_slide_targets:
            rels_root.remove(rel)

    for override in list(content_types_root.findall("ct:Override", NS)):
        part_name = override.attrib.get("PartName", "")
        if part_name.startswith("/ppt/slides/slide") and part_name not in active_targets_with_prefix:
            content_types_root.remove(override)
        if part_name.startswith("/ppt/notesSlides/notesSlide"):
            note_name = Path(part_name).name
            slide_name = note_name.replace("notesSlide", "slide")
            if f"/ppt/slides/{slide_name}" not in active_targets_with_prefix:
                content_types_root.remove(override)

    rels_tree.write(rels_path, encoding="utf-8", xml_declaration=True)
    content_types_tree.write(content_types_path, encoding="utf-8", xml_declaration=True)


def update_title_slide(work_dir: Path) -> None:
    slide1_path = work_dir / "ppt" / "slides" / "slide1.xml"
    tree = ET.parse(slide1_path)
    root = tree.getroot()
    texts = root.findall(".//a:t", NS)
    for text_node in texts:
        if text_node.text == "组员：待填写":
            text_node.text = ""
    tree.write(slide1_path, encoding="utf-8", xml_declaration=True)


def repack_ppt(src_dir: Path, output_path: Path) -> None:
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for file_path in sorted(src_dir.rglob("*")):
            if file_path.is_file():
                out_zip.write(file_path, file_path.relative_to(src_dir).as_posix())


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(PPT_PATH) as zf:
            zf.extractall(temp_path)

        remove_orphan_slides(temp_path)
        update_title_slide(temp_path)
        repack_ppt(temp_path, PPT_PATH)

    print(f"fixed: {PPT_PATH}")


if __name__ == "__main__":
    main()
