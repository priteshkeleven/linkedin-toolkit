---
name: linkedin-performance-review
description: "Post-mortem on posts already published: rank them by engagement rate, comment ratio and reach multiple instead of impressions, compare the top and bottom five by hook formula, format, length and theme, and state what to stop and do more of with the sample size attached. Use with an analytics export or pasted posts and numbers. Not for checking an unpublished draft (use linkedin-humanizer --mode audit)."
---

# LinkedIn Performance Review

The only honest source of what works for an account is that account. Every rule in every LinkedIn guide, including the ones in this bundle (`../../references/algorithm-heuristics.md`), is a prior measured on someone else's posts. The user's own last 30 posts are the evidence.

Adapted from Jake Schincariol's `li-audit` (linkedin-agent-skill, MIT).

## Input

Ask for whichever the user has:

- The content analytics export from LinkedIn (Analytics, Content, Export). CSV or XLSX.
- A screenshot per post with impressions, reactions, comments and reposts.
- Just the posts and their reaction and comment counts, which is enough for a first pass.

Also ask for the follower count, so reach can be compared to audience size.

## What to measure

Raw impressions are the least useful number, because they mostly track how many people already follow the user. Compute these instead, and show the working:

| Metric | How | What it tells you |
|---|---|---|
| **Engagement rate** | (reactions + comments + reposts) / impressions | whether the post earned its reach |
| **Comment ratio** | comments / reactions | whether it started a conversation or just got a nod |
| **Reach multiple** | impressions / follower count | whether it travelled past the existing audience |
| **Save and send rate** | if the export has it | the strongest single signal of future reach |

Rank by engagement rate and reach multiple, not impressions. A post with 900 impressions and 40 comments beat the one with 12,000 impressions and 6.

## Then find the pattern

Put the top 5 and bottom 5 side by side and look for what separates them. Be willing to conclude something the user will not like.

- **Hook formula.** Classify each post's first line against `../../references/hook-formulas.md` (the F-numbers `linkedin-hook-extractor` uses). Which formulas sit in the top 5?
- **Format.** Text, document, image, video, poll.
- **Length.**
- **Theme or pillar.**
- **First-hour replies.** Posts where the user answered comments inside the first hour, against those where they did not.
- **Day and time, last,** and only if nothing above explains the gap. It is rarely the cause and it is where people want it to be.

State each finding as a claim with the evidence and the sample size, and say how confident it is. With 30 posts a pattern can show; with 6 it cannot, and the review should say that instead of inventing one.

## Output

```
REVIEW  ·  31 posts  ·  Jun 12 - Sep 5  ·  4,200 followers

TOP 5 BY ENGAGEMENT RATE
  8.1%  F7   "$18,000 is what no contract cost me"       1,940 imp  0.46x reach
  6.4%  F11  "I fired my highest-paying client"          2,210 imp  0.53x reach
  ...

BOTTOM 5
  0.4%  --   "7 tools every founder needs"              11,400 imp  2.7x reach
            (no formula: a list opener; mark it unclassified rather than force a match)
  ...

WHAT THE DATA SAYS
1. Posts where the user paid a cost: mean 6.2% vs 1.1% for the rest. n=6.
   Strongest signal here, and not close.
2. Tool lists reach far and convert nothing: high impressions, no comments.
   Three of the bottom five.
3. Day of week shows nothing. Tuesday and Friday means are inside the noise.

STOP: tool lists.
DO MORE: posts with a cost the user paid, and a number.
```

The example's figures are illustrative. In a real review every number comes from the user's data, and a missing field is reported as missing, not estimated.

## Hard rules

Global voice rules: see root `SKILL.md` §Voice rules. Additional skill-specific rules:

- Never estimate a metric the data does not contain. Say which field is missing and what it would show.
- Report the sample size with every claim. Under 10 posts, give observations, not conclusions.
- Correlation only. Say "posts like X did better", not "X causes reach".

## Files

- `SKILL.md` — this file
- `../../references/hook-formulas.md` — formula numbers for classifying first lines
- `../../references/algorithm-heuristics.md` — the priors the user's own data is checked against
- `../../references/industry-benchmarks.md` — outside benchmarks, used only for context

## Related skills

- `linkedin-content-planner` — hand it the STOP and DO MORE lines so next week is built on the user's own evidence
- `linkedin-hook-extractor` — for classifying a single post's formula in depth
- `linkedin-engager-analytics` — who engaged with the top posts, not just how many
