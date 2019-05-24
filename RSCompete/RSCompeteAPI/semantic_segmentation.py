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

from matplotlib.colors import ListedColormap
fig, ax = plt.subplots()

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

    fig, ax = plt.subplots(figsize=(30,20))
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
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else '9.1f'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(os.path.join(save_fig_path, fig_name))

    #15
def plot_precision(precision_s,classes=None, save_fig_path='',
                          cmap=plt.cm.Blues):
    plt.style.use('seaborn-ticks')
    fig_name = 'precision.png'
#     precision_s = precision_s.astype('float')
    fig, ax = plt.subplots()

    plt.barh(range(16), precision_s, height=0.7, alpha=0.8)      # 从下往上画
    plt.yticks(range(16),classes)
    plt.xlim(0,1.0)
    plt.xlabel(u"Precison")
    plt.title(u"Precisions of different classes")
    for x, y in enumerate(precision_s):
        plt.text(y +0.01, x-0.3 , '%s' % y)


    plt.savefig(os.path.join(save_fig_path, fig_name),dpi=400, bbox_inches = 'tight')   
    plt.show()  
    
    

def show_result(path_image1,path_result,save_fig_path='./result'):
    files_img = GetFileFromThisRootDir(path_image1)
    files_result = GetFileFromThisRootDir(path_result)
    save_flag = 0
    pic_size = [800,800]
    start_position = [100,100]
    cMap = ListedColormap(['#000000', '#00C800', '#96FA00','#96C896','#C800C8','#9600FA','#9696FA','#FAC800','#C8C800','#C80000','#FA0096','#C89696','#FA9696','#0000C8','#0096C8','#00C8FA'])
    for img in files_img:
        for result in files_result:
            if(os.path.basename(img).split('.tif')[0] == os.path.basename(result).split("_label")[0]):
                plt.figure(figsize=(25,14))
                gs = gridspec.GridSpec(1, 2, width_ratios=[4, 5]) 
                ax1 = plt.subplot(gs[0])
                im = Image.open(img)
#                 w,h = im.size
                imc = im.crop((start_position[0], start_position[1], start_position[0]+pic_size[0],  start_position[1]+pic_size[1]))
                #ax1.imshow(imc)
                plt.title(u'Test image',fontsize=30)
                plt.axis('off') 
                ax2 = plt.subplot(gs[1])
                label = Image.open(result)
#                 w_1,h_1 = label.size
                labelc = label.crop((start_position[0], start_position[1], start_position[0]+pic_size[0],  start_position[1]+pic_size[1]))
                #ADD_color = ax2.imshow(labelc,cmap = cMap)  
                plt.title('Test result',fontsize=30)
                plt.axis('off') 
                plt.subplots_adjust(wspace =0.1, hspace =0,right = 0.8)
                
                
                ax3 = fig.add_subplot(1,1,1)
                ax3.axis('off')
                cbar = plt.colorbar(ADD_color)
                
                position = np.linspace(0.0,250.0,17)
                cbar.set_ticks(position-9.3)
                cbar.set_ticklabels(position-9.3)
                cbar.ax.set_yticklabels([u'others',u'irrigated land',u'paddy field',u'dry cropland',u'garden plot',u'arbor woodland',u'shrub land',u'natural grassland',u'artificial grassland',u'industrial land',u'urban residential',u'rural residential',u'traffic land',u'river',u'lake',u'pond'],minor=False)
#                 cbar.set_label('# Classes', rotation=270)
                
#                 plt.tight_layout()
                plt.savefig(os.path.join(save_fig_path,'show_result.png'))
                save_flag = 1 
#                 break
            if(save_flag == 1):
                break
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
#         print('zip error')
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



