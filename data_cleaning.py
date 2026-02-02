"""
data_cleaning.py

Goal:
- Provide reusable, testable functions that Streamlit can import.
- Keep notebooks for exploration; production logic lives here.

This module includes:
- Loading the three challenge CSVs
- Light type normalization (dates/numerics/yes-no)
- Data quality auditing + Health Score
- Cleaning functions that return:
    (clean_df, excluded_df, log_dict)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Loading
# -----------------------------

DATASETS = {
    "inventario": "inventario_central_v2.csv",
    "transacciones": "transacciones_logistica_v2.csv",
    "feedback": "feedback_clientes_v2.csv",
}


def load_raw_data(data_dir: str | Path = "data") -> Dict[str, pd.DataFrame]:
    """
    Load the 3 CSVs from a folder (default: ./data).

    Returns:
        {"inventario": df_inv, "transacciones": df_trx, "feedback": df_fb}
    """
    data_dir = Path(data_dir)
    out: Dict[str, pd.DataFrame] = {}
    for k, fname in DATASETS.items():
        path = data_dir / fname
        out[k] = pd.read_csv(path)
    return out


# -----------------------------
# Small helpers (normalization)
# -----------------------------

def _to_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def parse_fecha_venta(df: pd.DataFrame, col: str = "Fecha_Venta") -> pd.DataFrame:
    """
    Notebook logic: Fecha_Venta appears as dd/mm/YYYY.
    Creates a standardized datetime column: Fecha_Venta_dt
    """
    if col not in df.columns:
        return df
    df = df.copy()
    df["Fecha_Venta_dt"] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")
    return df


def normalize_yes_no(series: pd.Series) -> pd.Series:
    """
    Normalizes common yes/no values to {1,0} with NaN for unknown.
    Includes the transformation seen in revision_data_feedback.ipynb
    for Ticket_Soporte_Abierto (Sí/No, '1'/'0').
    """
    if series is None:
        return series
    s = series.astype("string").str.strip().str.lower()
    mapping = {
        "sí": 1, "si": 1, "s": 1, "yes": 1, "y": 1, "1": 1, "true": 1, "t": 1,
        "no": 0, "n": 0, "0": 0, "false": 0, "f": 0,
    }
    out = s.map(mapping)
    return pd.to_numeric(out, errors="coerce")


def normalize_city(series: pd.Series) -> pd.Series:
    """
    Validation guide expects you to normalize city variants like MED/med/Medellín
    into one canonical value.

    This is intentionally conservative: extend the mapping as you discover variants.
    """
    if series is None:
        return series
    s = series.astype("string").str.strip()

    # Lowercase for matching, but we output canonical "Title Case"
    sl = s.str.lower()

    mapping = {
        "med": "Medellín",
        "medellin": "Medellín",
        "medellín": "Medellín",
        "bog": "Bogotá",
        "bogota": "Bogotá",
        "bogotá": "Bogotá",
        "cali": "Cali",
        "ctg": "Cartagena",
        "cartagena": "Cartagena",
        # add more as needed
    }

    out = sl.map(mapping)
    # if not in mapping, keep original trimmed value
    out = out.fillna(s)
    return out


# -----------------------------
# Outliers (IQR)
# -----------------------------

def iqr_bounds(series: pd.Series) -> tuple[float, float] | None:
    s = _to_numeric(series).dropna()
    if s.empty:
        return None
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return float(q1), float(q3)
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return float(lower), float(upper)


# -----------------------------
# Auditing + Health Score
# -----------------------------

def audit_quality(
    df: pd.DataFrame,
    dataset_name: str,
    critical_cols: List[str],
    numeric_cols: List[str],
    invalid_rules: Dict[str, Callable[[pd.DataFrame], pd.Series]] | None = None,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      summary: dict of KPIs (health score, null pct, dup, outliers, invalid)
      nulls_table: DataFrame(column, null_pct)
      outliers_table: DataFrame(column, outlier_count, outlier_pct, lower, upper)
      excluded_rows_df: DataFrame of rows flagged as invalid/outlier with 'reason'
    """
    invalid_rules = invalid_rules or {}
    df0 = df
    n_rows, n_cols = df0.shape

    # Nulls
    null_pct_by_col = (df0.isna().mean() * 100).sort_values(ascending=False)
    null_global_pct = (df0.isna().sum().sum() / (n_rows * n_cols) * 100) if (n_rows and n_cols) else 0.0

    critical_present = [c for c in critical_cols if c in df0.columns]
    critical_null_pct = float(null_pct_by_col[critical_present].mean()) if critical_present else 0.0

    # Duplicates (full row)
    dup_rows = int(df0.duplicated().sum())
    dup_ratio = (dup_rows / n_rows * 100) if n_rows else 0.0

    # Invalid rules
    invalid_masks = []
    excluded_parts = []

    for rule_name, rule_fn in invalid_rules.items():
        try:
            mask = rule_fn(df0)
        except Exception:
            continue
        if mask is not None and mask.any():
            invalid_masks.append(mask.to_numpy())
            tmp = df0.loc[mask].copy()
            tmp["reason"] = f"invalid: {rule_name}"
            tmp["dataset"] = dataset_name
            excluded_parts.append(tmp)

    invalid_mask = np.logical_or.reduce(invalid_masks) if invalid_masks else np.array([False] * n_rows)
    invalid_rows_total = int(invalid_mask.sum())

    # Outliers via IQR
    outlier_any_mask = np.array([False] * n_rows)
    outlier_meta = []

    for col in [c for c in numeric_cols if c in df0.columns]:
        bounds = iqr_bounds(df0[col])
        if bounds is None:
            continue
        lower, upper = bounds
        s = _to_numeric(df0[col])
        mask = (s < lower) | (s > upper)
        count = int(mask.sum())

        outlier_meta.append({
            "column": col,
            "outlier_count": count,
            "outlier_pct": (count / n_rows * 100) if n_rows else 0.0,
            "lower": lower,
            "upper": upper,
        })

        if count:
            outlier_any_mask = outlier_any_mask | mask.fillna(False).to_numpy()
            tmp = df0.loc[mask.fillna(False)].copy()
            tmp["reason"] = f"outlier: {col}"
            tmp["dataset"] = dataset_name
            excluded_parts.append(tmp)

    outlier_rows_total = int(outlier_any_mask.sum())
    outlier_ratio = (outlier_rows_total / n_rows * 100) if n_rows else 0.0

    # Health score (explainable & stable)
    penalty_nulls = (null_global_pct * 0.4) + (critical_null_pct * 0.6)
    penalty_dup = dup_ratio * 0.5
    penalty_out = outlier_ratio * 0.7
    penalty_inv = ((invalid_rows_total / n_rows * 100) * 1.5) if n_rows else 0.0

    score = 100 - (penalty_nulls + penalty_dup + penalty_out + penalty_inv)
    score = float(max(0, min(100, score)))

    summary = {
        "dataset": dataset_name,
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "null_global_pct": float(null_global_pct),
        "critical_null_pct": float(critical_null_pct),
        "dup_rows": int(dup_rows),
        "outlier_rows_total": int(outlier_rows_total),
        "invalid_rows_total": int(invalid_rows_total),
        "health_score": score,
    }

    nulls_table = null_pct_by_col.reset_index()
    nulls_table.columns = ["column", "null_pct"]

    outliers_table = pd.DataFrame(outlier_meta)
    if not outliers_table.empty:
        outliers_table = outliers_table.sort_values("outlier_count", ascending=False)

    excluded_rows_df = pd.concat(excluded_parts, ignore_index=True) if excluded_parts else pd.DataFrame()

    return summary, nulls_table, outliers_table, excluded_rows_df


