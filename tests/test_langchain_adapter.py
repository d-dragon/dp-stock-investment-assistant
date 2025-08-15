from core.langchain_adapter import build_prompt


def test_build_prompt_includes_tickers():
    p = build_prompt("Analyze trends", {}, ["AAPL", "TSLA"])
    assert "AAPL" in p and "TSLA" in p, "Prompt must include the referenced tickers"