import streamlit as st
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Pick-3 Lowest Payout Analyzer", layout="centered")

st.title("🎯 Pick-3 Lowest Payout Analyzer")
st.caption("Digits 0–9 | Duplicates Allowed | Straight • Rumble • Chance")

# ---------------------------
# PAYOUT TABLE
# ---------------------------
STRAIGHT_3 = 2950
RUMBLE_3 = 1000
CHANCE_PAYOUT = {1: 30, 2: 120, 3: 1200}

# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:

    # ---------------------------
    # LOAD DATA
    # ---------------------------
    df = pd.read_excel(uploaded_file)

    tickets = np.array(
        [list(map(int, str(x).split(","))) for x in df.iloc[:, 0]],
        dtype=np.int8
    )

    categories = np.array(
        [str(x).strip().lower() for x in df.iloc[:, 1]]
    )

    straight_tickets = tickets[categories == "straight"]
    rumble_tickets = np.sort(tickets[categories == "rumble"], axis=1)
    chance_tickets = tickets[categories == "chance"]

    # ---------------------------
    # ALL PICK-3 COMBINATIONS
    # ---------------------------
    all_results = np.array(
        np.meshgrid(np.arange(10), np.arange(10), np.arange(10))
    ).T.reshape(-1, 3).astype(np.int8)

    # ---------------------------
    # WORKER FUNCTION
    # ---------------------------
    def evaluate_result(result):
        total = 0

        # STRAIGHT
        if straight_tickets.size > 0:
            total += np.all(
                straight_tickets == result, axis=1
            ).sum() * STRAIGHT_3

        # RUMBLE
        if rumble_tickets.size > 0:
            total += np.all(
                rumble_tickets == np.sort(result), axis=1
            ).sum() * RUMBLE_3

        # CHANCE (RIGHT MATCH)
        if chance_tickets.size > 0:
            right_match = chance_tickets[:, ::-1] == result[::-1]
            match_count = right_match.cumsum(axis=1).max(axis=1)

            for k, v in CHANCE_PAYOUT.items():
                total += np.sum(match_count == k) * v

        return tuple(result.tolist()), total

    # ---------------------------
    # RUN BUTTON
    # ---------------------------
    if st.button("🚀 Calculate Lowest Payouts"):

        with st.spinner("Processing 1,000 combinations..."):

            with Pool(cpu_count()) as pool:
                payouts = pool.map(evaluate_result, all_results)

        payouts.sort(key=lambda x: x[1])
        top_20 = payouts[:20]

        # ---------------------------
        # DISPLAY RESULTS
        # ---------------------------
        result_df = pd.DataFrame(
            top_20,
            columns=["Combination", "Total Payout"]
        )

        st.success("✅ Calculation Complete")
        st.dataframe(result_df, use_container_width=True)

        # ---------------------------
        # DOWNLOAD BUTTON
        # ---------------------------
        st.download_button(
            "⬇️ Download Results",
            result_df.to_csv(index=False),
            file_name="lowest_payout_pick3.csv",
            mime="text/csv"
        )
