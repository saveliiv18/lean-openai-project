import Mathlib.Data.Real.Basic
import Mathlib.Tactic

theorem sub_mul_sub (a b c d : ℝ) :
    (a - b) * (c - d) = a * c - a * d - b * c + b * d := by
  ring