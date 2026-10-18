"""Offline V2 Candidate Evaluation Runner (Phase 9 Block O - Task O5).

Evaluates candidate configurations declared in configs/offline_v2_candidates.yaml
strictly on data/splits/dev.jsonl using the identical GroupKFold (n_splits=5)
splits grouped by template_id.

STRICT INVARIANTS:
- data/splits/test.jsonl is NEVER opened or accessed.
- data/test_v2* is NEVER opened or accessed.
- NO keyword rules added.
- Strictly offline, zero network dependencies.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import scipy.stats
import yaml
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.extract.normalize import normalize_arabizi_and_slang, normalize_digits

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def validate_dataset_path(path: Path | str) -> Path:
    """Validate dataset path and strictly refuse to touch test.jsonl."""
    p = Path(path).resolve()
    normalized_str = str(p).lower().replace("\\", "/")

    assert not (p.name == "test.jsonl" or "test.jsonl" in normalized_str), (
        f"Access denied: {p} is a burned diagnostic set and must NEVER be opened or used for cross-validation!"
    )
    if p.name == "test.jsonl" or "test.jsonl" in normalized_str:
        raise ValueError(
            f"Access denied: {p} is a burned diagnostic set and must NEVER be opened or used for cross-validation!"
        )

    if not p.exists():
        raise FileNotFoundError(f"Dataset path not found: {p}")

    return p


def load_dev_dataset(path: Path | str = "data/splits/dev.jsonl") -> list[dict[str, Any]]:
    """Load items from development set after validating test.jsonl exclusion."""
    valid_path = validate_dataset_path(path)
    items: list[dict[str, Any]] = []
    with open(valid_path, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                items.append(json.loads(line_str))
    return items


def extract_groups(items: list[dict[str, Any]]) -> list[str]:
    """Extract grouping labels by template_id.

    Hand-written tickets without template_id each receive their own unique group.
    """
    groups: list[str] = []
    for idx, item in enumerate(items):
        t_id = item.get("label", {}).get("template_id")
        if t_id and str(t_id).strip():
            groups.append(str(t_id).strip())
        else:
            ticket_id = item.get("ticket", {}).get("ticket_id") or f"handwritten_{idx}"
            groups.append(f"unique_handwritten_{ticket_id}")
    return groups


def compute_wilson_ci(correct: int, total: int, confidence: float = 0.95) -> tuple[float, float, float]:
    """Calculate the Wilson score confidence interval for a binomial proportion."""
    if total == 0:
        return 0.0, 0.0, 0.0
    p = correct / total
    z = float(scipy.stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total)))
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return round(p, 4), round(lower, 4), round(upper, 4)


def compute_paired_mcnemar(
    y_true: list[str],
    y_pred_base: list[str],
    y_pred_cand: list[str],
) -> tuple[float, float, bool]:
    """Paired McNemar test on identical out-of-fold predictions."""
    b = sum(1 for yt, yb, yc in zip(y_true, y_pred_base, y_pred_cand, strict=True) if yt == yb and yt != yc)
    c = sum(1 for yt, yb, yc in zip(y_true, y_pred_base, y_pred_cand, strict=True) if yt != yb and yt == yc)
    total_discordant = b + c
    if total_discordant == 0:
        return 0.0, 1.0, False

    if total_discordant < 25:
        res = scipy.stats.binomtest(b, total_discordant, 0.5)
        p_val = float(res.pvalue)
        stat = float(abs(b - c))
    else:
        stat = ((abs(b - c) - 1.0) ** 2) / total_discordant
        p_val = float(scipy.stats.chi2.sf(stat, df=1))

    return round(stat, 4), round(p_val, 4), p_val < 0.05


def arabic_v2_normalizer(text: str) -> str:
    """Enhanced Arabic normalization for V2 candidate models.

    - Strips tatweel (\\u0640) and harakat/tashkeel
    - Unifies alef: [إأآٱ] -> ا
    - Unifies ya / alif maqsura: [ى] -> ي
    - Unifies ta-marbuta: [ة] -> ه
    - Squeezes repeated letters (3+ -> 2)
    - Arabizi digit-letters when adjacent to latin
    """
    if not text:
        return text
    t = text.replace("\u0640", "")
    t = re.sub(r"[\u064B-\u065F\u0670]", "", t)
    t = re.sub(r"[إأآٱ]", "ا", t)
    t = re.sub(r"[ى]", "ي", t)
    t = re.sub(r"[ة]", "ه", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    t = re.sub(r"(?<=[a-zA-Z])7|7(?=[a-zA-Z])", "h", t)
    t = re.sub(r"(?<=[a-zA-Z])3|3(?=[a-zA-Z])", "e", t)
    t = re.sub(r"(?<=[a-zA-Z])5|5(?=[a-zA-Z])", "kh", t)
    t = re.sub(r"(?<=[a-zA-Z])8|8(?=[a-zA-Z])", "gh", t)
    return t


def build_pipeline_from_candidate(config: dict[str, Any]) -> tuple[Pipeline, dict[str, Any]]:
    """Build scikit-learn Pipeline and training options from V2 candidate dict."""
    vec_cfg = config.get("vectorizer", {})
    clf_cfg = config.get("classifier", {})
    norm_cfg = config.get("normalization", {})
    training_cfg = config.get("training", {})

    preproc = arabic_v2_normalizer if norm_cfg else None

    # Vectorizer
    vec_type = vec_cfg.get("type", "word")
    if vec_type == "char_wb":
        ngram_range = tuple(vec_cfg.get("ngram_range", [3, 5]))
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=ngram_range,
            sublinear_tf=vec_cfg.get("sublinear_tf", True),
            min_df=vec_cfg.get("min_df", 1),
            preprocessor=preproc,
        )
    elif vec_type == "union_word_char":
        w_ngram = tuple(vec_cfg.get("word_ngram_range", [1, 2]))
        c_ngram = tuple(vec_cfg.get("char_ngram_range", [3, 5]))
        vectorizer = FeatureUnion([
            (
                "w",
                TfidfVectorizer(
                    ngram_range=w_ngram,
                    sublinear_tf=vec_cfg.get("sublinear_tf", True),
                    min_df=vec_cfg.get("min_df", 1),
                    preprocessor=preproc,
                ),
            ),
            (
                "c",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=c_ngram,
                    sublinear_tf=vec_cfg.get("sublinear_tf", True),
                    min_df=vec_cfg.get("min_df", 1),
                    preprocessor=preproc,
                ),
            ),
        ])
    else:
        ngram_range = tuple(vec_cfg.get("ngram_range", [1, 2]))
        vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            sublinear_tf=vec_cfg.get("sublinear_tf", True),
            min_df=vec_cfg.get("min_df", 1),
            preprocessor=preproc,
        )

    # Classifier
    clf_type = clf_cfg.get("type", "logistic_regression")
    if clf_type == "logistic_regression":
        classifier = LogisticRegression(
            C=float(clf_cfg.get("C", 2.5)),
            class_weight=clf_cfg.get("class_weight"),
            max_iter=int(clf_cfg.get("max_iter", 300)),
            random_state=int(clf_cfg.get("random_state", 42)),
        )
    elif clf_type == "logistic_regression_calibrated":
        base_lr = LogisticRegression(
            C=float(clf_cfg.get("C", 2.5)),
            class_weight=clf_cfg.get("class_weight"),
            max_iter=int(clf_cfg.get("max_iter", 300)),
            random_state=int(clf_cfg.get("random_state", 42)),
        )
        classifier = CalibratedClassifierCV(
            base_lr,
            cv=int(clf_cfg.get("calibration_cv", 3)),
        )
    elif clf_type == "linear_svc_calibrated":
        base_svc = LinearSVC(
            C=float(clf_cfg.get("C", 1.0)),
            max_iter=int(clf_cfg.get("max_iter", 2000)),
            random_state=int(clf_cfg.get("random_state", 42)),
        )
        classifier = CalibratedClassifierCV(
            base_svc,
            cv=int(clf_cfg.get("calibration_cv", 3)),
        )
    elif clf_type == "complement_nb":
        classifier = ComplementNB(
            alpha=float(clf_cfg.get("alpha", 0.5)),
            norm=bool(clf_cfg.get("norm", False)),
        )
    elif clf_type == "sgd":
        classifier = SGDClassifier(
            loss=clf_cfg.get("loss", "log_loss"),
            penalty=clf_cfg.get("penalty", "l2"),
            alpha=float(clf_cfg.get("alpha", 1e-4)),
            class_weight=clf_cfg.get("class_weight"),
            max_iter=int(clf_cfg.get("max_iter", 1000)),
            random_state=int(clf_cfg.get("random_state", 42)),
        )
    else:
        raise ValueError(f"Unknown classifier type: {clf_type}")

    pipe = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])
    return pipe, training_cfg


def evaluate_v2_candidate(
    items: list[dict[str, Any]],
    cand_config: dict[str, Any] | None,
    n_splits: int = 5,
) -> dict[str, Any]:
    """Evaluate candidate on GroupKFold splits.

    If cand_config is None, evaluates baseline v1.
    """
    raw_texts = [str(it["ticket"]["raw_text"]) for it in items]
    norm_texts = [normalize_arabizi_and_slang(normalize_digits(t)) for t in raw_texts]
    categories = [str(it["label"]["category"]) for it in items]
    priorities = [str(it["label"]["priority"]) for it in items]
    channels = [str(it["ticket"].get("channel", "app")) for it in items]
    template_ids = [str(it["label"].get("template_id", "")) for it in items]
    groups = extract_groups(items)

    total_samples = len(items)
    gkf = GroupKFold(n_splits=n_splits)

    oof_ml_preds: list[str] = [""] * total_samples
    oof_rules_ml_preds: list[str] = [""] * total_samples
    oof_rules_ml_confs: list[float] = [0.0] * total_samples

    prio_base_pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("lr", LogisticRegression(C=2.0, max_iter=300, random_state=42)),
    ])

    for _fold, (train_idx, test_idx) in enumerate(gkf.split(norm_texts, categories, groups)):
        if cand_config is None:
            # Baseline v1 pipeline
            fold_cat_pipe = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
                ("lr", LogisticRegression(C=2.5, max_iter=300, random_state=42)),
            ])
            training_cfg: dict[str, Any] = {}
        else:
            fold_cat_pipe, training_cfg = build_pipeline_from_candidate(cand_config)

        # Handle training modifications (de-duplication or template weighting)
        effective_train_idx = list(train_idx)
        if training_cfg.get("deduplicate_within_template", False):
            seen_templates: set[tuple[str, str]] = set()
            filtered_idx = []
            for i in train_idx:
                key = (template_ids[i], norm_texts[i])
                if key not in seen_templates:
                    seen_templates.add(key)
                    filtered_idx.append(i)
            effective_train_idx = filtered_idx

        X_train = [norm_texts[i] for i in effective_train_idx]
        y_train = [categories[i] for i in effective_train_idx]
        y_train_prio = [priorities[i] for i in effective_train_idx]

        # Calculate sample weights if template weighting enabled
        fit_params: dict[str, Any] = {}
        if training_cfg.get("sample_weight") == "template_sqrt_inverse":
            t_counts = Counter(template_ids[i] for i in effective_train_idx)
            weights = np.array([1.0 / math.sqrt(max(1, t_counts[template_ids[i]])) for i in effective_train_idx])
            fit_params["classifier__sample_weight"] = weights

        fold_cat_pipe.fit(X_train, y_train, **fit_params)

        fold_prio_pipe = Pipeline(prio_base_pipe.steps)
        fold_prio_pipe.fit(X_train, y_train_prio)

        provider = MockClassifierProvider()
        provider.cat_pipe = fold_cat_pipe
        provider.prio_pipe = fold_prio_pipe

        for idx in test_idx:
            test_norm = norm_texts[idx]
            pred_ml = str(fold_cat_pipe.predict([test_norm])[0])
            oof_ml_preds[idx] = pred_ml

            res = provider.classify(ticket_text=raw_texts[idx], channel=channels[idx])
            oof_rules_ml_preds[idx] = res.category
            oof_rules_ml_confs[idx] = res.category_confidence

    # ML-only metrics
    ml_corr = sum(1 for yt, yp in zip(categories, oof_ml_preds, strict=True) if yt == yp)
    ml_acc, ml_low, ml_high = compute_wilson_ci(ml_corr, total_samples)
    ml_rep = classification_report(categories, oof_ml_preds, output_dict=True, zero_division=0)

    # Rules+ML metrics
    rules_corr = sum(1 for yt, yp in zip(categories, oof_rules_ml_preds, strict=True) if yt == yp)
    rules_acc, rules_low, rules_high = compute_wilson_ci(rules_corr, total_samples)
    rules_rep = classification_report(categories, oof_rules_ml_preds, output_dict=True, zero_division=0)

    return {
        "total_samples": total_samples,
        "y_true": categories,
        "ml_only": {
            "correct": ml_corr,
            "accuracy": rules_acc,  # placeholder
            "acc": ml_acc,
            "wilson_ci": (ml_low, ml_high),
            "predictions": oof_ml_preds,
            "report": ml_rep,
        },
        "rules_ml": {
            "correct": rules_corr,
            "accuracy": rules_acc,
            "wilson_ci": (rules_low, rules_high),
            "predictions": oof_rules_ml_preds,
            "confidences": oof_rules_ml_confs,
            "report": rules_rep,
        },
    }


def evaluate_escalation_thresholds(
    y_true: list[str],
    y_pred: list[str],
    confs: list[float],
    thresholds: list[float] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate accuracy vs escalation rate across confidence thresholds."""
    if thresholds is None:
        thresholds = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]

    total = len(y_true)
    results = []
    for th in thresholds:
        escalated_idx = [i for i, c in enumerate(confs) if c < th]
        accepted_idx = [i for i, c in enumerate(confs) if c >= th]
        n_esc = len(escalated_idx)
        n_acc = len(accepted_idx)
        esc_rate = n_esc / total if total > 0 else 0.0
        acc_accepted = (
            sum(1 for i in accepted_idx if y_true[i] == y_pred[i]) / n_acc if n_acc > 0 else 0.0
        )
        results.append({
            "threshold": th,
            "escalated_count": n_esc,
            "escalation_rate": round(esc_rate, 4),
            "accepted_count": n_acc,
            "accepted_accuracy": round(acc_accepted, 4),
        })
    return results


