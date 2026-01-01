import streamlit as st
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count

st.set_page_config(page_title="Lowest Payout Pick-3", layout="centered")

st.title("🎯 Pick-3 Lowest Payout Analyzer")
st.write("Digits 0–9 | Duplicates Allowed | Straight / Rumble / Chance")

# ---------------------------
# PAYOUT TABLE
# ---------------------------
STRAIGHT_3 = 2950
RUMBLE_3 = 1000
CHANCE_PAYOUT = {1: 30, 2: 120, 3: 1200}

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    tickets = np.array([list(map(int, str(x).split(","))) for x in df.iloc[:, 0]], dtype=np.int8)
    categories = np.array([str(x).strip().lower() for x in df.iloc[:, 1]])

    straight_tickets = tickets[categories == "straight"]
    rumble_tickets = np.sort(tickets[categories == "rumble"], axis=1)
    chance_tickets = tickets[categories == "chance"]

    all_results = np.array(
        np.meshgrid(np.arange(10), np.arange(10), np.arange(10))
    ).T.reshape(-1, 3).astype(np.int8)

    def evaluate_result(result):
        total = 0

        if straight_tickets.size:
            total += np.all(straight_tickets == result, axis=1).sum() * STRAIGHT_3

        if rumble_tickets.size:
            total += np.all(rumble_tickets == np.sort(result), axis=1).sum() * RUMBLE_3

        if chance_tickets.size:
            right_match = chance_tickets[:, ::-1] == result[::-1]
            match_count = right_match.cumsum(axis=1).max(axis=1)
            for k, v in CHANCE_PAYOUT.items():
                total += np.sum(match_count == k) * v

        return (tuple(result.tolist()), total)

    if st.button("🚀 Calculate Lowest Payouts"):
        with st.spinner("Processing combinations..."):
            with Pool(cpu_count()) as pool:
                payouts = pool.map(evaluate_result, all_results)

        payouts.sort(key=lambda x: x[1])
        top_20 = payouts[:20]

        st.success("✅ Calculation Complete")

        result_df = pd.DataFrame(top_20, columns=["Combination", "]()
