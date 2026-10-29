import os
import platform
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import numpy as np
import pandas as pd
import streamlit as st
from wordcloud import WordCloud
from kiwipiepy import Kiwi

# ========================================================
# 0. 한글 폰트 설정 및 초기화 (속도 최적화 + addfont 직접 등록)
# ========================================================


@st.cache_resource
def init_korean_font():
    font_filename = "NanumGothic.ttf"

    # 절대 경로 확보
    if "__file__" in globals():
        font_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), font_filename
        )
    else:
        font_path = os.path.abspath(font_filename)

    # 1. NanumGothic.ttf 파일이 존재하는 경우 Matplotlib에 직접 등록
    if os.path.exists(font_path):
        font_manager.fontManager.addfont(font_path)
        font_prop = font_manager.FontProperties(fname=font_path)
        font_name = font_prop.get_name()

        rc("font", family=font_name)
        plt.rcParams["axes.unicode_minus"] = False
        return font_path

    # 2. 파일이 없는 경우 OS 기본 폰트로 대체 (깨짐 방지)
    system_os = platform.system()
    if system_os == "Windows":
        rc("font", family="Malgun Gothic")
        font_path = "C:/Windows/Fonts/malgun.ttf"
    elif system_os == "Darwin":  # macOS
        rc("font", family="AppleGothic")
        font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    else:  # Linux / Streamlit Cloud 등
        rc("font", family="NanumGothic")
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

    plt.rcParams["axes.unicode_minus"] = False
    return font_path


@st.cache_resource
def load_kiwi():
    """Kiwi 형태소 분석기를 1회만 로드하도록 캐싱합니다."""
    return Kiwi()


# 캐시된 폰트 및 Kiwi 객체 로드
font_path = init_korean_font()
kiwi = load_kiwi()

# 긍정 / 부정 감성 어휘 사전 정의
POSITIVE_WORDS = {
    "좋다",
    "좋음",
    "만족",
    "유익",
    "추천",
    "최고",
    "재미",
    "재밌다",
    "훌륭",
    "알참",
    "도움",
    "친절",
    "쾌적",
    "성장",
    "보람",
}
NEGATIVE_WORDS = {
    "아쉽다",
    "아쉬움",
    "부족",
    "힘들다",
    "힘듦",
    "불만",
    "최악",
    "별로",
    "어렵다",
    "복잡",
    "피곤",
    "지루",
    "부담",
    "불편",
    "개선",
}


# ========================================================
# 1. 웹페이지 기본 설정 및 제목
# ========================================================
st.set_page_config(page_title="학과별 생활 습관 분석", layout="wide")
st.title("🎓 학과별 학생 생활 습관 및 만족도 분석 웹")
st.write(
    "학생들의 생활 습관, 만족도, 한 줄 의견 데이터를 분석하는 웹페이지입니다."
)

st.divider()

# ========================================================
# 2. CSV 파일 업로드
# ========================================================
st.header("1. 데이터 파일 업로드")
uploaded_file = st.file_uploader("분석할 CSV 파일을 업로드하세요.", type=["csv"])

