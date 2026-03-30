Step.4 - SCM MILP PoC UI 구현

Upload / Validation / Solve / Download 화면 로직 및 기준 정의

1. 설계 목표

Step.1에서 확정된 기술 스택(Pyomo + HiGHS + FastAPI + React(Vite) + MongoDB)과 Step.2의 폴더 구조, Step.3의 파싱/검증/표준화/solve 흐름을 사용자 UI 기준으로 연결한다.

UI는 단순히 화면을 보여주는 역할이 아니라, 업로드된 Excel이 어떤 상태인지, 보정 가능한지, solve 가능한지, 어떤 결과가 생성되었는지를 단계적으로 명확히 전달해야 한다.

PoC 단계에서는 복잡한 다중 메뉴형 제품이 아니라 단일 실행 흐름 중심의 1-page 또는 wizard형 UI를 권장한다. 사용자는 Upload → Validation → Solve → Download의 순서를 자연스럽게 따라가야 한다.

2. 화면 구성 원칙

• 메인 메뉴는 Upload / Validation / Solve / Result 4단계로 고정한다.

• 현재 단계와 완료 단계를 상단 stepper로 항상 표시한다.

• 한 단계에서 필수 조건이 충족되지 않으면 다음 단계로 넘어갈 수 없도록 한다.

• Input 업로드 파일은 매 실행마다 전체를 다시 읽으며, 이전 실행 데이터와 혼합하지 않는다.

• Validation에서 error가 존재하면 Solve 버튼은 비활성화한다. warning만 존재하면 사용자가 내용을 확인한 뒤 진행 가능하다.

• 모든 기간 컬럼 표시는 w0, w1, ..., w25 자연 정렬을 유지한다.

• 숫자 표시는 정수 기준이며, UI에서도 소수점 없이 보여준다.

3. 전체 화면 흐름

기본 동선은 4-step main flow로 구성하고, 우측 또는 하단에 실행 이력(Run History) 영역을 둔다. 사용자는 현재 run의 상태를 보면서 필요 시 과거 결과를 재조회할 수 있어야 한다.




4. 화면별 상세 정의

4.1 Upload 화면

Upload 화면은 사용자가 13개 sheet로 구성된 input.xlsx를 등록하고, 현재 파일이 어떤 구조로 읽혔는지를 1차 확인하는 영역이다.

업로드 직후 backend는 input read report를 생성하며, 시트명, row 수, 컬럼 수, 필수 컬럼 존재 여부를 즉시 반환한다.

화면 구성

• 파일 업로드 영역: drag & drop + 파일 선택 버튼 동시 제공

• 허용 파일 형식 표시: .xlsx 1개 파일만 허용

• 파일 메타정보 카드: 파일명, 크기, 업로드 시각, run_id

• Input Read Summary: 13개 시트별 row 수 / 컬럼 수 / 읽기 성공 여부

• 샘플 미리보기 탭: sheet별 상위 N행 표시

• 다음 단계 이동 버튼: Validation 실행 또는 Validation 화면으로 이동

버튼 및 상태 기준

예외 처리

• xlsx 외 형식 업로드 시 즉시 차단하고 허용 포맷 메시지를 표시한다.

• 필수 시트 누락 또는 파일 손상 시 read failed 상태로 표시하고 상세 사유를 제공한다.

• 새 파일 업로드 시 이전 파일의 미리보기, validation, solve 결과는 모두 초기화한다.



4.2 Validation 화면

Validation 화면은 최적화 실행 전 데이터 정합성과 보정 여부를 사용자가 확인하는 핵심 단계다.

Step.3에서 정의한 규칙에 따라 중복, 음수, null, 주차 컬럼 누락, key mapping 누락 등을 검사하고 결과를 error / warning / info로 구분해 보여준다.

• Validation Summary 카드: error 수, warning 수, info 수, 검사 시각

• 시트별 검사 결과 테이블: sheet, rule, status, count

• 상세 이슈 테이블: sheet명, key, 컬럼, 원본값, 처리값, 처리 규칙

• 필터: All / Error / Warning / Info

• 다운로드: validation_report.json 또는 csv 다운로드

실행 차단 기준

버튼 기준

• Re-upload: 항상 활성. 이전 단계로 돌아가 새 파일 등록 가능.

• Proceed to Solve: error=0일 때만 활성.

• Download Validation Report: validation 완료 후 활성.

• Show Corrected Preview: warning이 1건 이상일 때 활성. 보정 후 표준 데이터 일부를 보여준다.




