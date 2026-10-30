"""Day 1 learning script: see what an LLM actually "reads".

Run from the backend folder (with the venv active):
    python ..\\learning\\day01_tokens.py

The first run downloads the tokenizer vocabulary (~2 MB), then it is cached.
"""

import tiktoken

BRIEF = (
    "Prepare the property for a premium real estate listing. Keep the outdoor view "
    "visible through the windows. Avoid oversaturated colours. Prioritise the kitchen "
    "and living room."
)

# o200k_base is the tokenizer used by recent OpenAI models. Gemini, Llama etc.
# use different tokenizers, so the exact counts differ - but the idea is identical.
enc = tiktoken.get_encoding("o200k_base")

token_ids = enc.encode(BRIEF)
pieces = [enc.decode([t]) for t in token_ids]

print(f"Characters: {len(BRIEF)}")
print(f"Words:      {len(BRIEF.split())}")
print(f"Tokens:     {len(token_ids)}\n")
print("First 20 tokens (id -> text piece):")
for tid, piece in list(zip(token_ids, pieces))[:20]:
    print(f"  {tid:>7} -> {piece!r}")

print("\nThings to notice:")
print(" - Common words are one token; rare words split into pieces.")
print(" - Spaces are usually glued to the start of the next word.")
print(" - You pay per token, and the context window is measured in tokens.")

for word in ["kitchen", "oversaturated", "Prioritise", "Prioritize", "சமையலறை"]:
    print(f"   {word!r:>18} -> {len(enc.encode(word))} token(s)")
