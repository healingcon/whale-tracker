# 🐋 고래추적기

> DART + SEC EDGAR 기반 기관 지분 변동 추적 사이트  
> GitHub Actions 자동화 · GitHub Pages 무료 배포 · Claude AI 분석 연동

## 📁 구조

```
whale-tracker/
├── index.html              ← 메인 사이트 (단일 파일)
├── data/
│   ├── dart_holdings.json  ← DART 지분변동 (자동 업데이트)
│   └── sec_13f.json        ← SEC 13F 보고서 (자동 업데이트)
├── scripts/
│   ├── fetch_dart.py       ← DART API 수집
│   ├── fetch_sec.py        ← SEC EDGAR 수집
│   └── build_index.py      ← HTML 데이터 인젝션
└── .github/workflows/
    └── update-data.yml     ← 자동화 스케줄러
```

## 🚀 배포 방법

### 1. GitHub 저장소 생성
```bash
git init
git remote add origin https://github.com/YOUR_ID/whale-tracker.git
git push -u origin main
```

### 2. API 키 등록 (GitHub Secrets)
Settings → Secrets → Actions → New repository secret

| 이름 | 값 |
|------|-----|
| `DART_API_KEY` | https://opendart.fss.or.kr 에서 무료 발급 |

### 3. GitHub Pages 활성화
Settings → Pages → Source: `main` 브랜치 / `root` 폴더

### 4. 자동 업데이트 확인
Actions 탭에서 워크플로우 실행 확인

---

## 🔑 DART API 키 발급

1. https://opendart.fss.or.kr 접속
2. 회원가입 → 인증키 신청
3. 이메일 인증 후 즉시 발급 (무료)
4. 하루 10,000건 호출 가능

## 📊 기능

| 탭 | 데이터 소스 | 업데이트 주기 |
|----|------------|-------------|
| DART 지분변동 | 금감원 DART API | 평일 2회 (08시, 17시) |
| 국민연금 국내 | DART 사업보고서 | 분기별 |
| 국민연금 미국 | SEC EDGAR 13F | 분기별 |
| 투자 전설 | SEC EDGAR 13F | 분기별 |
| 종목별 고래 | DART + SEC 합산 | 자동 |

## 🤖 Claude AI 분석

각 탭의 "AI 요약 분석" 버튼을 누르면 Claude가 현재 데이터를 분석해 한국어로 요약합니다.

---
**투자 참고용 정보입니다. 투자 판단의 책임은 본인에게 있습니다.**
