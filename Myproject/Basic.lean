import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem nat_sum_eq (k : ℕ) : ((k + 1) * (k + 2)) / 2 = (k * (k + 1)) / 2 + (k + 1) := by
  ring_nf
