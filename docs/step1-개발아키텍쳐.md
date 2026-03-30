Step.1 - SCM MILP PoC 개발 아키텍처

1. 프로젝트 목표

입력: 13개 시트로 구성된 1개 Excel 파일
(set-price, set-demand, set-inventory, item-inventory, item-delivery, bom, 
resource, capacity, set-shipment, bod, delivery, air-mode, demand-priority).
출력: 3개 시트로 구성된 결과 Excel 파일(shipment-sea, shipment-air, shortage).
핵심 목표: 복잡한 생산계획·수요충족·자재제약·리드타임·설비 CAPA 제약을 동시에 반영한 MILP 최적화 모델을 구현한다.
PoC 우선순위: 정밀도보다 구현 명확성, 구조의 이해 용이성, 추후 확장성에 우선순위를 둔다.

2. 목적함수 및 최적화 방향

최종 방향: 계층형(lexicographic) 목적이 아니라, 단일 최적화 함수의 최대값을 찾는 방식으로 구현한다.

1순위 해석상 shortage 최소화가 핵심이지만, 실제 구현은 매출 항의 가중치가 air 비용보다 충분히 크도록 설계하여 shortage가 먼저 줄어들도록 한다.

2순위 성격의 air 사용 억제는 목적함수를 통해 shortage를 피하는 매출 이득이 air 비용보다 더 크게 작동하도록 수식을 구성한다.

권장 목적함수 구조Maximize Σ(price[p] × demand-priority[w] × demandFulfilled[p,w]) − Σ(air-cost[p] × air-shipment[p,w]).

조기 종료 요구사항(“10번 이상 더 나은 값이 없으면 중단”)은 solver 설정 또는 탐색 반복 제어 옵션으로 반영하되, PoC 1차에서는 time limit / mip gap / no-improvement 기준을 파라미터화한다.


3. 확정된 입력 해석 규칙

4. 1단계 최종 권장 개발 아키텍처

<개발 도구>

모델링: Pyomo

Solver: HiGHS 우선, 필요 시 SCIP 전환

백엔드: FastAPI
프론트엔드: React + Vite

DB: MongoDB

배포: Front는 Vercel, Back은 별도 Python 서버

개발 방식: ChatGPT로 설계 확정 → Codex로 폴더/파일 초안 생성 → Cursor에서 단계별 구체화

<개발 아키텍처>

React + Vite (업로드/검증/실행/다운로드 UI)

↓ REST API

FastAPI (Excel 파싱, 검증, 모델 구성, Solver 실행, 결과 파일 생성)

↓

MongoDB (실행 이력, 메타데이터, 검증 결과, KPI 저장)

↓

파일 저장소(로컬 폴더 또는 추후 외부 저장소): input/output Excel

Pyomo

SCM 제약식을 business rule 관점에서 읽고 수정하기 쉽다. 생산, BOM, 리드타임, CAPA, shortage 수식이 많은 문제에서 모델 가독성이 높다.

HiGHS

PoC 초기 설치와 실행이 비교적 단순하다. 추후 구조를 유지한 채 SCIP 등 다른 solver로 교체할 수 있다.

FastAPI

React 화면에서 업로드한 파일을 받아 파이썬 최적화 코드를 실행하고 결과를 반환하는 데 적합하다.

React + Vite

빠르게 UI를 만들 수 있고, 파일 업로드·표시·다운로드 화면을 가볍게 구성하기 좋다.

MongoDB

실행 이력과 검증 리포트, KPI, 파일 경로를 저장하기에 적합하다. 결과 Excel 자체는 파일 저장소에 두고 DB에는 메타정보를 남기는 구조가 단순하다.

6. 배포 전략

초기 PoC: 개인 PC에서 FastAPI 서버를 실행한 상태로 유지하여 개발·테스트를 진행한다. 즉 PC가 켜져 있고 서버 프로세스가 살아 있으면 React 화면이 해당 서버를 호출할 수 있다.

주의: 개인 PC 서버는 PC 종료, IP 변경, 방화벽/포트 문제에 취약하므로 외부 공유용으로는 불안정하다.

후속 배포 대안: Heroku는 사용 경험이 있다면 후보가 될 수 있다. 다만 solver 바이너리 설치, 장시간 MILP 실행, ephemeral filesystem 특성을 반드시 검토해야 한다.

따라서 권장 순서는 로컬 서버에서 기능 완성 → Heroku로 백엔드 배포 검증 → 필요 시 worker 분리 또는 저장소 구조 개선이다.

7. 데이터 저장 전략

MongoDB에는 input/output 파일 그 자체보다 실행 이력, 검증 결과, KPI 요약, 파일 경로를 저장한다.

실제 input.xlsx / output.xlsx는 서버 폴더 또는 별도 파일 저장소에 둔다.

PoC 초기에는 uploads/, outputs/ 폴더 기반 저장이 가장 단순하다.

Heroku 등으로 이전할 경우 로컬 디스크 의존을 줄이고 외부 object storage 또는 GridFS 사용 여부를 검토한다.



8. 1단계 산출물 범위

개발 툴과 기술스택 확정

입력 데이터 해석 규칙 확정

목적함수 방향과 solver 선택 원칙 확정

배포 초안(로컬 PC → 추후 Heroku) 확정

다음 단계(폴더 구조 설계)로 넘어가기 위한 전제 정리 완료

9. 다음 작업 순서

Step.2: 폴더/파일 구조 설계 (input 업로드 폴더, backend/frontend 연계, output 생성 위치 정의)

Step.3: 최적화 로직 적용 순서 정의 (파싱 → 검증 → 표준화 → 모델 생성 → solve → output writer)
Step.4: UI 구현 (Upload / Validation / Solve / Download 화면)
