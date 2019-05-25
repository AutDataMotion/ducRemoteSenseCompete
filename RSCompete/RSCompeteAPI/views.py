from django.shortcuts import render
from RSCompeteAPI.models import User, Competition, Result, Team
from django.http import HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, send_mass_mail

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer
from rest_framework import serializers
import os
import time
import traceback
import json
from RSCompeteAPI.default_settings import System_Config
from RSCompeteAPI.tasks import add, mul, wtf, scene_classification, change_detection, semantic_segmentation, object_detection
from django.db.models import Avg, Max, Min, Count, Sum
#3代表有某种属性重复
status_code = {"ok":1,"error":2,"team_repeat":3,"user_repeat":4, "full_member":5, "not_login":6,"not_exist":7, "unknown_error":8}
#加入竞赛id与竞赛项目的区分
#竞赛类型 1-目标检测 2-场景分类 3-语义分割 4-变化检测 5-目标追踪
competition_dict = {1:"object_detection", 2:"scene_classification", 3:"semantic_segmentation", 4:"change_detection", 5:"object_tracking"}

#TODO: 从系统设置中读入设置
root_dir = System_Config.result_root_dir
team_member_number = System_Config.team_member_number
leadboard_root_dir = System_Config.leader_board_root_dir
scene_classification_gt = System_Config.scene_classification_gt
change_detection_gt = System_Config.change_detection_gt
semantic_segmentation_gt = System_Config.semantic_segmentation_gt
scene_classification_test_image_path = System_Config.scene_classification_test_image_path
change_detection_test_image_path = System_Config.change_detection_test_image_path
semantic_segmentation_test_image_path = System_Config.semantic_segmentation_test_image_path
detection_gt = System_Config.detection_gt
detection_test_image_path = System_Config.detection_test_image_path
upload_perday = System_Config.upload_count_perday
current_stage = System_Config.current_stage
deadline = System_Config.deadline

import random
import string

