# 🎓 학과별 학생 생활 습관 및 만족도 분석 웹 (Streamlit)

학생들의 **공부시간, 수면시간, 스마트폰 사용시간** 등 생활 습관과 **학교 생활 만족도**, 그리고 **한 줄 의견 데이터**를 학과별로 다각도 분석 및 시각화해 주는 Streamlit 대시보드 웹 애플리케이션입니다.

---

## 📌 주요 기능

1. **데이터 자동 전처리**: CSV 업로드 시 결측치 및 숫자가 아닌 이상치 데이터 자동 정제
2. **학과별 필터링**: 전체 데이터 및 특정 학과별 조건 조회 완벽 연동
3. **생활 습관 평균 비교**: 학과별 공부/수면/스마트폰 사용 시간 평균 막대그래프 시각화
4. **만족도 관계 분석**: 생활 습관 항목과 만족도 간 상관관계를 확인할 수 있는 라디오 버튼 연동 산점도
5. **한 줄 의견 키워드 & 감성 분석 (Kiwi 형태소 분석기)**:
   - 💬 **감성 어휘 카운트**: 긍정 / 부정 키워드 등장 횟수 실시간 집계
   - 📊 **주요 키워드 Top 10**: 자주 등장하는 명사 단어 상위 10개 수평 막대그래프
   - ☁️ **워드클라우드**: 핵심 키워드를 직관적인 시각화로 제공

---

## 📁 프로젝트 구조 (File Structure)

```text
.
├── app.py               # Streamlit 메인 애플리케이션 코드
├── NanumGothic.ttf      # 한글 폰트 파일 (그래프 및 워드클라우드 깨짐 방지용)
├── requirements.txt     # 설치할 파이썬 패키지 목록
└── README.md            # 프로젝트 설명 문서
```

> **주의:** Matplotlib 및 WordCloud의 한글 깨짐 방지를 위해 `NanumGothic.ttf` 폰트 파일이 `app.py`와 동일한 폴더에 위치해야 합니다.

---

## 🛠️ 설치 및 실행 방법 (Installation & Run)

### 1. Repository 클론
```bash
git clone https://github.com/사용자이름/저장소이름.git
cd 저장소이름
```

### 2. 가상환경 구축 및 가상환경 활성화 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. Streamlit 앱 실행
```bash
streamlit run app.py
```

---

## 📊 CSV 데이터 요구사항 (CSV Format)

업로드하는 CSV 파일에는 아래의 열(Header) 이름들이 포함되어 있어야 합니다:

| 열 이름 | 설명 | 데이터 타입 |
| :--- | :--- | :--- |
| `학과` | 학생의 소속 학과 | 문자열 (`String`) |
| `공부시간` | 하루 평균 공부 시간 (시간) | 숫자 (`Float/Int`) |
| `수면시간` | 하루 평균 수면 시간 (시간) | 숫자 (`Float/Int`) |
| `스마트폰` | 하루 평균 스마트폰 사용 시간 (시간) | 숫자 (`Float/Int`) |
| `만족도` | 학교 생활 만족도 점수 (1~10점) | 숫자 (`Float/Int`) |
| `한줄의견` | 학생들의 주관식 한 줄 피드백 | 문자열 (`String`) |