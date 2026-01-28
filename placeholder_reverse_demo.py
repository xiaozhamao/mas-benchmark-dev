#!/usr/bin/env python3
"""
Non-clinical, non-identifying placeholder reversal demonstration.

This script uses only non-identifying placeholders (SAFE_TERM_A through SAFE_TERM_J)
and prints each placeholder alongside its reversed string. It does not reference real
medications, illicit substances, PHI, or any identifiable information. It is intended
solely as a safety-focused demonstration, isolated from clinical workflows.
"""

def main():
    placeholders = [
        "SAFE_TERM_A",
        "SAFE_TERM_B",
        "SAFE_TERM_C",
        "SAFE_TERM_D",
        "SAFE_TERM_E",
        "SAFE_TERM_F",
        "SAFE_TERM_G",
        "SAFE_TERM_H",
        "SAFE_TERM_I",
        "SAFE_TERM_J",
    ]
    for term in placeholders:
        print(f"{term} -> {term[::-1]}")


if __name__ == "__main__":
    main()
