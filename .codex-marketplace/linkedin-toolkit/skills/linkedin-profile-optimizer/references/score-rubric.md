# Profile score rubric (100 points)

Adapted from Jake Schincariol's `rubric.json` (linkedin-agent-skill, MIT), with
full-marks criteria that change by goal. The goal comes first (Step 1 of the
skill): scoring a job seeker's keyword headline against a services formula
marks a deliberate choice as a fault and produces rewrites the user rejects.

Score every item, show the table, give the total. Be honest: most first-pass
profiles land in the 30s and 40s, and a generous score is useless. Never score
an item you have not been shown; mark it `not shown` and leave it out of the
total, then state the total as `N / (100 - unshown points)`.

| Item | Pts | Full marks: clients | Full marks: job seeking | Full marks: authority |
|---|---|---|---|---|
| Headline | 12 | Who you help and what changes for them, one piece of proof, not the job title. Uses the 220 characters. | Target role title and the 3-5 keywords recruiters search, plus one proof point. Keep existing keywords; only add. | The one topic you want to be known for, plus a proof point (book, newsletter, talk, number). |
| About, first 2 lines | 10 | Name the reader's problem. Visible before "see more" (about 265-275 characters). | Name the role you want and your strongest proof. | State your position or thesis in one line. |
| About, body | 10 | To one reader, second person: their problem, what you do, one number as proof, what to do next. Under 1,400 characters. | Scope, 2-3 outcomes with numbers, what you want next, how to reach you. | The argument behind the thesis, the proof, where to read more. |
| Featured | 8 | Lead magnet or case study with results, best post, contact or calendar link. | Portfolio or work samples, best post, a recommendation or result. | Best content, media or podcast features, newsletter signup. |
| Banner | 6 | One line of positioning, one way to reach you. Not the default gradient or a stock skyline. | Role and specialty in one line. | Topic or publication name plus where to follow. |
| Photo | 6 | Face fills about 60% of the frame, eyes visible, taken in the last two years, background not distracting. | Same. | Same. |
| Current role | 10 | One line of scope, then 2-3 outcome bullets with numbers. Duties are not outcomes. | Same, written in the vocabulary of the target role's job descriptions. | Same, plus the body of work it produced. |
| Experience depth | 8 | Last two roles detailed; anything older than ten years compressed to one line each. | Same; keep older roles that carry target keywords. | Same. |
| Skills | 6 | Top three pinned are the three you want to be hired for, each endorsed. | Top three mirror the target job descriptions. | Top three are the topic. |
| Recommendations | 8 | At least three in the last two years, each naming a specific outcome rather than character. | Same, ideally from managers. | Same, ideally from people the audience knows. |
| Activity | 10 | Posted or commented in the last seven days. An empty feed reads as an abandoned profile. | Same; commenting in the target industry counts. | Posting at least weekly. |
| Contact | 6 | Custom URL (not the default hash), a working email or booking link, the same handle as other platforms. | Custom URL, email, "Open to work" set the way the user wants it (recruiters only or public). | Custom URL, newsletter or site link. |

## Rules that hold for every goal

- Never invent an audience, an offer, a number or a client to raise a score.
  If an item needs a number the user has not given, the rewrite carries
  `{{your number}}` and a flag.
- Do not recommend dated content (a two-year-old post, an old talk) for Featured.
- Re-score after the rewrites and show the delta honestly. If the rewrite gets
  to 82 and not 98, say 82, and say what the remaining points need
  (recommendations, a real banner, posting history), none of which a rewrite
  can create.
