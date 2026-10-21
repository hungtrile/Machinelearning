from demo_salesdatabase.dal.customerDAO import customerDAO
from flask import Flask
from flaskext.mysql import MySQL
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import html
from pathlib import Path

from sklearn.cluster import KMeans
import numpy as np
app = Flask(__name__)
df = customerDAO.getCustomer()

print(df)
print(df.columns)
def showHistogram(df, columns):
    plt.figure(1, figsize=(7, 8))
    n = 0
    for column in columns:
        n += 1
        plt.subplot(3, 1, n)
        plt.subplots_adjust(hspace=0.5, wspace=0.5)
        sns.histplot(df[column], bins=32, kde=True)
        plt.title(f'Histogram of {column}')
    plt.show()

showHistogram(df, df.columns[1:])

def elbowMethod(df, columnsForElbow):
    if len(columnsForElbow) == 0:
        raise ValueError("columnsForElbow must contain at least one column.")

    X = df.loc[:, columnsForElbow].dropna().to_numpy(dtype=float)
    if len(X) < 3:
        raise ValueError("At least 3 complete rows are required to find an elbow.")

    inertia = []
    cluster_counts = np.arange(1, min(10, len(X)) + 1)

    for n in cluster_counts:
        model = KMeans(
            n_clusters=int(n),
            init='k-means++',
            max_iter=500,
            random_state=42
        )
        model.fit(X)
        inertia.append(model.inertia_)

    inertia = np.asarray(inertia)
    inertia_range = np.ptp(inertia)
    if inertia_range == 0:
        optimal_index = 0
    else:
        normalized_x = (cluster_counts - cluster_counts[0]) / (cluster_counts[-1] - cluster_counts[0])
        normalized_y = (inertia - inertia.min()) / inertia_range
        direction = np.array([normalized_x[-1] - normalized_x[0], normalized_y[-1] - normalized_y[0]])
        distances = np.abs(
            direction[0] * (normalized_y - normalized_y[0])
            - direction[1] * (normalized_x - normalized_x[0])
        ) / np.linalg.norm(direction)

        interior_distances = distances[1:-1]
        optimal_index = (
            int(np.argmax(interior_distances)) + 1
            if np.max(interior_distances) > np.finfo(float).eps
            else 0
        )

    optimal_k = int(cluster_counts[optimal_index])

    plt.figure(figsize=(15, 6))
    plt.plot(cluster_counts, inertia, 'o-', label='Inertia')
    plt.plot(
        [cluster_counts[0], cluster_counts[-1]],
        [inertia[0], inertia[-1]],
        '--',
        color='gray',
        label='Reference line'
    )
    plt.scatter([optimal_k], [inertia[optimal_index]], color='red', zorder=3)
    plt.axvline(optimal_k, color='red', linestyle=':', label=f'Optimal K = {optimal_k}')
    plt.xticks(cluster_counts)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Cluster sum of squared distances')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()
    return optimal_k

columns = ['Age', 'Spending_Score']
optimal_k = elbowMethod(df, columns)
print(f'Optimal number of clusters by elbow: {optimal_k}')

def runKMeans(X, cluster):
    model = KMeans(
        n_clusters=cluster,
        init='k-means++',
        max_iter=500,
        random_state=42
    )

    model.fit(X)
    labels = model.labels_
    centroids = model.cluster_centers_
    y_kmeans = model.fit_predict(X)

    return y_kmeans, centroids, labels

X = df.loc[:, columns].values
cluster = 4
colors = ["red", "green", "blue", "purple", "black", "pink", "orange"]

y_kmeans, centroids, labels = runKMeans(X, cluster)

print(y_kmeans)
print(centroids)
print(labels)

df["cluster"] = labels
def visualizeKMeans(X, y_kmeans, cluster, title, xlabel, ylabel, colors):
    plt.figure(figsize=(10, 10))

    for i in range(cluster):
        plt.scatter(
            X[y_kmeans == i, 0],
            X[y_kmeans == i, 1],
            s=100,
            c=colors[i],
            label='Cluster %i' % (i + 1)
        )

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()
visualizeKMeans(
    X,
    y_kmeans,
    cluster,
    "Clusters of Customers - Age X Spending Score",
    "Age",
    "Spending Score",
    colors
)
def export_df2excel(df, filename):
    if "cluster" not in df.columns:
        raise ValueError("DataFrame must contain a 'cluster' column.")
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame.")

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    used_sheet_names = set()
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for cluster_value, cluster_df in df.groupby("cluster", sort=False, dropna=False):
            base_name = re.sub(r"[\[\]:*?/\\]", "_", f"Cluster_{cluster_value}")
            base_name = base_name.strip("'")[:31] or "Cluster"
            sheet_name = base_name
            suffix = 2
            while sheet_name in used_sheet_names:
                suffix_text = f"_{suffix}"
                sheet_name = f"{base_name[:31 - len(suffix_text)]}{suffix_text}"
                suffix += 1

            cluster_df.to_excel(writer, sheet_name=sheet_name, index=False)
            used_sheet_names.add(sheet_name)

