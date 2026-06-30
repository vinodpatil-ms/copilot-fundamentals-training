# Hands-On Demo (15 Minutes): GitHub Copilot Prompting

> Companion to the "GitHub Business Fundamentals" slides. Concepts (Four Pillars +
> techniques) are on the slides — **this is the live coding demo only.**
> App: a **Tip / Bill Splitter** in Python. We **generate code from prompts**,
> step by step, through a **Generate → Analyze → Repair** loop, and **add tests last**.

---

## 🧱 The Four Pillars (quick reference)

Every strong prompt carries these. Watch for them tagged on each step below.

| Pillar | Question it answers | Example phrase from this demo |
|--------|--------------------|-------------------------------|
| **Context** | What's the surrounding situation? | *"In `tip_calculator.py` …"* / open files as neighboring tabs |
| **Intent** | What outcome do I want? | *"…return how much each person pays…"* |
| **Clarity** | Is it unambiguous? | *"…as a float rounded to 2 decimal places…"* |
| **Specificity** | What exact details/constraints? | *"…raise ValueError when number_of_people <= 0…"* |

---

## ⏱️ Before You Start (do this OFF the clock)

```text
1. Folder `tip-splitter` open in the editor.
2. Python venv active, pytest installed.
3. Two files created AND both open side-by-side:
       tip_calculator.py          ← we write code here
       test_tip_calculator.py     ← stays open for "neighboring tabs" + final tests
4. A terminal open, ready to run:  python  and later  pytest
```

---

## 15-Minute Timeline

| Time | Phase | Step | Technique |
|------|-------|------|-----------|
| 0–5 min | **GENERATE** | 1–2 | Zero-shot → Few-shot |
| 5–9 min | **ANALYZE** | 3 | Role prompting |
| 9–13 min | **REPAIR** | 4–5 | Specificity + strong-vs-vague |
| 13–15 min | **TESTS (last)** | 6 | Neighboring tabs |

---

## PHASE A — GENERATE (0–5 min)

### Step 1 — Generate the function (Zero-shot)

*Pillars: **Context** (names the function/module) · **Intent** (what to return)*

In **`tip_calculator.py`**, prompt — **no examples**, just a direct ask:
```text
Write a Python function `split_bill(bill_amount, tip_percent, number_of_people)`
that adds the tip to the bill and returns how much each person pays as a float.
```
Accept the suggestion.

> 🎤 Say: *"No examples, no context beyond the goal — that's **zero-shot**. It works, but notice the rounding and format are whatever Copilot guessed."*

### Step 2 — Refine the behavior (Few-shot)

*Pillars: **Clarity** (rounding/format) · **Specificity** (exact input→output examples)*

Still in **`tip_calculator.py`**, prompt — now **give examples** to pin exact behavior:
```text
Refine split_bill so its output matches these examples exactly:
  split_bill(100.00, 20, 4) -> 30.00
  split_bill(50.00, 10, 2)  -> 27.50
  split_bill(0.00, 15, 3)   -> 0.00
Return a float rounded to 2 decimal places.
```
Quickly check one example in the terminal (`python -c "..."`) to show it matches.

> 🎤 Say: *"Same function, but the **few-shot** examples removed the ambiguity about rounding and what 'each person pays' means."*

---

## PHASE B — ANALYZE (5–9 min)

### Step 3 — Review for gaps (Role prompting)

*Pillars: **Context** (open file) · **Intent** (find what's not handled)*

In Copilot Chat (with `tip_calculator.py` open), prompt:
```text
Act as a senior Python engineer. Review split_bill in the open file and list the
edge cases and bugs that are NOT handled — for example zero people, negative
values, or bad input. Give a short bullet list, no code.
```
Read the list aloud. Expect **zero people (division by zero)** and **negatives**.

> 🎤 Say: *"Giving Copilot a **role** changes the depth of the review. This is the **Analyze** step — it finds what the happy-path code missed."*

---

## PHASE C — REPAIR (9–13 min)

### Step 4 — Repair using the review (Specificity)

*Pillars: **Specificity** (handle each edge case) · **Intent** (keep example behavior)*

Continue in the **same chat thread** so Copilot remembers its list, then prompt:
```text
Update split_bill to handle every edge case you just listed. Raise ValueError
with a clear message for invalid input. Keep the existing behavior from the
examples unchanged. Show the full updated function.
```
Paste into **`tip_calculator.py`**. Spot-check `split_bill(100, 20, 0)` raises an error.

> 🎤 Say: *"I didn't re-type the issues — the **Analyze** output **is** the spec for the **Repair**."*

### Step 5 — Vague vs. strong prompt (the punchline)

*Pillars: the weak prompt has **none**; the strong one has **all four** (Context, Intent, Clarity, Specificity)*

Type the weak prompt, show the guessy result, **don't accept**:
```text
make the tip thing better
```
Then the strong prompt:
```text
In tip_calculator.py, add float type hints to all parameters and the return value
of split_bill, add a one-line docstring, and round to exactly 2 decimals using
round(). Keep the current behavior identical.
```

> 🎤 Say: *"Same goal — the strong prompt carries all four pillars; the vague one carries none."*

---

## STEP 6 — Add the tests, LAST (13–15 min)

### Generate tests for the finished code (Neighboring tabs)

*Pillars: **Context** (reads the implementation tab) · **Specificity** (cover happy path + edge cases)*

Switch to **`test_tip_calculator.py`** (keep `tip_calculator.py` open), prompt:
```text
Using the split_bill function in the open tip_calculator.py file, write pytest
tests that cover the happy path and the edge cases it handles (zero people and
negative values should raise ValueError). Import the function at the top.
```
Run `pytest` → **all green**. ✅

> 🎤 Say: *"Because the implementation file is a **neighboring tab**, Copilot wrote tests that match the real code — no re-explaining needed."*

---

## Recap (slide-ready)

```text
TECHNIQUES
  Zero-shot       → Step 1   direct ask, no examples
  Few-shot        → Step 2   examples nail exact behavior
  Role prompting  → Step 3   persona deepens the review
  Neighboring tabs→ Step 6   open files = free context

FOUR PILLARS (in every strong prompt)
  Context     → name the file/module, keep related files open
  Intent      → state the outcome you want
  Clarity     → remove ambiguity (types, rounding, format)
  Specificity → exact values, edge cases, constraints

Loop: GENERATE (build) → ANALYZE (review) → REPAIR (fix) → then TEST.
```
