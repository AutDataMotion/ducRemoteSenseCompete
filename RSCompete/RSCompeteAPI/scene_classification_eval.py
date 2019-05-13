from __future__ import absolute_import, unicode_literals
import xml.etree.ElementTree as ET
import os
# import cPickle
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
# import codecs
import time
import zipfile
from tqdm import tqdm
import shutil
import logging
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
# from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import accuracy_score
    # ,precision_score,recall_score,f1_score,precision_recall_curve

from celery import shared_task

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

def GetFileFromThisRootDir(dir,ext = None):
  allfiles = []
  needExtFilter = (ext != None)
  for root,dirs,files in os.walk(dir):
    for filespath in files:
      filepath = os.path.join(root, filespath)
      extension = os.path.splitext(filepath)[1][1:]
      if needExtFilter and extension in ext:
        allfiles.append(filepath)
      elif not needExtFilter:
        allfiles.append(filepath)
  return allfiles

def parse_result(filename, classname):
    """
    clssification results format:
    1 0.85 1034.png
    """
    objects = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line:
            splitlines = line.strip().split(' ')
            object_struct = {}
            if (len(splitlines) == 3):
                object_struct['name'] = splitlines[2]
                object_struct['confidence'] = splitlines[1]
                # object_struct['number'] = splitlines[0]
                object_struct['pred_cls'] = classname
            else:
                logging.error('txtfile format error')
                break
            objects.append(object_struct)
        else:
            break
    return objects

def parse_gt(filename):
    """
    Ground Truth format:
    1034.png class0
    """
    objects = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line:
            splitlines = line.strip().split(' ')
            object_struct = {}
            if (len(splitlines) == 2):
                object_struct['name'] = splitlines[0]
                object_struct['cls_name'] = splitlines[1]
            objects.append(object_struct)
        else:
            break
    return objects


