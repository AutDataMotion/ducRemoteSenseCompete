from django.shortcuts import render
from RSCompeteAPI.models import User, Competition, Result, Team
from django.http import HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer
import os
import time
import traceback

from RSCompeteAPI.tasks import add, mul, wtf
#3代表有某种属性重复
status_code = {"ok":1,"error":2,"team_repeat":3,"user_repeat":4, "full_member":5, "not_login":6}
#TODO: 文件存放根目录,待更改为从系统设置表中读入
root_dir = "../results"


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
@api_view(["GET"])
def leaderboard(request):
    #TODO: 每天一榜，为了提高效率可以写到文件中
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "competition_id" in json_dic:
        try:
            competition = Competition.objects.get(pk=json_dic["competition_id"])
            teams = competition.team_set.all() 
        except Competition.DoesNotExist:
            #若传入竞赛ID错误，则直接返回所有竞赛
            teams = Team.objects.all()
    else:
        teams = Team.objects.all()
    results = []
    results_teams = []
    for team in teams:
        team_results = team.result_set.all().order_by("-score")
        if len(team_results) > 0:
            results.append(team_results[0])
            results_teams.append(team)
    if "page" in json_dic:
        if "number" in json_dic:
            number = int(json_dic["number"])
        else:
            number = 25
        results_paginator = Paginator(results, number)
        teams_paginator = Paginator(results_teams, number)
        page = int(json_dic["page"])
        try:
            page_results = results_paginator.page(page)
            page_teams = teams_paginator.page(page)
        except PageNotAnInteger:
            page_results = results_paginator.page(1)
            page_teams = teams_paginator.page(1)
        except EmptyPage:
            page_results = results_paginator.page(results_paginator.num_pages)
            page_teams = teams_paginator.page(teams_paginator.num_pages)
        serializer = ResultSerializer(page_results, many=True)
        teams_serializer = TeamSerializer(page_teams, many=True)
        return standard_response(status_code["ok"],"",{"results":serializer.data, "page_count":results_paginator.num_pages, "teams": teams_serializer.data})
    else:
        serializer = ResultSerializer(results, many=True)
        teams_serializer = TeamSerializer(results_teams, many=True)
        return standard_response(status_code["ok"], "", {"results":serializer.data, 'teams': teams_serializer.data})


@api_view(["GET", "POST"])
def results(request):
    if request.method == "POST":
        #处理文件的上传
        
        if "user" in request.session:
            user = request.session["user"]
            try:
                user = User.objects.get(phone_number=user["phone_number"])
            except User.DoesNotExist:
                return standard_response(status_code["not_login"], "尚未登录")
            competition = user.competition_id
            team = user.team_id
            
            file_obj = request.FILES.get("file")
            if file_obj is None:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            
            unix_time = str(int(round(time.time() * 1000)))
            #TODO: 添加创建目录
            file_path = os.path.join(root_dir, str(competition.pk), str(team.pk), unix_time)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            
            f = open(os.path.join(file_path, file_obj.name),"wb") 
            try:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            except Exception as e:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            finally:
                f.close()
            result = Result(time_stamp=int(unix_time), score=-1., competition_id=competition, team_id=team, user_id=user, is_review=False)
            serializer = ResultSerializer(result)
            try:
                result.save()
            except Exception as e:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            #TODO: 上传文件成功需要加入任务调度功能
            #TODO: 上传文件应该是一个压缩包，需要解压缩操作
            return standard_response(status_code["ok"],"", {"result_info":serializer.data})
              
        else:
            return standard_response(status_code["not_login"], "尚未登录")
    elif request.method == "GET":
        if "user" in request.session:
            user = request.session["user"]
            try:
                user = User.objects.get(phone_number=user["phone_number"])
            except User.DoesNotExist:
                return standard_response(status_code["not_login"], "尚未登录")
            competition = user.competition_id
            team = user.team_id
            #上传的结果以队伍为单位返回并按照时间降序排列
            results = team.result_set.all().order_by("-time_stamp")
            content = JSONRenderer().render(request.GET)
            stream = BytesIO(content)
            json_dic = JSONParser().parse(stream)
            if "page" in json_dic:
                if "number" in json_dic:
                    number = int(json_dic["number"])
                else:
                    number = 25
                results_paginator = Paginator(results, number)
                page = int(json_dic["page"])
                try:
                    page_results = results_paginator.page(page)
                except PageNotAnInteger:
                    page_results = results_paginator.page(1)
                except EmptyPage:
                    page_results = results_paginator.page(results_paginator.num_pages)
                serializer = ResultSerializer(page_results, many=True)
                return standard_response(status_code["ok"],"",{"results":serializer.data, "page_count":results_paginator.num_pages})
            else:
                serializer = ResultSerializer(results, many=True)
                return standard_response(status_code["ok"], "", {"results":serializer.data})
        else:
            return standard_response(status_code["not_login"], "尚未登录")

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
            #serializer = UserSerializer(user, many=False)
            try:
                user = User.objects.get(phone_number=user["phone_number"])
            except User.DoesNotExist:
                return standard_response(status_code["not_login"], "尚未登录")
            team = user.team_id
            team_members = team.user_set.all()
            team_members_serializer = UserSerializer(team_members, many=True)
            serializer = UserSerializer(user, many=False)
            return standard_response(status_code["ok"], "", data={"user_info": serializer.data, "team_members": team_members_serializer.data})
        else:
            return standard_response(status_code["not_login"], "尚未登录") 
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
            return standard_response(status_code["not_login"], "尚未登录")
            
