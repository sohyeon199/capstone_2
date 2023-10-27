from models import product_basic, product_nutrition, product_expire
from database import db_session
from sqlalchemy import select, insert

from crawler_service import crawl_prdt_barcd, crawl_nut_nm, crawl_expire_atrb

def get_prdt_barcd(bar_cd: str) -> product_basic:
    """바코드를 입력받아 db조회, 크롤링을 수행하여 반환하는 서비스
    Args:
        bar_cd (str): 바코드
    Returns:
        product_basic: 제품정보 데이터 클래스
    """
    p = product_basic()
    p.bar_cd = bar_cd
    
    result = db_session.execute(
        select(product_basic).where(product_basic.bar_cd == p.bar_cd)
    ).first()
    
    if result is None:
        if not crawl_prdt_barcd(p, bar_cd)['result']:
            return None
        else:
            db_session.add(p)
            db_session.commit()
    else:
        p = result[0]
    
    return p

def get_nut_nm(bar_cd: str, prod_name: str) -> product_nutrition:
    if bar_cd == "" and prod_name == "":
        return None
    
    p = product_basic()
    p.bar_cd = bar_cd
    
    if bar_cd != "" and bar_cd is not None:
        result = db_session.execute(
            select(product_nutrition).where(product_nutrition.bar_cd == p.bar_cd)
        ).first()
        
        if result is None:
            result = db_session.execute(
                select(product_basic).where(product_basic.bar_cd == p.bar_cd)
            ).first()
    else:
        result = db_session.execute(
            select(product_basic).where(product_basic.prdt_nm_kor == prod_name)
        ).first()
    
    if result is None:
        if bar_cd:
            if crawl_prdt_barcd(p, bar_cd)['result']:
                if p.nutrition is None:
                    if not crawl_nut_nm(p, p.prdt_nm_kor)['result']:
                        #나머지 경우는 모두 정상
                        return None
                    
                db_session.add(p)
                db_session.commit()
            else:
                return None
        else:
            if not crawl_nut_nm(p, prod_name)['result']:
                return None
    
    elif type(result[0]) is product_nutrition:
        p.nutrition = result[0]
    
    elif result[0].nutrition is None:
        p = result[0]
        if not crawl_nut_nm(p, prod_name)['result']:
            return None
        
        db_session.add(p)
        db_session.commit()
    else:
        p = result[0]
    
    return p.nutrition

def get_expire_atrb(bar_cd:str="", atrb:str="") -> product_expire:
    if bar_cd == "" and atrb == "":
        return None
    
    p = product_basic()
    p.bar_cd = bar_cd
    
    if bar_cd != "" and bar_cd is not None:
        result = db_session.execute(
            select(product_expire).where(product_expire.bar_cd == p.bar_cd)
        ).first()
        if result is None:
            result = db_session.execute(
                select(product_basic).where(product_basic.bar_cd == bar_cd)
            ).first()
    
    if result is None:
        if bar_cd:
            if crawl_prdt_barcd(p, bar_cd)['result']:
                if p.prdt_atrb is not None:
                    if not crawl_expire_atrb(p, p.prdt_atrb)['result']:
                        return None
                    db_session.add(p)
                    db_session.commit()
                else:
                    return None
            else:
                return None
        else:
            if not crawl_expire_atrb(p, p.prdt_atrb)['result']:
                return None
    
    elif type(result[0]) is product_expire:
        return result[0]
    
    elif result[0].prdt_expire is None:
        p = result[0]
        if not crawl_expire_atrb(p, result[0].prdt_atrb)['result']:
            return None
        
        db_session.add(p)
        db_session.commit()
        
    else:
        p = result[0]
    
    return p.prdt_expire
    

def get_rec_nut(gender, age, height, weight, activity_level='2') -> dict:
    """권장 소비칼로리, 영양성분 등을 계산하여 반환하는 함수
    Args:
        p (product_info): 프로그램 내부에서 사용하는 제품정보 데이터 클래스
        gender (str): 성별
        age (str): 나이
        height (str): 키
        weight (str): 몸무게
        activity_level (str, optional): 활동지수, Default='2', 1:비활동적, 2:저활동적, 3:활동적, 4:매우활동적, 5:극도활동적
    Returns:
        dict: 크롤링 결과 반환(key:result, msg)
    Note:
        크롤링 실패시 result["result"] = False, result["msg"] = "크롤링 실패"
    """
    result = {}

    if gender == 'M':
        calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == 'F':
        calories = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    if activity_level == '2':
        calories *= 1.375
    elif activity_level == '1':
        calories *= 1.2
    elif activity_level == '3':
        calories *= 1.55
    elif activity_level == '4':
        calories *= 1.725
    elif activity_level == '5':
        calories *= 1.9
    
    #권장 탄수화물 : 전연령 동일 55~65%, 중위값 60%
    total_carb = (calories * 0.6) / 4
    #권장 지방 : 3세 이상 동일, 15~30%, 중위값 22.5% / 3세 이하 20~35%, 중위값 27.5%
    if age >= 3:
        total_fat = (calories * 0.225) / 9
    else:
        total_fat = (calories * 0.275) / 9
    #권장 단백질 : 탄수화물, 지방 뺀 나머지
    if age >= 3:
        protein = (calories * 0.175) / 9
    else:
        protein = (calories * 0.125) / 9
    
    #권장 첨가당 : 총 에너지섭취량의 10-20%로 제한, 식품의 조리 및 가공 시 첨가되는 첨가당은 총 에너지 섭취량의 10% 이내로 섭취
    sugers = (calories * 0.1) / 4

    #충분 나트륨 : 근거자료 도표 참고할것, 임산부/수유부는 1500이나 여기서는 제외함
    if gender == 'M':
        if age <= 2:
            sodium = 810
        elif age <= 5:
            sodium = 1000
        elif age <= 8:
            sodium = 1200
        elif age <= 64:
            sodium = 1500
        elif age <= 74:
            sodium = 1300
        else:
            sodium = 1100

    elif gender == 'F':
        if age <= 2:
            sodium = 810
        elif age <= 5:
            sodium = 1000
        elif age <= 8:
            sodium = 1200
        elif age <= 64:
            sodium = 1500
        elif age <= 74:
            sodium = 1300
        else:
            sodium = 1100
            
    result['calories'] = calories
    result['total_carb'] = total_carb
    result['total_fat'] = total_fat
    result['protein'] = protein
    result['sugers'] = sugers
    result['sodium'] = sodium
    
    return result
