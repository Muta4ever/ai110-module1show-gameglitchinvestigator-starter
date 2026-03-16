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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
