class System_Config():
    #在该类中进行系统设置
    #最好使用绝对路径
    result_root_dir = "../results"
    team_member_number = 5
    leader_board_root_dir = "/home/xuan/ducRemoteSenseCompete/leadboard"
    #scene_classification_gt = "/home/xuan/ducRemoteSenseCompete/NSFC_contest/scene_classification_gt"
    scene_classification_gt = "/home/xuan/下载/interfaces2/NSFC_contest_scene_cls/scene_classification_gt"
    change_detection_gt = "/home/xuan/下载/interfaces2/NSFC_contest/CD_gt"
    semantic_segmentation_gt = "/home/xuan/下载/interfaces2/semantic_segmentation/SS_gt"
    scene_classification_test_image_path = "/home/xuan/下载/interfaces2/NSFC_contest_scene_cls/vis_imgs"
    change_detection_test_image_path = "/home/xuan/下载/interfaces2/NSFC_contest/section4_sample"
    semantic_segmentation_test_image_path = "/home/xuan/下载/interfaces2/semantic_segmentation/test_pics"

    
    
    upload_count_perday = 50
    current_stage = "注册中" #目前的状态
    deadline = "2019/06/30"




    #竞赛类型 1-目标检测 2-场景分类 3-语义分割 4-变化检测 5-目标追踪
