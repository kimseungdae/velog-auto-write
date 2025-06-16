#!/usr/bin/env python3
"""
Velog 자동 포스팅 초기 설정 스크립트
Google 로그인을 통한 인증 후 세션 쿠키 저장
"""

import os
import json
import time
from playwright.sync_api import sync_playwright

def setup_browser_context(context):
   """
   Google 로그인 차단을 우회하기 위한 브라우저 설정
   """
   # User Agent 설정
   context.set_extra_http_headers({
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
   })
   
   # 자동화 탐지 우회 스크립트 주입
   context.add_init_script("""
       // webdriver 속성 제거
       Object.defineProperty(navigator, 'webdriver', {
           get: () => undefined,
       });
       
       // 플러그인 정보 조작
       Object.defineProperty(navigator, 'plugins', {
           get: () => [1, 2, 3, 4, 5],
       });
       
       // 언어 설정
       Object.defineProperty(navigator, 'languages', {
           get: () => ['ko-KR', 'ko', 'en-US', 'en'],
       });
       
       // Chrome 런타임 정보 조작
       Object.defineProperty(navigator, 'chrome', {
           get: () => ({
               runtime: {},
           }),
       });
       
       // 권한 API 조작
       const originalQuery = window.navigator.permissions.query;
       window.navigator.permissions.query = (parameters) => (
           parameters.name === 'notifications' ?
               Promise.resolve({ state: Notification.permission }) :
               originalQuery(parameters)
       );
   """)

def login_to_velog():
   """
   브라우저를 열어 사용자가 수동으로 Velog에 로그인하고
   세션 쿠키를 저장하는 함수
   """
   print("🌐 브라우저를 열어 Velog에 로그인합니다...")
   print("구글 계정으로 로그인 후 메인 페이지가 로드되면 아무 키나 눌러주세요.")
   
   with sync_playwright() as p:
       # 브라우저 실행 (Google 감지 우회 설정)
       browser = p.chromium.launch(
           headless=False,
           args=[
               '--disable-blink-features=AutomationControlled',
               '--no-first-run',
               '--disable-extensions',
               '--disable-default-apps',
               '--disable-background-timer-throttling',
               '--disable-backgrounding-occluded-windows',
               '--disable-renderer-backgrounding',
               '--disable-web-security',
               '--disable-features=VizDisplayCompositor'
           ]
       )
       
       context = browser.new_context(
           viewport={'width': 1920, 'height': 1080},
           user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
       )
       
       # 브라우저 설정 적용
       setup_browser_context(context)
       
       page = context.new_page()
       
       try:
           # Velog 메인 페이지로 이동
           print("📍 Velog 메인 페이지로 이동 중...")
           page.goto("https://velog.io", wait_until='networkidle')
           time.sleep(2)
           
           # 로그인 버튼 클릭
           print("🔍 로그인 버튼을 찾는 중...")
           try:
               # 로그인 버튼 찾기 (여러 가능한 셀렉터 시도)
               login_selectors = [
                   'text=로그인',
                   'a[href="/login"]',
                   'button:has-text("로그인")',
                   '.login-button'
               ]
               
               login_clicked = False
               for selector in login_selectors:
                   try:
                       page.click(selector, timeout=3000)
                       login_clicked = True
                       print("✅ 로그인 버튼을 클릭했습니다.")
                       break
                   except:
                       continue
               
               if not login_clicked:
                   print("⚠️  로그인 버튼을 자동으로 찾지 못했습니다. 수동으로 로그인 버튼을 클릭해주세요.")
               
           except Exception as e:
               print(f"⚠️  로그인 버튼 클릭 중 오류: {e}")
               print("수동으로 로그인 버튼을 클릭해주세요.")
           
           time.sleep(3)
           
           # Google 로그인 처리
           print("🔑 Google 로그인 진행 중...")
           print("Google 계정 정보를 입력하고 로그인을 완료해주세요.")
           print("⚠️  '이 브라우저 또는 앱은 안전하지 않을 수 있습니다' 메시지가 나오면:")
           print("   1. '고급' 또는 '자세히' 클릭")
           print("   2. '안전하지 않은 앱 액세스 허용' 선택")
           print("   또는 다른 브라우저에서 https://myaccount.google.com/lesssecureapps 에서 설정 변경")
           
           # 사용자가 수동으로 로그인할 때까지 대기
           input("\n✅ 로그인 완료 후 Velog 메인 페이지로 돌아오면 아무 키나 눌러주세요...")
           
           # 로그인 상태 확인
           print("🔍 로그인 상태 확인 중...")
           
           # 현재 URL 확인
           current_url = page.url
           print(f"현재 URL: {current_url}")
           
           # 여러 방법으로 로그인 상태 확인
           login_confirmed = False
           
           # 방법 1: 프로필 관련 요소 확인
           profile_selectors = [
               'a[href*="/@"]',  # 프로필 링크
               '.user-profile',
               '.profile-image',
               'img[alt*="profile"]',
               '[data-testid="profile"]'
           ]
           
           for selector in profile_selectors:
               try:
                   if page.locator(selector).count() > 0:
                       login_confirmed = True
                       print(f"✅ 로그인 확인됨 (프로필 요소 발견: {selector})")
                       break
               except:
                   continue
           
           # 방법 2: 로그인 버튼이 없는지 확인
           if not login_confirmed:
               try:
                   login_buttons = page.locator('text=로그인').count()
                   if login_buttons == 0:
                       login_confirmed = True
                       print("✅ 로그인 확인됨 (로그인 버튼 없음)")
               except:
                   pass
           
           # 방법 3: 쿠키에서 인증 토큰 확인
           if not login_confirmed:
               cookies = context.cookies()
               auth_cookies = [c for c in cookies if 'token' in c['name'].lower() or 'auth' in c['name'].lower() or 'session' in c['name'].lower()]
               if auth_cookies:
                   login_confirmed = True
                   print("✅ 로그인 확인됨 (인증 쿠키 발견)")
           
           if not login_confirmed:
               confirm = input("❓ 로그인 상태를 자동으로 확인할 수 없습니다. 로그인이 완료되었나요? (y/N): ").strip().lower()
               if confirm != 'y':
                   print("❌ 로그인이 완료되지 않았습니다. 다시 시도해주세요.")
                   browser.close()
                   return False
               login_confirmed = True
           
           if login_confirmed:
               print("✅ 로그인이 확인되었습니다!")
               
               # 쿠키 및 세션 정보 저장
               cookies = context.cookies()
               local_storage = page.evaluate("() => ({ ...localStorage })")
               session_storage = page.evaluate("() => ({ ...sessionStorage })")
               
               session_data = {
                   'cookies': cookies,
                   'localStorage': local_storage,
                   'sessionStorage': session_storage,
                   'user_agent': page.evaluate('navigator.userAgent'),
                   'url': page.url,
                   'timestamp': time.time()
               }
               
               try:
                   with open('velog_session.json', 'w', encoding='utf-8') as f:
                       json.dump(session_data, f, indent=2, ensure_ascii=False)
                   
                   print("✅ 세션 정보가 저장되었습니다!")
                   print(f"📁 저장된 쿠키 수: {len(cookies)}")
                   print(f"📁 저장된 로컬스토리지 항목 수: {len(local_storage)}")
                   
                   browser.close()
                   return True
                   
               except Exception as e:
                   print(f"❌ 세션 저장 중 오류: {e}")
                   browser.close()
                   return False
           
       except Exception as e:
           print(f"❌ 로그인 과정 중 오류 발생: {e}")
           browser.close()
           return False

