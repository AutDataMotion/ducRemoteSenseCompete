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
import cv2 as cv
import json
from matplotlib import gridspec 
from PIL import Image


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


def plot_confusion_matrix(cm,classes=None, save_fig_path='',
                          normalize=False,
                          cmap=plt.cm.Blues):
    """
    This function plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        title = 'Normalized confusion matrix'
        fig_name = 'Norm_cm.png'
    else:
        title = 'Confusion matrix, without normalization'
        fig_name = 'unNorm_cm.png'



    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # print("Normalized confusion matrix")
    else:
        cm = cm.astype('float') 
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
    fmt = '.2f' if normalize else '7.1f'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(os.path.join(save_fig_path, fig_name))

    #15
def show_result(path_image1,path_result,save_fig_path='./result'):
    files_img = GetFileFromThisRootDir(path_image1)
    files_result = GetFileFromThisRootDir(path_result)
#     files_img = [os.path.basename(t) for t in files_img]
    save_flag = 0
    pic_size = [960,960]
    start_position = [0,0]
    for img in files_img:
        str_name = os.path.basename(img).split('_')[-1]
        img_2017 = os.path.join(path_image1,"image_2017_960_960_"+str_name)
        img_2018 = os.path.join(path_image1,"image_2018_960_960_"+str_name)
        if((img_2017 in files_img)and(img_2018 in files_img)):
#             if(os.path.basename(img).split('.tif')[0] == os.path.basename(result).split("_label")[0]):
                plt.figure(figsize=(30,9))
                gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1,1]) 
                ax1 = plt.subplot(gs[0])
                im =  cv.imread(img_2017)
#                 w,h = im.size
#                 imc = im.crop((start_position[0], start_position[1], start_position[0]+pic_size[0],  start_position[1]+pic_size[1]))
                imc = np.array(im,dtype=np.uint16)
                ax1.imshow(imc)
                plt.title(u'2017 image',fontsize=30)
                plt.axis('off') 
                ax2 = plt.subplot(gs[1])
                im2 = cv.imread(img_2018)
                imc2 = np.array(im2,dtype=np.uint16)
#                 w_1,h_1 = label.size
#                 imc2 = im2.crop((start_position[0], start_position[1], start_position[0]+pic_size[0],  start_position[1]+pic_size[1]))
                ax2.imshow(imc2)
                plt.title('2018 image',fontsize=30)
                plt.axis('off') 
                ax3 = plt.subplot(gs[2])
                label = Image.open(img)
#                 w,h = im.size
                labelc = label.crop((start_position[0], start_position[1], start_position[0]+pic_size[0],  start_position[1]+pic_size[1]))
                ax3.imshow(labelc)  
                plt.title('Test result',fontsize=30)
                plt.axis('off')        
        
                plt.subplots_adjust(wspace =0.1, hspace =0)

                plt.tight_layout()
                plt.savefig(os.path.join(save_fig_path,'show_result.png'))
                save_flag = 1 

        if(save_flag == 1):
            break
    if(save_flag == 0):
        details = 'No matched result.Please ensure the result filename'
        print(details)
    else:
        print("create vis pic ok.")

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
        logging.debug("zip error")
        logging.debug(s)
        print('zip error')
        return [flag, s]
    else:
        logging.info("zip ok")
        print('zip ok')
        flag = True
        return [flag, unzip_dir]

def get_filepath(dir):
    filenames = GetFileFromThisRootDir(dir)
    # flag = 0
    for file in filenames:
        if os.path.splitext(file)[1] == '.zip':
            return [True, file]
    return [False, '']


def kappa(data):
    """Computes Cohen's Kappa coefficient given a confusion matrix.
    Where Pr(a) is the percentage of observed agreement and Pr(e) is percentage 
    of expected agreement."""
    observation = observed(data)
    expectation = expected(data)
    perfection = 1.0
    k = np.divide(
        observation - expectation,
        perfection - expectation
    )
    return k

def observed(data):
    """Computes the observed agreement, Pr(a), between annotators."""
    total = float(np.sum(data))
    agreed = np.sum(data.diagonal())
    percent_agreement = agreed / total
    return percent_agreement

def expected(data):
    """Computes the expected agreement, Pr(e), between annotators."""
    total = float(np.sum(data))
    annotators = range(len(data.shape))
    percentages = ((data.sum(axis=i) / total) for i in annotators) 
    percent_expected = np.dot(*percentages)
    return percent_expected



def get_score(root_path, annopath,path_test_image):
    # res_flg: 0, success, 1, error, 2, format error
    logging.basicConfig(filename=os.path.join(root_path, 'change_detection.log'), level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.debug("This is a debug log.")
    print('Starting evaluation for change detection ...')
    start = time.time()
    numclass = 2;
    class_names = ['changed', 'unchanged']
    imagesetfile = os.path.join(annopath, 'testset.txt')
    labelpath = os.path.join(annopath, 'labelTIF')
    with open(imagesetfile, 'r') as f:
        lines = f.readlines()
    imagenames = [x.strip() for x in lines]
    Cal_array = np.zeros((numclass,numclass))
#     Cal_array = np.array([[1,2,3],[4,5,6],[7,8,9]])
    unzip_path = os.path.join(root_path, 'unzips_change_detection')
    [state, zip_path] = get_filepath(root_path)
    if state:
        [flag, res] = unzipFile(zip_path, unzip_path)
    else:
        return [2, '', 0, '']
    print('zip flag',flag)
    if not flag:
        details = 'unzip  error'
        logging.error(details)
        return [2, res, 0,'']   ##unzip error
    detpath = res

    for i, imagename in enumerate(imagenames):
        # print('parse_files name: ', annopath.format(imagename))
        anno_png_path = os.path.join(labelpath, imagename)
        test_png_path = os.path.join(detpath, imagename)
        print(anno_png_path)
        print(test_png_path)
        anno_png = np.array(Image.open(anno_png_path))
        test_png = np.array(Image.open(test_png_path))
        print(np.shape(anno_png))
        print(np.shape(test_png))
        [width_, hight_] =  np.shape(anno_png)
        print(width_)
        if(np.shape(anno_png) == np.shape(test_png)):
            pass
        else:
            details = 'dimension is wrong.'
            logging.error(details)
            return [2, details]
        
#         print(test_png[3,3])
# opencv read as  b g r
        for i in range(width_):
            for j in range(hight_):
                if ((test_png[i,j] == 0).all()):
                    a = 0;
                elif((test_png[i,j] == 255).all()):
                    a = 1;
                else:
                    log = "Not the true format."
                    return log

                if ((anno_png[i,j] == 0).all()):
                    b = 0;
                elif((anno_png[i,j] == 255).all()):
                    b = 1;
                else:
                    log = "Not the true format."
                    return log
                    
                Cal_array[a,b] = Cal_array[a,b]  + 1

    labels = ('Matrix', 'OA','Pr(a)', 'Pr(e)', 'kappa','IOU_change','F1_score')
    separator = ' : '
    width = max(map(len, labels))
    indent = ' ' * (width + len(separator))
    matrix = ('\n' + indent).join(map(str, Cal_array))
    IOU_change = float(Cal_array[1,1])/(Cal_array.sum(axis=0)[1]+Cal_array.sum(axis=1)[1]-Cal_array[1,1])
    F1_score = Cal_array[1,1]/(Cal_array.sum(axis=0)[1]+Cal_array.sum(axis=1)[1])
    OA =  observed(Cal_array)
    results_dict = {}
    values = (matrix, OA, observed(Cal_array), expected(Cal_array), kappa(Cal_array),IOU_change,F1_score)
    for i in range(len(labels)):
        results_dict[labels[i]] = values[i]
    output = ''.join(('{:>', str(width), '}', separator, '{}'))
    print('\n'.join(output.format(*record) for record in zip(labels, values)))

    dt_name = 'change_detection.json'
    if not os.path.exists(os.path.join(root_path, 'results_change_detection')):
        os.mkdir(os.path.join(root_path, 'results_change_detection'))
    save_file = os.path.join(root_path, 'results_change_detection', dt_name)
    with open(save_file, 'w') as f:
        json.dump(results_dict, f)
#         f.write('\n'.join(output.format(*record) for record in zip(labels, values)))
    save_fig_path = os.path.join(root_path, 'figures')
    if not os.path.exists(save_fig_path):
        os.mkdir(save_fig_path)
    print("fuck1")
    plot_confusion_matrix(Cal_array, classes=class_names,
                          save_fig_path=save_fig_path, normalize=True)
    print("fuck2")
    plot_confusion_matrix(Cal_array, classes=class_names,
                          save_fig_path=save_fig_path,normalize=False)
    print("fuck3")
    show_result(path_test_image,detpath,save_fig_path=save_fig_path)
    end = time.time()
    print('cost time:',end-start,' seconds')

    return 0, "success"
if __name__ == '__main__':
    root_path = './4/team_1'
    annopath = './CD_gt'
    path_test_image = "./section4_sample/"
    res = get_score(root_path, annopath,path_test_image)
    if res == "success":
        logging.info('success')
    print(res)