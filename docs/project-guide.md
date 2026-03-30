1.구현 목표복잡한 생산계획·수요충족·자재제약·리드타임·설비별 CAPA 제약 등이 모두 반영된 MILP 최적화 모델 (예) Google Opensource OR Tools)을 반복 시뮬레이션하며 최적의 값이 도출한다. 오픈소스 최적화 모델을 활용하여 Backend , Frontend code로 연결하며, 파이썬 코드로 작성한다.

Local Mongo DB와 Github – Vercel React기반의 데모용으로 배포할 예정이다. PoC목적으로 정밀도보다는 구현 명확성과 용이성을 우선하여 구현한다.<최적화 목적함수> - output data 기준 shortage 총합 최소화 (근거리 구간 매출 최대화)  - output data 기준 shipment-air 총합 최소화 (air선적금액 최소화)     (10번이상 더 나은 값이 나오지 않으면 중단하고 그때까지의 최적값 ouput 생성)     Maximize Σ( price[p] * demand-priority[w] * demandFulfilled[p,w] )– Σ( air-cost[p] * air-shipment[p,w] )


2. Input Data

업로드하는 Input 파일은 1개이며 형태는 xlsx, 13개 sheet로 구성되어 있다. Openpyxl 도구등을 활용하여, 중복 없이 각 시트를 정확히 읽고 데이터로 연계한다.

set-price

model-site : 제품 모델명 + 판매site

price : 단가

holding-cost : Handling cost (0으로 고정)

backorder-penalty : Shortage발생시 Penalty (0으로 고정)

이후 파라미터 추가 가능





set-demand

model-site : 제품 모델명 + 판매site

w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주 선적계획 수량)- 각 주차별 판매계획 수량을 의미함 (Sales PSI 상 Sales Plan)

이후 적용주차 구간 추가 가능 (예) W26)

set inventory

model-site : 제품 모델명 + 판매site

w0 : 이번주 기준 판매법인 set 기초 재고 (Sales PSI 상 Inventory)

item-inventory

item-code : 해당 제품 모델에 반영되는 item code

w0 : 이번주 기준 material(자재) 기초 재고 (BOH = Beginning on Hand)

item-delivery

item-code : 해당 제품 모델에 반영되는 item code

w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주 자재 입고계획 수량)- 각주차별 공급가능한 자재(item) 입고주차별 수량

bom

item-code : 해당 제품 모델에 반영되는 item code

model-site : 제품 모델명

usage : 제품단위당 투입되는 자재 item 개수 (소요량)

resource

model-site : 제품 모델명 + 판매site

set-resource : 제품 모델이 사용하는 resource name

capacity

resource ((1개 제품은 1개의 resource만 mapping)

w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주 가용 resource 수량)- 각주차별 생산가능한 제품(set) capa수량

set-shipment

model-site : 제품 모델명 + 판매site

from-to : 운송수단 (sea -해상/air-항공/rail-철송)

w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주차별 선적 수량)- 각주차별 확정된 선적계획 수량 (set모델/생산지/판매지/운송수단별 선적 수량)

bod

model-bod : 생산지 (plant site + 운송수단 (sea/rail/air) + sales site)

leadtime : 운송 리드타임(week)

delivery

model-site : 제품 모델명 + 판매site

w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주 가용 입고 예상 수량)- set-shipment sheet의 model-site별 주차별 선적수량을 transportation   set-bod 정보를 mapping한 리드타임을 더한 결과를 각 주차별  delivery수량으로 update

air-mode

model-site : 제품 모델명 + 판매site

air-cost : air로 1대 운송시 발생하는 cost

enabled : air로 운송가능 대상 site-code 여부 (y=1/n=0)

air-leadtime : air 운송시 운송 리드타임 (week)

demand-priority

week : 판매계획 수량

priority : 주차별 판매계획 가중치 (근거리일수록 가중치가 높음으로 설정)w0~w25 (w0은 현재주차를 의미하며 현재주차 포함 26주 판매계획 구간 가중치)





