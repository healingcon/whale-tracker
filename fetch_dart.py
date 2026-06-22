"""
DART API - 대량 지분 변동 공시 수집
API 키: https://opendart.fss.or.kr 에서 무료 발급
"""

import requests
import json
import os
from datetime import datetime, timedelta

DART_API_KEY = os.environ.get('DART_API_KEY', '')
BASE_URL = 'https://opendart.fss.or.kr/api'

def get_major_holdings(days_back=7):
    """5% 이상 지분 변동 공시 수집"""
    today = datetime.now()
    start = today - timedelta(days=days_back)
    
    params = {
        'crtfc_key': DART_API_KEY,
        'bgn_de': start.strftime('%Y%m%d'),
        'end_de': today.strftime('%Y%m%d'),
        'page_count': 100,
        'pblntf_ty': 'A',  # 지분공시
    }
    
    try:
        res = requests.get(f'{BASE_URL}/list.json', params=params, timeout=10)
        data = res.json()
        
        if data.get('status') != '000':
            print(f"DART API 오류: {data.get('message')}")
            return []
        
        items = []
        for item in data.get('list', []):
            # 5% 보고서만 필터
            if '주요주주' in item.get('report_nm', '') or '5%' in item.get('report_nm', ''):
                items.append({
                    'ticker': item.get('stock_code', ''),
                    'name': item.get('corp_name', ''),
                    'reporter': item.get('flr_nm', ''),
                    'report_nm': item.get('report_nm', ''),
                    'date': item.get('rcept_dt', ''),
                    'rcept_no': item.get('rcept_no', ''),
                })
        
        print(f"✅ DART 수집 완료: {len(items)}건")
        return items
        
    except Exception as e:
        print(f"❌ DART 수집 실패: {e}")
        return []


def get_holding_detail(rcept_no):
    """공시 상세 내용 (지분율, 변동 주식수 등)"""
    params = {
        'crtfc_key': DART_API_KEY,
        'rcept_no': rcept_no,
    }
    try:
        res = requests.get(f'{BASE_URL}/majorstock.json', params=params, timeout=10)
        return res.json()
    except:
        return {}


def main():
    print("📡 DART 지분변동 데이터 수집 시작...")
    
    holdings = get_major_holdings(days_back=30)
    
    # 상세 데이터 보강 (처음 20건만)
    result = []
    for item in holdings[:20]:
        detail = get_holding_detail(item['rcept_no'])
        detail_list = detail.get('list', [{}])
        if detail_list:
            d = detail_list[0]
            item['curr_pct'] = float(d.get('stkqy_irds', 0) or 0)
            item['prev_pct'] = float(d.get('bfsr_stkqy', 0) or 0)
            item['change_shares'] = d.get('stkqy_irds', '0')
        
        # 변동 유형 분류
        change = item.get('curr_pct', 0) - item.get('prev_pct', 0)
        if item.get('prev_pct', 0) == 0:
            item['type'] = 'new'
        elif change > 0:
            item['type'] = 'buy'
        else:
            item['type'] = 'sell'
        item['change'] = round(change, 2)
        
        result.append(item)
    
    # JSON 저장
    os.makedirs('data', exist_ok=True)
    output = {
        'updated_at': datetime.now().isoformat(),
        'count': len(result),
        'data': result
    }
    
    with open('data/dart_holdings.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"💾 data/dart_holdings.json 저장 완료 ({len(result)}건)")


if __name__ == '__main__':
    main()
