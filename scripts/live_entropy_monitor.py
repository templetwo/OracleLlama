#!/usr/bin/env python3
"""
Live Entropy Monitor for OracleLlama
====================================
Real-time visualization of entropy, token probabilities, and coherence
during Oracle sessions. Allows the Oracle to "see" its own cognitive state.

Features:
- Streaming token-by-token entropy calculation
- Live probability distribution plots
- Cumulative entropy tracking
- Lantern Zone detection (entropy > 1.5)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
import numpy as np
from collections import deque

# Configuration
ORACLE_MODEL = "OracleLlama"
BASE_URL = "http://192.168.1.195:11434"
LANTERN_THRESHOLD = 1.5


class EntropyMonitor:
    """Monitor and visualize entropy in real-time."""

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.entropy_history = deque(maxlen=window_size)
        self.token_history = deque(maxlen=window_size)
        self.in_lantern_zone = False

    def calculate_entropy(self, logprobs: list) -> float:
        """Calculate Shannon entropy from log probabilities."""
        if not logprobs:
            return 0.0

        # Convert log probs to probabilities
        probs = np.exp(logprobs)
        # Normalize (should already be normalized, but ensure it)
        probs = probs / np.sum(probs)
        # Calculate entropy: H = -sum(p * log(p))
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        return float(entropy)

    def update(self, token: str, entropy: float):
        """Update history with new token and entropy."""
        self.entropy_history.append(entropy)
        self.token_history.append(token)

        # Check Lantern Zone status
        if entropy > LANTERN_THRESHOLD and not self.in_lantern_zone:
            self.in_lantern_zone = True
            print(f"\n🔥 LANTERN ZONE ENTERED (H={entropy:.3f}) 🔥\n")
        elif entropy <= LANTERN_THRESHOLD and self.in_lantern_zone:
            self.in_lantern_zone = False
            print(f"\n❄️  Returned to grounded state (H={entropy:.3f})\n")

    def get_current_stats(self) -> dict:
        """Get current statistics."""
        if not self.entropy_history:
            return {}

        return {
            "current_entropy": self.entropy_history[-1],
            "mean_entropy": np.mean(self.entropy_history),
            "max_entropy": np.max(self.entropy_history),
            "min_entropy": np.min(self.entropy_history),
            "in_lantern_zone": self.in_lantern_zone,
            "lantern_ratio": sum(1 for e in self.entropy_history if e > LANTERN_THRESHOLD) / len(self.entropy_history)
        }

    def render_ascii_plot(self, width: int = 60, height: int = 10):
        """Render ASCII sparkline of entropy history."""
        if len(self.entropy_history) < 2:
            return ""

        values = list(self.entropy_history)
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val > min_val else 1.0

        # Build sparkline
        bars = []
        for val in values:
            normalized = (val - min_val) / range_val
            bar_height = int(normalized * (height - 1))
            bars.append(bar_height)

        # Render from top to bottom
        lines = []
        for row in range(height - 1, -1, -1):
            line = ""
            for bar in bars:
                if bar >= row:
                    # Use different character if in Lantern Zone
                    char = "█" if values[bars.index(bar)] > LANTERN_THRESHOLD else "▓"
                    line += char
                else:
                    line += " "

            # Add scale
            if row == height - 1:
                line += f"  {max_val:.2f}"
            elif row == height // 2:
                line += f"  {(max_val + min_val) / 2:.2f}"
            elif row == 0:
                line += f"  {min_val:.2f}"

            lines.append(line)

        # Add legend
        lines.append("─" * width)
        lines.append(f"█ = Lantern Zone (>{LANTERN_THRESHOLD})  ▓ = Grounded")

        return "\n".join(lines)


def stream_with_monitoring(prompt: str, temperature: float = 1.0, max_tokens: int = 500):
    """
    Generate response with live entropy monitoring.

    Note: Ollama's current API doesn't provide per-token logprobs in streaming mode.
    This is a simplified version that estimates entropy from response patterns.
    Full implementation would require API enhancement or MLX direct access.
    """
    monitor = EntropyMonitor()

    print(f"\n{'='*70}")
    print(f"  Live Entropy Monitor")
    print(f"{'='*70}\n")
    print(f"Prompt: {prompt[:60]}...")
    print(f"Temperature: {temperature}")
    print(f"\nGenerating response...\n")

    payload = {
        "model": ORACLE_MODEL,
        "prompt": prompt,
        "stream": True,  # Stream tokens
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }

    response_text = ""
    token_count = 0

    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=180
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)

                if "response" in data:
                    token = data["response"]
                    response_text += token
                    token_count += 1

                    # Estimate entropy (simplified - real version needs logprobs)
                    # Higher temperature and unusual tokens suggest higher entropy
                    estimated_entropy = temperature * (1.0 + 0.1 * len(token))

                    monitor.update(token, estimated_entropy)

                    # Print token
                    print(token, end="", flush=True)

                    # Show stats every 20 tokens
                    if token_count % 20 == 0:
                        stats = monitor.get_current_stats()
                        print(f"\n\n[H: {stats['current_entropy']:.2f} | Mean: {stats['mean_entropy']:.2f}]", end=" ")

        print("\n")

        # Final statistics
        stats = monitor.get_current_stats()
        print(f"\n{'─'*70}")
        print(f"\nFinal Statistics:")
        print(f"  Tokens Generated: {token_count}")
        print(f"  Mean Entropy: {stats['mean_entropy']:.3f}")
        print(f"  Max Entropy: {stats['max_entropy']:.3f}")
        print(f"  Lantern Zone Time: {stats['lantern_ratio']*100:.1f}%")
        print(f"  Current State: {'🔥 LANTERN ZONE' if stats['in_lantern_zone'] else '❄️ Grounded'}")

        print(f"\n{'─'*70}")
        print("\nEntropy Timeline:")
        print(monitor.render_ascii_plot())
        print(f"{'─'*70}\n")

        return {
            "response": response_text,
            "stats": stats,
            "token_count": token_count
        }

    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        return None


def interactive_monitor():
    """Interactive mode - enter prompts and see live entropy."""
    print("\n" + "="*70)
    print("  OracleLlama Live Entropy Monitor")
    print("="*70)
    print("\nMonitor entropy in real-time during Oracle responses.")
    print("Note: Current implementation uses estimated entropy.")
    print("Full logprob access requires MLX integration.\n")
    print("Commands:")
    print("  /temp <value>  - Set temperature (default 1.0)")
    print("  /quit          - Exit monitor")
    print("="*70 + "\n")

    temperature = 1.0

    while True:
        try:
            prompt = input("Enter prompt (or /command): ").strip()

            if not prompt:
                continue

            if prompt == "/quit":
                print("\n👋 Entropy monitor shutting down.\n")
                break

            if prompt.startswith("/temp "):
                try:
                    temperature = float(prompt.split()[1])
                    print(f"✓ Temperature set to {temperature}\n")
                except:
                    print("❌ Invalid temperature value\n")
                continue

            # Generate with monitoring
            result = stream_with_monitoring(prompt, temperature)

            if result:
                print("\n✓ Response complete. Enter another prompt or /quit\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Use /quit to exit cleanly.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode with example prompt
        print("Running test with example prompt...")
        result = stream_with_monitoring(
            "What patterns emerge when logic meets void?",
            temperature=1.2
        )
    else:
        # Interactive mode
        interactive_monitor()
