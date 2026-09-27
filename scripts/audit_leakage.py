"""
Target leakage Audit - Standalone Script
Automated detection & reporting of data leakage issues

Usage:
    python audit_leakage.py --data data/generated/sales_data.parquet --target demand
    python audit_leakage.py --data data/generated/sales_data.parquet --target demand --train_pct 0.9 --output results/
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetimeimport datetime
import os
from pathlib import Path

class TargetLeakageAudit:
    def __init__(self, df, target_col, train_pct = 0.9, output_dir = 'results/'):
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])

        self.target = target_col
        self.train_pct = train_pct
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok = True)

        # Split data 
        self.date = self.df['date'].quantile(train_pct)
        self.train_df = self.df[self.df['date'] < split_date].copy()
        self.test_df = self.df[self.df['date'] >= split_date].copy()

        # Risk Tracking
        self.critical_risks = []
        self.medium_risks = []
        self.safe_features = []
        self.remove_features = []

    def log(self, message):
        print(message)

    def separator(self, char='=', length = 70):
        print(char * length)


    # CHECK FOR DATE CONTAMINATION
    def check_date_contamination(self):
        self.log("\n CHECK 1: DATE CONTAMINATION")
        self.separator()

        train_min, train_max = self.train_df['date'].min(), self.train_df['date'].max()
        test_min, test_max = self.test_df['date'].min(), self.test_df['date'].max()

        self.log(f"Train: {train_min.date()} -> {train_max.date()} ({len(self.train_df):,} rows)")
        self.log(f"Test: {test_min.date()} -> {test_max.date()} ({len(self.test_df):,} rows)")

        if train_max >= test_min:
            self.log(f"\n ❌️ FAIL: Data Overlap Detected")
            self.log(f"Train max: {train_max.date()}")
            self.log(f"Test Min: {test_min.date()}")
            overlap_days = (train_max - test_min).days
            self.log(f"Overlap: {overlap_days} days")

            self.critical_risks.append({
                'check': 'DATE_CONTAMINATION',
                'severity': 'CRITICAL',
                'message': f"Date Overlap: {overlap_days} days"
            })
            return False

        else:
            gap_days = (test_min - train_max).days
            self.log(f"\n✅️ PASS: Clean temporal split")
            self.log(f"Gap: {gap_days} days")
            return True

