from django.shortcuts import render
from RSCompeteAPI.models import User, Competition, Result, Team
from django.http import HttpResponse, JsonResponse
from django.utils.six import BytesIO

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer



def standard_response(status, message, data=None):
    if data == None:
        return JsonResponse({"status":status, "message":message}, safe=False, json_dumps_params={"ensure_ascii":False})
    else:
        return JsonResponse({"status":status, "message":message, "data": data}, safe=False, json_dumps_params={"ensure_ascii":False})
# Create your views here.
@api_view(["GET", "POST"])
def competitionList(request):
    if request.method == "GET":
        competition = Competition.objects.all()
        
        serializer = CompetitionSerializer(competition, many=True)
        return JsonResponse({"status":"ok", "competitions":serializer.data}, status=status.HTTP_200_OK, safe=False, json_dumps_params={"ensure_ascii":False})
        
    elif request.method == "POST":
        content = JSONRenderer().render(request.POST)
        stream = BytesIO(content)
        json_dic = JSONParser().parse(stream)
        number = len(Competition.objects.all())
        json_dic["cid"] = number + 1
        serializer = CompetitionSerializer(data=json_dic)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error"}, status=status.HTTP_400_BAD_REQUEST, safe=False, json_dumps_params={"ensure_ascii":False})
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, json_dumps_params={"ensure_ascii":False})
        return JsonResponse({"status":serializer.errors}, status=status.HTTP_400_BAD_REQUEST, json_dumps_params={"ensure_ascii":False})

@api_view(["POST"])
def login(request):
    if request.method == "POST":
        content = JSONRenderer().render(request.POST)
        stream = BytesIO(content)
        json_dic = JSONParser().parse(stream)
        if 'phone_number' in json_dic and 'password' in json_dic:
            phone_number = json_dic['phone_number']
            password = json_dic['password']
            user = User.objects.filter(phone_number=phone_number)
            if len(user) == 1:
                user = user.first()
                if user.password == password:
                    #success login
                    serializer = UserSerializer(user)
                    request.session["user"] = serializer.data
                    return standard_response("ok", "", {"user_info": serializer.data})
                else:
                    #password error
                    return standard_response("error", "密码不正确")
            else:
                return standard_response("error", "没有该用户")
        else: 
            return standard_response("error", "缺少必要参数") 
@api_view(["GET", "POST"])
def users(request):
    if request.method == "GET":
        if "user" in request.session:
            user = request.session["user"]
            # serializer = UserSerializer(user, many=False)
            return standard_response("ok", "", data={"user_info": user})
            #TODO: need to return the team message

        else:
            return standard_response("error", "尚未登录") 
    elif request.method == "POST":
        if "user" in request.session:
            user = request.session["user"]
            #serializer = UserSerializer(data=user)
            content = JSONRenderer().render(request.POST)
            stream = BytesIO(content)
            json_dic = JSONParser().parse(stream)
            if "password" in json_dic:
                user_model = User.objects.get(uid=user["uid"])
                user_model.password = json_dic["password"]
                try:
                    user_model.save()
                    #TODO: not complete
                    #update success need to update session too
                    serializer = UserSerializer(user_model)
                    request.session["user"] = serializer.data
                    return standard_response("ok", "", {"user_info": serializer.data})
                except Exception as e:
                    print(e)
                    return standard_response("error", e)
                
            else:
                return standard_response("error", "传递参数错误")
        else:
            return standard_response("error", "尚未登录")
            

        