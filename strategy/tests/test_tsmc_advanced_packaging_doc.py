from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "台積電先進封裝設備股分析.md"
OLD_DOC = ROOT / "test.md"
SUMMARY = ROOT.parent / "SUMMARY.md"


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def extract_markdown_targets(text):
    image_targets = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    link_targets = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)
    html_image_targets = re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", text, re.I)
    return image_targets, link_targets, html_image_targets


def assert_local_target_exists(target, source_path):
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        raise AssertionError(f"{source_path.name} contains remote target: {target}")

    path_only = target.split("#", 1)[0].strip()
    if not path_only:
        return

    resolved = (source_path.parent / path_only).resolve()
    assert_true(resolved.exists(), f"missing local target: {target}")


def main():
    assert_true(not OLD_DOC.exists(), "test.md should be renamed to the final document name")
    assert_true(DOC.exists(), f"missing document: {DOC.name}")

    text = DOC.read_text(encoding="utf-8")
    summary = SUMMARY.read_text(encoding="utf-8")

    assert_true(
        text.startswith("# 台積電先進封裝設備股分析"),
        "document should start with the normalized Traditional Chinese title",
    )
    assert_true(
        "[台積電先進封裝設備股分析](strategy/台積電先進封裝設備股分析.md)" in summary,
        "SUMMARY.md should link to the final document",
    )

    image_targets, link_targets, html_image_targets = extract_markdown_targets(text)
    for target in image_targets + html_image_targets:
        assert_true(target.startswith("images/"), f"image should be stored under images/: {target}")
        assert_local_target_exists(target, DOC)

    for target in link_targets:
        assert_local_target_exists(target, DOC)

    simplified_words = [
        "数据",
        "技术",
        "为什么",
        "超级",
        "独占",
        "战略",
        "对比",
        "先进",
        "类",
        "营收",
        "现",
        "线",
        "发",
        "点",
        "净",
        "组",
        "当",
        "与",
    ]
    leftovers = [word for word in simplified_words if word in text]
    assert_true(not leftovers, f"possible Simplified Chinese leftovers: {', '.join(leftovers)}")

    table_lines = [line for line in text.splitlines() if line.startswith("|")]
    assert_true(len(table_lines) >= 3, "expected a Markdown table")
    assert_true(any(re.match(r"^\| *:?-{3,}:? *\|", line) for line in table_lines), "missing table separator")

    print("document checks passed")


if __name__ == "__main__":
    main()
