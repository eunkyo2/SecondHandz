# Second handz

중고 물건을 사고파는 사람들을 위한 Django 기반 중고거래 웹 플랫폼입니다. Secure Coding 과제로 제작되었으며, 회원가입부터 상품 거래, 채팅, 신고/제재, 송금, 관리자 기능까지 실제 중고거래 서비스에 필요한 기능을 갖추고 보안 요소를 적용했습니다.

## 주요 기능

- **회원**: 회원가입/로그인/로그아웃, 마이페이지(닉네임·자기소개·프로필 사진 수정, 비밀번호 변경), 아이디 중복 방지
- **상품**: 등록/수정/삭제, 목록·검색(제목 기준), 상세 조회, 판매완료 처리
- **채팅**: 상품별 1:1 채팅(구매 문의), 전체 유저가 참여하는 전체 채팅
- **신고/제재**: 유저·상품 신고(사유 + 증거 사진 첨부, 선택), 누적 신고 시 자동으로 상품 차단/유저 휴면 처리
- **송금**: 유저 간 잔액 송금
- **관리자**: Django 관리자 페이지 + 마이페이지 내 신고건 조회, 휴면계정 관리, 차단된 게시물 관리 화면

## 적용된 보안 조치

- 비밀번호 Argon2 해싱
- CSRF 토큰, 세션/CSRF 쿠키 하드닝(HttpOnly, SameSite, Secure), 세션 만료
- 로그인 실패 5회 시 계정 5분 잠금
- 아이디 등 민감정보 변경 시 현재 비밀번호 재인증
- 상품/채팅 등 소유자·참여자 검증(IDOR 방지), 폼 mass-assignment 방지
- WebSocket Origin 검증 및 메시지 전송 rate limiting
- 송금 시 트랜잭션 처리로 동시성(레이스 컨디션) 방지
- 보안 헤더(CSP 등) 적용

## 기술 스택

- Python / Django 5.2
- Django Channels + Daphne (WebSocket 채팅)
- SQLite
- Pillow (이미지 검증)

## 환경설정

### 1. 요구사항

- Python 3.11 이상

### 2. 저장소 클론 및 가상환경 설정

```bash
git clone <이 저장소 URL>
cd Secure_coding_web
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 내용을 채워주세요.

```
SECRET_KEY=원하는-임의의-긴-문자열
DEBUG=True
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

이 명령 한 번으로 `admin` / `1234@` 관리자 계정이 자동으로 생성됩니다(마이그레이션에 포함된 시딩 코드). 별도로 `createsuperuser`를 실행할 필요는 없으며, 추가 관리자 계정이 필요할 때만 아래 명령을 사용하면 됩니다.

```bash
python manage.py createsuperuser
```

## 실행 방법

```bash
python manage.py runserver
```

`daphne`가 설치되어 있어 위 명령만으로 일반 HTTP 요청과 채팅용 WebSocket이 함께 처리됩니다. 브라우저에서 아래 주소로 접속합니다.

```
http://127.0.0.1:8000
```

- 관리자 페이지: `http://127.0.0.1:8000/admin/`
- 전체 채팅: `http://127.0.0.1:8000/chat/global/`

## 외부(다른 기기)에서 접속하고 싶다면

[ngrok](https://ngrok.com)을 이용해 로컬 서버를 외부에 노출할 수 있습니다.

```bash
ngrok http 8000
```

ngrok이 발급하는 `https://xxxx.ngrok-free.app`(또는 `.ngrok-free.dev`) 주소는 이미 `settings.py`의 `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`에 허용되어 있어 별도 설정 없이 접속할 수 있습니다.
