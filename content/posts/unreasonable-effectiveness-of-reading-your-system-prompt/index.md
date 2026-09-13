---
title: "The Unreasonable Effectiveness of Reading Your System Prompt"
date: 2026-08-31T21:00:00+10:00
draft: false
tags: ["llms", "agents"]
description: "I bet you haven't read it."
summary: "A 10k-token system prompt is about 7,500 words, which is half an hour of reading. Nobody does it, and every time I have, I've come away with a cleaner prompt and a bump in evals."
---

I bet you haven't read your system prompt.
Not skimmed it.
Not had it summarised for you.
Actually read it. 
The whole thing. 
Every token. 
As the LLM sees it.
With jinja templating rendered, with AGENTS.md appended, with few-shot examples, with tool schemas. Everything.

Try it. You'll doubtless find dozens of little issues. Poorly explained concepts. Overly verbose language. Redundant information. Inconsistencies between prompt and tool specs.

It's wild when you consider how important the system prompt is, and how little effort it takes to read it, and yet no one *really* knows what's in it.

It really isn't even that hard. Back of the envelope: a pretty big system prompt, with few-shot examples, and a bunch of tools might be 10k tokens. 0.75 words per token means it's about 7.5k words. Reading speed is about 250 words per minute. So half an hour. Half an hour for you to read every single word. That's nothing in the grand scheme of things.

Every time I have done this, I have come away with a much better, cleaner prompt, lower costs and a quality bump. 

Try it out. Get your agent to render your system prompt as it would appear at runtime. And then sit down and read it. All of it.