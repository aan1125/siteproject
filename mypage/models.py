from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from decimal import Decimal
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # 기본 권한 필드를 True로 설정
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True,primary_key=True)
    nickname = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=200, blank=True)
    detail_address = models.CharField(max_length=200, blank=True)
    extra_address = models.CharField(max_length=200, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=50,blank=True,null=True)  # 위도와 경도를 문자열로 저장할 필드

    # 권한 관련 필드 추가
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # 추가 필수 필드가 없다면 빈 리스트

    def __str__(self):
        return self.username

    # 추가적인 권한 확인 메서드
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_link = models.URLField(max_length=200)
    product_image_url=models.URLField(max_length=200)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    people_count = models.PositiveIntegerField(default=0)#방장 미포함 모집할 인원수
    people_now_count = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.product_name

class RegisteredProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='registered_products')
    registrant_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    tracking_number = models.CharField(max_length=100, blank=True,null=True)
    courier_service = models.CharField(max_length=100, blank=True,null=True)
    purchase_amount=models.DecimalField(max_digits=10, decimal_places=2) #구매할 금액
    receivable_amount=models.DecimalField(max_digits=10, decimal_places=2) #정산받을 금액
    
    def save(self, *args, **kwargs):
        # Debugging: 출력 각 값
        print("Product Price:", self.product.product_price)
        print("Shipping Fee:", self.product.shipping_fee)

        # 구매할 금액 계산
        self.purchase_amount = Decimal(self.product.product_price) + Decimal(self.product.shipping_fee)
        
        # 받을 금액 계산
        if self.product.people_count > 0:
            self.receivable_amount = (Decimal(self.purchase_amount) / Decimal(self.product.people_count+1)) * Decimal(self.product.people_count)
        else:
            self.receivable_amount = Decimal(0)  
        
        # Debugging: 출력 계산 결과
        print("Purchase Amount:", self.purchase_amount)
        print("Receivable Amount:", self.receivable_amount)

        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        parent_product = self.product
        print(f"Deleting RegisteredProduct: {self.id}")  # 삭제되는 자식 객체 ID 출력
        super().delete(*args, **kwargs)
        print(f"Deleting Product: {parent_product.id}")  # 삭제되는 부모 객체 ID 출력
        parent_product.delete()


    def __str__(self):
        return f"{self.product.product_name} - {self.registrant_id}"
    
class Participant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='participants')
    applicant_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participants')
    registered_product = models.ForeignKey(RegisteredProduct, on_delete=models.CASCADE, related_name='participants')
    final_amount=models.DecimalField(max_digits=10, decimal_places=2)#최종가격
    # 최종가격 계산
    def save(self, *args, **kwargs):
        # 최종가격 계산
        if self.product.people_count > 0:  # 사람들이 0명 이상일 때만 계산
            self.final_amount = (Decimal(self.product.product_price) + Decimal(self.product.shipping_fee)) / Decimal(self.product.people_count + 1)
        else:
            self.final_amount = Decimal(0)  # 사람들이 0명일 경우 0으로 설정

        # 부모 클래스의 save 메서드 호출
        super().save(*args, **kwargs)
        
        

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"
    

'''class RegisteredProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='registered_products')
    registrant_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    product_link = models.URLField(max_length=200)
    product_image_url = models.URLField(max_length=200)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    people_count = models.PositiveIntegerField(default=0)
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    receivable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100)
    courier_service = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # 구매할 금액 계산
        self.purchase_amount = self.product.product_price + self.product.shipping_fee
        
        # 받을 금액 계산
        if self.product.people_count > 1:
            self.receivable_amount = (self.product.product_price + self.product.shipping_fee) / (self.product.people_count - 1)
        else:
            self.receivable_amount = 0  # 사람 수가 1 이하일 경우 0으로 설정
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.registrant_id}"'''