"""Unit tests for code_analysis module (EnhancedCodeAnalyzer)."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_analysis import EnhancedCodeAnalyzer, LanguageType


@pytest.fixture
def sample_project(tmp_path) -> Path:
    """A small on-disk project with one file per supported language."""
    project = tmp_path / "sample_project"
    project.mkdir()

    (project / "main.py").write_text(
        '"""Module docstring for the entry point."""\n'
        "import os\n"
        "\n"
        "\n"
        "def run(seconds: int) -> str:\n"
        '    """Run the loop."""\n'
        "    total = 0\n"
        "    for i in range(seconds):\n"
        "        if i % 2 == 0:\n"
        "            total += i\n"
        "    return f'done {total}'\n"
        "\n"
        "\n"
        "class Runner:\n"
        '    """Runs things."""\n'
        "\n"
        "    def go(self):\n"
        "        return undefined_variable_name\n",
        encoding="utf-8",
    )

    (project / "app.js").write_text(
        "function compute(n) {\n"
        "  return n * 2;\n"
        "}\n"
        "class Widget {\n"
        "  constructor(x) { this.x = x; }\n"
        "}\n"
        "const net = require('net');\n",
        encoding="utf-8",
    )

    (project / "Main.java").write_text(
        "import java.util.List;\n"
        "public class Main {\n"
        "    public int add(int a, int b) { return a + b; }\n"
        "}\n",
        encoding="utf-8",
    )

    (project / "notes.txt").write_text("not code\n", encoding="utf-8")

    junk = project / "node_modules"
    junk.mkdir()
    (junk / "junk.js").write_text("function junk() {}\n", encoding="utf-8")

    return project


class TestLanguageDetection:
    def test_python(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        assert analyzer._detect_language(sample_project / "main.py") is LanguageType.PYTHON

    def test_javascript(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        assert analyzer._detect_language(sample_project / "app.js") is LanguageType.JAVASCRIPT

    def test_typescript(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        ts = sample_project / "app.ts"
        ts.write_text("const x = 1;\n")
        assert analyzer._detect_language(ts) is LanguageType.TYPESCRIPT

    def test_java(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        assert analyzer._detect_language(sample_project / "Main.java") is LanguageType.JAVA

    def test_unknown(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        assert analyzer._detect_language(sample_project / "notes.txt") is LanguageType.UNKNOWN


class TestFileFiltering:
    def test_code_files_found(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        names = {p.name for p in analyzer._get_code_files()}
        assert {"main.py", "app.js", "Main.java"} <= names

    def test_node_modules_skipped(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        names = {p.name for p in analyzer._get_code_files()}
        assert "junk.js" not in names

    def test_non_code_skipped(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        names = {p.name for p in analyzer._get_code_files()}
        assert "notes.txt" not in names


class TestPythonAnalysis:
    def test_functions_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "main.py")
        fn_names = {f["name"] for f in result["functions"]}
        assert "run" in fn_names

    def test_classes_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "main.py")
        class_names = {c["name"] for c in result["classes"]}
        assert "Runner" in class_names

    def test_docstrings_captured(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "main.py")
        docstrings = [f.get("docstring") for f in result["functions"]]
        assert "Run the loop." in docstrings

    def test_complexity_counts_branches(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "main.py")
        run = next(f for f in result["functions"] if f["name"] == "run")
        assert run["complexity"] >= 3  # base + for + if

    def test_undefined_variable_error_pattern(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "main.py")
        messages = " ".join(e["message"] for e in result["error_patterns"])
        assert "undefined_variable_name" in messages


class TestJavaScriptAnalysis:
    def test_functions_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "app.js")
        fn_names = {f["name"] for f in result["functions"]}
        assert "compute" in fn_names

    def test_classes_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "app.js")
        class_names = {c["name"] for c in result["classes"]}
        assert "Widget" in class_names

    def test_imports_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "app.js")
        assert any("require" in imp for imp in result["imports"])


class TestJavaAnalysis:
    def test_methods_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "Main.java")
        fn_names = {f["name"] for f in result["functions"]}
        assert "add" in fn_names

    def test_classes_extracted(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_file(sample_project / "Main.java")
        class_names = {c["name"] for c in result["classes"]}
        assert "Main" in class_names


class TestProjectAnalysis:
    def test_analyze_project_metrics(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_project()
        metrics = result["metrics"]
        assert metrics["total_lines"] > 0
        assert metrics["total_functions"] >= 2
        assert metrics["total_classes"] >= 2

    def test_analyze_project_files_populated(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_project()
        assert any(str(p).endswith("main.py") for p in result["files"])

    def test_chunked_analysis(self, sample_project):
        analyzer = EnhancedCodeAnalyzer(str(sample_project))
        result = analyzer.analyze_project(chunk_size=1)
        assert result["files"], "chunked analysis should still produce results"