def check_qualification_gate(
    baseline_res: dict[str, Any],
    cand_res: dict[str, Any],
) -> tuple[bool, str]:
    """Evaluate candidate against the 3 Qualification Gate requirements:

    1. McNemar p < 0.05 vs baseline Rules+ML (78/219)
    2. No category recall drops by > 15 percentage points (0.15)
    3. Offline only, no live calls
    """
    y_true = baseline_res["y_true"]
    y_base = baseline_res["rules_ml"]["predictions"]
    y_cand = cand_res["rules_ml"]["predictions"]

    _stat, p_val, is_sig = compute_paired_mcnemar(y_true, y_base, y_cand)
    delta_acc = cand_res["rules_ml"]["accuracy"] - baseline_res["rules_ml"]["accuracy"]

    # Condition 1: McNemar p < 0.05 and positive delta
    if not is_sig or delta_acc <= 0:
        return False, f"Condition 1 failed: McNemar p={p_val:.4f} (must be < 0.05) or delta={delta_acc:+.2%} <= 0"

    # Condition 2: No category recall drops by > 15 percentage points
    base_rep = baseline_res["rules_ml"]["report"]
    cand_rep = cand_res["rules_ml"]["report"]
    all_cats = [k for k in base_rep if k not in ["accuracy", "macro avg", "weighted avg"]]

    worst_drop = 0.0
    worst_cat = ""
    for cat in all_cats:
        r_base = base_rep[cat]["recall"]
        r_cand = cand_rep[cat]["recall"]
        drop = r_base - r_cand
        if drop > worst_drop:
            worst_drop = drop
            worst_cat = cat

    if worst_drop > 0.1501:
        return False, f"Condition 2 failed: Category '{worst_cat}' recall dropped by {worst_drop:.1%} (> 15pp)"

    # Condition 3: Offline only (verified by architecture)
    return True, f"Qualified! Delta={delta_acc:+.2%}, p={p_val:.4f}, max recall drop={worst_drop:.1%} on '{worst_cat}'"


