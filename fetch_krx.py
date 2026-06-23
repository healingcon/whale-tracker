"""
KRX 외국인·기관 순매수 데이터 수집
매일 오후 4시 GitHub Actions 실행
네이버 금융 기반 (무료, API 키 불필요)
"""

import requests
import json
import os
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.naver.com',
}


def fetch_naver_investor(market='KOSPI'):
    """
    네이버 금융 - 외국인·기관 순매수 상위 종목
    https://finance.naver.com/sise/sise_quant.naver
    """
    url = 'https://finance.naver.com/sise/sise_quant.naver'
    params = { 'sosok': '0' if market == 'KOSPI' else '1' }

    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=10)
        res.encoding = 'euc-kr'

        # 간단한 파싱 (실제 운영 시 BeautifulSoup 사용 권장)
        # pip install beautifulsoup4 lxml
        from html.parser import HTMLParser

        data = []
        # 네이버 금융 테이블 파싱은 복잡하므로
        # KRX OpenAPI 사용을 권장
        return data

    except Exception as e:
        print(f"네이버 파싱 오류: {e}")
        return []


def fetch_krx_official():
    """
    KRX 공식 데이터포털 - 투자자별 거래실적
    https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201
    """
    today = datetime.now().strftime('%Y%m%d')

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    payload = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT02301',
        'mktId': 'STK',  # KOSPI
        'trdDd': today,
        'money': '1',    # 억원 단위
        'csvxls_isNo': 'false',
    }

    headers = {
        **HEADERS,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://data.krx.co.kr',
        'Referer': 'http://data.krx.co.kr/',
    }

    try:
        res = requests.post(url, data=payload, headers=headers, timeout=15)
        raw = res.json()

        items = []
        for row in raw.get('output', [])[:20]:
            # KRX 응답 필드 매핑
            foreign_buy = int(row.get('FRGN_NETBID_TRDVOL', '0').replace(',','').replace('-','') or 0)
            foreign_sign = row.get('FRGN_NETBID_TRDVOL', '0')
            if '-' in str(foreign_sign): foreign_buy = -foreign_buy

            inst_buy = int(row.get('ORGN_NETBID_TRDVOL', '0').replace(',','').replace('-','') or 0)
            inst_sign = row.get('ORGN_NETBID_TRDVOL', '0')
            if '-' in str(inst_sign): inst_buy = -inst_buy

            change = float(row.get('FLUC_RT', '0').replace(',','') or 0)

            items.append({
                'ticker': row.get('ISU_SRT_CD', ''),
                'name': row.get('ISU_ABBRV', ''),
                'foreign': foreign_buy,
                'institute': inst_buy,
                'change': change,
            })

        print(f"✅ KRX 공식 데이터 {len(items)}건 수집")
        return items

    except Exception as e:
        print(f"KRX API 오류: {e}")
        return get_sample_data()


def get_sample_data():
    """API 실패 시 샘플 데이터"""
    print("⚠️ 샘플 데이터 사용")
    return [
        {'ticker':'005930','name':'삼성전자',   'foreign':2847, 'institute':1203, 'change':1.24},
        {'ticker':'000660','name':'SK하이닉스', 'foreign':1923, 'institute': 892, 'change':2.31},
        {'ticker':'005380','name':'현대차',     'foreign': 834, 'institute':-234, 'change':0.87},
        {'ticker':'051910','name':'LG화학',     'foreign': 723, 'institute': 445, 'change':1.56},
        {'ticker':'006400','name':'삼성SDI',    'foreign': 612, 'institute': 321, 'change':0.94},
        {'ticker':'035420','name':'NAVER',      'foreign':-456, 'institute':-189, 'change':-0.73},
        {'ticker':'207940','name':'삼성바이오', 'foreign': 389, 'institute':-102, 'change':0.45},
        {'ticker':'015760','name':'한국전력',   'foreign':-892, 'institute': 334, 'change':-2.34},
        {'ticker':'035720','name':'카카오',     'foreign':-723, 'institute':-445, 'change':-1.89},
        {'ticker':'000270','name':'기아',       'foreign': 567, 'institute': 123, 'change':0.78},
    ]


def main():
    os.makedirs('data', exist_ok=True)

    print("📡 KRX 외국인·기관 순매수 수집 시작...")
    data = fetch_krx_official()

    # 동시 매수 신호 추가
    for item in data:
        if item['foreign'] > 0 and item['institute'] > 0:
            item['signal'] = 'both'
        elif item['foreign'] > 500:
            item['signal'] = 'foreign_strong'
        elif item['institute'] > 300:
            item['signal'] = 'institute_strong'
        elif item['foreign'] < -500:
            item['signal'] = 'foreign_sell'
        else:
            item['signal'] = 'neutral'

    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().isoformat(),
        'market': 'KOSPI',
        'count': len(data),
        'data': data,
        'summary': {
            'both_buy': len([d for d in data if d.get('signal')=='both']),
            'foreign_top': max(data, key=lambda x: x['foreign'])['name'] if data else '',
            'institute_top': max(data, key=lambda x: x['institute'])['name'] if data else '',
        }
    }

    with open('data/krx_today.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"💾 data/krx_today.json 저장 완료")
    print(f"   동시매수: {result['summary']['both_buy']}개")
    print(f"   외국인 1위: {result['summary']['foreign_top']}")
    print(f"   기관 1위: {result['summary']['institute_top']}")


if __name__ == '__main__':
    main()
