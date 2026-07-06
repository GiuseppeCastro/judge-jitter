from judge_jitter.metrics import item_stats, summarize


def test_identical_scores_are_stable():
    stats = item_stats("a", [5] * 10)
    assert stats.stable
    assert stats.distinct == 1
    assert stats.variance == 0.0


def test_mixed_scores_are_unstable():
    stats = item_stats("a", [2, 4, 2, 4])
    assert not stats.stable
    assert stats.distinct == 2
    assert stats.variance == 1.0


def test_single_score_has_zero_variance():
    assert item_stats("a", [3]).variance == 0.0


def test_all_failed_runs_count_errors():
    stats = item_stats("a", [], errors=10)
    assert stats.errors == 10
    assert stats.variance == 0.0


def test_summary_counts_unstable_items():
    items = [item_stats("a", [5, 5]), item_stats("b", [1, 5])]
    summary = summarize(items)
    assert summary.total == 2
    assert summary.unstable == 1
    assert summary.instability == 0.5


def test_agreement_is_one_when_fully_stable():
    summary = summarize([item_stats("a", [4, 4, 4])])
    assert summary.agreement == 1.0


def test_agreement_is_zero_at_maximum_disagreement():
    summary = summarize([item_stats("a", [1, 5, 1, 5])])
    assert summary.agreement == 0.0
