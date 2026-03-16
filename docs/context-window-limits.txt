Great question. The limiting factors are actually a layered stack — hardware KV cache is *one* of them, but not the only one, and often not the binding constraint in practice.

## The Real Limiting Factors (in order of typical impact)

**1. Memory (VRAM) — usually the primary hardware constraint**

The KV cache is the main culprit here. For each token in the context, the model stores key and value tensors for every attention head in every layer. This grows as:

```
KV cache size = 2 × num_layers × num_heads × head_dim × context_length × bytes_per_element
```

For a large model (e.g. 70B params) at 16-bit precision, a 128K context can consume **hundreds of GB of VRAM** — easily exceeding what's available even on high-end multi-GPU rigs. This is why providers aggressively use techniques like GQA (Grouped Query Attention) and quantisation.

**2. Attention computation — quadratic scaling**

Standard self-attention is **O(n²)** in both time and memory relative to sequence length. Double the context → 4× the attention cost. This is a fundamental algorithmic bottleneck, not just a hardware one. Techniques like Flash Attention mitigate the memory overhead but don't change the compute complexity.

**3. Latency / time-to-first-token (TTFT)**

Even if you *have* the VRAM, prefilling a 1M token context takes significant wall-clock time. For coding agents doing iterative reasoning loops, this compounds badly — you're re-prefilling on every turn.

**4. Model architecture decisions**

Models are *trained* with a maximum context length baked in (positional encodings, RoPE scaling etc.). You can't just extend context at inference time beyond what the model was trained to handle without degradation — the model literally hasn't learned to attend reliably at those distances.

**5. "Lost in the middle" — attention quality degradation**

Even within a model's stated context limit, empirical research shows models attend well to the **beginning and end** of context but lose coherence in the middle. For coding agents with large codebases injected as context, this is often the *practical* limiting factor before hardware even becomes the issue.

---

## For Coding Agents Specifically

The real-world ceiling is usually a combination of:

| Constraint | Typical Binding Point |
|---|---|
| VRAM / KV cache | ~100K–200K tokens on commodity hardware |
| Attention quality degradation | ~32K–128K tokens in practice |
| Cost per token | Often the first thing that limits you in production |
| Latency per loop iteration | Compounds in agentic multi-step workflows |

---

## What Practitioners Do Instead

Rather than fighting the context limit, most production coding agents use **retrieval-augmented approaches** — chunking codebases, embedding them, and retrieving only relevant context per step. This sidesteps the hardware problem entirely. For your self-learning architecture, this is almost certainly the right direction — maintaining a vector store of code/skill knowledge that gets selectively injected rather than stuffing everything into a single window.