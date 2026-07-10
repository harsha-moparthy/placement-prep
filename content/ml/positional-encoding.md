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

## 8. Interview questions to be ready for
1. Prove/explain why attention without PE is permutation-equivariant.
2. Write the sinusoidal formula. Why sinusoids and not a linear ramp $pos/L$? (unique smooth fingerprint, relative shifts are rotations, no magnitude explosion)
3. Why does RoPE apply to Q and K but not V? (position should influence *matching*, not the *content* being aggregated)
4. Show that RoPE attention depends only on $m-n$.
5. Your model was trained on 4k context. What breaks at 8k for each method, and what is the cheapest fix? (learned: breaks outright; RoPE: rescale angles + light finetune; ALiBi: mostly just works)
6. Where does each method inject position — input vs every attention layer — and why does that matter?

*Grounding: Vaswani et al. 2017 (Attention Is All You Need) for sinusoidal; Su et al. 2021 arXiv:2104.09864 abstract fetched for RoPE claims (rotation matrix, relative dependency, decay, length flexibility); Press et al. 2021 arXiv:2108.12409 for ALiBi; Raffel et al. 2020 for T5 bias.*