@api_view(["POST"])
def register(request):
    content = JSONRenderer().render(request.POST)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if not "is_captain" in json_dic:
        return standard_response(status_code["error"], "参数错误")
    
    if json_dic["is_captain"] == "1":
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
        if "team_id" in json_dic and "competition_id" in json_dic:
            try:
                team = Team.objects.get(pk=json_dic["team_id"])
            except Exception as e:
                return standard_response(status_code['error'], "%s"%traceback.format_exc())
            
            if not team.competition_id.pk == int(json_dic["competition_id"]):
                return standard_response(status_code['error'], "队伍与队员传入的竞赛不同")
            #TODO: 获取当前已经在该队伍中的人员数
            team_members = team.user_set.all()
            if len(team_members) > 4:#先设定为4，该设定之后写入system_config表中
                return standard_response(status_code["full_member"],"队伍人数已满")
            json_dic["team_name"] = team.team_name
            json_dic["competition_id"] = team.competition_id.pk
            
            try:
                serializer = UserSerializer(data=json_dic)
            except:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            if serializer.is_valid():
                try:
                    serializer.save()
                except:
                    return standard_response(status_code["user_repeat"], "%s"%traceback.format_exc())
                team = Team.objects.get(pk=json_dic["team_id"])
                #TODO: 保存后再次判断队伍人数
                team_members = team.user_set.all()
                #暂时设置为5
                if len(team_members) > 5:
                    serializer.delete()
                    return standard_response(status_code["full_member"], "队伍人数已满")
                request.session["user"] = serializer.data
                return standard_response(status_code["ok"],"", {"user_info":serializer.data}) 
            else:
                return standard_response(status_code["user_repeat"], "查询各个信息是否唯一")

        else:
            return standard_response(status_code["error"], "传入参数不足(team_id or competition_id)")

@api_view(["GET"])
def count(request):
    count_array = []
    competitions = Competition.objects.all()
    for competition in competitions:
        teams = competition.team_set.all()
        teams_number = len(teams)
        users = competition.user_set.all()
        users_number = len(users)
        count_array.append({competition.pk:{"teams_number":str(teams_number), "users_number":str(users_number)}})
        #TODO: 是否增加已经提交的结果数量
    
    return standard_response(status_code["ok"],"",count_array)

@api_view(["POST"])
def test(request):
    team = Team.objects.get(pk=29)
    add.delay(4,4)
    mul.delay(4,4)
    wtf.delay("abc")
    #team.delete()
    return standard_response("ok","")

@api_view(["POST"])
def logout(request):
    try:
        del request.session["user"]
    except:
        return standard_response(status_code["error"], "%s"%traceback.format_exc())
    else:
        return standard_response(status_code["ok"], "")

        