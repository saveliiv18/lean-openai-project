# Myproject

This project experiments with using an LLM to generate Lean 4 proofs and verify them with Lean/mathlib.

The agent sends a theorem prompt to GPT, writes the output to Myproject/Basic.lean, runs lake build, and if it fails, feeds the compiler error back to GPT to fix — up to MAX_RETRIES times.
GPT-4.1-mini → Lean code → lake build → [error?] → GPT fix → repeat
This mirrors the core idea from Numina-Lean-Agent: use compiler feedback to iteratively correct proofs rather than hoping the first generation is correct.

## Files
- `run_agent.py` — sends a prompt to OpenAI, writes generated Lean code to `Myproject/Basic.lean`, and runs `lake build`
- `Myproject/Basic.lean` — main Lean file being tested
- `Myproject.lean` — imports `Myproject.Basic`
- `lakefile.toml` / `lake-manifest.json` / `lean-toolchain` — Lean project configuration

## Setup
Make sure the following are installed:
- Lean 4
- Lake
- mathlib dependencies

Then run:

```bash
lake update
lake build
```


#Usage

To generate and test Lean code:

Run:
```bash
python3 run_agent.py
```

Current goal:
The project is currently being used to test whether LLM-generated Lean proofs can verify graph-theoretic and arithmetic lemmas step by step.



## Example

Prompt:
"Prove that n + 0 = n"

Generated Lean code:

theorem add_zero_example (n : ℕ) : n + 0 = n := by
  simp
