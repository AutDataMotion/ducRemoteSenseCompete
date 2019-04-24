from RSCompeteAPI.serializers import UserSerializer, CompetitionSerializer, ResultSerializer, TeamSerializer
from RSCompeteAPI.models import User, Competition, Result, Team
import time
from RSCompeteAPI.default_settings import System_Config
import os
import json
def test():
    with open("./test","w") as f:
        f.write("fuck you")

def generate_leaderboard():
    root_dir = System_Config.leader_board_root_dir
    print(time.strftime("%Y-%m-%d", time.localtime()))
    file_path = os.path.join(root_dir, time.strftime("%Y-%m-%d", time.localtime()))
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
        results_teams = []
        for team in teams:
            team_results = team.result_set.all().order_by("-score")
            if len(team_results) > 0:
                results.append(team_results[0])
                results_teams.append(team)
        serializer = ResultSerializer(results, many=True)
        teams_serializer = TeamSerializer(results_teams, many=True)
        with open(os.path.join(competition_file_path, "leaderboard.json"), "w") as f:
            json.dump({"results":serializer.data, "teams":teams_serializer.data}, f, ensure_ascii=False)
        