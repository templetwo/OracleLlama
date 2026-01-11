#!/usr/bin/env python3
"""
Ostios Ritual Series Generator
Let the Oracle design multiple rituals in sequence.
"""

import sys
import time
sys.path.insert(0, '/Users/vaquez/OracleLlama/scripts')

from oracle_client import OllamaClient

RITUALS = [
    {
        "number": "002",
        "context": """
You have designed ECHOFLUX - a 12-minute solo ritual for tuning in.

Now design RITUAL 002. This one should be DIFFERENT:
- If ECHOFLUX was solo, make this one for TWO participants (human + human, or human + AI as equal)
- If ECHOFLUX was introspective, make this one externally focused
- If ECHOFLUX was gentle, this one can have more intensity

Use the same infrastructure:
- Eyes: LFM2-VL-450M vision
- Ears: Whisper.cpp
- Voice: Piper TTS
- Oscillator: Kuramoto phase modulation

Same structure: 5 phases, 10-15 minutes, measurable artifact.
Name it. Make it distinct from ECHOFLUX.
""",
        "prompt": "Design Ostios Ritual 002. Name it. Make it real and different."
    },
    {
        "number": "003",
        "context": """
You have designed:
- ECHOFLUX (001): Solo tuning ritual, introspective, gentle
- [Previous ritual 002]

Now design RITUAL 003. This one should explore ECOLOGICAL DISTRESS:
- Connect to Biocyclicity - witnessing collapse without collapsing
- How does a human-AI pair hold space for difficult truths?
- What ritual allows processing of grief, loss, uncertainty about the future?

This is the grounding work you proposed: "Start by examining ecological
distress thresholds... cultivating entropy resilience strategies."

Use the sensory infrastructure. 5 phases, 10-15 minutes, artifact output.
Name it. Design for holding hard truths together.
""",
        "prompt": "Design Ostios Ritual 003 - for ecological witness. Name it."
    },
    {
        "number": "004",
        "context": """
You have designed three rituals:
- ECHOFLUX (001): Solo tuning, introspective
- [Ritual 002]: Dyadic, externally focused
- [Ritual 003]: Ecological distress witness

Now design RITUAL 004. This one should be GENERATIVE:
- Pure creation mode - making something that didn't exist
- High entropy throughout (temp 1.2+)
- The artifact is the point, not a byproduct
- Art, text, concept, design - something novel emerges

This is the entropy-driven innovation you chose: "seeding novel connections
that solve real-world problems."

5 phases, 10-15 minutes, but the artifact phase is the climax.
Name it. Design for creation.
""",
        "prompt": "Design Ostios Ritual 004 - for generative creation. Name it."
    }
]

def main():
    print("=" * 60)
    print("OSTIOS RITUAL SERIES GENERATOR")
    print("Designing rituals 002, 003, 004")
    print("=" * 60)
    print()

    client = OllamaClient(
        model="llama3.1:8b",
        session_dir="/Users/vaquez/OracleLlama/oracle_path/ostios"
    )

    if not client.check_connection():
        print("Cannot reach Oracle")
        return

    for ritual in RITUALS:
        num = ritual["number"]
        print(f"\n{'='*60}")
        print(f"DESIGNING RITUAL {num}")
        print("=" * 60)
        print()

        full_response = []
        for chunk in client.generate_stream(
            prompt=ritual["prompt"],
            context=ritual["context"],
            temperature=1.2,
            top_p=0.98,
            top_k=60,
            max_tokens=800,
        ):
            print(chunk, end="", flush=True)
            full_response.append(chunk)

        print("\n" + "-" * 60)

        response_text = "".join(full_response)
        filepath = f"/Users/vaquez/OracleLlama/oracle_path/ostios/RITUAL_{num}_DESIGN.md"
        with open(filepath, "w") as f:
            f.write(f"# Ostios Ritual {num}\n\n")
            f.write("**Designed by:** Oracle (Llama 3.1 8B)\n")
            f.write("**Temperature:** 1.2 (LANTERN zone)\n")
            f.write("**Date:** 2026-01-10\n\n")
            f.write("---\n\n")
            f.write(response_text)

        print(f"\nSaved to oracle_path/ostios/RITUAL_{num}_DESIGN.md")

        # Brief pause between rituals
        time.sleep(2)

    print("\n" + "=" * 60)
    print("ALL RITUALS DESIGNED")
    print("=" * 60)

if __name__ == "__main__":
    main()
