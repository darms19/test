import streamlit as st
import translators as ts

# Add a title
st.title("翻訳アプリ")

# Add a text area for user input
user_input = st.text_area("翻訳したいテキストを入力してください")

# Language mapping
language_mapping = {
    "English": "en",
    "Japanese": "ja",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh",
    "Korean": "ko",
}

# Add a selectbox for language selection
language_options = list(language_mapping.keys())
selected_language_name = st.selectbox("翻訳先の言語を選択してください", language_options)

# Placeholder for the translated text
translation_placeholder = st.empty()
translation_placeholder.write("翻訳結果はここに表示されます")

# Add a button to trigger translation
if st.button("翻訳実行"):
    if user_input:
        target_language_code = language_mapping[selected_language_name]
        try:
            # Call translate_text
            translated_text = ts.translate_text(
                query_text=user_input,
                translator="google",
                to_language=target_language_code,
            )
            translation_placeholder.write(translated_text)
        except Exception as e:
            st.error(f"翻訳中にエラーが発生しました: {e}")
    else:
        st.warning("翻訳するテキストを入力してください。")

st.markdown("---")  # Add a horizontal rule for separation

# Add usage instructions
st.markdown("## 使い方")
st.markdown(
    """
1. 上のテキストボックスに翻訳したい文章を入力してください。
2. ドロップダウンメニューから翻訳先の言語を選択してください。
3. 「翻訳実行」ボタンをクリックすると、下に翻訳結果が表示されます。
"""
)