def run_evaluations(
    dev_path: Path | str = "data/splits/dev.jsonl",
    candidates_path: Path | str = "configs/offline_v2_candidates.yaml",
) -> dict[str, Any]:
    """Run GroupKFold evaluation on all V2 candidates."""
    items = load_dev_dataset(dev_path)
    logger.info("Loaded %d tickets from %s", len(items), dev_path)

    # 1. Baseline Rules+ML evaluation
    logger.info("Evaluating Baseline Rules+ML (v1)...")
    baseline_res = evaluate_v2_candidate(items, None)
    b_rules = baseline_res["rules_ml"]
    logger.info(
        "Baseline Rules+ML: %d/%d (%.2f%%) [Wilson CI: %.2f%% - %.2f%%]",
        b_rules["correct"],
        baseline_res["total_samples"],
        b_rules["accuracy"] * 100,
        b_rules["wilson_ci"][0] * 100,
        b_rules["wilson_ci"][1] * 100,
    )

    # 2. Baseline Escalation evaluation (O4)
    esc_baseline = evaluate_escalation_thresholds(
        baseline_res["y_true"],
        b_rules["predictions"],
        b_rules["confidences"],
    )

    # 3. Load Candidates
    with open(candidates_path, encoding="utf-8") as f:
        cand_yaml = yaml.safe_load(f)
    candidates: list[dict[str, Any]] = cand_yaml.get("candidates", [])
    logger.info("Loaded %d candidates from %s", len(candidates), candidates_path)

    eval_results = []
    qualified_candidates = []

    for c in candidates:
        cid = c["id"]
        cname = c["name"]
        logger.info("Evaluating Candidate [%s]: %s ...", cid, cname)

        c_res = evaluate_v2_candidate(items, c)
        c_rules = c_res["rules_ml"]
        corr = c_rules["correct"]
        acc = c_rules["accuracy"]
        ci = c_rules["wilson_ci"]
        delta = round(acc - b_rules["accuracy"], 4)

        stat, p_val, is_sig = compute_paired_mcnemar(
            baseline_res["y_true"],
            b_rules["predictions"],
            c_rules["predictions"],
        )

        qualifies, gate_reason = check_qualification_gate(baseline_res, c_res)
        if qualifies:
            qualified_candidates.append(cid)

        logger.info(
            "--> Result [%s]: %d/219 (%.2f%%) | delta: %+.2f%% | McNemar p=%.4f (sig=%s) | %s",
            cid,
            corr,
            acc * 100,
            delta * 100,
            p_val,
            is_sig,
            gate_reason,
        )

        eval_results.append({
            "id": cid,
            "name": cname,
            "description": c.get("description", ""),
            "correct": corr,
            "accuracy": acc,
            "wilson_ci": ci,
            "delta": delta,
            "mcnemar_stat": stat,
            "mcnemar_p": p_val,
            "is_significant": is_sig,
            "qualifies": qualifies,
            "gate_reason": gate_reason,
            "res": c_res,
        })

    return {
        "baseline": baseline_res,
        "escalation_baseline": esc_baseline,
        "candidates": eval_results,
        "qualified_candidates": qualified_candidates,
    }


