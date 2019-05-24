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
import json
import random
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import cv2
from sklearn.metrics import accuracy_score
# from sklearn.utils.multiclass import unique_labels


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

Error_Type = {0: 'Success', 1: 'Zip error', 2: 'File error', 3: 'File line error',
              4: 'Image name error'}

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

# def parse_result_top5(filename):
#     """
#     clssification result format:
#     1034.png cls1 cls2 cls3 cls4 cls5
#     """
#     objects = []
#     with open(filename, 'r') as f:
#         lines = f.readlines()
#     for line in lines:
#         if line:
#             splitlines = line.strip().split(' ')
#             object_struct = {}
#             if len(splitlines) == 6:
#                 object_struct['name'] = splitlines[0]
#                 # object_struct['confidence'] = splitlines[1]
#                 # object_struct['number'] = splitlines[0]
#                 object_struct['pred1'] = splitlines[1]
#                 object_struct['pred2'] = splitlines[2]
#                 object_struct['pred3'] = splitlines[3]
#                 object_struct['pred4'] = splitlines[4]
#                 object_struct['pred5'] = splitlines[5]
#             else:
#                 assert len(splitlines) == 6, Error_Type[2]
#                 logging.error(Error_Type[2]+': '+line)
#             objects.append(object_struct)
#     return objects

def parse_result_top1(filename):
    """
    clssification result format:
    1034.png cls_pred
    """
    objects = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line:
            try:
                splitlines = line.strip().split(' ')
                object_struct = {}
                object_struct['name'] = splitlines[0]
                object_struct['pred'] = splitlines[1]
            except Exception as e:
                s = repr(e) + ' (line: ' + line.strip() + ')'
                return [3, s, []]
            else:
                objects.append(object_struct)
    return [0, '', objects]

