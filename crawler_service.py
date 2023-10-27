import re

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
    
from dataclasses import dataclass

from models import product_basic, product_nutrition, product_company, product_expire

@dataclass(frozen=True)
class external_url:
    """크롤링에 사용되는 외부 사이트 URL
    Note:
        frozen=True: 불변 객체로 생성
    """
    koreanNet: str = 'http://www.koreannet.or.kr/home/hpisSrchGtin.gs1?gtin='
    retailDB: str = 'https://www.retaildb.or.kr/service/product_info?barcode='
    fatSecret: str = 'https://www.fatsecret.kr/칼로리-영양소/search?q='
    allproductkorea: str = 'http://www.allproductkorea.or.kr/products/info?q='
    foodsafety: str = 'https://www.foodsafetykorea.go.kr/portal/specialinfo/searchInfoProduct.do?menu_grp=MENU_NEW04&menu_no=2815'

def selenium_init() -> webdriver.Chrome:
    """셀레니움 크롤러 사용을 위한 init 함수
    Returns:
        webdriver.Chrome: 셀레니움 크롤러 객체
    """
    webdriver_path = './lib/chrome/driver/chromedriver.exe'
    options = Options()
    # chrome driver option
    options.binary_location = './lib/chrome/browser/App/Chrome-bin/Chrome.exe'
    # options.add_argument('headless')
    options.add_argument('no-default-browser-check')
    options.add_argument('no-first-run')
    options.add_argument('disable-gpu')
    options.add_argument('disable-extensions')
    options.add_argument('disable-default-apps')
    options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(webdriver_path, options=options)

def crawl_prdt_barcd(p:product_basic, bar_cd, nutrition='yes') -> dict:
    """바코드 정보를 입력받아 allproductkorea에서 데이터 크롤링 후 반환
    Args:
        p (product_basic): 프로그램 내부에서 사용하는 제품정보 데이터 클래스
        bar_cd (str): 바코드번호
        nutrition (str, optional): 영양정보 크롤링 여부, Default="yes"
    Returns:
        dict: 크롤링 결과 반환(key:result, msg)
    Note:
        크롤링 실패시 result["result"] = False, result["msg"] = "크롤링 실패"
    """
    
    result = {"result": False, "msg": "크롤링 실패"}
    #크롬드라이버 사용
    driver = selenium_init()
    
    #페이지 실행
    try:
        driver.get(external_url.allproductkorea + '%7B"mainKeyword":"' + bar_cd + \
                '","subKeyword":""%7D')
    except: 
        #예외처리 로직
        driver.close()
        return result
    
    #검색결과 중 첫번째 항목 클릭
    try:
        driver.find_element(By.XPATH, '//*[@class="spl_list"]//*[contains(text(), "' + bar_cd + '")]').click()
    except:
        #예외처리 로직
        driver.close()
        return result

    try:
        #데이터 추출
        p.img_link = driver.find_element(By.XPATH, '//*[@id="imgEl"]').get_attribute('src')
        data_list = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/table/tbody')
        p.bar_cd = bar_cd
        p.rep_prdt_nm = data_list.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/h3").text

        p.prdt_cat = data_list.find_element(By.XPATH, "//*[@data-code='KAN_CODE']").text
        #상품분류 관련 추가처리
        prdt_categorys = p.prdt_cat.split('>')
        p.prdt_cat_class1 = prdt_categorys[0] # 상품 대분류
        p.prdt_cat_class2 = prdt_categorys[1] # 상품 중분류
        p.prdt_cat_class3 = prdt_categorys[2] # 상품 소분류
        p.prdt_cat_class4 = prdt_categorys[3] # 상품 세분류

        p.prdt_nm_kor = data_list.find_element(By.XPATH, "//*[@data-code='PRD_NM_KOR']").text
        #회사정보 관련 추가
        company_list = data_list.find_element(By.XPATH, "//*[@data-code='COMPANIES']").find_elements(By.TAG_NAME, "p")
        for i in range(len(company_list)):
            p.companys.append(product_company(bar_cd=p.bar_cd, company=company_list[i].text))

        p.brnd_nm = data_list.find_element(By.XPATH, "//*[@data-code='IST_BRAND_NM']").text
        p.prdt_nation = data_list.find_element(By.XPATH, "//*[@data-code='COUNTRIES']").text
        p.prdt_compo = data_list.find_element(By.XPATH, "//*[@data-code='PRD_COMP']").text
        p.prdt_volume = data_list.find_element(By.XPATH, "//*[@data-code='ORIGIN_VOLUME']").text
        p.prdt_pac_type = data_list.find_element(By.XPATH, "//*[@data-code='PRD_PAC_TYP']").text
        
        #신고번호 관련 추가처리
        atrb = data_list.find_element(By.XPATH, "//*[@data-code='PRD_ATRB']").text
        atrbs = (atrb.split(','))[-1].split(' ')
        for atrb in atrbs:
            if atrb.isdigit():
                p.prdt_atrb = atrb
                break
        
        result = {"result": True, "msg": ""}
    except:
        pass
    #영양정보도 동시수집
    if nutrition == 'yes':
        try:
            nutrition_list = driver.find_element(By.CLASS_NAME, 'pop_list').find_elements(By.TAG_NAME, 'tr')
            cal, total_carb, sugers, protein, total_fat, saturated_fat, trans_fat, cholesterol, sodium = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            for nutrition_data in nutrition_list:
                case = nutrition_data.find_elements(By.TAG_NAME, 'td')

                if case[0].text == '열량':
                    cal = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '탄수화물':
                    total_carb = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '당류':
                    sugers = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '단백질':
                    protein = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '지방':
                    total_fat = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '포화지방':
                    saturated_fat = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '트랜스지방':
                    trans_fat = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '콜레스테롤':
                    cholesterol = float(re.sub(r'[^0-9.]', '', case[1].text))
                elif case[0].text == '나트륨':
                    sodium = float(re.sub(r'[^0-9.]', '', case[1].text))
                    
            p.nutrition = product_nutrition(bar_cd=p.bar_cd, calories=cal, total_carb=total_carb, sugers=sugers, protein=protein,
                           total_fat=total_fat, saturated_fat=saturated_fat, trans_fat=trans_fat, cholesterol=cholesterol, sodium=sodium)
            
            result = {"result": True, "msg": ""}
        except:
            pass
        
    #브라우저 종료
    driver.close()

    return result
    
