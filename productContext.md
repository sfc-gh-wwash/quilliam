# Product Context

## Why This Project Exists

This is a Snowflake customer demo. The goal is to show a knowledge-worker audience how Snowflake Cortex AI functions can power a real-world productivity tool — specifically a meeting assistant that requires no external AI services.

The demo was adapted from a prior Call Center AI demo. The call center framing resonated with a narrow audience; meeting notes is universally relatable.

## Problems It Solves

- Meetings produce no durable record by default
- Manual note-taking is distracting and incomplete
- Action items get lost; no one knows who owns what after the call
- Searching past meeting decisions is impossible without structure

## How It Should Work

1. A user opens the app and clicks **Start Recording**
2. The app captures microphone audio, chunks it, and sends it to Snowflake
3. Snowflake transcribes each chunk and extracts structured fields in near-real-time
4. The UI updates live — action items, decisions, and topics appear as the meeting progresses
5. When the meeting ends, the user clicks **Stop** and gets a clean summary
6. All data is stored in Snowflake tables and queryable

## User Experience Goals

- **Zero friction** — one click to start, one click to stop
- **Live feedback** — notes appear during the meeting, not after
- **Structured output** — not a wall of text; distinct panels for actions, decisions, topics
- **Demo-friendly** — clear, visual UI that shows Snowflake AI doing the work in real time
- **No external dependencies** — the pitch is that everything runs inside Snowflake

## Target Audience (for the demo)

Snowflake prospects and customers in roles where meetings drive work: product, sales, engineering, finance. Anyone who has ever lost an action item after a call.