# -----------------------------
# Invalid rules (based on challenge + validation)
# -----------------------------

def invalid_rules_inventario() -> Dict[str, Callable[[pd.DataFrame], pd.Series]]:
    rules = {}

    if "Stock_Actual" in rules:  # no-op, keep pattern
        pass

    def stock_negative(df: pd.DataFrame) -> pd.Series:
        if "Stock_Actual" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        return _to_numeric(df["Stock_Actual"]) < 0

    rules["stock_negative"] = stock_negative
    return rules


def invalid_rules_transacciones(now: pd.Timestamp | None = None) -> Dict[str, Callable[[pd.DataFrame], pd.Series]]:
    now = now or pd.Timestamp.now()
    rules = {}

    def future_sales(df: pd.DataFrame) -> pd.Series:
        if "Fecha_Venta_dt" not in df.columns and "Fecha_Venta" in df.columns:
            tmp = parse_fecha_venta(df)
            d = tmp["Fecha_Venta_dt"]
        else:
            d = df.get("Fecha_Venta_dt")
        if d is None:
            return pd.Series([False] * len(df), index=df.index)
        return pd.to_datetime(d, errors="coerce") > now

    rules["future_sales"] = future_sales
    return rules


def invalid_rules_feedback() -> Dict[str, Callable[[pd.DataFrame], pd.Series]]:
    rules = {}

    def age_impossible(df: pd.DataFrame) -> pd.Series:
        if "Edad_Cliente" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        age = _to_numeric(df["Edad_Cliente"])
        # conservative bounds (tune if the dataset is different)
        return (age < 10) | (age > 110)

    def nps_out_of_range(df: pd.DataFrame) -> pd.Series:
        if "Satisfaccion_NPS" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        nps = _to_numeric(df["Satisfaccion_NPS"])
        # NPS usually -100..100
        return (nps < -100) | (nps > 100)

    rules["age_impossible"] = age_impossible
    rules["nps_out_of_range"] = nps_out_of_range
    return rules


