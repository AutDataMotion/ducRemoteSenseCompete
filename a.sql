-- MySQL dump 10.13  Distrib 5.7.26, for Linux (x86_64)
--
-- Host: localhost    Database: RSCompete
-- ------------------------------------------------------
-- Server version	5.7.26-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `RSCompeteAPI_competition`
--

DROP TABLE IF EXISTS `RSCompeteAPI_competition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RSCompeteAPI_competition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `announcement` longtext NOT NULL,
  `dataset` varchar(128) NOT NULL,
  `rule` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RSCompeteAPI_competition`
--

LOCK TABLES `RSCompeteAPI_competition` WRITE;
/*!40000 ALTER TABLE `RSCompeteAPI_competition` DISABLE KEYS */;
INSERT INTO `RSCompeteAPI_competition` VALUES (1,'2','3','4'),(2,'3','4','2');
/*!40000 ALTER TABLE `RSCompeteAPI_competition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RSCompeteAPI_result`
--

DROP TABLE IF EXISTS `RSCompeteAPI_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RSCompeteAPI_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_stamp` bigint(20) NOT NULL,
  `score` double NOT NULL,
  `is_review` tinyint(1) NOT NULL,
  `competition_id_id` int(11) NOT NULL,
  `team_id_id` int(11) NOT NULL,
  `user_id_id` int(11) NOT NULL,
  `root_dir` varchar(128) NOT NULL,
  `file_name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `RSCompeteAPI_result_competition_id_id_7e20218b_fk_RSCompete` (`competition_id_id`),
  KEY `RSCompeteAPI_result_team_id_id_de064c36_fk_RSCompeteAPI_team_id` (`team_id_id`),
  KEY `RSCompeteAPI_result_user_id_id_d5352312` (`user_id_id`),
  CONSTRAINT `RSCompeteAPI_result_competition_id_id_7e20218b_fk_RSCompete` FOREIGN KEY (`competition_id_id`) REFERENCES `RSCompeteAPI_competition` (`id`),
  CONSTRAINT `RSCompeteAPI_result_team_id_id_de064c36_fk_RSCompeteAPI_team_id` FOREIGN KEY (`team_id_id`) REFERENCES `RSCompeteAPI_team` (`id`),
  CONSTRAINT `RSCompeteAPI_result_user_id_id_d5352312_fk_RSCompeteAPI_user_id` FOREIGN KEY (`user_id_id`) REFERENCES `RSCompeteAPI_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RSCompeteAPI_result`
--

LOCK TABLES `RSCompeteAPI_result` WRITE;
/*!40000 ALTER TABLE `RSCompeteAPI_result` DISABLE KEYS */;
INSERT INTO `RSCompeteAPI_result` VALUES (1,1554721661207,-1,0,1,1,6,'',''),(5,1554722086295,-1,0,1,1,6,'',''),(6,1554723432149,-1,0,1,1,6,'',''),(7,1554723436616,-1,0,1,1,6,'',''),(8,1554723437179,-1,0,1,1,6,'',''),(9,1554723437942,-1,0,1,1,6,'',''),(10,1554723438511,-1,0,1,1,6,'',''),(11,1554723439118,-1,0,1,1,6,'',''),(12,1554723439739,-1,0,1,1,6,'',''),(13,1554723440553,-1,0,1,1,6,'',''),(14,1554723441410,-1,0,1,1,6,'',''),(15,1554723442074,-1,0,1,1,6,'',''),(16,1554723442789,-1,0,1,1,6,'',''),(17,1554723443375,20,0,1,1,6,'',''),(18,1554723444129,-1,0,1,1,6,'',''),(19,1554723444854,-1,0,1,1,6,'',''),(20,1554723445613,-1,0,1,1,6,'',''),(21,1554723446169,-1,0,1,1,6,'',''),(22,1554723446850,-1,0,1,1,6,'',''),(23,1554723447695,-1,0,1,1,6,'',''),(24,1554723448317,-1,0,1,1,6,'',''),(25,1554723448952,-1,0,1,1,6,'',''),(26,1554723449538,-1,0,1,1,6,'',''),(27,1554723450323,-1,0,1,1,6,'',''),(28,1554723450828,-1,0,1,1,6,'',''),(29,1554723451423,-1,0,1,1,6,'',''),(30,1554804766049,-1,0,1,29,2,'',''),(31,1554804767115,-1,0,1,29,2,'',''),(32,1554804768010,-1,0,1,29,2,'',''),(33,1556072430725,-1,0,1,29,2,'',''),(34,1556094016929,-1,0,1,29,2,'',''),(35,1556095114206,-1,0,1,29,2,'../results/1/29/1556095114206',''),(36,1556095616633,-1,0,1,29,2,'../results/1/29/1556095616633',''),(37,1556095958216,0.875,0,1,29,2,'../results/1/29/1556095958216',''),(38,1556348709382,0.875,0,1,29,2,'../results/1/29/1556348709382','');
/*!40000 ALTER TABLE `RSCompeteAPI_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RSCompeteAPI_team`
--

DROP TABLE IF EXISTS `RSCompeteAPI_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RSCompeteAPI_team` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `team_name` varchar(32) NOT NULL,
  `captain_name` varchar(32) NOT NULL,
  `competition_id_id` int(11) NOT NULL,
  `invite_code` varchar(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `team_name` (`team_name`),
  UNIQUE KEY `RSCompeteAPI_team_invite_code_c7c5d512_uniq` (`invite_code`),
  KEY `RSCompeteAPI_team_competition_id_id_c4e67c20_fk_RSCompete` (`competition_id_id`),
  CONSTRAINT `RSCompeteAPI_team_competition_id_id_c4e67c20_fk_RSCompete` FOREIGN KEY (`competition_id_id`) REFERENCES `RSCompeteAPI_competition` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RSCompeteAPI_team`
--

LOCK TABLES `RSCompeteAPI_team` WRITE;
/*!40000 ALTER TABLE `RSCompeteAPI_team` DISABLE KEYS */;
INSERT INTO `RSCompeteAPI_team` VALUES (1,'duc','x',1,'1235'),(29,'ducdd','xx',1,'1236'),(67,'ducddddd','xx',1,'1239'),(69,'ducdda','xx',1,'BoTW'),(70,'ducddaa','xx',2,'OW8E'),(76,'ducddaaf','xx',1,'0tQt'),(77,'ducddddddf','xx',1,'8KtO');
/*!40000 ALTER TABLE `RSCompeteAPI_team` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RSCompeteAPI_user`
--

DROP TABLE IF EXISTS `RSCompeteAPI_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RSCompeteAPI_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  `country` varchar(32) NOT NULL,
  `province` varchar(32) NOT NULL,
  `city` varchar(32) NOT NULL,
  `work_id` int(11) NOT NULL,
  `phone_number` varchar(11) NOT NULL,
  `ID_card` varchar(18) NOT NULL,
  `email` varchar(64) NOT NULL,
  `is_captain` tinyint(1) NOT NULL,
  `competition_id_id` int(11) NOT NULL,
  `team_id_id` int(11) NOT NULL,
  `work_place_second` varchar(64) NOT NULL,
  `work_place_third` varchar(64) NOT NULL,
  `work_place_top` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `ID_card` (`ID_card`),
  UNIQUE KEY `email` (`email`),
  KEY `RSCompeteAPI_user_competition_id_id_fcb87021_fk_RSCompete` (`competition_id_id`),
  KEY `RSCompeteAPI_user_team_id_id_5f3c6b1c_fk_RSCompeteAPI_team_id` (`team_id_id`),
  CONSTRAINT `RSCompeteAPI_user_competition_id_id_fcb87021_fk_RSCompete` FOREIGN KEY (`competition_id_id`) REFERENCES `RSCompeteAPI_competition` (`id`),
  CONSTRAINT `RSCompeteAPI_user_team_id_id_5f3c6b1c_fk_RSCompeteAPI_team_id` FOREIGN KEY (`team_id_id`) REFERENCES `RSCompeteAPI_team` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RSCompeteAPI_user`
--

LOCK TABLES `RSCompeteAPI_user` WRITE;
/*!40000 ALTER TABLE `RSCompeteAPI_user` DISABLE KEYS */;
INSERT INTO `RSCompeteAPI_user` VALUES (1,'x','1234','china','5','beijing',1,'12345678810','123456789987654321','a@a.cn',1,1,1,'','',''),(2,'xx','654','china','5','beijing',1,'12345678811','123456789987654322','a@a.cnc',1,1,29,'','',''),(3,'xx','123','china','5','beijing',1,'12345678814','123456789987654324','a@a.cnc2',0,1,1,'','',''),(4,'xx','123','china','5','beijing',1,'12345678816','123456789987654325','a@a.cncm',0,1,1,'','',''),(5,'xx','123','china','5','beijing',1,'12345678819','123456789987654320','ab@a.cncm',0,1,1,'','',''),(6,'xx','123','china','5','beijing',1,'12345678823','123456789987654312','abc@a.cncm',0,1,1,'','',''),(7,'xx','123','china','5','beijing',1,'12445678823','123456789982654312','1abc@a.cncm',0,1,29,'','',''),(8,'xx','123','china','5','beijing',1,'12445678820','123456789982654302','1abc@a.cncm2',1,1,67,'','',''),(9,'xx','123','china','5','beijing',1,'12445678800','123456789982654347','1abc@a.cncm22',0,1,29,'','',''),(10,'xx','123','china','5','beijing',1,'12345678233','123456789987654343','abc@a.cncma',0,1,67,'233','466','asaa'),(11,'xx','123','china','5','beijing',1,'12345678232','123456789987654234','abc@a.cncma1',1,1,69,'233','466','asaa'),(12,'xx','123','china','5','beijing',1,'12345678230','123456789987654239','abc@a.cncma1s',1,2,70,'233','466','asaa'),(19,'xx','123','china','5','beijing',1,'12345678777','123456789987654231','zhaozifei18@csu.ac.cn',1,1,76,'233','466','asaa'),(20,'xx','123','china','5','beijing',1,'12445678123','123456789982654232','1abc@a.cncm22f',1,1,77,'fasdfa','fff','asaa');
/*!40000 ALTER TABLE `RSCompeteAPI_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add user',2,'add_user'),(6,'Can change user',2,'change_user'),(7,'Can delete user',2,'delete_user'),(8,'Can view user',2,'view_user'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add permission',4,'add_permission'),(14,'Can change permission',4,'change_permission'),(15,'Can delete permission',4,'delete_permission'),(16,'Can view permission',4,'view_permission'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add result',7,'add_result'),(26,'Can change result',7,'change_result'),(27,'Can delete result',7,'delete_result'),(28,'Can view result',7,'view_result'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add team',9,'add_team'),(34,'Can change team',9,'change_team'),(35,'Can delete team',9,'delete_team'),(36,'Can view team',9,'view_team'),(37,'Can add competition',10,'add_competition'),(38,'Can change competition',10,'change_competition'),(39,'Can delete competition',10,'delete_competition'),(40,'Can view competition',10,'view_competition'),(41,'Can add task result',11,'add_taskresult'),(42,'Can change task result',11,'change_taskresult'),(43,'Can delete task result',11,'delete_taskresult'),(44,'Can view task result',11,'view_taskresult');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_celery_results_taskresult`
--

DROP TABLE IF EXISTS `django_celery_results_taskresult`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_celery_results_taskresult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL,
  `content_type` varchar(128) NOT NULL,
  `content_encoding` varchar(64) NOT NULL,
  `result` longtext,
  `date_done` datetime(6) NOT NULL,
  `traceback` longtext,
  `hidden` tinyint(1) NOT NULL,
  `meta` longtext,
  `task_args` longtext,
  `task_kwargs` longtext,
  `task_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `django_celery_results_taskresult_hidden_cd77412f` (`hidden`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_celery_results_taskresult`
--

LOCK TABLES `django_celery_results_taskresult` WRITE;
/*!40000 ALTER TABLE `django_celery_results_taskresult` DISABLE KEYS */;
INSERT INTO `django_celery_results_taskresult` VALUES (1,'77fb9953-938f-4015-9b4c-bb64dbf2f12b','SUCCESS','application/json','utf-8','16','2019-04-09 03:07:34.557334',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.mul'),(2,'c23dda1a-d0af-451f-b59a-fa7aaa26503b','SUCCESS','application/json','utf-8','8','2019-04-09 03:07:34.558082',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.add'),(3,'9afe83d7-7134-46d8-9638-f0a490f1af71','FAILURE','application/json','utf-8','{\"exc_module\": \"celery.exceptions\", \"exc_message\": [\"RSCompeteAPI.tasks.wtf\"], \"exc_type\": \"NotRegistered\"}','2019-04-09 06:29:12.597272',NULL,0,'{\"children\": []}',NULL,NULL,NULL),(4,'c6745202-c5e7-49f7-8076-43cbff94d684','SUCCESS','application/json','utf-8','8','2019-04-09 06:29:12.598574',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.add'),(5,'ade09881-1c85-4e86-935c-e58d6e7650e1','SUCCESS','application/json','utf-8','16','2019-04-09 06:29:12.661248',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.mul'),(6,'6dd110e2-31a2-4b97-8549-6c6ae3dc73b3','SUCCESS','application/json','utf-8','\"abc\"','2019-04-09 06:30:45.042758',NULL,0,'{\"children\": []}','[\'abc\']','{}','RSCompeteAPI.tasks.wtf'),(7,'84e7f269-a240-4847-b583-441b9cead6f0','SUCCESS','application/json','utf-8','8','2019-04-09 06:30:45.042908',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.add'),(8,'77b16efe-fd36-4c6b-afb5-607f96868024','SUCCESS','application/json','utf-8','16','2019-04-09 06:30:45.043538',NULL,0,'{\"children\": []}','[4, 4]','{}','RSCompeteAPI.tasks.mul'),(9,'c9f6c8e7-5662-453a-8fc8-61ffcd627abb','SUCCESS','application/json','utf-8','[0, \"success\"]','2019-04-24 08:20:17.424084',NULL,0,'{\"children\": []}','[\'../results/1/29/1556094016929\', \'/media/xuan/新加卷/code/NSFC接口/NSFC_contest/scene_classification_gt\']','{}','RSCompeteAPI.scene_classification_eval.get_score'),(10,'6e525866-7e12-42d3-b04e-3e4669faebcc','SUCCESS','application/json','utf-8','[0, \"success\"]','2019-04-24 08:38:34.689375',NULL,0,'{\"children\": []}','[\'../results/1/29/1556095114206\', \'/media/xuan/新加卷/code/NSFC接口/NSFC_contest/scene_classification_gt\']','{}','RSCompeteAPI.scene_classification_eval.get_score'),(11,'0e6ddb4c-924d-4432-b780-27dfc7f67170','SUCCESS','application/json','utf-8','null','2019-04-24 08:52:38.713116',NULL,0,'{\"children\": []}','[\'../results/1/29/1556095958216\', \'/media/xuan/新加卷/code/NSFC接口/NSFC_contest/scene_classification_gt\', 37]','{}','RSCompeteAPI.tasks.scene_classification'),(12,'8091422d-72b1-4519-b37d-13b00f0e7aac','SUCCESS','application/json','utf-8','null','2019-04-27 07:05:10.369412',NULL,0,'{\"children\": []}','[\'../results/1/29/1556348709382\', \'/media/xuan/新加卷/code/NSFC接口/NSFC_contest/scene_classification_gt\', 38]','{}','RSCompeteAPI.tasks.scene_classification');
/*!40000 ALTER TABLE `django_celery_results_taskresult` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(4,'auth','permission'),(2,'auth','user'),(5,'contenttypes','contenttype'),(11,'django_celery_results','taskresult'),(10,'RSCompeteAPI','competition'),(7,'RSCompeteAPI','result'),(9,'RSCompeteAPI','team'),(8,'RSCompeteAPI','user'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'RSCompeteAPI','0001_initial','2019-04-05 07:05:09.794598'),(2,'contenttypes','0001_initial','2019-04-05 07:05:10.246448'),(3,'auth','0001_initial','2019-04-05 07:05:17.435473'),(4,'admin','0001_initial','2019-04-05 07:05:19.287181'),(5,'admin','0002_logentry_remove_auto_add','2019-04-05 07:05:19.337549'),(6,'admin','0003_logentry_add_action_flag_choices','2019-04-05 07:05:19.413620'),(7,'contenttypes','0002_remove_content_type_name','2019-04-05 07:05:20.273235'),(8,'auth','0002_alter_permission_name_max_length','2019-04-05 07:05:20.802376'),(9,'auth','0003_alter_user_email_max_length','2019-04-05 07:05:21.413396'),(10,'auth','0004_alter_user_username_opts','2019-04-05 07:05:21.445108'),(11,'auth','0005_alter_user_last_login_null','2019-04-05 07:05:21.863270'),(12,'auth','0006_require_contenttypes_0002','2019-04-05 07:05:21.930999'),(13,'auth','0007_alter_validators_add_error_messages','2019-04-05 07:05:21.961940'),(14,'auth','0008_alter_user_username_max_length','2019-04-05 07:05:22.660330'),(15,'auth','0009_alter_user_last_name_max_length','2019-04-05 07:05:23.219073'),(16,'sessions','0001_initial','2019-04-05 07:05:23.847447'),(17,'RSCompeteAPI','0002_auto_20190408_1107','2019-04-08 11:07:34.281754'),(18,'RSCompeteAPI','0003_auto_20190408_1114','2019-04-08 11:14:41.448665'),(19,'django_celery_results','0001_initial','2019-04-09 02:27:35.435635'),(20,'django_celery_results','0002_add_task_name_args_kwargs','2019-04-09 02:27:37.031968'),(21,'django_celery_results','0003_auto_20181106_1101','2019-04-09 02:27:37.098228'),(22,'RSCompeteAPI','0004_result_root_dir','2019-04-24 08:24:24.330970'),(23,'RSCompeteAPI','0005_auto_20190513_0239','2019-05-13 02:40:16.657949'),(24,'RSCompeteAPI','0006_auto_20190513_0249','2019-05-13 02:50:01.509809');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('bj5dowb7vamm9zkvii180nryf436jgzx','YzFmNTBlNTA2ZWFiYTRhYzM4MGM2OTZhN2Q4MGQ2NjA0ZTZmMzMwMzp7InVzZXIiOnsibmFtZSI6Inh4IiwicGFzc3dvcmQiOiI2NTQiLCJjb3VudHJ5IjoiY2hpbmEiLCJwcm92aW5jZSI6IjUiLCJjaXR5IjoiYmVpamluZyIsIndvcmtfaWQiOjEsIndvcmtfcGxhY2VfdG9wIjoiIiwid29ya19wbGFjZV9zZWNvbmQiOiIiLCJ3b3JrX3BsYWNlX3RoaXJkIjoiIiwicGhvbmVfbnVtYmVyIjoiMTIzNDU2Nzg4MTEiLCJJRF9jYXJkIjoiMTIzNDU2Nzg5OTg3NjU0MzIyIiwiZW1haWwiOiJhQGEuY25jIiwiaXNfY2FwdGFpbiI6dHJ1ZSwidGVhbV9pZCI6MjksImNvbXBldGl0aW9uX2lkIjoxfX0=','2019-05-27 13:49:13.079750'),('yu2r3l9xtfqulhdjmochs7ue84svweqx','MzM1NzQyYmI3NTVmZDU5MTkzYjhiNjJlZmMzNGIyM2ZjYTJiNDYzMjp7InVzZXIiOnsibmFtZSI6Inh4IiwicGFzc3dvcmQiOiI2NTQiLCJjb3VudHJ5IjoiY2hpbmEiLCJwcm92aW5jZSI6IjUiLCJjaXR5IjoiYmVpamluZyIsIndvcmtfaWQiOjEsIndvcmtfcGxhY2UiOiJhc2FhIiwicGhvbmVfbnVtYmVyIjoiMTIzNDU2Nzg4MTEiLCJJRF9jYXJkIjoiMTIzNDU2Nzg5OTg3NjU0MzIyIiwiZW1haWwiOiJhQGEuY25jIiwiaXNfY2FwdGFpbiI6dHJ1ZSwidGVhbV9pZCI6MjksImNvbXBldGl0aW9uX2lkIjoxfX0=','2019-05-11 07:32:04.935004');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-05-17 11:20:25