def get_score(root_path, annopath,test_pic_path):
    # res_flg: 0, success, 1, error, 2, format error
    logging.basicConfig(filename=os.path.join(root_path, 'change_detection.log'), level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.debug("This is a debug log.")
    print('Starting evaluation for change detection ...')
    start = time.time()
    numclass = 16;
    class_names = [u'others', u'irrigated land',u'paddy field',u'dry cropland',u'garden plot',u'arbor woodland',u'shrub land',u'natural grassland',u'artificial grassland',u'industrial land',u'urban residential',u'rural residential',u'traffic land',u'river',u'lake',u'pond']
    imagesetfile = os.path.join(annopath, 'testset.txt')
    labelpath = os.path.join(annopath, 'labelPNG')
    print("fuck")
    with open(imagesetfile, 'r') as f:
        lines = f.readlines()
    imagenames = [x.strip() for x in lines]
    Cal_array = np.zeros((16,16))
#     Cal_array = np.array([[1,2,3],[4,5,6],[7,8,9]])
    unzip_path = os.path.join(root_path, 'unzips_semantic_segmentation')
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
        print(labelpath)
        test_png_path = os.path.join(detpath, imagename)
        print(anno_png_path)
        print(test_png_path)
        anno_png = cv.imread(anno_png_path)
        test_png = cv.imread(test_png_path)
        print(np.shape(anno_png))
        print(np.shape(test_png))
        [width_, hight_, channel_] =  np.shape(anno_png)
        print(width_)
        if(np.shape(anno_png) == np.shape(test_png)):
            pass
        else:
            details = 'dimension is wrong.'
            logging.error(details)
            return [2, details]
        store_color = []

# opencv read as  b g r
        for i in range(width_):
            for j in range(hight_):
                    
                if ((test_png[i,j] == [0,0,0]).all()): #others 
                    a = 0;
                elif((test_png[i,j] == [0,200,0]).all()):
                    a = 1;
                elif((test_png[i,j] == [0,250,150]).all()):
                    a = 2;
                elif((test_png[i,j] == [150,200,150]).all()):
                    a = 3;  
                elif((test_png[i,j] == [200,0,200]).all()):
                    a = 4;                     
                elif((test_png[i,j] == [250,0,150]).all()):
                    a = 5; 
                elif((test_png[i,j] == [250,150,150]).all()):
                    a = 6; 
                elif((test_png[i,j] == [0,200,250]).all()):
                    a = 7; 
                elif((test_png[i,j] == [0,200,200]).all()):
                    a = 8; 
                elif((test_png[i,j] == [0,0,200]).all()):
                    a = 9; 
                elif((test_png[i,j] == [150,0,250]).all()):
                    a = 10; 
                elif((test_png[i,j] == [150,150,200]).all()):
                    a = 11; 
                elif((test_png[i,j] == [150,150,250]).all()):
                    a = 12; 
                elif((test_png[i,j] == [200,0,0]).all()):
                    a = 13; 
                elif((test_png[i,j] == [200,150,0]).all()):
                    a = 14; 
                elif((test_png[i,j] == [250,200,0]).all()):
                    a = 15; 
                else:
                    a = 0;
#                     log = "Not the true format."
#                     print(test_png[i,j])
#                     print(i)
#                     print(j)
#                     return log
                
                if ((anno_png[i,j] == [0,0,0]).all()): #others 
                    b = 0;
                elif((anno_png[i,j] == [0,200,0]).all()):
                    b = 1;
                elif((anno_png[i,j] == [0,250,150]).all()):
                    b = 2;
                elif((anno_png[i,j] == [150,200,150]).all()):
                    b = 3;  
                elif((anno_png[i,j] == [200,0,200]).all()):
                    b = 4;                     
                elif((anno_png[i,j] == [250,0,150]).all()):
                    b = 5; 
                elif((anno_png[i,j] == [250,150,150]).all()):
                    b = 6; 
                elif((anno_png[i,j] == [0,200,250]).all()):
                    b = 7; 
                elif((anno_png[i,j] == [0,200,200]).all()):
                    b = 8; 
                elif((anno_png[i,j] == [0,0,200]).all()):
                    b = 9; 
                elif((anno_png[i,j] == [150,0,250]).all()):
                    b = 10; 
                elif((anno_png[i,j] == [150,150,200]).all()):
                    b = 11; 
                elif((anno_png[i,j] == [150,150,250]).all()):
                    b = 12; 
                elif((anno_png[i,j] == [200,0,0]).all()):
                    b = 13; 
                elif((anno_png[i,j] == [200,150,0]).all()):
                    b = 14; 
                elif((anno_png[i,j] == [250,200,0]).all()):
                    b = 15; 
                else:
                    b = 0
#                     log = "Not the true format."
#                     print(anno_png[i,j])
#                     print(i)
#                     print(j)
#                     return log
                Cal_array[a,b] = Cal_array[a,b]  + 1
#     Cal_array = np.eye(16)
    labels = ('Matrix', 'OA','Pr(a)', 'Pr(e)', 'kappa','precision_s')
    separator = ' : '
    width = max(map(len, labels))
    indent = ' ' * (width + len(separator))
    matrix = ('\n' + indent).join(map(str, Cal_array))
#     IOU_A = float(Cal_array[1,1])/(Cal_array.sum(axis=0)[1]+Cal_array.sum(axis=1)[1]-Cal_array[1,1])
#     IOU_B = float(Cal_array[2,2])/(Cal_array.sum(axis=0)[2]+Cal_array.sum(axis=1)[2]-Cal_array[2,2])
#     IOU_C = float(Cal_array[0,0])/(Cal_array.sum(axis=0)[0]+Cal_array.sum(axis=1)[0]-Cal_array[0,0])
#     mIOU = (IOU_A + IOU_B + IOU_C)/3
    precision_s = [0.0]*16
    for i,precision in enumerate(precision_s):
        precision_s[i] = float(Cal_array[i,i])/max(Cal_array.sum(axis=0)[i],1)
    OA =  observed(Cal_array)
    results_dict = {}
    values = (matrix, OA, observed(Cal_array), expected(Cal_array), kappa(Cal_array),precision_s)
    for i in range(len(labels)):
        results_dict[labels[i]] = values[i]
    output = ''.join(('{:>', str(width), '}', separator, '{}'))
    print('\n'.join(output.format(*record) for record in zip(labels, values)))

    dt_name = 'semantic_segmentation.json'
    if not os.path.exists(os.path.join(root_path, 'results_semantic_segmentation')):
        os.mkdir(os.path.join(root_path, 'results_semantic_segmentation'))
    save_file = os.path.join(root_path, 'results_semantic_segmentation', dt_name)
    with open(save_file, 'w') as f:
        json.dump(results_dict, f)
#         f.write('\n'.join(output.format(*record) for record in zip(labels, values)))
    save_fig_path = os.path.join(root_path, 'figures')
    if not os.path.exists(save_fig_path):
        os.mkdir(save_fig_path)
    plot_confusion_matrix(Cal_array, classes=class_names,
                          save_fig_path=save_fig_path, normalize=True)
    plot_confusion_matrix(Cal_array, classes=class_names,
                          save_fig_path=save_fig_path,normalize=False)
    plot_precision(precision_s,classes=class_names, save_fig_path=save_fig_path)
    show_result(test_pic_path,detpath,save_fig_path=save_fig_path)
    end = time.time()
    print('cost time:',end-start,' seconds')

    return 0, "success"
if __name__ == '__main__':
    root_path = './3/team_1'
    annopath = './SS_gt'
    test_pic_path = "./test_pics/"
    res = get_score(root_path, annopath,test_pic_path)
    if res == "success":
        logging.info('success')
    print(res)