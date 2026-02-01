from models import WorkflowOutputs


def test_workflow_outputs_parses_code_fence():
    text = """```json
[
  {"url": "https://example.com", "brand": ["A"], "item_name": "Item", "pros": [], "cons": [], "summary": "ok"}
]
```"""
    outputs = WorkflowOutputs(text=text)
    items = outputs.parsed_items()
    assert len(items) == 1
    assert items[0].brand == ["A"]
    assert items[0].item_name == "Item"


def test_brand_string_is_normalized_to_list():
    text = """[
      {"url": "https://example.com", "brand": "Skippy Natural, Justin's", "item_name": "Item"}
    ]"""
    outputs = WorkflowOutputs(text=text)
    items = outputs.parsed_items()
    assert items[0].brand == ["Skippy Natural", "Justin's"]


def test_brand_commas_inside_parentheses_not_split():
    text = """[
      {"url": "https://example.com", "brand": "Natural Peanut Butters (various brands, including Skippy Natural, Justin's, and 88 Acres)", "item_name": "Item"}
    ]"""
    outputs = WorkflowOutputs(text=text)
    items = outputs.parsed_items()
    assert items[0].brand == [
        "Natural Peanut Butters (various brands, including Skippy Natural, Justin's, and 88 Acres)"
    ]
