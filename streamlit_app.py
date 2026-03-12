import os
import re
from io import BytesIO
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import wikipedia

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Kanana Study Agent Premium",
    page_icon="💛",
    layout="wide"
)

MODEL_NAME = "kakaocorp/kanana-nano-2.1b-instruct"
wikipedia.set_lang("ko")


# --------------------------------------------------
# Config
# --------------------------------------------------
def get_secret_or_default(key: str, default: str) -> str:
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


API_URL = get_secret_or_default("API_URL", "https://YOUR_SPACE_NAME.hf.space")
API_KEY = get_secret_or_default("API_KEY", "local-dev-key")
API_TIMEOUT = int(get_secret_or_default("API_TIMEOUT", "180"))


# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
:root {
    --primary: #6d5efc;
    --primary-soft: #f1efff;
    --primary-deep: #5b4df0;
    --kakao-yellow: #FEE500;
    --kakao-yellow-soft: #FFF6B8;
    --card: #ffffff;
    --text-main: #111827;
    --text-sub: #6b7280;
    --line: #ece8ff;
    --dark-panel: #243648;
    --dark-panel-2: #1f3040;
    --dark-line: #3b5064;
}
.taste-grid-card {
    background: linear-gradient(180deg, #fffef7 0%, #fff8d9 100%);
    border: 1px solid #f4d64f;
    border-radius: 22px;
    padding: 18px 18px 16px 18px;
    box-shadow: 0 10px 24px rgba(254, 229, 0, 0.10);
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: 10px;
}

.taste-grid-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}

.taste-grid-icon {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: #fff3a6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.taste-grid-title {
    font-size: 1.25rem;
    font-weight: 850;
    color: #0f172a;
    line-height: 1.2;
}

.taste-grid-body {
    color: #1f2937;
    font-size: 1rem;
    line-height: 1.7;
    word-break: keep-all;
}

.taste-grid-tag {
    display: inline-block;
    align-self: flex-start;
    margin-top: auto;
    background: #fff3a6;
    color: #5a4500;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 0.78rem;
    font-weight: 800;
}
.block-container {
    padding-top: 4rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8faff 0%, #f2eeff 100%);
    border-right: 1px solid #ece8ff;
}