def verify_session():
   """
   저장된 세션이 유효한지 확인
   """
   if not os.path.exists('velog_session.json'):
       return False
   
   try:
       with open('velog_session.json', 'r', encoding='utf-8') as f:
           session_data = json.load(f)
       
       # 세션 만료 시간 확인 (7일)
       if time.time() - session_data.get('timestamp', 0) > 7 * 24 * 3600:
           print("⚠️  세션이 만료되었습니다. (7일 초과)")
           return False
       
       print("✅ 저장된 세션을 발견했습니다.")
       return True
       
   except Exception as e:
       print(f"❌ 세션 파일 읽기 오류: {e}")
       return False

def main():
   print("📝 Velog 자동 포스팅 초기 설정")
   print("=" * 40)
   print("🔐 Velog는 구글 로그인을 사용합니다.")
   print("브라우저가 열리면 구글 계정으로 로그인해주세요.")
   print()
   print("💡 Google 로그인 팁:")
   print("   - '안전하지 않은 앱' 경고가 나오면 '고급' → '안전하지 않은 앱 액세스 허용'")
   print("   - 2단계 인증 사용 시 앱 비밀번호 생성을 고려해주세요.")
   print()
   
   # 기존 세션 파일 확인
   if verify_session():
       overwrite = input("⚠️  유효한 세션 파일이 있습니다. 새로 로그인하시겠습니까? (y/N): ").strip().lower()
       if overwrite != 'y':
           print("✅ 기존 세션을 사용합니다.")
           return
   
   # 로그인 및 세션 저장
   print("\n🚀 로그인 프로세스를 시작합니다...")
   if login_to_velog():
       print("\n🎉 설정이 완료되었습니다!")
       print("=" * 40)
       print("✅ 이제 다음 명령어로 자동 포스팅을 실행할 수 있습니다:")
       print("   python post_writer.py")
       print()
       print("📌 주의사항:")
       print("   - 세션은 약 7일간 유효합니다.")
       print("   - 만료 시 이 스크립트를 다시 실행해주세요.")
   else:
       print("\n❌ 설정에 실패했습니다.")
       print("💡 문제 해결 방법:")
       print("   1. 인터넷 연결 확인")
       print("   2. Google 계정 보안 설정 확인")
       print("   3. 다른 브라우저에서 수동 로그인 후 재시도")

if __name__ == "__main__":
   main()