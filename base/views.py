from django.shortcuts import render


# Create your views here.
def home(request):
    print(f"{'*'*5}{request.session}{'*'*5}")
    # if not request.user.is_authenticated:
    #     request.session["session_id"] = 1
    #     request.session.modified = True
    return render(request, "index.html")
