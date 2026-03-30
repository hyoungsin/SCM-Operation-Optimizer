<가상환경 설치/실행/삭제>

1) 가상환경 생성
python -m venv .venv

2) 가상환경 실행
.venv\Scripts\activate

3) 패키지 설치
pip install -r requirements.txt

4) 서버 실행
uvicorn app.main:app --reload
 : Uvicorn running on http://127.0.0.1:8000 보이면 성공 

<Fast API 실행방법> 
 --> 개인 PC안에 쉽게 설치할수 있는 나만의 간이 I/F 가능한 서버

 1) 서버 실행
먼저 백엔드 서버가 떠 있어야 합니다.터미널에서 backend 폴더 기준:
uvicorn app.main:app --reload

2) 브라우저에서는 Swagger 열기:
http://127.0.0.1:8000/docs

3) API 실행 및 테스트 
Swagger(Test창)에서 upload API를 찾습니다.
Try it out
엑셀 파일 선택 (upload test 기준)
Execute