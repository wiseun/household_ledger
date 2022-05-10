# What is household_ledger
household_ledger는 집에게 가계부를 쓰기 편하게 하기 위해 작성한 script 입니다.

# Description of household_ledger
저희 집은 자산 카테고리가 총 4가지 입니다.
* 식비(1) : 식사 비용
* 간식비(2) : 식사 외에 간식 비용
* 고정지출(3) : 세금, 보험료 등의 고정비
* 변동지출(4) : 고정비 외의 비용

본 script는 연간, 월간, 주간으로 위의 4가 카테고리의 합산 결과를 보여 줍니다.
저희 집은 결산일이 매달 10일이기 때문에 구분을 월이 아닌 id로 합니다.

# Insert data to db
Data 입력 script는 household-ledger-input.py 입니다. 이 script는 아래의 2가지 방식의 입력을 지원 합니다.
* File을 통한 bulk 입력
* Text를 통한 입력
입력 형식은 다음과 같습니다.
"id|날짜|항목|가격|카테고리"
```
4|2022-02-26|쌈밥|20000|1
4|2022-04-26|아빠생일|100000|3
4|2022-04-27|커피|7000|2
4|2022-04-27|빵|7000|2
4|2022-04-27|병원비|56000|4
```
이 script는 1년 단위로 DB를 바꾸도록 구조를 잡았습니다. 년이 바뀌면 household-ledger-input.py과 household-ledger-calculate.py의 household_ledger_name변수를 적절히 바꿔야 합니다. 지금은 2022_household_ledger로 되어 있습니다.
## Insert data using file
파일에 위의 data를 입력해서 한번에 DB에 write 할 수 있습니다.
```
python household-ledger-input.py -f input.txt
```
## Insert data using text
Text 입력을 통해서 DB에 write 할 수 있습니다.
```
python household-ledger-input.py -t "4|2022-05-02|치즈|19000|1"
```
# Check data of db
DB에 있는 data를 확인 하는 기능도 제공 합니다.
## Print about last one week data of db
오늘 부터 일주일 간의 입력 데이터를 확인 할 수 있습니다.
```
python household-ledger-input.py -w
```
## Print about some month data of db
특정 월의 결과를 확인 할 수 있습니다. 저희 집은 결산일이 매달 10일 이기 때문에 정확히는 이전달 10 부터 이번달 9일 까지의 데이터를 확인 합니다. 아래의 예제는 4월의 결과를 출력한 것입니다.
```
python household-ledger-input.py -m 4
```
# Calculate household ledger
Calculate script는 household-ledger-calculate.py 입니다. 가계부의 계산 결과를 주 단위, 월 단위, 연 단위로 볼 수 있습니다.
## Get result of last week
일주일 이전 부터 오늘 까지의 결과를 봅니다.
```
./household-ledger-calculate.py -w
```
## Get result of month
4월 한달 간의 결과를 봅니다.
```
./household-ledger-calculate.py -m 4
```
## Get result ot year
DB 파일을 연에 하나씩 만들도록 구조를 잡았기 때문에 DB에 저장된 모든 결과를 봅니다.
```
./household-ledger-calculate.py -y
```
