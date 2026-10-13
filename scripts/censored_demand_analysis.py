"""
CENSORED DEMAND ANALYSIS -> STANDALONE SCRIPT

Analyzes the impact of stockouts on observed demand and identifies high-risk stores

Usage:
    python censored_demand_analysis.py --data sales_data.parquet --output
results/
    python censored_demand_analysis.py --data sales_data.csv --output results/ --verbose
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import datetime
from datetime import datetime


class CensoredDemandAnalysis:
    def __init__(self, df, output_dir="results/", verbose=False):
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.verbose = verbose
        self.results = {}

    def log(self, message):
        """Print message if verbose"""
        if self.verbose:
            print(message)

    def separator(self, char="=", length=70):
        """Print Separator"""
        print(char * length)

    # ANALYSIS
    def analyze_global_censoring(self):
        """Overall censoring problem overview"""
        self.log("\nSTEP 1: Global Censoring Statistics")
        self.separator()

        total_rows = len(self.df)
        censored_rows = self.df["stockout_flag"].sum()
        censored_rate = censored_rows / total_rows if total_rows > 0 else 0

        # Lost sales
        total_lost_sales = self.df["lost_sales"].sum()
        total_actual_sales = self.df["sales_qty"].sum()
        true_demand_sum = self.df["demand"].sum()

        # Estimated lost revenue
        avg_price = self.df["final_price"].mean()
        estimated_lost_revenue = total_lost_sales * avg_price

        self.results["global"] = {
            "total_observations": total_rows,
            "censored_observations": int(censored_rows),
            "censoring_rate": float(censored_rate),
            "uncensored_observations": int(total_rows - censored_rows),
            "uncensoring_rate": float(1 - censored_rate),
            "total_lost_sales_units": int(total_lost_sales),
            "total_actual_sales_units": int(total_actual_sales),
            "true_demand_units": int(true_demand_sum),
            "lost_as_pct_of_demand": float(total_lost_sales / true_demand_sum * 100)
            if true_demand_sum > 0
            else 0,
            "avg_unit_price": float(avg_price),
            "estimated_lost_revenue": float(estimated_lost_revenue),
        }

        return self.results["global"]

    # STORE LEVEl CENSORING
    def analyze_store_censoring(self):
        """Store-level censoring analysis"""
        self.log("\n STEP 2: Store-level censoring")
        self.separator()

        store_censoring = (
            self.df.groupby("store_id")
            .agg(
                {
                    "store": "first",
                    "city": "first",
                    "region": "first",
                    "stockout_flag": ["sum", "mean"],
                    "lost_sales": "sum",
                    "sales_qty": "sum",
                    "demand": "sum",
                    "final_price": "mean",
                    "date": "count",
                }
            )
            .reset_index(drop=True)
        )

        store_censoring.columns = [
            "store",
            "city",
            "region",
            "stockouts_count",
            "censoring_rate",
            "lost_sales_units",
            "actual_sales_units",
            "true_demand_units",
            "avg_price",
            "total_records",
        ]

        # Calculate lost revenue
        store_censoring["estimated_lost_revenue"] = (
            store_censoring["lost_sales_units"] * store_censoring["avg_price"]
        )

        # Sort
        store_censoring.sort_values("censoring_rate", ascending=False, inplace=True)

        self.log(f"Total stores: {len(store_censoring)}")
        self.log(
            f"Stores with > 10% censoring: {(store_censoring['censoring_rate'] > 0.1).sum()}"
        )
        self.log(
            f"Stores with > 20% censoring: {(store_censoring['censoring_rate'] > 0.2).sum()}"
        )

        # Save
        store_censoring.to_csv(
            self.output_dir / "store_censoring_analysis.csv", index=False
        )

        self.results["store_censoring"] = store_censoring

        return store_censoring

    # CATEGORY LEVEL CENSORING
    def analyze_category_censoring(self):
        """Category-level censoring analysis"""
        self.log("\nSTEP 3: Category-level censoring")
        self.separator()

        category_censoring = (
            self.df.groupby("category")
            .agg(
                {
                    "stockout_flag": ["sum", "mean"],
                    "lost_sales": "sum",
                    "sales_qty": "sum",
                    "demand": "sum",
                    "final_price": "mean",
                }
            )
            .reset_index()
        )

        category_censoring.columns = [
            "category",
            "stockouts_count",
            "censoring_rate",
            "lost_sales_units",
            "actual_sales_units",
            "true_demand_units",
            "avg_price",
        ]

        # Lost revenue
        category_censoring["estimated_lost_revenue"] = (
            category_censoring["lost_sales_units"] * category_censoring["avg_price"]
        )
        category_censoring.sort_values("censoring_rate", ascending=False, inplace=True)

        self.log("\nCensoring by category:")
        for idx, row in category_censoring.iterrows():
            self.log(
                f"{row['category']} : {row['censoring_rate'] * 100:.2f}% | Lost: Rs.{row['estimated_lost_revenue']:,.0f}"
            )

        # Save
        category_censoring.to_csv(
            self.output_dir / "category_censoring_analysis.csv", index=False
        )
        self.results["category_censoring"] = category_censoring

        return category_censoring

    # ANALYSIS 4: REGION-LEVEL CENSORING
    def analyze_region_censoring(self):
        """Region level censoring analysis"""
        self.log("\n STEP 4: Region-level censoring")
        self.separator()

        region_censoring = (
            self.df.groupby("region")
            .agg(
                {
                    "stockout_flag": ["sum", "mean"],
                    "lost_sales": "sum",
                    "sales_qty": "sum",
                    "demand": "sum",
                    "final_price": "mean",
                }
            )
            .reset_index()
        )

        region_censoring.columns = [
            "region",
            "stockouts_count",
            "censoring_rate",
            "lost_sales_units",
            "actual_sales_units",
            "true_demand_units",
            "avg_price",
        ]

        region_censoring["estimated_lost_revenue"] = (
            region_censoring["lost_sales_units"] * region_censoring["avg_price"]
        )

        region_censoring.sort_values(by="censoring_rate", ascending=False, inplace=True)

        self.log("\nCensoring by Region:")
        for idx, row in region_censoring.iterrows():
            self.log(
                f" {row['region']} : {row['censoring_rate'] * 100:.2f} % | Lost: Rs.{row['estimated_lost_revenue']:,.0f}"
            )

        # Save
        region_censoring.to_csv(
            self.output_dir / "region_censoring_analysis.csv", index=False
        )
        self.results["region_censoring"] = region_censoring

        return region_censoring

    # ANALYSIS 5: HIGH RISK COMBINATIONS
    def analyze_high_risk_combinations(self):
        """Identify high risk store & category combinations"""
        self.log("\n STEP 5: High-Risk Store x Category Combinations")
        self.separator()

        store_cat = (
            self.df.groupby(["store_id", "store", "city", "category"])
            .agg(
                {
                    "stockout_flag": ["sum", "mean"],
                    "lost_sales": "sum",
                    "sales_qty": "sum",
                    "final_price": "mean",
                }
            )
            .reset_index()
        )

        store_cat.columns = [
            "store_id",
            "store",
            "city",
            "category",
            "stockouts_count",
            "censoring_rate",
            "lost_sales_units",
            "actual_sales_units",
            "avg_price",
        ]

        store_cat["estimated_lost_revenue"] = (
            store_cat["lost_sales_units"] * store_cat["avg_price"]
        )

        # Filter high risk
        high_risk = store_cat[
            (store_cat["censoring_rate"] > 0.15) | (store_cat["lost_sales_units"] > 100)
        ].sort_values("estimated_lost_revenue", ascending=False)

        self.log(f"High risk combinations: {len(high_risk)}")

        self.log("Top 10:")
        for idx, row in high_risk.head(10).iterrows():
            self.log(
                f"{row['store']} - {row['category']} : {row['censoring_rate'] * 100:.1f}% censoring"
            )

        # Save
        high_risk.to_csv(self.output_dir / "high_risk_combinations.csv", index=False)

        self.results["high_risk"] = high_risk

        return high_risk

    # ANALYSIS 6: TIME-SERIES TRENDS
    def analyze_censoring_trends(self):
        """Analyze censoring trends over time"""
        self.log("\n STEP 6: Censoring trends over time")
        self.separator()

        self.df["year_month"] = self.df["date"].dt.to_period("M")

        monthly = (
            self.df.groupby("year_month")
            .agg(
                {
                    "stockout_flag": "mean",
                    "lost_sales": "sum",
                    "sales_qty": "sum",
                    "demand": "sum",
                }
            )
            .reset_index()
        )

        monthly["year_month"] = monthly["year_month"].astype(str)

        # Trend analysis
        if len(monthly) > 1:
            early_rate = (
                monthly["stockout_flag"].iloc[: max(1, len(monthly) // 3)].mean()
            )
            late_rate = monthly["stockout_flag"].iloc[-max(1, len(monthly) // 3)].mean()
            trend = " INCREASING" if late_rate > early_rate else "DECREASING"

            self.log(f"Early period censoring: {early_rate * 100:.2f}%")
            self.log("Recent period censoring: {late_rate*100:.2f}%")
            self.log(f"Trend: {trend}")

        # Save
        monthly.to_csv(self.output_dir / "monthly_censoring_trend.csv", index=False)

        self.results["trends"] = monthly

        return monthly

    # GENERATE RECOMMENDATIONS
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        self.log("\nRECOMMENDATIONS:")
        self.separator()

        global_stats = self.results["global"]
        store_stats = self.results["store_censoring"]
        category_stats = self.results["category_censoring"]
        high_risk = self.results["high_risk"]

        recommendations = []

        # 1. Inventory planning
        if global_stats["censoring_rate"] > 0.10:
            recommendations.append(
                {
                    "priority": 1,
                    "area": "Inventory Planning",
                    "action": "Increase reorder points by 20-30% for high risk stores",
                    "rationale": f"Current censoring rate {global_stats['censoring_rate'] * 100:.1f}% is above acceptable threshold",
                }
            )

        # 2. Top stores to fix
        top_5_stores = store_stats.head(5)
        for idx, row in top_5_stores.iterrows():
            recommendations.append(
                {
                    "priority": 2,
                    "area": "Specific Store Action",
                    "action": f"Fix {row['store']} ({row['city']}) : Increase inventory",
                    "rationale": f"Censoring rate {row['censoring_rate'] * 100:.1f} | Lost revenue: Rs.{row['estimated_lost_revenue']:,.0f}",
                }
            )

        # 3. Category Specific
        for idx, row in category_stats.iterrows():
            if row["censoring_rate"] > 0.05:
                recommendations.append(
                    {
                        "priority": 3,
                        "area": f"Increase {row['category']} stock allocation by 25%",
                        "rationale": f"Censoring {row['censoring_rate'] > 100:.1f}%",
                    }
                )

        # 4. Demand Forecasting
        recommendations.append(
            {
                "priority": 1,
                "area": "Demand Forecasting",
                "action": 'Use "demand" column (not "sales_qty") as target in model',
                "rationale": f"Sales qty is censored: using it would underestimate demand by {global_stats['lost_as_pct_of_demand']:.1f}%",
            }
        )

        # 5. Financial Opportunity
        recommendations.append(
            {
                "priority": 1,
                "area": "Financial Opportunity",
                "action": f"Reduce censoring by 50% to unlock Rs.{global_stats['estimated_lost_revenue'] * 0.5:,.0f} revenue",
                "rationale": f"Current lost revenue: Rs.{global_stats['estimated_lost_revenue']:,.0f}",
            }
        )

        rec_df = pd.DataFrame(recommendations)
        rec_df.to_csv(self.output_dir / "recommendations.csv", index=False)

        self.log("\nTop priority Actions:")
        for rec in recommendations[:5]:
            self.log(f" [{rec['priority']}] {rec['action']}")
            self.log(f"     -> {rec['rationale']}")

        return rec_df

    # EXPORT SUMMARY
    def export_summary(self):
        """Export overall summary"""
        self.log("\n Exporting Summary")
        self.separator()

        summary = {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_observations": self.results["global"]["total_observations"],
            "censored_observations": self.results["global"]["censored_observations"],
            "global_censoring_rate": f"{self.results['global']['censoring_rate'] * 100:.2f}%",
            "total_lost_sales_units": self.results["global"]["total_lost_sales_units"],
            "estimated_lost_revenue": f"Rs.{self.results['global']['estimated_lost_revenue']:,.0f}",
            "high_risk_combinations": len(self.results["high_risk"]),
            "stores_with_high_censoring": (
                self.results["store_censoring"]["censoring_rate"] > 0.15
            ).sum(),
        }

        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(self.output_dir / "censoring_summary.csv", index=False)

        self.log("\nExported Files")
        self.log("✅️ censoring_summary.csv")
        self.log("✅️ store_censoring_analysis.csv")
        self.log("✅️ category_censoring_analysis.csv")
        self.log("✅️ region_censoring_analysis.csv")
        self.log("✅️ high_risk_combinations.csv")
        self.log("✅️ monthly_censoring_trend.csv")
        self.log("✅️ recommendations.csv")

        self.log(f"\nOutput directory: {self.output_dir}/")

    # RUN FULL ANALYSIS
    def run(self):
        """Run full analysis"""
        print("=" * 70)
        print("CENSORED DEMAND ANALYSIS")
        print("=" * 70)

        self.analyze_global_censoring()
        self.analyze_store_censoring()
        self.analyze_category_censoring()
        self.analyze_region_censoring()
        self.analyze_high_risk_combinations()
        self.analyze_censoring_trends()
        self.export_summary()

        print("\n")
        self.separator()
        print("ANALYSIS COMPLETE")
        self.separator()

        print(
            f"\nGlobal Censoring Rate: {self.results['global']['censoring_rate'] * 100:.2f}%"
        )
        print(
            f"Estimatd Lost Revenue: Rs.{self.results['global']['estimated_lost_revenue']:,.0f}"
        )
        print(f"High Risk Combinations: {len(self.results['high_risk'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Censored Demand Analysis for retail forecasting"
    )
    parser.add_argument(
        "--data", type=str, required=True, help="Path to sales data (CSV or Parquet"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/",
        help="Output directory (default = results/)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed progress messages"
    )

    args = parser.parse_args()

    try:
        if args.data.endswith(".parquet") or args.data.endswith(".pq"):
            df = pd.read_parquet(args.data)
        else:
            df = pd.read_csv(args.data)

        print(f"✅️ Data Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

    except FileNotFoundError:
        print(f"❌️ File not found: {args.data}")
        sys.exit(1)
    except Exception as e:
        print(f"❌️ Error loading data: {e}")
        sys.exit(1)

    # Run analysis
    analysis = CensoredDemandAnalysis(df, output_dir=args.output, verbose=args.verbose)
    analysis.run()

    print("\n Next Steps:")
    print("     1. Review results/ directory for detailed reports")
    print("     2. Check recommendations.csv for action items")
    print("     3. Use high_risk_combinations.csv to prioritize fixes")
    print("     4. In demand model: use 'demand' column, not 'sales_qty'")


if __name__ == "__main__":
    main()
