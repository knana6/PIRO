from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignupForm(UserCreationForm):
    # Profile 선택지
    GENDER_CHOICES = [
        ('Male', '남자'),
        ('Female', '여자'),
    ]

    JOB_CHOICES = [
        ('Student', '학생'),
        ('Worker', '직장인'),
        ('JobSeeker', '취준생'),
        ('Other', '기타'),
    ]

    # User 필드
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Profile 필드
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="성별",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    job = forms.ChoiceField(
        choices=JOB_CHOICES,
        label="직업",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    bio = forms.CharField(
        label="자기소개",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    image = forms.ImageField(
        label="프로필 이미지",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # 핵심: User + Profile 같이 저장
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                gender=self.cleaned_data['gender'],
                job=self.cleaned_data['job'],
                bio=self.cleaned_data['bio'],
                image=self.cleaned_data.get('image'), 
            )

        return user

    # 이메일 중복 검사
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email
