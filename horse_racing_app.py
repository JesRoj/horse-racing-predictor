import streamlit as st
from datetime import datetime
import re, io, math
from pypdf import PdfReader

st.set_page_config(page_title="🐎 Expert Racing Predictor", page_icon="🐎")
st.title("🐎 Expert Racing Predictor – Top-1 % Handicapper Model")
st.write("Upload a racing PDF/TXT/CSV and receive a full quantitative report.")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is not None:
    # ---------- OCR ----------
    try:
        from pytesseract import image_to_string
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(uploaded_file.read())
        text = "\n".join(image_to_string(img, lang='eng') for img in images)
    except Exception as e:
        st.error("OCR failed → " + str(e))
        st.stop()

    if not text.strip():
        st.error("No readable text found – try an OCR’d or text-based file.")
        st.stop()
    st.success(f"Extracted {len(text)} characters")

    # ---------- horse grab (same regex you already had) ----------
    seen = set()
    horses = []
    for line in text.splitlines():
        m = re.search(
            r'(?:^|\s)(1?\d)\s+([A-Z][A-Z0-9ÁÉÍÓÚÜÑáéíóúüñ\ \(\)\-]{4,}?(?:\s+[A-Z][a-z]*){0,2})(?=\s+[A-Z][a-z]+\s+[A-Z][a-z]|\s+\d)',
            line, re.I)
        if not m:
            continue
        post, name = m.groups()
        post = int(post)
        name = name.strip()
        if 1 <= post <= 20 and name.lower() not in seen:
            seen.add(name.lower())
            horses.append({"post": post, "name": name})

    # ---------- expert model ----------
    if st.button("🔮 Predict race", type="primary"):
        def try_float(x, default=0.0):
            try:
                return float(x)
            except (ValueError, TypeError):
                return default

        # 1. universal extractor
        for h in horses:
            line = next((l for l in text.splitlines() if h["name"] in l), "")
            finishes = [int(n) for n in re.findall(r'\b([1-9]|1\d|20)\b', line)]
            h["avg_finish"] = sum(finishes[:3]) / 3 if finishes else 5.0
            h["runs"] = len(finishes)
            h["wins"] = finishes.count(1)

            speed_figs = [try_float(n) for n in re.findall(r'(\d{2,3})\s*mts?', line)]
            h["avg_speed"] = sum(speed_figs) / len(speed_figs) if speed_figs else 70.0

            weight = re.search(r'(\d{2,3})\s*kg', line)
            h["weight"] = try_float(weight.group(1)) if weight else 54.0

            days_off = re.search(r'(\d+)\s*d[ií]as?', line)
            h["days_off"] = int(days_off.group(1)) if days_off else 28

            post = re.search(r'PP\s*(\d+)', line)
            h["post"] = int(post.group(1)) if post else h["post"]

            odds = re.search(r'(\d+\.?\d*)\s*(?:/1)?\s*cps?', line)
            h["market_odds"] = try_float(odds.group(1)) if odds else None

            jockey_pct = re.search(r'(\d+)%\s*$', line)
h["jockey_pct"] = float(jockey_pct.group(1)) if jockey_pct else 12.0

            trainer_pct = re.findall(r'(\d+)%', line)
            h["trainer_pct"] = try_float(trainer_pct[1]) if len(trainer_pct) > 1 else 10.0

            h["class_drop"] = bool(re.search(r'\b(drop|baja)\b', line, re.I))

            if "fast" in line.lower() or "rápida" in line.lower():
                h["track"] = "fast"
            elif "good" in line.lower() or "buena" in line.lower():
                h["track"] = "good"
            elif "muddy" in line.lower() or "pesada" in line.lower():
                h["track"] = "muddy"
            else:
                h["track"] = "fast"

        # 2. composite score
        def composite(h):
            finish_score = max(0, 100 - h["avg_finish"] * 8)
            speed_score = max(0, 100 - abs(h["avg_speed"] - 65) * 2)
            weight_score = max(0, 100 - abs(h["weight"] - 54) * 3)
            rest_score = max(0, 100 - abs(h["days_off"] - 21) * 2)
            post_score = max(0, 100 - abs(h["post"] - 4) * 5)
            jockey_score = h["jockey_pct"] * 8
            trainer_score = h["trainer_pct"] * 8
            drop_bonus = 10 if h["class_drop"] else 0
            track_bonus = 5 if h["track"] == "fast" else 0
            total = (finish_score * 0.35 + speed_score * 0.20 + weight_score * 0.10 +
                     rest_score * 0.10 + post_score * 0.10 + jockey_score * 0.08 +
                     trainer_score * 0.07 + drop_bonus + track_bonus)
            return max(0, min(100, total))

        for h in horses:
            h["prob"] = round(composite(h), 1)

        ranked = sorted(horses, key=lambda x: x["prob"], reverse=True)
        top5 = ranked[:5]

        # 3. table
        st.markdown("### 🏆 Top 5 win probabilities (expert model)")
        df = {"Horse": [], "Win Prob %": [], "Fair Odds": [], "Market Odds": [], "Edge": [], "Key Evidence": []}
        for h in top5:
            fair_odds = round(max(1.01, (100 - h["prob"]) / h["prob"]), 2) if h["prob"] else 999
            market = h.get("market_odds") or "-"
            edge = "" if market == "-" else f"{round(fair_odds - market, 1)} ✅" if fair_odds > market + 0.5 else "no value"
            ev = []
            if h["avg_finish"] <= 3:
                ev.append(f"avg finish {h['avg_finish']:.1f}")
            if h["wins"]:
                ev.append(f"{h['wins']} wins last {h['runs']}")
            if h["class_drop"]:
                ev.append("class drop")
            if h["jockey_pct"] >= 15:
                ev.append(f"jockey {h['jockey_pct']}%")
            if h["days_off"] in range(14, 35):
                ev.append("ideal rest")
            df["Horse"].append(h["name"])
            df["Win Prob %"].append(f"{h['prob']}%")
            df["Fair Odds"].append(str(fair_odds))
            df["Market Odds"].append(str(market))
            df["Edge"].append(edge)
            df["Key Evidence"].append(" | ".join(ev) or "solid fundamentals")
        st.dataframe(df)

        # 4. best bet
        best = None
        for h in top5:
            if h.get("market_odds") and (100 / h["prob"] - 1) - h["market_odds"] >= 0.05:
                best = h
                break
        if best:
            st.markdown("### 🎯 Recommended WIN bet")
            st.success(f"**{best['name']}**  –  win probability **{best['prob']}%**, "
                       f"fair odds **{(100 - best['prob']) / best['prob']:.1f}**, "
                       f"market **{best['market_odds']}**  →  **edge ≥ 5 %**")
        else:
            st.info("No horse shows ≥ 5 % edge vs. market; consider passing the race.")

        # 5. CSV
        csv_lines = ["Rank,Horse,Post,WinProb%,FairOdds"]
        for i, h in enumerate(ranked, 1):
            fair = round(max(1.01, (100 - h["prob"]) / h["prob"]), 2)
            csv_lines.append(f"{i},{h['name']},{h['post']},{h['prob']},{fair}")
        csv_str = "\n".join(csv_lines)
        st.download_button(
            label="📥 Download full expert model CSV",
            data=csv_str,
            file_name=f"expert_pred_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv"
        )

