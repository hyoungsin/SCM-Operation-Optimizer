Step.2 - SCM MILP PoC폴더/파일 아키텍처

1. 설계 목표

Step.1에서 확정된 기술 스택(Pyomo + HiGHS + FastAPI + React(Vite) + MongoDB)을 기준으로 실제 구현 가능한 개발 폴더 구조를 정의한다.

Front는 Vercel, Back은 별도 Python 서버로 분리 배포하며, 업로드·검증·최적화·결과 다운로드 흐름이 파일 구조상 명확하게 드러나도록 설계한다.

PoC 단계에서는 구현 속도와 구조 명확성을 우선하고, 운영 단계에서 확장 가능한 형태로 parser / validator / optimization / writer 를 분리한다.

2. 확정된 실행 및 저장 기준


set-shipment는 기존 확정 계획 데이터이며, 이를 참고해 향후 26주 선적 제안을 계산한다.

delivery는 w0 실제 입고 수량으로 사용하고, w1부터는 update 규칙을 적용한다.

중복 데이터는 운영환경에서는 오류 대상이지만, 이번 PoC에서는 합산 처리한다.

enabled는 y=1 / n=0 기준으로 정규화한다.

목적함수는 계층형이 아니라 단일 max 방식으로 구현하며, revenue 항이 air penalty보다 크게 작동하도록 설계한다.





3. 최상위 폴더 구조


frontend: React + Vite 기반 업로드, 검증, 실행, 결과 조회 UI

backend: FastAPI + Pyomo + HiGHS + Excel 처리 + MongoDB 연계

data: 업로드 원본, 전처리 결과, 검증 리포트, 결과 파일 저장

docs: 아키텍처, API, business rule, 예시 문서 관리

4. Frontend 폴더 구조


api: FastAPI와 통신하는 요청 모듈을 기능별로 분리한다.

components: 업로드, validation 결과, override 입력, 결과 테이블을 UI 단위로 나눈다.

pages: Upload / Validation / Simulation / Result 흐름을 페이지로 분리한다.

types: input / validation / solve / result 타입을 별도로 관리한다.

5. Backend 폴더 구조


api/routes: upload, validation, simulation, result, health 엔드포인트를 분리한다.

parsers: Excel 13개 sheet 읽기, 컬럼 표준화, 시트 매핑을 담당한다.

validators: 중복, 누락, 주차 범위, mapping, leadtime 등 검사를 담당한다.

services: upload / validation / preprocessing / simulation / result 오케스트레이션을 담당한다.

optimization: Pyomo 세트, 파라미터, 변수, 제약식, 목적함수, solver 실행을 담당한다.

writers: shipment-sea, shipment-air, shortage 결과를 output Excel로 생성한다.

repository: MongoDB 실행 이력, validation 결과, KPI 메타데이터 저장을 담당한다.







6. Data 및 Docs 폴더 구조


uploads/raw: 사용자가 올린 원본 Excel 저장

normalized: enabled 변환, 중복 합산, 주차 정렬 등 전처리 결과 저장

outputs: 최종 output.xlsx 저장

reports: input read report, validation report 저장

docs: Step 문서, API 명세, 입력 규칙, 샘플 설명 문서 관리

7. MongoDB 저장 구조


runs: run_id, 상태, 입력 파일 경로, 출력 파일 경로, solver 정보, 생성 시각 저장

validation_reports: 오류/경고 상세, 중복 합산 처리 여부, 시트별 검사 결과 저장

kpi_summaries: objective value, shortage, air shipment, air cost 등 요약 저장





8. 파일명 규칙 및 설계 원칙

파일은 run_id 기준으로 통일하여 input, validation, output을 연결한다. 예: {run_id}_input.xlsx, {run_id}_validation_report.json, {run_id}_output.xlsx

Excel 파싱 코드와 Pyomo 모델 코드는 분리한다.

validation과 preprocessing은 분리한다.

output writer는 optimization 로직과 분리한다.

PoC 단계에서는 구조 명확성, 변경 용이성, 추후 운영 확장성을 우선한다.