def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str
def get_time_range():
    #FIXME: 还是需要注意一下时区的问题
    dt = time.strftime("%Y-%m-%d", time.localtime())
    
    begin_time = dt + "00:00:00"
    end_time = dt + "23:59:59"
    begin_time_stamp = time.mktime(time.strptime(begin_time, "%Y-%m-%d%H:%M:%S"))
    end_time_stamp = time.mktime(time.strptime(end_time, "%Y-%m-%d%H:%M:%S"))
    return int(round(begin_time_stamp * 1000)), int(round(end_time_stamp * 1000))

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
    #TODO: 每天一榜，为了提高效率可以写到文件中, 使用定时任务cron每天00:01生成新的排行榜
    #FIXME: 若未传入竞赛id则返回的排行榜应该按照竞赛进行分类
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "competition_id" in json_dic:
        try:
            competition = Competition.objects.get(pk=json_dic["competition_id"])
        except Competition.DoesNotExist:
            return standard_response(status_code["error"],"未找到指定竞赛")
        cid = competition.pk
        file_path = os.path.join(leadboard_root_dir, time.strftime("%Y-%m-%d", time.localtime()), str(cid), "leaderboard.json")
        print(file_path)
        try:
            with open(file_path,"r") as f:
                file_jsondic = json.load(f)
        except IOError as e:
            # return standard_response(status_code["not_exist"], "排行榜维护中")
            #FIXME: 该处时间与定时任务时间时区不一致
            now = time.localtime()
            # now.tm_mday -= 1
            file_path = os.path.join(leadboard_root_dir, time.strftime("%Y-%m-%d", now), str(cid), "leaderboard.json")
            try:
                with open(file_path,"r") as f:
                    file_jsondic = json.load(f)
            except IOError as e:
                return standard_response(status_code["not_exist"], "排行榜维护中")
        results = file_jsondic["results"]
        #处理搜索的情况
        if "team_name" in json_dic:
            #这个数组最大是该赛题队伍的数量, 可以直接线性遍历
            for result in results:
                if result["team_name"] == json_dic["team_name"]:
                    return standard_response(status_code["ok"],"", {"list":[result]})
            return standard_response(status_code["ok"], "", {"list":[]})
        #处理非搜索情况
        if "pageId" in json_dic:
            if "pageSize" in json_dic:
                number = int(json_dic["pageSize"])
            else:
                number = 30
            results_paginator = Paginator(results, number)
            # teams_paginator = Paginator(teams, number)
            page = int(json_dic["pageId"])
            try:
                page_results = results_paginator.page(page)
                # page_teams = teams_paginator.page(page)
            except PageNotAnInteger:
                page_results = results_paginator.page(1)
                page = 1
                # page_teams = teams_paginator.page(1)
            except EmptyPage:
                page_results = results_paginator.page(results_paginator.num_pages)
                page = results_paginator.num_pages
                # page_teams = teams_paginator.page(teams_paginator.num_pages)
            #print(page_results.object_list)
            # serializer = ResultSerializer(data=page_results, many=True)
            # teams_serializer = TeamSerializer(data=page_teams, many=True)
            return standard_response(status_code["ok"],"",{"results":page_results.object_list, "pageId":page, "pageSize":number, "total":len(results)})
        else:
            return standard_response(status_code["ok"], "", {"list":results, "total": len(results)})

    else:
        return standard_response(status_code["error"], "必须指定需要获取排行榜的竞赛类型")
    # if "competition_id" in json_dic:
    #     try:
    #         competition = Competition.objects.get(pk=json_dic["competition_id"])
    #         teams = competition.team_set.all() 
    #     except Competition.DoesNotExist:
    #         #若传入竞赛ID错误，则直接返回所有竞赛
    #         return standard_response(status_code["error"],"未找到指定竞赛")
    # else:
    #     return standard_response(status_code["error"],"为传入要获取的竞赛id")
    # results = []
    # results_teams = []
    # for team in teams:
    #     team_results = team.result_set.all().order_by("-score")
    #     if len(team_results) > 0:
    #         results.append(team_results[0])
    #         results_teams.append(team)
    # if "page" in json_dic:
    #     if "number" in json_dic:
    #         number = int(json_dic["number"])
    #     else:
    #         number = 25
    #     results_paginator = Paginator(results, number)
    #     teams_paginator = Paginator(results_teams, number)
    #     page = int(json_dic["page"])
    #     try:
    #         page_results = results_paginator.page(page)
    #         page_teams = teams_paginator.page(page)
    #     except PageNotAnInteger:
    #         page_results = results_paginator.page(1)
    #         page_teams = teams_paginator.page(1)
    #     except EmptyPage:
    #         page_results = results_paginator.page(results_paginator.num_pages)
    #         page_teams = teams_paginator.page(teams_paginator.num_pages)
    #     serializer = ResultSerializer(page_results, many=True)
    #     teams_serializer = TeamSerializer(page_teams, many=True)
    #     return standard_response(status_code["ok"],"",{"results":serializer.data, "page_count":results_paginator.num_pages, "teams": teams_serializer.data})
    # else:
    #     serializer = ResultSerializer(results, many=True)
    #     teams_serializer = TeamSerializer(results_teams, many=True)
    #     return standard_response(status_code["ok"], "", {"results":serializer.data, 'teams': teams_serializer.data})
@api_view(["POST","OPTIONS"])
def results_upload(request):
    if "user" in request.session:
        user = request.session["user"]
        try:
            user = User.objects.get(phone_number=user["phone_number"])
        except User.DoesNotExist:
            return standard_response(status_code["not_login"], "尚未登录")
        competition = user.competition_id
        team = user.team_id
        begin_time_stamp, end_time_stamp = get_time_range()
        today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
        print(today_results_count)
        remain = upload_perday - today_results_count
        if remain == 0:
            return standard_response(status_code["error"], "今日上传次数已满")
        print(request.FILES)
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
        
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
            return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
        finally:
            f.close()
        result = Result(time_stamp=int(unix_time), score=-1., competition_id=competition, team_id=team, user_id=user, is_review=False, root_dir=file_path, file_name=file_obj.name)
        serializer = ResultSerializer(result)
        try:
            result.save()
        except Exception as e:
            return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
        else:
            #再进行检查目前的已经上传的数量，防止并发出现的超出上传上限
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            remain = upload_perday - today_results_count
            if remain < 0:
                result.delete()
                return standard_response(status_code["error"], "今日上传次数已满")
            #TODO: 上传文件成功需要加入任务调度功能
            #TODO: 上传文件应该是一个压缩包，需要解压缩操作
            #FIXME: 加入场景分类作为测试
            #
            print(competition.pk)
            if competition.pk == 1:
                object_detection.delay(file_path, detection_gt, detection_test_image_path, result.pk)
            elif competition.pk == 2:
                scene_classification.delay(file_path, scene_classification_gt, scene_classification_test_image_path, result.pk)
            elif competition.pk == 3:
                semantic_segmentation.delay(file_path, semantic_segmentation_gt, semantic_segmentation_test_image_path, result.pk)
            elif competition.pk == 4:
                change_detection.delay(file_path, change_detection_gt, change_detection_test_image_path, result.pk)
            #mysql_test.delay(file_path, scene_classification_gt, result.pk)
            return standard_response(status_code["ok"],"")
              
    else:
        return standard_response(status_code["not_login"], "尚未登录")

