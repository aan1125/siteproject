import requests
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login as auth_login,authenticate,logout
from .models import CustomUser  # CustomUser 모델 임포트
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from .models import Product, RegisteredProduct
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from geopy.distance import geodesic

# 신청버튼 클릭하면 증가하기
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Participant  # Participant 모델이 있다고 가정

'''def search(request):
    query = request.GET.get('q')  # 쿼리 문자열에서 'q' 파라미터 가져오기
    if query:
        results = Product.objects.filter(product_name__icontains=query)  # 상품명으로 필터링
    else:
        results = Product.objects.none()  # 쿼리가 없으면 빈 쿼리셋 반환

    context = {
        'results': results,
        'query': query,
        'registered_products': Product.objects.all(),  # 전체 상품 목록도 포함
    }
    return render(request, 'myapp/index.html', context)  # 기존 index.html 템플릿 사용'''
@login_required
def setting(request):
    user = request.user

    if request.method == 'POST':
        # 폼에서 데이터 가져오기
        user.nickname = request.POST.get('nickname')
        user.phone = request.POST.get('phone')
        user.postcode = request.POST.get('postcode')
        user.address = request.POST.get('address')
        
        user.save()  # 변경된 정보 저장
        return redirect('setting')  # 저장 후 개인정보 페이지로 리디렉션

    # GET 요청 시 사용자 정보를 템플릿에 전달
    context = {
        'nickname': user.nickname,
        'phone': user.phone,
        'postcode': user.postcode,
        'address': user.address,
        
    }
    # 설정 페이지에 필요한 처리 로직
    return render(request, 'myapp/setting.html',context)
