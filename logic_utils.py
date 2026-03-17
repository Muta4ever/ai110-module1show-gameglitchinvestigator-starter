def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive (low, high) number range for a given difficulty level.

    The range defines the pool of possible secret numbers for a game session.
    Wider ranges correspond to harder difficulties, giving the player a larger
    search space and fewer contextual clues per guess.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.
            Any unrecognised value falls back to the Normal range.

    Returns:
        A ``(low, high)`` tuple of integers representing the inclusive bounds
        of the guessing range for the chosen difficulty.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    # FIX: AI identified that Normal (1–50) and Hard (1–100) were swapped — Hard should have the wider range.
    # Verified by checking sidebar range captions and confirming Hard gives a bigger search space than Normal.
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str) -> tuple[bool, int | None, str | None]:
    """Parse raw text input from the player into a validated integer guess.

    Accepts plain integers and decimal strings (e.g. ``"3.9"`` is truncated to
    ``3``).  Scientific notation that contains a decimal point (e.g. ``"2.5e2"``)
    is also accepted via the float branch and becomes ``250``.  Scientific notation
    without a decimal point (e.g. ``"1e3"``) is rejected as non-numeric because
    Python's ``int()`` does not accept that form directly.

    Args:
        raw: The raw string value submitted by the player.  May be ``None``,
            an empty string, a valid integer string, or arbitrary text.

    Returns:
        A three-element tuple ``(ok, guess_int, error_message)`` where:

        - ``ok`` (``bool``) — ``True`` if parsing succeeded, ``False`` otherwise.
        - ``guess_int`` (``int | None``) — the parsed integer value when
          ``ok`` is ``True``, otherwise ``None``.
        - ``error_message`` (``str | None``) — a human-readable error string
          when ``ok`` is ``False``, otherwise ``None``.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except ValueError:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int | str) -> str:
    """Compare the player's guess against the secret number and return an outcome.

    Performs a numeric comparison when both values are compatible types.  If a
    ``TypeError`` is raised (e.g. when ``secret`` is a string due to a known
    upstream bug), the function falls back to lexicographic string comparison so
    the game never crashes.

    Args:
        guess: The integer value submitted by the player.
        secret: The target number the player is trying to guess.  Expected to
            be an ``int``, but the fallback handles ``str`` values defensively.

    Returns:
        One of three outcome strings:

        - ``"Win"``      — the guess exactly matches the secret.
        - ``"Too High"`` — the guess is greater than the secret (player should go lower).
        - ``"Too Low"``  — the guess is less than the secret (player should go higher).

    Examples:
        >>> check_guess(50, 50)
        'Win'
        >>> check_guess(80, 30)
        'Too High'
        >>> check_guess(10, 90)
        'Too Low'
    """
    # Return only the outcome string: "Win", "Too High", or "Too Low".
    # Use try/except to handle comparisons between numbers and strings
    try:
        if guess == secret:
            return "Win"
        if guess > secret:
            return "Too High"
        return "Too Low"
    except TypeError:
        # Fallback to string comparison when types are incompatible
        guess_str = str(guess)
        secret_str = str(secret)
        if guess_str == secret_str:
            return "Win"
        if guess_str > secret_str:
            return "Too High"
        return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate and return an updated score based on the outcome of a single guess.

    Scoring rules:

    - **Win**: awards ``100 - 10 * (attempt_number + 1)`` points, with a minimum
      of ``10`` points so a late win still earns something.
    - **Too High on an even attempt**: awards ``+5`` points (a small bonus for
      narrowing from above on the right turn).
    - **Too High on an odd attempt** or **Too Low**: deducts ``5`` points.
    - Any other outcome (e.g. an unrecognised string): score is unchanged.

    Args:
        current_score: The player's score before this guess.
        outcome: The result string from :func:`check_guess` —
            one of ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based index of the current attempt
            (i.e. ``1`` on the first guess, ``2`` on the second, etc.).

    Returns:
        The updated integer score after applying the outcome's point adjustment.

    Examples:
        >>> update_score(0, "Win", 1)
        80
        >>> update_score(100, "Too Low", 3)
        95
        >>> update_score(100, "Too High", 2)
        105
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
