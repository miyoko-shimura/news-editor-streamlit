import streamlit as st
import google.generativeai as genai
from google.api_core import retry
import PyPDF2
from docx import Document

# 記事の文体リスト (より一般的なスタイル)
styles = ["ですます調", "である調", "ニュースレポート", "カジュアル", "フォーマル", "その他（自由入力）"]

st.set_page_config(page_title="多言語文章生成アプリ", layout="wide")
st.title("📰 多言語文章生成アプリ")

# サイドバーでAPIキーを入力
with st.sidebar:
    st.header("Gemini API 設定")
    api_key = st.text_input("Gemini API キーを入力", type="password")
    
    if api_key:
        # Gemini APIの設定
        genai.configure(api_key=api_key)
    else:
        st.warning("APIキーを入力してください。")

# ファイルアップローダーを一番上に配置
uploaded_file = st.file_uploader("ファイルをアップロード", type=["txt", "pdf", "docx"])

# 記事設定をメインに配置
st.header("記事設定")
writing_style = st.selectbox("記事の文体を選択", styles)
if writing_style == "その他（自由入力）":
    writing_style = st.text_input("文体を入力してください")

word_count = st.number_input("目標文字数", min_value=100, max_value=1000, value=300, step=50)

# 言語の選択肢と言語コードのマッピング
language_options = {
    "日本語": "Japanese",
    "English": "English",
    "中文 (简体)": "Simplified Chinese",
    "中文 (繁體)": "Traditional Chinese",
    "한국어": "Korean",
    "Português": "Portuguese",
    "Tagalog": "Tagalog"
}
selected_language = st.selectbox("言語を選択", list(language_options.keys()))

def read_file_content(file):
    if file.type == "text/plain":
        return file.getvalue().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        st.error("Unsupported file type")
        return None

if uploaded_file is not None and api_key:
    # ファイルの内容を読み込む
    file_contents = read_file_content(uploaded_file)
    if file_contents:
        st.write("ファイルが正常にアップロードされました。")

        if st.button("記事を生成"):
            with st.spinner("記事を生成中..."):
                prompt = f"""
                Task: Summarize the following content into an article.
                Style: {writing_style}
                Target word count: Approximately {word_count} words
                Language: {language_options[selected_language]}

                Important: The entire output must be in {language_options[selected_language]}.

                Content to summarize:
                {file_contents}

                Please generate the article now:
                """

                # Gemini APIを使用して記事を生成
                @retry.Retry()
                def generate_article():
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    return response.text

                try:
                    generated_article = generate_article()
                    st.subheader("生成された記事")
                    st.markdown(generated_article)
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")

elif not api_key:
    st.warning("サイドバーからGemini APIキーを入力してください。")
else:
    st.info("記事を生成するには、まずファイルをアップロードしてください。")