4.3 Solve 화면

Solve 화면은 solver 실행 전 최종 확인과 실행 상태 모니터링을 담당한다.

PoC 단계에서는 solver 옵션을 최소화하되, 사용자가 어떤 조건으로 실행되는지는 명확히 보이도록 한다.

• Solve Summary 카드: solver(HiGHS), run_id, 입력 파일명, validation 결과 요약

• Execution Option 영역: 기본 solver 표시, compact log 사용 여부, 실행 시각

• Solve 버튼

• 실행 진행 상태 영역: queued / running / completed / failed

• 로그 패널: compact solver log, 주요 단계(progress) 메시지

실행 중 상태 전이

Solve 전 체크 조건

• 업로드 파일 존재

• Validation 완료

• Error 0건

• 표준화 데이터 생성 완료

• backend health 정상

실행 결과로 즉시 받아야 하는 값

• solve status

• termination condition

• objective value

• solving time

• total shortage

• total air shipment

• total air cost

4.4 Result / Download 화면

Result 화면은 최적화 결과를 사용자가 바로 확인하고, output.xlsx를 다운로드하는 단계다.

출력은 shipment-sea, shipment-air, shortage 3개 sheet를 기준으로 하며, wide format과 long format 조회를 모두 지원하는 것이 바람직하다.

• KPI Summary 카드: objective, total shortage, total air shipment, total air cost, solving time

• Before vs After 비교 카드: 기존 plan 기준 값과 최적화 결과 비교

• 결과 테이블 탭: shipment-sea / shipment-air / shortage

• 표현 옵션: Wide 보기 / Long 보기

• 정렬 기준: model-site, week 자연 정렬

• 다운로드 버튼: output.xlsx, result_summary.json

시각화 기준

• Shortage 비교는 bar chart 또는 KPI delta 카드로 표시한다.

• Air shipment / air cost는 trend 또는 total 카드로 표시한다.

• PoC 단계에서는 과도한 차트보다 수치와 표 중심 구성이 우선이며, chart는 2~3개 핵심 지표만 제공한다.

결과 테이블 규칙

• 모든 수치는 정수형 표시

• 기간 컬럼은 반드시 w0~w25 자연 정렬

• 빈 값은 0으로 표시

• 다운로드 파일명은 {run_id}_output.xlsx 기준 사용




5. 공통 UI 컴포넌트 기준

• 상단 Stepper: 현재 단계, 완료 단계, 차단 상태를 한눈에 보여준다.

• Run Summary Bar: run_id, 파일명, solver, 현재 상태 표시.

• Status Badge: success / warning / error / running 색상 체계 통일.

• Toast 또는 Alert 영역: 업로드 성공, validation 완료, solve 실패 등 이벤트 메시지 통합.

• Table Filter/Search: sheet명, model-site, item-code 기준 검색 가능.

6. API 연계 기준




7. 상태 관리 기준

Frontend 상태는 최소한 currentRun, uploadState, validationState, solveState, resultState로 분리한다.

새 파일을 업로드하면 currentRun이 변경되며 validation, solve, result 상태는 초기화된다.

solve 완료 후 result 조회 시 run_id 기준으로만 읽어오며, 다른 run과 혼합 표시하지 않는다.

8. 예외 처리 및 사용자 메시지 기준






9. PoC 완료 기준

• 사용자가 1개 xlsx 파일을 업로드할 수 있다.

• 업로드 직후 input read report와 sheet preview를 볼 수 있다.

• Validation 결과가 error / warning / info로 구분되어 보인다.

• error가 0건일 때만 Solve 버튼이 활성화된다.

• solve 진행 상태와 완료 KPI가 화면에 표시된다.

• shipment-sea / shipment-air / shortage 결과를 표로 확인할 수 있다.

• output.xlsx를 다운로드할 수 있다.

10. 구현 우선순위

11. 다음 활용 방식

본 Step.4 문서는 Cursor 또는 Codex에 그대로 전달하여 frontend page 구성, API 연결, 상태 관리 스토어, 공통 컴포넌트 설계의 기준 문서로 사용할 수 있다.
실제 구현 시에는 frontend/pages 기준으로 UploadPage, ValidationPage, SolvePage, ResultPage를 나누거나, 단일 Wizard 페이지 안에서 step panel로 구현해도 무방하다. 다만 상태 차단 규칙과 run_id 기준 데이터 분리는 반드시 유지해야 한다.
작성 기준: Step.1~Step.3 확정사항과 사용자 요구사항을 연결한 UI 기준 문서
