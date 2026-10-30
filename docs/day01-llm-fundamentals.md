# Day 1 — LLM fundamentals, and why today's API has no LLM in it

## 1. Generative AI and LLMs

Classic ML *classifies*: given a photo, output "kitchen". Generative AI *produces new content*: text, images, code.

A **Large Language Model** is a neural network (a Transformer) trained on a huge amount of text to do one thing: **given some text, predict the next piece of text.** That's it. Chat, summaries, JSON extraction — all of it is next-token prediction run in a loop:

```
"Prioritise the kitchen and"  →  model scores every possible next token
                               →  " living" is most likely → append it
"Prioritise the kitchen and living"  →  " room" → append ... and so on
```

You've trained a Vision Transformer for blood cells, so you already know the core idea: input becomes vectors, attention layers mix information between positions, a head produces probabilities. An LLM is the same family, much bigger, with text as input and "next token" as the label.

## 2. Tokens

Models don't read characters or words — they read **tokens**: chunks from a fixed vocabulary (~100k–200k entries). Common words are one token; rare words are split ("oversaturated" → several pieces). Each token is an integer ID.

Why you care:
- **Cost** — APIs charge per input token and per output token (output usually costs more).
- **Limits** — every model has a maximum number of tokens it can see at once.
- **Language** — non-English text usually needs more tokens for the same meaning. Run the script and look at the Tamil word.

Run `python ..\learning\day01_tokens.py` to see your client brief as tokens.

## 3. Context window

The **context window** is the model's working memory: system instructions + your prompt + any documents you paste in + its own answer, all counted in tokens. Anything outside the window doesn't exist for the model. It has no memory between API calls unless *you* send the history again.

This is why RAG (milestone 8) exists: you can't paste 500 photo descriptions into every call, so you *retrieve* the 10 relevant ones and send only those.

## 4. Sampling and temperature

The model outputs a probability for every token. **Temperature** controls how it picks:
- Low (0–0.3): almost always the top choice → consistent. Use for JSON extraction, like brief parsing.
- High (0.8+): more variety → use for creative listing descriptions.

Even at temperature 0, outputs aren't guaranteed identical across runs or model versions. That's why we store model version and prompt version with every result.

## 5. Prompts and LLM APIs (preview of milestone 3)

An API call is just an HTTP request with a list of messages (system instructions, user input) and settings (model, temperature, max output tokens, optional JSON schema). The response is text plus token counts. You already know REST — the new skill is writing instructions the model follows reliably, and *never trusting the answer until it validates*.

## 6. Why Day 1 uses OpenCV, not an LLM

| Task | Right tool | Why |
|---|---|---|
| Is it blurry? | Laplacian variance | Measurable maths, 5 ms, free, same answer every time |
| Is it too dark? | Histogram / mean | Same |
| Exact duplicate? | SHA-256 | Same |
| Which room is it? | CLIP (milestone 4) | Needs visual understanding, but a small free model suffices |
| What does the client want? | LLM (milestone 3) | Messy natural language — only an LLM handles this well |

A good GenAI engineer's first question is "does this need an LLM at all?"

### How the two checks work

**Blur — variance of the Laplacian.** The Laplacian is a second-derivative filter: it responds strongly at edges and ~0 on flat areas. A sharp photo has many strong edges, so the response *varies* a lot. A blurry photo is smoothed, edges are weak, variance is low. We resize to 1024 px first because variance depends on resolution.

Limitation: a genuinely plain wall is "flat" too and can look blurry. That's a known false positive; milestone 4 measures how often it happens.

**Exposure — mean + clipping.** The mean says if the image is dark or bright overall. Clipping % says how many pixels are pure black (≤5) or pure white (≥250) — lost detail that editing can't recover. Interiors with windows often have fine averages but a blown-out window; the API reports that separately because your brief example ("keep the outdoor view visible") depends on it.

## Exercise

1. Add a `sharpness_score` (0–100) to `BlurResult` — e.g. `min(100, variance / threshold * 50)` — and a test for it.
2. Run the API on 10 of your real-estate photos (mix of good, blurry, dark, bright windows). Write down which verdicts look wrong. Bring that list to the next session — it's the seed of your evaluation set.
3. Answer in your own words: why would sending every photo to a vision LLM for blur detection be a bad design? (Think cost, speed, consistency.)
