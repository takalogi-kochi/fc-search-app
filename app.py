import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO

st.title("拠点検索アプリ")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# --- PDF 内のリンク注釈と周囲テキストから拠点名を抽出 ---
for page in doc:
    links = page.get_links()
    blocks = page.get_text("blocks")

    for link in links:
        if "uri" not in link:
            continue

        uri = link["uri"]
        lx0, ly0, lx1, ly1 = link["from"]
        link_center = ((lx0 + lx1) / 2, (ly0 + ly1) / 2)

        # まず注釈からテキストを取得
        annot_text = ""
        annots = page.annots()
        if annots:
            for annot in annots:
                if annot.rect.intersects(fitz.Rect(lx0, ly0, lx1, ly1)):
                    annot_text = annot.info.get("content", "").strip()

        # 注釈にテキストが無い場合は、周囲テキストから最も近いものを取得
        nearest_text = None
        nearest_dist = 999999

        for block in blocks:
            bx0, by0, bx1, by1, text, *_ = block
            text_center = ((bx0 + bx1) / 2, (by0 + by1) / 2)

            dist = abs(text_center[0] - link_center[0]) + abs(text_center[1] - link_center[1])

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_text = text.strip()

        # 最終的な拠点名
        key = annot_text if annot_text else nearest_text

        if key:
            base_points[key] = uri

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
