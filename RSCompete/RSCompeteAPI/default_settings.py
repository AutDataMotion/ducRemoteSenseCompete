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
    tracking_gt = "/data/tracking/gt/RS_gt"    
    upload_count_perday = 50
    current_stage = "注册中" #目前的状态
    deadline = "2019/08/10"

    admin_username = "csu"
    admin_passwd = "csucsucsu"

    data_path = {1:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 2:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 3:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 4:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}, 5:{"url":"数据将于2019年6月15日发布，请耐心等待！", "code":""}}

    #竞赛类型 1-目标检测 2-场景分类 3-语义分割 4-变化检测 5-目标追踪
