#!/usr/bin/env python3
"""
Velog 자동 포스팅 메인 스크립트
저장된 세션을 이용하여 Velog에 자동으로 글을 작성
"""

import os
import json
import time
from playwright.sync_api import sync_playwright
from utils.content_generator import ContentGenerator

class VelogPoster:
    def __init__(self, ai_api_key=None):
        self.session_file = 'velog_session.json'
        self.generator = ContentGenerator(use_ai=bool(ai_api_key), ai_api_key=ai_api_key)
        
    def load_session(self):
        """저장된 세션 정보 로드"""
        if not os.path.exists(self.session_file):
            print("❌ 세션 파일이 없습니다. 먼저 python install.py를 실행해주세요.")
            return None
            
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 세션 파일 로드 실패: {e}")
            return None
    
    def create_post(self, post_data):
        """Playwright를 사용하여 Velog에 포스트 작성"""
        session_data = self.load_session()
        if not session_data:
            return False
            
        print("🚀 Velog 자동 포스팅을 시작합니다...")
        
        with sync_playwright() as p:
            # 브라우저 시작
            browser = p.chromium.launch(headless=False)  # 디버깅을 위해 헤드리스 모드 비활성화
            context = browser.new_context(
                user_agent=session_data.get('user_agent', '')
            )
            
            # 쿠키 복원
            if 'cookies' in session_data:
                context.add_cookies(session_data['cookies'])
            
            page = context.new_page()
            
            try:
                # Velog 메인 페이지로 이동
                print("📄 Velog에 접속 중...")
                page.goto("https://velog.io", timeout=30000)
                
                # 로그인 상태 확인
                try:
                    page.wait_for_selector('a[href*="/@"]', timeout=5000)
                    print("✅ 로그인 상태 확인됨")
                except:
                    print("❌ 로그인이 필요합니다. python install.py를 다시 실행해주세요.")
                    return False
                
                # 글쓰기 페이지로 이동
                print("✏️  글쓰기 페이지로 이동...")
                page.goto("https://velog.io/write", timeout=30000)
                
                # 페이지 로딩 대기
                time.sleep(2)
                
                # 제목 입력
                print(f"📝 제목 입력: {post_data['title']}")
                title_input = page.wait_for_selector('textarea[placeholder*="제목"]', timeout=10000)
                title_input.fill(post_data['title'])
                
                # 본문 입력
                print("📄 본문 입력 중...")
                # Velog의 에디터는 CodeMirror를 사용하므로 적절한 셀렉터 찾기
                try:
                    # 다양한 에디터 셀렉터 시도
                    editor_selectors = [
                        '.ProseMirror',
                        'div[contenteditable="true"]',
                        '.CodeMirror-code',
                        'textarea'
                    ]
                    
                    editor = None
                    for selector in editor_selectors:
                        try:
                            editor = page.wait_for_selector(selector, timeout=3000)
                            if editor:
                                break
                        except:
                            continue
                    
                    if editor:
                        editor.click()
                        time.sleep(1)
                        # fill 대신 type 사용
                        editor.type(post_data['content'], delay=5)
                        print("✅ 본문 입력 완료")
                    else:
                        print("⚠️  에디터를 찾을 수 없어 키보드 입력 시도...")
                        page.keyboard.type(post_data['content'], delay=5)
                        
                except Exception as e:
                    print(f"⚠️  본문 입력 중 오류: {e}")
                
                # 태그 입력
                print(f"🏷️  태그 입력: {', '.join(post_data['tags'])}")
                try:
                    # 태그 입력 필드 찾기
                    tag_input = page.wait_for_selector('input[placeholder*="태그"]', timeout=5000)
                    for tag in post_data['tags']:
                        tag_input.fill(tag)
                        page.keyboard.press('Enter')
                        time.sleep(0.5)
                    print("✅ 태그 입력 완료")
                except Exception as e:
                    print(f"⚠️  태그 입력 실패: {e}")
                
                # 출간하기 버튼 클릭 (1차)
                publish_button = page.wait_for_selector('button:has-text("출간하기")', timeout=5000)
                publish_button.click()
                time.sleep(1)

                # 최종 출간하기 버튼 클릭 전 오버레이가 사라질 때까지 대기
                try:
                    page.wait_for_selector('.sc-bilyIR', state='detached', timeout=10000)
                except:
                    pass

                # 최종 출간하기 버튼 찾기 (정확한 셀렉터)
                final_publish_button = page.wait_for_selector('button[data-testid="publish"]', timeout=5000)

                # 버튼 활성화 및 가시성 체크 후 클릭
                if final_publish_button.is_enabled() and final_publish_button.is_visible():
                    final_publish_button.scroll_into_view_if_needed()
                    final_publish_button.click()
                    time.sleep(3)
                else:
                    print("❌ 최종 출간하기 버튼이 비활성화 상태이거나 보이지 않습니다.")
                    input("브라우저에서 직접 확인 후 엔터를 누르세요...")
                    return False

                # 에러 메시지 확인
                error_message = None
                try:
                    error_message = page.wait_for_selector('div:has-text("제목 또는 내용이 비어있습니다")', timeout=2000)
                except:
                    pass

                if error_message:
                    print("❌ [에러] 제목 또는 내용이 비어있습니다. 실제로 포스팅이 되지 않았습니다.")
                    input("디버깅을 위해 브라우저를 종료하려면 엔터를 누르세요...")
                    return False

                # 성공적으로 게시된 경우, URL이 /@username/ 으로 이동하는지 확인
                if "/@" in page.url:
                    print("✅ 포스트가 성공적으로 게시되었습니다!")
                else:
                    print("❌ 포스트가 정상적으로 게시되지 않았습니다. 브라우저에서 직접 확인하세요.")
                    input("디버깅을 위해 브라우저를 종료하려면 엔터를 누르세요...")
                    return False

                return True
                
            except Exception as e:
                print(f"❌ 포스팅 중 오류 발생: {e}")
                return False
            finally:
                # 브라우저 종료 전 잠시 대기 (결과 확인용)
                time.sleep(3)
                browser.close()

def main():
    print("🤖 Velog 자동 포스팅 시작")
    print("=" * 40)
    
    # AI API 키 설정 (환경변수에서 가져오기)
    ai_api_key = os.getenv('OPENAI_API_KEY')
    if ai_api_key:
        print("✅ AI 콘텐츠 생성 모드")
    else:
        print("📝 기본 콘텐츠 생성 모드 (AI API 키가 없습니다)")
    
    # VelogPoster 인스턴스 생성
    poster = VelogPoster(ai_api_key=ai_api_key)
    
    # 포스트 데이터 생성
    print("📝 포스트 내용 생성 중...")
    post_data = poster.generator.generate_post()
    
    print(f"📋 생성된 포스트 정보:")
    print(f"   제목: {post_data['title']}")
    print(f"   시리즈: {post_data['series']}")
    print(f"   태그: {', '.join(post_data['tags'])}")
    print(f"   본문 길이: {len(post_data['content'])}자")
    
    # 사용자 확인
    confirm = input("\n이 내용으로 포스팅하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("포스팅을 취소했습니다.")
        return
    
    # 포스팅 실행
    success = poster.create_post(post_data)
    
    if success:
        print("\n🎉 자동 포스팅이 완료되었습니다!")
        print("Velog에서 확인해보세요.")
    else:
        print("\n❌ 포스팅에 실패했습니다.")
        print("로그를 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main()