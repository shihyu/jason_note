from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT.parent / "SUMMARY.md"
DOC_NAME = "Put避險與碗型底選股心法.md"
DOC_PATH = ROOT / DOC_NAME
LEGACY_PATH = ROOT / "test.md"
SUMMARY_LINK = f"strategy/{DOC_NAME}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_document_is_promoted_from_temporary_name():
    assert DOC_PATH.exists(), f"missing document: {DOC_PATH}"
    assert not LEGACY_PATH.exists(), "temporary file test.md should be renamed"


def test_document_has_markdown_structure():
    content = read_text(DOC_PATH)
    lines = content.splitlines()

    assert lines, "document should not be empty"
    assert lines[0] == "# Put 避險與碗型底選股心法"
    assert "## 核心觀點" in content
    assert "## 操作框架" in content
    assert "## 型態觀察重點" in content
    assert "```" not in content or content.count("```") % 2 == 0


def test_summary_contains_document_link():
    summary = read_text(SUMMARY)

    assert SUMMARY_LINK in summary
    assert "- [Put 避險與碗型底選股心法]" in summary


def test_markdown_image_links_are_local_and_existing():
    content = read_text(DOC_PATH)
    image_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)

    for link in image_links:
        assert not link.startswith(("http://", "https://")), link
        assert link.startswith("images/"), link
        assert (ROOT / link).exists(), link


def test_no_remote_image_links_remain():
    content = read_text(DOC_PATH)

    assert not re.search(r"!\[[^\]]*\]\(https?://", content)