3. 최적화모델 요구사항

업로드된 Input Data를 기반으로 다음 조건을 갖는 MILP 최적화를 수행해야 한다.

🎯 목적함수 (single objective)

Maximize Σ( price[p] * demand-priority[w] * demandFulfilled[p,w] )

– Σ( air-cost[p] * air-shipment[p,w] )

📌 주요 제약 조건

Demand 충족 조건 (set-demand)

DemandFulfilled[p,w] ≤ set-demand[p,w]

Inventory Balance

Inv[p,t] = set-inventory[p,w-1] + delivery[p,w] – demandFulfilled[p,w]

Inventory ≥ 0

Material 사용량 제약 (mat-inventory, mat-available)

Σ( set-shipment[p,w] * bom[m,p] ) ≤ mat-available[m,w]

설비 CAPA 제약 : capacity 기반 제약

Σ( set-shipment [p,w] ) ≤ capacity[e,w](p가 e에 매핑된 경우)

Air shipment plan은air-leadtime로 shipment plan 반영

Initial Inventory는 w0 기준으로 정확히 반영하여 주차별 순차 계산

기간 선호도(앞 기간 우선)

demand-priority(w)을 w0 > w1 > … 로 입력하면 자동 적용됨

조합 최적화를 통해 앞 기간 판매를 우선하는 해 제공






4. Output Data

최적화 수행 후 아래 3개 sheet로 1파일의 출력물을 생성해야 한다.

shipment-sea : sea로 선적되는 model-site/주차별 (w0 ~ w25) 선적수량

shipment-air : air로 선적되는 model-site/주차별(w0 ~ w25) 선적수량

shortage : model-site/주차별(w0 ~ w25) shortage 수량

각 Output은 아래 포맷으로 모두 제공:

wide format (w0~wN)

long format (model-site, Period, Value)

자연 정렬(w0, w1, …, wN)

모든 값은 정수 변환















5. Backend DB - Frontend 구성

MongoDB, Frontend는 React를 활용, input, 실행, output section 구성   <Input Section>

Input : 엑셀 업로드

Input data를 각 sheet별로 sample data를 보여주고 다운로드 받음

simulation하고자 하는 자재 (item-code)를 등록하고 기초재고와(mat-inventory)자재입고계획(mat-available)을 update하면 기존에 입력했던 내용을 overwrite함

capacity는 resource type과 w0 ~ w25까지 수정할수 있도록 함

실행 버튼을 누르면 사용된 solver명과, output data가 출력됨

📌 데이터 정합성 체크 규칙

Input 업로드 파일은 아래를 자동 검사한다.

set 중복 검사

bom 중복 검사

bucket(w1~w25) 정합성

leadtime / air-leadtime 음수 또는 Null 여부

set-resource 매핑 누락 여부

mat-available 기간 누락

set-demand 기간 누락

문제가 발견되면,

즉시 상세 리포트 출력

어떤 시트의 어떤 값이 문제인지 명확히 표기

Input data 정합성 문제 해결 전 최적화 실행 금지



<Output Section>

Output data는 3개 sheet를 각각 보여주고 다운로드도 받을수 있도록 구성함

Summary로 하기 값을 보여준다- 최종 최적화 score (max값), - shortage 수량(max(0,당주 demand plan -당주 기초재고-당주 delivery수량) - air-cost * air-shipment total . 최적화 전과 비교해서 보여주고 인포그래픽으로 시각화하여 보여줌



6. 시스템 운영 Rule

업로드하는 Excel을 기준으로 전 시트를 다시 읽고 전면 반영한다

이전 파일 내용을 캐싱하거나 혼합하지 않는다

파일을 업로드할 때마다 Input Read Report를 생성한다

출력 테이블에서 기간은 반드시 w0~wN 자연 정렬

숫자는 반드시 정수 처리

에러 발생시 사유 설명

Solver는 최적의 Open Source 기준으로 실행하되, Log 수준은 compact 유지