@api_view(["GET"])
def results(request):
    if "user" in request.session:
        user = request.session["user"]
        begin_time_stamp, end_time_stamp = get_time_range()
        try:
            user = User.objects.get(phone_number=user["phone_number"])
        except User.DoesNotExist:
            return standard_response(status_code["not_login"], "尚未登录")
        competition = user.competition_id
        team = user.team_id
        #上传的结果以队伍为单位返回并按照时间降序排列
        results = team.result_set.all().order_by("-time_stamp")
        results_count = results.count()
        # print(results_count)
        # if results_count == 0:
        #     return standard_response(status_code["ok"], "", {"results":[], "total": results_count})
        content = JSONRenderer().render(request.GET)
        stream = BytesIO(content)
        json_dic = JSONParser().parse(stream)
        if "pageId" in json_dic:
            if "pageSize" in json_dic:
                number = int(json_dic["pageSize"])
            else:
                number = 30
            results_paginator = Paginator(results, number)
            page = int(json_dic["pageId"])
            try:
                page_results = results_paginator.page(page)
            except PageNotAnInteger:
                page_results = results_paginator.page(1)
                page = 1
            except EmptyPage:
                page_results = results_paginator.page(results_paginator.num_pages)
                page = results_paginator.num_pages
            serializer = ResultSerializer(page_results, many=True)
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            remain = upload_perday - today_results_count
            return standard_response(status_code["ok"],"",{"results":serializer.data, "total": results_count, "pageId": page, "pageSize": number, "today_remain": remain})
        else:
            serializer = ResultSerializer(results, many=True)
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            remain = upload_perday - today_results_count
            return standard_response(status_code["ok"], "", {"results":serializer.data, "total": results_count, "today_remain": remain})
    else:
        return standard_response(status_code["not_login"], "尚未登录")
#TODO: 登录成功返回队伍信息，队伍名等
@api_view(["POST","OPTIONS"])
def login(request):
    if request.method == "POST":
        content = JSONRenderer().render(request.data)
        stream = BytesIO(content)
        json_dic = JSONParser().parse(stream)
        #json_dic = json.loads(request.body)
        print(json_dic)
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
                    print(request.session["user"])
                    return standard_response(status_code["ok"], "", {"user_info": serializer.data})
                else:
                    #password error
                    return standard_response(status_code["error"], "密码不正确")
            else:
                return standard_response(status_code["error"], "没有该用户")
        else: 
            return standard_response(status_code["error"], "缺少必要参数") 
@api_view(["GET", "POST","OPTIONS"])
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
            #team_members = team.user_set.all()
            #team_members_serializer = UserSerializer(team_members, many=True)
            #serializer = UserSerializer(user, many=False)
            return standard_response(status_code["ok"], "", data={"user_info": {'name':user.name, 'competition_id':user.competition_id.pk, 'team_name': team.team_name}})
        else:
            return standard_response(status_code["not_login"], "尚未登录") 
    elif request.method == "POST":
        if "user" in request.session:
            user = request.session["user"]
            #serializer = UserSerializer(data=user)
            content = JSONRenderer().render(request.data)
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
                    return standard_response(status_code["ok"], "")
                except Exception as e:
                    print(e)
                    return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
                
            else:
                return standard_response(status_code["error"], "传递参数错误")
        else:
            return standard_response(status_code["not_login"], "尚未登录")
            
