import streamlit as st
import pandas as pd
import textwrap

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL (CSS - TILES MODERNOS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    .block-container {padding-top: 2rem;}

    /* --- CONTAINER DO CARD --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0px !important;
        transition: transform 0.2s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    /* --- HEADER --- */
    .tile-header {
        padding: 15px 15px 10px 15px;
    }
    .tile-title {
        color: white;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 700;
        font-size: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }
    .tile-sub {
        color: #8b949e;
        font-size: 0.75rem;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- DATA STRIP --- */
    .data-strip {
        background-color: #0d1117;
        border-top: 1px solid #21262d;
        border-bottom: 1px solid #21262d;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .data-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 25%;
    }
    .data-col:not(:last-child) {
        border-right: 1px solid #30363d;
    }
    .data-lbl {
        font-size: 0.6rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .data-val {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e6edf3;
        font-family: "Source Sans Pro", sans-serif;
    }

    /* --- FOOTER --- */
    .tile-footer {
        padding: 10px 15px;
    }
    .progress-track {
        background-color: #21262d;
        height: 4px;
        border-radius: 2px;
        width: 100%;
        margin-bottom: 10px;
        overflow: hidden;
    }
    .progress-fill { height: 100%; border-radius: 2px; }

    .footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 20px;
    }

    .badge-status {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
        line-height: 1.2;
    }

    .footer-pct {
        font-size: 0.8rem;
        font-weight: 700;
        font-family: "Source Sans Pro", sans-serif;
        line-height: 1;
        display: flex;
        align-items: center;
    }

    /* --- BOTÃO (REDUZIDO) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent;
        color: #58a6ff;
        border: 1px solid transparent;
        border-radius: 4px;

        font-size: 0.65rem;   /* ↓ menor */
        padding: 2px 6px;     /* ↓ menor */
        height: auto;
        min-height: 0px;
        line-height: 1.1;
        margin: 0;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #1f242c;
        border-color: #30363d;
        text-de
