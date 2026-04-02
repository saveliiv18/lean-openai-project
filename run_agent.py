import subprocess
import re
from openai import OpenAI

client = OpenAI()

prompt = """
Write Lean 4 code ONLY.

Rules:
- Use Lean 4 syntax only.
- Do not use `begin` / `end`; use `by`.
- Do not use `rw [mul_sub]`.
- Do not invent imports, theorem names, or lemmas.
- Use only the imports listed below.
- Use `ring_nf` if needed.
- Do not weaken, restate, or replace the theorem.
- Return only Lean code.

Use exactly these imports:
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

Prove this theorem exactly:

\begin{theorem}
For all natural numbers $k$,
\[
\frac{(k+1)(k+2)}{2}=\frac{k(k+1)}{2}+(k+1).
\]
\end{theorem}



Return only valid Lean code.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

lean_code = response.output_text

# remove markdown fences if they exist
lean_code = re.sub(r"```.*?\n", "", lean_code)
lean_code = lean_code.replace("```", "")

print("Generated Lean code:\n")
print(lean_code)

# write to Lean file
with open("Myproject/Basic.lean", "w") as f:
    f.write(lean_code)

print("\nRunning Lean build...\n")

result = subprocess.run(["lake", "build"], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)
