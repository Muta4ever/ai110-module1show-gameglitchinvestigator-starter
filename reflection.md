# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

  1. Hints were backwards. When it was supposed to say "Go lower", It actually said "Go higher" and vice versa. Fixed by correcting the outcome-to-message mapping in `app.py` so `"Too High"` shows "Go LOWER!" and `"Too Low"` shows "Go HIGHER!".
  2. After clicking the "New game" button, the game never actually restarted. Fixed by resetting `st.session_state.status` back to `"playing"` and clearing `st.session_state.history` in the new game handler — without resetting `status`, the `st.stop()` block fired immediately after rerun, freezing the game in its ended state.
  3. In-game attempts did not match the actual allowed attempts. For Normal mode, the player only got 7 guesses instead of 8. Fixed by initializing `st.session_state.attempts` to `0` instead of `1`, so the counter correctly starts before any guess is made.
  4. Guesses required two clicks of the Submit button before being recorded. Fixed by wrapping the text input and submit button in a `st.form`, which batches both into a single rerun so the typed value is always captured on the first click.
  5. Hints broke on every even-numbered attempt. The secret was being converted to a string on even attempts, causing lexicographic comparison (e.g., `"9" > "50"` is `True`), which produced wrong hints. Fixed by always passing the integer secret directly to `check_guess`.
  6. The info banner always said "Guess a number between 1 and 100" regardless of difficulty. Fixed by using the `low` and `high` variables from `get_range_for_difficulty` so the message reflects the actual range for each mode.
  7. Changing difficulty did not update the secret number or reset the game — the old secret persisted until a page refresh. Fixed by tracking `st.session_state.difficulty` and regenerating the secret (plus resetting attempts, status, and history) whenever the selected difficulty changes.
  8. The attempts counter displayed one step behind — pressing Submit still showed the old count until the next interaction. Fixed by moving `st.session_state.attempts += 1` before the `st.info` render so the decremented count is always visible immediately after submitting a guess.

---

## 2. How did you use AI as a teammate?

I used Claude Code (Anthropic's AI coding assistant) as my primary AI tool throughout this project. It helped me read the broken code, identify bugs, and suggest targeted fixes — acting like a pair programmer who could explain the reasoning behind each change.

**Correct AI suggestion:** The AI correctly diagnosed that the attempts counter was displaying one step behind because `st.info` rendered before `st.session_state.attempts += 1` in the script. It suggested using `st.empty()` as a placeholder above the form, then filling it after the increment runs — so the displayed count always reflects the just-submitted guess. I verified this by pressing Submit and watching the counter drop immediately on the same interaction rather than requiring a second guess.

**Incorrect / misleading AI suggestion:** When fixing the UI layout, the AI initially put the input box, Show Hint checkbox, New Game button, and Submit button all in columns on a single row inside the form. This was misleading because the input field became too narrow and the layout looked cramped — it did not match the intended design. I caught this by looking at the rendered app, then corrected it by telling the AI to put the input on its own full-width row and place the buttons on the row below. The AI had assumed a single-row layout was desired without checking the actual visual result first.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed by combining two checks: first running `pytest` to confirm the logic layer passed all automated tests, then manually playing the game in the browser to confirm the UI behaved correctly. Passing tests alone was not enough — the attempts counter bug and the difficulty reset bug were both invisible to `pytest` because they involved Streamlit's render order, not pure logic.

I ran `python3 -m pytest tests/test_game_logic.py -v` after every fix. One important run exposed that the Normal and Hard range tests were asserting the wrong values (`Normal == 100`, `Hard == 50`) — the tests had been written to match the bug, not the correct behaviour. This showed me that AI-generated tests can encode bugs just as easily as the code they test, so test assertions need to be reviewed critically, not just trusted because they pass.

The AI helped me understand `test_hint_direction_too_high_means_go_lower` and `test_hint_direction_too_low_means_go_higher` — it explained that the test names encode the *expected* direction so a reader can immediately spot if the mapping is backwards without reading the assertion. That naming convention made the hint-direction bug much easier to confirm was actually fixed.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

  The original code ran `st.session_state.secret = random.randint(low, high)` every time without checking whether a secret already existed. Because Streamlit reruns the entire script from top to bottom on every interaction — button click, text input, sidebar change — the secret was re-rolled on every single rerun. It was not a bug in the random number generator; it was that the assignment was never guarded.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

   every time you click anything on the page, the entire Python script starts over from line 1. Streamlit reruns everything. The problem is that normal variables reset to nothing each time. `st.session_state` is like a sticky notepad that survives across reruns — anything you write there stays put until you explicitly change or delete it. So the trick to building a stateful game in Streamlit is to store everything that needs to persist (the secret, the attempts count, the score) in `st.session_state`, and only set those values when you actually want them to change.

- What change did you make that finally gave the game a stable secret number?

  I added a guard: `if "difficulty" not in st.session_state or st.session_state.difficulty != difficulty`. This means the secret is only generated when the game is brand new (no difficulty recorded yet) or when the player deliberately switches difficulty. On every other rerun the block is skipped entirely, so the secret sits unchanged in `st.session_state.secret` until the player starts a new game.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  Running `pytest` after every individual fix rather than batching all changes first. This project taught me that a fix can introduce a new failure — the range swap broke two tests that had been encoding the bug — and catching that immediately after one change is far easier than untangling it after five changes.

- What is one thing you would do differently next time you work with AI on a coding task?

  I would ask the AI to explain *why* it is suggesting each change before accepting it, especially for tests. In this project the AI generated test assertions that matched the broken behaviour, which meant the tests passed but were useless. Asking "what assumption does this test make?" before accepting it would have caught that earlier.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  AI-generated code can look completely correct and still be subtly wrong in ways that only show up when you actually run the game and interact with it. I now treat AI output as a first draft that needs to be read critically and tested against the real running system, not just accepted because it looks plausible.
