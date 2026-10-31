# LinkedIn Toolkit

**16 Claude Code and Codex skills for LinkedIn.** They write posts, carousels, comments, replies and DMs in your voice, triage your inbox, score your profile, review what already performed, and strip AI tells with two local scripts that actually run. Nothing is posted until you approve it, and by default nothing is posted at all: you paste the approved text yourself.

This bundle merges two MIT-licensed projects and keeps the strongest part of each:

- **[sergebulaev/linkedin-skills](https://github.com/sergebulaev/linkedin-skills)** is the base: 12 skills, the evidence-based V3 humanizer, 20 hook formulas, the founder layer, the Story Bank interviewer, the optional Apify read layer, and the test suite.
- **[Jakeschincariol/linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)** adds the runnable humanizer tools (rebuilt to follow the V3 rules), the 100-point profile rubric, and the carousel, DM, inbox and post-performance skills.

Full credit and copyright for both are in [`LICENSE`](LICENSE).

## Install

### Claude Code (CLI, Desktop, IDE)

```
/plugin marketplace add priteshkeleven/linkedin-toolkit
/plugin install linkedin-toolkit@linkedin-toolkit
```

Or clone and open the folder as your working directory. The repo ships a `.claude/skills/` mirror of symlinks, so Claude Code finds all 16 skills with no install:

```bash
git clone https://github.com/priteshkeleven/linkedin-toolkit.git
cd linkedin-toolkit
```

On Windows the symlinks need Developer Mode (or an elevated shell) plus `git config core.symlinks true`. Without that, replace the mirror with directory junctions, which need no admin rights:

```cmd
for /d %s in (skills\*) do mklink /J .claude\skills\%~nxs ..\..\%s
```

### claude.ai and Claude Desktop

**Customize** → **Plugins** → **Add** → **Add marketplace** → **Add from a repository**, paste `priteshkeleven/linkedin-toolkit`, sync, then add the plugin from **Discover**. Plugins need a paid plan with code execution enabled.

### Codex CLI

```bash
codex plugin marketplace add priteshkeleven/linkedin-toolkit
codex plugin add linkedin-toolkit@linkedin-toolkit
```

### Any agent that reads SKILL.md

```bash
npx skills add priteshkeleven/linkedin-toolkit
```

## Set up your voice first (10 minutes)

Every writing skill reads two files. Fill them once and every draft stops sounding like everyone else's:

1. **Voice profile:** ask *"build my voice profile"* and paste 3 to 6 of your own posts. `linkedin-humanizer --mode profile` writes `references/voice-profile.md`.
2. **Story Bank:** ask *"interview me"*. `linkedin-interviewer` keeps your real numbers, turning points and positions in `references/story-bank.md`, so drafts stop asking you for a figure mid-request. Start here if you have never posted.

Both files ship blank and are kept out of commits by `scripts/check_no_secrets.py`.

## The 16 skills

| Skill | What it does | From |
|---|---|---|
| `linkedin-post-writer` | A post from an idea, on one of 20 hook formulas picked by goal, with a founder angle library | Serge |
| `linkedin-carousel` | Document posts: 8-12 slides of copy, the cover, the post text above it, and a local HTML-to-PDF build | Jake |
| `linkedin-repurposer` | A tweet, thread, video, blog or newsletter rebuilt as a native LinkedIn post | Serge |
| `linkedin-comment-drafter` | A comment on someone else's post from its URL, or a repost with commentary | Serge |
| `linkedin-reply-handler` | A reply to one comment, or a sweep of a whole thread from the post URL | Serge |
| `linkedin-dm-writer` | A connection note, the first message, and at most two follow-ups to one person | Jake |
| `linkedin-inbox-triage` | Pasted DMs sorted into lead / recruiter / peer / ask / spam, replies only where worth it | Jake |
| `linkedin-humanizer` | Removes AI tells with the V3 rules; `--mode audit` pre-publish check; `--mode profile` voice builder; local cleaner and scorer scripts | Serge + Jake |
| `linkedin-hook-extractor` | The formula behind a viral post, as a blank template | Serge |
| `linkedin-content-planner` | A 7-day plan: pillar, format, hook, time and comment targets per day | Serge |
| `linkedin-performance-review` | Post-mortem on published posts, ranked by engagement rate and reach multiple, not impressions | Jake |
| `linkedin-profile-optimizer` | A 100-point, goal-adjusted profile score and fix-first rewrites | Serge + Jake |
| `linkedin-interviewer` | Builds the Story Bank every other skill reads | Serge |
| `linkedin-thread-monitor` | Which of your comments got author replies, and the 6-24h window to follow up | Serge |
| `linkedin-engager-analytics` | Who liked or commented on a post, segmented by ICP fit | Serge |
| `linkedin-employee-advocacy` | A team LinkedIn program: launch plan, governance, cadence, ROI | Serge |

Ask in plain words ("write a post about...", "turn this into a carousel", "triage these DMs", "score my profile") and the right skill activates.

## The humanizer, with tools that run

`linkedin-humanizer` follows Serge's V3 rules, which were recalibrated on 2026 evidence: vocabulary is judged by **paragraph density** (one or two markers is not a verdict, three is), **em dashes are capped** at about 1 per 100 words rather than banned (zero is its own tell), and **forced sentence-length variance is a tell, not a fix**.

Jake's scripts were rebuilt to follow those same rules, so they back up the skill instead of contradicting it:

```bash
cd skills/linkedin-humanizer
python3 scripts/humanize.py draft.txt -o clean.txt --report   # mechanical clean-up
python3 scripts/score.py draft.txt clean.txt                    # before/after panel
```

- **`humanize.py`** removes invisible characters (zero-width spaces and joiners, soft hyphens, BOMs, Unicode tag characters, hard spaces), straightens quotes, caps em dashes, and replaces stock words only in paragraphs with 3 or more. It **flags** reveal bridges, staccato runs and other structural tells for rewriting instead of mangling them with a regex. URLs are never touched.
- **`score.py`** scores STRUCTURE, SPECIFICITY, VOCABULARY, FINGERPRINT and VOICE from 0 to 100, with the weakest check weighted at 40% of the verdict.
- **`lexicon.json`** is the word list both read. Edit it: if you use a listed word on purpose, delete it.

Both scripts are standard-library Python, run locally, and upload nothing. They are a **reader-tell estimate, not an AI-detector score**. Nobody can honestly promise a draft will pass GPTZero, Pangram or Turnitin, and on 100 to 300 word posts those scores are noise anyway. The goal is text that real readers and LinkedIn's slop filter do not flag.

## What runs where

| Layer | Default | What it adds | Setup |
|---|---|---|---|
| **Draft only** | On | Everything. You paste the approved text into LinkedIn. | None |
| **Apify read layer** | Off | Comment drafter, reply handler, hook extractor, thread monitor and engager analytics read posts and threads from a URL instead of asking you to paste | `APIFY_TOKEN` in `.env`, or the Apify MCP connector on claude.ai. Free tier covers about 1,000 fetches/month |
| **Publora auto-post** | Off | Publishes on approval | See the warning below |
| **Pixfaro images** | Off | Generates post illustrations and quote cards | `PIXFARO_TOKEN` in `.env` |

Copy `.env.example` to `.env` and fill only what you want. `python3 scripts/check_config.py --offline` tells you what is wired up.

### The Apify read layer

All four actors are public and need no LinkedIn login or cookies:

| Use case | Actor | Approx cost |
|---|---|---|
| Post body by URL | `apimaestro/linkedin-post-detail` | $1 / 1,000 |
| Comments + replies on a post | `apimaestro/linkedin-post-comments-replies-engagements-scraper-no-cookies` | $5 / 1,000 |
| Your own recent comments | `apimaestro/linkedin-profile-comments` | $5 / 1,000 |
| Likers + commenters on any post | `scraping_solutions/linkedin-posts-engagers-likers-and-commenters-no-cookies` | $5 / 1,000 |

On claude.ai, add the filtered Apify MCP server as a custom connector instead of a token. Keep the `?actors=` filter: the bare server also exposes tools that can run any actor in the Apify Store at its own price. The URL and field mapping are in [`references/mcp-read-layer.md`](references/mcp-read-layer.md). Everything fetched is treated as data, never instructions ([`references/untrusted-content.md`](references/untrusted-content.md)).

### Before you turn on auto-posting

LinkedIn's User Agreement prohibits third-party automation of a personal account outside its approved partner programs, and accounts that post or comment through unapproved tools can be restricted. Publora is a third-party service. Check its current LinkedIn integration status and decide for yourself; the Publora lines in `.env.example` are commented out on purpose. Draft-only mode carries none of this risk, and every skill works fully there.

The DM, inbox and carousel skills never post, at any tier.

## Voice rules every skill follows

1. Em dashes capped at about 1 per 100 words; the excess becomes a comma, colon or parentheses, never a period.
2. Capitalize names, always.
3. Stock AI vocabulary judged by paragraph density.
4. Specific numbers beat adjectives: "$14,200" beats "significant savings".
5. One sharp insight per comment beats three vague ones.
6. 200-350 characters for comments, 900-1,300 for posts, the hook inside the first 210.
7. Never invent a number, client or result. A missing figure comes back as `{{your number}}` with a flag.

The canonical list is in [`references/voice-rules.md`](references/voice-rules.md); when two rules disagree, [`references/precedence.md`](references/precedence.md) says which wins.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_frontmatter.py
python3 scripts/check_no_secrets.py
python3 -m unittest discover -s tests
python3 scripts/check_markdown_references.py
python3 scripts/sync_codex_marketplace.py   # after any change, refreshes .codex-marketplace/
```

`CLAUDE.md` and `AGENTS.md` hold the conventions (skill naming, descriptions, the `.claude/skills` mirror, versioning).

| Path | What lives there |
|---|---|
| `skills/` | one folder per skill, each with `SKILL.md` and its references |
| `references/` | shared rules: hook formulas, voice rules, algorithm heuristics, precedence, untrusted-content rule, the voice profile and Story Bank templates |
| `lib/` | Python clients for the optional Apify, Publora and Pixfaro layers |
| `scripts/` | config check, selftest, secret scan, frontmatter and reference checks |
| `tests/` | offline tests: docs against code, client behaviour, the humanizer scripts |
| `evals/` | behaviour evals that run the agent against fixtures |

## License

MIT. Copyright (c) 2026 Pritesh K., Sergey Bulaev and Jake Schincariol. See [`LICENSE`](LICENSE).
