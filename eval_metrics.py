import csv
import json
import math
import os
import sqlite3
from collections import defaultdict

import matplotlib.pyplot as plt

from config import Config


def load_qrels(path: str):
    """Reads qrels CSV with columns: query,url,relevant (1/0)."""
    qrels = defaultdict(dict)
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row['query'].strip()
            url = row['url'].strip()
            rel = int(row['relevant'])
            qrels[q][url] = rel
    return qrels


def fetch_system_results(conn, query: str):
    """Gets concatenated results for all pages for a query (p1..pN)."""
    cur = conn.cursor()
    like = f"{query}::p%"
    cur.execute('SELECT results_json FROM queries WHERE query LIKE ? ORDER BY updated_at ASC', (like,))
    urls = []
    seen = set()
    for (results_json,) in cur.fetchall():
        if not results_json:
            continue
        results = json.loads(results_json)
        for r in results:
            u = r.get('url')
            if u and u not in seen:
                urls.append(u)
                seen.add(u)
    return urls


def precision_at_k(ranked_urls, relset, k):
    k = min(k, len(ranked_urls))
    if k == 0:
        return 0.0
    hits = sum(1 for u in ranked_urls[:k] if relset.get(u, 0) == 1)
    return hits / k


def recall(ranked_urls, relset):
    total_rel = sum(1 for v in relset.values() if v == 1)
    if total_rel == 0:
        return 0.0
    hits = sum(1 for u in ranked_urls if relset.get(u, 0) == 1)
    return hits / total_rel


def r_precision(ranked_urls, relset):
    R = sum(1 for v in relset.values() if v == 1)
    if R == 0:
        return 0.0
    return precision_at_k(ranked_urls, relset, R)


def average_precision(ranked_urls, relset):
    total_rel = sum(1 for v in relset.values() if v == 1)
    if total_rel == 0:
        return 0.0
    ap_sum = 0.0
    found = 0
    for i, u in enumerate(ranked_urls, start=1):
        if relset.get(u, 0) == 1:
            found += 1
            ap_sum += found / i
    return ap_sum / total_rel


def f1(prec, rec):
    if prec == 0 and rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def accuracy_error(ranked_urls, relset):
    # Build a binary decision per item universe: relevant seen in results vs not
    # For IR evaluation, use confusion at cutoff N = len(ranked_urls)
    N = len(ranked_urls)
    # positives predicted = N, negatives = rest unknown; we approximate within cutoff
    tp = sum(1 for u in ranked_urls if relset.get(u, 1) == 1)  # treat unknown as non-penalizing
    fp = sum(1 for u in ranked_urls if relset.get(u, 0) == 0)
    # Without a closed world of all documents, accuracy/error are less meaningful; compute on cutoff only
    a = tp
    b = fp
    c = 0
    d = 0
    denom = (a + b + c + d)
    if denom == 0:
        return 0.0, 0.0
    acc = (a + d) / denom
    err = (b + c) / denom
    return acc, err


def interpolated_pr_points(ranked_urls, relset):
    # Build precision after each retrieved relevant; then 11-pt interpolation
    precisions = []
    recalls = []
    rel_total = sum(1 for v in relset.values() if v == 1)
    if rel_total == 0:
        return [(r, 0.0) for r in [i/10 for i in range(11)]]

    found = 0
    for i, u in enumerate(ranked_urls, start=1):
        if relset.get(u, 0) == 1:
            found += 1
        precisions.append(sum(1 for x in ranked_urls[:i] if relset.get(x, 0) == 1) / i)
        recalls.append(found / rel_total)

    def interp(p_required):
        p_max = 0.0
        for p, r in zip(precisions, recalls):
            if r >= p_required and p > p_max:
                p_max = p
        return p_max

    points = []
    for t in range(11):
        r_level = t / 10
        points.append((r_level, interp(r_level)))
    return points


def evaluate(qrels_path='data/qrels.csv', output_plot='data/precision_recall.png'):
    qrels = load_qrels(qrels_path)
    conn = sqlite3.connect(Config.DB_PATH)

    per_query = {}
    avg = defaultdict(float)
    pr_curves = {}

    for query, relset in qrels.items():
        ranked_urls = fetch_system_results(conn, query)

        p = precision_at_k(ranked_urls, relset, len(ranked_urls) or 1)
        r = recall(ranked_urls, relset)
        p5 = precision_at_k(ranked_urls, relset, 5)
        p10 = precision_at_k(ranked_urls, relset, 10)
        rp = r_precision(ranked_urls, relset)
        ap = average_precision(ranked_urls, relset)
        f = f1(p, r)
        acc, err = accuracy_error(ranked_urls, relset)
        curve = interpolated_pr_points(ranked_urls, relset)

        per_query[query] = {
            'precision': p,
            'recall': r,
            'precision@5': p5,
            'precision@10': p10,
            'r_precision': rp,
            'average_precision': ap,
            'f1': f,
            'accuracy': acc,
            'error': err,
        }

        avg['precision'] += p
        avg['recall'] += r
        avg['precision@5'] += p5
        avg['precision@10'] += p10
        avg['r_precision'] += rp
        avg['average_precision'] += ap
        avg['f1'] += f
        avg['accuracy'] += acc
        avg['error'] += err
        pr_curves[query] = curve

    n = max(1, len(per_query))
    macro = {k: v / n for k, v in avg.items()}

    # 11-point averaged curve
    recalls = [i / 10 for i in range(11)]
    mean_precisions = []
    for r_level in recalls:
        vals = []
        for curve in pr_curves.values():
            for r, p in curve:
                if abs(r - r_level) < 1e-9:
                    vals.append(p)
                    break
        mean_precisions.append(sum(vals) / len(vals) if vals else 0.0)

    # Plot
    plt.figure(figsize=(6, 5))
    plt.plot(recalls, mean_precisions, marker='o')
    plt.title('11-point Interpolated Precision-Recall')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim(0, 1.05)
    plt.xlim(0, 1.0)
    plt.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(output_plot), exist_ok=True)
    plt.savefig(output_plot, dpi=150, bbox_inches='tight')
    plt.close()

    return per_query, macro, output_plot


if __name__ == '__main__':
    q = os.environ.get('QRELS', 'data/qrels.csv')
    per_query, macro, plot_path = evaluate(qrels_path=q)
    print('Per-query metrics:')
    for k, v in per_query.items():
        print(k, v)
    print('\nMacro-averaged:')
    for k, v in macro.items():
        print(f'{k}: {v:.4f}')
    print(f'PR plot saved to: {plot_path}')


