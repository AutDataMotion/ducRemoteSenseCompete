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

import traceback
#3代表有某种属性重复
status_code = {"ok":1,"error":2,"team_repeat":3,"user_repeat":4}
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
                    return standard_response(status_code["ok"], "", {"user_info": serializer.data})
                else:
                    #password error
                    return standard_response(status_code["error"], "密码不正确")
            else:
                return standard_response(status_code["error"], "没有该用户")
        else: 
            return standard_response(status_code["error"], "缺少必要参数") 
@api_view(["GET", "POST"])
def users(request):
    if request.method == "GET":
        if "user" in request.session:
            user = request.session["user"]
            # serializer = UserSerializer(user, many=False)
            return standard_response(status_code["ok"], "", data={"user_info": user})
            #TODO: need to return the team message

        else:
            return standard_response(status_code["error"], "尚未登录") 
    elif request.method == "POST":
        if "user" in request.session:
            user = request.session["user"]
            #serializer = UserSerializer(data=user)
            content = JSONRenderer().render(request.POST)
            stream = BytesIO(content)
            json_dic = JSONParser().parse(stream)
            if "password" in json_dic:
                user_model = User.objects.get(phone_number=user["phone_number"])
                user_model.password = json_dic["password"]
                try:
                    user_model.save()
                    #TODO: not complete
                    #update success need to update session too
                    serializer = UserSerializer(user_model)
                    request.session["user"] = serializer.data
                    return standard_response(status_code["ok"], "", {"user_info": serializer.data})
                except Exception as e:
                    print(e)
                    return standard_response(status_code["error"], "%s"%traceback.format_exc())
                
            else:
                return standard_response(status_code["error"], "传递参数错误")
        else:
            return standard_response(status_code["error"], "尚未登录")
            
@api_view(["POST"])
def register(request):
    content = JSONRenderer().render(request.POST)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if json_dic["is_captain"]:
        #队长注册
        #print(json_dic["work_id"])
        if json_dic['work_id'] in ['1','2','3','4']:
            try:
                competition = Competition.objects.get(pk=json_dic["competition_id"])
            except:
                return standard_response(status_code["error"],"无指定竞赛")
            team = Team(team_name=json_dic['team_name'], competition_id=competition, captain_name=json_dic['name'])
            try:
                team.save()
            except Exception as e:
                return standard_response(status_code["team_repeat"], "%s"%traceback.format_exc())
            
            team = Team.objects.get(team_name=json_dic['team_name'])
            json_dic["team_id"] = team.pk
            try:
                serializer = UserSerializer(data=json_dic)
            except:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            if serializer.is_valid():
                try:
                    serializer.save()
                except Exception as e:
                    team.delete()
                    return standard_response(status_code["user_repeat"], "%s"%traceback.format_exc())
                    #创建失败队伍也不应该被创建
                request.session["user"] = serializer.data
                return standard_response(status_code["ok"],"", {"user_info":serializer.data})    
            else:
                #TODO: 区分是某一项重复
                team.delete()
                return standard_response(status_code["user_repeat"], "输入格式错误")
        else:
            return standard_response(status_code["error"], "未知参数")
    else:
        #TODO: 队员注册
        pass
@api_view(["POST"])
def test(request):
    team = Team.objects.get(pk=15)
    team.delete()
    return standard_response("ok","")

@api_view(["POST"])
def logout(request):
    try:
        del request.session["user"]
    except:
        return standard_response(status_code["error"], "%s"%traceback.format_exc())
    else:
        return standard_response(status_code["ok"], "")

        