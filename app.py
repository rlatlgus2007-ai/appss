import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import platform

# --------------------------------------------------------
# 0. 한글 폰트 설정 (그래프 한글 깨짐 방지)
# --------------------------------------------------------
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# --------------------------------------------------------
# 1. 제목
# --------------------------------------------------------
st.title("🎓 대학 생활 데이터 대시보드")
st.write("우리 학교 학생들의 생활 습관과 만족도를 한눈에 분석해 보세요!")

# --------------------------------------------------------
# 2. CSV 업로드
# --------------------------------------------------------
uploaded_file = st.file_uploader("'campus_life.csv' 파일을 업로드 해주세요.", type=['csv'])

if uploaded_file is None:
    st.info("데이터 파일을 업로드해주세요. 🚀")
else:
    # 데이터 읽어오기
    df = pd.read_csv(uploaded_file)

    # ========================================================
    # 🚨 [강력한 에러 방지 처리 구간 시작] 🚨
    # ========================================================

    # 1. 컬럼명(열 이름)의 모든 띄어쓰기를 없앱니다.
    df.columns = df.columns.str.replace(' ', '')

    # 2. 분석에 사용할 주요 열들을 모두 찾아 강제로 '숫자'로 바꿉니다.
    target_numeric_columns = ['만족도', '수면시간', '공부시간', '스마트폰사용시간']

    for col in target_numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

            # ========================================================
    # 🚨 [강력한 에러 방지 처리 구간 끝] 🚨
    # ========================================================

    # --------------------------------------------------------
    # 3. 데이터 미리보기
    # --------------------------------------------------------
    st.subheader("👀 데이터 미리보기")
    st.dataframe(df.head())

    # --------------------------------------------------------
    # 4. 전처리 결과 (결측치 제외)
    # --------------------------------------------------------
    st.subheader("🛠️ 데이터 전처리 결과")
    original_count = len(df)

    # 빈칸(결측치)이 있는 행 제거
    df = df.dropna()
    cleaned_count = len(df)
    dropped_count = original_count - cleaned_count

    st.success(f"데이터 정제 완료! 빈칸이 있거나 잘못된 데이터 **{dropped_count}건**을 제외했습니다.")

    # --------------------------------------------------------
    # 5. 학과 선택 (필터링)
    # --------------------------------------------------------
    st.subheader("🎯 학과 선택 및 결과 보기")

    if '학과' in df.columns:
        department_list = ['전체'] + list(df['학과'].unique())
        selected_dept = st.selectbox("결과를 확인할 학과를 선택하세요:", department_list)

        if selected_dept == '전체':
            filtered_df = df
        else:
            filtered_df = df[df['학과'] == selected_dept]
    else:
        st.warning("데이터에 '학과' 열이 존재하지 않아 전체 데이터로 분석합니다.")
        filtered_df = df
        selected_dept = "전체"

    st.markdown("---")

    # --------------------------------------------------------
    # 6. 그래프 및 결과
    # --------------------------------------------------------

    # 6-1. 평균 만족도
    if '만족도' in filtered_df.columns:
        avg_satisfaction = filtered_df['만족도'].mean()
        st.metric(label=f"[{selected_dept}] 평균 학교 생활 만족도", value=f"{avg_satisfaction:.2f}점")
    else:
        st.error("데이터에 '만족도' 열이 없어 계산할 수 없습니다.")

    col1, col2 = st.columns(2)

    # [그래프 1] 생활습관 차이 (막대 그래프)
    with col1:
        st.write("##### 📊 평균 생활습관 시간 비교")
        check_habits = ['수면시간', '공부시간', '스마트폰사용시간']
        exist_habits = [col for col in check_habits if col in filtered_df.columns]

        if exist_habits:
            habit_means = filtered_df[exist_habits].mean()
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            habit_means.plot(kind='bar', ax=ax1, color=['#4C72B0', '#55A868', '#C44E52'][:len(exist_habits)])
            ax1.set_title(f"{selected_dept} 생활습관 평균", fontsize=12)
            ax1.set_ylabel("시간 (Hour)")
            ax1.set_xlabel("항목")
            plt.xticks(rotation=0)
            st.pyplot(fig1)
        else:
            st.warning("수면/공부/스마트폰 관련 열을 찾을 수 없습니다.")

    # [그래프 2] 만족도 상관관계 (산점도)
    with col2:
        st.write("##### 📈 공부시간과 만족도의 관계")
        if '공부시간' in filtered_df.columns and '만족도' in filtered_df.columns:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            sns.scatterplot(data=filtered_df, x='공부시간', y='만족도', ax=ax2, color='#8C564B')
            ax2.set_title("공부시간 vs 만족도 산점도", fontsize=12)
            ax2.set_xlabel("공부시간 (Hour)")
            ax2.set_ylabel("만족도 (점수)")
            st.pyplot(fig2)
        else:
            st.warning("공부시간 또는 만족도 열을 찾을 수 없습니다.")

    # --------------------------------------------------------
    # [기능 추가] 한줄 의견 텍스트 분석 (학과 필터 연동)
    # --------------------------------------------------------
    st.write("##### 💬 한줄 의견 키워드 및 감성 분석")
    if '한줄의견' in filtered_df.columns:
        # 모든 한줄의견 텍스트 합치기 및 단어 단위 분리
        all_text = " ".join(filtered_df['한줄의견'].astype(str).tolist())
        words = all_text.split()

        # 1. 자주 등장하는 단어 상위 10개 막대그래프
        meaningful_words = [word for word in words if len(word) >= 2]  # 2글자 이상 단어만 추출
        word_counts = Counter(meaningful_words)
        top_words = word_counts.most_common(10)

        # 2. 긍정/부정 단어 분석 로직
        # (원하는 긍정/부정 키워드가 있다면 아래 리스트에 추가/수정 가능합니다)
        positive_keywords = ['좋아', '좋음', '만족', '최고', '행복', '감사', '편해', '유익', '추천', '재밌', '좋다']
        negative_keywords = ['별로', '최악', '불만', '피곤', '힘들', '어려', '나빠', '나쁨', '아쉽', '부족', '짜증']

        pos_count = sum(1 for word in words if any(pos in word for pos in positive_keywords))
        neg_count = sum(1 for word in words if any(neg in word for neg in negative_keywords))

        # 결과 출력 화면 레이아웃 분할
        text_col1, text_col2 = st.columns([2, 1])

        with text_col1:
            if top_words:
                df_words = pd.DataFrame(top_words, columns=['단어', '빈도수'])
                fig3, ax3 = plt.subplots(figsize=(7, 4))
                # sns.barplot에 x, y 할당 방식 적용
                sns.barplot(data=df_words, x='빈도수', y='단어', ax=ax3, palette='viridis')
                ax3.set_title(f"[{selected_dept}] 자주 등장한 단어 Top 10", fontsize=12)
                ax3.set_xlabel("등장 횟수 (번)")
                ax3.set_ylabel("단어")
                st.pyplot(fig3)
            else:
                st.info("분석할 의미 있는 텍스트 데이터가 없습니다.")

        with text_col2:
            st.markdown("###### 💡 긍정 vs 부정 단어 분석")
            st.success(f"😊 **긍정 단어:** {pos_count}회 등장")
            st.error(f"😞 **부정 단어:** {neg_count}회 등장")
            st.caption("※ '만족', '최고', '힘들다', '별로' 등의 키워드 포함 여부로 단순 측정된 결과입니다.")

    else:
        st.warning("데이터에 '한줄의견' 열이 없습니다.")





