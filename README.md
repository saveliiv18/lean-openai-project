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
Requires:

Lean 4 + Lake
mathlib (v4.28.0)
Python 3 + openai package (pip install openai)
OPENAI_API_KEY set in environment

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

### NOTE: 
We got a selection of the following OpenAI models to use to prove lemmas with their pros and cons listed:

-gpt-4.1-mini:
Fast and cheap. Good for simple, well-known theorems where the proof strategy is obvious. Fails on anything requiring creative tactic selection or multi-step reasoning. Hallucinates lemma names frequently.
-o4-mini:
Best balance for this use case. Slower than 4.1-mini but reasons through proof structure before generating, so it hallucinates far less and needs fewer retries. Good for medium-hard theorems. Costs more per call but saves money overall by not burning through retries. Recommended default for Lean proving.
-o3:
Strongest reasoning of the three. Will attempt and often solve theorems that o4-mini gets stuck on. Very slow (can take minutes per attempt) and expensive. Only worth it for theorems where o4-mini is consistently failing after all retries.

## Example

Prompt:
--- Attempt 1/5 ---
Generated Lean code:
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem ...

Running lake build...

Proof verified on attempt 1!
