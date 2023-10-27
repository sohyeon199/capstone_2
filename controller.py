from flask import Blueprint, request, make_response, jsonify, send_from_directory
import json
from urllib.parse import unquote

from service import *

#동시성 문제 발생가능!

#바꺼야댐!
from crawler_service import *

#여기 컨트롤러에서 사용하는 주소에 모두 api를 붙여야 함
home = Blueprint('home', __name__, url_prefix='/api', 
                 template_folder='t-templates', static_folder='t-static')

@home.route('/')
def push_test():
    from flask import render_template
    
    return render_template('index.html')

@home.route('/firebase-messaging-sw.js', methods=['GET'])
def sw():
    response = make_response(send_from_directory('t-static', 'firebase-messaging-sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    
    return response

    
#바코드 정보를 입력받아 제품 기본정보를 JSON으로 반환
#입력데이터 : 바코드번호 13자리(필수)
#반환데이터 : 바코드번호, 상품명(국문), 구성정보, 상품형태, 이미지링크
@home.route('/search/basicinfo')
def search_prod_basic_info():
    bar_cd = request.args.get('bar_cd')
    
    product = get_prdt_barcd(bar_cd)
    if product is None:
        return make_response(
            json.dumps({"result":"fail", "err_code":"401", "err_msg":"크롤링 실패. 관리자에게 문의해 주세요"}, ensure_ascii=False)
        )
    model = {
        'bar_cd': product.bar_cd,
        'prdt_nm_kor': product.prdt_nm_kor,
        'prdt_compo': product.prdt_compo,
        'prdt_pac_type': product.prdt_pac_type,
        'img_link': product.img_link,
    }
    
    return make_response(
        json.dumps(model, ensure_ascii=False)
    )

#바코드를 입력받아 제품 상세정보를 JSON으로 반환
#입력데이터 : 바코드번호 13자리(필수)
#반환데이터 : 바코드번호, 상품명(국문), 구성정보, 상품형태, 이미지링크, 상품대분류, 상품중분류, 상품소분류, 상품세분류, 회사정보, 국가정보
@home.route('/search/detailinfo')
def search_prod_detail_info():
    bar_cd = request.args.get('bar_cd')

    product = get_prdt_barcd(bar_cd)
    if product is None:
        return make_response(
            json.dumps({"result":"fail", "err_code":"402", "err_msg":"크롤링 실패. 관리자에게 문의해 주세요"}, ensure_ascii=False)
        )
    
    model = {
        'bar_cd': product.bar_cd,
        'prdt_nm_kor': product.prdt_nm_kor,
        'prdt_compo': product.prdt_compo,
        'prdt_pac_type': product.prdt_pac_type,
        'img_link': product.img_link,
        'prdt_cat': product.prdt_cat,
        'prdt_cat_class1': product.prdt_cat_class1,
        'prdt_cat_class2': product.prdt_cat_class2,
        'prdt_cat_class3': product.prdt_cat_class3,
        'prdt_cat_class4': product.prdt_cat_class4,
        'prdt_nation': product.prdt_nation,
        'companys': [c.company for c in product.companys]
    }
    
    return make_response(
        json.dumps(model, ensure_ascii=False)
    )

#바코드/제품명을 입력받아 영양정보를 JSON으로 반환
#입력데이터 : 바코드번호, 제품명 (둘중하나는 필수, 바코드 우선적용)
#반환데이터 : 바코드번호, 서빙사이즈, 열량, 탄수화물, 단백질, 지방, 설탕당, 나트륨
@home.route('/search/nutriinfo')
def search_prod_nutri_info():
    bar_cd = request.args.get('bar_cd')
    prod_name = request.args.get('prod_name')

    nutrition = get_nut_nm(bar_cd, prod_name)
    if nutrition == None:
        return make_response(
            json.dumps({"result":"fail", "err_code":"403", "err_msg":"크롤링 실패. 관리자에게 문의해 주세요"}, ensure_ascii=False)
        )
    model = {
        'bar_cd': nutrition.bar_cd,
        'calories': nutrition.calories,
        'total_carb' : nutrition.total_carb,
        'protein' : nutrition.protein,
        'total_fat' : nutrition.total_fat,
        'sugers' : nutrition.sugers,
        'sodium' : nutrition.sodium,
        'serving_size' : nutrition.serving_size
    }
    
    return make_response(
        json.dumps(model, ensure_ascii=False)
    )

#유통기한 정보조회
@home.route('/search/expiredate')
def search_expire_date():
    bar_cd = request.args.get('bar_cd')
    atrb = request.args.get('atrb')
    
    expire = get_expire_atrb(bar_cd, atrb)
    if expire is None:
        return make_response(
            json.dumps({"result":"fail", "err_code":"404", "err_msg":"지원하지 않는 제품입니다. 관리자에게 문의해 주세요"}, ensure_ascii=False)
        )
    model = {
        'bar_cd': expire.bar_cd,
        'best_before_date': expire.best_before_date,
        'basis': expire.basis
    }
    
    return make_response(
        json.dumps(model, ensure_ascii=False)
    )

#이름을 입력받아 사전DB에서 리스트 상위 n개를 JSON으로 반환
#입력데이터 : 바코드번호, 제품명 (둘중하나는 필수, 바코드 우선적용), 목록사이즈(기본값 10)
#반환데이터 : 제품명, 바코드번호, 이미지 주소
@home.route('/search/productList')
def search_name_dic():
    bar_cd = request.args.get('bar_cd')
    prod_name = request.args.get('prod_name')
    list_size = request.args.get('list_size')

#성별, 나이, 활동지수를 입력받아 mifflin-st jeor 방식으로 권장칼로리를 계산하며, 한국영양학회의 한국인 영양소 섭취기준에 따라 출력값을 반환
#입력데이터 : 성별(필수), 나이(필수, 1이상), 활동지수(기본값 2)
#반환데이터 : 권장칼로리, 권장탄수화물양, 권장단백질양, 권장지방량, 충분나트륨, 첨가당
@home.route('/nutrition/recommendation')
def nutrition_recommendation():
    gender =  request.args.get('gender')
    age = request.args.get('age')
    height = request.args.get('height')
    weight = request.args.get('weight')
    activity_level = request.args.get('activity_level')

    #파라미터 검증

    model = get_rec_nut(gender, int(age), int(height), int(weight), activity_level)
    
    return make_response(
        json.dumps(model, ensure_ascii=False)
    )



