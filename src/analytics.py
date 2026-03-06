import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from src.config import VIDEOS_CSV, REVIEWERS, OUTPUT_DIR
import logging

logger = logging.getLogger(__name__)

REPORT_PATH = OUTPUT_DIR / "report.html"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(VIDEOS_CSV, delimiter=";")
    reviewer_cols = [r["score_column"] for r in REVIEWERS]
    df["average_score"] = df[reviewer_cols].mean(axis=1)
    df["score_variance"] = df[reviewer_cols].var(axis=1)
    df["rank"] = range(1, len(df) + 1)
    return df


def terminal_report(df: pd.DataFrame) -> None:
    reviewer_cols = [r["score_column"] for r in REVIEWERS]
    reviewer_names = [r["name"] for r in REVIEWERS]

    print(f"\n{'='*50}")
    print(f"  Analytics Report")
    print(f"{'='*50}\n")

    # Reviewer generosity
    print("  Reviewer averages:")
    for name, col in zip(reviewer_names, reviewer_cols):
        print(f"    {name:<12} {df[col].mean():.2f}")

    # Most generous / harshest
    avgs = {name: df[col].mean() for name, col in zip(reviewer_names, reviewer_cols)}
    print(f"\n  Most generous: {max(avgs, key=avgs.get)}")
    print(f"  Harshest:      {min(avgs, key=avgs.get)}")

    # Score correlation
    print(f"\n  Score correlations:")
    for i in range(len(reviewer_cols)):
        for j in range(i + 1, len(reviewer_cols)):
            corr = df[reviewer_cols[i]].corr(df[reviewer_cols[j]])
            print(f"    {reviewer_names[i]} & {reviewer_names[j]}: {corr:.2f}")

    # Most controversial
    most_controversial = df.nlargest(5, "score_variance")
    print(f"\n  Most controversial entries:")
    for _, row in most_controversial.iterrows():
        scores = " / ".join([str(row[c]) for c in reviewer_cols])
        print(f"    [{int(row['rank'])}] {row['anime_name']} - {row['song_name']} ({scores})")

    # Most agreed upon
    most_agreed = df.nsmallest(5, "score_variance")
    print(f"\n  Most agreed upon entries:")
    for _, row in most_agreed.iterrows():
        scores = " / ".join([str(row[c]) for c in reviewer_cols])
        print(f"    [{int(row['rank'])}] {row['anime_name']} - {row['song_name']} ({scores})")

    # Perfect 10s
    print(f"\n  Perfect 10s:")
    for name, col in zip(reviewer_names, reviewer_cols):
        count = (df[col] == 10.0).sum()
        print(f"    {name:<12} {count}")

    # Top franchises by average score
    franchise_avg = df.groupby("anime_name")["average_score"].mean().nlargest(10)
    print(f"\n  Top 10 franchises by average score:")
    for franchise, score in franchise_avg.items():
        print(f"    {franchise:<40} {score:.2f}")

    # Top franchises by entry count
    franchise_count = df["anime_name"].value_counts().head(10)
    print(f"\n  Top 10 franchises by entry count:")
    for franchise, count in franchise_count.items():
        print(f"    {franchise:<40} {count}")

    print(f"\n{'='*50}\n")


