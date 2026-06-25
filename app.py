import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO

st.title("拠点検索")

PDF_URL = "https://m.media-amazon.com/images/G/09/vendor/RC/FC_List_Operating_hours.pdf"

# --- PDF を URL から自動取得 ---
response = requests.get(PDF_URL)
pdf_bytes = BytesIO(response.content)

doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")

base_points = {}

# --- PDF 内の URL を抽出 ---
for page_num, page in enumerate(doc):
    links = page.get_links()
    text_blocks = page.get_text("blocks")

    for link in links:
        if "uri" in link:  # 外部PDF URL
            x0, y0, x1, y1 = link["from"]

            # クリック領域に重なるテキストを探す
            for block in text_blocks:
                bx0, by0, bx1, by1, text, *_ = block
                if (bx0 >= x0 and by0 >= y0 and bx1 <= x1 and by1 <= y1):
                    key = text.strip()
                    base_points[key] = link["uri"]

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

    # PDFを埋め込み表示
    st.components.v1.iframe(url, height=600)
