#파라미터 검증
#100번 : 매개변수 관련
#400번 : 크롤링 관련(외부 연계)
#500번 : 내부 DB접속
def validate_bar_cd(args: str):
    if (not args.isdigit()):
        return {"result":"fail", "err_code":"112", "err_msg":"바코드에 숫자가 아닌 값이 들어있습니다"}
    elif (len(args) != 13):
        return {"result":"fail", "err_code":"111", "err_msg":"바코드가 13자리가 아닙니다"}

def validate_age(args: str):
    if (not args.isdigit()):
        return {"result":"fail", "err_code":"112", "err_msg":"바코드에 숫자가 아닌 값이 들어있습니다"}
    elif (len(args) != 13):
        return {"result":"fail", "err_code":"111", "err_msg":"바코드가 13자리가 아닙니다"}
    
    if age < 1:
        return {"err_code":"112", "err_msg":"바코드에 숫자가 아닌 값이 들어있습니다"}