if uploaded_file is not None:
    # 데이터 불러오기
    df_raw = pd.read_csv(uploaded_file)

    # 열 이름의 양쪽 공백 제거
    df_raw.columns = df_raw.columns.str.strip()

    # 필수 분석 열 지정
    required_cols = ["학과", "공부시간", "수면시간", "스마트폰", "만족도", "한줄의견"]

    # 열 이름 존재 여부 검사
    missing_cols = [col for col in required_cols if col not in df_raw.columns]

    if missing_cols:
        st.error(
            f"❌ CSV 파일에서 다음 열을 찾지 못했습니다: **{', '.join(missing_cols)}**"
        )
        st.info(f"💡 현재 업로드한 CSV의 열 목록: `{list(df_raw.columns)}`")
    else:
        # 3. 데이터 전처리 및 결과 표시
        st.header("2. 데이터 전처리 결과")

        initial_count = len(df_raw)

        # 결측치 제거
        df_clean = df_raw.dropna(subset=required_cols).copy()

        # 숫자형 데이터 변환
        num_cols = ["공부시간", "수면시간", "스마트폰", "만족도"]
        for col in num_cols:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        df_clean = df_clean.dropna(subset=num_cols)

        final_count = len(df_clean)
        removed_count = initial_count - final_count

        # 처리 결과 화면 출력
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("전체 데이터 수", f"{initial_count} 건")
        col_info2.metric(
            "제외된 잘못된 데이터",
            f"{removed_count} 건",
            delta_color="inverse",
        )
        col_info3.metric("최종 분석 데이터", f"{final_count} 건")

        st.divider()

        # 4. 학과 선택 필터
        st.header("3. 학과 선택 및 분석")

        dept_list = ["전체"] + list(df_clean["학과"].unique())
        selected_dept = st.selectbox("분석할 학과를 선택하세요:", dept_list)

        # 선택된 학과에 맞춰 데이터 필터링
        if selected_dept == "전체":
            filtered_df = df_clean
        else:
            filtered_df = df_clean[df_clean["학과"] == selected_dept]

        # 평균 만족도 표시
        avg_satisfaction = filtered_df["만족도"].mean()
        st.subheader(
            f"📌 [{selected_dept}] 평균 학교 생활 만족도: {avg_satisfaction:.2f}점 / 10.0점"
        )

        st.divider()

        # 5. 생활 습관 차이 (막대그래프)
        st.header("4. 학과별 생활 습관 비교 (막대그래프)")
        st.write("공부시간, 수면시간, 스마트폰 사용시간의 평균을 비교합니다.")

        habit_means = filtered_df[["공부시간", "수면시간", "스마트폰"]].mean()

        fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
        habit_means.plot(
            kind="bar", ax=ax_bar, color=["#4C72B0", "#55A868", "#C44E52"]
        )
        ax_bar.set_ylabel("평균 시간 (시간)")
        ax_bar.set_title(f"{selected_dept} - 평균 생활 습관")
        plt.xticks(rotation=0)
        st.pyplot(fig_bar)

        st.divider()

        # 6. 생활 습관과 학교 생활 만족도의 관계 (산점도)
        st.header("5. 생활 습관과 학교 생활 만족도 관계 (산점도)")

        x_var = st.radio(
            "만족도와 함께 비교할 항목을 선택하세요:",
            ["공부시간", "수면시간", "스마트폰"],
            horizontal=True,
        )

        fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
        ax_scatter.scatter(
            filtered_df[x_var],
            filtered_df["만족도"],
            alpha=0.7,
            color="#8172B3",
        )
        ax_scatter.set_xlabel(f"{x_var} (시간)")
        ax_scatter.set_ylabel("학교 생활 만족도")
        ax_scatter.set_title(f"{x_var}에 따른 학교 생활 만족도 분포")
        ax_scatter.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig_scatter)

        st.divider()

        # 7. 한 줄 의견 키워드 분석 (상위 10개 막대그래프 + 긍정/부정 카운트 + 워드클라우드)
        st.header("6. 한 줄 의견 키워드 & 감성 분석")

        text_list = filtered_df["한줄의견"].astype(str).tolist()
        full_text = " ".join(text_list)

        if len(full_text.strip()) > 0:
            # Kiwi 형태소 분석 (명사 및 형용사/동사 어근 추출)
            tokens = kiwi.tokenize(full_text)

            # 명사(NNG, NNP) 추출 (2글자 이상) -> 빈도 분석 및 워드클라우드용
            nouns = [
                t.form
                for t in tokens
                if t.tag in ["NNG", "NNP"] and len(t.form) > 1
            ]

            # 전체 토큰 어근(form) 추출 -> 긍정/부정 어휘 카운트용
            all_forms = [t.form for t in tokens]

            # 1) 긍정/부정 단어 등장 횟수 산출
            pos_count = sum(1 for f in all_forms if f in POSITIVE_WORDS)
            neg_count = sum(1 for f in all_forms if f in NEGATIVE_WORDS)

            st.subheader(f"💬 [{selected_dept}] 한 줄 의견 감성 단어 수")
            col_pos, col_neg = st.columns(2)
            col_pos.metric("😊 긍정 단어 등장 횟수", f"{pos_count} 회")
            col_neg.metric(
                "😟 부정 단어 등장 횟수", f"{neg_count} 회", delta_color="inverse"
            )

            st.write("")

            # 2) 자주 등장하는 단어 상위 10개 추출 및 시각화
            if nouns:
                noun_counts = Counter(nouns)
                top10_words = noun_counts.most_common(10)

                words, counts = zip(*top10_words)

                col_chart, col_wc = st.columns(2)

                with col_chart:
                    st.markdown("##### 📊 자주 등장하는 단어 Top 10")
                    fig_top10, ax_top10 = plt.subplots(figsize=(6, 4.5))
                    ax_top10.barh(
                        words[::-1], counts[::-1], color="#4C72B0"
                    )  # 상위 단어가 위로 오도록 반전
                    ax_top10.set_xlabel("빈도수")
                    ax_top10.set_title(f"{selected_dept} - 주요 키워드 Top 10")
                    ax_top10.grid(axis="x", linestyle="--", alpha=0.5)
                    st.pyplot(fig_top10)

                with col_wc:
                    st.markdown("##### ☁️ 키워드 워드클라우드")
                    processed_text = " ".join(nouns)
                    wordcloud = WordCloud(
                        width=500,
                        height=370,
                        background_color="white",
                        font_path=font_path
                        if os.path.exists(font_path)
                        else None,
                    ).generate(processed_text)

                    fig_wc, ax_wc = plt.subplots(figsize=(6, 4.5))
                    ax_wc.imshow(wordcloud, interpolation="bilinear")
                    ax_wc.axis("off")
                    st.pyplot(fig_wc)
            else:
                st.info("의미 있는 명사 단어를 추출하지 못했습니다.")
        else:
            st.info("한 줄 의견 데이터가 없습니다.")

        st.divider()

        # 8. 데이터 미리보기
        st.header("7. 선택한 데이터 미리보기")
        st.dataframe(filtered_df)

else:
    st.info("⬆️ 상단의 업로드 창에 분석할 CSV 파일을 넣어주세요.")