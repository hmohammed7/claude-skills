---
name: research
description: Research, look into, compare, fact-check or "figure out" anything that needs outside facts - and run it before any build task that depends on outside facts, like an API's real limits, a tool's real behaviour or a licence's real wording. Use when I say "research X", "look into X", "compare X and Y", "is it true that...", "fact-check this", "figure out whether...", "check the docs for...", or when a paper or citation needs verifying. Not for questions answerable from my own files, code or brain vault (search those instead).
---

# Research

Research is only worth doing if it changes a decision. These gates and rules keep it short when it
can be short, and honest when it has to be long.

## Gate 1: name the decision

Before the first search, write one line: **"This feeds: <the decision>"**
(e.g. "This feeds: whether the Obby leaderboard can use OrderedDataStore without hitting limits").

- **No decision?** Give a short answer from 1-3 searches, still following the four rules, and save
  nothing. Say "No decision named, so this is a quick answer and nothing was saved."
- If the decision depends on my own files, code or brain, check those first; outside research only
  fills what they can't answer.

## Gate 2: choose a depth and say which

| Depth | Searches | Use when |
|---|---|---|
| **quick** | 1-3 | One fact, low stakes, easy to undo (a property name, a default value) |
| **standard** | 5-12 | A build choice, a comparison, anything that costs hours if wrong |
| **deep** | 12+ | Money, legal or licence wording, platform rules that can get a game taken down, or sources disagree |

Write **"Depth: <quick|standard|deep> - <one reason>"** right under the decision line. If the
evidence turns out messier than expected, say you're moving up a depth and why.

## The four rules

1. **Judge a source by what others say about its publisher**, not by how it looks or what it says
   about itself. Official docs and the vendor's own forum staff beat blogs; a blog that other
   reputable sources cite beats one nobody mentions. For an unfamiliar publisher, do one search
   about the publisher itself.
2. **Count origins, not repeats.** Ten articles quoting the same tweet or press release are one
   source. Trace a claim back to where it started before counting it as confirmed.
3. **Never cite a source you haven't opened.** A search snippet is not a source. If a page couldn't
   be opened (paywall, error, blocked), say so and don't lean on it. For academic papers, run
   `scripts/verify_sources.py` on the citations before citing them.
4. **At least one search tries to break the answer.** Search for the opposite: "X not working",
   "X limit exceeded", "X deprecated", "X vs Y problems", "X wrong". Report what it found, even
   if it found nothing.

## Workflow

1. Gate 1 and Gate 2 (two lines, shown to me).
2. Search. Open the sources you'll rely on (rule 3). Note what each one is and who published it.
3. Run the breaking search (rule 4).
4. **Before reporting, re-read the draft against the four rules.** Every claim must point to an
   opened source or be marked as inference; any "confirmed" claim must have 2+ independent origins.
   Fix anything that fails.
5. Write the report (format below).
6. Save a note only if the save rule says so.

## Report format

Lead with the answer. Keep it short; this is a decision aid, not an essay.

```
**Answer:** 1-3 sentences that settle the decision (or say plainly that it can't be settled yet).

**What the evidence shows**
- <claim> - **measured** (I tested or ran it) | **one source said** (<source>) | **sources agree** (<n> independent origins: <sources>) | **my inference** (from <what>)

**What the evidence does NOT support**
- Claims people make that the sources don't back, and conclusions it would be tempting but wrong to draw.

**Limits**
- Searches run: <n> (list the queries for standard/deep)
- Read in full: <sources> | Skimmed: <sources> | Couldn't open: <sources>
- Gaps: what's still unknown and what would settle it
```

Every claim gets exactly one of the marks above. "One source said" is fine; hiding that it's only
one source is not.

## Verifying paper citations

```powershell
python "$env:USERPROFILE\.claude\skills\research\scripts\verify_sources.py" citations.txt
python "$env:USERPROFILE\.claude\skills\research\scripts\verify_sources.py" --cite "LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521, 436-444."
```

One citation per line (blank lines and lines starting with `#` are skipped). Uses the free Crossref
API, no key needed. Results:

- **VERIFIED** - Crossref has a record whose title, first author and year all match.
- **MISMATCH** - a close record exists but the title, author or year differ. Check the details
  shown; the citation may be garbled, or the paper may be made up from a real one.
- **NOT FOUND** - no record comes close. Treat the paper as unconfirmed; don't cite it.
- **ERROR** - Crossref couldn't be reached, so nothing was checked. Never read this as NOT FOUND.

Run one citation first before a long list. Exit code: 0 all verified, 1 any problem, 2 bad input
or empty list. Crossref covers most journals and conferences with DOIs but not every book, preprint
or thesis, so NOT FOUND for those means "check by hand", not "fake". (Example: "Attention Is All
You Need" (NeurIPS 2017) is NOT FOUND because Crossref has no record of the original.)

After changing the script, run `python tests/run_tests.py` (live Crossref calls, all must pass).

## Saving to the brain

Save a note **only if both** are true:
- it feeds a live project (one listed under Active projects in `Brain Root.md`), and
- depth was standard or deep.

Otherwise save nothing. If you're unsure it's worth keeping, it goes in `90 Inbox`.

To save, follow the brain skill's SYNC steps: `next-id RES`, write the note into `30 Research`
from `00 System/Templates/Research.md` with today's date in `created:`/`updated:`, fill its four
sections from the report, and add a `## Sources` section listing every source with its URL and
the date it was opened. Link the project it feeds with `[[Project name]]`.