def crawl_nut_nm(p:product_basic, prdt_name="", only_serv_size=False) -> dict:
    """제품이름을 활용하여 fatSecret에서 영양정보 데이터 크롤링 후 반환
    Args:
        p (product_basic): 프로그램 내부에서 사용하는 제품정보 데이터 클래스
        prod_name (str): 제품명
    Returns:
        dict: 크롤링 결과 반환(key:result, msg)
    Note:
        해당 메소드는 정확도가 낮을 수 있습니다(검색결과 중 첫번째 항목을 선택합니다)
        크롤링 실패시 result["result"] = False, result["msg"] = "크롤링 실패"
    """
    result = {"result": False, "msg": "크롤링 실패"}
    #크롬드라이버 사용
    driver = selenium_init()

    #페이지 실행
    try:
        if not prdt_name:
            driver.get(external_url.fatSecret + p.prdt_nm_kor)
        else:
            driver.get(external_url.fatSecret + prdt_name)
    except: 
        #예외처리 로직
        driver.close()
        return result
    
    #검색결과 중 첫번째 항목 클릭
    #정확도가 낮으므로 유의해야함
    try:
        driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody/tr/td[1]/div/table[1]').find_element(By.TAG_NAME, 'a').click()
    except:
        #예외처리 로직
        driver.close()
        return result

    try:
        #데이터 가져오기
        data_list = driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody/tr/td[1]/div/table/tbody/tr/td[1]/div[1]')
        # serving size 추출
        serving_size = data_list.find_element(By.CLASS_NAME, 'serving_size_value').text
        
        if only_serv_size:
            p.nutrition = product_nutrition(serving_size = serving_size)
            return result
    except:
        pass
    
    # 영양정보 추출 및 전처리
    try:
        nutrition_list = data_list.find_elements(By.CLASS_NAME, 'nutrient')
        nutrition_list = [x for x in nutrition_list if (bool(x.text) & ('서브' not in x.text) & ('kJ' not in x.text))]
        for i in range(len(nutrition_list)):
            case = nutrition_list[i].text

            if case == '열량':
                cal = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '탄수화물':
                total_carb = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '설탕당':
                sugers = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '단백질':
                protein = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '지방':
                total_fat = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '포화지방':
                saturated_fat = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '트랜스 지방':
                trans_fat = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '콜레스테롤':
                cholesterol = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
            elif case == '나트륨':
                sodium = float(re.sub(r'[^0-9.]', '', nutrition_list[i+1].text))
                
        p.nutrition = product_nutrition(bar_cd=p.bar_cd, calories=cal, serving_size=serving_size, total_carb=total_carb, sugers=sugers, protein=protein,
                                        total_fat=total_fat, saturated_fat=saturated_fat, trans_fat=trans_fat, cholesterol=cholesterol, sodium=sodium)
        
        result = {"result": True, "msg": ""}
    except:
        pass
    #브라우저 종료
    driver.close()

    return result

def crawl_expire_atrb(p:product_basic, atrb) -> dict:
    """품목신고번호를 입력받아 식품안전나라에서 데이터 크롤링 후 반환
    Args:
        p (product_basic): 프로그램 내부에서 사용하는 제품 유통기한 클래스
        atrb (str): 신고번호
    Returns:
        dict: 크롤링 결과 반환(key:result, msg)
    Note:
        크롤링 실패시 result["result"] = False, result["msg"] = "크롤링 실패"
    """
    
    result = {"result": False, "msg": "크롤링 실패"}
    #크롬드라이버 사용
    driver = selenium_init()
    
    #페이지 실행
    try:
        driver.get(external_url.foodsafety)
    except: 
        #예외처리 로직
        driver.close()
        return result
    
    #보고번호 입력
    try:
        driver.find_element(By.XPATH, '//input[@id="prdlst_report_no"]').send_keys(atrb)
        driver.find_element(By.XPATH, '//a[@id="srchBtn"]').click()
    except:
        #예외처리 로직
        driver.close()
        return result
    
    WebDriverWait(driver, 15).until(
        EC.invisibility_of_element_located((By.XPATH, '//*[@id="fancybox-loading"]'))
    )
    
    raw = []
    rows = driver.find_element(By.XPATH, '//*[@id="tbody"]').find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        elements = row.find_elements(By.TAG_NAME, 'td')
        if elements[1].text == atrb:
            raw = elements[4].text.split(' ')
            break
    
    if not raw:
        #예외처리 로직
        driver.close()
        return result
    
    if not any(char.isdigit() for char in raw[0]):
        basis = raw[0]
        best_before_date = raw[1]
    else:
        best_before_date = raw[0]
        
    p.prdt_expire = product_expire(bar_cd = p.bar_cd, best_before_date = best_before_date, basis = basis)
            
    result = {"result": True, "msg": ""}
    return result