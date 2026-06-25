import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
import re

st.title("拠点検索アプリ")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# 拠点名の形式（例：HND3, KIX2, NGO5）
pattern = re.compile(r"^[A-Z]{2,4}\d{1,2}$")

# --- PDF 全ページから拠点名リンクだけを抽出 ---
for page in doc:
    links = page.get_links()
    blocks = page.get_text("blocks")

    # 拠点名リンクのY座標帯を推定（左端のリンクのY位置はほぼ一定）
    y_positions = [link["from"][1] for link in links if "uri" in link]
    if not y_positions:
        continue

    # 拠点名リンクのY帯（最も密集している帯を抽出）
    y_min = min(y_positions)
    y_max = max(y_positions)

    for link in links:
        if "uri" not in link:
            continue

        uri = link["uri"]

        # mailto: は除外
        if uri.startswith("mailto:"):
            continue

        x0, y0, x1, y1 = link["from"]

        # 拠点名リンクは「縦に密集」している → Y座標帯で判定
        if not (y_min <= y0 <= y_max):
            continue

        # 周囲テキストから最も近いものを取得
        nearest_text = None
        nearest_dist = 999999

        link_center = ((x0 + x1) / 2, (y0 + y1) / 2)

        for block in blocks:
            bx0, by0, bx1, by1, text, *_ = block
            text_center = ((bx0 + bx1) / 2, (by0 + by1) / 2)

            dist = abs(text_center[0] - link_center[0]) + abs(text_center[1] - link_center[1])

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_text = text.strip()

        # 正規表現で拠点名だけ抽出
        if nearest_text:
            candidate = nearest_text.split()[0]
            if pattern.match(candidate):
                base_points[candidate] = uri

# --- 検索窓 ---
keyword = st.text_input("拠点名を検索")

# --- 絞り込み ---
filtered_keys = [k for k in base_points.keys() if keyword.lower() in k.lower()]

# --- 拠点一覧 ---
selected = st.selectbox("拠点を選択", filtered_keys)

# --- 選択された拠点の情報を表示 ---
if selected:
    url = base_points[selected]

    st.subheader(f"{selected} のPDF")
    st.markdown(f"[PDFを開く]({url})")

    st.components.v1.iframe(url, height=600)
