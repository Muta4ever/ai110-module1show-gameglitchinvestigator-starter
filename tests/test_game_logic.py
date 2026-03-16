from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# ---------------------------------------------------------------------------
# check_guess
# ---------------------------------------------------------------------------

def test_winning_guess():
    assert check_guess(50, 50) == "Win"

def test_guess_too_high():
    assert check_guess(60, 50) == "Too High"

def test_guess_too_low():
    assert check_guess(40, 50) == "Too Low"

# Bug fix: hints were backwards — verify direction is correct
def test_hint_direction_too_high_means_go_lower():
    # guess > secret → "Too High" → user should go lower
    assert check_guess(80, 30) == "Too High"

def test_hint_direction_too_low_means_go_higher():
    # guess < secret → "Too Low" → user should go higher
    assert check_guess(10, 90) == "Too Low"

def test_check_guess_boundary_one_above():
    assert check_guess(51, 50) == "Too High"

def test_check_guess_boundary_one_below():
    assert check_guess(49, 50) == "Too Low"

def test_check_guess_secret_as_string_match():
    # Handles string secret (even-attempt glitch in app)
    assert check_guess(50, "50") == "Win"

def test_check_guess_secret_as_string_too_high():
    # 99 vs "50": numeric comparison should still work via fallback
    result = check_guess(99, "50")
    assert result == "Too High"


# ---------------------------------------------------------------------------
# parse_guess
# ---------------------------------------------------------------------------

def test_parse_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None

def test_parse_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."

def test_parse_none():
    ok, _, err = parse_guess(None)
    assert ok is False
    assert err == "Enter a guess."

def test_parse_non_numeric():
    ok, _, err = parse_guess("abc")
    assert ok is False
    assert err == "That is not a number."

def test_parse_float_string_truncates():
    # "3.9" should parse to 3
    ok, value, _ = parse_guess("3.9")
    assert ok is True
    assert value == 3

def test_parse_negative_number():
    ok, value, _ = parse_guess("-5")
    assert ok is True
    assert value == -5

def test_parse_whitespace_only():
    ok, _, _ = parse_guess("   ")
    assert ok is False


# ---------------------------------------------------------------------------
# get_range_for_difficulty
# ---------------------------------------------------------------------------

def test_range_easy():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20

def test_range_normal():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 50

def test_range_hard():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 100

def test_range_unknown_defaults():
    low, high = get_range_for_difficulty("Unknown")
    assert low == 1
    assert high == 100


# ---------------------------------------------------------------------------
# update_score — including attempts off-by-one fix
# ---------------------------------------------------------------------------

def test_score_win_first_attempt():
    # attempt_number=1 (fixed: starts at 0, increments to 1 on first submit)
    score = update_score(0, "Win", 1)
    assert score == 100 - 10 * (1 + 1)  # 80

def test_score_win_does_not_go_below_10_points():
    # attempt_number=9 → 100 - 10*10 = 0, clamped to 10
    score = update_score(0, "Win", 9)
    assert score == 10

def test_score_win_adds_to_existing_score():
    score = update_score(50, "Win", 1)
    assert score == 130  # 50 + 80

def test_score_too_low_deducts():
    score = update_score(100, "Too Low", 1)
    assert score == 95

def test_score_too_high_even_attempt_adds():
    score = update_score(100, "Too High", 2)
    assert score == 105

def test_score_too_high_odd_attempt_deducts():
    score = update_score(100, "Too High", 1)
    assert score == 95

def test_score_unknown_outcome_unchanged():
    score = update_score(42, "Draw", 3)
    assert score == 42

# Bug fix: attempts initialized to 0 (not 1), so first real guess is attempt 1
def test_attempts_start_at_zero_means_first_guess_is_attempt_1():
    # Simulates: attempts=0 → submit → attempts becomes 1
    initial_attempts = 0
    attempts_after_submit = initial_attempts + 1
    score = update_score(0, "Win", attempts_after_submit)
    assert score == 80  # Not 70 (which would happen if first guess were attempt 2)
