# ============================================================
# run_agent.py
#
# This script uses GPT-4.1-mini to generate a Lean 4 proof,
# then verifies it by running `lake build`. If the build fails,
# it feeds the Lean compiler error back to GPT so it can fix
# its own code. This retry loop repeats up to MAX_RETRIES times.
#
# This mirrors the core idea from the Numina-Lean-Agent paper:
# use compiler feedback to iteratively correct proofs, rather
# than hoping the first generation is correct.
# ============================================================

import subprocess
import re
from openai import OpenAI

client = OpenAI()

# How many times we allow GPT to attempt + fix the proof before giving up.
MAX_RETRIES = 5

# ============================================================
# INITIAL_PROMPT
# This is the prompt sent on the very first attempt.
# It gives GPT the theorem to prove and strict rules to follow.
#
# Key fix vs the original: we explicitly cast k to ℚ (rationals)
# so that division works correctly. In Lean 4, dividing natural
# numbers (ℕ) uses integer (floor) division, which breaks ring
# identities involving fractions. By casting to ℚ, division is
# exact and `ring` can close the goal in one step.
# ============================================================
INITIAL_PROMPT = """
Write Lean 4 code ONLY.

Rules:
- Use Lean 4 syntax only.
- Do not use `begin` / `end`; use `by`.
- Do not use `rw [mul_sub]`.
- Do not invent imports, theorem names, or lemmas.
- Use only the imports listed below.
- Do not use `let ... in` syntax (that is Lean 3). Use `let x := ...` on its own line.
- Do not weaken, restate, or replace the theorem.
- If the theorem involves division over rationals (ℚ), NOT natural numbers (ℕ).
  Cast k as (k : ℚ) so that division behaves correctly.
- Try `ring` first to close the goal. Only use `ring_nf` if `ring` alone is insufficient.
- Return only Lean code, no explanation, no markdown fences.

Use exactly these imports:
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

Prove this theorem exactly:


"""

# ============================================================
# RETRY_PROMPT_TEMPLATE
# This prompt is used on attempt 2, 3, 4, ... (after a failure).
# It shows GPT:
#   1. The code it previously generated
#   2. The exact error from the Lean compiler
# Then asks it to fix the code.
#
# The {lean_code} and {error} placeholders are filled in at
# runtime using .format() with the actual values from the
# previous failed attempt.
# ============================================================
RETRY_PROMPT_TEMPLATE = """
The Lean 4 code you generated previously failed to compile.

Previous code:
```lean
{lean_code}
```

Lean compiler error:
```
{error}
```

Fix the code so it compiles correctly. Rules:
- Use Lean 4 syntax only. No `begin`/`end`. No `let ... in`.
- The theorem must use (k : ℚ) so division is over rationals, not natural numbers.
- Try `ring` to close the goal. Use `ring_nf` + additional tactics only if needed.
- Do not invent lemma names. Do not change the theorem statement.
- Return only valid Lean 4 code, no explanation, no markdown fences.

Use exactly these imports:
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
"""


def strip_markdown(code: str) -> str:
    """
    GPT sometimes wraps its output in markdown code fences like:
        ```lean
        theorem ...
        ```
    This function removes those fences so we're left with raw
    Lean code that can be written directly to a .lean file.
    """
    code = re.sub(r"```[a-zA-Z]*\n", "", code)  # remove opening fence e.g. ```lean
    code = code.replace("```", "")               # remove closing fence
    return code.strip()


def generate_lean(prompt: str) -> str:
    """
    Sends a prompt to GPT-4.1-mini and returns the generated
    Lean code as a clean string (markdown fences removed).
    """
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return strip_markdown(response.output_text)


def write_lean_file(code: str, path: str = "Myproject/Basic.lean"):
    """
    Writes the generated Lean code to disk so that `lake build`
    can pick it up and compile it. Overwrites the file each time
    so previous attempts don't linger.
    """
    with open(path, "w") as f:
        f.write(code)


def run_lean_build() -> tuple[bool, str, str]:
    """
    Runs `lake build` as a subprocess and captures its output.

    Returns a tuple of:
        success (bool)  — True if the build exited with code 0 (proof verified)
        stdout  (str)   — standard output from lake
        stderr  (str)   — standard error from lake (this is where Lean errors appear)
    """
    result = subprocess.run(["lake", "build"], capture_output=True, text=True)
    success = result.returncode == 0
    return success, result.stdout, result.stderr


def main():
    print("=" * 60)
    print("Lean Proof Agent — GPT-4.1-mini + Retry Loop")
    print("=" * 60)

    lean_code = None   # holds the most recently generated Lean code
    last_error = None  # holds the most recent compiler error (used in retry prompt)

    # --------------------------------------------------------
    # Main retry loop.
    # range(1, MAX_RETRIES + 1) gives us attempts 1, 2, 3, 4, 5.
    # On attempt 1: use the initial prompt (fresh generation).
    # On attempts 2+: use the retry prompt (error-guided fix).
    # If the build succeeds, we break out early.
    # If all attempts fail, the `else` block on the for loop runs.
    # --------------------------------------------------------
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- Attempt {attempt}/{MAX_RETRIES} ---")

        if attempt == 1:
            # First try: send the original theorem prompt
            prompt = INITIAL_PROMPT
        else:
            # Subsequent tries: inject the previous code + error
            # so GPT knows exactly what went wrong and can fix it
            prompt = RETRY_PROMPT_TEMPLATE.format(
                lean_code=lean_code,
                error=last_error
            )

        # Ask GPT to generate (or fix) the Lean proof
        lean_code = generate_lean(prompt)

        print("Generated Lean code:")
        print(lean_code)

        # Write the code to disk so lake can compile it
        write_lean_file(lean_code)

        print("\nRunning lake build...")
        success, stdout, stderr = run_lean_build()

        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

        if success:
            # Build passed — Lean accepted the proof, we're done
            print(f"\n Proof verified on attempt {attempt}!")
            break
        else:
            # Build failed — save the error so we can send it back to GPT
            last_error = stderr or stdout
            print(f"\n Attempt {attempt} failed. Retrying with error feedback...\n")
    else:
        # This `else` runs only if the loop exhausted all retries without breaking
        print(f"\n All {MAX_RETRIES} attempts failed. Last generated code:")
        print(lean_code)
        print("\nLast error:")
        print(last_error)


# Only run main() if this script is executed directly,
# not if it's imported as a module by another script.
if __name__ == "__main__":
    main()