.sidebar-header {
    background: linear-gradient(135deg, #6d5efc 0%, #8b7cff 100%);
    color: white;
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 12px;
}
.sidebar-header-title {
    font-weight: 800;
    font-size: 1.1rem;
}
.sidebar-header-sub {
    font-size: 0.82rem;
    opacity: 0.92;
    margin-top: 4px;
}
.kakao-pill {
    background: var(--kakao-yellow);
    color: #2b2200;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 800;
    display: inline-block;
    margin-top: 8px;
}
.menu-label {
    font-size: 0.9rem;
    color: #6b7280;
    font-weight: 700;
    margin: 10px 0 8px 2px;
}

.hero-wrap {
    background: linear-gradient(135deg, #6d5efc 0%, #8b7cff 45%, #b7a7ff 100%);
    border-radius: 30px;
    padding: 24px 26px;
    color: white;
    box-shadow: 0 18px 40px rgba(109, 94, 252, 0.20);
    margin-bottom: 18px;
}
.hero-kakao {
    position: absolute;
    top: 18px;
    right: 22px;

    background: #FEE500;
    color: #111;

    padding: 7px 14px;
    border-radius: 999px;

    font-weight: 800;
    font-size: 0.85rem;

    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}
.hero-title {
    font-size: 2.1rem;
    font-weight: 850;
    line-height: 1.2;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 1.02rem;
    opacity: 0.96;
    margin-bottom: 16px;
}
.hero-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.hero-badge {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.20);
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.84rem;
    font-weight: 700;
}
.hero-right-badge {
    display: inline-block;
    background: var(--kakao-yellow);
    color: #2b2200;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.85rem;
    margin-bottom: 12px;
}

.premium-card {
    background: #ffffff;
    border: 1px solid #ebe7ff;
    border-radius: 24px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 16px;
}
.soft-card {
    background: linear-gradient(180deg, #ffffff 0%, #fbfaff 100%);
    border: 1px solid #ece8ff;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
    margin-bottom: 12px;
}
.result-card {
    background: linear-gradient(180deg, #ffffff 0%, #fcfbff 100%);
    border: 1px solid #ece8ff;
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px;
}
.taste-card {
    background: linear-gradient(135deg, #fffef7 0%, #fff8cc 100%);
    border: 1px solid #ffe77c;
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0 8px 18px rgba(254, 229, 0, 0.12);
    margin-bottom: 12px;
    min-height: 180px;
}

.card-title {
    font-size: 1.08rem;
    font-weight: 800;
    color: #111827;
    margin-bottom: 8px;
}
.card-subtitle {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 10px;
}
.section-title {
    font-size: 1.2rem;
    font-weight: 850;
    margin: 6px 0 10px 0;
    color: #111827;
}
.section-desc {
    color: #6b7280;
    margin-bottom: 8px;
    font-size: 0.95rem;
}
.mini-pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.mini-pill {
    background: #f3f0ff;
    color: #4c3dd8;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
}
.yellow-pill {
    background: #FFF6B8;
    color: #5a4500;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 800;
}

.sql-panel {
    background: #243648;
    border: 1px solid #3b5064;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 8px;
}
.sql-header {
    background: #1f3040;
    color: white;
    padding: 14px 18px;
    font-weight: 800;
    border-bottom: 1px solid #3b5064;
}
.sql-body {
    padding: 18px;
    color: #dce7f2;
}
.sql-codehint {
    color: #9fd3ff;
    font-size: 0.88rem;
    margin-top: 6px;
}
.footer-note {
    color: #6b7280;
    font-size: 0.92rem;
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
        max-width: 100% !important;
    }
    .hero-wrap {
        padding: 18px 16px !important;
        border-radius: 20px !important;
    }
    .hero-title {
        font-size: 1.55rem !important;
        line-height: 1.25 !important;
    }
    .hero-sub {
        font-size: 0.95rem !important;
    }
    .hero-kakao {
        position: static !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }
    .premium-card, .soft-card, .result-card, .taste-card, .taste-grid-card, .sql-panel {
        border-radius: 18px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Utility
# --------------------------------------------------
def clean_output(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if "출력" in text:
        text = text.split("출력")[-1].strip(" :\n")
    return text


def build_prompt(instruction: str, input_text: str, output_format: str, example: str | None = None) -> str:
    prompt = f"""
너는 한국어 학습 멘토이자 기술 튜터이다.

규칙
- 반드시 한국어로만 답하라.
- 실무적으로 설명하라.
- 초보자도 이해할 수 있게 설명하라.
- 불필요한 서론 없이 핵심부터 답하라.
- 출력 형식을 최대한 지켜라.

지시
{instruction}
"""

    if example:
        prompt += f"""

예시
{example}
"""

    prompt += f"""

입력
{input_text}

출력 형식
{output_format}

출력
"""
    return prompt


def render_result_textarea(value, height=260, key="result_box"):
    st.text_area(
        "result",
        value=value,
        height=height,
        key=key,
        label_visibility="collapsed"
    )



def get_taste_bundle(subject: str, topic: str):
    if not topic:
        return {
            "concept": "주제를 고르면 한입 맛보기처럼 가볍게 감을 잡을 수 있어요.",
            "metaphor": "주제를 고르면 비유와 함께 감을 잡을 수 있어요.",
            "why": "주제를 고르면 왜 중요한지도 함께 보여드려요."
        }

    taste_map = {
        "JOIN": {
            "concept": "JOIN은 흩어진 테이블을 연결해서 하나의 이야기로 읽게 만드는 방법이에요. 고객 정보와 주문 정보를 이어 붙이듯, 따로 보면 약한 데이터가 함께 볼 때 의미를 가집니다.",
            "metaphor": "JOIN은 서로 다른 퍼즐 조각을 맞춰 한 장면으로 만드는 작업 같아요. 조각 하나만 봐서는 애매하지만, 연결되는 순간 전체 그림이 보입니다.",
            "why": "실무 데이터는 대부분 한 테이블에 다 있지 않아서 JOIN을 모르면 분석이 끊겨요. 결국 ‘연결해서 읽는 능력’이 SQL 실력의 핵심이 됩니다."
        },
        "GROUP BY": {
            "concept": "GROUP BY는 행을 하나씩 보는 대신, 같은 기준끼리 묶어서 패턴을 보는 도구예요. 부서별 평균 급여, 카테고리별 매출처럼 ‘요약’이 필요할 때 쓰입니다.",
            "metaphor": "GROUP BY는 서랍 정리와 비슷해요. 물건을 하나하나 바닥에 펼쳐두는 대신 종류별로 나누면 훨씬 빨리 구조가 보이죠.",
            "why": "데이터 분석은 결국 ‘개별 값’보다 ‘묶음의 특징’을 보는 일이 많아요. GROUP BY를 이해하면 숫자를 모아 의미로 바꾸는 감각이 생깁니다."
        },
        "서브쿼리": {
            "concept": "서브쿼리는 큰 문제를 풀기 전에 작은 문제를 먼저 해결하는 방식이에요. 바깥 쿼리가 기준을 세우기 전에, 안쪽 쿼리가 필요한 값을 미리 구해줍니다.",
            "metaphor": "서브쿼리는 요리 전에 재료 손질을 먼저 해두는 준비 과정 같아요. 본요리를 바로 시작하는 게 아니라, 필요한 재료를 먼저 만들어두는 거죠.",
            "why": "조건이 복잡해질수록 한 문장에 다 우겨 넣기보다 단계를 나누는 게 중요해요. 서브쿼리를 알면 SQL을 더 논리적으로 설계할 수 있습니다."
        },
        "윈도우 함수": {
            "concept": "윈도우 함수는 데이터를 묶되 행 자체를 잃지 않으면서 순위, 누적합, 이전값 비교 같은 계산을 가능하게 해줘요. 요약과 상세를 동시에 보는 도구라고 생각하면 좋아요.",
            "metaphor": "윈도우 함수는 운동 경기 중계 화면 같아요. 선수 한 명 한 명은 그대로 보이는데, 동시에 현재 순위와 기록 비교도 함께 보여주죠.",
            "why": "실무에서는 단순 집계보다 ‘행을 유지한 채 비교’하는 일이 많아요. 윈도우 함수를 이해하면 SQL이 분석 도구로 훨씬 강력해집니다."
        },
        "CTE": {
            "concept": "CTE는 복잡한 쿼리를 이름 붙인 중간 결과로 나눠서 읽기 쉽게 만드는 방식이에요. SQL을 한 번에 해석하기 어렵다면, 단계별로 쪼개서 생각하게 도와줍니다.",
            "metaphor": "CTE는 긴 문장을 문단으로 나눠 쓰는 것과 비슷해요. 내용은 같아도 구조를 나누면 이해가 훨씬 쉬워집니다.",
            "why": "실무 SQL은 길어질수록 ‘맞는 쿼리’보다 ‘읽히는 쿼리’가 더 중요해져요. CTE를 쓰면 유지보수와 협업이 쉬워집니다."
        },
        "NULL 처리": {
            "concept": "NULL 처리는 값이 0인 것과 값이 없는 것을 구분하는 감각이에요. 데이터 분석에서 빠진 값은 단순 빈칸이 아니라 해석을 바꾸는 중요한 신호가 될 수 있어요.",
            "metaphor": "NULL은 답안지에 0점을 적은 게 아니라 아예 답을 안 쓴 상태와 비슷해요. 둘은 결과도, 해석도 완전히 다릅니다.",
            "why": "NULL을 잘못 다루면 평균, 합계, 조건 필터가 전부 틀어질 수 있어요. 정확한 분석을 하려면 값이 없는 상태를 먼저 이해해야 합니다."
        },
        "리스트 컴프리헨션": {
            "concept": "리스트 컴프리헨션은 반복문을 짧고 간결하게 표현하는 파이썬 문법이에요. 같은 일을 더 적은 코드로, 더 읽기 쉽게 만들 수 있습니다.",
            "metaphor": "리스트 컴프리헨션은 장황한 설명 대신 핵심만 담은 메모 같아요. 필요한 내용은 그대로인데 훨씬 빠르게 읽히죠.",
            "why": "파이썬은 단순히 동작만 하는 코드보다 읽기 좋은 코드가 중요해요. 리스트 컴프리헨션을 익히면 코드 스타일이 한 단계 올라갑니다."
        },
        "예외 처리": {
            "concept": "예외 처리는 에러를 없애는 게 아니라, 에러가 나도 프로그램이 덜 망가지게 만드는 장치예요. 실패를 대비하는 코드라고 보면 됩니다.",
            "metaphor": "예외 처리는 자동차 에어백 같아요. 사고를 막진 못해도, 사고가 났을 때 피해를 줄여줍니다.",
            "why": "실무 코드에서는 항상 입력 오류, 파일 누락, 네트워크 문제 같은 변수가 생겨요. 예외 처리를 아는 순간 코드가 훨씬 실전형이 됩니다."
        },
        "클래스": {
            "concept": "클래스는 관련된 데이터와 기능을 하나의 설계도로 묶는 개념이에요. 여러 객체를 같은 구조로 다루고 싶을 때 강력합니다.",
            "metaphor": "클래스는 아파트 설계도와 비슷해요. 설계도 하나로 여러 집을 만들 수 있지만, 각 집은 조금씩 다른 상태를 가질 수 있죠.",
            "why": "규모가 커질수록 변수와 함수만으로는 구조를 관리하기 어려워져요. 클래스를 이해하면 큰 프로그램을 더 체계적으로 다룰 수 있습니다."
        },
        "정규분포": {
            "concept": "정규분포는 값들이 평균 근처에 많이 몰리고 양쪽 끝으로 갈수록 드물어지는 분포예요. 통계에서 가장 자주 등장하는 기본 패턴입니다.",
            "metaphor": "정규분포는 시험 점수에서 중간 점수대 사람이 많고, 아주 높은 점수나 아주 낮은 점수는 적은 상황과 비슷해요.",
            "why": "가설검정, 신뢰구간, 모델링 등 많은 통계 기법이 정규분포 감각 위에서 돌아가요. 이걸 이해하면 통계 전체가 덜 낯설어집니다."
        },
        "가설검정": {
            "concept": "가설검정은 ‘이 차이가 우연인지 아닌지’를 판단하는 절차예요. 직감 대신 기준을 세워서 데이터로 판단하는 방법입니다.",
            "metaphor": "가설검정은 소문을 듣고 바로 믿는 대신, 증거를 모아 사실 여부를 따지는 탐정 작업과 비슷해요.",
            "why": "데이터를 본다고 해서 바로 결론을 내리면 위험해요. 가설검정을 알면 느낌이 아니라 근거로 말할 수 있게 됩니다."
        },
        "로지스틱 회귀": {
            "concept": "로지스틱 회귀는 결과가 ‘예/아니오’, ‘합격/불합격’처럼 범주형일 때 확률을 예측하는 기본 모델이에요.",
            "metaphor": "로지스틱 회귀는 시험 합격 가능성을 점수로 환산해주는 상담 선생님 같아요. 단순히 맞다/틀리다가 아니라 가능성을 알려주죠.",
            "why": "분류 문제의 기초를 이해하려면 로지스틱 회귀가 가장 좋은 출발점이에요. 복잡한 모델을 보기 전에 분류의 사고방식을 익힐 수 있습니다."
        },
        "랜덤포레스트": {
            "concept": "랜덤포레스트는 여러 개의 의사결정나무를 모아 더 안정적인 예측을 만드는 앙상블 모델이에요.",
            "metaphor": "랜덤포레스트는 한 사람의 의견보다 여러 전문가의 다수결을 듣는 방식과 비슷해요. 개별 판단은 흔들려도 함께 보면 더 안정적입니다.",
            "why": "실무에서 강력하면서도 비교적 이해하기 쉬운 모델이라 많이 쓰여요. 앙상블 개념을 배우는 데도 좋은 출발점입니다."
        },
        "퍼셉트론": {
            "concept": "퍼셉트론은 입력값에 가중치를 주고 최종적으로 하나의 판단을 내리는 가장 기초적인 인공신경망 단위예요.",
            "metaphor": "퍼셉트론은 여러 힌트를 점수화해 최종 결정을 내리는 심사위원 같아요. 각 힌트의 중요도가 다르게 반영됩니다.",
            "why": "딥러닝은 복잡해 보여도 결국 작은 판단 단위들이 쌓인 구조예요. 퍼셉트론을 이해하면 신경망의 출발점이 보입니다."
        },
        "CNN": {
            "concept": "CNN은 이미지처럼 공간 구조가 있는 데이터를 잘 처리하도록 만든 신경망이에요. 작은 특징을 잡고 점점 큰 패턴으로 확장해갑니다.",
            "metaphor": "CNN은 사진을 볼 때 전체를 한 번에 보는 게 아니라, 눈·코·입 같은 부분 특징을 먼저 찾고 나중에 얼굴 전체를 인식하는 과정과 비슷해요.",
            "why": "컴퓨터비전의 핵심 개념이라 이미지 AI를 이해하려면 거의 필수예요. 지역 특징을 어떻게 학습하는지 감이 생깁니다."
        },
        "토큰": {
            "concept": "토큰은 LLM이 텍스트를 이해하기 위해 문장을 잘게 나눈 최소 처리 단위예요. 사람이 단어를 보듯, 모델은 토큰을 봅니다.",
            "metaphor": "토큰은 레고 블록 같아요. 긴 문장도 작은 조각으로 나뉘어야 조립하고 이해할 수 있습니다.",
            "why": "LLM이 왜 입력 길이에 제한이 있고, 비용이 왜 토큰 단위로 계산되는지 이해하려면 토큰 개념이 가장 먼저 필요합니다."
        },
        "임베딩": {
            "concept": "임베딩은 텍스트나 데이터를 숫자 벡터로 바꿔서 의미적 유사성을 계산할 수 있게 만드는 표현 방식이에요.",
            "metaphor": "임베딩은 단어에 좌표를 붙여 지도 위에 올리는 것과 비슷해요. 비슷한 의미일수록 가까운 위치에 놓이게 됩니다.",
            "why": "RAG, 검색, 추천, 클러스터링처럼 ‘유사성’이 중요한 AI 시스템 대부분이 임베딩 개념 위에서 움직여요."
        },
        "트랜스포머": {
            "concept": "트랜스포머는 문장 안의 각 단어가 서로 어떤 관계를 가지는지 동시에 살피며 이해하는 구조예요. 현대 LLM의 핵심 뼈대입니다.",
            "metaphor": "트랜스포머는 회의에서 모든 사람의 말을 동시에 듣고 관계를 파악하는 진행자와 같아요. 앞말만 듣는 게 아니라 전체 맥락을 함께 봅니다.",
            "why": "LLM을 이해하고 있다고 말하려면 결국 트랜스포머를 알아야 해요. 지금 생성형 AI의 중심 구조이기 때문입니다."
        },
        "RAG": {
            "concept": "RAG는 LLM이 자기 기억만으로 답하지 않고, 외부 문서를 찾아 참고한 뒤 답하도록 만드는 구조예요.",
            "metaphor": "RAG는 기억에 의존해 대답하는 학생이 아니라, 시험 전에 교과서를 다시 펼쳐보고 답하는 학생과 비슷해요.",
            "why": "최신 정보, 사내 문서, 전문 자료를 반영하려면 RAG가 매우 중요해요. 실무형 LLM 서비스의 핵심 패턴 중 하나입니다."
        },
        "에이전트": {
            "concept": "에이전트는 LLM이 단순히 대답만 하는 게 아니라, 도구를 선택하고 순서를 판단하며 작업을 수행하도록 만든 구조예요.",
            "metaphor": "에이전트는 답만 주는 상담원이 아니라, 필요하면 검색도 하고 계산도 하고 문서도 열어보는 비서와 같아요.",
            "why": "생성형 AI를 ‘채팅’ 수준에서 ‘행동하는 시스템’ 수준으로 확장하려면 에이전트 개념이 중요합니다."
        },
    }

    default_bundle = {
        "concept": f"{topic}는 처음에는 낯설 수 있지만, {subject}를 이해하는 데 꼭 필요한 핵심 개념이에요. 이 개념을 이해하면 전체 흐름을 훨씬 쉽게 따라갈 수 있습니다.",
        "metaphor": f"{topic}는 복잡한 장비라기보다, 익숙해지면 자주 꺼내 쓰는 도구 상자의 핵심 도구와 비슷해요.",
        "why": f"{topic}를 이해하면 {subject}를 단순 암기가 아니라 원리 중심으로 바라볼 수 있게 됩니다."
    }

    return taste_map.get(topic, default_bundle)


def get_wiki_summary(topic: str) -> str:
    if not topic.strip():
        return "검색어를 입력하면 위키피디아 요약을 보여드립니다."
    try:
        return wikipedia.summary(topic, sentences=3, auto_suggest=False)
    except Exception:
        try:
            results = wikipedia.search(topic)
            if results:
                return f"검색 결과 기준 요약 ({results[0]})\n{wikipedia.summary(results[0], sentences=3, auto_suggest=False)}"
            return "위키피디아에서 관련 개념을 찾지 못했습니다."
        except Exception:
            return "위키피디아 요약을 가져오지 못했습니다."




def split_sentences(text: str):
    if not text:
        return []
    parts = re.split(r'(?<=[.!?。])\s+|(?<=다\.)\s+|(?<=요\.)\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def get_concept_from_wikipedia(topic: str) -> str:
    if not topic or not topic.strip():
        return """1. 개념 정의
입력된 개념이 없습니다.

2. 핵심 원리
설명할 개념을 입력해주세요.

3. 쉬운 예시
예: JOIN, 정규분포, 트랜스포머"""

    topic = topic.strip()

    try:
        summary = wikipedia.summary(topic, sentences=3, auto_suggest=False)
        page_title = topic
    except Exception:
        try:
            results = wikipedia.search(topic)
            if not results:
                return f"""1. 개념 정의
'{topic}'에 대한 위키피디아 문서를 찾지 못했습니다.

2. 핵심 원리
검색어를 더 구체적으로 입력해보세요.

3. 쉬운 예시
예: SQL JOIN, 로지스틱 회귀, 트랜스포머"""
            page_title = results[0]
            summary = wikipedia.summary(page_title, sentences=3, auto_suggest=False)
        except Exception:
            return f"""1. 개념 정의
'{topic}'에 대한 설명을 불러오지 못했습니다.

2. 핵심 원리
위키피디아 검색 중 오류가 발생했습니다.

3. 쉬운 예시
조금 더 구체적인 키워드로 다시 입력해보세요."""

    sentences = split_sentences(summary)

    definition = sentences[0] if len(sentences) >= 1 else f"{topic}에 대한 요약을 찾았습니다."
    principle = " ".join(sentences[1:]) if len(sentences) >= 2 else f"{topic}는 관련 분야에서 중요한 개념으로 활용됩니다."
    example = f"예를 들어 '{page_title}'는 실제 학습이나 설명, 문제 풀이에서 핵심 개념으로 자주 등장합니다."

    return f"""1. 개념 정의
{definition}

2. 핵심 원리
{principle}

3. 쉬운 예시
{example}"""


def get_library_explanations(subject, selected_libs, library_map):
    infos = library_map.get(subject, {})
    if not selected_libs:
        return "라이브러리를 선택하면 설명을 보여드립니다."
    lines = []
    for lib in selected_libs:
        if lib in infos:
            lines.append(f"• {lib}: {infos[lib]}")
    return "\n\n".join(lines) if lines else "선택한 라이브러리 설명이 없습니다."


def get_library_code_example(lib_name: str) -> str:
    examples = {
        "pandas": """import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())
print(df.describe())""",
        "numpy": """import numpy as np

arr = np.array([1, 2, 3, 4])
print(arr.mean())""",
        "scikit-learn": """from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)""",
        "transformers": """from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer("Hello world")
print(tokens)""",
    }
    return examples.get(lib_name, f"# {lib_name} 기본 예제\nprint('{lib_name} example')")


# --------------------------------------------------
# API
# --------------------------------------------------
def call_api_generate(prompt: str, max_new_tokens: int = 180) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "max_new_tokens": max_new_tokens
        },
        headers=headers,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()
    return clean_output(data["response"])


@st.cache_data(ttl=20)
def get_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {"status": "offline", "device": "unknown", "model_loaded": False}


# --------------------------------------------------
# Data
# --------------------------------------------------
AI_LIBRARY_INFO = {
    "pandas": "표 형태 데이터 처리, 결측치 처리, 집계, 전처리에 자주 사용됩니다.",
    "numpy": "수치 계산과 배열 연산의 핵심 라이브러리입니다.",
    "scikit-learn": "대표적인 머신러닝 라이브러리입니다.",
    "matplotlib": "기초 시각화 라이브러리입니다.",
    "seaborn": "통계 시각화 라이브러리입니다.",
    "transformers": "트랜스포머 기반 모델을 쉽게 사용할 수 있게 해줍니다.",
    "PyTorch": "유연한 딥러닝 프레임워크입니다.",
    "TensorFlow": "대규모 배포와 생태계가 강한 프레임워크입니다.",
    "langchain": "LLM 애플리케이션과 에이전트 구성을 돕습니다.",
    "streamlit": "AI 웹앱을 빠르게 만들 수 있습니다.",
}
LIBRARY_INFO = {
    "통계": AI_LIBRARY_INFO,
    "ML": AI_LIBRARY_INFO,
    "DL": AI_LIBRARY_INFO,
    "LLM": AI_LIBRARY_INFO,
    "AI": AI_LIBRARY_INFO
}
EXAMPLE_TOPICS = {
    "SQL": ["JOIN", "GROUP BY", "서브쿼리", "윈도우 함수", "CTE", "NULL 처리"],
    "Python": ["리스트 컴프리헨션", "예외 처리", "클래스", "딕셔너리", "반복문", "함수"],
    "통계": ["평균과 분산", "정규분포", "가설검정", "p-value", "회귀분석", "상관계수"],
    "ML": ["로지스틱 회귀", "의사결정나무", "랜덤포레스트", "XGBoost", "과적합", "평가지표"],
    "DL": ["퍼셉트론", "CNN", "RNN", "LSTM", "Backpropagation", "Optimizer"],
    "LLM": ["토큰", "임베딩", "트랜스포머", "어텐션", "RAG", "에이전트"],
    "AI": ["지도학습", "비지도학습", "강화학습", "컴퓨터비전", "NLP", "생성형 AI"]
}
SQL_QUIZ_BANK = [
    {
        "title": "평균 일일 대여 요금 구하기",
        "table": "CAR_RENTAL_COMPANY_CAR",
        "schema": """CAR_ID (INTEGER)
CAR_TYPE (VARCHAR)
DAILY_FEE (INTEGER)
OPTIONS (VARCHAR)""",
        "desc": "CAR_RENTAL_COMPANY_CAR 테이블에서 자동차 종류가 'SUV'인 자동차들의 평균 일일 대여 요금을 출력하세요. 평균 일일 대여 요금은 소수 첫째 자리에서 반올림하고, 컬럼명은 AVERAGE_FEE 로 지정하세요.",
        "answer": """SELECT ROUND(AVG(DAILY_FEE), 0) AS AVERAGE_FEE
FROM CAR_RENTAL_COMPANY_CAR
WHERE CAR_TYPE = 'SUV';""",
        "point": "AVG로 평균을 구하고, ROUND로 반올림합니다. SUV 조건은 WHERE에서 필터링합니다."
    },
    {
        "title": "부서별 직원 수 구하기",
        "table": "EMPLOYEES",
        "schema": """EMP_ID (INTEGER)
EMP_NAME (VARCHAR)
DEPT_ID (INTEGER)
SALARY (INTEGER)""",
        "desc": "EMPLOYEES 테이블에서 부서별 직원 수를 조회하세요. 결과 컬럼은 DEPT_ID, EMP_COUNT 입니다.",
        "answer": """SELECT DEPT_ID, COUNT(*) AS EMP_COUNT
FROM EMPLOYEES
GROUP BY DEPT_ID;""",
        "point": "부서 기준 집계이므로 GROUP BY DEPT_ID와 COUNT(*)를 사용합니다."
    },
    {
        "title": "고액 연봉자 조회",
        "table": "EMPLOYEES",
        "schema": """EMP_ID (INTEGER)
EMP_NAME (VARCHAR)
SALARY (INTEGER)""",
        "desc": "EMPLOYEES 테이블에서 연봉이 5000 이상인 직원의 이름과 연봉을 조회하세요.",
        "answer": """SELECT EMP_NAME, SALARY
FROM EMPLOYEES
WHERE SALARY >= 5000;""",
        "point": "조건에 맞는 행만 조회하므로 WHERE를 사용합니다."
    }
]

# --------------------------------------------------
# LLM functions
# --------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def explain_with_llm(subject, concept):
    concept = (concept or "").strip()
    if not concept:
        return """1. 개념 정의
설명할 개념이 비어 있습니다.

2. 핵심 원리
궁금한 개념을 입력해주세요.

3. 쉬운 예시
예: JOIN, 정규분포, 트랜스포머, CTE"""

    instruction = f"{subject} 학습용 개념을 초보자도 이해할 수 있게 설명하라."
    input_text = f"과목: {subject}\\n개념: {concept}"
    output_format = "1. 개념 정의
2. 핵심 원리
3. 쉬운 예시 또는 예제"
    example = """1. 개념 정의
JOIN은 두 개 이상의 테이블을 공통 컬럼 기준으로 연결해 하나의 결과로 조회하는 SQL 기능이다.

2. 핵심 원리
테이블이 분리되어 저장된 이유는 중복을 줄이고 구조를 명확하게 하기 위해서다. JOIN은 필요한 순간에만 데이터를 연결해 읽게 해준다.

3. 쉬운 예시 또는 예제
예를 들어 회원 테이블과 주문 테이블이 있을 때, 회원 이름과 주문 금액을 함께 보고 싶다면 회원 ID를 기준으로 JOIN한다."""
    prompt = build_prompt(instruction, input_text, output_format, example)
    return call_api_generate(prompt, max_new_tokens=220)


def answer_question_with_llm(subject, question):
    instruction = f"{subject} 관련 질문에 정확하고 쉽게 답하라."
    input_text = f"과목: {subject}\n질문: {question}"
    output_format = "1. 핵심 답변\n2. 이유 또는 원리\n3. 추가 팁"
    prompt = build_prompt(instruction, input_text, output_format)
    return call_api_generate(prompt, max_new_tokens=150)


def solve_python_problem(code_text, error_text, question_text):
    instruction = "파이썬 코드 또는 에러를 보고 수정 가이드와 주요 문법을 설명하라."
    input_text = f"에러 메시지:\n{error_text if error_text else '없음'}\n\n질문:\n{question_text if question_text else '없음'}\n\n코드:\n{code_text if code_text else '없음'}"
    output_format = "1. 문제 원인\n2. 수정 코드\n3. 주요 사용 문법과 학습 포인트"
    prompt = build_prompt(instruction, input_text, output_format)
    return call_api_generate(prompt, max_new_tokens=150)


def generate_practice_problem(subject, topic):
    instruction = f"{subject} 학습용 문제를 만들고 풀이 방향도 간단히 제시하라."
    input_text = f"과목: {subject}\n주제: {topic}"
    output_format = "1. 문제\n2. 문제\n3. 풀이 방향"
    prompt = build_prompt(instruction, input_text, output_format)
    return call_api_generate(prompt, max_new_tokens=150)

# --------------------------------------------------
# Roadmap helpers
# --------------------------------------------------
def period_to_days(period_label: str) -> int:
    return {"7일": 7, "2주": 14, "1달": 30, "3달": 90}.get(period_label, 7)


def generate_roadmap_tasks(domain, period_label):
    days = period_to_days(period_label)
    if days <= 14:
        output_format = "\n".join([f"Day {i}: 학습 내용" for i in range(1, days + 1)])
    elif days == 30:
        output_format = "Week 1: 학습 내용\nWeek 2: 학습 내용\nWeek 3: 학습 내용\nWeek 4: 학습 내용"
    else:
        output_format = "\n".join([f"Week {i}: 학습 내용" for i in range(1, 13)])

    prompt = build_prompt(
        "기간에 맞춰 현실적인 학습 로드맵을 작성하라.",
        f"관심 도메인: {domain}\n기간: {period_label}",
        output_format
    )
    return call_api_generate(prompt, max_new_tokens=520)


def parse_roadmap_to_schedule(roadmap_text: str, period_label: str):
    days = period_to_days(period_label)
    items = []

    for line in roadmap_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            items.append(line.split(":", 1)[1].strip())
        else:
            items.append(line)

    if not items:
        items = ["기초 개념 학습", "예제 실습", "복습"]

    if days <= 14:
        return [(i + 1, items[i % len(items)]) for i in range(days)]
    if days == 30:
        return [(f"Week {i+1}", items[i % len(items)]) for i in range(4)]
    return [(f"Week {i+1}", items[i % len(items)]) for i in range(12)]


def build_calendar_dataframe(schedule, period_label: str):
    today = datetime.today().date()

    if period_label in ["7일", "2주"]:
        rows, current, week_row = [], today, []
        for _, task in schedule:
            week_row.append(f"{current.month}/{current.day}\n{task}")
            if len(week_row) == 7:
                rows.append(week_row)
                week_row = []
            current += timedelta(days=1)
        if week_row:
            while len(week_row) < 7:
                week_row.append("")
            rows.append(week_row)
        return pd.DataFrame(rows, columns=["월", "화", "수", "목", "금", "토", "일"])

    if period_label == "1달":
        rows, current, week_row = [], today, []
        task_idx = 0
        for _ in range(30):
            task = schedule[min(task_idx, len(schedule)-1)][1]
            week_row.append(f"{current.month}/{current.day}\n{task}")
            if len(week_row) == 7:
                rows.append(week_row)
                week_row = []
                task_idx = min(task_idx + 1, len(schedule)-1)
            current += timedelta(days=1)
        if week_row:
            while len(week_row) < 7:
                week_row.append("")
            rows.append(week_row)
        return pd.DataFrame(rows, columns=["월", "화", "수", "목", "금", "토", "일"])

    rows, week_row = [], []
    for label, task in schedule:
        week_row.append(f"{label}\n{task}")
        if len(week_row) == 4:
            rows.append(week_row)
            week_row = []
    if week_row:
        while len(week_row) < 4:
            week_row.append("")
        rows.append(week_row)
    return pd.DataFrame(rows, columns=["1", "2", "3", "4"])


def dataframe_to_image(df: pd.DataFrame, title: str):
    fig, ax = plt.subplots(figsize=(16, max(4, len(df) * 1.4)))
    ax.axis("off")
    tbl = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="left", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 2.4)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf

# --------------------------------------------------
# Quiz Helper
# --------------------------------------------------
def get_current_sql_quiz():
    idx = st.session_state["sql_quiz_index"] % len(SQL_QUIZ_BANK)
    return SQL_QUIZ_BANK[idx]

# --------------------------------------------------
# Session State
# --------------------------------------------------
defaults = {
    "selected_subject": "SQL",
    "selected_example_topic": "",
    "python_code": "",
    "python_error": "",
    "python_question": "",
    "roadmap_result": "",
    "library_search": "",
    "sql_quiz_index": 0,
    "sql_show_answer": False,
    "sql_user_answer": "SELECT",
    "sql_concept": "DATA 가 뭐야",
    "python_concept": "DATA 가 뭐야",
    "통계_concept": "DATA 가 뭐야",
    "ML_concept": "DATA 가 뭐야",
    "DL_concept": "DATA 가 뭐야",
    "LLM_concept": "DATA 가 뭐야",
    "AI_concept": "DATA 가 뭐야"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------
# Sidebar menu
# --------------------------------------------------
menu_items = ["SQL", "Python", "통계", "ML", "DL", "LLM", "AI", "로드맵 생성하기"]

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-header-title">📚 과목선택</div>
        <div class="sidebar-header-sub">원하는 학습 메뉴를 골라보세요</div>
        <div class="kakao-pill">💛 Powered by Kanana</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="menu-label">메뉴</div>', unsafe_allow_html=True)

    for item in menu_items:
        label = f"☑ {item}" if st.session_state["selected_subject"] == item else f"☐ {item}"
        if st.button(label, use_container_width=True, key=f"menu_{item}"):
            st.session_state["selected_subject"] = item
            st.rerun()

    st.markdown("---")
    st.info(f"🤖 모델\n\n{MODEL_NAME}")

subject = st.session_state["selected_subject"]

# --------------------------------------------------
# Hero
# --------------------------------------------------
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-kakao">💛 Kakao LLM</div>
    <div class="hero-title">🎓 Kanana Study Agent Premium</div>
    <div class="hero-sub">
        카카오 LLM 카나나를 활용한 학습 스튜디오입니다. 한줄 맛보기, 개념원리, AI 문제풀기, 튜터에게 질문하기까지 한 화면에서 경험해보세요.
    </div>
    <div class="hero-badges">
        <div class="hero-badge">🧠 한줄 맛보기</div>
        <div class="hero-badge">📘 개념원리</div>
        <div class="hero-badge">🧩 AI 문제풀기</div>
        <div class="hero-badge">💬 튜터에게 질문하기</div>
        <div class="hero-badge">🗓️ 로드맵 생성</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# API health / model status
# --------------------------------------------------
health = get_api_health()
api_status = health.get("status", "offline")
device = health.get("device", "unknown")

a, b, c = st.columns(3)
with a:
    status_text = "카나나 모델 로드 완료" if api_status == "ok" else "API 연결 확인 필요"
    ready_badge = "Ready" if api_status == "ok" else "Offline"
    st.markdown(
        f'<div class="soft-card"><div class="card-title">⚙️ 모델 상태</div><div class="card-subtitle">{status_text}</div><div class="mini-pill-row"><div class="mini-pill">{ready_badge}</div><div class="yellow-pill">Kakao</div></div></div>',
        unsafe_allow_html=True
    )
with b:
    st.markdown(
        f'<div class="soft-card"><div class="card-title">🖥️ 디바이스</div><div class="card-subtitle">{device}</div><div class="mini-pill-row"><div class="mini-pill">Inference</div></div></div>',
        unsafe_allow_html=True
    )
with c:
    st.markdown(
        f'<div class="soft-card"><div class="card-title">📦 모델명</div><div class="card-subtitle">{MODEL_NAME}</div><div class="mini-pill-row"><div class="mini-pill">Kanana</div><div class="yellow-pill">💛 LLM</div></div></div>',
        unsafe_allow_html=True
    )

# --------------------------------------------------
# Common taste section
# --------------------------------------------------
if subject != "로드맵 생성하기":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌟 한줄 맛보기</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">버튼을 누르면 자동 입력 대신, 재미있는 비유가 담긴 한줄 설명을 보여줍니다.</div>', unsafe_allow_html=True)

    topics = EXAMPLE_TOPICS.get(subject, [])
    cols = st.columns(3)

    for i, topic_name in enumerate(topics):
        with cols[i % 3]:
            if st.button(topic_name, key=f"{subject}_taste_{i}", use_container_width=True):
                st.session_state["selected_example_topic"] = topic_name
                if subject == "SQL":
                    st.session_state["sql_concept"] = topic_name
                elif subject == "Python":
                    st.session_state["python_concept"] = topic_name
                elif subject in ["통계", "ML", "DL", "LLM", "AI"]:
                    st.session_state[f"{subject}_concept"] = topic_name
                st.rerun()

    taste_topic = st.session_state["selected_example_topic"]
    col1, col2, col3 = st.columns(3)

taste_bundle = get_taste_bundle(subject, taste_topic)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="taste-grid-card">
        <div class="taste-grid-header">
            <div class="taste-grid-icon">🍯</div>
            <div class="taste-grid-title">한입 개념</div>
        </div>
        <div class="taste-grid-body">{taste_bundle["concept"]}</div>
        <div class="taste-grid-tag">Quick Taste</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="taste-grid-card">
        <div class="taste-grid-header">
            <div class="taste-grid-icon">🎭</div>
            <div class="taste-grid-title">비유</div>
        </div>
        <div class="taste-grid-body">{taste_bundle["metaphor"]}</div>
        <div class="taste-grid-tag">Metaphor</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="taste-grid-card">
        <div class="taste-grid-header">
            <div class="taste-grid-icon">🚀</div>
            <div class="taste-grid-title">왜 배우나</div>
        </div>
        <div class="taste-grid-body">{taste_bundle["why"]}</div>
        <div class="taste-grid-tag">Why It Matters</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# SQL
# --------------------------------------------------
if subject == "SQL":
    st.markdown('<div class="premium-card"><div class="section-title">📘 개념원리</div></div>', unsafe_allow_html=True)

    concept = st.text_input(
        "개념 입력",
        key="sql_concept"
    )

    concept_result = explain_with_llm("SQL", st.session_state["sql_concept"])

    st.markdown('<div class="result-card"><div class="card-title">개념 설명</div></div>', unsafe_allow_html=True)
    render_result_textarea(concept_result, 260, "sql_concept_default")

    st.markdown('<div class="premium-card"><div class="section-title">🧩 AI 문제풀기</div><div class="section-desc">예시 테이블과 스키마를 보고 오른쪽에서 SQL을 직접 작성해보세요.</div></div>', unsafe_allow_html=True)

    quiz = get_current_sql_quiz()
    left, right = st.columns([1.05, 1.2], gap="large")

    with left:
        st.markdown(f"""
        <div class="sql-panel">
            <div class="sql-header">📘 {quiz["title"]}</div>
            <div class="sql-body">
                <h4>문제 설명</h4>
                <p>{quiz["desc"]}</p>
                <h4>예시 테이블</h4>
                <pre>{quiz["table"]}</pre>
                <h4>스키마</h4>
                <pre>{quiz["schema"]}</pre>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sql-panel"><div class="sql-header">solution.sql</div><div class="sql-body">', unsafe_allow_html=True)

        st.session_state["sql_user_answer"] = st.text_area(
            "SQL 작성 영역",
            value=st.session_state["sql_user_answer"],
            height=320,
            key=f"sql_editor_{st.session_state['sql_quiz_index']}",
            label_visibility="collapsed"
        )
        st.markdown('<div class="sql-codehint">-- 여기에 SQL 정답을 작성해보세요</div>', unsafe_allow_html=True)

        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("✅ 정답확인", use_container_width=True):
                st.session_state["sql_show_answer"] = True
        with btn2:
            if st.button("➡️ 다음문제", use_container_width=True):
                st.session_state["sql_quiz_index"] += 1
                st.session_state["sql_show_answer"] = False
                st.session_state["sql_user_answer"] = "SELECT"
                st.rerun()

        st.markdown("---")
        st.markdown("#### 실행 결과")
        if st.session_state["sql_show_answer"]:
            result_text = f"""[정답 SQL]
{quiz["answer"]}

[풀이 포인트]
{quiz["point"]}"""
        else:
            result_text = "실행 결과가 여기에 표시됩니다.\n정답확인을 누르면 정답 SQL과 풀이 포인트가 보입니다."

        st.text_area(
            "실행 결과",
            value=result_text,
            height=180,
            key=f"sql_result_panel_{st.session_state['sql_quiz_index']}",
            label_visibility="collapsed"
        )

        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="premium-card"><div class="section-title">💬 튜터에게 질문하기</div></div>', unsafe_allow_html=True)
    question = st.text_area("SQL 질문 입력", value=st.session_state["selected_example_topic"], height=140)
    if st.button("📨 SQL 질문 답변받기", use_container_width=True):
        try:
            result = answer_question_with_llm("SQL", question)
            st.markdown('<div class="result-card"><div class="card-title">답변</div></div>', unsafe_allow_html=True)
            render_result_textarea(result, 280, "sql_qa_1")
        except Exception as e:
            st.error(f"API 오류: {e}")

# --------------------------------------------------
# Python
# --------------------------------------------------
elif subject == "Python":
    st.markdown('<div class="premium-card"><div class="section-title">📘 개념원리</div></div>', unsafe_allow_html=True)

    concept = st.text_input(
        "개념 입력",
        key="python_concept"
    )

    concept_result = explain_with_llm("Python", st.session_state["python_concept"])

    st.markdown('<div class="result-card"><div class="card-title">개념 설명</div></div>', unsafe_allow_html=True)
    render_result_textarea(concept_result, 260, "python_concept_default")

    st.markdown('<div class="premium-card"><div class="section-title">🧩 AI 문제풀기</div></div>', unsafe_allow_html=True)
    st.session_state["python_code"] = st.text_area("코드 붙여넣기", value=st.session_state["python_code"], height=220)
    st.session_state["python_error"] = st.text_input("에러 메시지 입력", value=st.session_state["python_error"])
    st.session_state["python_question"] = st.text_area("무엇이 이해되지 않는지 설명", value=st.session_state["python_question"], height=120)

    if st.button("✨ Python 코드 가이드 받기", use_container_width=True):
        try:
            result = solve_python_problem(
                st.session_state["python_code"],
                st.session_state["python_error"],
                st.session_state["python_question"]
            )
            st.markdown('<div class="result-card"><div class="card-title">Python 가이드</div></div>', unsafe_allow_html=True)
            render_result_textarea(result, 360, "python_solve_1")
        except Exception as e:
            st.error(f"API 오류: {e}")

    st.markdown('<div class="premium-card"><div class="section-title">💬 튜터에게 질문하기</div></div>', unsafe_allow_html=True)
    question = st.text_area("Python 질문 입력", value=st.session_state["selected_example_topic"], height=140)
    if st.button("📨 Python 질문 답변받기", use_container_width=True):
        try:
            result = answer_question_with_llm("Python", question)
            st.markdown('<div class="result-card"><div class="card-title">답변</div></div>', unsafe_allow_html=True)
            render_result_textarea(result, 280, "python_qa_1")
        except Exception as e:
            st.error(f"API 오류: {e}")

# --------------------------------------------------
# AI-style subjects
# --------------------------------------------------
elif subject in ["통계", "ML", "DL", "LLM", "AI"]:
    st.markdown('<div class="premium-card"><div class="section-title">📘 개념원리</div></div>', unsafe_allow_html=True)

    concept = st.text_input(
        "개념 입력",
        key=f"{subject}_concept"
    )

    concept_result = explain_with_llm(subject, st.session_state[f"{subject}_concept"])

    st.markdown('<div class="result-card"><div class="card-title">개념 설명</div></div>', unsafe_allow_html=True)
    render_result_textarea(concept_result, 260, f"{subject}_concept_default")

    st.markdown('<div class="premium-card"><div class="section-title">🧩 AI 문제풀기</div><div class="section-desc">주요 라이브러리를 고르거나 검색하면 위키피디아 설명과 코드 예제를 함께 보여줍니다.</div></div>', unsafe_allow_html=True)

    all_libs = sorted(list(AI_LIBRARY_INFO.keys()))
    selected_libs = st.multiselect("주요 라이브러리 선택", all_libs, default=all_libs[:5])
    st.session_state["library_search"] = st.text_input("🔎 라이브러리 검색하기", value=st.session_state["library_search"])

    searched = st.session_state["library_search"].strip().lower()
    filtered = [lib for lib in all_libs if searched in lib.lower()] if searched else []
    active_lib = filtered[0] if filtered else (selected_libs[0] if selected_libs else "pandas")

    st.markdown('<div class="result-card"><div class="card-title">🛠️ 라이브러리 설명</div></div>', unsafe_allow_html=True)
    st.markdown(get_library_explanations(subject, selected_libs[:5], LIBRARY_INFO))

    st.markdown('<div class="result-card"><div class="card-title">🌐 위키피디아 검색결과</div></div>', unsafe_allow_html=True)
    st.write(get_wiki_summary(active_lib))

    st.markdown('<div class="result-card"><div class="card-title">💻 코드 활용예제</div></div>', unsafe_allow_html=True)
    st.code(get_library_code_example(active_lib), language="python")

    problem_topic = st.text_area("문제 또는 적용 주제", value=st.session_state["selected_example_topic"], height=150, key=f"{subject}_problem_topic")
    if st.button(f"✨ {subject} 문제풀이 생성", use_container_width=True):
        try:
            result = generate_practice_problem(subject, problem_topic)
            st.markdown('<div class="result-card"><div class="card-title">문제풀이 결과</div></div>', unsafe_allow_html=True)
            render_result_textarea(result, 320, f"{subject}_solve_1")
        except Exception as e:
            st.error(f"API 오류: {e}")

    st.markdown('<div class="premium-card"><div class="section-title">💬 튜터에게 질문하기</div></div>', unsafe_allow_html=True)
    question = st.text_area("질문 입력", value=st.session_state["selected_example_topic"], height=140, key=f"{subject}_question")
    if st.button(f"📨 {subject} 질문 답변받기", use_container_width=True):
        try:
            result = answer_question_with_llm(subject, question)
            st.markdown('<div class="result-card"><div class="card-title">답변</div></div>', unsafe_allow_html=True)
            render_result_textarea(result, 280, f"{subject}_qa_1")
        except Exception as e:
            st.error(f"API 오류: {e}")

# --------------------------------------------------
# Roadmap
# --------------------------------------------------
elif subject == "로드맵 생성하기":
    st.markdown('<div class="premium-card"><div class="section-title">🗓️ 로드맵 생성하기</div><div class="section-desc">기간과 관심도메인을 선택하고 카나나로 학습 캘린더를 생성해보세요.</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        period_label = st.selectbox("기간", ["7일", "2주", "1달", "3달"])
    with c2:
        domain = st.selectbox("관심도메인", ["SQL", "Python", "통계", "ML", "DL", "LLM", "AI", "데이터분석", "MLOps"])

    if st.button("✨ 로드맵 생성하기", use_container_width=True):
        with st.spinner("카나나가 로드맵을 작성하는 중입니다..."):
            try:
                st.session_state["roadmap_result"] = generate_roadmap_tasks(domain, period_label)
            except Exception as e:
                st.error(f"API 오류: {e}")

    if st.session_state["roadmap_result"]:
        schedule = parse_roadmap_to_schedule(st.session_state["roadmap_result"], period_label)
        cal_df = build_calendar_dataframe(schedule, period_label)
        img_buf = dataframe_to_image(cal_df, f"{domain} 학습 로드맵 ({period_label})")

        st.markdown('<div class="result-card"><div class="card-title">📄 로드맵 원문</div></div>', unsafe_allow_html=True)
        render_result_textarea(st.session_state["roadmap_result"], 300, "roadmap_1")

        st.markdown('<div class="result-card"><div class="card-title">🗂️ 표 형태</div></div>', unsafe_allow_html=True)
        st.dataframe(cal_df, use_container_width=True)

        st.markdown('<div class="result-card"><div class="card-title">🖼️ 캘린더 그림</div></div>', unsafe_allow_html=True)
        st.image(img_buf, use_container_width=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown('<div class="footer-note">💜 Made with Kanana · Kakao 💛</div>', unsafe_allow_html=True)
