#!/usr/bin/env python3
"""
Velog 자동 포스팅용 콘텐츠 생성기
제목, 본문, 태그, 시리즈를 자동 생성
"""

import random
import requests
import json
from faker import Faker

# 한글 콘텐츠 생성을 위한 Faker 인스턴스
fake = Faker('ko_KR')

class ContentGenerator:
    def __init__(self, use_ai=True, ai_api_key=None):
        self.use_ai = use_ai
        self.ai_api_key = ai_api_key
        
        self.tech_keywords = [
            'Python', 'JavaScript', 'React', 'Vue', 'Django', 'Flask',
            'FastAPI', 'Docker', 'Kubernetes', 'AWS', 'Git', 'Linux',
            'API', 'Database', 'MongoDB', 'PostgreSQL', 'Redis', 'Nginx'
        ]
        
        self.dev_topics = [
            '개발 일지', '프로젝트 회고', '기술 정리', '학습 노트',
            '트러블슈팅', '성능 최적화', '코드 리뷰', '아키텍처 설계'
        ]
        
        self.available_tags = [
            'Python', 'JavaScript', 'React', 'Vue', 'Django', 'Flask',
            'Playwright', 'Velog', '자동화', 'GPT', '개발일지', 'API',
            'Docker', 'AWS', 'Git', 'Linux', 'Database', 'Frontend',
            'Backend', '웹개발', '데이터베이스', '성능최적화'
        ]
        
        self.series_options = [
            '개발자동화', 'Velog 자동화 실험', 'AI 포스팅 시리즈',
            '개발 일기', '기술 탐구', '프로젝트 회고록'
        ]
    
    def generate_title(self):
        """자연스러운 개발 관련 제목 생성"""
        patterns = [
            f"{random.choice(self.tech_keywords)}로 {random.choice(['구현하는', '만드는', '개발하는'])} {fake.word()}",
            f"{random.choice(self.dev_topics)}: {random.choice(self.tech_keywords)} {fake.word()}",
            f"{fake.word()} {random.choice(['개발', '구현', '최적화'])} 경험 공유",
            f"{random.choice(self.tech_keywords)} {random.choice(['입문', '심화', '활용'])} 가이드",
            f"실무에서 배운 {random.choice(self.tech_keywords)} {fake.word()}"
        ]
        
        return random.choice(patterns)
    
    def generate_ai_content(self, topic=None):
        """AI를 이용한 고품질 콘텐츠 생성"""
        if not self.use_ai or not self.ai_api_key:
            return self.generate_basic_content()
        
        if not topic:
            topic = f"{random.choice(self.tech_keywords)} {random.choice(self.dev_topics)}"
        
        prompt = f"""
다음 주제로 개발 블로그 포스트를 마크다운 형식으로 작성해주세요:
주제: {topic}

요구사항:
1. 개발자들에게 유용한 실용적인 내용
2. 코드 예제 포함 (```언어명 형식 사용)
3. 이미지 플레이스홀더 여러 개 포함 (![설명](이미지URL) 형식)
4. 1500-2000자 분량
5. 마크다운 문법 활용 (제목, 부제목, 리스트, 강조 등)
6. 실무 경험 기반의 생생한 설명

내용 구성:
- 소개
- 문제 상황 설명 
- 해결 과정 (코드 포함)
- 결과 및 개선사항
- 마무리 및 다음 계획
"""
        
        try:
            # OpenAI API 호출 (예시)
            headers = {
                'Authorization': f'Bearer {self.ai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"AI API 오류: {response.status_code}")
                return self.generate_basic_content()
                
        except Exception as e:
            print(f"AI 콘텐츠 생성 실패: {e}")
            return self.generate_basic_content()
    
    def generate_basic_content(self):
        """기본 콘텐츠 생성 (AI 미사용 시)"""
        paragraphs = []
        
        # 인트로 문단
        intro_templates = [
            f"# {random.choice(self.tech_keywords)} 프로젝트 경험\n\n오늘은 {random.choice(self.tech_keywords)}를 활용한 프로젝트를 진행했습니다.",
            f"# {random.choice(self.dev_topics)} 정리\n\n최근 {random.choice(self.dev_topics)}를 정리하면서 느낀 점들을 공유하고자 합니다.",
            f"# {random.choice(self.tech_keywords)} 개발 기록\n\n{random.choice(self.tech_keywords)} 관련 작업을 하면서 겪었던 경험을 기록해보겠습니다."
        ]
        paragraphs.append(random.choice(intro_templates))
        
        # 이미지 플레이스홀더 추가
        paragraphs.append(f"![프로젝트 개요](https://via.placeholder.com/600x300?text={random.choice(self.tech_keywords)}+Project)")
        
        # 메인 콘텐츠 문단들 (2-3개)
        main_content_count = random.randint(2, 3)
        for i in range(main_content_count):
            content_templates = [
                f"## 주요 기능 구현\n\n이번 작업에서 가장 중요했던 부분은 **{random.choice(self.tech_keywords)}**의 핵심 기능을 제대로 활용하는 것이었습니다.\n\n```python\n# 예시 코드\ndef main_function():\n    return 'Hello World'\n```\n\n![구현 과정](https://via.placeholder.com/500x250?text=Implementation)",
                f"## 문제 해결 과정\n\n{random.choice(self.tech_keywords)}를 사용하면서 새롭게 알게 된 점들을 정리해보겠습니다:\n\n- **성능 최적화** 방법\n- **에러 처리** 개선\n- **코드 품질** 향상\n\n![결과 화면](https://via.placeholder.com/400x200?text=Result)",
                f"## 성능 개선 결과\n\n개발 과정에서 **{random.choice(['성능', '보안', '유지보수성'])}** 측면을 중점적으로 고려했습니다.\n\n> 💡 **팁**: 이런 방식으로 접근하면 더 효율적입니다.\n\n![성능 비교](https://via.placeholder.com/550x300?text=Performance+Chart)"
            ]
            paragraphs.append(random.choice(content_templates))
        
        # 마무리 문단
        outro_templates = [
            f"## 마무리\n\n이번 경험을 통해 **{random.choice(self.tech_keywords)}**에 대한 이해를 더욱 깊게 할 수 있었습니다. 다음에는 더 복잡한 기능도 시도해보고 싶습니다.\n\n![다음 계획](https://via.placeholder.com/400x150?text=Next+Plan)",
            f"## 정리\n\n앞으로도 지속적으로 학습하고 기록하면서 개발 실력을 향상시켜 나가겠습니다.\n\n**관련 링크:**\n- [공식 문서](https://example.com)\n- [GitHub 저장소](https://github.com/example)",
            f"## 마치며\n\n비슷한 작업을 하시는 분들께 도움이 되었으면 좋겠습니다. 궁금한 점이 있으시면 댓글로 남겨주세요!\n\n![마무리](https://via.placeholder.com/300x100?text=Thank+You)"
        ]
        paragraphs.append(random.choice(outro_templates))
        
        return '\n\n'.join(paragraphs)
    
    def generate_content(self):
        """콘텐츠 생성 메인 메서드"""
        if self.use_ai:
            return self.generate_ai_content()
        else:
            return self.generate_basic_content()
    
    def generate_tags(self, count=3):
        """랜덤 태그 3개 선택"""
        return random.sample(self.available_tags, min(count, len(self.available_tags)))
    
    def generate_series(self):
        """시리즈 이름 선택"""
        return random.choice(self.series_options)
    
    def set_ai_config(self, api_key):
        """AI API 키 설정"""
        self.ai_api_key = api_key
        self.use_ai = True
    
    def generate_post(self, topic=None):
        """전체 포스트 데이터 생성"""
        return {
            'title': self.generate_title(),
            'content': self.generate_content() if not topic else self.generate_ai_content(topic),
            'tags': self.generate_tags(),
            'series': self.generate_series()
        }

# 테스트용 실행 코드
if __name__ == "__main__":
    generator = ContentGenerator()
    post_data = generator.generate_post()
    
    print("=" * 50)
    print("📝 생성된 포스트 미리보기")
    print("=" * 50)
    print(f"제목: {post_data['title']}")
    print(f"시리즈: {post_data['series']}")
    print(f"태그: {', '.join(post_data['tags'])}")
    print("\n본문:")
    print(post_data['content'])
    print("=" * 50)