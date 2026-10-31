---
name: linkedin-carousel
description: "Build a LinkedIn document post (carousel): 8 to 12 slides of copy, the cover that earns the swipe, the post text that sits above it, and a local HTML-to-PDF build at 1080x1350. Use when the user says carousel, document post, slides for LinkedIn, or has a list-shaped idea with steps or parts. Not for a single-claim idea (use linkedin-post-writer)."
---

# LinkedIn Carousel

Document posts hold attention longer than any other LinkedIn format, because each swipe is an interaction and a scroll past is not. The format rewards one idea broken into steps. It punishes a text post cut into pieces.

Adapted from Jake Schincariol's `li-carousel` (linkedin-agent-skill, MIT).

## When to use it instead of a text post

Use a carousel when the idea has **sequence**: steps, a countdown, a before/after progression, a framework with parts. Use a text post when the idea is one claim. Splitting one claim across eight slides is the most common way carousels fail; if that is what the user has, say so and hand them to `linkedin-post-writer`.

## Before you write

**Voice profile.** If `../../references/voice-profile.md` has `filled: yes`, load it and match the user's voice, handle and brand colour. If it is not filled, mention once that `linkedin-humanizer --mode profile` can learn their voice from a few posts, then use the generic voice rules.

**Story bank.** If `../../references/story-bank.md` has `filled: yes`, take numbers, dates and named examples for the slides from there. Never invent a figure that is not in it; ask, or leave `{{your number}}` and flag it.

## Structure

8 to 12 slides. Under 8 is a text post. Over 12 and completion falls off.

```
1        COVER      the hook, 6 words or fewer, plus one line of promise
2        THE STAKE  why this matters, in one sentence
3-N      ONE IDEA PER SLIDE. A headline of 3-7 words, and at most 25 words under it.
                    If a slide needs a paragraph, it is two slides.
N+1      RECAP      the whole thing as a list, so the screenshot is useful
LAST     CTA        one action: follow, comment on a specific question, or where to find more. One.
```

## Slide copy rules

- **The cover is most of the result.** Six words, big. The rest of the deck cannot save a cover nobody swipes. Pick the angle with `../../references/hook-formulas.md`, the same formulas the post writer uses.
- **Number every slide** (3/10). Completion goes up when people can see the end.
- **No slide is a paragraph.** If it cannot be said in 25 words, split it.
- **The recap slide is the one people screenshot.** Make it standalone.
- **The user's handle on every slide**, small, bottom corner. Screenshots travel without the post.

## Making the PDF

LinkedIn takes a PDF; 1080x1350 (4:5) uses the most feed space. Build it as HTML and print it to PDF locally:

- One `<section>` per slide, `width:1080px; height:1350px; page-break-after:always`, no page margins.
- One accent colour, type no smaller than 28px. People read these on a phone at thumbnail size.
- If the user has a brand guide or design system in this project, use it and do not invent a palette. Otherwise use the brand colour from the voice profile.
- Print with headless Chrome (`--print-to-pdf`) or any HTML-to-PDF tool the user already has. Check the page count equals the slide count before handing it over.

## Output

1. The slide copy as a numbered list the user can read in ten seconds.
2. The **post text** that goes above the document: 2-3 lines, the actual hook in the feed, under 600 characters.
3. Both run through `linkedin-humanizer` before the user sees them.
4. The PDF, built only after the user approves the copy.

The user uploads the PDF to LinkedIn themselves. This skill does not publish.

## Hard rules

Global voice rules: see root `SKILL.md` §Voice rules. Additional skill-specific rules:

- One idea per deck. A deck with two arcs is two decks; say so.
- No invented statistics on a slide, even as an example. Slides get screenshotted without context.
- No outbound link on any slide or in the post text unless the user asks for it.

## Files

- `SKILL.md` — this file
- `../../references/hook-formulas.md` — formulas for the cover line
- `../../references/voice-profile.md` — voice, handle and brand colour
- `../../references/story-bank.md` — numbers and examples for the slides

## Related skills

- `linkedin-post-writer` — when the idea is one claim, not a sequence
- `linkedin-repurposer` — when the source is a blog, thread or video to break into slides
- `linkedin-humanizer` — scrubs the slide copy and post text
- `linkedin-content-planner` — schedules carousel days in the weekly mix