def plot_confusion_matrix(y_true, y_pred, classes=None, save_fig_path='',
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
            fig_name = 'Norm_cm.png'
        else:
            title = 'Confusion matrix, without normalization'
            fig_name = 'unNorm_cm.png'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Only use the labels that appear in the data
    # if not classes:
    #     classes = classes[unique_labels(y_true, y_pred)]

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # print("Normalized confusion matrix")
    # else:
        # print('Confusion matrix, without normalization')
    # print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(os.path.join(save_fig_path, fig_name))


def unzipFile(submit_path, unzip_parent='./unzips'):
    flag = False
    try:
        # basename = os.path.split(submit_path)[-1]  # delete the path ,only the file name
        # unzip_dir = os.path.join(unzip_parent, basename[:-4])  # delete the " .zip "
        unzip_dir = unzip_parent
        if not os.path.exists(unzip_dir):
            os.mkdir(unzip_dir)
        else:
            pass
        fh = open(submit_path, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            z.extract(name, unzip_dir)
        fh.close()
        # os.system('unzip '+submit_path+' -d '+unzip_dir)
    except Exception as e:
        # s = str(e)
        s = repr(e)
        logging.debug(s)
        logging.error("zip error")
        return [flag, s]
    else:
        # logging.info("zip ok")
        # print 'zip ok'
        flag = True
        return [flag, unzip_dir]

def get_filepath(dir):
    filenames = GetFileFromThisRootDir(dir)
    # flag = 0
    for file in filenames:
        if os.path.splitext(file)[1] == '.zip':
            return [True, file]
    return [False, '']

def get_cls_report(gt, pred, target_names):
    # print(accuracy_score(gt, pred))
    return classification_report(gt, pred, target_names)

def comp_top1(tp, imgnum):
    return float(tp) / float(imgnum)

def comp_top5(tp, imgnum):
    return float(tp)/float(imgnum)

def eval(detpath,annopath,save_fig_path,save_res_path,class_names):
    # assumes detections are in detpath.format(classname)
    # assumes annotations are in annopath.format(imagename)
    # res_flag = 0

    details = ''  # error message

    # load ground truth
    annofile = os.path.join(annopath, 'testset_gt.txt')
    objects_gt = parse_gt(annofile)
    testset_name = [obj['name'] for obj in objects_gt]
    testset_clsname = [obj['cls_name'] for obj in objects_gt]
    # print(testset_name)
    # print(testset_clsname)

    def _recursive_find_sub_dirs(curr_dir):
        for root, subdirs, files in os.walk(curr_dir):
            for s in files:
                if s.endswith(".txt"):
                    # dt_files.append(os.path.join(root, s ))
                    # sub_id_sub_dir_pairs.append(os.path.join(root, s))
                    return root
                else:
                    _recursive_find_sub_dirs(s)
        return ''

    dt_dir = _recursive_find_sub_dirs(detpath)

    # load results
    objects_res = []
    testset_pred = ['class0']*len(testset_clsname)
    top5_tp = 0
    top1_tp = 0
    for classname in class_names:
        try:
            detfile = glob(os.path.join(dt_dir, classname + '*' + '.txt'))[0]
        except:
            details = 'txtfile name error'
            logging.error(details)
            return [2, details]
        try:
            objects_res_cls = parse_result(detfile, classname)
            objects_res = objects_res + objects_res_cls
        except:
            details = 'txtfile line error (1 0.85 1034.png)'
            logging.error(details)
            return [2, details]
    # print(objects_res)

    for i, imgname in enumerate(testset_name):
        top5_obj = [obj for obj in objects_res if obj['name'] == imgname]
        if len(top5_obj) == 5:
            confidence = np.array([float(x['confidence']) for x in top5_obj])
            clses = [x['pred_cls'] for x in top5_obj]
            # print(confidence)
            # sort by confidence
            sorted_ind = np.argsort(-confidence)
            sorted_scores = np.sort(-confidence)
            sorted_cls = [clses[x] for x in sorted_ind]
            # print(sorted_cls)
            testset_pred[i] = sorted_cls[0]
            if testset_clsname[i] in sorted_cls:
                top5_tp += 1
            if testset_clsname[i] == testset_pred[i]:
                top1_tp += 1
        else:
            details = 'txtfile no top5'
            logging.error(details)
            return [2, details]

    top5_ac = comp_top5(top5_tp, len(testset_clsname))
    top1_ac = comp_top1(top1_tp, len(testset_clsname))
    cls_report = get_cls_report(testset_clsname, testset_pred, target_names=class_names)

    with open(os.path.join(save_res_path, 'accuracy.txt'), 'w') as f:
        f.write('top1_accuracy: ' + str(top1_ac) + '\n')
        f.write('top5_accuracy: ' + str(top5_ac) + '\n')
    with open(os.path.join(save_res_path, 'classification_report.txt'), 'w') as f:
        f.write(cls_report)
    plot_confusion_matrix(testset_clsname, testset_pred, classes=class_names,
                          save_fig_path=save_fig_path, normalize=True)
    plot_confusion_matrix(testset_clsname, testset_pred, classes=class_names,
                          save_fig_path=save_fig_path)

    return [0, 'success']


def get_score(root_path, annopath):
    '''
    res_flg:
    0, success
    1, error
    2, format error
    '''
    res_flag = [0, 'success']
    logging.basicConfig(filename=os.path.join(root_path, 'evaluation.log'), level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    # logging.debug("This is a debug log.")
    print('Starting evaluation for scene classification...')
    start = time.time()
    class_names = ['class0', 'class1', 'class2', 'class3', 'class4', 'class5']
    unzip_path = os.path.join(root_path, 'unzips')
    [state, zip_path] = get_filepath(root_path)
    if state:
        [flag, det_results] = unzipFile(zip_path, unzip_path)
    else:
        return [2, '']
    if not flag:
        return [2, '']   # unzip error
    detpath = det_results

    save_fig_path = os.path.join(root_path, 'figures')
    if not os.path.exists(save_fig_path):
        os.mkdir(save_fig_path)

    save_res_path = os.path.join(root_path, 'results')
    if not os.path.exists(save_res_path):
        os.mkdir(save_res_path)

    res_flag = eval(detpath, annopath, save_fig_path, save_res_path, class_names)
    end = time.time()
    print('cost time:', end-start, ' seconds')
    return res_flag

if __name__ == '__main__':
    root_path = './2/team_3'
    annopath = './scene_classification_gt'
    res = get_score(root_path, annopath)
    print(res[1])
    if res[0] == 0:
        logging.info('success')