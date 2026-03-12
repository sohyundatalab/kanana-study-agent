import streamlit as st
import requests

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="Kanana Study Agent",
    layout="wide"
)

st.title("📚 Kanana Study Agent")

# -----------------------------
# API 설정
# -----------------------------
API_URL = st.secrets.get("API_URL", "")
API_KEY = st.secrets.get("API_KEY", "")


# -----------------------------
# API 호출 함수
# -----------------------------
def call_api_generate(prompt, max_new_tokens=200):

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "prompt": prompt,
        "max_new_tokens": max_new_tokens
    }

    try:
        res = requests.post(
            f"{API_URL}/generate",
            headers=headers,
            json=payload,
            timeout=120
        )

        if res.status_code != 200:
            return f"API 오류: {res.text}"

        data = res.json()

        if "response" in data:
            return data["response"]

        return str(data)

    except Exception as e:
        return f"API 호출 실패: {e}"


# -----------------------------
# LLM 개념 설명 함수
# -----------------------------
def explain_with_llm(subject, concept):

    instruction = f"{subject} 개념을 학습자가 이해하기 쉽게 설명하라."

    input_text = f"과목: {subject}\n개념: {concept}"

    output_format = (
        "1. 개념 정의\n"
        "2. 핵심 원리\n"
        "3. 쉬운 예시"
    )

    prompt = (
        f"{instruction}\n\n"
        f"{input_text}\n\n"
        f"다음 형식으로 설명하라.\n\n"
        f"{output_format}"
    )

    return call_api_generate(prompt, max_new_tokens=250)


# -----------------------------
# 과목 선택
# -----------------------------
subject = st.selectbox(
    "과목 선택",
    ["SQL", "Python", "통계", "ML", "DL", "LLM", "AI"]
)


# -----------------------------
# 개념 입력
# -----------------------------
concept = st.text_input(
    "개념 입력",
    placeholder="예: JOIN, 정규분포, 트랜스포머"
)


# -----------------------------
# 실행 버튼
# -----------------------------
if st.button("개념 설명 보기"):

    if concept.strip() == "":
        st.warning("개념을 입력해주세요.")
    else:

        with st.spinner("카카오 LLM이 설명 생성중..."):

            result = explain_with_llm(subject, concept)

            st.markdown("---")
            st.markdown(result)
