---
title: "Positional Encoding: How Transformers Know Word Order"
track: ml
topic: transformers
status: in-progress
author: harsha
tags: [ml/transformers]
---

## 1. Why transformers need it at all

Self-attention is a weighted average over the whole sequence:

$$
\operatorname{Attention}(Q,K,V) = \operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

Nothing in this formula knows *where* a token sits. Shuffle the input tokens and you get the same outputs, shuffled the same way — attention is **permutation-equivariant**. "dog bites man" and "man bites dog" would be identical. So we must inject position information explicitly. Every method below is just a different answer to *where and how* to inject it.

## 2. Sinusoidal (the original — Vaswani et al. 2017)

Add a fixed vector $PE_{pos}$ to each token embedding, built from sines and cosines at geometrically spaced frequencies:

$$
PE_{(pos,\,2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right), \qquad
PE_{(pos,\,2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)
$$

![[sinusoidal-pe.png]]

```python
import numpy as np
def sinusoidal_pe(seq_len, d):
    pos = np.arange(seq_len)[:, None]          # (L, 1)
    i   = np.arange(d // 2)[None, :]           # (1, d/2)
    angles = pos / (10000 ** (2 * i / d))
    pe = np.zeros((seq_len, d))
    pe[:, 0::2] = np.sin(angles)
    pe[:, 1::2] = np.cos(angles)
    return pe
```

Why this weird construction?
- Each dimension pair is a clock ticking at a different speed — together they give every position a unique fingerprint (compare: binary counting, but smooth).
- **Key property**: $PE_{pos+k}$ is a *linear function* (a rotation) of $PE_{pos}$, so relative offsets are easy for the model to learn.
- No learned parameters; defined for any position, so in principle it extends past training length (in practice it degrades).

## 3. Learned absolute (BERT, GPT-2)

Just an embedding table: position $p$ looks up a trainable vector, added to the token embedding. Dead simple, works well — but position 1025 **does not exist** if you trained with 1024 positions. Hard ceiling on context length.

## 4. Relative position (Shaw et al. 2018; T5 bias)

Intuition: what usually matters is *how far apart* two tokens are, not their absolute indices. T5's version is the one to remember: skip position embeddings entirely and add a **learned scalar bias** $b_{i-j}$ directly to the attention logit:

$$
\text{logit}_{ij} = \frac{q_i \cdot k_j}{\sqrt{d_k}} + b_{\,\text{bucket}(i-j)}
$$

Distances are bucketed (exact for small offsets, logarithmic for large), and shared across layers. Translation-invariant by construction.

## 5. RoPE — Rotary Position Embedding (LLaMA, Qwen, most modern LLMs)

Instead of *adding* anything, **rotate** each 2-D pair of query/key dimensions by an angle proportional to the position (Su et al. 2021, arXiv:2104.09864):

$$
f(x, m) =
\begin{pmatrix} \cos m\theta & -\sin m\theta \\ \sin m\theta & \cos m\theta \end{pmatrix}
\begin{pmatrix} x_1 \\ x_2 \end{pmatrix},
\qquad \theta_i = 10000^{-2i/d}
$$

The magic: a dot product between a query rotated by $m\theta$ and a key rotated by $n\theta$ depends only on the **difference** $m-n$:

$$
\langle f(q,m),\, f(k,n)\rangle = g(q,\,k,\,m-n)
$$

So you encode *absolute* position, but attention *sees relative* position — best of both. The paper also shows the interaction naturally decays as relative distance grows.

![[rope-rotation.png]]

```python
def rope(x, pos):                       # x: (L, d), d even
    d = x.shape[-1]
    theta = 10000 ** (-np.arange(0, d, 2) / d)      # (d/2,)
    ang = pos[:, None] * theta[None, :]             # (L, d/2)
    x1, x2 = x[:, 0::2], x[:, 1::2]
    out = np.empty_like(x)
    out[:, 0::2] = x1 * np.cos(ang) - x2 * np.sin(ang)
    out[:, 1::2] = x1 * np.sin(ang) + x2 * np.cos(ang)
    return out    # applied to Q and K only, never V
```

Notes that win interview points: RoPE is applied to **Q and K only** (not V); it lives inside every attention layer rather than only at the input; long-context finetuning tricks (position interpolation / NTK scaling, as in LLaMA long-context variants) work by rescaling these rotation angles.

## 6. ALiBi — Attention with Linear Biases (BLOOM, MPT)

No embeddings at all. Add a fixed penalty proportional to distance to every attention logit (Press et al. 2021, arXiv:2108.12409):

$$
\text{logit}_{ij} = \frac{q_i \cdot k_j}{\sqrt{d_k}} - m_h \,(i-j)
$$

where each head $h$ gets a different fixed slope $m_h$ (a geometric sequence like $\tfrac{1}{2}, \tfrac{1}{4}, \dots$). Near tokens are barely penalized; far tokens fade. Its headline property: **train short, test long** — it extrapolates to sequences much longer than seen in training far better than sinusoidal or learned PE.

![[alibi-bias.png]]

## 7. Comparison table (memorize this)

| Method | Where injected | Learned? | Relative? | Extrapolates? | Used by |
|---|---|---|---|---|---|
| Sinusoidal | added to input embedding | no | indirectly | poorly | original Transformer |
| Learned absolute | added to input embedding | yes | no | no (hard cap) | BERT, GPT-2 |
| T5 relative bias | attention logits | yes | yes | somewhat | T5 |
| RoPE | rotates Q,K every layer | no | yes (via dot product) | with angle rescaling | LLaMA, Qwen, Mistral |
| ALiBi | attention logits | no | yes | **best** | BLOOM, MPT |

## 8. Worked example: sinusoidal PE with real numbers

Take a tiny model with $d=4$. Then there are two frequency pairs: $\theta_0 = 1/10000^{0} = 1$ and $\theta_1 = 1/10000^{2/4} = 0.01$.

$$
PE_{pos} = \big[\sin(pos),\ \cos(pos),\ \sin(0.01\,pos),\ \cos(0.01\,pos)\big]
$$

| pos | dim 0 (fast sin) | dim 1 (fast cos) | dim 2 (slow sin) | dim 3 (slow cos) |
|---|---|---|---|---|
| 0 | 0.000 | 1.000 | 0.000 | 1.000 |
| 1 | 0.841 | 0.540 | 0.010 | 1.000 |
| 2 | 0.909 | −0.416 | 0.020 | 1.000 |
| 3 | 0.141 | −0.990 | 0.030 | 1.000 |

Read it like a clock shop: dims 0-1 are a second hand (distinguish neighbors), dims 2-3 an hour hand (distinguish position 3 from position 300). Together the vector is unique for every position, and all values stay in $[-1,1]$ — no magnitude blow-up like a raw ramp $pos$ would cause.

**The linear-shift property, concretely.** For one frequency, the pair at position $pos$ is $(\sin\omega\, pos, \cos\omega \,pos)$. The angle-addition identities give

$$
\begin{pmatrix} \sin \omega(pos+k) \\ \cos \omega(pos+k) \end{pmatrix}
=
\begin{pmatrix} \cos\omega k & \sin\omega k \\ -\sin\omega k & \cos\omega k \end{pmatrix}
\begin{pmatrix} \sin \omega\, pos \\ \cos \omega\, pos \end{pmatrix}
$$

so "shift by $k$" is one fixed rotation matrix, independent of $pos$. A single linear layer can therefore learn "attend 3 tokens back" — the design goal stated in the original paper.

## 9. Worked example: RoPE really only sees distance

Let a query and key both be the 2-D vector $(1, 0)$, with $\theta = 0.5$ rad.

- Query at position $m=3$: rotated by $1.5$ rad → $q' = (\cos 1.5, \sin 1.5) = (0.071, 0.997)$
- Key at position $n=1$: rotated by $0.5$ rad → $k' = (0.878, 0.479)$
- Dot product: $0.071 \times 0.878 + 0.997 \times 0.479 = 0.540 = \cos(1.0)$

Now move both tokens 10 positions to the right ($m=13, n=11$): the rotations change, but the dot product is again $\cos\big((13-11)\times 0.5\big) = \cos(1.0) = 0.540$. Identical. In general, for rotations the dot product only sees the **angle difference**:

$$
\langle R(m\theta)\,q,\; R(n\theta)\,k \rangle = \langle q,\; R\big((n-m)\theta\big)\,k \rangle
$$

because rotation matrices satisfy $R(a)^\top R(b) = R(b-a)$. That one line is the whole RoPE proof, and it's a favorite "show me" prompt in research-engineer loops. A full $d$-dim head is just $d/2$ independent 2-D rotations at frequencies $\theta_i = 10000^{-2i/d}$ — same clock-shop idea as sinusoidal PE, but applied multiplicatively to Q and K inside every layer.

Why not rotate V? Position should change **who attends to whom** (the matching), not **what content gets mixed** once the weights are decided. Rotating V would corrupt the payload.

## 10. Worked example: ALiBi head slopes

With 8 heads, slopes are the geometric sequence $m_h = 2^{-h}$: $\tfrac{1}{2}, \tfrac{1}{4}, \tfrac{1}{8}, \dots, \tfrac{1}{256}$. For a query at position 10:

| key position | distance | head 1 penalty ($m=\tfrac12$) | head 8 penalty ($m=\tfrac{1}{256}$) |
|---|---|---|---|
| 9 | 1 | −0.5 | −0.004 |
| 5 | 5 | −2.5 | −0.020 |
| 0 | 10 | −5.0 | −0.039 |

Head 1 is myopic (effectively a local-window head); head 8 barely cares about distance (a global head). The model gets a spectrum of receptive fields for free, with **zero learned position parameters** — which is exactly why it extrapolates: position 5000 is not "unseen", it's just a bigger penalty on the same line.

## 11. Long-context: what actually breaks

- **Learned absolute**: position 4097 has no embedding row. Hard crash of quality; only fix is retraining/resizing.
- **Sinusoidal**: defined for any position, but the model never *saw* those phase combinations; quality decays.
- **RoPE**: at unseen positions the fast-frequency dims spin into unseen angle territory. **Position interpolation** rescales positions ($m \to m \cdot \frac{L_{train}}{L_{new}}$) to squeeze new lengths into the trained angle range, then briefly finetunes — the standard recipe behind long-context LLaMA variants (NTK-aware scaling is the refinement that rescales frequencies unevenly).
- **ALiBi**: designed for this; train-short-test-long is its headline result.

## 12. Questions actually asked in top-company loops

Paraphrased from published interview collections and prep guides (myengineeringpath.dev LLM question set; Towards Data Science and learncodecamp RoPE guides; igotanoffer FAANG ML question roundups):

1. **"Why do transformers need positional encoding at all when RNNs don't?"** — attention is permutation-equivariant (Section 1); RNNs get order for free from recurrence.
2. **"Write the sinusoidal formula and explain the 10000."** — it sets the geometric frequency ladder; smallest wavelength $2\pi$, largest $2\pi \cdot 10000$, so both neighbors and far positions are distinguishable.
3. **"Why sin *and* cos, not just sin?"** — the pair makes shift-by-$k$ a rotation (Section 8's identity); with sin alone the map from position to phase is ambiguous and not linearly shiftable.
4. **"Explain RoPE to me like I haven't read the paper"** (Meta/DeepMind-style, per the RoPE explainers above) — rotate Q and K by position-proportional angles; dot products then depend only on relative distance; show the $R(a)^\top R(b)=R(b-a)$ step.
5. **"Why apply RoPE to Q,K but not V?"** — matching vs content (Section 9).
6. **"Model trained at 4k, need 32k — options?"** — per method (Section 11); expected to mention position interpolation + short finetune for RoPE, and why ALiBi models mostly just work.
7. **"Additive PE vs bias-in-attention vs rotation — compare"** — the table in Section 7; the deep answer notes *where* information enters: once at the input (sinusoidal/learned) vs every layer's attention (T5/RoPE/ALiBi), and that input-level PE can wash out in deep stacks.
8. **"Does BERT use sinusoidal PE?"** — a common trap: no, BERT uses *learned absolute* embeddings; the original Transformer used sinusoidal.
9. (System-design flavored) **"You're fine-tuning LLaMA for 100k-token legal documents — walk me through the positional-encoding implications end to end."**

*Grounding: Vaswani et al. 2017; Su et al. 2021 (arXiv:2104.09864, abstract fetched — rotation formulation, relative dependency, distance decay); Press et al. 2021 (ALiBi, arXiv:2108.12409); the fetched/search-listed explainers above for what interviewers emphasize. Question phrasings are paraphrased.*