@api_view(["POST","OPTIONS"])
def register(request):
    content = JSONRenderer().render(request.data)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if not "is_captain" in json_dic:
        return standard_response(status_code["error"], "必须选择是否为队长")
    
    if json_dic["is_captain"] == "1":
        #队长注册
        #print(json_dic["work_id"])
        if not "competition_id" in json_dic:
            return standard_response(status_code["error"], "必须制定竞赛项目")
        if not "team_name" in json_dic:
            return standard_response(status_code["error"], "必须指定队伍名称")
        if json_dic['work_id'] in ['1','2','3','4','5']:
            try:
                competition = Competition.objects.get(pk=json_dic["competition_id"])
            except:
                return standard_response(status_code["not_exist"],"无指定竞赛")
            #添加队伍重复验证
            try:
                Team.objects.get(team_name=json_dic["team_name"])
            except Team.DoesNotExist:
               
                while True:
                    try:
                        invite_code = generate_random_str(4)
                        Team.objects.get(invite_code=invite_code)
                    except Team.DoesNotExist:
                        team = Team(team_name=json_dic['team_name'], competition_id=competition, captain_name=json_dic['name'], invite_code=invite_code)
                        try:
                            team.save()
                        except Exception as e:
                            return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
                        finally:
                            break
                

            else:
                return standard_response(status_code["team_repeat"], "队伍名称重复")
            
            team = Team.objects.get(team_name=json_dic['team_name'])
            json_dic["team_id"] = team.pk
            try:
                serializer = UserSerializer(data=json_dic)
            except:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())

            try:
                #serializer.validate(json_dic)
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                #区分某一部分重复
                team.delete()
                for k,v in e.detail.items():
                    message = v[0]
                return standard_response(status_code["user_repeat"], message)
            except Exception as e:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())  
            else:
                try:
                    serializer.save()
                except Exception as e:
                    team.delete()
                    return standard_response(status_code["user_repeat"], "%s"%traceback.format_exc())
                    #创建失败队伍也不应该被创建
                else:
                    #TODO: 注册成功向注册邮箱发送邮件
                    try:
                       pass
                       #TODO: 目前无法发送，稍后再试
                       # send_mail("恭喜你成功报名参加本届比赛", "请积极准备比赛，并邀请你的队伍成员加入，你的队伍邀请码为{}".format(team.invite_code), "rssrai2019@163.com", [serializer.data["email"]], fail_silently=False)
                    except Exception as e:
                        #发送邮件失败注册信息全部删除
                        #只需要删除队伍信息即可，用户与队伍通过外键关联，删除队伍将删除对应的队员
                        print(e)
                        team.delete()
                        # user = User.objects.get(phone_number=serializer.data["phone_number"])
                        # user.delete()

                        return standard_response(status_code["error"], "发送邮件失败")
                    else:
                        request.session["user"] = serializer.data
                        return standard_response(status_code["ok"],"", {"user_info":serializer.data, "team_name": team.team_name})
        else:
            return standard_response(status_code["error"], "未选择正确的工作身份")
    else:
        #TODO: 队员注册, 传入的属性为邀请码(team_id->invite_code)
        if "invite_code" in json_dic:
            try:
                team = Team.objects.get(invite_code=json_dic["invite_code"])
            except Team.DoesNotExist:
                return standard_response(status_code["not_exist"], "邀请码错误，无此队伍")
            if "competition_id" in json_dic:
                if not team.competition_id.pk == int(json_dic["competition_id"]):
                    return standard_response(status_code['error'], "队伍与队员传入的竞赛不同")
            #TODO: 获取当前已经在该队伍中的人员数
            team_members = team.user_set.all()
            if len(team_members) > team_member_number - 1:
                return standard_response(status_code["full_member"],"队伍人数已满")

            json_dic["team_name"] = team.team_name
            json_dic["competition_id"] = team.competition_id.pk
            json_dic['team_id'] = team.pk
            try:
                serializer = UserSerializer(data=json_dic)
            except:
                return standard_response(status_code["error"], "%s"%traceback.format_exc())
            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                for k,v in e.detail.items():
                    message = v[0]
                return standard_response(status_code["user_repeat"], message)
            else:
                try:
                    serializer.save()
                except:
                    return standard_response(status_code["error"], "%s"%traceback.format_exc())
                team = Team.objects.get(invite_code=json_dic["invite_code"])
                #TODO: 保存后再次判断队伍人数
                team_members = team.user_set.all()
                
                if len(team_members) > team_member_number:
                    serializer.delete()
                    return standard_response(status_code["full_member"], "队伍人数已满")
                request.session["user"] = serializer.data
                return standard_response(status_code["ok"],"", {"user_info":serializer.data}) 
        else:
            return standard_response(status_code["error"], "未提供邀请码(invite_code)")