def html_report(df: pd.DataFrame) -> None:
    reviewer_cols = [r["score_column"] for r in REVIEWERS]
    reviewer_names = [r["name"] for r in REVIEWERS]

    avgs = {name: df[col].mean() for name, col in zip(reviewer_names, reviewer_cols)}
    most_generous = max(avgs, key=avgs.get)
    harshest = min(avgs, key=avgs.get)
    most_controversial = df.nlargest(1, "score_variance").iloc[0]
    most_agreed = df.nsmallest(1, "score_variance").iloc[0]
    franchise_avg = df.groupby("anime_name")["average_score"].mean()
    top_franchise = franchise_avg.idxmax()
    corr_matrix = df[reviewer_cols].corr()
    corr_pairs = []
    for i in range(len(reviewer_cols)):
        for j in range(i + 1, len(reviewer_cols)):
            corr_pairs.append((reviewer_names[i], reviewer_names[j], corr_matrix.iloc[i, j]))
    most_correlated = max(corr_pairs, key=lambda x: x[2])
    least_correlated = min(corr_pairs, key=lambda x: x[2])

    # Score inflation
    df_alpha = df.sort_values(["anime_name", "song_name"]).reset_index(drop=True)
    mid = len(df_alpha) // 2
    first_half_avg = df_alpha.iloc[:mid]["average_score"].mean()
    second_half_avg = df_alpha.iloc[mid:]["average_score"].mean()
    diff = second_half_avg - first_half_avg
    inflation_verdict = (
        f"Average score in the first half (A-M): {first_half_avg:.3f}, "
        f"second half (N-Z): {second_half_avg:.3f}. "
        + ("No significant score inflation detected." if abs(diff) < 0.05
           else "Scores got more generous as ranking progressed." if diff > 0
           else "Scores got harsher as ranking progressed.")
    )

    # Franchise score variance (3+ entries only)
    franchise_counts = df["anime_name"].value_counts()
    multi_entry_franchises = franchise_counts[franchise_counts >= 3].index
    df_multi = df[df["anime_name"].isin(multi_entry_franchises)]
    franchise_variance = df_multi.groupby("anime_name")["average_score"].var().nlargest(15).sort_values()

    # Entries per franchise
    franchise_count_top = franchise_counts.head(15).sort_values()

    if len(franchise_variance) > 0:
        franchise_variance_verdict = f"'{franchise_variance.index[-1]}' has the highest internal variance ({franchise_variance.values[-1]:.2f}), meaning reviewers disagreed significantly across its entries. '{franchise_variance.index[0]}' is the most consistent."
    else:
        franchise_variance_verdict = "Not enough data — no franchises with 3 or more entries found."

    descriptions = {
        "Score Distribution per Reviewer": {
            "description": "Shows how each reviewer distributed their scores across all entries.",
            "methodology": "Histogram of raw scores per reviewer with 40 bins across the 1-10 range.",
            "verdict": f"Most scores cluster between 6 and 9. {most_generous} tends to score higher overall ({avgs[most_generous]:.2f} avg), while {harshest} is the harshest ({avgs[harshest]:.2f} avg)."
        },
        "Reviewer Average Scores": {
            "description": "Compares the mean score each reviewer gave across all entries.",
            "methodology": "Simple arithmetic mean of all scores per reviewer.",
            "verdict": f"{most_generous} is the most generous reviewer ({avgs[most_generous]:.2f}). {harshest} is the harshest ({avgs[harshest]:.2f}). A difference above 0.5 suggests meaningfully different taste thresholds."
        },
        "Most Controversial Entries": {
            "description": "Entries where reviewers disagreed the most — one loved it, another didn't.",
            "methodology": "Ranked by score variance across reviewers. Higher variance means more disagreement.",
            "verdict": f"The most controversial entry is '{most_controversial['song_name']}' from {most_controversial['anime_name']} with a variance of {most_controversial['score_variance']:.2f}. Low variance entries like '{most_agreed['song_name']}' had near-unanimous scores."
        },
        "Score Correlation Matrix": {
            "description": "Shows how similarly each pair of reviewers scored entries relative to each other.",
            "methodology": "Pearson correlation coefficient between reviewer score columns. 1.0 = perfect agreement, 0 = no relationship, -1.0 = opposite tastes.",
            "verdict": f"{most_correlated[0]} and {most_correlated[1]} agree the most (r={most_correlated[2]:.2f}). {least_correlated[0]} and {least_correlated[1]} have the most divergent taste (r={least_correlated[2]:.2f})."
        },
        "Top Franchises by Average Score": {
            "description": "Which franchises consistently produced the highest rated OSTs.",
            "methodology": "Mean of average scores across all entries per franchise, top 15 shown.",
            "verdict": f"{top_franchise} has the highest average score ({franchise_avg[top_franchise]:.2f}) across all its entries, making it the most consistently well-rated franchise in the list."
        },
        "Score by Alphabet Position": {
            "description": "Checks whether scores changed as reviewers progressed through the alphabetically sorted list.",
            "methodology": "Each point is one entry plotted by its position in the original alphabetical ranking order against its average score.",
            "verdict": inflation_verdict
        },
        "Franchise Score Variance": {
            "description": "Which franchises have the most inconsistent scores across their entries.",
            "methodology": "Score variance per franchise, only franchises with 3 or more entries included.",
            "verdict": franchise_variance_verdict
        },
        "Entries per Franchise": {
            "description": "Which franchises dominate the list by sheer number of entries.",
            "methodology": "Raw entry count per franchise, top 15 shown.",
            "verdict": f"'{franchise_count_top.index[-1]}' has the most entries ({franchise_count_top.values[-1]}), making it the most represented franchise in the list."
        },
    }

    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=list(descriptions.keys()),
        vertical_spacing=0.08,
    )

    # Score distribution histograms
    for name, col in zip(reviewer_names, reviewer_cols):
        fig.add_trace(go.Histogram(x=df[col], name=name, opacity=0.7, nbinsx=40), row=1, col=1)

    # Reviewer averages bar chart
    fig.add_trace(go.Bar(x=reviewer_names, y=list(avgs.values()), name="Average"), row=1, col=2)

    # Most controversial entries
    top_controversial = df.nlargest(10, "score_variance")
    labels = [f"{row['anime_name'][:20]} - {row['song_name'][:20]}" for _, row in top_controversial.iterrows()]
    fig.add_trace(go.Bar(x=top_controversial["score_variance"].values, y=labels, orientation="h", name="Variance"), row=2, col=1)

    # Correlation heatmap
    fig.add_trace(go.Heatmap(
        z=corr_matrix.values,
        x=reviewer_names,
        y=reviewer_names,
        colorscale="RdYlGn",
        zmin=-1, zmax=1
    ), row=2, col=2)

    # Top franchises by average score
    franchise_avg_top = franchise_avg.nlargest(15).sort_values()
    fig.add_trace(go.Bar(x=franchise_avg_top.values, y=franchise_avg_top.index, orientation="h", name="Avg Score"), row=3, col=1)

    # Score by alphabet position
    df_alpha["position"] = range(1, len(df_alpha) + 1)
    fig.add_trace(go.Scatter(x=df_alpha["position"], y=df_alpha["average_score"], mode="markers", name="Score", opacity=0.5), row=3, col=2)

    # Franchise score variance
    fig.add_trace(go.Bar(
        x=franchise_variance.values,
        y=franchise_variance.index,
        orientation="h",
        name="Variance"
    ), row=4, col=1)

    # Entries per franchise
    fig.add_trace(go.Bar(
        x=franchise_count_top.values,
        y=franchise_count_top.index,
        orientation="h",
        name="Entries"
    ), row=4, col=2)

    fig.update_layout(
        height=2400,
        title_text="Anime OST Pipeline — Analytics Report",
        showlegend=False,
        template="plotly_dark"
    )

    # Build description blocks as HTML
    desc_html = ""
    for title, content in descriptions.items():
        desc_html += f"""
        <div style="margin: 20px 40px; padding: 16px; background: #1e1e1e; border-radius: 8px; border-left: 4px solid #7b68ee;">
            <h3 style="color: #7b68ee; margin: 0 0 8px 0;">{title}</h3>
            <p style="color: #ccc; margin: 4px 0;"><strong style="color: white;">What:</strong> {content['description']}</p>
            <p style="color: #ccc; margin: 4px 0;"><strong style="color: white;">How:</strong> {content['methodology']}</p>
            <p style="color: #ccc; margin: 4px 0;"><strong style="color: white;">Verdict:</strong> {content['verdict']}</p>
        </div>
        """

    full_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Anime OST Analytics Report</title>
        <style>
            body {{ background: #121212; color: white; font-family: sans-serif; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #7b68ee; }}
        </style>
    </head>
    <body>
        <h1>Anime OST Pipeline — Analytics Report</h1>
        {full_html}
        <h2 style="text-align:center; color: #7b68ee; margin-top: 40px;">Chart Descriptions</h2>
        {desc_html}
    </body>
    </html>
    """

    REPORT_PATH.write_text(page, encoding="utf-8")
    logger.info(f"HTML report saved to {REPORT_PATH}")
    print(f"\n  HTML report saved to: {REPORT_PATH}\n")


def generate_report() -> None:
    df = load_data()
    terminal_report(df)
    html_report(df)
