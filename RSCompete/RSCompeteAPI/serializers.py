from rest_framework import serializers
from RSCompeteAPI.models import User, Competition, Result, Team

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=11)
    ID_card = serializers.CharField(max_length=18)
    email = serializers.CharField(max_length=64)
    class Meta:
        model = User
        fields = ("name", "password", "country", "province", "city", "work_id", "work_place_top", "work_place_second", "work_place_third", "phone_number", "ID_card", "email", "is_captain", "team_id", "competition_id")
        validators = []
    def validate_phone_number(self, phone_number):
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return phone_number
        else:
            raise serializers.ValidationError("该手机号码已经注册")
    def validate_ID_card(self, ID_card):
        try:
            user = User.objects.get(ID_card=ID_card)
        except User.DoesNotExist:
            return ID_card
        else:
            raise serializers.ValidationError("该证件号已经注册")
    def validate_email(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        else:
            raise serializers.ValidationError("该邮箱已经注册")
# class UserSerializer(serializers.Serializer):
#     #work_id_choices = ((1, "院所"),(2, "公司"),(3, "学校"),(4,"个人"))
#     name = serializers.CharField(max_length=32)
#     password = serializers.CharField(max_length=32)
#     country = serializers.CharField(max_length=32)
#     province = serializers.CharField(max_length=32)
#     city = serializers.CharField(max_length=32)
#     work_id = serializers.IntegerField()
#     work_place = serializers.CharField(max_length=64)
#     phone_number = serializers.CharField(max_length=11)
#     ID_card = serializers.CharField(max_length=18)
#     email = serializers.CharField(max_length=64)
#     is_captain = serializers.BooleanField()
#     team_id = serializers.PrimaryKeyRelatedField(read_only=True)
    
#     competition_id = serializers.PrimaryKeyRelatedField(read_only=True)

#     def create(self, validated_data):
#         return User.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         #只能修改密码
#         instance.password = validated_data.get("password", instance.password)
#         instance.save()
#         return instance

#     def validate_phone_number(self, phone_number):
#             try:
#                 user = User.objects.get(phone_number=phone_number)
#             except User.DoesNotExist:
#                 return phone_number
#             else:
#                 raise serializers.ValidationError({'error':"该手机号码已经注册"})
#     def validate_ID_card(self, ID_card):
#         try:
#             user = User.objects.get(ID_card=ID_card)
#         except User.DoesNotExist:
#             return ID_card
#         else:
#             raise serializers.ValidationError("该证件号已经注册")
#     def validate_email(self, email):
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return email
#         else:
#             raise serializers.ValidationError("该邮箱已经注册")

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ("announcement", "dataset", "rule")

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ("time_stamp", "score", "competition_id", "team_id", "is_review", "user_id", "root_dir", "file_name")

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("team_name", "captain_name", "competition_id", "invite_code")