# -----------------------------
# Cleaning functions (return clean + excluded + log)
# -----------------------------

def clean_inventario(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    df0 = df.copy()
    excluded_parts = []

    # Normalize categorical text
    if "Ciudad" in df0.columns:
        df0["Ciudad"] = normalize_city(df0["Ciudad"])
    if "Bodega_Origen" in df0.columns:
        df0["Bodega_Origen"] = df0["Bodega_Origen"].astype("string").str.strip()

    # Coerce numerics
    for col in ["Stock_Actual", "Costo_Unitario_USD", "Punto_Reorden", "Lead_Time_Dias"]:
        if col in df0.columns:
            df0[col] = _to_numeric(df0[col])

    # Invalid: stock negative (exclude)
    inv_rules = invalid_rules_inventario()
    mask_neg = inv_rules["stock_negative"](df0)
    if mask_neg.any():
        tmp = df0.loc[mask_neg].copy()
        tmp["reason"] = "invalid: stock_negative"
        excluded_parts.append(tmp)
        df0 = df0.loc[~mask_neg].copy()

    excluded = pd.concat(excluded_parts, ignore_index=True) if excluded_parts else pd.DataFrame()
    log = {
        "dataset": "inventario",
        "rows_in": int(len(df)),
        "rows_out": int(len(df0)),
        "excluded_rows": int(len(excluded)),
        "notes": "Types normalized; negative stock excluded (see excluded reasons).",
    }
    return df0, excluded, log


def clean_transacciones(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    df0 = df.copy()
    excluded_parts = []

    # Fecha parsing (from notebook)
    df0 = parse_fecha_venta(df0, col="Fecha_Venta")

    # Normalize city fields
    for col in ["Ciudad_Destino", "Ciudad_Origen"]:
        if col in df0.columns:
            df0[col] = normalize_city(df0[col])

    # Coerce numerics
    for col in ["Cantidad_Vendida", "Precio_Venta_Final", "Costo_Envio", "Tiempo_Entrega"]:
        if col in df0.columns:
            df0[col] = _to_numeric(df0[col])

    # Invalid: future sales (exclude)
    trx_rules = invalid_rules_transacciones()
    mask_future = trx_rules["future_sales"](df0)
    if mask_future.any():
        tmp = df0.loc[mask_future].copy()
        tmp["reason"] = "invalid: future_sales"
        excluded_parts.append(tmp)
        df0 = df0.loc[~mask_future].copy()

    excluded = pd.concat(excluded_parts, ignore_index=True) if excluded_parts else pd.DataFrame()
    log = {
        "dataset": "transacciones",
        "rows_in": int(len(df)),
        "rows_out": int(len(df0)),
        "excluded_rows": int(len(excluded)),
        "notes": "Fecha_Venta parsed to Fecha_Venta_dt; future sales excluded.",
    }
    return df0, excluded, log


def clean_feedback(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    df0 = df.copy()
    excluded_parts = []

    # Transform Ticket_Soporte_Abierto (from revision_data_feedback.ipynb)
    if "Ticket_Soporte_Abierto" in df0.columns:
        df0["Ticket_Soporte_Abierto"] = normalize_yes_no(df0["Ticket_Soporte_Abierto"])

    # Coerce numerics
    for col in ["Rating_Producto", "Rating_Logistica", "Satisfaccion_NPS", "Edad_Cliente"]:
        if col in df0.columns:
            df0[col] = _to_numeric(df0[col])

    # Drop duplicated Transaccion_ID if present (keep first; log excluded)
    if "Transaccion_ID" in df0.columns:
        dup_mask = df0.duplicated(subset=["Transaccion_ID"], keep="first")
        if dup_mask.any():
            tmp = df0.loc[dup_mask].copy()
            tmp["reason"] = "duplicate: Transaccion_ID"
            excluded_parts.append(tmp)
            df0 = df0.loc[~dup_mask].copy()

    # Invalid: impossible ages / NPS out of expected range
    fb_rules = invalid_rules_feedback()
    mask_age = fb_rules["age_impossible"](df0)
    if mask_age.any():
        tmp = df0.loc[mask_age].copy()
        tmp["reason"] = "invalid: age_impossible"
        excluded_parts.append(tmp)
        df0 = df0.loc[~mask_age].copy()

    mask_nps = fb_rules["nps_out_of_range"](df0)
    if mask_nps.any():
        tmp = df0.loc[mask_nps].copy()
        tmp["reason"] = "invalid: nps_out_of_range"
        excluded_parts.append(tmp)
        df0 = df0.loc[~mask_nps].copy()

    excluded = pd.concat(excluded_parts, ignore_index=True) if excluded_parts else pd.DataFrame()
    log = {
        "dataset": "feedback",
        "rows_in": int(len(df)),
        "rows_out": int(len(df0)),
        "excluded_rows": int(len(excluded)),
        "notes": "Ticket_Soporte_Abierto normalized to 0/1; duplicate Transaccion_ID removed; invalid ages/NPS excluded.",
    }
    return df0, excluded, log


def clean_all(raw: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], dict]:
    """
    Cleans all datasets and returns:
      cleaned: dict of cleaned dfs
      report: dict with 'excluded' dfs and 'logs'
    """
    cleaned: Dict[str, pd.DataFrame] = {}
    excluded: Dict[str, pd.DataFrame] = {}
    logs: Dict[str, dict] = {}

    cleaned["inventario"], excluded["inventario"], logs["inventario"] = clean_inventario(raw["inventario"])
    cleaned["transacciones"], excluded["transacciones"], logs["transacciones"] = clean_transacciones(raw["transacciones"])
    cleaned["feedback"], excluded["feedback"], logs["feedback"] = clean_feedback(raw["feedback"])

    report = {"excluded": excluded, "logs": logs}
    return cleaned, report


# -----------------------------
# Auditing helpers for Streamlit
# -----------------------------

AUDIT_CONFIG = {
    "inventario": {
        "critical": ["SKU_ID", "Costo_Unitario_USD", "Stock_Actual"],
        "numeric": ["Costo_Unitario_USD", "Stock_Actual", "Punto_Reorden", "Lead_Time_Dias"],
    },
    "transacciones": {
        "critical": ["Transaccion_ID", "SKU_ID", "Fecha_Venta", "Tiempo_Entrega", "Cantidad_Vendida", "Precio_Venta_Final"],
        "numeric": ["Tiempo_Entrega", "Cantidad_Vendida", "Precio_Venta_Final", "Costo_Envio"],
    },
    "feedback": {
        "critical": ["Transaccion_ID", "Satisfaccion_NPS"],
        "numeric": ["Satisfaccion_NPS", "Edad_Cliente", "Rating_Producto", "Rating_Logistica"],
    },
}


def audit_dataset(df: pd.DataFrame, key: str) -> dict:
    """
    Runs audit_quality for a single dataset key in {'inventario','transacciones','feedback'}
    and returns a dict with summary/nulls/outliers/excluded.
    """
    cfg = AUDIT_CONFIG[key]
    if key == "inventario":
        rules = invalid_rules_inventario()
        name = "Inventario"
    elif key == "transacciones":
        rules = invalid_rules_transacciones()
        name = "Transacciones"
    else:
        rules = invalid_rules_feedback()
        name = "Feedback"

    summary, nulls, outliers, excluded = audit_quality(
        df=df,
        dataset_name=name,
        critical_cols=cfg["critical"],
        numeric_cols=cfg["numeric"],
        invalid_rules=rules,
    )
    return {"summary": summary, "nulls": nulls, "outliers": outliers, "excluded": excluded}


def audit_before_after(raw: Dict[str, pd.DataFrame], cleaned: Dict[str, pd.DataFrame]) -> tuple[dict, dict]:
    """
    Convenience function: run audits for raw and cleaned datasets.
    Returns (aud_before, aud_after)
    """
    before = {k: audit_dataset(raw[k], k) for k in raw.keys()}
    after = {k: audit_dataset(cleaned[k], k) for k in cleaned.keys()}
    return before, after
