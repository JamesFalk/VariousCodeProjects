# crossword_scratcher_analyzer.py
# Works in Pydroid 3 (install numpy if you want faster random – optional)
# ---------------------------------------------------------------
import random
import string
from collections import Counter
from typing import List, Tuple, Dict

# ---------------------------------------------------------------
# 1. CONFIGURATION – change only this part for a new ticket
# ---------------------------------------------------------------

# ---- WORDS (all UPPERCASE, only A-Z) ---------------------------------
THREE  = ["RAT", "TEA", "RED", "ICE"]          # 4 × 3-letter
FOUR   = ["BEAN", "TWO", "NEED", "BOOK", "BEST"]  # 5 × 4-letter
FIVE   = ["CHEF", "CHESS", "BATHS"]           # 3 × 5-letter
SIX    = ["EATING", "ACROSS", "BATTLE"]       # 3 × 6-letter
SEVEN  = ["CLEANER"]                           # 1 × 7-letter
EIGHT  = ["EXCESSIVE", "ENGINEER"]            # 2 × 8-letter
NINE   = ["BACTERIA"]                          # 1 × 9-letter

# ---- PRIZE TABLE (word-count → multiplier) -------------------------
# The same for every ticket price ($2,$3,$5,$10,$20)
PRIZE_MULTIPLIER = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 5,
    5: 10,
    6: 15,
    7: 20,
    8: 40,
    9: 50,
    10: 100,
    11: 500,
    12: 1000,
    13: 5000,
    14: 10000,
    # 15+ words is impossible with only 18 call-letters → 0
}

# ---- SIMULATION SETTINGS --------------------------------------------
SIMULATIONS = 1_500_000          # 1.5 million draws
CALL_LETTERS = 18                # exactly 18 unique letters per draw

# ---------------------------------------------------------------
# 2. PRE-PROCESS WORDS → list of required letter counts
# ---------------------------------------------------------------
def word_to_req(word: str) -> Counter:
    """Return Counter of required letters for ONE word (A=1 … Z=26)."""
    return Counter(ord(c) - ord('A') + 1 for c in word)

ALL_WORDS = (
    [word_to_req(w) for w in THREE] +
    [word_to_req(w) for w in FOUR] +
    [word_to_req(w) for w in FIVE] +
    [word_to_req(w) for w in SIX] +
    [word_to_req(w) for w in SEVEN] +
    [word_to_req(w) for w in EIGHT] +
    [word_to_req(w) for w in NINE]
)

TOTAL_WORDS = len(ALL_WORDS)   # 4+5+3+3+1+2+1 = 19

# ---------------------------------------------------------------
# 3. MAIN SIMULATION
# ---------------------------------------------------------------
def can_form_word(req: Counter, available: Counter) -> bool:
    """True if every letter in req is present in available (enough times)."""
    for let, need in req.items():
        if available.get(let, 0) < need:
            return False
    return True

def run_simulation() -> Dict[int, int]:
    prize_hits = Counter()

    for _ in range(SIMULATIONS):
        # ---- draw 18 unique letters (1-26) ----
        draw = random.sample(range(1, 27), CALL_LETTERS)
        available = Counter(draw)

        # ---- count how many ticket-words can be formed ----
        completed = sum(1 for req in ALL_WORDS if can_form_word(req, available))

        # ---- map to multiplier (prize) ----
        mult = PRIZE_MULTIPLIER.get(completed, 0)
        prize_hits[mult] += 1

    return prize_hits

# ---------------------------------------------------------------
# 4. RUN & PRINT RESULTS
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("Starting 1.5 million simulations … (this takes ~30-60 s on a phone)")
    hits = run_simulation()

    print("\n=== PROBABILITY TABLE ===")
    print(f"{'Prize multiplier':<18} {'% of tickets':<12} {'Hits':<10}")
    print("-" * 42)
    total = SIMULATIONS
    for mult in sorted(hits):
        percent = hits[mult] / total * 100
        print(f"{mult:>16}x {'':>4}{percent:>8.4f}%  {hits[mult]:>8,}")
    # also show the “no win” case (multiplier 0)
    if 0 not in hits:
        print(f"{'0x':>16} {'':>4}{'0.0000'%:>8}  {'0':>8}")

    # ---------------------------------------------------------------
    # 5. OPTIONAL: quick sanity check – expected words per draw
    # ---------------------------------------------------------------
    avg_words = sum(k * v for k, v in hits.items() if k in PRIZE_MULTIPLIER) / total
    print(f"\nAverage completed words per ticket: {avg_words:.3f}")
    