---
title: "Sample: Linearity of Expectation"
track: quant
topic: expectation
status: done
author: akanksh
tags: [quant/expectation]
---

Sanity-check note: LaTeX, images, and frontmatter-driven progress all render from this file.

Inline math: $E[X+Y] = E[X] + E[Y]$ holds even when $X, Y$ are dependent.

Block math (delimiters on own lines):

$$
E\left[\sum_{i=1}^{n} X_i\right] = \sum_{i=1}^{n} E[X_i]
$$

> [!tip] Interview pattern
> Indicator variables + linearity kills most "expected number of ..." questions.

Classic: expected fixed points of a random permutation $= n \cdot \frac{1}{n} = 1$.
