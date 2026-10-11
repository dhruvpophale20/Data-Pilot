"""Standalone page for exporting a dataset with only user-selected columns."""

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from app_pages.prewarming import get_excel_sheet_names, load_uploaded_dataset


def column_selection_page() -> None:
    """Let users independently upload a file and choose columns to retain."""
    st.title("🧩 Select Dataset Columns")
    st.caption(
        "Upload a dataset, choose the columns to keep, and download the result. "
        "This page works independently of the analysis and preprocessing pipeline."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        key="column_selection_file",
    )
    if uploaded_file is None:
        st.info("Upload a CSV or Excel file to choose its columns.")
        return

    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    extension = Path(uploaded_file.name).suffix.lower()
    sheet_name = None
    if extension in {".xlsx", ".xls"}:
        try:
            sheets = get_excel_sheet_names(file_bytes)
        except Exception as exc:
            st.error(f"Could not read workbook sheets: {exc}")
            return
        if not sheets:
            st.error("This workbook does not contain any worksheets.")
            return
        sheet_name = st.selectbox(
            "Worksheet",
            sheets,
            key=f"column_selection_sheet_{file_hash}",
        )

    try:
        df = load_uploaded_dataset(file_bytes, uploaded_file.name, sheet_name)
    except Exception as exc:
        st.error(f"Could not load dataset: {exc}")
        return

    st.write(f"**Source:** {uploaded_file.name} · **Shape:** {len(df):,} rows × {len(df.columns):,} columns")
    selected_columns = st.multiselect(
        "Columns to keep",
        options=list(df.columns),
        default=list(df.columns),
        key=f"column_selection_columns_{file_hash}_{sheet_name or 'csv'}",
        help="Clear the columns you want to remove. The source dataset is not modified.",
    )

    if not selected_columns:
        st.warning("Select at least one column to prepare a download.")
        return

    result = df.loc[:, selected_columns]
    st.caption(f"Preview: {len(result):,} rows × {len(result.columns):,} columns")
    st.dataframe(result.head(100), hide_index=True, width="stretch")

    stem = Path(uploaded_file.name).stem
    download_name = f"{stem}_selected_columns.csv"
    st.download_button(
        "Download selected columns as CSV",
        data=result.to_csv(index=False).encode("utf-8-sig"),
        file_name=download_name,
        mime="text/csv",
        type="primary",
        use_container_width=True,
        key=f"column_selection_download_{file_hash}_{sheet_name or 'csv'}",
    )
