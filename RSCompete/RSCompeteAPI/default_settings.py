class System_Config():
    #在该类中进行系统设置
    #最好使用绝对路径
    result_root_dir = "/data/results"
    team_member_number = 5
    leader_board_root_dir = "/home/xuan/ducRemoteSenseCompete/leadboard"
    #scene_classification_gt = "/home/xuan/ducRemoteSenseCompete/NSFC_contest/scene_classification_gt"
    scene_classification_gt = "/data/NSFC_contest_scene_cls/scene_classification_gt"
    change_detection_gt = "/data/change_detection/CD_gt"
    semantic_segmentation_gt = "/data/semantic_segmentation/SS_gt"
    scene_classification_test_image_path = "/data/NSFC_contest_scene_cls/vis_imgs"
    change_detection_test_image_path = "/data/change_detection/section4_sample"
    semantic_segmentation_test_image_path = "/data/semantic_segmentation/test_pics"
    detection_gt = "/data/detection/test_challenge_c1_gt"
    detection_test_image_path = "/data/detection/visualize_images"
    tracking_gt = "/data/Stage_1_groundtruth"    
    upload_count_perday = 0
   # current_stage = "注册中" #目前的状态
    current_stage = "数据发布"
    deadline = "2019/08/10"

    admin_username = "csu"
    admin_passwd = "csucsucsu"

   # data_path = {1:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 2:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 3:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 4:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 5:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}}
    data_path = {1:{"url":"https://pan.baidu.com/s/1pw8SmeZ23VRSLXquefiRTA", "code":"hms2"}, 2:{"url":"https://pan.baidu.com/s/1SYgYm85sJo7TrvmDm0d0zQ", "code":"3neo"}, 3:{"url":"https://pan.baidu.com/s/1gx4Si7S17Uqe3bt_cVkULw", "code":"v785"}, 4:{"url":"https://pan.baidu.com/s/1BsGTuRkWAR-y2LO5GGTsoA", "code":"p4cf"}, 5:{"url":"https://pan.baidu.com/s/1GXJHQRn9MtqtuZ-D73c26Q", "code":"prle"}}

    #竞赛类型 1-目标检测 2-场景分类 3-语义分割 4-变化检测 5-目标追踪
