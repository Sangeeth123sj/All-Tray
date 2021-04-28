from django.contrib.auth.backends import BaseBackend
from tray.models import Student
from django.contrib.auth.models import User, Permission
from django.contrib.auth.hashers import check_password, make_password

class MyBackend(BaseBackend):
    def authenticate(self, request, pin_no=None, reg_no=None):
        try:
            if pin_no:
                pin_no = make_password(pin_no, 'pepper')
                student = Student.objects.get(pin_no=pin_no)
            elif reg_no:
                reg_no = make_password(reg_no, 'pepper')
                student = Student.objects.get(reg_no=reg_no)
            user = student.user
        except Student.DoesNotExist:
            return None
        return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None