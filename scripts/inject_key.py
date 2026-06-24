import os, re

anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
finnhub_key   = os.environ.get('FINNHUB_API_KEY', '')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Anthropic 헤더 주입 (모든 형태 처리) ──
if anthropic_key:
    new_headers = (
        f"headers: {{\n"
        f"          'Content-Type': 'application/json',\n"
        f"          'x-api-key': '{anthropic_key}',\n"
        f"          'anthropic-version': '2023-06-01',\n"
        f"          'anthropic-dangerous-direct-browser-access': 'true'\n"
        f"        }},"
    )
    # 정규식으로 모든 형태 한 번에 교체
    pattern = r"headers:\s*\{[\s'\"]*Content-Type[\s'\"]*:[\s'\"]*application/json[\s'\"]*\},"
    count = len(re.findall(pattern, html))
    html = re.sub(pattern, new_headers, html)
    print(f"✅ Anthropic 키 주입 완료 ({count}곳)")
else:
    print("⚠️ ANTHROPIC_API_KEY 없음")

# ── 2. Finnhub 키 주입 ──
if finnhub_key:
    old = "const FINNHUB_KEY = window.FINNHUB_API_KEY || '';"
    new = f"const FINNHUB_KEY = window.FINNHUB_API_KEY || '{finnhub_key}';"
    if old in html:
        html = html.replace(old, new)
        print("✅ Finnhub 키 주입 완료")
else:
    print("⚠️ FINNHUB_API_KEY 없음")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ inject_key.py 완료")
