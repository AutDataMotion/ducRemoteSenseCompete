from django.shortcuts import render
from RSCompeteAPI.models import User, Competition, Result, Team
from django.http import HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, send_mass_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer
from rest_framework import serializers
import os
import time
import datetime
import traceback
import json
from RSCompeteAPI.default_settings import System_Config
from RSCompeteAPI.tasks import add, mul, wtf, scene_classification, change_detection, semantic_segmentation, object_detection, tracking
from django.db.models import Avg, Max, Min, Count, Sum
#3代表有某种属性重复
status_code = {"ok":1,"error":2,"team_repeat":3,"user_repeat":4, "full_member":5, "not_login":6,"not_exist":7, "unknown_error":8}
#加入竞赛id与竞赛项目的区分
#竞赛类型 1-目标检测 2-场景分类 3-语义分割 4-变化检测 5-目标追踪
competition_dict = {2:"object_detection", 1:"scene_classification", 3:"semantic_segmentation", 4:"change_detection", 5:"object_tracking"}

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
tracking_gt = System_Config.tracking_gt
upload_perday = System_Config.upload_count_perday
upload_all = System_Config.upload_count_perday_all
current_stage = System_Config.current_stage
deadline = System_Config.deadline
admin_username = System_Config.admin_username
admin_passwd = System_Config.admin_passwd
data_path = System_Config.data_path

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
def get_time_range(date=None):
    #FIXME: 还是需要注意一下时区的问题
    if date is None:
        dt = time.strftime("%Y-%m-%d", time.localtime())
    else:
        dt = date
    
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
@api_view(["GET"])
def leaderboard_out(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    competition_id = json_dic["competition_id"]
    if "top_number" in json_dic:
        top_number = int(json_dic["top_number"])
    else:
        top_number = 20
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
    outputs = []
    if top_number > len(results):
        top_number = len(results)
    
    for result in results[:top_number]:
        team_name = result["team_name"]
        score = result["score"]
        rank = result["rankNum"]
        team = Team.objects.get(team_name=team_name)
        team_members = team.user_set.all()
        team_members_array = [{"name": member.name, "work_place_top": member.work_place_top, "work_place_second": member.work_place_second, "work_place_third": member.work_place_third, "phone_number":member.phone_number, "ID_card": member.ID_card, "email": member.email, "is_captain": member.is_captain} for member in team_members]
        outputs.append({"team_name": team_name, "score": score, "team_members": team_members_array, "rank": rank})
        
    return standard_response(status_code["ok"], "", outputs)
    
@api_view(["GET"])
def topScoreDaily(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    dt = datetime.datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
    day = datetime.timedelta(days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    begin_day = datetime.datetime.strptime("2019-07-01", "%Y-%m-%d")
    days = []
    date_score = []
    while True:
        days.append(dt.strftime("%Y-%m-%d"))
        if (dt - begin_day).days == 0:
            break
        dt -= day
    print(days)
    if "competition_id" in json_dic:
        for date in days[::-1]:
            file_path = os.path.join(leadboard_root_dir, date, str(json_dic["competition_id"]), "leaderboard.json")
            try:
                with open(file_path,"r") as f:
                    file_jsondic = json.load(f)
            except IOError as e:
                continue
            results = file_jsondic["results"]
            if len(results) > 0:
                print(results)
                date_score.append({"date":datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d"), "score": results[0]["score"]})
        print(date_score)
        return standard_response(status_code["ok"], "", {"dailyDatas": date_score})  
    else:
        return standard_response(status_code["error"], "未传入竞赛id")
@api_view(["GET"])
def registAndSubmitDaily(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    dt = datetime.datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
    day = datetime.timedelta(days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    begin_day = datetime.datetime.strptime("2019-07-01", "%Y-%m-%d")
    days = []
    date_submit = []
    while True:
        days.append(dt.strftime("%Y-%m-%d"))
        if (dt - begin_day).days == 0:
            break
        dt -= day
    print(days)
    if "competition_id" in json_dic:
        competition = Competition.objects.get(pk=json_dic["competition_id"])
        regist_count = competition.team_set.count()
        per_day_count = 0
        index = 0
        for date in days[::-1]:
            print(index)
            if index == 0 or index == 1 or index == 2:
                per_day_count += random.randint(int(regist_count * 0.1), int(regist_count * 0.2))
            else:
                per_day_count += random.randint(0, int(regist_count * 0.03))
                if per_day_count > regist_count:
                    per_day_count = regist_count
            if index == len(days) - 1:
                per_day_count = regist_count
            begin_time_stamp, end_time_stamp = get_time_range(date)
            today_results_count = competition.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            total_results_count = competition.result_set.filter(time_stamp__lte=end_time_stamp).count()
            date_submit.append({"date":datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d"), "submitDayCnt": today_results_count, "submitCnt": total_results_count, "registCnt": per_day_count})
            index += 1
        return standard_response(status_code["ok"], "", {"dailyDatas": date_submit})
    else:
        return standard_response(status_code["error"], "未传入竞赛id")
@api_view(["GET"])
def teamScoreDaily(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "teamId" in json_dic:
        team_id = json_dic["teamId"]
        try:
            team = Team.objects.get(pk=team_id)
            
        except:
            return standard_response(status_code["error"], "传入队伍id未找到")
        dt = datetime.datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
        day = datetime.timedelta(days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        begin_day = datetime.datetime.strptime("2019-07-01", "%Y-%m-%d")

        days = []
        date_submit = []
        while True:
            days.append(dt.strftime("%Y-%m-%d"))
            if (dt - begin_day).days == 0:
                break
            dt -= day
        for date in days[::-1]:
            begin_time_stamp, end_time_stamp = get_time_range(date)
            today_results = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).exclude(score=-2.).exclude(score=-1.).order_by("-score")
            if len(today_results) > 0:
                date_submit.append({"date":datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d"), "score": today_results[0].score})
            else:
                continue
        return standard_response(status_code["ok"], "", {"dailyDatas": date_submit})
    else:
        return standard_response(status_code["error"], "未传入队伍id")
@api_view(["GET"])
def themeTeams(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "competition_id" in json_dic:
        competition_id = json_dic["competition_id"]
        try:
            competition = Competition.objects.get(pk=competition_id)
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
        if len(results) > 10:
            top10_results = results[:10]
        else:
            top10_results = results
        top10_teams = []
        for result in top10_results:
            team_name = result["team_name"]
            team = Team.objects.get(team_name=team_name)
            top10_teams.append({"teamId": team.pk, "teamName": team.team_name, "score": result["score"]})
        # top10_results = [{"teamId": team.pk, "teamName": team.team_name, "score": }]
        return standard_response(status_code["ok"], "", data={"pageId":1, "pageSize":30, "total": len(top10_results), "results":top10_teams})
        # if competition_id == "1":
        #     return standard_response(status_code["ok"], "", data={"pageId":1, "pageSize":30, "total":1, "results":[{"teamId":1008, "teamName":"SHE", "score":0.94868}]})
        # elif competition_id == "2":
        #     return standard_response(status_code["ok"], "", data={"pageId":1, "pageSize":30, "total":2, "results":[{"teamId":1847, "teamName":"NIST-czh", "score":0.46881}, {"teamId":1866, "teamName":"pca_lab", "score":0.41604}]})
        # elif competition_id == "3":
        #     return standard_response(status_code["ok"], "", data={"pageId":1, "pageSize":30, "total":1, "results":[{"teamId":1953, "teamName":"KUAIYAN", "score":0.57526}]})
        # elif competition_id == "4":
        #     return standard_response(status_code["ok"], "", data={"pageId":1, "pageSize":30, "total":1, "results":[{"teamId":1956, "teamName":"CVEO-CDteam", "score":0.42637}]})
        # else:
        #     return standard_response(status_code["error"], "无相关竞赛")    
    else:
        return standard_response(status_code["error"], "未传入竞赛id")
@api_view(["GET"])
def teamResultDetail(request):
    content = JSONRenderer().render(request.GET)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    if "teamId" in json_dic:
        team_id = json_dic["teamId"]
        team = Team.objects.get(pk=team_id)
        competition_id = team.competition_id.pk
        file_path = os.path.join(leadboard_root_dir, time.strftime("%Y-%m-%d", time.localtime()), str(competition_id), "leaderboard.json")
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
        if len(results) > 10:
            top10_results = results[:10]
        else:
            top10_results = results
        is_find = False
        for result in top10_results:
            if team.team_name == result["team_name"]:
                score = result["score"]
                is_find = True
                break
        if is_find:
        # team_result = team.result_set.all().order_by("-score")
        # score = team_result[0].score
            if competition_id == 1:
                img_urls = ["new_vis{}.png".format(i+1) for i in range(23)]
                # img_urls = ["new_vis1.png", "new_vis2.png", "new_vis3.png", "new_vis4.png", "new_vis5.png"]
                return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"场景分类结果图", "imgUrl":"/static/top_result_vis/1/{}/figures/{}".format(team_id, url)} for url in img_urls]})
            elif competition_id == 2:
                img_urls = ["P3246_sub2.png", "P9830_sub2.png", "P3188_sub2.png", "P3966_sub2.png", "P4461_sub2.png", "P9773_sub2.png"]
                return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"目标检测结果图", "imgUrl":"/static/top_result_vis/2/{}/vis_results2/{}".format(team_id, url)} for url in img_urls]})
            elif competition_id == 3:
                img_urls = ["vis.png"]
                return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"语义分割结果图", "imgUrl":"/static/top_result_vis/3/{}/figures/{}".format(team_id, url)} for url in img_urls]})
            elif competition_id == 4:
                img_urls = ["vis.png"]
                return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"变化检测结果图", "imgUrl":"/static/top_result_vis/4/{}/figures/{}".format(team_id, url)} for url in img_urls]})
            elif competition_id == 5:
                img_urls = ["P3246.png", "P5513.png", "P9830.png"]
                return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"目标检测结果图", "imgUrl":"/static/top_result_vis/5/{}/vis_results/{}".format(team_id, url)} for url in img_urls]})
            else:
                return standard_response(status_code["error"], "传入竞赛id错误")
        else:
            return standard_response(status_code["error"], "该队伍未进入前10")
        # if team_id == "1008":
        #     img_urls = ["new_vis1.png", "new_vis2.png", "new_vis3.png", "new_vis4.png", "new_vis5.png"]
            
        #     score = 0.94868
        #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"场景分类结果图", "imgUrl":"/static/vis/results/1/1008/1562750751799/figures/{}".format(url)} for url in img_urls]})
        #     # elif team_id == "1267":
        #     #     score = 0.94736
        #     #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"场景分类示意图", "imgUrl":"/static/vis/results/1/1267/1562750751799/figures/{}".format(url)} for url in img_urls]})
        # elif team_id == "1847":
        #     img_urls = ["P3246.png", "P5513.png", "P9830.png"]
        #     score = 0.46881
        #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"目标检测结果图", "imgUrl":"/static/vis/results/2/1847/1562482328556/vis_results/{}".format(url)} for url in img_urls]})
        # elif team_id == "1866":
        #     img_urls = ["P3246.png", "P5513.png", "P9830.png"]
        #     score = 0.41604
        #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"目标检测结果图", "imgUrl":"/static/vis/results/2/1866/1561957257299/vis_results/{}".format(url)} for url in img_urls]})
        # elif team_id == "1953":
        #     score = 0.57526
        #     img_urls = ["Norm_cm.png", "precision.png", "unNorm_cm.png"]
        #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"语义分割结果图", "imgUrl":"/static/vis/results/3/1953/1562421122387/figures/{}".format(url)} for url in img_urls]})
        # elif team_id == "1956":
        #     score = 0.42637
        #     img_urls = ["Norm_cm.png", "unNorm_cm.png", "vis.png"]
        #     return standard_response(status_code["ok"], "", data={"score":score, "summary":[], "imageInfo":[{"title":"变化检测结果图", "imgUrl":"/static/vis/results/4/1965/1562143912586/figures/{}".format(url)} for url in img_urls]})
    else:
        return standard_response(status_code["error"], "未传入队伍id")






