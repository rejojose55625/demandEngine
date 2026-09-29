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
from pathlib import Path
import sys


class TargetLeakageAudit:
    def __init__(self, df, target_col, train_pct=0.9, output_dir="results/"):
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        self.target = target_col
        self.train_pct = train_pct
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Split data
        split_date = self.df["date"].quantile(train_pct)
        self.train_df = self.df[self.df["date"] < split_date].copy()
        self.test_df = self.df[self.df["date"] >= split_date].copy()

        # Risk Tracking
        self.critical_risks = []
        self.medium_risks = []
        self.safe_features = []
        self.remove_features = []

    def log(self, message):
        print(message)

    def separator(self, char="=", length=70):
        print(char * length)

    # CHECK FOR DATE CONTAMINATION
    def check_date_contamination(self):
        self.log("\n CHECK 1: DATE CONTAMINATION")
        self.separator()

        train_min, train_max = self.train_df["date"].min(), self.train_df["date"].max()
        test_min, test_max = self.test_df["date"].min(), self.test_df["date"].max()

        self.log(
            f"Train: {train_min.date()} -> {train_max.date()} ({len(self.train_df):,} rows)"
        )
        self.log(
            f"Test: {test_min.date()} -> {test_max.date()} ({len(self.test_df):,} rows)"
        )

        if train_max >= test_min:
            self.log("\n ❌️ FAIL: Data Overlap Detected")
            self.log(f"Train max: {train_max.date()}")
            self.log(f"Test Min: {test_min.date()}")
            overlap_days = (train_max - test_min).days
            self.log(f"Overlap: {overlap_days} days")

            self.critical_risks.append(
                {
                    "check": "DATE_CONTAMINATION",
                    "severity": "CRITICAL",
                    "message": f"Date Overlap: {overlap_days} days",
                }
            )
            return False

        else:
            gap_days = (test_min - train_max).days
            self.log("\n✅️ PASS: Clean temporal split")
            self.log(f"Gap: {gap_days} days")
            return True

    def check_outcome_dependent_features(self):
        self.log("\n CHECK 2: Outcome-dependent features")
        self.separator()

        outcome_dependent = ["sales", "sales_qty", "lost_sales"]
        risky = []

        for col in outcome_dependent:
            if col in self.df.columns and col != self.target:
                self.log(f"❌️ Found: {col}")
                self.log(f"-> Depends on target: {self.target}")
                self.log("Action: REMOVE")

                risky.append(col)
                self.remove_features.append(col)

                self.critical_risks.append(
                    {
                        "check": "OUTCOME_DEPENDENT",
                        "feature": col,
                        "severity": "CRITICAL",
                        "message": f"{col} depends on {self.target}",
                    }
                )

        if not risky:
            self.log("✅️ PASS: No outcome-dependent features found")
            return True
        else:
            return False

    def check_future_information(self):
        self.log("\n CHECK 3: Future Information")
        self.separator()

        future_keywords = [
            "tomorrow",
            "next_",
            "future",
            "_forecast",
            "predicted_",
            "ahead",
        ]
        future_features = []

        for col in self.df.columns:
            if any(kw in col.lower() for kw in future_keywords):
                self.log(f"❌️ Found: {col}")
                self.log("-> Contains future information")
                self.log("-> Action: Use lagged/ historical version")

                future_features.append(col)
                self.remove_features.append(col)

                self.critical_risks.append(
                    {
                        "check": "FUTURE_INFORMATION",
                        "feature": col,
                        "severity": "CRITICAL",
                        "message": f"{col} contains future data",
                    }
                )

        if not future_features:
            self.log("✅️ PASS: No future information")
            return True

        else:
            return False

    def check_global_statistics(self):
        self.log("\n CHECK 4: Global Statistics Confirmation")
        self.separator()

        static_candidates = [
            "avg_basket_size",
            "population_density",
            "foot_traffic_index",
        ]
        issues = []

        self.log("Checking if statistics use train-only data...")

        for col in static_candidates:
            if col in self.df.columns:
                # Check if truly static
                train_variation = self.train_df.groupby("store_id")[col].nunique().max()

                if train_variation > 1:
                    self.log(f"\n⚠️ {col}: TIME-VARYING (needs historical calc)")
                    issues.append(col)

                    self.medium_risks.append(
                        {
                            "check": "GLOBAL_STATS",
                            "feature": col,
                            "severity": "MEDIUM",
                            "message": f"{col} is time-varying, use train-only average",
                        }
                    )

        if not issues:
            self.log("✅️ PASS: Static features appear safe")
            return True

        else:
            self.log(f"\n⚠️ {len(issues)} features need train-only recalculation")
            return True

    def check_endogenous_variables(self):
        self.log("\n CHECK 5: Endogenous Variables")
        self.separator()

        endogenous_candidates = {
            "marketing_spend": "Decided before or after demand forecast",
            "is_promo_campaign": "Based on expected campaign",
            "inventory": "Ordered based on demand forecast",
        }

        suspicious = []

        for col in endogenous_candidates:
            if col in self.df.columns:
                corr = self.df[col].corr(self.df[self.target])
                self.log(f"\n{col}")
                self.log(f"Correlation with {self.target}: {corr:.3f}")

                if abs(corr) > 0.3:
                    self.log("⚠️ SUSPICIOUS - Consider using lagged version")

                    suspicious.append(col)

                    self.medium_risks.append(
                        {
                            "check": "ENDOGENOUS",
                            "feature": col,
                            "severity": "MEDIUM",
                            "message": f"Correlation {corr:.3f} - likely endogenous",
                        }
                    )
                else:
                    self.log("✅️ Weak Correlation (likely OK)")

        if not suspicious:
            self.log("\n✅️ PASS: No obvious endogenous variables")
            return True
        else:
            return True

    def check_suspicious_correlations(self):
        self.log("\n CHECK 6: Suspicious Correlations")
        self.separator()

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        correlations = (
            self.df[numeric_cols].corr()[self.target].sort_values(ascending=False)
        )

        suspicious = []
        for col, corr in correlations.items():
            if col != self.target and abs(corr) > 0.5:
                self.log(f"❓️ {col}: {corr:.3f} (investigate)")
                suspicious.append((col, corr))

        if suspicious:
            self.log(f"\n⚠️ Found {len(suspicious)} suspicious correlations")

            for col, corr in suspicious:
                self.medium_risks.append(
                    {
                        "check": "SUSPICIOUS_CORR",
                        "feature": col,
                        "correlation": corr,
                        "severity": "MEDIUM",
                        "message": f"High correlation ({corr:.3f}) - check for leakage",
                    }
                )
            return False
        else:
            self.log("✅️ PASS: No suspicious correlations")
            return True

    def build_safe_features(self):
        self.log("\n Building Safe Feature List")
        self.separator()

        remove_cols = set(["sales", "sales_qty", "lost_sales", "final_price"])
        remove_cols.update(self.remove_features)

        safe = [
            col
            for col in self.df.columns
            if col not in remove_cols and col != self.target
        ]
        self.safe_features = safe
        self.remove_features = list(remove_cols)

        self.log("\n REMOVE ({len(self.remove_features)} features):")
        for feat in sorted(self.remove_features)[:10]:
            self.log(f"* {feat}")
        if len(self.remove_features) > 10:
            self.log(f"... and {len(self.remove_features) - 10} more")

    def generate_report(self):
        self.log("\n\n" + "=" * 70)
        self.log("AUDIT SUMMARY")
        self.log("=" * 70)

        self.log(f"\nDataset: {self.df.shape[0]:,} rows x {self.df.shape[1]} cols")
        self.log(f"Target: {self.target}")
        self.log(
            f"Train/Test Split: {self.train_pct * 100:.0f}% / {(1 - self.train_pct) * 100:.0f}%"
        )

        self.log("\n⚠️ RISKS DETECTED")
        self.log("🔴 CRITICAL RISKS:")
        self.log("🟡 Medium: {len(self.medium_risks)}")

        if self.critical_risks:
            self.log("\n🔴 CRITICAL RISKS:")
            for risk in self.critical_risks:
                self.log(f"* {risk['check']}: {risk['message']}")
            if len(self.medium_risks) > 5:
                self.log(f"... and {len(self.medium_risks) - 5} more")

        self.log("\n" + "=" * 70)
        if len(self.critical_risks) == 0:
            self.log("✅️ ✅️ ✅️ AUDIT PASSED - DATA IS CLEAN ✅️ ✅️ ✅️")
            self.log("\n Action: Safe to proceed to modelling")
            return True
        else:
            self.log("❌️ ❌️ ❌️ AUDIT FAILED - FIX CRITICAL ISSUES ❌️ ❌️ ❌️")

            self.log(
                f"\nAction: Fix {len(self.critical_risks)} critical risk(s) before modelling"
            )
            return False

    def export_results(self):
        self.log("\nExporting Results to {self.output_dir}/")

        safe_df = pd.DataFrame(
            {
                "feature": self.safe_features,
                "status": ["KEEP"] * len(self.safe_features),
            }
        )
        safe_df.to_csv(self.output_dir / "safe_features.csv", index=False)

        self.log(f"✅️ safe_features.csv ({len(safe_df)} features)")

        # Risk report
        risk_df = pd.DataFrame(self.critical_risks + self.medium_risks)
        risk_df.to_csv(self.output_dir / "risk_report.csv", index=False)
        self.log(f"✅️ risk_report.csv ({len(risk_df)} risks)")

    def run(self):
        self.log("=" * 70)
        self.log("TARGET LEAKAGE AUDIT")
        self.log("=" * 70)

        self.check_date_contamination()
        self.check_outcome_dependent_features()
        self.check_future_information()
        self.check_future_information()
        self.check_global_statistics()
        self.check_endogenous_variables()
        self.check_suspicious_correlations()

        self.build_safe_features()

        self.export_results()

        return len(self.critical_risks) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Target Leakage Audit for demand forecasting"
    )
    parser.add_argument(
        "--data", type=str, required=True, help="Path to sales data CSV or Parquet"
    )

    parser.add_argument(
        "--target",
        type=str,
        default="demand",
        help="Target column name (default: demand)",
    )

    parser.add_argument(
        "--train_pct",
        type=float,
        default=0.9,
        help="Train/Test split percentage (default: 0.9)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="results/",
        help="Output directory (default: results/)",
    )

    args = parser.parse_args()

    try:
        if args.data.endswith(".parquet") or args.data.endswith(".pq"):
            df = pd.read_parquet(args.data)
        else:
            df = pd.read_csv(args.data)
        print(f"✅️ Data loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

    except FileNotFoundError:
        print(f"Error: File not found: {args.data}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    audit = TargetLeakageAudit(
        df=df, target_col=args.target, train_pct=args.train_pct, output_dir=args.output
    )

    passed = audit.run()

    print(f"\n{'=' * 70}")
    if passed:
        print("✅️ ✅️ ✅️ AUDIT PASSED ✅️ ✅️ ✅️")
        print(f"Critical risks: {len(audit.critical_risks)}")
        print(f"Medium risks: {len(audit.medium_risks)}")
        sys.exit(0)
    else:
        print("❌️ ❌️ ❌️ AUDIT FAILED ❌️ ❌️ ❌️")
        print(f"Critical risks: {len(audit.critical_risks)}")
        print(f"Medium risks: {len(audit.medium_risks)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
