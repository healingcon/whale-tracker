
import os, re

api_key = os.environ.get('ANTHROPIC_API_KEY', '')
if not api_key:
    print("⚠️ API 키 없음 — 건너뜀")
    exit()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# API 키 + 헤더 주입
old = "headers: {'Content-Type': 'application/json'},"
new = f"""headers: {{
          'Content-Type': 'application/json',
          'x-api-key': '{api_key}',
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true'
        }},"""

html = html.replace(old, new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ API 키 주입 완료")
