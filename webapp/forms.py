from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from webapp.models import Project, Invite, BillingRecord, get_user_balance


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['state']

class RegisterForm(UserCreationForm):
    invite = forms.CharField(max_length=30, label="Инвайт")

    def clean_invite(self):
        invite = self.cleaned_data.get("invite")
        if Invite.objects.filter(code=invite).count() > 0:
            Invite.objects.filter(code=invite).all().delete()
            return invite
        else:
            raise forms.ValidationError(
                "Некорректный инвайт",
                code='invalid_invite',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit)
        BillingRecord(amount=1000, comment="Initial", user=user).save()

        return user

class IpoInvestForm(forms.Form):
    amount = forms.IntegerField(label='Сумма', min_value=0)

    def __init__(self, user, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.project = project

    def save(self):
        amount = int(self.cleaned_data.get('amount'))
        if self.project.invest(self.user, amount):
            return True
        else:
            return False


class StockForm(forms.Form):
    number = forms.IntegerField(label='Кол-во', min_value=0)

    def __init__(self, user, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.project = project

    def save(self):
        number = int(self.cleaned_data.get('number'))
        if self.data.get('sell'):
            if self.project.sell(self.user, number):
                return True
        if self.data.get('buy'):
            if self.project.buy(self.user, number):
                return True

        return False

class ChangeForm(forms.Form):
    percent = forms.IntegerField(label='Процент', min_value=-100, max_value=100)

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

    def save(self):
        self.project.change(self.cleaned_data.get('percent'))
        return True