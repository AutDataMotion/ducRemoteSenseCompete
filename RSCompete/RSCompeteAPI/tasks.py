from __future__ import absolute_import, unicode_literals
from celery import shared_task
from RSCompeteAPI.scene_classification_eval import get_score as scene_classification_get_score
from RSCompeteAPI.models import User, Competition, Result, Team
import os
@shared_task
def add(x, y):
    return x + y
@shared_task
def mul(x, y):
    return x * y
@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def wtf(s):
    return s

@shared_task
def scene_classification(root_path, annopath, result_id):
    res = scene_classification_get_score(root_path, annopath)
    if res[0] == 0:
        #若评分成功，则从评分接口生成的文件中读入分数写入数据库中
        result = Result.objects.get(pk=result_id)
        with open(os.path.join(root_path, "results", "accuracy.txt")) as f:
            line = f.readline()
            #FIXME: 此处需要进行更改
            #FIXME: 需要更改为从json文件读取
            top1 = line[16:]

        result.score = float(top1)
        try:
            result.save()
        except Exception as e:
            print(e)
        #TODO: 评价完成传传件件式式误误score写为-2