output_file = Path(__file__).resolve().parents[1] / "results" / "Customer_cluster.xlsx"
export_df2excel(df, output_file)

def export_df2html(df, filename):
    if "cluster" not in df.columns:
        raise ValueError("DataFrame must contain a 'cluster' column.")
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame.")

    display_columns = ["CustomerID", "Age", "Annual_Income", "Spending_Score"]
    missing_columns = [column for column in display_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {', '.join(missing_columns)}")

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    groups = list(df.groupby("cluster", sort=False, dropna=False))
    colors = [
        "#3867d6", "#20bf6b", "#fa8231", "#8854d0", "#eb3b5a",
        "#0fb9b1", "#f7b731", "#4b6584", "#a55eea", "#2d98da"
    ]

    cluster_labels = []
    cluster_counts = []
    for cluster_value, cluster_df in groups:
        label = "Unassigned" if pd.isna(cluster_value) else str(cluster_value)
        cluster_labels.append(label)
        cluster_counts.append(len(cluster_df))

    try:
        import plotly.express as px
    except ModuleNotFoundError as error:
        if error.name != "plotly":
            raise

        center = 160
        radius = 140
        start_angle = -np.pi / 2
        pie_slices = []
        for index, (label, count) in enumerate(zip(cluster_labels, cluster_counts)):
            sweep = 2 * np.pi * count / len(df)
            color = colors[index % len(colors)]
            if len(groups) == 1:
                pie_slices.append(
                    f'<circle cx="{center}" cy="{center}" r="{radius}" fill="{color}"></circle>'
                )
                label_angle = start_angle + np.pi
            else:
                end_angle = start_angle + sweep
                start_x = center + radius * np.cos(start_angle)
                start_y = center + radius * np.sin(start_angle)
                end_x = center + radius * np.cos(end_angle)
                end_y = center + radius * np.sin(end_angle)
                large_arc = 1 if sweep > np.pi else 0
                pie_slices.append(
                    f'<path d="M {center} {center} L {start_x:.2f} {start_y:.2f} '
                    f'A {radius} {radius} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f} Z" '
                    f'fill="{color}"></path>'
                )
                label_angle = start_angle + sweep / 2

            percentage = count / len(df) * 100
            if percentage >= 4:
                label_radius = 96
                label_x = center + label_radius * np.cos(label_angle)
                label_y = center + label_radius * np.sin(label_angle)
                pie_slices.append(
                    f'<text x="{label_x:.2f}" y="{label_y:.2f}" class="slice-label">'
                    f'{percentage:.1f}%</text>'
                )
            start_angle += sweep

        svg_chart = (
            '<svg class="pie-chart" viewBox="0 0 320 320" role="img" '
            'aria-label="Customer percentage by cluster">'
            + "".join(pie_slices)
            + f'<circle cx="{center}" cy="{center}" r="78" fill="#fff"></circle>'
            + f'<text x="{center}" y="{center - 5}" class="donut-total">{len(df)}</text>'
            + f'<text x="{center}" y="{center + 20}" class="donut-caption">customers</text>'
            + "</svg>"
        )
        legend_items = "".join(
            f'<li><span class="legend-swatch" style="background:{colors[index % len(colors)]}"></span>'
            f'<span>Cluster {html.escape(label)} <strong>{count / len(df) * 100:.1f}%</strong> '
            f'({count} khách hàng)</span></li>'
            for index, (label, count) in enumerate(zip(cluster_labels, cluster_counts))
        )
        chart_html = (
            f'<div class="chart-fallback">{svg_chart}'
            f'<ul class="chart-legend">{legend_items}</ul></div>'
        )
    else:
        chart_data = pd.DataFrame({"Cluster": cluster_labels, "Customers": cluster_counts})
        figure = px.pie(
            chart_data,
            names="Cluster",
            values="Customers",
            hole=0.48,
            color_discrete_sequence=colors
        )
        figure.update_traces(textposition="inside", textinfo="label+percent")
        figure.update_layout(
            autosize=True,
            height=420,
            margin=dict(t=20, b=20, l=20, r=20),
            legend_title_text="Cụm"
        )
        chart_html = figure.to_html(
            full_html=False,
            include_plotlyjs=True,
            config={"responsive": True, "displayModeBar": False}
        )

    cluster_sections = []
    for (cluster_value, cluster_df), label in zip(groups, cluster_labels):
        title = f"Cluster {label}"
        table_html = cluster_df.loc[:, display_columns].to_html(
            index=False,
            escape=True,
            border=0,
            classes="customer-table"
        )
        cluster_sections.append(
            f'<section class="cluster-card">'
            f'<div class="cluster-heading"><h2>{html.escape(title)}</h2>'
            f'<span class="count-badge">{len(cluster_df)} khách hàng</span></div>'
            f'<div class="table-wrap">{table_html}</div>'
            f'</section>'
        )

    document = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Báo cáo phân cụm khách hàng</title>
  <style>
    :root {{ color-scheme: light; --ink: #172b4d; --muted: #64748b; --line: #e5eaf2; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f4f7fb; color: var(--ink); font: 15px/1.5
      "Segoe UI", Arial, sans-serif; }}
    .page {{ width: min(1180px, calc(100% - 40px)); margin: 36px auto 56px; }}
    header {{ padding: 30px 34px; border-radius: 18px; color: #fff;
      background: linear-gradient(120deg, #203a73, #3867d6); box-shadow: 0 12px 30px #203a7326; }}
    header p {{ margin: 8px 0 0; color: #dce7ff; }}
    h1 {{ margin: 0; font-size: clamp(25px, 4vw, 36px); letter-spacing: -.5px; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 16px; margin: 20px 0; }}
    .metric, .panel, .cluster-card {{ background: #fff; border: 1px solid var(--line);
      border-radius: 14px; box-shadow: 0 5px 18px #21385b0a; }}
    .metric {{ padding: 20px 22px; }}
    .metric-label {{ color: var(--muted); font-size: 13px; }}
    .metric-value {{ margin-top: 5px; font-size: 30px; font-weight: 700; }}
    .panel {{ padding: 22px; margin-bottom: 22px; }}
    .panel h2 {{ margin: 0 0 12px; font-size: 20px; }}
    .chart-fallback {{ display: flex; align-items: center; justify-content: center;
      gap: 34px; flex-wrap: wrap; }}
    .pie-chart {{ width: min(320px, 100%); height: auto; overflow: visible; }}
    .slice-label {{ fill: #fff; font-size: 12px; font-weight: 700; text-anchor: middle;
      dominant-baseline: middle; }}
    .donut-total {{ fill: var(--ink); font-size: 30px; font-weight: 700; text-anchor: middle; }}
    .donut-caption {{ fill: var(--muted); font-size: 12px; text-anchor: middle; }}
    .chart-legend {{ display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }}
    .chart-legend li {{ display: flex; align-items: center; gap: 9px; color: var(--muted); }}
    .chart-legend strong {{ color: var(--ink); }}
    .legend-swatch {{ width: 12px; height: 12px; border-radius: 3px; }}
    .cluster-list {{ display: grid; gap: 18px; }}
    .cluster-card {{ overflow: hidden; }}
    .cluster-heading {{ display: flex; align-items: center; justify-content: space-between;
      gap: 12px; padding: 18px 20px; border-bottom: 1px solid var(--line); }}
    .cluster-heading h2 {{ margin: 0; font-size: 18px; }}
    .count-badge {{ padding: 5px 10px; border-radius: 999px; color: #284fa5;
      background: #edf3ff; font-size: 12px; font-weight: 600; white-space: nowrap; }}
    .table-wrap {{ overflow-x: auto; }}
    .customer-table {{ width: 100%; border-collapse: collapse; white-space: nowrap; }}
    .customer-table th, .customer-table td {{ padding: 11px 16px; text-align: left;
      border-bottom: 1px solid #edf0f5; }}
    .customer-table th {{ color: #52637d; background: #f8faff; font-size: 12px;
      text-transform: uppercase; letter-spacing: .04em; }}
    .customer-table tbody tr:last-child td {{ border-bottom: 0; }}
    .customer-table tbody tr:hover {{ background: #f8faff; }}
    @media (max-width: 640px) {{
      .page {{ width: min(100% - 24px, 1180px); margin-top: 16px; }}
      header {{ padding: 24px 20px; }}
      .panel {{ padding: 17px; }}
      .chart-fallback {{ gap: 18px; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <h1>Báo cáo phân cụm khách hàng</h1>
      <p>Phân bổ và danh sách khách hàng theo từng cụm</p>
    </header>
    <section class="summary" aria-label="Report summary">
      <article class="metric"><div class="metric-label">Tổng số khách hàng</div>
        <div class="metric-value">{len(df)}</div></article>
      <article class="metric"><div class="metric-label">Số cụm khách hàng</div>
        <div class="metric-value">{len(groups)}</div></article>
    </section>
    <section class="panel">
      <h2>Tỷ lệ khách hàng theo cụm</h2>
      {chart_html}
    </section>
    <section class="cluster-list" aria-label="Customers grouped by cluster">
      {''.join(cluster_sections)}
    </section>
  </main>
</body>
</html>
"""
    filename.write_text(document, encoding="utf-8")
    return str(filename.resolve())

output_html = Path(__file__).resolve().parents[1] / "results" / "customers_cluster.html"
export_df2html(df, output_html)