@csrf_exempt
def increment_count(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            # 참여자 수가 최대 수에 도달하지 않았는지 확인
            if product.people_now_count < product.people_count:
                
                # 등록된 제품 중 해당 상품과 연결된 것을 찾음
                registered_product = RegisteredProduct.objects.filter(product=product).first()
                if not registered_product:
                    return JsonResponse({'success': False, 'error': '등록된 제품을 찾을 수 없습니다.'})
                # 등록자와 신청자가 같으면 신청 불가
                if registered_product.registrant_id == request.user:
                    return JsonResponse({'success': False, 'error': '등록자는 신청할 수없습니다'})
                product.people_now_count += 1
                product.save()
                # 참가자 정보 저장 (예시)
                Participant.objects.create(product=product, applicant_id=request.user,registered_product=registered_product)  # 사용자 정보 저장

                return JsonResponse({
                    'success': True,
                    'people_now_count': product.people_now_count
                })
            else:
                return JsonResponse({'success': False, 'error': '최대 참여자 수에 도달했습니다.'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': '제품을 찾을 수 없습니다.'})
    return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})

def index(request):
    query = request.GET.get('q')  # 쿼리 문자열에서 'q' 파라미터 가져오기
    registered_products = RegisteredProduct.objects.select_related('product', 'registrant_id')

    # 사용자 위치 가져오기
    user_location = None
    if request.user.is_authenticated:
        user_location = request.user.location  # "위도,경도" 형식

    # 500m 이내 상품 필터링
    nearby_products = []
    if user_location:
        user_latitude, user_longitude = map(float, user_location.split(','))

        for registered_product in registered_products:
            registrant_location = registered_product.registrant_id.location
            if registrant_location:
                registrant_latitude, registrant_longitude = map(float, registrant_location.split(','))
                distance = geodesic((user_latitude, user_longitude), (registrant_latitude, registrant_longitude)).meters  # 거리 계산 (m 단위)

                if distance <= 500:  # 500m 이내인 경우
                    nearby_products.append(registered_product)

    # 검색 기능
    if query:
        results = Product.objects.filter(product_name__icontains=query)  # 상품명으로 필터링
    else:
        results = Product.objects.none()  # 쿼리가 없으면 빈 쿼리셋 반환

    # 위치 정보를 미리 분리하여 전달
    for product in registered_products:
        if product.registrant_id.location:
            lat, lng = product.registrant_id.location.split(',')
            product.latitude = lat
            product.longitude = lng

    context = {
        'registered_products': registered_products,  # 전체 상품
        'nearby_products': nearby_products,  # 근처 상품
        'results': results,  # 검색 결과
        'query': query,  # 검색어
        'user': request.user,
    }
    return render(request, 'myapp/index.html', context)  # 기존 index.html 템플릿 사용
'''#메인페이지 상품 진열
def index(request):
    registered_products = RegisteredProduct.objects.select_related('product', 'registrant_id')

    # 사용자 위치 가져오기
    user_location = None
    if request.user.is_authenticated:
        user_location = request.user.location  # "위도,경도" 형식

    # 500m 이내 상품 필터링
    nearby_products = []
    if user_location:
        user_latitude, user_longitude = map(float, user_location.split(','))

        for registered_product in registered_products:
            registrant_location = registered_product.registrant_id.location
            if registrant_location:
                registrant_latitude, registrant_longitude = map(float, registrant_location.split(','))
                distance = geodesic((user_latitude, user_longitude), (registrant_latitude, registrant_longitude)).meters  # 거리 계산 (m 단위)

                if distance <= 500:  # 500m 이내인 경우
                    nearby_products.append(registered_product)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        address = request.POST.get('address')  # 주소 입력 받기
        product = get_object_or_404(Product, id=product_id)

        registered_product = RegisteredProduct(
            product=product,
            registrant_id=request.user,
            address=address,
        )
        registered_product.save()  # 저장
     # 위치 정보를 미리 분리하여 전달
    for product in registered_products:
        if product.registrant_id.location:
            lat, lng = product.registrant_id.location.split(',')
            product.latitude = lat
            product.longitude = lng
    context = {
        'registered_products': registered_products,  # 전체 상품
        'nearby_products': nearby_products,  # 근처 상품
        'user': request.user,
    }
    return render(request, 'myapp/index.html', context)'''


def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            # 사용자 인증
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # 로그인 처리
                auth_login(request, user)
                return redirect('index')  # 로그인 성공 시 리디렉트할 페이지
            else:
                messages.error(request, "사용자 이름 또는 비밀번호가 잘못되었습니다.")
        else:
            messages.error(request, "모든 필드를 입력해주세요.")

    return render(request, 'myapp/login.html')

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('index')  # 로그아웃 후 리디렉트할 페이지

def apply(request):
    return render(request, 'myapp/apply.html')
@login_required
def mypg(request):
    # 현재 로그인한 사용자의 등록 상품 가져오기
    registered_products = RegisteredProduct.objects.filter(registrant_id=request.user)

    # 신청한 상품 가져오기 (적절한 모델을 사용하여 수정)
    applied_products = Participant.objects.filter(applicant_id=request.user)

    if request.method == 'POST':
        registered_product_id = request.POST.get('registered_product_id')
        tracking_number = request.POST.get('tracking_number')
        courier_service = request.POST.get('courier_service')

        # RegisteredProduct 객체 가져오기
        try:
            registered_product = RegisteredProduct.objects.get(id=registered_product_id)
            registered_product.tracking_number = tracking_number  # 운송장 번호 저장
            registered_product.courier_service = courier_service  # 택배사 저장
            registered_product.save()
        except RegisteredProduct.DoesNotExist:
            pass  # 상품이 존재하지 않을 경우 처리

    print(f"Registered Products: {registered_products.count()}")
    print("Registered Products:", registered_products)  # 콘솔에 등록된 상품 개수 출력
    
    context = {
        'registered_products': registered_products,
        'applied_products': applied_products,  # 신청한 상품 추가
        'user': request.user,
    }
    
    return render(request, 'myapp/mypg.html', context)


'''@login_required
def mypg(request):
    # 현재 로그인한 사용자의 등록 상품 가져오기
    registered_products = RegisteredProduct.objects.filter(registrant_id=request.user)
    
    if request.method == 'POST':
        registered_product_id = request.POST.get('registered_product_id')
        tracking_number = request.POST.get('tracking_number')
        courier_service = request.POST.get('courier_service')

        # RegisteredProduct 객체 가져오기
        try:
            registered_product = RegisteredProduct.objects.get(id=registered_product_id)
            registered_product.tracking_number = tracking_number  # 운송장 번호 저장
            registered_product.courier_service = courier_service  # 택배사 저장
            registered_product.save()
        except RegisteredProduct.DoesNotExist:
            pass  # 상품이 존재하지 않을 경우 처리

    print(f"Registered Products: {registered_products.count()}")
    print("Registered Products:", registered_products)  # 콘솔에 등록된 상품 개수 출력
    
    context = {
        'registered_products': registered_products,
        'user': request.user,
    }
    
    return render(request, 'myapp/mypg.html', context)'''


def scrape_product_info(product_link):
    """주어진 링크에서 상품 정보를 스크래핑하여 반환합니다."""
    options = Options()
    options.headless = True  # 브라우저를 실제로 열지 않으려면 True로 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    product_info = {}

    try:
        driver.get(product_link)

        # 상품명과 가격을 스크래핑하는 부분
        product_info['product_name'] = driver.find_element(By.CSS_SELECTOR, "h3.prod_tit .title").text  # 상품명 선택자 수정 필요
        product_price = driver.find_element(By.CSS_SELECTOR, "span.lwst_prc em.prc_c").text  # 가격 선택자 수정 필요
        product_info['product_price'] = product_price.replace(',', '').strip()
        # 상품명에서 "(숫자개)" 형태의 수량 추출
        match = re.search(r'\((\d+)개\)', product_info['product_name'])
        if match:
            product_info['quantity'] = match.group(1)  # 숫자 추출
        else:
            product_info['quantity'] = None  # 수량이 없는 경우
        # 이미지 URL 스크래핑
        product_info['product_image_url'] = driver.find_element(By.CSS_SELECTOR, "#baseImage").get_attribute("src")  # 이미지 URL 선택자 수정 필요
        
        # 배송비 스크래핑
        shipping_fee_element = driver.find_element(By.CSS_SELECTOR, ".deleveryBaseSection")  # 배송비 선택자 수정 필요
        shipping_fee = shipping_fee_element.text if shipping_fee_element else "배송비 정보 없음"
        product_info['shipping_fee'] = shipping_fee.replace('무료배송','0').replace(',', '').replace('원', '').strip()

    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        return None
    finally:
        driver.quit()

    return product_info

def product_registration(request):
    if request.method == 'POST':
        if 'productLink' in request.POST:
            # 크롤링 수행
            product_link = request.POST.get('productLink')
            product_info = scrape_product_info(product_link)

            if product_info is None:
                return HttpResponse("상품 정보를 가져오는 데 실패했습니다.")

            # 스크래핑한 정보를 세션에 저장
            request.session['product_data'] = {
                'product_link': product_link,
                'product_name': product_info['product_name'],
                'product_price': product_info['product_price'],
                'product_image_url': product_info['product_image_url'],
                'shipping_fee': product_info['shipping_fee'],
                'quantity':product_info['quantity'],
            }
            print("세션에 저장된 데이터:", request.session['product_data'])  # 디버깅용 로그
            return render(request, 'myapp/apply.html', {
                'product_link': product_link,
                'product_name': product_info['product_name'],
                'product_price': product_info['product_price'],
                'product_image_url': product_info['product_image_url'],
                'shipping_fee': product_info['shipping_fee'],
                'quantity':product_info['quantity'],
            })

        elif 'people_count' in request.POST:
            # 세션에서 크롤링된 정보 가져오기
            product_data = request.session.get('product_data')
            print("세션에서 가져온 데이터:", product_data)  # 디버깅용 로그

            if not product_data:
                return HttpResponse("세션에 상품 정보가 없습니다.")  # 세션 데이터가 없을 경우 처리

            people_count = request.POST.get('people_count')

            try:
                user = request.user
                # 데이터베이스에 저장
                product=Product.objects.create(
                    user=user,
                    product_link=product_data['product_link'],
                    product_name=product_data['product_name'],
                    product_price=product_data['product_price'],
                    product_image_url=product_data['product_image_url'],
                    shipping_fee=product_data['shipping_fee'],
                    quantity=product_data['quantity'],
                    people_count=int(people_count)
                )
                # RegisteredProduct 객체 생성 및 저장
                RegisteredProduct.objects.create(
                    product=product,  # 방금 생성한 Product 객체 참조
                    registrant_id=user,
                    
                )
                print("상품 정보가 데이터베이스에 저장되었습니다.")  # 성공 메시지
            except Exception as e:
                print("데이터베이스 저장 중 오류 발생:", e)  # 오류 메시지 출력
                return HttpResponse("상품 정보를 저장하는 데 실패했습니다.")

            # 세션에서 크롤링된 정보 삭제
            del request.session['product_data']
            return redirect('index')

    return render(request, 'myapp/apply.html')  # GET 요청 시 폼 렌더링




def my_page(request):
    registered_products = ...  # 등록된 상품 쿼리셋 가져오기
    applied_products = ...  # 신청한 상품 쿼리셋 가져오기
    return render(request, 'myapp/mypg.html', {
        'registered_products': registered_products,
        'applied_products': applied_products,
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        postcode = request.POST.get('sample3_postcode')
        address = request.POST.get('sample3_address')
        detail_address = request.POST.get('sample3_detailAddress')
        extra_address = request.POST.get('sample3_extraAddress')
        latitude = request.POST.get('latitude')  # 위도 추가
        longitude = request.POST.get('longitude')  # 경도 추가

        # 사용자 이름 중복 체크
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "이미 사용 중인 아이디입니다.")
        
        # 서버 측 유효성 검사
        elif not all([username, nickname, password, password_confirm, phone, postcode, address]):
            messages.error(request, "모든 필드를 완전히 입력해야 합니다.")
        elif password != password_confirm:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
        else:
            password_hashed = make_password(password)
            location = f"{latitude},{longitude}"  # 위도와 경도를 합쳐서 문자열로 생성
            CustomUser.objects.create(
                username=username,
                nickname=nickname,
                password=password_hashed,
                phone=phone,
                postcode=postcode,
                address=address,
                detail_address=detail_address,
                extra_address=extra_address,
                location=location  # 합쳐진 위치 저장
            )
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect('index')  # 회원가입 성공시 이동할 페이지

    return render(request, 'myapp/register.html')
'''def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        postcode = request.POST.get('sample3_postcode')
        address = request.POST.get('sample3_address')
        detail_address = request.POST.get('sample3_detailAddress')
        extra_address = request.POST.get('sample3_extraAddress')
        # 사용자 이름 중복 체크
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "이미 사용 중인 아이디입니다.")
        # 서버 측 유효성 검사
        
        elif not all([username, nickname, password, password_confirm, phone, postcode, address]):
            messages.error(request, "모든 필드를 완전히 입력해야 합니다.")
        elif password != password_confirm:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
        else:
            password_hashed = make_password(password)
            CustomUser.objects.create(
                username=username,
                nickname=nickname,
                password=password_hashed,
                phone=phone,
                postcode=postcode,
                address=address,
                detail_address=detail_address,
                extra_address=extra_address
            )
            return redirect('index')  # 회원가입 성공시 이동할 페이지

    return render(request, 'myapp/register.html')'''







