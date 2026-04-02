from openai import OpenAI

client = OpenAI()

prompt = """
How to prevent unexpected token 'in' from being geenrated in:

\begin{lemma}[Self-contained version of Lemma 1]
Let $n>1$ and let $m$ be an integer satisfying
\[
n-1 \le m \le \frac{n(n-1)}{2}.
\]
Define
\[
k := \left\lfloor \frac{\sqrt{\,1+8(m-n+1)\,}-1}{2}\right\rfloor,
\qquad
\ell := m-n+1-\frac{k(k+1)}{2}.
\]
Then $k,\ell \in \mathbb{Z}_{\ge 0}$, $\ell \le k$, and they are the unique nonnegative integers satisfying
\[
m = n-1+\frac{k(k+1)}{2}+\ell,
\qquad
0 \le \ell \le k.
\]
\end{lemma}
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

print(response.output_text)

