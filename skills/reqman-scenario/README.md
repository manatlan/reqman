# This SKILL (for agentic ia) is under construction.

## Current
It already gives me good result with claude's agent with skills support (in my case gemini-cli (0.28/skill-support), with claude 4.5 sonnet llm ... or using it, as part of a prompt, in a simple exchange with a claude llm).

Its goal is to create a usable scenario (given a swagger + prompt), currently, it focus on :

 - generating a unique simple yaml (with conf and scenario, in one file, using the new "RUN:" mechanism, to separate conf from requests sequences ...)
 - use old tests assertion with "R." prefix (not the python ones)
 - able to generate a old python transformer (not the new ones in "python:" statements)
 - able to save data to reuse later.
 - able to produce/capitalize a sequence of requests (a reuse using "call" statement)

This skill is handmade created !

## Future

 - be able to use foreach/params statements
 - be able to generate python assertions in tests
 - be able to generate new python declarations
 - be able to support an already existing "reqman.conf" (for global conf)

