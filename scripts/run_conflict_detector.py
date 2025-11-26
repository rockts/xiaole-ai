#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from conflict_detector import ConflictDetector  # noqa: E402


def main():
    detector = ConflictDetector()
    report = detector.generate_conflict_report()
    print(report)


if __name__ == '__main__':
    main()