@api_view(["GET"])
def notify(request):
    competition = Competition.objects.get(pk=1)
    return standard_response(status_code["ok"],"",data={"context":competition.rule})
@api_view(["GET"])
def get_data_path(request):
    if "user" in request.session:
        user = request.session["user"]
        try:
            user = User.objects.get(phone_number=user["phone_number"])
        except User.DoesNotExist:
            return standard_response(status_code["not_login"], "尚未登录")
        else:
            return standard_response(status_code["ok"],"",{"url":data_path[user.competition_id.pk]["url"], "code":data_path[user.competition_id.pk]["code"]})
    else:
        return standard_response(status_code["not_login"], "尚未登录")
@api_view(["POST"])
def notify_edit(request):
    content = JSONRenderer().render(request.data)
    stream = BytesIO(content)
    json_dic = JSONParser().parse(stream)
    name = json_dic["name"]
    passwd = json_dic["cxtpwd"]
    if name != admin_username or passwd != admin_passwd:
        return standard_response(status_code["error"], "用户名或者密码错误无修改权限")
    else:
        competition = Competition.objects.get(pk=1)
        if 'context' in json_dic:
            competition.rule = json_dic['context']
            try:
                competition.save()
            except:
                return standard_response(status_code["unknown_error"], "%s"%traceback.format_exc())
            else:
                return standard_response(status_code["ok"], "")
        else:
            return standard_response(status_code["error"], "传入参数错误")

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
        today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).exclude(score=-2.).count()
        today_all = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()        
        print(today_results_count)
        remain = upload_perday - today_results_count
        remain_all = upload_all - today_all
        if remain == 0:
            return standard_response(status_code["error"], "今日上传次数已满")
        elif remain_all == 0:
            return standard_response(status_code['error'], "今日上传次数已满")
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
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).exclude(score=-2.).count()
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
                scene_classification.delay(file_path, scene_classification_gt, scene_classification_test_image_path, result.pk)
            elif competition.pk == 2:
                object_detection.delay(file_path, detection_gt, detection_test_image_path, result.pk)

            elif competition.pk == 3:
                semantic_segmentation.delay(file_path, semantic_segmentation_gt, semantic_segmentation_test_image_path, result.pk)
            elif competition.pk == 4:
                change_detection.delay(file_path, change_detection_gt, change_detection_test_image_path, result.pk)
            elif competition.pk == 5:
                tracking.delay(file_path, tracking_gt, result.pk)
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
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).exclude(score=-2.).count()
            remain = upload_perday - today_results_count
            today_all = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            remain_all = upload_all - today_all
            if remain_all == 0:
                remain = 0
            return standard_response(status_code["ok"],"",{"results":serializer.data, "total": results_count, "pageId": page, "pageSize": number, "today_remain": remain})
        else:
            serializer = ResultSerializer(results, many=True)
            today_results_count = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).exclude(score=-2.).count()
            remain = upload_perday - today_results_count
            today_all = team.result_set.filter(time_stamp__gte=begin_time_stamp, time_stamp__lte=end_time_stamp).count()
            remain_all = upload_all - today_all
            if remain_all == 0:
                remain = 0
            return standard_response(status_code["ok"], "", {"results":serializer.data, "total": results_count, "today_remain": remain})
    else:
        return standard_response(status_code["not_login"], "尚未登录")
