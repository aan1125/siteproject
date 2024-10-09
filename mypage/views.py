from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def index(request):
    return render(request, 'myapp/index.html')

def register(request):
    return render(request, 'myapp/register.html')

def login(request):
    return render(request, 'myapp/login.html')

def apply(request):
    return render(request, 'myapp/apply.html')

def product_registration(request):
    product_link = ''
    product_name = ''
    product_price = ''
    product_image_url = ''
    shipping_fee = ''

    if request.method == 'POST':
        product_link = request.POST.get('productLink')

        # Selenium을 사용하여 상품 정보 스크래핑
        options = Options()
        options.headless = True  # 브라우저를 실제로 열지 않으려면 True로 설정
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get(product_link)

            # 상품명과 가격을 스크래핑하는 부분
            product_name = driver.find_element(By.CSS_SELECTOR, "h3.prod_tit .title").text  # 상품명 선택자 수정 필요
            # 가격을 스크래핑하고 쉼표와 "원" 제거
            product_price = driver.find_element(By.CSS_SELECTOR, "span.lwst_prc em.prc_c").text  # 가격 선택자 수정 필요
            product_price = product_price.replace(',', '').strip()

            # 이미지 URL 스크래핑
            product_image_url = driver.find_element(By.CSS_SELECTOR, "#baseImage").get_attribute("src")  # 이미지 URL 선택자 수정 필요
            
            # 배송비 스크래핑
            shipping_fee_element = driver.find_element(By.CSS_SELECTOR, ".deleveryBaseSection")  # 배송비 선택자 수정 필요
            shipping_fee = shipping_fee_element.text if shipping_fee_element else "배송비 정보 없음"
            # 배송비의 쉼표와 "원" 제거
            shipping_fee = shipping_fee.replace(',', '').replace('원', '').strip()

            # 스크래핑한 정보를 폼에 채워 넣기
            return render(request, 'myapp/apply.html', {
                'product_link': product_link,
                'product_name': product_name,
                'product_price': product_price,
                'product_image_url': product_image_url,
                'shipping_fee': shipping_fee,
            })

        except Exception as e:
            print(f"Error occurred: {e}")
            return HttpResponse("상품 정보를 가져오는 데 실패했습니다.")
        finally:
            driver.quit()
    
    return render(request, 'myapp/apply.html')  # GET 요청 시 폼 렌더링