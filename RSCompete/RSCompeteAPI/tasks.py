from __future__ import absolute_import, unicode_literals
from celery import shared_task
from RSCompeteAPI.scene_cls_eval import get_score as scene_classification_get_score
from RSCompeteAPI.change_detection import get_score as change_detection_get_score
from RSCompeteAPI.semantic_segmentation import get_score as semantic_segmentation_get_score
from RSCompeteAPI.models import User, Competition, Result, Team
import os
import pymysql
import json
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
def semantic_segmentation(root_path, annopath, path_test_image, result_id):
    try:
        res = semantic_segmentation_get_score(root_path, annopath, path_test_image)
    except:
        db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
            db.commit()
        except:
            db.rollback()
        db.close()
    else:
        if len(res > 1):
            if res[0] == 0:
                with open(os.path.join(root_path, "results_semantic_segmentation", "semantic_segmentation.json")) as f:
                    json_txt = f.read()
                json_dic = json.loads(json_txt)
                kappa = json_dic["kappa"]
                db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
                cursor = db.cursor()
                try:
                    cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(kappa, result_id))
                    db.commit()
                except:
                    db.rollback()
                db.close()
            else:
                db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
                cursor = db.cursor()
                try:
                    cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
                    db.commit()
                except:
                    db.rollback()
                db.close()
        else:
            db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
            cursor = db.cursor()
            try:
                cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
                db.commit()
            except:
                db.rollback()
            db.close()
@shared_task
def change_detection(root_path, annopath, path_test_image, result_id):
    try:
        res = change_detection_get_score(root_path, annopath, path_test_image)
    except:
        db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
            db.commit()
        except:
            db.rollback()
        db.close()
    else:
        if len(res > 1):
            if res[0] == 0:
                with open(os.path.join(root_path, "results_change_detection", "change_detection.json")) as f:
                    json_txt = f.read()
                json_dic = json.loads(json_txt)
                kappa = json_dic["F1_score"]
                db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
                cursor = db.cursor()
                try:
                    cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(kappa, result_id))
                    db.commit()
                except:
                    db.rollback()
                db.close()
            else:
                db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
                cursor = db.cursor()
                try:
                    cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
                    db.commit()
                except:
                    db.rollback()
                db.close()
        else:
            db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
            cursor = db.cursor()
            try:
                cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
                db.commit()
            except:
                db.rollback()
            db.close()

@shared_task
def scene_classification(root_path, annopath, path_test_image, result_id):
    try:
        res = scene_classification_get_score(root_path, annopath, path_test_image)
    except:
        db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(-2, result_id))
            db.commit()
        except:
            db.rollback()
        db.close()
    else:
        if res[0] == 0:
            #若评分成功，则从评分接口生成的文件中读入分数写入数据库中
            #result = Result.objects.get(pk=result_id)
            with open(os.path.join(root_path, "scores", "cls_scores.json")) as f:
                json_txt = f.read()
            json_dic = json.loads(json_txt)
            acc = json_dic["overall-accuracy"]

            db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
            cursor = db.cursor()
            try:
                cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(acc, result_id))
                db.commit()
            except:
                db.rollback()
            db.close()
        else:
            db = pymysql.connect("localhost","RSAdmin","xuan","RSCompete")
            cursor = db.cursor()
            try:
                cursor.execute("UPDATE RSCompeteAPI_result SET score = {} WHERE id = {};".format(top1, result_id))
                db.commit()
            except:
                db.rollback()
            db.close()




