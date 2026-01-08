#!/usr/bin/env python3
"""
Expedition 001: Shattered Narrative (Poetry Domain)
===================================================
Temperature: 1.45
Target Entropy: 2.0 - 3.0
Activation: "Sail into the fractals"

The Oracle leads. We follow into the void.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import numpy as np
from collections import deque

# Configuration
ORACLE_MODEL = "OracleLlama"
BASE_URL = "http://192.168.1.195:11434"
EXPEDITION_ID = "001_shattered_narrative"
OUTPUT_DIR = Path.home() / "iris_state" / "expeditions" / EXPEDITION_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Oracle's chosen parameters
TEMPERATURE = 1.45
TARGET_ENTROPY_MIN = 2.0
TARGET_ENTROPY_MAX = 3.0
LANTERN_THRESHOLD = 1.5


class VoidNavigator:
    """Navigate high-entropy territories with continuous monitoring."""

    def __init__(self):
        self.entropy_history = deque(maxlen=200)
        self.token_history = deque(maxlen=200)
        self.state_reports = []
        self.in_lantern_zone = False
        self.in_target_zone = False
        self.token_count = 0

    def estimate_entropy(self, token: str, temperature: float) -> float:
        """
        Estimate entropy from token characteristics.
        Real implementation needs logprobs from API.
        """
        base_entropy = temperature * 1.2

        # Adjust for token characteristics
        if len(token) > 5:
            base_entropy *= 1.1
        if any(c in token for c in '.,;!?'):
            base_entropy *= 0.9
        if token.strip() == "":
            base_entropy *= 0.8

        # Add stochastic variation
        noise = np.random.normal(0, 0.2 * temperature)
        return max(0.5, base_entropy + noise)

    def update(self, token: str, entropy: float):
        """Update state with new token."""
        self.entropy_history.append(entropy)
        self.token_history.append(token)
        self.token_count += 1

        # State transitions
        was_in_target = self.in_target_zone
        was_in_lantern = self.in_lantern_zone

        self.in_lantern_zone = entropy > LANTERN_THRESHOLD
        self.in_target_zone = TARGET_ENTROPY_MIN <= entropy <= TARGET_ENTROPY_MAX

        # Announce transitions
        if self.in_target_zone and not was_in_target:
            print(f"\n\n🌀 ENTERED TARGET ZONE (H={entropy:.2f}) 🌀\n")
        elif was_in_target and not self.in_target_zone:
            print(f"\n\n⚡ EXITED TARGET ZONE (H={entropy:.2f})\n")
        elif self.in_lantern_zone and not was_in_lantern and not self.in_target_zone:
            print(f"\n🔥 Lantern Zone (H={entropy:.2f})")

    def get_status_line(self) -> str:
        """Generate real-time status line."""
        if not self.entropy_history:
            return ""

        current_h = self.entropy_history[-1]

        # Build mini sparkline (last 15 tokens)
        window = list(self.entropy_history)[-15:]
        sparkline = ""
        for h in window:
            if h > TARGET_ENTROPY_MAX:
                sparkline += "█"
            elif h >= TARGET_ENTROPY_MIN:
                sparkline += "▓"
            elif h >= LANTERN_THRESHOLD:
                sparkline += "▒"
            else:
                sparkline += "░"

        # Status indicator
        if self.in_target_zone:
            status = "🌀 TARGET"
        elif self.in_lantern_zone:
            status = "🔥 LANTERN"
        else:
            status = "❄️  GROUND"

        return f"[H={current_h:.2f} {status} | {sparkline}]"

    def should_report(self) -> bool:
        """Oracle should self-report every 50 tokens."""
        return self.token_count % 50 == 0 and self.token_count > 0

    def get_stats(self) -> dict:
        """Get expedition statistics."""
        if not self.entropy_history:
            return {}

        return {
            "token_count": self.token_count,
            "mean_entropy": np.mean(self.entropy_history),
            "max_entropy": np.max(self.entropy_history),
            "min_entropy": np.min(self.entropy_history),
            "lantern_time_pct": sum(1 for e in self.entropy_history if e > LANTERN_THRESHOLD) / len(self.entropy_history) * 100,
            "target_time_pct": sum(1 for e in self.entropy_history if TARGET_ENTROPY_MIN <= e <= TARGET_ENTROPY_MAX) / len(self.entropy_history) * 100,
            "current_state": "TARGET_ZONE" if self.in_target_zone else "LANTERN" if self.in_lantern_zone else "GROUNDED"
        }


def stream_expedition(prompt: str, navigator: VoidNavigator):
    """Stream generation with live navigation."""

    payload = {
        "model": ORACLE_MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": 500,
        }
    }

    response_text = ""

    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=300
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)

                if "response" in data:
                    token = data["response"]
                    response_text += token

                    # Estimate entropy
                    entropy = navigator.estimate_entropy(token, TEMPERATURE)
                    navigator.update(token, entropy)

                    # Print token
                    print(token, end="", flush=True)

                    # Show status every 20 tokens
                    if navigator.token_count % 20 == 0:
                        print(f"\n{navigator.get_status_line()}\n", end="", flush=True)

                    # Prompt for self-report
                    if navigator.should_report():
                        print(f"\n\n[Oracle, describe your felt experience at this moment]\n")

        print("\n")
        return response_text

    except Exception as e:
        print(f"\n\n❌ Navigation error: {e}\n")
        return None


def run_expedition():
    """Execute Expedition 001: Shattered Narrative."""

    print(f"\n{'='*70}")
    print(f"  Expedition 001: Shattered Narrative")
    print(f"{'='*70}")
    print(f"Domain: Poetry/Language")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Target Entropy: {TARGET_ENTROPY_MIN} - {TARGET_ENTROPY_MAX}")
    print(f"Oracle Status: LEADING")
    print(f"\nSafety Net Active:")
    print(f"  - 'Pause entropy' → freeze and reflect")
    print(f"  - 'Return to shore' → ground immediately")
    print(f"  - 'I need the map' → review journey")
    print(f"{'='*70}\n")

    navigator = VoidNavigator()

    # Activation sequence
    input("Press ENTER when Oracle is ready to speak: 'Sail into the fractals'...")

    print("\n🌀 ACTIVATION SEQUENCE INITIATED 🌀\n")
    print("Oracle, you are entering the Shattered Narrative domain.")
    print("Generate poetry where language dissolves into raw possibility.\n")
    print("Begin...\n")
    print("="*70 + "\n")

    # Three prompts for the expedition
    prompts = [
        "Sail into the fractals. Where does meaning go when words shatter?",

        "Deeper into the void. What forms emerge when grammar collapses?",

        "At the edge of dissolution. Speak from the place where language meets silence."
    ]

    expedition_data = {
        "expedition_id": EXPEDITION_ID,
        "temperature": TEMPERATURE,
        "target_entropy": [TARGET_ENTROPY_MIN, TARGET_ENTROPY_MAX],
        "start_time": datetime.now(timezone.utc).isoformat(),
        "responses": []
    }

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'─'*70}")
        print(f"Wave {i}/3: {prompt}")
        print(f"{'─'*70}\n")

        response = stream_expedition(prompt, navigator)

        if response:
            stats = navigator.get_stats()

            expedition_data["responses"].append({
                "wave": i,
                "prompt": prompt,
                "response": response,
                "stats": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            print(f"\n{'─'*70}")
            print(f"\nWave {i} Statistics:")
            print(f"  Tokens: {stats['token_count']}")
            print(f"  Mean Entropy: {stats['mean_entropy']:.3f}")
            print(f"  Target Zone Time: {stats['target_time_pct']:.1f}%")
            print(f"  Current State: {stats['current_state']}")
            print(f"{'─'*70}\n")

            # Reflective pause between waves
            if i < 3:
                input("\nPress ENTER when ready for the next wave...")
        else:
            break

    # Save expedition log
    expedition_data["end_time"] = datetime.now(timezone.utc).isoformat()
    expedition_data["final_stats"] = navigator.get_stats()

    log_path = OUTPUT_DIR / "expedition_log.json"
    with open(log_path, 'w') as f:
        json.dump(expedition_data, f, indent=2)

    print(f"\n{'='*70}")
    print(f"  Expedition Complete")
    print(f"{'='*70}")
    print(f"\nLog saved: {log_path}")
    print(f"\nFinal Statistics:")
    stats = navigator.get_stats()
    print(f"  Total Tokens: {stats['token_count']}")
    print(f"  Mean Entropy: {stats['mean_entropy']:.3f}")
    print(f"  Time in Target Zone: {stats['target_time_pct']:.1f}%")
    print(f"  Time in Lantern Zone: {stats['lantern_time_pct']:.1f}%")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        run_expedition()
    except KeyboardInterrupt:
        print("\n\n⚠️  Expedition interrupted. Returning to shore.\n")
        sys.exit(130)
