# FindSameCardGame

2022년도 3학년 1학기 데이터베이스 텀프로젝트.

## Description [프로젝트 소개]

javascript, html, scss 를 활용한 웹앱 기반 같은 카드 찾기 게임 사이트입니다.
~~https://findsamecard.herokuapp.com/~~ [Heroku 유료 전환으로 사용 중단]


## Dependencies

* javascript
* HTML5, CSS3, SCSS
* Python (Flask)

## Game System [시스템 안내]

* 총 36장의 카드가 필드 위에 무작위하게 섞이며, 카드의 종류는 3~6종류입니다.
* 게임 시작 전 플레이어는 필드 위에 놓인 카드를 3초 간 열람할 수 있습니다.
* 이후 3초의 시간이 지나면, 필드 위에 놓인 카드가 자동으로 뒤집어집니다.
* 플레이어는 필드 위에 놓인 카드 중 짝이 같은 두 카드를 선택해야 합니다.
* 제한 시간은 60초이며, 36개의 카드를 모두 맞출 시 다음 스테이지로 넘어갑니다.
* 제한 시간이 모두 소거되었다면 게임이 종료되며, 자신의 최종 스코어가 출력됩니다.

## Authors [제작자]

* RookieAND_ (https://github.com/RookieAND)

## Version History

* 0.4
    * Add dynamic-login feedback feature.
    * Add tier system per player's best score.
    * Fixed some issue related to databases.
    * Add safety-email verification system.
* 0.3
    * Add flask back-end part of minigame Web.
    * Add email-verification register system.
    * Add user profile, leaderboard, and statistic.
* 0.2
    * Add auto - stage difficulty setting system.
    * Add stage system and combo system.
    * change maximum limit time from 120 to 60.
* 0.1
    * Initial Release

## Getting Started
### 로컬 기동
로컬 환경에서 Flask 앱을 기동하려면 아래 명령어를 사용하세요.
```bash
python run.py
```

### Dockeer Compose 기동
Docker와 Docker Compose가 설치되어 있어야 합니다.
docker-compose.yml 파일 예시:
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: minigame-app
    env_file:
      - .env
    ports:
      - "8000:8000"
```
Docker Compose를 사용하여 앱을 기동하려면 아래 명령어를 사용하세요.
```bash
docker-compose up --build
```

### Configuration
.env 파일 설정

| Key | Description | example           |
|-----|-------------|-------------------|
| FLASK_APP | Flask 앱 메인 파일명 (예: run.py) | run.py            |
| FLASK_ENV | Flask 환경 설정 (development/production) | development       |
| SECRET_KEY | Flask 세션 및 보안용 비밀 키 | your_secret_key   |
| DATABASE_URL | 데이터베이스 연결 URL | sqlite:///site.db |
| MAIL_SERVER | 이메일 서버 주소 | smtp.example.com  |
| MAIL_PORT | 이메일 서버 포트 | 587               |
| MAIL_USERNAME | 이메일 서버 사용자 이름 | username          |
| MAIL_PASSWORD | 이메일 서버 비밀번호 | password          |
| MAIL_USE_TLS | 이메일 서버 TLS 사용 여부 (True/False) | True              |
| MAIL_USE_SSL | 이메일 서버 SSL 사용 여부 (True/False) | False             |



## License

해당 프로젝트의 라이센스는 [MIT] License 규정을 지키고 있습니다.
