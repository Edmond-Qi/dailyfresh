from django.shortcuts import render

def register(request):
    return render(request,'df_user/register.html')
