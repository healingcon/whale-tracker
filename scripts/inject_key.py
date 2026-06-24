import os, re

# ── Anthropic API 키 ──
anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
# ── Finnhub API 키 ──
finnhub_key = os.environ.get('FINNHUB_API_KEY', '')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Anthropic 헤더 주입
if anthropic_key:
    old = "headers: {'Content-Type': 'application/json'},"
    new = f"""headers: {{
          'Content-Type': 'application/json',
          'x-api-key': '{anthropic_key}',
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true'
        }},"""
    count = html.count(old)
    html = html.replace(old, new)
    print(f"✅ Anthropic 키 주입 완료 ({count}곳)")
else:
    print("⚠️ ANTHROPIC_API_KEY 없음")

# 2. Finnhub 키 주입
if finnhub_key:
    old_finn = "const FINNHUB_KEY = window.FINNHUB_API_KEY || '';"
    new_finn = f"const FINNHUB_KEY = window.FINNHUB_API_KEY || '{finnhub_key}';"
    if old_finn in html:
        html = html.replace(old_finn, new_finn)
        print("✅ Finnhub 키 주입 완료")
    else:
        print("⚠️ Finnhub 키 삽입 위치 못 찾음")
else:
    print("⚠️ FINNHUB_API_KEY 없음 — 미국 주식 비활성화 상태")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ inject_key.py 실행 완료")
