from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer
from RSCompeteAPI.models import User, Competition, Result, Team
import time
from RSCompeteAPI.default_settings import System_Config
import os
import json
from datetime import datetime
def test():
    with open("./test","w") as f:
        f.write("fuck you")

def generate_leaderboard():
    root_dir = System_Config.leader_board_root_dir
    print(time.strftime("%Y-%m-%d-%H", time.localtime()))
    #FIXME: 此处定时任务的时区与系统时区不一致
    file_path = os.path.join(root_dir, time.strftime("%Y-%m-%d", time.localtime()))
    #file_path = os.path.join(root_dir, datetime.utcnow)
    # if not os.path.exists(file_path):
    #     os.makedirs(file_path)
    competitions = Competition.objects.all()
    for competition in competitions:
        cid = competition.pk
        competition_file_path = os.path.join(file_path, str(cid))
        if not os.path.exists(competition_file_path): 
            os.makedirs(competition_file_path)
        teams = competition.team_set.all()
        results = []
        order = 1
        rank = 1
        team_dic = []        
        for team in teams:
            #需要处理并列的情况
            team_results = team.result_set.all().order_by("-score")
            if len(team_results) > 0:
                if team_results[0].score != -1 and team_results[0].score != -2:
                    team_dic.append((team.team_name, team_results[0].score))
                #if order == 1:
                #    previous_score = team_results[0].score
                #if previous_score != team_results[0].score:
                #    previous_score = team_results[0].score
                #    rank = order
                #results.append({"team_name": team.team_name, "score": team_results[0].score, "rankNum": rank})
                #order += 1
                
        team_dic.sort(key=lambda a: a[1], reverse=True)
        for element in team_dic:
            if order == 1:
                previous_score = element[1]
            if previous_score != element[1]:
                previous_score = element[1]
                rank = order
            results.append({"team_name": element[0], "score": element[1], "rankNum": rank})
            order += 1
                
        # serializer = ResultSerializer(results, many=True)
        # teams_serializer = TeamSerializer(results_teams, many=True)
        with open(os.path.join(competition_file_path, "leaderboard.json"), "w") as f:
            json.dump({"results":results}, f, ensure_ascii=False)
        
