from rest_framework import serializers
from RSCompeteAPI.models import User, Competition, Result, Team

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "password", "country", "province", "city", "work_id", "work_place", "phone_number", "ID_card", "email", "is_captain", "team_id", "competition_id")

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ("announcement", "dataset", "rule")

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ("time_stamp", "score", "competition_id", "team_id", "is_review", "user_id")

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("team_name", "captain_name", "competition_id")
