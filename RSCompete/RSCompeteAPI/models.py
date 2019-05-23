from django.db import models

# Create your models here.
class User(models.Model):
    work_id_choices = ((1, "学生"),(2, "教师"),(3, "工程师"),(4,"科研人员"),(5,"其他"))
    # 1是高校，2是科研院所，3是公司，4是其他
    #uid = models.IntegerField(primary_key=True)
    #token = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    province = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    work_id = models.IntegerField(choices=work_id_choices)
    #TODO: 工作地点更改为三级 
    work_place_top = models.CharField(max_length=64, default="") #最高级
    work_place_second = models.CharField(max_length=64, default="") #二级
    work_place_third = models.CharField(max_length=64, default="") #三级
    phone_number = models.CharField(unique=True, max_length=11)
    ID_card = models.CharField(unique=True, max_length=18)
    email = models.CharField(unique=True, max_length=64)
    is_captain = models.BooleanField(verbose_name="是否为队长")
    team_id = models.ForeignKey(to="Team", on_delete=models.CASCADE)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)

# class SystemConfig(models.Model):
#     result_root_dir = models.CharField(max_length=128, default="../results")
#     team_member_number = models.IntegerField(default=5)


class Competition(models.Model):
    #cid = models.IntegerField(primary_key=True)
    announcement = models.TextField()
    dataset = models.CharField(max_length=128)
    rule = models.TextField()

class Result(models.Model):
    #rid = models.IntegerField(primary_key=True)
    #此处可以改为timefield，目前存储为unix时间戳
    time_stamp = models.BigIntegerField()
    root_dir = models.CharField(max_length=128, default="")
    score = models.FloatField(default=-1.)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)
    team_id = models.ForeignKey(to="Team", on_delete=models.CASCADE)
    user_id = models.ForeignKey(to="User", on_delete=models.CASCADE)
    is_review = models.BooleanField(default=False)
    #TODO: 上传成功后，增加文件名字字段
    file_name = models.CharField(max_length=128, default="")
    #TODO: 添加上传的文件名字段

class Team(models.Model):
    #tid = models.IntegerField(primary_key=True)
    team_name = models.CharField(unique=True, max_length=32)
    captain_name = models.CharField(max_length=32)
    competition_id = models.ForeignKey(to="Competition", on_delete=models.CASCADE)
    #TODO: 队长注册成功后，添加邀请码的绑定
    invite_code = models.CharField(max_length=4, unique=True)

#TODO: 增加地区表