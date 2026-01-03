from django.shortcuts import render, redirect
from users.forms import SignupForm #회원가입에 사용할 커스텀 Form
from django.contrib.auth.forms import AuthenticationForm #Django에서 기본 제공하는 로그인 Form
from django.contrib import auth #로그인, 로그아웃 같은 인증 관련 기능 모음
from django.contrib.auth.decorators import login_required #로그인한 사용자만 접근 가능하게 만드는 데코레이터

def main(request):
    return render(request, "users/main.html")

def signup(request):
		# SignUp 버튼 눌렀을 때
    if request.method == 'POST':
        form = SignupForm(request.POST,request.FILES) #사용자가 입력한 데이터를 SignupForm에 넣음
        # 유효성 검사 통과 시
        if form.is_valid():
            user = form.save() #폼을 저장해서 그 폼을 통해 만들어진 User 객체 가져오기
            auth.login(request, user) #회원가입 직후 자동 로그인
            return redirect('users:profile') #profile 페이지로 이동
        else:
            return redirect('users:signup') #다시 회원가입 페이지로
		# GET ->  빈 폼을 보여줌
    else:
        form = SignupForm()
        context = {
            'form': form,
        }
        return render(request, 'users/signup.html', context)
    
def login(request):
		# 로그인 버튼 클릭
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST) #Django 기본 로그인 폼 사용
        if form.is_valid():
            user = form.get_user() #User 객체 가져오기
            auth.login(request, user)
            return redirect('users:profile')
        else:
            context = {
                'form':form,
            }
            return render(request, 'users/login.html',context) #다시 로그인 페이지로
		#GET -> 빈 폼을 보여줌
    else:
        form = AuthenticationForm()
        context = {
            'form': form,
        }
        return render(request, 'users/login.html', context)

def logout(request):
    auth.logout(request)
    return redirect('users:main')
 
@login_required #로그인한 사용자만 프로필 페이지 접근 가능.
def profile(request):
    return render(request,"users/profile.html")