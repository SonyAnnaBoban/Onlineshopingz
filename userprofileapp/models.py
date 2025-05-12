from django.db import models
from Accountsapp.models import MyUser



class  UserAddress(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="addresses")
    name=models.CharField(max_length=25)
    address_line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_shipping_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state} - {self.zip_code} -{self.phone_number}"