def parse_gt(filename):
    """
    Ground Truth format:
    1034.png cls_gt
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
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    print(cm)

    # Only use the labels that appear in the data
    # if not classes:
    #     classes = unique_labels(y_true, y_pred)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # print("Normalized confusion matrix")
    # else:
        # print('Confusion matrix, without normalization')
    # print(cm)

    fig, ax = plt.subplots(figsize=(20, 16))
    #im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
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
    # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #          rotation_mode="anchor")

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

def unzipFile(submit_path, unzip_path):
    try:
        if not os.path.exists(unzip_path):
            os.mkdir(unzip_path)
        else:
            pass
        fh = open(submit_path, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            z.extract(name, unzip_path)
        fh.close()
        # os.system('unzip '+submit_path+' -d '+unzip_dir)
    except Exception as e:
        s = repr(e)
        return [1, s]
    else:
        # logging.info("zip ok")
        return [0, '']

def comp_top1(tp, imgnum):
    return float(tp) / float(imgnum)

# def comp_top5(tp, imgnum):
#     return float(tp)/float(imgnum)

def get_vis(vis_img_path, name2gt, name2pred, save_fig_path):
    vis_imgs = os.listdir(vis_img_path)
    vis_imgs = random.sample(vis_imgs, 25)  # display 5*5 images
    blank_img = np.zeros((1150, 1150, 3), np.uint8)  # Create a blank large image(230*5)
    count = 0
    for img in vis_imgs:
        count += 1
        rows = count // 5 + 1
        cols = count % 5
        if count % 5 == 0:
            rows -= 1
            cols = 5
        # print(rows, cols)
        img_path = os.path.join(vis_img_path, img)
        img_data = cv2.imread(img_path)
        img_data = cv2.resize(img_data, (200, 200))
        if name2pred[img] == name2gt[img]:
            frame_img = cv2.copyMakeBorder(img_data, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 255, 0])
            # cv2.imwrite('frame_{}'.format(img), frame_img)
        else:
            frame_img = cv2.copyMakeBorder(img_data, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 0, 255])
            # cv2.imwrite('frame_{}'.format(img), frame_img)
        frame_img = cv2.copyMakeBorder(frame_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        # print(frame_img.shape)
        blank_img[(rows - 1) * 230:rows * 230, (cols - 1) * 230:cols * 230] = frame_img
    cv2.imwrite(os.path.join(save_fig_path, 'vis.png'), blank_img)



def eval(respath, annopath, vis_img_path, save_fig_path, save_scr_path, class_names):
    name2gt = {}
    name2pred = {}
    # load ground truth
    annofile = os.path.join(annopath, 'testset_gt.txt')
    objects_gt = parse_gt(annofile)
    for obj in objects_gt:
        name2gt[obj['name']] = obj['cls_name']
        name2pred[obj['name']] = 'none'      #initialize pred
    # load results
    resfiles = GetFileFromThisRootDir(respath, '.txt')
    if not len(resfiles) == 1:
        return 2, 'more than one txt file in the zip'
    resfile = resfiles[0]
    [readtxt_flag, detail, objects_res] = parse_result_top1(resfile)
    if readtxt_flag != 0:
        # logging.error(Error_Type[readtxt_flag] + detail)
        return readtxt_flag, detail
    if len(objects_gt) != len(objects_res):
        logging.info('Warning: The number of gts and preds is different: {} gts, {} preds'.format(len(objects_gt), len(objects_res)))
    for obj in objects_res:
        name2pred[obj['name']] = obj['pred']

    # compute OA(top1-ac)
    top1_tp = 0
    for img_name in name2gt.keys():
        if name2gt[img_name] == name2pred[img_name]:
            top1_tp += 1
    top1_ac = comp_top1(top1_tp, len(name2gt))

    if list(name2gt.keys()) == list(name2pred.keys()):
        test_gt = np.array(list(name2gt.values()))
        test_pred = np.array(list(name2pred.values()))
        # print(accuracy_score(y_true=test_gt, y_pred=test_pred))
        cls_report = classification_report(y_true=test_gt, y_pred=test_pred, labels=class_names)
        json_data = {
            'overall-accuracy': top1_ac,
            'cls-report': cls_report
        }

        # save scores to json
        with open(os.path.join(save_scr_path, 'cls_scores.json'), 'w') as json_file:
            json_file.write(json.dumps(json_data, indent=4))

        # save Confusion Matrix figures
        # plot_confusion_matrix(test_gt, test_pred, classes=class_names,
        #                       save_fig_path=save_fig_path, normalize=True)
        # plot_confusion_matrix(test_gt, test_pred, classes=class_names,
        #                       save_fig_path=save_fig_path)

        # select vis
        get_vis(vis_img_path, name2gt, name2pred, save_fig_path)
        return 0, ''
    else:
        return 4, 'There exist some image names not in the test set'




def get_score(root_path, annopath, vis_img_path):
    '''
    :param root_path: the path of submitted zip file
    :param annopath: the path of testset_gt.txt
    :return:
    '''
    logging.basicConfig(filename=os.path.join(root_path, 'evaluation.log'), level=logging.INFO, format=LOG_FORMAT,
                        datefmt=DATE_FORMAT)
    # print('Starting evaluation for scene classification...')
    # start = time.time()
    class_names = [str(i) for i in range(1, 46)]
    # print(class_names)
    zip_path = os.path.join(root_path, 'classification.zip')
    unzip_path = os.path.join(root_path, 'unzips')
    # if os.path.isfile(zip_path):
    [unzip_flag, unzip_detail] = unzipFile(zip_path, unzip_path)
    if unzip_flag != 0:
        logging.error(Error_Type[unzip_flag] + ': ' + unzip_detail)
        return unzip_flag, unzip_detail

    save_fig_path = os.path.join(root_path, 'figures')
    if not os.path.exists(save_fig_path):
        os.mkdir(save_fig_path)
    save_scr_path = os.path.join(root_path, 'scores')
    if not os.path.exists(save_scr_path):
        os.mkdir(save_scr_path)

    res_flag, res_detail = eval(unzip_path, annopath, vis_img_path, save_fig_path, save_scr_path, class_names)
    # if res_flag != 0:
    #     logging.error(Error_Type[res_flag] + ': ' + res_detail)
    #     return unzip_flag, detail

    # end = time.time()
    # logging.info(end-start)
    # print('cost time:', end-start, ' seconds')
    return res_flag, res_detail

if __name__ == '__main__':
    root_path = './team_files/team_1'
    annopath = './scene_classification_gt'
    vis_img_path = './vis_imgs'
    flag, detail = get_score(root_path, annopath, vis_img_path)
    print(Error_Type[flag] + ': ' + detail)
    if flag != 0:
        logging.info('error')