def print_markdown_table(results: dict[str, Any]) -> str:
    """Format evaluation table as Markdown."""
    lines = []
    lines.append("| Candidate Config | Grouped-CV Acc | 95% Wilson CI | Delta vs Rules+ML (78/219, 35.62%) | McNemar p vs Rules+ML | Qualified? | Gate Verdict |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

    b_acc = results["baseline"]["rules_ml"]["accuracy"]
    b_ci = results["baseline"]["rules_ml"]["wilson_ci"]
    lines.append(f"| `baseline_rules_ml_v1` | {b_acc:.2%} | [{b_ci[0]:.2%}, {b_ci[1]:.2%}] | +0.00% | 1.0000 | Reference | Baseline |")

    for c in results["candidates"]:
        cid = c["id"]
        acc = c["accuracy"]
        ci = c["wilson_ci"]
        delta = c["delta"]
        p_val = c["mcnemar_p"]
        qual = "**YES**" if c["qualifies"] else "No"
        gate = c["gate_reason"]
        lines.append(f"| `{cid}` | **{acc:.2%}** | [{ci[0]:.2%}, {ci[1]:.2%}] | **{delta:+.2%}** | {p_val:.4f} | {qual} | {gate} |")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline V2 Candidate Evaluation Runner")
    parser.add_argument("--dev-path", default="data/splits/dev.jsonl", help="Path to dev dataset")
    parser.add_argument("--candidates-path", default="configs/offline_v2_candidates.yaml", help="Path to candidates YAML")
    args = parser.parse_args()

    results = run_evaluations(args.dev_path, args.candidates_path)
    md_table = print_markdown_table(results)
    print("\n" + md_table + "\n")


if __name__ == "__main__":
    main()
