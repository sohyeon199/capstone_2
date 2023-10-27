from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class product_basic(Base):
    """제품정보 데이터 클래스
    Args:
        bar_cd (String(255), primary_key=True): 바코드번호
        prdt_nm_kor (String(255), nullable=False): 제품명(국문)
        rep_prdt_nm (String(255)): 통합상품명
        img_link (String(255)): 이미지 링크
        brnd_nm (String(255)): 브랜드명
        prdt_nation (String(255)): 제조국
        prdt_compo (String(255)): 구성정보
        prdt_pac_type (String(255)): 상품형태(포장유형)
        prdt_cat (String(255)): 제품분류
        prdt_cat_class1 (String(255)): 제품대분류
        prdt_cat_class2 (String(255)): 제품중분류
        prdt_cat_class3 (String(255)): 제품소분류
        prdt_cat_class4 (String(255)): 제품세분류
        prdt_volume (String(255)): 중량
        prdt_atrb (String(255)): 신고번호
        nutrition (product_nutrition): 영양정보
        companys (product_company): 회사정보
        prdt_expire (product_expire): 유통기한 정보
    Notes:
        sqlalchemy를 이용하여 데이터베이스에 접근하는 클래스
    """
    
    __tablename__ = 'product basic'
    
    bar_cd = Column(String(255), primary_key=True, index=True)
    prdt_nm_kor = Column(String(255), nullable=False)
    rep_prdt_nm = Column(String(255))
    img_link = Column(String(255))
    brnd_nm = Column(String(255))
    prdt_nation = Column(String(255))
    prdt_compo = Column(String(255))
    prdt_pac_type = Column(String(255))
    prdt_cat = Column(String(255))
    prdt_cat_class1 = Column(String(255))
    prdt_cat_class2 = Column(String(255))
    prdt_cat_class3 = Column(String(255))
    prdt_cat_class4 = Column(String(255))
    prdt_volume = Column(String(255))
    prdt_atrb = Column(String(255))
    nutrition = relationship(
        "product_nutrition",
        cascade="all, delete",
        back_populates="prdt",
        uselist=False,
    )
    companys = relationship(
        "product_company",
        cascade="all, delete",
        back_populates="prdt",
        uselist=True,
    )
    prdt_expire = relationship(
        "product_expire",
        cascade="all, delete",
        back_populates="prdt",
        uselist=False,
    )
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class product_nutrition(Base):
    """제품정보 데이터 클래스
    Args:
        bar_cd (String(255), ForeignKey('product basic.bar_cd'), primary_key=True): 바코드번호
        calories (Float(), nullable=False): 칼로리
        serving_size (String(255)): 1회 제공량
        total_carb (Float(), nullable=False): 탄수화물
        sugers (Float()): 당류
        protein (Float(), nullable=False): 단백질
        total_fat (Float(), nullable=False): 총지방
        saturated_fat (Float()): 포화지방
        trans_fat (Float()): 트랜스지방
        cholesterol (Float()): 콜레스테롤
        sodium (Float()): 나트륨
        prdt (product_basic): 제품정보
    Notes:
        sqlalchemy를 이용하여 데이터베이스에 접근하는 클래스
    """
    
    __tablename__ = 'product nutrition'
    
    bar_cd = Column(String(255), ForeignKey('product basic.bar_cd', ondelete='cascade'), primary_key=True, index=True)
    calories = Column(Float(), nullable=False)
    serving_size = Column(String(255))
    total_carb = Column(Float(), nullable=False)
    sugers = Column(Float())
    protein = Column(Float(), nullable=False)
    total_fat = Column(Float(), nullable=False)
    saturated_fat = Column(Float())
    trans_fat = Column(Float())
    cholesterol = Column(Float())
    sodium = Column(Float())
    prdt = relationship("product_basic", back_populates="nutrition", uselist=False)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class product_company(Base):
    """제품정보 데이터 클래스
    Args:
        company_id (Integer(), primary_key=True, default=auto_increment): 회사정보 아이디
        bar_cd (String(255), ForeignKey('product basic.bar_cd'), primary_key=True): 바코드번호
        company (String(255), nullable=False): 회사명
        prdt (product_basic): 제품정보
    Notes:
        sqlalchemy를 이용하여 데이터베이스에 접근하는 클래스
        company_id는 공백으로 보내면 자동으로 증가함
    """
    
    __tablename__ = 'product company'
    
    company_id = Column(Integer(), primary_key=True, index=True)
    bar_cd = Column(String(255), ForeignKey('product basic.bar_cd', ondelete='cascade'), nullable=False)
    company = Column(String(255), nullable=False)
    prdt = relationship("product_basic", back_populates="companys", uselist=False)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
                        
class product_expire(Base):
    """제품정보 데이터 클래스
    Args:
        bar_cd (String(255), ForeignKey('product basic.bar_cd'), primary_key=True): 바코드번호
        best_before_date (String(255), nullable=False): 유통기한
        expiration_date (String(255)): 소비기한
        basis (String(255)): 유통기한기준
        prdt (product_basic): 신고번호
    Notes:
        sqlalchemy를 이용하여 데이터베이스에 접근하는 클래스
    """
    
    __tablename__ = 'product expire'
    
    bar_cd = Column(String(255), ForeignKey('product basic.bar_cd', ondelete='cascade'), primary_key=True, index=True)
    best_before_date = Column(String(255), nullable=False)
    expiration_date = Column(String(255))
    basis = Column(String(255))
    prdt = relationship("product_basic", back_populates="prdt_expire", uselist=False)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}