#传入竟赛id，返回指定竟赛的统计信息
@api_view(["GET"])
def count(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    print(json_dic)
    if 'competition_id' in json_dic:
        try:
            competition = Competition.objects.get(pk=json_dic["competition_id"])
        except Competiton.DoesNotExist:
            return standard_response(status_code["not_exist"], "指定的竞赛不存在")
        else:
            teams = competition.team_set.all()
            teams_number = len(teams)
            users = competition.user_set.all()
            users_number = len(users) 
            return standard_response(status_code["ok"],"", {"team_number": str(teams_number), "user_number": str(users_number), "current_stage": current_stage, "deadline": deadline})
    else:
        if "user" in request.session:
            user = request.session["user"]
            try:
                user = User.objects.get(phone_number=user['phone_number'])
            except User.DoesNotExist:
                return standard_response(status_code["not_login"], "目前尚未登录")
            else:   
                competition = user.competition_id
                teams = competition.team_set.all()
                teams_number = len(teams)
                users = competition.user_set.all()
                users_number = len(users) 
                return standard_response(status_code["ok"],"", {"team_number": str(teams_number), "user_number": str(users_number), "current_stage": current_stage, "deadline": deadline})
        else:
            return standard_response(status_code["not_login"], "目前尚未登录")   
@api_view(["GET"])
def statistics_all(request):
    country = User.objects.values_list("country").annotate(Count("country"))
    country_size = len(country)
    city = User.objects.values_list("city").annotate(Count("city"))
    city_size = len(city)
    team = Team.objects.all()
    team_size = len(team)
    return standard_response(status_code["ok"],"", {"country": country_size, "city": city_size, "team_number": team_size})

@api_view(["GET"])
def statistics_country(request):
    country = User.objects.filter(is_captain=1).values("country").annotate(count=Count("country")).order_by('-count')
    json_list = [{"rankNum": index + 1, "name":item["country"], "team_number":item["count"]} for index, item in enumerate(country)]
    
    return standard_response(status_code["ok"],"",{"countries":json_list})
    
@api_view(["GET"])
def statistics_city(request):
    city = User.objects.filter(is_captain=1).values("city").annotate(count=Count("city")).order_by('-count')
    json_list = [{"rankNum": index + 1, "name":item["city"], "team_number":item["count"]} for index, item in enumerate(city)]
    
    return standard_response(status_code["ok"],"",{"cities":json_list})   

@api_view(["GET"])
def statistics_detail(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "city_name" in json_dic:
        captain = User.objects.filter(is_captain=1).filter(city=json_dic["city_name"])
        school = captain.filter(work_id=1).values("work_place_top").annotate(count=Count("work_place_top")).order_by("-count")
        academy = captain.filter(work_id=2).values("work_place_top").annotate(count=Count("work_place_top")).order_by("-count")
        company = captain.filter(work_id=3).values("work_place_top").annotate(count=Count("work_place_top")).order_by("-count")
        other = captain.filter(work_id=4).values("work_place_top").annotate(count=Count("work_place_top")).order_by("-count")
        school_json_list = [{"rankNum": index + 1, "name":item["work_place_top"], "team_number":item["count"]} for index, item in enumerate(school)]
        academy_json_list = [{"rankNum": index + 1, "name":item["work_place_top"], "team_number":item["count"]} for index, item in enumerate(academy)]
        company_json_list = [{"rankNum": index + 1, "name":item["work_place_top"], "team_number":item["count"]} for index, item in enumerate(company)]
        other_json_list = [{"rankNum": index + 1, "name":item["work_place_top"], "team_number":item["count"]} for index, item in enumerate(other)]
        return standard_response(status_code["ok"], "", {"school":school_json_list,"academy":academy_json_list,"company":company_json_list,"other":other_json_list})

    else:
        return standard_response(status_code["error"], "未传入需查询城市")
@api_view(["GET"])
def invite_code(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "invite_code" in json_dic:
        try:
            team = Team.objects.get(invite_code=json_dic["invite_code"])
        except Team.DoesNotExist:
            return standard_response(status_code["ok"], "", {"result":"false"})
        else:
            return standard_response(status_code["ok"], "", {'result':"true", 'team_id':team.pk, "team_name":team.team_name, "competition_id": team.competition_id.pk})
    else:
        return standard_response(status_code["error"], "未正确传入参数")


@api_view(["POST"])
def test(request):
    team = Team.objects.get(pk=29)
    add.delay(4,4)
    mul.delay(4,4)
    wtf.delay("abc")
    #team.delete()
    return standard_response("ok","")

@api_view(["POST","OPTIONS"])
def logout(request):
    if not 'user' in request.session:
        return standard_response(status_code['ok'], "")
    try:
        del request.session["user"]
    except:
        return standard_response(status_code["error"], "%s"%traceback.format_exc())
    else:
        return standard_response(status_code["ok"], "")

        
