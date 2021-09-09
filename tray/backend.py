from django.contrib.auth.backends import BaseBackend
from tray.models import Student
from django.contrib.auth.models import User, Permission
from django.contrib.auth.hashers import check_password, make_password

class MyBackend(BaseBackend):
    def authenticate(self, request, username=None, pin_no=None, reg_no=None,):
        try:
            student_user = User.objects.get(username = username)
            student = student_user.student
            if pin_no:
                password = student.pin_no
                check_pin_no = check_password(pin_no, password)
                if check_pin_no:
                    user = student_user
                    return user

            elif reg_no:
                password = student.reg_no
                check_reg_no = check_password(reg_no, password)
                if check_reg_no:
                    user = student_user
                    return user
            
        except User.DoesNotExist:
            print("authentication backend error user not found")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None