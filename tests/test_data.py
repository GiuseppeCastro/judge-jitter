import pytest

from judge_jitter.data import Example, build_prompt, load_examples


def test_load_examples(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text(
        '{"id": "a", "input": "q", "answer": "r", "reference": "ref"}\n'
        "\n"
        '{"id": "b", "input": "q2", "answer": "r2"}\n'
    )
    examples = load_examples(path)
    assert [e.id for e in examples] == ["a", "b"]
    assert examples[0].reference == "ref"
    assert examples[1].reference is None


def test_load_examples_reports_bad_line_number(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": "a", "input": "q", "answer": "r"}\n{"id": "b", "input": "q2"}\n')
    with pytest.raises(ValueError, match=":2:"):
        load_examples(path)


def test_load_examples_rejects_empty_file(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text("\n")
    with pytest.raises(ValueError, match="no examples"):
        load_examples(path)


def test_build_prompt_includes_reference():
    example = Example(id="a", input="q", answer="r", reference="ref")
    prompt = build_prompt("Judge this.", example)
    assert "Judge this." in prompt
    assert "Input:\nq" in prompt
    assert "Answer:\nr" in prompt
    assert "Reference:\nref" in prompt


def test_build_prompt_omits_missing_reference():
    example = Example(id="a", input="q", answer="r")
    assert "Reference" not in build_prompt("Judge this.", example)
