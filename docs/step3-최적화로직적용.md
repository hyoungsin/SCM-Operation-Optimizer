Step.3 - SCM MILP PoC 최적화 로직 적용

1. 설계 목표

Step.1에서 확정된 기술 스택(Pyomo + HiGHS + FastAPI + React(Vite) + MongoDB)과 Step.2에서 설계 완료한 frontend / backend / data / docs 구조를 기준으로, 실제 최적화 로직 적용 단계를 정의한다.

본 단계의 범위는 파싱 → 검증 → 표준화 → 모델 생성 → solve → output writer 전체 흐름이며, Excel 입력이 solver에 들어가기 전 어떤 방식으로 해석·가공·기록되는지를 명확히 하는 것이다.

PoC 단계에서는 운영 확장성을 고려하여 parser / validator / standardization / optimization / writer를 분리하고, 추후 규칙 추가가 가능하도록 모듈형 구조를 유지한다.


2. 운영 Input Data 해석 원칙

실제 운영 input data는 시스템 데이터이므로 원칙적으로 구조 오류, 중복, 음수, null이 발생하지 않는다고 가정한다.

다만 PoC에서는 테스트 데이터, 샘플 데이터, 수작업 정리 데이터가 일부 섞일 수 있으므로 아래 방어 규칙을 적용한다.

중복 row가 있을 경우 오류로 중단하지 않고 동일 key 기준으로 합산 처리한다.

값이 음수이거나 null일 경우 0으로 간주하여 후속 로직에 반영한다.

위와 같은 상황이 발생하면 validation warning 정보를 반드시 생성하고, 어떤 값을 어떻게 보정했는지 리포트와 로그에 표시한다.

즉, PoC에서는 solve 중단보다 실행 가능성과 처리 이력의 투명성을 우선한다.

3. Step.3 전체 실행 흐름

Parsing: 업로드된 13개 sheet Excel을 읽어 sheet별 DataFrame / 내부 객체로 변환한다.

Validation: 필수 시트, 필수 컬럼, key 정합성, 주차 컬럼, 값 범위, 보정 발생 여부를 검사하고 warning / info를 기록한다.

Standardization: 중복 합산, 음수·null 보정, week 정렬, enabled 정규화, long format 변환 등 모델 입력 형식으로 재구성한다.

Model Build: Pyomo set / parameter / variable / constraint / objective를 생성한다.

Solve: HiGHS를 호출하여 최적해를 계산하고 status, objective, KPI를 수집한다.

Output Writer: shipment-sea / shipment-air / shortage 결과 Excel과 요약 정보를 생성한다.

4. 단계별 상세 설계

4.1 Parsing

대상 시트: set-price, set-demand, set-inventory, item-inventory, item-delivery, bom, resource, capacity, set-shipment, bod, delivery, air-mode, demand-priority

시트명 존재 여부, 필수 컬럼 존재 여부, w0~w25 컬럼 구성을 확인한다.

숫자형 컬럼은 숫자로 변환하고, 공백 및 불필요한 문자열은 1차 정리한다.

raw 입력은 그대로 보존하고, 이후 단계는 parsed 데이터 사본을 기준으로 처리한다.

4.2 Validation

실운영 기준 오류 가정은 없지만, PoC에서는 방어적으로 중복·음수·null·주차 누락 여부를 확인한다.

중복 row는 warning으로 기록한 뒤 key 기준 합산 처리 대상으로 넘긴다.

음수 또는 null 값은 warning으로 기록한 뒤 0으로 치환 대상으로 넘긴다.

set-demand, bom, resource, air-mode, capacity 등 주요 시트의 key mapping 연결 가능 여부를 점검한다.

validation 결과는 error / warning / info 구조로 저장하되, 본 PoC에서는 보정 가능한 항목은 warning 중심으로 처리한다.

4.3 Standardization

동일 key row는 합산하여 단일 표준 row로 만든다.

숫자 컬럼의 음수 또는 null 값은 0으로 치환한다.

enabled 값은 y=1, n=0 기준으로 정규화한다.

week 컬럼은 w0, w1, w2 ... w25 자연 정렬을 강제한다.

wide format 데이터를 모델 입력에 적합한 long format으로 변환한다.

보정 전 원본값, 보정 후 값, 적용 규칙은 warning report에 함께 남긴다.

4.4 Model Build

Pyomo 기준 set, parameter, variable, constraint, objective를 생성한다.

주요 set은 model-site, item-code, resource, week, shipment mode(sea / air)로 구성한다.

주요 parameter는 demand, price, init inventory, item delivery, bom usage, capacity, leadtime, air cost, demand priority 등을 포함한다.

목적함수는 단일 max 방식이며, revenue 항이 air penalty보다 크게 작동하도록 설계하여 shortage 감소가 먼저 반영되도록 한다.

4.5 Solve

기본 solver는 HiGHS를 사용하며, solve status / termination condition / objective value / solving time을 저장한다.

해를 구한 뒤 demand fulfillment, shortage, shipment-sea, shipment-air, inventory balance 결과를 추출한다.

PoC에서는 계산 실패보다 원인 추적이 중요하므로 solver log와 validation summary를 함께 관리한다.

4.6 Output Writer

최종 결과는 shipment-sea, shipment-air, shortage 3개 시트 Excel로 생성한다.

추가로 objective value, total shortage, total air shipment, solve status 등 summary 정보를 저장한다.

warning 발생 시 결과 파일 또는 별도 report에 보정 이력을 함께 남겨 사용자가 처리 방식을 확인할 수 있도록 한다.















5. Backend 모듈 역할 분리

parsers: Excel workbook 읽기, 시트 매핑, 컬럼 표준화

validators: 중복, null, 음수, week, mapping, 필수 컬럼 검사 및 warning 생성

services: parsing → validation → standardization → solve 전체 orchestration

optimization: Pyomo model builder, constraint, objective, solver runner

writers: 결과 Excel 및 summary report 생성

repository: MongoDB에 run 이력, validation report, KPI, warning 정보 저장

6. 산출물 및 저장 기준

input read report: 시트별 row 수, 컬럼 수, 필수 컬럼 확인 결과

validation report: warning / info 목록, 보정 발생 건수, 처리 방식

normalized data: 중복 합산 및 0 치환까지 반영한 모델 입력용 표준 데이터

solve result: objective, solver status, KPI, 실행 시간

output Excel: shipment-sea / shipment-air / shortage

MongoDB 저장 항목: run_id, 파일 메타정보, validation summary, warning detail, KPI summary

7. Step.3 완료 기준

13개 sheet parsing 로직이 동작한다.

중복 합산, 음수·null 0 치환, warning 기록 규칙이 구현된다.

표준화된 모델 입력 구조가 확정된다.

Pyomo model build와 HiGHS solve가 연결된다.

output writer가 결과 Excel을 생성한다.

warning 및 처리 내역이 report와 저장소에 남는다.

8. 구현 우선순위

1순위: workbook parser + validation warning 구조
2순위: standardization 규칙(중복 합산, 음수·null 0 치환)
3순위: model builder + solver runner
4순위: output writer + summary report + MongoDB 저장
