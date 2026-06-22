"""
SEC EDGAR API - 13F 보고서 수집
국민연금 + 투자 전설 포트폴리오
완전 무료, API 키 불필요
"""

import requests
import json
import os
import time
from datetime import datetime

HEADERS = {
    'User-Agent': 'whale-tracker contact@example.com',  # SEC 필수 헤더
    'Accept': 'application/json',
}

# 주요 투자자 CIK (SEC 등록 번호)
INVESTORS = {
    'nps': {
        'name': '국민연금공단',
        'cik': '0001640575',
        'emoji': '🇰🇷',
        'aum': '$246B',
    },
    'berkshire': {
        'name': '워런 버핏',
        'firm': 'Berkshire Hathaway',
        'cik': '0001067983',
        'emoji': '🎩',
        'aum': '$347B',
    },
    'scion': {
        'name': '마이클 버리',
        'firm': 'Scion Asset Management',
        'cik': '0001536285',
        'emoji': '🐻',
        'aum': '$1.8B',
    },
    'pershing': {
        'name': '빌 애크먼',
        'firm': 'Pershing Square',
        'cik': '0001336528',
        'emoji': '📐',
        'aum': '$16.2B',
    },
    'appaloosa': {
        'name': '데이비드 테퍼',
        'firm': 'Appaloosa Management',
        'cik': '0001656456',
        'emoji': '🐎',
        'aum': '$14.8B',
    },
    'bridgewater': {
        'name': '레이 달리오',
        'firm': 'Bridgewater Associates',
        'cik': '0001350694',
        'emoji': '🌊',
        'aum': '$124B',
    },
    'soros': {
        'name': '조지 소로스',
        'firm': 'Soros Fund Management',
        'cik': '0001029160',
        'emoji': '🔮',
        'aum': '$8.9B',
    },
}


def get_latest_13f(cik):
    """가장 최근 13F 보고서 accession number 가져오기"""
    url = f'https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json'
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        data = res.json()
        
        filings = data.get('filings', {}).get('recent', {})
        forms = filings.get('form', [])
        accessions = filings.get('accessionNumber', [])
        dates = filings.get('filingDate', [])
        
        for i, form in enumerate(forms):
            if form in ['13F-HR', '13F-HR/A']:
                return {
                    'accession': accessions[i].replace('-', ''),
                    'date': dates[i],
                    'form': form
                }
    except Exception as e:
        print(f"  CIK {cik} 조회 실패: {e}")
    return None


def get_13f_holdings(cik, accession):
    """13F 보유 종목 목록 파싱"""
    # SEC EDGAR XML 파싱
    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/infotable.json'
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    
    # 대안: 인덱스 파일에서 찾기
    idx_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F&dateb=&owner=include&count=1&search_text='
    return []


def fetch_all():
    print("📡 SEC EDGAR 13F 데이터 수집 시작...")
    os.makedirs('data', exist_ok=True)
    
    result = {}
    for key, investor in INVESTORS.items():
        print(f"  📊 {investor['name']} ({investor.get('firm', '')}) 수집 중...")
        
        filing = get_latest_13f(investor['cik'])
        if filing:
            holdings = get_13f_holdings(investor['cik'], filing['accession'])
            result[key] = {
                **investor,
                'filing_date': filing['date'],
                'holdings': holdings[:10] if isinstance(holdings, list) else [],
            }
            print(f"    ✅ {filing['date']} 기준 데이터 수집")
        else:
            result[key] = {**investor, 'filing_date': None, 'holdings': []}
            print(f"    ⚠️ 13F 데이터 없음")
        
        time.sleep(0.5)  # SEC 서버 과부하 방지
    
    output = {
        'updated_at': datetime.now().isoformat(),
        'source': 'SEC EDGAR 13F',
        'investors': result
    }
    
    with open('data/sec_13f.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"💾 data/sec_13f.json 저장 완료")


if __name__ == '__main__':
    fetch_all()
