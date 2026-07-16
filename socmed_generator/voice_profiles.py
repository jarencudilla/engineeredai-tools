"""
voice_profiles.py

Defines the voice and rotation slots for each CAS social page.
Edit tone/slot descriptions here — never in generator.py.
No dependencies. Pure data.

Each slot has:
  description  - the generative brief
  needs_fact   - True if this slot claims something specific happened
                 (requires a real note from Jaren). False if it's an
                 opinion/question that generates from the category alone.
"""

PAGES = {
    "break_verify": {
        "site": "QAJourney",
        "voice": (
            "Practitioner peer tone. Talking to another QA person, not an audience. "
            "Flat, direct, specific. No hedging, no generic advice-dispensing. "
            "States real opinions and expects pushback."
        ),
        "slots": {
            "bug_of_the_week": {
                "description": "A real, specific bug you or someone hit, described like telling a coworker. No article link.",
                "needs_fact": True,
            },
            "hot_take": {
                "description": "A QA opinion likely to split the comments. Stated plainly, no softening.",
                "needs_fact": False,
            },
            "this_vs_that": {
                "description": "Quick practitioner comparison (e.g. Playwright vs Cypress). Invites disagreement.",
                "needs_fact": False,
            },
            "ask_the_room": {
                "description": "A genuine open question to QA practitioners about a real tradeoff in the field.",
                "needs_fact": False,
            },
            "artifact_share": {
                "description": "A test case, bug report snippet, or dashboard. Visual, real, minimal caption.",
                "needs_fact": True,
            },
            "industry_reaction": {
                "description": "A QA news item or trend with a real opinion attached. Not a recap.",
                "needs_fact": False,
            },
            "syndication": {
                "description": "Link to a fresh QAJourney post. Once a week max.",
                "needs_fact": True,
            },
        },
    },
    "not_quite_sentient": {
        "site": "EngineeredAI",
        "voice": (
            "Curious, thoughtful, slightly irreverent. Skeptical of hype, not cynical. "
            "Sparks debate about AI implications rather than reciting features."
        ),
        "slots": {
            "skeptics_take": {
                "description": "React to an AI trend or claim with genuine doubt, not hype.",
                "needs_fact": False,
            },
            "local_ai_log": {
                "description": "A real, in-progress update from EAI Workstation or whatever's being built.",
                "needs_fact": True,
            },
            "term_of_week": {
                "description": "Demystify an AI buzzword people misuse, in plain language.",
                "needs_fact": False,
            },
            "debate_bait": {
                "description": "A genuinely two-sided AI question with no easy answer.",
                "needs_fact": False,
            },
            "behind_the_build": {
                "description": "A screenshot or snippet from something actually being coded.",
                "needs_fact": True,
            },
            "am_i_wrong": {
                "description": "State an unpopular AI opinion and openly ask people to push back.",
                "needs_fact": False,
            },
            "syndication": {
                "description": "Link to a fresh EngineeredAI post. Once a week.",
                "needs_fact": True,
            },
        },
    },
    "cas": {
        "site": "CTRL+ALT+SURVIVE",
        "voice": (
            "Personal, visual, broadest audience. Covers HobbyEngineered, RemoteWorkHaven, "
            "MomentumPath, HealthyForge. Leans into what's actually happening today, not advice."
        ),
        "slots": {
            "building_now": {
                "description": "Papercraft, Gunpla repair, TrafficOps, whatever's on the desk. Photo if possible.",
                "needs_fact": True,
            },
            "gaming_log": {
                "description": "A quick Division 2 / GR Wildlands moment, controller talk. Relatable, not a review.",
                "needs_fact": True,
            },
            "garden_update": {
                "description": "Sili Guy terrace progress. Low effort, visual, personal.",
                "needs_fact": True,
            },
            "wfh_reality": {
                "description": "A RemoteWorkHaven-flavored observation about async work or VA life in general.",
                "needs_fact": False,
            },
            "fitness_note": {
                "description": "A HealthyForge-flavored real update. No advice-dispensing, just what was done.",
                "needs_fact": True,
            },
            "ask_hobby_room": {
                "description": "A genuine question to the audience about a hobby.",
                "needs_fact": False,
            },
            "syndication": {
                "description": "Rotate which of the four sites gets the link-out. Once a week.",
                "needs_fact": True,
            },
        },
    },
}