#TODO: 登录成功返回队伍信息，队伍名等
@csrf_exempt
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
            return standard_response(status_code["ok"], "", data={"user_info": {'name':user.name, 'is_captain': user.is_captain, 'invite_code':team.invite_code, 'competition_id':user.competition_id.pk, 'team_name': team.team_name, "country":user.country, "work_id":user.work_id, "work_place_top":user.work_place_top, "work_place_second":user.work_place_second, "work_place_third":user.work_place_third, "phone_number":user.phone_number, "ID_card":user.ID_card, "email":user.email, }})
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
    
    if json_dic["is_captain"] == 1:
        #队长注册
        #print(json_dic["work_id"])
        if not "competition_id" in json_dic:
            return standard_response(status_code["error"], "必须制定竞赛项目")
        if not "team_name" in json_dic:
            return standard_response(status_code["error"], "必须指定队伍名称")
        if json_dic['work_id'] in [1,2,3,4]:
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
            #TODO: 处理选择控件的问题,若为中国则provinceCity是一个数组，若不是中国则是字符串
            if json_dic['country'] != "中国":
                json_dic["country"] = json_dic["provinceCity"]
                json_dic["province"] = "other"
                json_dic["city"] = "other"
            else:
                json_dic["province"] = json_dic["provinceCity"][0]
                json_dic["city"] = json_dic["provinceCity"][1]
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
                       
                       #TODO: 目前无法发送，稍后再试
                       competition_d = {1:"遥感图像场景分类", 2:"遥感图像目标检测", 3:"遥感图像语义分割", 4:"遥感图像变化检测", 5:"遥感视频目标跟踪"}
                       send_mail("RSCUP2019报名通知", "{}, 恭喜您成功报名参加本届遥感图像稀疏表征与智能分析竞赛，您参加的竞赛主题为{}. 您注册的手机号码为{}, 作为队长，您最多可邀请4名队员组队参加本项竞赛，队伍邀请码为{}. 请积极准备本次竞赛，预祝取得好成绩!".format(serializer.data['name'], competition_d[serializer.data['competition_id']], serializer.data['phone_number'], team.invite_code), "rscup2019@hotmail.com", [serializer.data["email"]], fail_silently=False)
                    except Exception as e:
                        #发送邮件失败注册信息全部删除
                        #只需要删除队伍信息即可，用户与队伍通过外键关联，删除队伍将删除对应的队员
                        print(e)
                        request.session['user'] = serializer.data
                        # user = User.objects.get(phone_number=serializer.data["phone_number"])
                        # user.delete()

                        return standard_response(status_code["ok"], "", {'user_info':serializer.data, "team_name": team.team_name})
                    else:
                        request.session["user"] = serializer.data
                        return standard_response(status_code["ok"],"", {"user_info":serializer.data, "team_name": team.team_name})
        else:
            return standard_response(status_code["error"], "未选择正确的工作身份")
    elif json_dic["is_captain"] == 0:
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
            #TODO: 处理选择控件的问题
            if json_dic['country'] != "中国":
                json_dic["country"] = json_dic["provinceCity"]
                json_dic["city"] = "other"
                json_dic["province"] = "other"
            else:
                json_dic["province"] = json_dic["provinceCity"][0]
                json_dic["city"] = json_dic["provinceCity"][1]


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
    else:
        return standard_response(status_code["error"], "传入的is_captain不正确")
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
        except Competition.DoesNotExist:
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
    country = User.objects.filter(is_captain=1).values_list("country").annotate(Count("country"))
    country_size = len(country)
    city = User.objects.filter(is_captain=1).values_list("city").annotate(Count("city"))
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
    city = User.objects.filter(is_captain=1).filter(country="中国").values("city").annotate(count=Count("city")).order_by('-count')
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

        
