"""Tests for the three text analyses."""

from __future__ import annotations

import pytest

from worker.analyses import compute, reading_time, top_words, word_count


def test_word_count_counts_whitespace_separated_words() -> None:
    assert word_count("  hello   world  ") == 2
    assert word_count("one two three") == 3


def test_word_count_empty_text_is_zero() -> None:
    assert word_count("") == 0
    assert word_count("   \n\t ") == 0


def test_compute_word_count_shape() -> None:
    assert compute("word_count", "a b c") == {"word_count": 3}


def test_compute_top_words_shape() -> None:
    result = compute("top_words", "the cat the dog the cat")
    assert result == {
        "top_words": [
            {"word": "the", "count": 3},
            {"word": "cat", "count": 2},
            {"word": "dog", "count": 1},
        ]
    }


def test_top_words_is_case_insensitive_and_strips_punctuation() -> None:
    result = top_words("Hello, hello! HELLO... world")
    assert result == [
        {"word": "hello", "count": 3},
        {"word": "world", "count": 1},
    ]


def test_top_words_ignores_punctuation_only_tokens() -> None:
    assert top_words("hi ... -- hi") == [{"word": "hi", "count": 2}]


def test_top_words_ties_ordered_alphabetically() -> None:
    result = top_words("banana apple cherry apple banana cherry grape")
    assert result[:3] == [
        {"word": "apple", "count": 2},
        {"word": "banana", "count": 2},
        {"word": "cherry", "count": 2},
    ]
    assert result[3] == {"word": "grape", "count": 1}


def test_top_words_limits_to_ten_entries() -> None:
    text = " ".join(f"w{i}" for i in range(15))
    result = top_words(text)
    assert len(result) == 10


def test_top_words_empty_text() -> None:
    assert top_words("") == []


def test_reading_time_200_words_per_minute_rounded_to_one_decimal() -> None:
    text_200 = " ".join(["word"] * 200)
    assert reading_time(text_200) == 1.0

    text_250 = " ".join(["word"] * 250)
    assert reading_time(text_250) == 1.2


def test_compute_reading_time_shape() -> None:
    assert compute("reading_time", " ".join(["word"] * 100)) == {
        "reading_time_minutes": 0.5,
        "word_count": 100,
    }


def test_reading_time_empty_text_is_zero() -> None:
    assert compute("reading_time", "") == {"reading_time_minutes": 0.0, "word_count": 0}


def test_unknown_analysis_raises() -> None:
    with pytest.raises(ValueError):
        compute("sentiment", "some text")
