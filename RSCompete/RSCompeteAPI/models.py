from django.db import models

# Create your models here.
class User(models.Model):
    work_id_choices = ((1, "院所"),(2, "公司"),(3, "学校"),(4,"个人"))
    #uid = models.IntegerField(primary_key=True)
    #token = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    province = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    work_id = models.IntegerField(choices=work_id_choices)
    work_place = models.CharField(max_length=64)
    phone_number = models.CharField(unique=True, max_length=11)
    ID_card = models.CharField(unique=True, max_length=18)
    email = models.CharField(unique=True, max_length=64)
    is_captain = models.BooleanField(verbose_name="是否为队长")
    team_id = models.ForeignKey(to="Team", on_delete=models.CASCADE)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)

class Competition(models.Model):
    #cid = models.IntegerField(primary_key=True)
    announcement = models.TextField()
    dataset = models.CharField(max_length=128)
    rule = models.TextField()

class Result(models.Model):
    #rid = models.IntegerField(primary_key=True)
    #此处可以改为timefield，目前存储为unix时间戳
    time_stamp = models.BigIntegerField()
    
    score = models.FloatField(default=-1.)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)
    team_id = models.ForeignKey(to="Team", on_delete=models.CASCADE)
    user_id = models.ForeignKey(to="User", on_delete=models.CASCADE)
    is_review = models.BooleanField(default=False)

class Team(models.Model):
    #tid = models.IntegerField(primary_key=True)
    team_name = models.CharField(unique=True, max_length=32)
    captain_name = models.CharField(max_length=32)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)


