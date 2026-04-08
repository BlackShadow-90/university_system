-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: university_system
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcements` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title_en` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_zh` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `published_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `is_pinned` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `attachment` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `view_count` int unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `published_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `announcements_published_by_id_0aff3b49_fk_users_id` (`published_by_id`),
  CONSTRAINT `announcements_published_by_id_0aff3b49_fk_users_id` FOREIGN KEY (`published_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `announcements_chk_1` CHECK ((`view_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES (1,'Welcome to Fall 2024 Semester','欢迎来到2024年秋季学期','Welcome all students to the new semester. Please check your course schedules.','欢迎所有学生来到新学期。请查看您的课程表。','','','normal','all',NULL,NULL,0,1,'',0,'2026-03-31 23:32:08.159583','2026-04-08 15:30:27.884159',NULL),(2,'Midterm Examination Schedule','期中考试安排','Midterm exams will be held from October 15-20. Please prepare accordingly.','期中考试将于10月15日至20日举行。请做好准备。','','','high','all',NULL,NULL,0,1,'',0,'2026-03-31 23:32:08.164893','2026-04-08 15:30:27.879805',NULL),(3,'Holiday Notice - National Day','假期通知 - 国庆节','The university will be closed from October 1-7 for National Day holiday.','大学将在10月1日至7日国庆节放假。','','','high','all',NULL,NULL,0,1,'',0,'2026-03-31 23:32:08.168530','2026-04-08 15:30:27.874134',NULL),(4,'Library Hours Extended','图书馆延长开放时间','Library will now be open until 11 PM during exam weeks.','考试周期间图书馆将开放至晚上11点。','','','normal','all',NULL,NULL,0,1,'',0,'2026-03-31 23:32:08.172859','2026-04-08 15:30:27.871134',NULL),(5,'COVID-19 Safety Guidelines','COVID-19 安全指南','Please follow all safety guidelines and wear masks in crowded areas.','请遵守所有安全指南，在拥挤区域佩戴口罩。','','','urgent','all',NULL,NULL,0,1,'',0,'2026-03-31 23:32:08.177442','2026-04-08 15:30:27.863217',NULL);
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_components`
--

DROP TABLE IF EXISTS `assessment_components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_components` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `assessment_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `weight_percentage` decimal(5,2) NOT NULL,
  `max_score` decimal(6,2) NOT NULL,
  `due_date` date DEFAULT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_published` tinyint(1) NOT NULL,
  `order` smallint unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `course_offering_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assessment_component_course_offering_id_3fc3ed1f_fk_course_of` (`course_offering_id`),
  CONSTRAINT `assessment_component_course_offering_id_3fc3ed1f_fk_course_of` FOREIGN KEY (`course_offering_id`) REFERENCES `course_offerings` (`id`),
  CONSTRAINT `assessment_components_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_components`
--

LOCK TABLES `assessment_components` WRITE;
/*!40000 ALTER TABLE `assessment_components` DISABLE KEYS */;
INSERT INTO `assessment_components` VALUES (1,'Attendance','attendance',10.00,100.00,NULL,'',0,1,'2026-04-02 05:42:08.405134','2026-04-02 05:42:08.405166',29),(2,'Assignment 1','assignment',15.00,100.00,NULL,'',0,2,'2026-04-02 05:42:08.408778','2026-04-02 05:42:08.408833',29),(3,'Midterm Exam','midterm',25.00,100.00,NULL,'',0,3,'2026-04-02 05:42:08.411990','2026-04-02 05:42:08.412028',29),(4,'Assignment 2','assignment',15.00,100.00,NULL,'',0,4,'2026-04-02 05:42:08.414789','2026-04-02 05:42:08.414825',29),(5,'Final Project','project',15.00,100.00,NULL,'',0,5,'2026-04-02 05:42:08.417996','2026-04-02 05:42:08.418037',29),(6,'Final Exam','final',20.00,100.00,NULL,'',0,6,'2026-04-02 05:42:08.423522','2026-04-02 05:42:08.423549',29);
/*!40000 ALTER TABLE `assessment_components` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_scores`
--

DROP TABLE IF EXISTS `assessment_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_scores` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `score` decimal(6,2) DEFAULT NULL,
  `percentage` decimal(5,2) DEFAULT NULL,
  `remarks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entered_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assessment_component_id` bigint NOT NULL,
  `enrollment_id` bigint NOT NULL,
  `entered_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `assessment_scores_enrollment_id_assessment_ec1cc91d_uniq` (`enrollment_id`,`assessment_component_id`),
  KEY `assessment_scores_assessment_component_1c3740fe_fk_assessmen` (`assessment_component_id`),
  KEY `assessment_scores_entered_by_id_da5f17cb_fk_users_id` (`entered_by_id`),
  CONSTRAINT `assessment_scores_assessment_component_1c3740fe_fk_assessmen` FOREIGN KEY (`assessment_component_id`) REFERENCES `assessment_components` (`id`),
  CONSTRAINT `assessment_scores_enrollment_id_2230dc03_fk_enrollments_id` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`),
  CONSTRAINT `assessment_scores_entered_by_id_da5f17cb_fk_users_id` FOREIGN KEY (`entered_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_scores`
--

LOCK TABLES `assessment_scores` WRITE;
/*!40000 ALTER TABLE `assessment_scores` DISABLE KEYS */;
INSERT INTO `assessment_scores` VALUES (1,70.00,90.00,'','submitted','2026-04-02 06:35:09.340659','2026-04-06 14:38:12.133069',3,85,135),(2,80.00,60.00,'','submitted','2026-04-02 20:38:14.558524','2026-04-06 14:38:30.609874',5,85,135),(3,70.00,50.00,'','submitted','2026-04-06 14:18:00.689517','2026-04-06 14:26:58.485066',6,90,135),(4,50.00,60.00,'','submitted','2026-04-06 14:18:00.724807','2026-04-06 14:26:58.517963',6,89,135),(5,90.00,80.00,'','submitted','2026-04-06 14:18:00.753895','2026-04-06 14:26:58.550514',6,88,135),(6,60.00,70.00,'','submitted','2026-04-06 14:18:00.782902','2026-04-06 14:26:58.581612',6,87,135),(7,80.00,80.00,'','submitted','2026-04-06 14:18:00.807406','2026-04-06 14:26:58.610920',6,86,135),(8,86.00,90.00,'','submitted','2026-04-06 14:18:00.832084','2026-04-06 14:38:40.081843',6,85,135),(9,80.00,80.00,'','submitted','2026-04-06 14:37:16.868815','2026-04-06 14:37:16.868841',1,85,135),(10,60.00,60.00,'','submitted','2026-04-06 14:37:59.632881','2026-04-06 14:37:59.632906',2,85,135),(11,70.00,70.00,'','submitted','2026-04-06 14:38:22.497313','2026-04-06 14:38:22.497337',4,85,135);
/*!40000 ALTER TABLE `assessment_scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_records`
--

DROP TABLE IF EXISTS `attendance_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attendance_date` date NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `recorded_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `enrollment_id` bigint NOT NULL,
  `recorded_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_records_enrollment_id_attendance_date_6a7bfa22_uniq` (`enrollment_id`,`attendance_date`),
  KEY `attendance_records_recorded_by_id_5754c2dd_fk_users_id` (`recorded_by_id`),
  CONSTRAINT `attendance_records_enrollment_id_3c51c395_fk_enrollments_id` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`),
  CONSTRAINT `attendance_records_recorded_by_id_5754c2dd_fk_users_id` FOREIGN KEY (`recorded_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_records`
--

LOCK TABLES `attendance_records` WRITE;
/*!40000 ALTER TABLE `attendance_records` DISABLE KEYS */;
INSERT INTO `attendance_records` VALUES (29,'2024-10-01','present','','2026-03-31 23:32:07.965688','2026-03-31 23:32:07.965718',126,7),(30,'2024-10-08','present','','2026-03-31 23:32:07.973048','2026-03-31 23:32:07.973079',126,7),(31,'2024-10-15','present','','2026-03-31 23:32:07.978705','2026-03-31 23:32:07.978737',126,7),(32,'2024-10-22','present','','2026-03-31 23:32:07.983693','2026-03-31 23:32:07.983723',126,7),(33,'2024-10-01','present','','2026-03-31 23:32:07.988792','2026-03-31 23:32:07.988823',125,7),(34,'2024-10-08','present','','2026-03-31 23:32:07.996687','2026-03-31 23:32:07.996725',125,7),(35,'2024-10-15','present','','2026-03-31 23:32:08.001436','2026-03-31 23:32:08.001460',125,7),(36,'2024-10-22','present','','2026-03-31 23:32:08.007194','2026-03-31 23:32:08.007226',125,7),(37,'2024-10-01','present','','2026-03-31 23:32:08.012860','2026-03-31 23:32:08.012892',124,7),(38,'2024-10-08','present','','2026-03-31 23:32:08.019549','2026-03-31 23:32:08.019595',124,7),(39,'2024-10-15','present','','2026-03-31 23:32:08.025361','2026-03-31 23:32:08.025390',124,7),(40,'2024-10-22','present','','2026-03-31 23:32:08.030275','2026-03-31 23:32:08.030311',124,7),(41,'2024-10-01','present','','2026-03-31 23:32:08.035771','2026-03-31 23:32:08.035815',123,7),(42,'2024-10-08','present','','2026-03-31 23:32:08.043831','2026-03-31 23:32:08.043860',123,7),(43,'2024-10-15','present','','2026-03-31 23:32:08.048822','2026-03-31 23:32:08.048854',123,7),(44,'2024-10-22','present','','2026-03-31 23:32:08.055898','2026-03-31 23:32:08.055954',123,7),(45,'2024-10-01','present','','2026-03-31 23:32:08.062397','2026-03-31 23:32:08.062426',122,7),(46,'2024-10-08','present','','2026-03-31 23:32:08.069335','2026-03-31 23:32:08.069365',122,7),(47,'2024-10-15','present','','2026-03-31 23:32:08.075654','2026-03-31 23:32:08.075683',122,7),(48,'2024-10-22','present','','2026-03-31 23:32:08.080693','2026-03-31 23:32:08.080722',122,7),(49,'2024-10-01','present','','2026-03-31 23:32:08.087450','2026-03-31 23:32:08.087519',121,7),(50,'2024-10-08','present','','2026-03-31 23:32:08.094903','2026-03-31 23:32:08.094936',121,7),(51,'2024-10-15','present','','2026-03-31 23:32:08.099984','2026-03-31 23:32:08.100013',121,7),(52,'2024-10-22','present','','2026-03-31 23:32:08.104701','2026-03-31 23:32:08.104736',121,7),(53,'2024-10-01','present','','2026-03-31 23:32:08.109402','2026-03-31 23:32:08.109430',120,7),(54,'2024-10-08','present','','2026-03-31 23:32:08.116211','2026-03-31 23:32:08.116236',120,7),(55,'2024-10-15','present','','2026-03-31 23:32:08.120426','2026-03-31 23:32:08.120451',120,7),(56,'2024-10-22','present','','2026-03-31 23:32:08.126134','2026-03-31 23:32:08.126165',120,7),(57,'2026-04-02','present','','2026-04-02 05:32:39.757797','2026-04-02 20:38:40.366854',90,135),(58,'2026-04-02','present','','2026-04-02 05:32:39.764992','2026-04-02 20:38:40.374085',89,135),(59,'2026-04-02','present','','2026-04-02 05:32:39.770279','2026-04-02 20:38:40.385916',88,135),(60,'2026-04-02','present','','2026-04-02 05:32:39.775183','2026-04-02 20:38:40.395140',87,135),(61,'2026-04-02','present','','2026-04-02 05:32:39.782668','2026-04-02 20:38:40.406074',86,135),(62,'2026-04-02','absent','','2026-04-02 05:32:39.788572','2026-04-02 20:38:40.416232',85,135),(63,'2026-04-08','present','','2026-04-08 10:30:29.207675','2026-04-08 10:30:29.207707',90,135),(64,'2026-04-08','present','','2026-04-08 10:30:29.259460','2026-04-08 10:30:29.259489',89,135),(65,'2026-04-08','present','','2026-04-08 10:30:29.308218','2026-04-08 10:30:29.308237',88,135),(66,'2026-04-08','present','','2026-04-08 10:30:29.351114','2026-04-08 10:30:29.351136',87,135),(67,'2026-04-08','present','','2026-04-08 10:30:29.392457','2026-04-08 10:30:29.392480',86,135),(68,'2026-04-08','present','','2026-04-08 10:30:29.439250','2026-04-08 10:30:29.439272',85,135);
/*!40000 ALTER TABLE `attendance_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `module` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `before_data` json NOT NULL,
  `after_data` json NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_logs_user_id_6193b2_idx` (`user_id`,`created_at` DESC),
  KEY `audit_logs_entity__d4c2e5_idx` (`entity_type`,`entity_id`),
  KEY `audit_logs_action_bcaa71_idx` (`action`,`created_at` DESC),
  CONSTRAINT `audit_logs_user_id_752b0e2b_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 07:53:06.740207',4),(2,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 07:53:18.416361',7),(3,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 09:10:08.115131',7),(4,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 09:24:20.527148',4),(5,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 09:24:48.384593',7),(6,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 09:24:52.150604',7),(7,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:03:36.937817',4),(8,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:05:58.455865',4),(9,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:15:09.305110',4),(10,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:15:34.243354',7),(11,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:16:49.310345',4),(12,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:19:02.883067',7),(13,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:19:55.835348',4),(14,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 10:36:30.199137',NULL),(15,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:37:33.401943',7),(16,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:40:32.329391',NULL),(17,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:41:06.998142',7),(18,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:52:03.454467',4),(19,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:54:11.861454',NULL),(20,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:58:01.032177',NULL),(21,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 11:59:05.353676',7),(22,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 12:05:19.460647',NULL),(23,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 12:05:41.134847',7),(24,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-30 12:06:20.835556',NULL),(25,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-31 22:26:15.461837',NULL),(26,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-31 22:26:33.944221',7),(27,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-31 22:28:49.574983',4),(28,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-31 22:49:28.192333',4),(29,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-03-31 22:49:51.141670',7),(30,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 08:19:01.775220',4),(31,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 08:20:09.256311',NULL),(32,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 08:20:31.601786',7),(33,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 11:59:49.082839',NULL),(34,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 12:00:18.721157',4),(35,'login','Authentication','User','6','Dr. John Smith','{}','{}','User john@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 12:10:47.700763',NULL),(36,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-01 12:20:38.294786',7),(37,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 04:53:02.079231',7),(38,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 05:01:00.749053',135),(39,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 05:21:43.030124',7),(40,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 05:22:32.393388',135),(41,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 06:35:52.018154',7),(42,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 14:51:24.974229',135),(43,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 14:52:16.150277',4),(44,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 15:10:07.039993',135),(45,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 15:43:12.652812',4),(46,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 20:29:38.848384',135),(47,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 20:41:20.047420',4),(48,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 20:43:55.139138',7),(49,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-02 20:45:12.086866',4),(50,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-05 12:04:40.036595',7),(51,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-05 12:04:41.631448',7),(52,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-05 12:05:44.075346',4),(53,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 12:01:54.808735',7),(54,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 12:02:38.251310',135),(55,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 12:03:42.225282',4),(56,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 13:23:59.624722',7),(57,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 14:14:36.433244',135),(58,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-06 14:39:18.277338',4),(59,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 05:14:00.065703',7),(60,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 05:17:39.989794',135),(61,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 05:23:30.917633',4),(62,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 08:07:46.342730',4),(63,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:24:43.064471',7),(64,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:26:35.190745',4),(65,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:30:07.006150',135),(66,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:31:18.826217',4),(67,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:31:49.667711',7),(68,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:32:26.249435',4),(69,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:33:44.195450',135),(70,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:40:16.052724',4),(71,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 10:44:42.468637',7),(72,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 11:35:10.557468',4),(73,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 11:47:16.606245',135),(74,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 12:17:58.620365',7),(75,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 14:33:25.439781',7),(76,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 14:58:35.283959',4),(77,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 15:17:37.526959',7),(78,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:01:00.906317',4),(79,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:04:39.994112',135),(80,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:06:55.427701',7),(81,'login','Authentication','User','4','omer','{}','{}','User abbasal@gmail.com logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:42:57.388438',4),(82,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:57:42.185155',7),(83,'login','Authentication','User','135','John Smith','{}','{}','User teacher1@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 16:58:05.318721',135),(84,'login','Authentication','User','7','ABBAS','{}','{}','User admin@university.edu logged in','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0','2026-04-08 17:16:47.315727',7);
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=165 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Permission',6,'add_permission'),(22,'Can change Permission',6,'change_permission'),(23,'Can delete Permission',6,'delete_permission'),(24,'Can view Permission',6,'view_permission'),(25,'Can add Role',7,'add_role'),(26,'Can change Role',7,'change_role'),(27,'Can delete Role',7,'delete_role'),(28,'Can view Role',7,'view_role'),(29,'Can add User',9,'add_user'),(30,'Can change User',9,'change_user'),(31,'Can delete User',9,'delete_user'),(32,'Can view User',9,'view_user'),(33,'Can add Role Permission',8,'add_rolepermission'),(34,'Can change Role Permission',8,'change_rolepermission'),(35,'Can delete Role Permission',8,'delete_rolepermission'),(36,'Can view Role Permission',8,'view_rolepermission'),(37,'Can add Department',10,'add_department'),(38,'Can change Department',10,'change_department'),(39,'Can delete Department',10,'delete_department'),(40,'Can view Department',10,'view_department'),(41,'Can add Program',12,'add_program'),(42,'Can change Program',12,'change_program'),(43,'Can delete Program',12,'delete_program'),(44,'Can view Program',12,'view_program'),(45,'Can add Curriculum Course',11,'add_curriculumcourse'),(46,'Can change Curriculum Course',11,'change_curriculumcourse'),(47,'Can delete Curriculum Course',11,'delete_curriculumcourse'),(48,'Can view Curriculum Course',11,'view_curriculumcourse'),(49,'Can add Semester',13,'add_semester'),(50,'Can change Semester',13,'change_semester'),(51,'Can delete Semester',13,'delete_semester'),(52,'Can view Semester',13,'view_semester'),(53,'Can add Student',14,'add_student'),(54,'Can change Student',14,'change_student'),(55,'Can delete Student',14,'delete_student'),(56,'Can view Student',14,'view_student'),(57,'Can add Teacher',15,'add_teacher'),(58,'Can change Teacher',15,'change_teacher'),(59,'Can delete Teacher',15,'delete_teacher'),(60,'Can view Teacher',15,'view_teacher'),(61,'Can add Course',16,'add_course'),(62,'Can change Course',16,'change_course'),(63,'Can delete Course',16,'delete_course'),(64,'Can view Course',16,'view_course'),(65,'Can add Course Offering',17,'add_courseoffering'),(66,'Can change Course Offering',17,'change_courseoffering'),(67,'Can delete Course Offering',17,'delete_courseoffering'),(68,'Can view Course Offering',17,'view_courseoffering'),(69,'Can add Enrollment',18,'add_enrollment'),(70,'Can change Enrollment',18,'change_enrollment'),(71,'Can delete Enrollment',18,'delete_enrollment'),(72,'Can view Enrollment',18,'view_enrollment'),(73,'Can add Attendance Record',19,'add_attendancerecord'),(74,'Can change Attendance Record',19,'change_attendancerecord'),(75,'Can delete Attendance Record',19,'delete_attendancerecord'),(76,'Can view Attendance Record',19,'view_attendancerecord'),(77,'Can add Assessment Component',20,'add_assessmentcomponent'),(78,'Can change Assessment Component',20,'change_assessmentcomponent'),(79,'Can delete Assessment Component',20,'delete_assessmentcomponent'),(80,'Can view Assessment Component',20,'view_assessmentcomponent'),(81,'Can add Assessment Score',21,'add_assessmentscore'),(82,'Can change Assessment Score',21,'change_assessmentscore'),(83,'Can delete Assessment Score',21,'delete_assessmentscore'),(84,'Can view Assessment Score',21,'view_assessmentscore'),(85,'Can add Grade Scheme',25,'add_gradescheme'),(86,'Can change Grade Scheme',25,'change_gradescheme'),(87,'Can delete Grade Scheme',25,'delete_gradescheme'),(88,'Can view Grade Scheme',25,'view_gradescheme'),(89,'Can add CGPA Record',22,'add_cgparecord'),(90,'Can change CGPA Record',22,'change_cgparecord'),(91,'Can delete CGPA Record',22,'delete_cgparecord'),(92,'Can view CGPA Record',22,'view_cgparecord'),(93,'Can add Final Result',23,'add_finalresult'),(94,'Can change Final Result',23,'change_finalresult'),(95,'Can delete Final Result',23,'delete_finalresult'),(96,'Can view Final Result',23,'view_finalresult'),(97,'Can add Grade Mapping',24,'add_grademapping'),(98,'Can change Grade Mapping',24,'change_grademapping'),(99,'Can delete Grade Mapping',24,'delete_grademapping'),(100,'Can view Grade Mapping',24,'view_grademapping'),(101,'Can add Semester Summary',26,'add_semestersummary'),(102,'Can change Semester Summary',26,'change_semestersummary'),(103,'Can delete Semester Summary',26,'delete_semestersummary'),(104,'Can view Semester Summary',26,'view_semestersummary'),(105,'Can add Early Warning Rule',28,'add_earlywarningrule'),(106,'Can change Early Warning Rule',28,'change_earlywarningrule'),(107,'Can delete Early Warning Rule',28,'delete_earlywarningrule'),(108,'Can view Early Warning Rule',28,'view_earlywarningrule'),(109,'Can add Early Warning Result',27,'add_earlywarningresult'),(110,'Can change Early Warning Result',27,'change_earlywarningresult'),(111,'Can delete Early Warning Result',27,'delete_earlywarningresult'),(112,'Can view Early Warning Result',27,'view_earlywarningresult'),(113,'Can add Announcement',29,'add_announcement'),(114,'Can change Announcement',29,'change_announcement'),(115,'Can delete Announcement',29,'delete_announcement'),(116,'Can view Announcement',29,'view_announcement'),(117,'Can add Notification',30,'add_notification'),(118,'Can change Notification',30,'change_notification'),(119,'Can delete Notification',30,'delete_notification'),(120,'Can view Notification',30,'view_notification'),(121,'Can add Audit Log',31,'add_auditlog'),(122,'Can change Audit Log',31,'change_auditlog'),(123,'Can delete Audit Log',31,'delete_auditlog'),(124,'Can view Audit Log',31,'view_auditlog'),(125,'Can add Grade Policy',32,'add_gradepolicy'),(126,'Can change Grade Policy',32,'change_gradepolicy'),(127,'Can delete Grade Policy',32,'delete_gradepolicy'),(128,'Can view Grade Policy',32,'view_gradepolicy'),(129,'Can add System Setting',33,'add_systemsetting'),(130,'Can change System Setting',33,'change_systemsetting'),(131,'Can delete System Setting',33,'delete_systemsetting'),(132,'Can view System Setting',33,'view_systemsetting'),(133,'Can add Warning Escalation Rule',35,'add_warningescalationrule'),(134,'Can change Warning Escalation Rule',35,'change_warningescalationrule'),(135,'Can delete Warning Escalation Rule',35,'delete_warningescalationrule'),(136,'Can view Warning Escalation Rule',35,'view_warningescalationrule'),(137,'Can add Parent/Guardian Notification',34,'add_parentguardiannotification'),(138,'Can change Parent/Guardian Notification',34,'change_parentguardiannotification'),(139,'Can delete Parent/Guardian Notification',34,'delete_parentguardiannotification'),(140,'Can view Parent/Guardian Notification',34,'view_parentguardiannotification'),(141,'Can add Warning Resolution',39,'add_warningresolution'),(142,'Can change Warning Resolution',39,'change_warningresolution'),(143,'Can delete Warning Resolution',39,'delete_warningresolution'),(144,'Can view Warning Resolution',39,'view_warningresolution'),(145,'Can add Warning History',37,'add_warninghistory'),(146,'Can change Warning History',37,'change_warninghistory'),(147,'Can delete Warning History',37,'delete_warninghistory'),(148,'Can view Warning History',37,'view_warninghistory'),(149,'Can add Warning Intervention',38,'add_warningintervention'),(150,'Can change Warning Intervention',38,'change_warningintervention'),(151,'Can delete Warning Intervention',38,'delete_warningintervention'),(152,'Can view Warning Intervention',38,'view_warningintervention'),(153,'Can add Warning Evidence',36,'add_warningevidence'),(154,'Can change Warning Evidence',36,'change_warningevidence'),(155,'Can delete Warning Evidence',36,'delete_warningevidence'),(156,'Can view Warning Evidence',36,'view_warningevidence'),(157,'Can add system calculation log',40,'add_systemcalculationlog'),(158,'Can change system calculation log',40,'change_systemcalculationlog'),(159,'Can delete system calculation log',40,'delete_systemcalculationlog'),(160,'Can view system calculation log',40,'view_systemcalculationlog'),(161,'Can add Processing Status',41,'add_processingstatus'),(162,'Can change Processing Status',41,'change_processingstatus'),(163,'Can delete Processing Status',41,'delete_processingstatus'),(164,'Can view Processing Status',41,'view_processingstatus');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cgpa_records`
--

DROP TABLE IF EXISTS `cgpa_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cgpa_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cumulative_gpa` decimal(3,2) NOT NULL,
  `cumulative_credits_attempted` decimal(6,2) NOT NULL,
  `cumulative_credits_earned` decimal(6,2) NOT NULL,
  `total_quality_points` decimal(10,2) NOT NULL,
  `semesters_completed` smallint unsigned NOT NULL,
  `computed_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `cgpa_records_student_id_1af73eae_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `cgpa_records_chk_1` CHECK ((`semesters_completed` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cgpa_records`
--

LOCK TABLES `cgpa_records` WRITE;
/*!40000 ALTER TABLE `cgpa_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `cgpa_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_systemcalculationlog`
--

DROP TABLE IF EXISTS `core_systemcalculationlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_systemcalculationlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `details` json NOT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `triggered_by_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `duration_ms` int DEFAULT NULL,
  `course_offering_id` bigint DEFAULT NULL,
  `enrollment_id` bigint DEFAULT NULL,
  `semester_id` bigint DEFAULT NULL,
  `student_id` bigint DEFAULT NULL,
  `triggered_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_systemcalculati_course_offering_id_15511011_fk_course_of` (`course_offering_id`),
  KEY `core_systemcalculationlog_triggered_by_id_01e6db65_fk_users_id` (`triggered_by_id`),
  KEY `core_systemcalculationlog_action_type_e53bb1b4` (`action_type`),
  KEY `core_systemcalculationlog_status_08bb55c6` (`status`),
  KEY `core_systemcalculationlog_created_at_4e5c9c10` (`created_at`),
  KEY `core_system_student_f3be83_idx` (`student_id`,`action_type`,`created_at` DESC),
  KEY `core_system_enrollm_5461f5_idx` (`enrollment_id`,`action_type`,`created_at` DESC),
  KEY `core_system_action__b81310_idx` (`action_type`,`status`,`created_at` DESC),
  KEY `core_system_semeste_ec6623_idx` (`semester_id`,`action_type`,`created_at` DESC),
  CONSTRAINT `core_systemcalculati_course_offering_id_15511011_fk_course_of` FOREIGN KEY (`course_offering_id`) REFERENCES `course_offerings` (`id`),
  CONSTRAINT `core_systemcalculati_enrollment_id_fb3a515f_fk_enrollmen` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`),
  CONSTRAINT `core_systemcalculationlog_semester_id_f9473933_fk_semesters_id` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`),
  CONSTRAINT `core_systemcalculationlog_student_id_b59477da_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `core_systemcalculationlog_triggered_by_id_01e6db65_fk_users_id` FOREIGN KEY (`triggered_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_systemcalculationlog`
--

LOCK TABLES `core_systemcalculationlog` WRITE;
/*!40000 ALTER TABLE `core_systemcalculationlog` DISABLE KEYS */;
INSERT INTO `core_systemcalculationlog` VALUES (1,'mark_sync','failed','Unexpected error processing mark update for Eva Martinez','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.705568',9,29,90,1,70,NULL),(2,'mark_sync','failed','Unexpected error processing mark update for David Kim','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.740730',9,29,89,1,69,NULL),(3,'mark_sync','failed','Unexpected error processing mark update for Carol Liu','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.769559',8,29,88,1,68,NULL),(4,'mark_sync','failed','Unexpected error processing mark update for Bob Zhang','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.795545',5,29,87,1,67,NULL),(5,'mark_sync','failed','Unexpected error processing mark update for Alice Wang','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.820913',6,29,86,1,66,NULL),(6,'mark_sync','failed','Unexpected error processing mark update for omer','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:18:00.847985',7,29,85,1,2,NULL),(13,'mark_sync','failed','Unexpected error processing mark update for Eva Martinez','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.505348',12,29,90,1,70,NULL),(14,'mark_sync','failed','Unexpected error processing mark update for David Kim','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.536260',10,29,89,1,69,NULL),(15,'mark_sync','failed','Unexpected error processing mark update for Carol Liu','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.566969',10,29,88,1,68,NULL),(16,'mark_sync','failed','Unexpected error processing mark update for Bob Zhang','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.596675',8,29,87,1,67,NULL),(17,'mark_sync','failed','Unexpected error processing mark update for Alice Wang','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.628284',9,29,86,1,66,NULL),(18,'mark_sync','failed','Unexpected error processing mark update for omer','{\"error_type\": \"AttributeError\"}','\'AssessmentComponent\' object has no attribute \'component_type\'','','2026-04-06 14:26:58.657899',7,29,85,1,2,NULL),(25,'warning_recalc','success','Updated early warning for omer: orange','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 50.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 50.0, \"warning_level\": \"orange\", \"attendance_risk\": null}','','','2026-04-06 14:37:16.914968',30,NULL,85,1,2,NULL),(26,'mark_sync','success','Processed mark update for omer','{\"score\": \"80\", \"component\": \"Attendance\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Mark validated successfully\", \"Final result not ready - missing components\", \"GPA not updated - result not published\", \"Warning updated: orange\"], \"gpa_updated\": false, \"warning_updated\": true, \"final_result_updated\": false}}','','','2026-04-06 14:37:16.916484',46,29,85,1,2,NULL),(28,'warning_recalc','success','Updated early warning for omer: yellow','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 25.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 25.0, \"warning_level\": \"yellow\", \"attendance_risk\": null}','','','2026-04-06 14:37:59.675906',26,NULL,85,1,2,NULL),(29,'mark_sync','success','Processed mark update for omer','{\"score\": \"60\", \"component\": \"Assignment 1\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Mark validated successfully\", \"Final result not ready - missing components\", \"GPA not updated - result not published\", \"Warning updated: yellow\"], \"gpa_updated\": false, \"warning_updated\": true, \"final_result_updated\": false}}','','','2026-04-06 14:37:59.677402',42,29,85,1,2,NULL),(31,'warning_recalc','success','Updated early warning for omer: yellow','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 25.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 25.0, \"warning_level\": \"yellow\", \"attendance_risk\": null}','','','2026-04-06 14:38:12.176229',23,NULL,85,1,2,NULL),(32,'mark_sync','success','Processed mark update for omer','{\"score\": \"70\", \"component\": \"Midterm Exam\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Mark validated successfully\", \"Final result not ready - missing components\", \"GPA not updated - result not published\", \"Warning updated: yellow\"], \"gpa_updated\": false, \"warning_updated\": true, \"final_result_updated\": false}}','','','2026-04-06 14:38:12.177796',42,29,85,1,2,NULL),(35,'mark_sync','failed','Unexpected error processing mark update for omer','{\"error_type\": \"AttributeError\"}','\'GradeScale\' object has no attribute \'get_grade_for_percentage\'','','2026-04-06 14:38:22.542289',43,29,85,1,2,NULL),(38,'mark_sync','failed','Unexpected error processing mark update for omer','{\"error_type\": \"AttributeError\"}','\'GradeScale\' object has no attribute \'get_grade_for_percentage\'','','2026-04-06 14:38:30.649687',38,29,85,1,2,NULL),(41,'mark_sync','failed','Unexpected error processing mark update for omer','{\"error_type\": \"AttributeError\"}','\'GradeScale\' object has no attribute \'get_grade_for_percentage\'','','2026-04-06 14:38:40.125780',42,29,85,1,2,NULL),(43,'warning_recalc','failed','Failed to update early warning for Eva Martinez','{\"error_type\": \"FieldError\"}','Invalid field name(s) for model EarlyWarningResult: \'calculated_at\'.','','2026-04-08 10:30:29.246516',13,NULL,90,1,70,NULL),(44,'attendance_recalc','failed','Failed to process attendance update for Eva Martinez','{\"errors\": [\"Failed to update warning: Invalid field name(s) for model EarlyWarningResult: \'calculated_at\'.\"], \"status\": \"present\"}','Failed to update warning: Invalid field name(s) for model EarlyWarningResult: \'calculated_at\'.','','2026-04-08 10:30:29.248207',37,29,90,1,70,NULL),(45,'warning_recalc','success','Updated early warning for David Kim: red','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 100.0, \"warning_level\": \"red\", \"attendance_risk\": null}','','','2026-04-08 10:30:29.298395',20,NULL,89,1,69,NULL),(46,'attendance_recalc','success','Processed attendance update for David Kim','{\"date\": \"2026-04-08\", \"status\": \"present\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Attendance validated successfully\", \"Attendance updated: 100.0%\", \"Warning updated: red\"], \"warning_updated\": true, \"attendance_updated\": true}, \"attendance_percentage\": \"100.0\"}','','','2026-04-08 10:30:29.299379',38,29,89,1,69,NULL),(47,'warning_recalc','success','Updated early warning for Carol Liu: red','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 100.0, \"warning_level\": \"red\", \"attendance_risk\": null}','','','2026-04-08 10:30:29.340182',17,NULL,88,1,68,NULL),(48,'attendance_recalc','success','Processed attendance update for Carol Liu','{\"date\": \"2026-04-08\", \"status\": \"present\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Attendance validated successfully\", \"Attendance updated: 100.0%\", \"Warning updated: red\"], \"warning_updated\": true, \"attendance_updated\": true}, \"attendance_percentage\": \"100.0\"}','','','2026-04-08 10:30:29.341649',31,29,88,1,68,NULL),(49,'warning_recalc','success','Updated early warning for Bob Zhang: red','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 100.0, \"warning_level\": \"red\", \"attendance_risk\": null}','','','2026-04-08 10:30:29.381273',15,NULL,87,1,67,NULL),(50,'attendance_recalc','success','Processed attendance update for Bob Zhang','{\"date\": \"2026-04-08\", \"status\": \"present\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Attendance validated successfully\", \"Attendance updated: 100.0%\", \"Warning updated: red\"], \"warning_updated\": true, \"attendance_updated\": true}, \"attendance_percentage\": \"100.0\"}','','','2026-04-08 10:30:29.382483',28,29,87,1,67,NULL),(51,'warning_recalc','success','Updated early warning for Alice Wang: red','{\"created\": false, \"risk_factors\": [{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}], \"academic_risk\": 100.0, \"warning_level\": \"red\", \"attendance_risk\": null}','','','2026-04-08 10:30:29.428721',20,NULL,86,1,66,NULL),(52,'attendance_recalc','success','Processed attendance update for Alice Wang','{\"date\": \"2026-04-08\", \"status\": \"present\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Attendance validated successfully\", \"Attendance updated: 100.0%\", \"Warning updated: red\"], \"warning_updated\": true, \"attendance_updated\": true}, \"attendance_percentage\": \"100.0\"}','','','2026-04-08 10:30:29.430409',36,29,86,1,66,NULL),(53,'warning_recalc','success','Updated early warning for omer: red','{\"created\": false, \"risk_factors\": [{\"type\": \"attendance\", \"score\": 75.0, \"reason\": \"Attendance below threshold (50.0%)\"}], \"academic_risk\": null, \"warning_level\": \"red\", \"attendance_risk\": 75.0}','','','2026-04-08 10:30:29.468426',13,NULL,85,1,2,NULL),(54,'attendance_recalc','success','Processed attendance update for omer','{\"date\": \"2026-04-08\", \"status\": \"present\", \"pipeline_results\": {\"errors\": [], \"success\": true, \"messages\": [\"Attendance validated successfully\", \"Attendance updated: 50.0%\", \"Warning updated: red\"], \"warning_updated\": true, \"attendance_updated\": true}, \"attendance_percentage\": \"50.0\"}','','','2026-04-08 10:30:29.470078',28,29,85,1,2,NULL);
/*!40000 ALTER TABLE `core_systemcalculationlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_offerings`
--

DROP TABLE IF EXISTS `course_offerings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_offerings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `section_name` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `room` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `day_of_week` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` time(6) DEFAULT NULL,
  `end_time` time(6) DEFAULT NULL,
  `capacity` int unsigned NOT NULL,
  `enrolled_count` int unsigned NOT NULL,
  `waiting_count` int unsigned NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_grade_published` tinyint(1) NOT NULL,
  `grade_published_at` datetime(6) DEFAULT NULL,
  `syllabus` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `course_id` bigint NOT NULL,
  `semester_id` bigint NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_offerings_course_id_semester_id_se_895b6121_uniq` (`course_id`,`semester_id`,`section_name`),
  KEY `course_offerings_semester_id_5e4a54b4_fk_semesters_id` (`semester_id`),
  KEY `course_offerings_teacher_id_c8e08e18_fk_teachers_id` (`teacher_id`),
  CONSTRAINT `course_offerings_course_id_5cc69bb5_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `course_offerings_semester_id_5e4a54b4_fk_semesters_id` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`),
  CONSTRAINT `course_offerings_teacher_id_c8e08e18_fk_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `course_offerings_chk_1` CHECK ((`capacity` >= 0)),
  CONSTRAINT `course_offerings_chk_2` CHECK ((`enrolled_count` >= 0)),
  CONSTRAINT `course_offerings_chk_3` CHECK ((`waiting_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_offerings`
--

LOCK TABLES `course_offerings` WRITE;
/*!40000 ALTER TABLE `course_offerings` DISABLE KEYS */;
INSERT INTO `course_offerings` VALUES (29,'01','','',NULL,NULL,30,6,0,'open',0,NULL,'','','2026-03-31 23:32:07.657738','2026-03-31 23:32:07.657770',26,1,66),(30,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.665042','2026-03-31 23:32:07.665073',27,1,67),(31,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.685070','2026-03-31 23:32:07.685098',1,1,68),(32,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.693341','2026-03-31 23:32:07.693375',28,1,69),(33,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.702663','2026-03-31 23:32:07.702685',26,12,68),(34,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.707018','2026-03-31 23:32:07.707042',27,12,69),(35,'01','','',NULL,NULL,30,0,0,'open',0,NULL,'','','2026-03-31 23:32:07.710414','2026-03-31 23:32:07.710442',1,12,70);
/*!40000 ALTER TABLE `course_offerings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_en` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_zh` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_hours` decimal(3,1) NOT NULL,
  `lecture_hours` decimal(3,1) NOT NULL,
  `lab_hours` decimal(3,1) NOT NULL,
  `course_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `learning_outcomes_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `learning_outcomes_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `courses_department_id_3eedabe1_fk_departments_id` (`department_id`),
  CONSTRAINT `courses_department_id_3eedabe1_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'CS301','Data Science','数据科学',3.0,3.0,1.0,'theory_lab','This course introduces the fundamental concepts of data science, including data collection, cleaning, analysis, visualization, and machine learning basics. Students will work with real-world datasets using Python and popular data science libraries.','本课程介绍数据科学的基本概念，包括数据收集、清洗、分析、可视化和机器学习基础。学生将使用Python和流行的数据科学库处理真实世界的数据集。','1. Understand the data science lifecycle and key methodologies.\r\n2. Apply data cleaning and preprocessing techniques to raw datasets.\r\n3. Create meaningful data visualizations to communicate insights.\r\n4. Implement basic machine learning models for prediction tasks.\r\n5. Use Python libraries such as Pandas, NumPy, Matplotlib, and Scikit-learn.','1. 理解数据科学生命周期和关键方法。\r\n2. 对原始数据集应用数据清洗和预处理技术。\r\n3. 创建有意义的数据可视化以传达见解。\r\n4. 实现基本的机器学习模型进行预测任务。\r\n5. 使用Python库，如Pandas、NumPy、Matplotlib和Scikit-learn。','active','2026-03-27 21:54:34.206321','2026-03-28 09:19:53.682717',2),(26,'CS101','Introduction to Computer Science','计算机科学导论',3.0,3.0,0.0,'theory','','','','','active','2026-03-31 23:32:07.633954','2026-03-31 23:32:07.633995',2),(27,'CS201','Data Structures','数据结构',3.0,3.0,0.0,'theory','','','','','active','2026-03-31 23:32:07.639290','2026-03-31 23:32:07.639328',2),(28,'CS401','Database Systems','数据库系统',3.0,3.0,0.0,'theory','','','','','active','2026-03-31 23:32:07.644774','2026-03-31 23:32:07.644811',2);
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses_prerequisites`
--

DROP TABLE IF EXISTS `courses_prerequisites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses_prerequisites` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `from_course_id` bigint NOT NULL,
  `to_course_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `courses_prerequisites_from_course_id_to_course_id_cd11b10f_uniq` (`from_course_id`,`to_course_id`),
  KEY `courses_prerequisites_to_course_id_058d4a20_fk_courses_id` (`to_course_id`),
  CONSTRAINT `courses_prerequisites_from_course_id_254544cd_fk_courses_id` FOREIGN KEY (`from_course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `courses_prerequisites_to_course_id_058d4a20_fk_courses_id` FOREIGN KEY (`to_course_id`) REFERENCES `courses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses_prerequisites`
--

LOCK TABLES `courses_prerequisites` WRITE;
/*!40000 ALTER TABLE `courses_prerequisites` DISABLE KEYS */;
INSERT INTO `courses_prerequisites` VALUES (1,1,1);
/*!40000 ALTER TABLE `courses_prerequisites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `curriculum_courses`
--

DROP TABLE IF EXISTS `curriculum_courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `curriculum_courses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recommended_semester` smallint unsigned NOT NULL,
  `is_required` tinyint(1) NOT NULL,
  `course_nature` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `course_id` bigint NOT NULL,
  `program_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `curriculum_courses_program_id_course_id_74f619e2_uniq` (`program_id`,`course_id`),
  KEY `curriculum_courses_course_id_3a61989b_fk_courses_id` (`course_id`),
  CONSTRAINT `curriculum_courses_course_id_3a61989b_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `curriculum_courses_program_id_a1894435_fk_programs_id` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`),
  CONSTRAINT `curriculum_courses_chk_1` CHECK ((`recommended_semester` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `curriculum_courses`
--

LOCK TABLES `curriculum_courses` WRITE;
/*!40000 ALTER TABLE `curriculum_courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `curriculum_courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name_en` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_zh` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES (2,'Computer Science','计算机科学系','CS','Focuses on programming, algorithms, and software development.','专注于编程、算法和软件开发。','active','2026-03-28 09:08:59.018411','2026-03-28 09:08:59.018436'),(51,'Engineering','工程系','ENG','','','active','2026-03-31 23:31:28.023967','2026-03-31 23:31:28.023992'),(52,'Business','商学院','BUS','','','active','2026-03-31 23:31:28.027889','2026-03-31 23:31:28.027925'),(53,'Science','理学系','SCI','','','active','2026-03-31 23:31:28.032647','2026-03-31 23:31:28.032680'),(54,'Arts','人文学院','ART','','','active','2026-03-31 23:31:28.035728','2026-03-31 23:31:28.035759');
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','permission'),(7,'accounts','role'),(8,'accounts','rolepermission'),(9,'accounts','user'),(1,'admin','logentry'),(29,'announcements','announcement'),(20,'assessments','assessmentcomponent'),(21,'assessments','assessmentscore'),(19,'attendance','attendancerecord'),(31,'auditlogs','auditlog'),(2,'auth','group'),(3,'auth','permission'),(4,'contenttypes','contenttype'),(41,'core','processingstatus'),(40,'core','systemcalculationlog'),(16,'courses','course'),(17,'courses','courseoffering'),(10,'departments','department'),(18,'enrollments','enrollment'),(30,'notifications','notification'),(11,'programs','curriculumcourse'),(12,'programs','program'),(22,'results','cgparecord'),(23,'results','finalresult'),(24,'results','grademapping'),(25,'results','gradescheme'),(26,'results','semestersummary'),(13,'semesters','semester'),(5,'sessions','session'),(32,'settings_app','gradepolicy'),(33,'settings_app','systemsetting'),(14,'students','student'),(15,'teachers','teacher'),(27,'warnings','earlywarningresult'),(28,'warnings','earlywarningrule'),(34,'warnings','parentguardiannotification'),(35,'warnings','warningescalationrule'),(36,'warnings','warningevidence'),(37,'warnings','warninghistory'),(38,'warnings','warningintervention'),(39,'warnings','warningresolution');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-03-27 18:13:28.986796'),(2,'contenttypes','0002_remove_content_type_name','2026-03-27 18:13:29.102920'),(3,'auth','0001_initial','2026-03-27 18:13:29.417707'),(4,'auth','0002_alter_permission_name_max_length','2026-03-27 18:13:29.509030'),(5,'auth','0003_alter_user_email_max_length','2026-03-27 18:13:29.519217'),(6,'auth','0004_alter_user_username_opts','2026-03-27 18:13:29.527885'),(7,'auth','0005_alter_user_last_login_null','2026-03-27 18:13:29.535467'),(8,'auth','0006_require_contenttypes_0002','2026-03-27 18:13:29.538141'),(9,'auth','0007_alter_validators_add_error_messages','2026-03-27 18:13:29.549882'),(10,'auth','0008_alter_user_username_max_length','2026-03-27 18:13:29.559861'),(11,'auth','0009_alter_user_last_name_max_length','2026-03-27 18:13:29.569441'),(12,'auth','0010_alter_group_name_max_length','2026-03-27 18:13:29.611165'),(13,'auth','0011_update_proxy_permissions','2026-03-27 18:13:29.623854'),(14,'auth','0012_alter_user_first_name_max_length','2026-03-27 18:13:29.638718'),(15,'accounts','0001_initial','2026-03-27 18:13:30.400100'),(16,'admin','0001_initial','2026-03-27 18:13:30.603582'),(17,'admin','0002_logentry_remove_auto_add','2026-03-27 18:13:30.622605'),(18,'admin','0003_logentry_add_action_flag_choices','2026-03-27 18:13:30.639515'),(19,'announcements','0001_initial','2026-03-27 18:13:30.761454'),(20,'departments','0001_initial','2026-03-27 18:13:30.806402'),(21,'teachers','0001_initial','2026-03-27 18:13:31.037020'),(22,'semesters','0001_initial','2026-03-27 18:13:31.092878'),(23,'courses','0001_initial','2026-03-27 18:13:31.760144'),(24,'programs','0001_initial','2026-03-27 18:13:32.222777'),(25,'students','0001_initial','2026-03-27 18:13:32.787752'),(26,'enrollments','0001_initial','2026-03-27 18:13:33.036717'),(27,'assessments','0001_initial','2026-03-27 18:13:33.493528'),(28,'attendance','0001_initial','2026-03-27 18:13:33.725344'),(29,'auditlogs','0001_initial','2026-03-27 18:13:33.923623'),(30,'notifications','0001_initial','2026-03-27 18:13:34.170809'),(31,'results','0001_initial','2026-03-27 18:13:35.132973'),(32,'sessions','0001_initial','2026-03-27 18:13:35.216705'),(33,'settings_app','0001_initial','2026-03-27 18:13:35.282730'),(34,'warnings','0001_initial','2026-03-27 18:13:35.582219'),(35,'accounts','0002_remove_user_activated_at_and_more','2026-03-29 08:35:43.557135'),(36,'warnings','0002_warningescalationrule_parentguardiannotification_and_more','2026-04-02 04:59:15.552755'),(37,'enrollments','0002_remove_enrollment_total_score_enrollment_final_score_and_more','2026-04-02 15:03:28.964436'),(38,'warnings','0003_delete_parentguardiannotification','2026-04-02 17:26:40.927314'),(39,'warnings','0004_earlywarningresult_cgpa_risk_score','2026-04-06 11:19:42.236267'),(40,'enrollments','0003_remove_enrollment_final_score_and_more','2026-04-06 11:31:11.721512'),(41,'core','0001_add_calculation_log','2026-04-06 12:40:41.022246'),(42,'enrollments','0004_alter_enrollment_attended_classes','2026-04-06 13:06:19.330508'),(43,'core','0002_processingstatus','2026-04-06 13:13:08.072032'),(44,'teachers','0002_teacher_awards_and_honors_and_more','2026-04-08 11:56:11.020074');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('z04jknrk2m5599ckbwbxqut0w7uzif9a','.eJxVi70OwiAQgN-F2TQU5OccjQ5OPgI5uCM0am1KmYzvrk066Pr9vETAtpTQKs9hIHEQTux-WcR043EVOE21w5SebVxqt_HanR843K_z5XTcyr-9YC3fl51X5C069ghIlpXTFrLNSbq9JoqowWcyDKuQ0UQPPZoIqDT30oj3B2drNwg:1wAWWF:qPfFtAAa1tGvBVV1iMtjE7xoW-dHe9bZIH3gQc901MA','2026-04-09 17:16:47.321238');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `early_warning_results`
--

DROP TABLE IF EXISTS `early_warning_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `early_warning_results` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `risk_score` decimal(5,2) NOT NULL,
  `warning_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `risk_factors` json NOT NULL,
  `attendance_risk_score` decimal(5,2) NOT NULL,
  `gpa_risk_score` decimal(5,2) NOT NULL,
  `course_failure_risk_score` decimal(5,2) NOT NULL,
  `trend_risk_score` decimal(5,2) NOT NULL,
  `missing_assessment_risk_score` decimal(5,2) NOT NULL,
  `teacher_flag_risk_score` decimal(5,2) NOT NULL,
  `recommendations` json NOT NULL,
  `is_acknowledged` tinyint(1) NOT NULL,
  `acknowledged_at` datetime(6) DEFAULT NULL,
  `generated_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `semester_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  `cgpa_risk_score` decimal(5,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `early_warning_results_student_id_semester_id_af3f91db_uniq` (`student_id`,`semester_id`),
  KEY `early_warning_results_semester_id_49d1590d_fk_semesters_id` (`semester_id`),
  CONSTRAINT `early_warning_results_semester_id_49d1590d_fk_semesters_id` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`),
  CONSTRAINT `early_warning_results_student_id_2c3cf1fa_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `early_warning_results`
--

LOCK TABLES `early_warning_results` WRITE;
/*!40000 ALTER TABLE `early_warning_results` DISABLE KEYS */;
INSERT INTO `early_warning_results` VALUES (2,0.00,'red','[{\"type\": \"attendance\", \"score\": 75.0, \"reason\": \"Attendance below threshold (50.0%)\"}]',75.00,0.00,0.00,0.00,0.00,50.00,'[]',1,'2026-03-30 10:35:45.585820','2026-03-30 07:56:24.691695','2026-04-08 10:30:29.460669',1,2,0.00),(7,55.00,'red','[{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}]',0.00,100.00,0.00,0.00,0.00,0.00,'[]',0,NULL,'2026-03-31 23:32:08.138107','2026-04-08 10:30:29.414937',1,66,0.00),(8,75.00,'red','[{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}]',0.00,100.00,0.00,0.00,0.00,0.00,'[]',0,NULL,'2026-03-31 23:32:08.143332','2026-04-08 10:30:29.372247',1,67,0.00),(9,40.00,'red','[{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}]',0.00,100.00,0.00,0.00,0.00,0.00,'[]',0,NULL,'2026-03-31 23:32:08.149201','2026-04-08 10:30:29.329057',1,68,0.00),(10,0.00,'red','[{\"type\": \"academic\", \"score\": 100.0, \"reason\": \"Academic performance concerns\"}]',0.00,100.00,0.00,0.00,0.00,0.00,'[\"Warning cleared by admin\"]',0,NULL,'2026-03-31 23:32:08.154034','2026-04-08 10:30:29.286971',1,69,0.00);
/*!40000 ALTER TABLE `early_warning_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `early_warning_rules`
--

DROP TABLE IF EXISTS `early_warning_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `early_warning_rules` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `threshold_value` decimal(6,2) NOT NULL,
  `comparison_operator` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `weight` decimal(4,2) NOT NULL,
  `severity` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `order` smallint unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `early_warning_rules_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `early_warning_rules`
--

LOCK TABLES `early_warning_rules` WRITE;
/*!40000 ALTER TABLE `early_warning_rules` DISABLE KEYS */;
INSERT INTO `early_warning_rules` VALUES (1,'gpa_critical','Critical Low GPA','GPA below 1.5 - Critical academic performance','gpa',1.50,'<',30.00,'red',1,0,'2026-03-30 07:58:49.009428','2026-03-30 07:58:49.009449'),(2,'gpa_warning','Low GPA Warning','GPA below 2.0 - Warning level','gpa',2.00,'<',20.00,'orange',1,0,'2026-03-30 07:58:49.016815','2026-03-30 07:58:49.016836'),(3,'cgpa_critical','Critical Low CGPA','CGPA below 2.0 - Critical cumulative performance','cgpa',2.00,'<',25.00,'red',1,0,'2026-03-30 07:58:49.024631','2026-03-30 07:58:49.024656'),(4,'cgpa_warning','Low CGPA Warning','CGPA below 2.5 - Warning level','cgpa',2.50,'<',15.00,'orange',1,0,'2026-03-30 07:58:49.029989','2026-03-30 07:58:49.030035'),(5,'attendance_critical','Critical Attendance','Attendance below 60% - Critical absence','attendance',60.00,'<',25.00,'red',1,0,'2026-03-30 07:58:49.035546','2026-03-30 07:58:49.035568'),(6,'attendance_warning','Low Attendance Warning','Attendance below 75% - Warning level','attendance',75.00,'<',15.00,'orange',1,0,'2026-03-30 07:58:49.042869','2026-03-30 07:58:49.042909'),(57,'CRIT_ATTEND','Critical Attendance Warning','','attendance',70.00,'<',10.00,'red',1,1,'2026-03-31 23:31:28.005802','2026-03-31 23:31:28.005826'),(58,'ATTEND_WARN','Attendance Warning','','attendance',80.00,'<',10.00,'orange',1,2,'2026-03-31 23:31:28.009261','2026-03-31 23:31:28.009293'),(59,'LOW_GRADE','Low Grade Warning','','gpa',60.00,'<',10.00,'orange',1,3,'2026-03-31 23:31:28.013050','2026-03-31 23:31:28.013091'),(60,'FAIL_GRADE','Failing Grade Warning','','gpa',50.00,'<',10.00,'red',1,4,'2026-03-31 23:31:28.020139','2026-03-31 23:31:28.020172');
/*!40000 ALTER TABLE `early_warning_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `enroll_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `enrolled_at` datetime(6) NOT NULL,
  `dropped_at` datetime(6) DEFAULT NULL,
  `drop_reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_classes` int unsigned NOT NULL,
  `attended_classes` decimal(6,1) NOT NULL,
  `attendance_percentage` decimal(5,2) NOT NULL,
  `remarks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `course_offering_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  `result_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `final_score` decimal(5,2) DEFAULT NULL,
  `grade_point` decimal(3,2) DEFAULT NULL,
  `letter_grade` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pass_fail_status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `enrollments_student_id_course_offering_id_f8b5df31_uniq` (`student_id`,`course_offering_id`),
  KEY `enrollments_course_offering_id_921f940d_fk_course_offerings_id` (`course_offering_id`),
  CONSTRAINT `enrollments_course_offering_id_921f940d_fk_course_offerings_id` FOREIGN KEY (`course_offering_id`) REFERENCES `course_offerings` (`id`),
  CONSTRAINT `enrollments_student_id_19c0bed4_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `enrollments_chk_1` CHECK ((`total_classes` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
INSERT INTO `enrollments` VALUES (85,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,1.0,50.00,'','2026-03-31 23:32:07.719830','2026-03-31 23:32:07.719844',29,2,'pending',NULL,NULL,'',''),(86,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,2.0,100.00,'','2026-03-31 23:32:07.725447','2026-03-31 23:32:07.725467',29,66,'pending',NULL,NULL,'',''),(87,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,2.0,100.00,'','2026-03-31 23:32:07.732180','2026-03-31 23:32:07.732207',29,67,'pending',NULL,NULL,'',''),(88,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,2.0,100.00,'','2026-03-31 23:32:07.737549','2026-03-31 23:32:07.737568',29,68,'pending',NULL,NULL,'',''),(89,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,2.0,100.00,'','2026-03-31 23:32:07.742482','2026-03-31 23:32:07.742529',29,69,'pending',NULL,NULL,'',''),(90,'enrolled','2024-09-30 16:00:00.000000',NULL,'',2,2.0,100.00,'','2026-03-31 23:32:07.746979','2026-03-31 23:32:07.747003',29,70,'pending',NULL,NULL,'',''),(91,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.750687','2026-03-31 23:32:07.750707',30,2,'pending',NULL,NULL,'',''),(92,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.756604','2026-03-31 23:32:07.756628',30,66,'pending',NULL,NULL,'',''),(93,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.760855','2026-03-31 23:32:07.760880',30,67,'pending',NULL,NULL,'',''),(94,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.764829','2026-03-31 23:32:07.764850',30,68,'pending',NULL,NULL,'',''),(95,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.768797','2026-03-31 23:32:07.768812',30,69,'pending',NULL,NULL,'',''),(96,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.773202','2026-03-31 23:32:07.773225',30,70,'pending',NULL,NULL,'',''),(97,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.777419','2026-03-31 23:32:07.777444',31,2,'pending',NULL,NULL,'',''),(98,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.782062','2026-03-31 23:32:07.782082',31,66,'pending',NULL,NULL,'',''),(99,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.785271','2026-03-31 23:32:07.785292',31,67,'pending',NULL,NULL,'',''),(100,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.789198','2026-03-31 23:32:07.789353',31,68,'pending',NULL,NULL,'',''),(101,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.794841','2026-03-31 23:32:07.794864',31,69,'pending',NULL,NULL,'',''),(102,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.798996','2026-03-31 23:32:07.799018',31,70,'pending',NULL,NULL,'',''),(103,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.803948','2026-03-31 23:32:07.803972',32,2,'pending',NULL,NULL,'',''),(104,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.811540','2026-03-31 23:32:07.811562',32,66,'pending',NULL,NULL,'',''),(105,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.815698','2026-03-31 23:32:07.815713',32,67,'pending',NULL,NULL,'',''),(106,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.819076','2026-03-31 23:32:07.819090',32,68,'pending',NULL,NULL,'',''),(107,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.824056','2026-03-31 23:32:07.824078',32,69,'pending',NULL,NULL,'',''),(108,'enrolled','2024-09-30 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.827811','2026-03-31 23:32:07.827826',32,70,'pending',NULL,NULL,'',''),(109,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.831664','2026-03-31 23:32:07.831680',33,2,'pending',NULL,NULL,'',''),(110,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.836796','2026-03-31 23:32:07.836819',33,66,'pending',NULL,NULL,'',''),(111,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.843601','2026-03-31 23:32:07.843624',33,67,'pending',NULL,NULL,'',''),(112,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.847211','2026-03-31 23:32:07.847227',33,68,'pending',NULL,NULL,'',''),(113,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.850799','2026-03-31 23:32:07.850819',33,69,'pending',NULL,NULL,'',''),(114,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.857160','2026-03-31 23:32:07.857183',33,70,'pending',NULL,NULL,'',''),(115,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.861512','2026-03-31 23:32:07.861531',34,2,'pending',NULL,NULL,'',''),(116,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.867466','2026-03-31 23:32:07.867492',34,66,'pending',NULL,NULL,'',''),(117,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.871278','2026-03-31 23:32:07.871297',34,67,'pending',NULL,NULL,'',''),(118,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.875379','2026-03-31 23:32:07.875402',34,68,'pending',NULL,NULL,'',''),(119,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,0.00,'','2026-03-31 23:32:07.878988','2026-03-31 23:32:07.879009',34,69,'pending',NULL,NULL,'',''),(120,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.882784','2026-03-31 23:32:07.882815',34,70,'pending',NULL,NULL,'',''),(121,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.888139','2026-03-31 23:32:07.888196',35,2,'pending',NULL,NULL,'',''),(122,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.893795','2026-03-31 23:32:07.893812',35,66,'pending',NULL,NULL,'',''),(123,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.897286','2026-03-31 23:32:07.897311',35,67,'pending',NULL,NULL,'',''),(124,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.901683','2026-03-31 23:32:07.901704',35,68,'pending',NULL,NULL,'',''),(125,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.906514','2026-03-31 23:32:07.906534',35,69,'pending',NULL,NULL,'',''),(126,'enrolled','2025-02-14 16:00:00.000000',NULL,'',0,0.0,100.00,'','2026-03-31 23:32:07.910635','2026-03-31 23:32:07.910656',35,70,'pending',NULL,NULL,'',''),(127,'enrolled','2026-04-08 11:21:43.700542',NULL,'',0,0.0,0.00,'','2026-04-08 11:21:43.700708','2026-04-08 11:21:43.700728',32,71,'pending',NULL,NULL,'',''),(128,'enrolled','2026-04-08 11:21:43.708673',NULL,'',0,0.0,0.00,'','2026-04-08 11:21:43.708815','2026-04-08 11:21:43.708842',32,72,'pending',NULL,NULL,'','');
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `final_results`
--

DROP TABLE IF EXISTS `final_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `final_results` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `total_score` decimal(5,2) DEFAULT NULL,
  `letter_grade` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `grade_point` decimal(3,2) DEFAULT NULL,
  `pass_fail_status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quality_points` decimal(6,2) DEFAULT NULL,
  `is_published` tinyint(1) NOT NULL,
  `published_at` datetime(6) DEFAULT NULL,
  `remarks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `enrollment_id` bigint NOT NULL,
  `published_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `enrollment_id` (`enrollment_id`),
  KEY `final_results_published_by_id_0c0108f4_fk_users_id` (`published_by_id`),
  CONSTRAINT `final_results_enrollment_id_66e18ab7_fk_enrollments_id` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`),
  CONSTRAINT `final_results_published_by_id_0c0108f4_fk_users_id` FOREIGN KEY (`published_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `final_results`
--

LOCK TABLES `final_results` WRITE;
/*!40000 ALTER TABLE `final_results` DISABLE KEYS */;
INSERT INTO `final_results` VALUES (15,93.00,'A',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.917543','2026-03-31 23:32:07.917577',126,NULL),(16,79.00,'C',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.923239','2026-03-31 23:32:07.923296',125,NULL),(17,77.00,'C',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.928956','2026-03-31 23:32:07.928994',124,NULL),(18,64.00,'D',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.935798','2026-03-31 23:32:07.935829',123,NULL),(19,66.00,'D',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.942056','2026-03-31 23:32:07.942101',122,NULL),(20,65.00,'D',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.948973','2026-03-31 23:32:07.949010',121,NULL),(21,67.00,'D',NULL,'',NULL,1,NULL,'','2026-03-31 23:32:07.955051','2026-03-31 23:32:07.955097',120,NULL);
/*!40000 ALTER TABLE `final_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_mappings`
--

DROP TABLE IF EXISTS `grade_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_mappings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `letter_grade` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `grade_point` decimal(3,2) NOT NULL,
  `min_percentage` decimal(5,2) NOT NULL,
  `max_percentage` decimal(5,2) NOT NULL,
  `is_passing` tinyint(1) NOT NULL,
  `order` smallint unsigned NOT NULL,
  `scheme_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `grade_mappings_scheme_id_6ac17169_fk_grade_schemes_id` (`scheme_id`),
  CONSTRAINT `grade_mappings_scheme_id_6ac17169_fk_grade_schemes_id` FOREIGN KEY (`scheme_id`) REFERENCES `grade_schemes` (`id`),
  CONSTRAINT `grade_mappings_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_mappings`
--

LOCK TABLES `grade_mappings` WRITE;
/*!40000 ALTER TABLE `grade_mappings` DISABLE KEYS */;
/*!40000 ALTER TABLE `grade_mappings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_policies`
--

DROP TABLE IF EXISTS `grade_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_policies` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `max_gpa` decimal(3,2) NOT NULL,
  `passing_grade_point` decimal(3,2) NOT NULL,
  `gpa_warning_threshold` decimal(3,2) NOT NULL,
  `cgpa_warning_threshold` decimal(3,2) NOT NULL,
  `attendance_warning_threshold` decimal(5,2) NOT NULL,
  `gpa_drop_warning_threshold` decimal(3,2) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_policies`
--

LOCK TABLES `grade_policies` WRITE;
/*!40000 ALTER TABLE `grade_policies` DISABLE KEYS */;
/*!40000 ALTER TABLE `grade_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_schemes`
--

DROP TABLE IF EXISTS `grade_schemes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_schemes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_schemes`
--

LOCK TABLES `grade_schemes` WRITE;
/*!40000 ALTER TABLE `grade_schemes` DISABLE KEYS */;
/*!40000 ALTER TABLE `grade_schemes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title_en` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_zh` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notification_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_object_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_object_id` int unsigned DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL,
  `read_at` datetime(6) DEFAULT NULL,
  `is_emailed` tinyint(1) NOT NULL,
  `emailed_at` datetime(6) DEFAULT NULL,
  `action_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `recipient_id` bigint NOT NULL,
  `sender_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_recipient_id_e1133bac_fk_users_id` (`recipient_id`),
  KEY `notifications_sender_id_57e62d28_fk_users_id` (`sender_id`),
  CONSTRAINT `notifications_recipient_id_e1133bac_fk_users_id` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`id`),
  CONSTRAINT `notifications_sender_id_57e62d28_fk_users_id` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  CONSTRAINT `notifications_chk_1` CHECK ((`related_object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `processing_statuses`
--

DROP TABLE IF EXISTS `processing_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `processing_statuses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `process_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` int unsigned DEFAULT NULL,
  `enrollment_id` int unsigned DEFAULT NULL,
  `semester_id` int unsigned DEFAULT NULL,
  `course_offering_id` int unsigned DEFAULT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `details` json NOT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `triggered_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `processing_statuses_triggered_by_id_fab4e941_fk_users_id` (`triggered_by_id`),
  KEY `processing_statuses_student_id_ddd33cd7` (`student_id`),
  KEY `processing_statuses_enrollment_id_9f7cd13b` (`enrollment_id`),
  KEY `processing_statuses_semester_id_9623c5f9` (`semester_id`),
  KEY `processing_statuses_course_offering_id_c2abaf2e` (`course_offering_id`),
  KEY `processing__process_44052e_idx` (`process_type`,`status`),
  KEY `processing__student_0557f0_idx` (`student_id`,`process_type`),
  KEY `processing__enrollm_14e027_idx` (`enrollment_id`,`process_type`),
  KEY `processing__semeste_8cb5f3_idx` (`semester_id`,`process_type`),
  KEY `processing__updated_810591_idx` (`updated_at`),
  CONSTRAINT `processing_statuses_triggered_by_id_fab4e941_fk_users_id` FOREIGN KEY (`triggered_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `processing_statuses_chk_1` CHECK ((`student_id` >= 0)),
  CONSTRAINT `processing_statuses_chk_2` CHECK ((`enrollment_id` >= 0)),
  CONSTRAINT `processing_statuses_chk_3` CHECK ((`semester_id` >= 0)),
  CONSTRAINT `processing_statuses_chk_4` CHECK ((`course_offering_id` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `processing_statuses`
--

LOCK TABLES `processing_statuses` WRITE;
/*!40000 ALTER TABLE `processing_statuses` DISABLE KEYS */;
INSERT INTO `processing_statuses` VALUES (1,'warning','completed',2,NULL,1,NULL,'Warning updated','{\"acknowledged\": true, \"warning_level\": \"red\"}','','2026-04-06 14:37:16.907639','2026-04-08 10:30:29.465258',NULL),(2,'attendance','completed',70,90,1,29,'Attendance tracking complete','{\"percentage\": \"100.0\", \"total_classes\": 2, \"attended_classes\": \"2.0\"}','','2026-04-08 10:30:29.228050','2026-04-08 10:30:29.229598',NULL),(3,'attendance','completed',69,89,1,29,'Attendance tracking complete','{\"percentage\": \"100.0\", \"total_classes\": 2, \"attended_classes\": \"2.0\"}','','2026-04-08 10:30:29.274179','2026-04-08 10:30:29.275367',NULL),(4,'warning','completed',69,NULL,1,NULL,'Warning updated','{\"acknowledged\": false, \"warning_level\": \"red\"}','','2026-04-08 10:30:29.294830','2026-04-08 10:30:29.296001',NULL),(5,'attendance','completed',68,88,1,29,'Attendance tracking complete','{\"percentage\": \"100.0\", \"total_classes\": 2, \"attended_classes\": \"2.0\"}','','2026-04-08 10:30:29.318448','2026-04-08 10:30:29.320002',NULL),(6,'warning','completed',68,NULL,1,NULL,'Warning updated','{\"acknowledged\": false, \"warning_level\": \"red\"}','','2026-04-08 10:30:29.334540','2026-04-08 10:30:29.336797',NULL),(7,'attendance','completed',67,87,1,29,'Attendance tracking complete','{\"percentage\": \"100.0\", \"total_classes\": 2, \"attended_classes\": \"2.0\"}','','2026-04-08 10:30:29.362213','2026-04-08 10:30:29.363046',NULL),(8,'warning','completed',67,NULL,1,NULL,'Warning updated','{\"acknowledged\": false, \"warning_level\": \"red\"}','','2026-04-08 10:30:29.377178','2026-04-08 10:30:29.378087',NULL),(9,'attendance','completed',66,86,1,29,'Attendance tracking complete','{\"percentage\": \"100.0\", \"total_classes\": 2, \"attended_classes\": \"2.0\"}','','2026-04-08 10:30:29.404198','2026-04-08 10:30:29.405081',NULL),(10,'warning','completed',66,NULL,1,NULL,'Warning updated','{\"acknowledged\": false, \"warning_level\": \"red\"}','','2026-04-08 10:30:29.423148','2026-04-08 10:30:29.424433',NULL),(11,'attendance','partial',2,85,1,29,'Attendance tracking partial','{\"percentage\": \"50.0\", \"total_classes\": 2, \"attended_classes\": \"1.0\"}','','2026-04-08 10:30:29.450540','2026-04-08 10:30:29.451460',NULL);
/*!40000 ALTER TABLE `processing_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programs`
--

DROP TABLE IF EXISTS `programs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `programs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name_en` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_zh` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `degree_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `duration_years` smallint unsigned NOT NULL,
  `total_credits` smallint unsigned NOT NULL,
  `description_en` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_zh` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `programs_department_id_447dc60d_fk_departments_id` (`department_id`),
  CONSTRAINT `programs_department_id_447dc60d_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `programs_chk_1` CHECK ((`duration_years` >= 0)),
  CONSTRAINT `programs_chk_2` CHECK ((`total_credits` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programs`
--

LOCK TABLES `programs` WRITE;
/*!40000 ALTER TABLE `programs` DISABLE KEYS */;
INSERT INTO `programs` VALUES (1,'Bachelor of Science in Computer Science','计算机科学学士','BSC-CS-01','bachelor',4,120,'','','active','2026-03-28 09:15:13.925353','2026-03-28 09:15:13.927619',2),(46,'Bachelor of Computer Science','计算机科学学士','CS-BS','bachelor',4,120,'','','active','2026-03-31 23:31:28.045197','2026-03-31 23:31:28.045225',2),(47,'Bachelor of Software Engineering','软件工程学士','SE-BS','bachelor',4,120,'','','active','2026-03-31 23:31:28.050638','2026-03-31 23:31:28.050660',2),(48,'Bachelor of Computer Engineering','计算机工程学士','CE-BS','bachelor',4,128,'','','active','2026-03-31 23:31:28.053956','2026-03-31 23:31:28.053990',51),(49,'Master of Business Administration','工商管理硕士','MBA','master',2,36,'','','active','2026-03-31 23:31:28.057498','2026-03-31 23:31:28.057536',52);
/*!40000 ALTER TABLE `programs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `permission_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_permissions_role_id_permission_id_04f77df0_uniq` (`role_id`,`permission_id`),
  KEY `role_permissions_permission_id_ad343843_fk_permissions_id` (`permission_id`),
  CONSTRAINT `role_permissions_permission_id_ad343843_fk_permissions_id` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`),
  CONSTRAINT `role_permissions_role_id_216516f2_fk_roles_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrator','admin','System Administrator','2026-03-27 18:28:41.884296','2026-03-27 18:28:41.884342'),(2,'Teacher','teacher','Teacher role','2026-03-28 09:45:26.077976','2026-03-28 09:45:26.078008'),(3,'Student','student','Student role','2026-03-28 09:45:26.090229','2026-03-28 09:45:26.090272'),(18,'Staff','staff','Administrative staff with limited system access','2026-03-31 23:31:28.001479','2026-03-31 23:31:28.001533');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semester_summaries`
--

DROP TABLE IF EXISTS `semester_summaries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semester_summaries` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `semester_gpa` decimal(3,2) NOT NULL,
  `semester_credits_attempted` decimal(5,2) NOT NULL,
  `semester_credits_earned` decimal(5,2) NOT NULL,
  `total_quality_points` decimal(8,2) NOT NULL,
  `courses_attempted` smallint unsigned NOT NULL,
  `courses_passed` smallint unsigned NOT NULL,
  `courses_failed` smallint unsigned NOT NULL,
  `failed_courses_list` json NOT NULL,
  `warning_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `computed_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `semester_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `semester_summaries_student_id_semester_id_a9986ed2_uniq` (`student_id`,`semester_id`),
  KEY `semester_summaries_semester_id_dc7b0fc6_fk_semesters_id` (`semester_id`),
  CONSTRAINT `semester_summaries_semester_id_dc7b0fc6_fk_semesters_id` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`),
  CONSTRAINT `semester_summaries_student_id_0ce21f33_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `semester_summaries_chk_1` CHECK ((`courses_attempted` >= 0)),
  CONSTRAINT `semester_summaries_chk_2` CHECK ((`courses_passed` >= 0)),
  CONSTRAINT `semester_summaries_chk_3` CHECK ((`courses_failed` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semester_summaries`
--

LOCK TABLES `semester_summaries` WRITE;
/*!40000 ALTER TABLE `semester_summaries` DISABLE KEYS */;
/*!40000 ALTER TABLE `semester_summaries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semesters` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `semester_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_en` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_zh` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `registration_start` date DEFAULT NULL,
  `registration_end` date DEFAULT NULL,
  `grade_entry_start` date DEFAULT NULL,
  `grade_entry_end` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `semesters_academic_year_semester_type_9c52aeb3_uniq` (`academic_year`,`semester_type`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
INSERT INTO `semesters` VALUES (1,'2024-2025','fall','Fall Semester','秋季学期','2024-09-01','2028-07-15',NULL,NULL,NULL,NULL,1,'active','2026-03-28 09:24:16.529096','2026-03-28 09:24:16.529131'),(12,'2024-2025','spring','Spring 2025','2025春季学期','2025-01-15','2025-05-15',NULL,NULL,NULL,NULL,1,'active','2026-03-31 23:31:28.065902','2026-04-08 10:55:47.858997');
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_no` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch_year` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `nationality` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guardian_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guardian_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guardian_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `guardian_relationship` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `admission_date` date DEFAULT NULL,
  `expected_graduation` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_credits_earned` decimal(6,2) NOT NULL,
  `cgpa` decimal(3,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `advisor_id` bigint DEFAULT NULL,
  `current_semester_id` bigint DEFAULT NULL,
  `department_id` bigint NOT NULL,
  `program_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_no` (`student_no`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `students_advisor_id_d0bb1ddb_fk_teachers_id` (`advisor_id`),
  KEY `students_current_semester_id_cef2c05a_fk_semesters_id` (`current_semester_id`),
  KEY `students_department_id_9c73830b_fk_departments_id` (`department_id`),
  KEY `students_program_id_f5510574_fk_programs_id` (`program_id`),
  CONSTRAINT `students_advisor_id_d0bb1ddb_fk_teachers_id` FOREIGN KEY (`advisor_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `students_current_semester_id_cef2c05a_fk_semesters_id` FOREIGN KEY (`current_semester_id`) REFERENCES `semesters` (`id`),
  CONSTRAINT `students_department_id_9c73830b_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `students_program_id_f5510574_fk_programs_id` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`),
  CONSTRAINT `students_user_id_42864fc9_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (2,'2024101010','2024','male','2026-03-04','','','打你','8655083193','','',NULL,NULL,'active',0.00,0.00,'2026-03-28 13:57:28.624263','2026-03-28 13:57:28.624288',NULL,1,2,1,4),(66,'S001','2024','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:31:51.162877','2026-03-31 23:31:51.162919',NULL,NULL,2,46,142),(67,'S002','2024','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:31:54.563542','2026-03-31 23:31:54.563594',NULL,NULL,2,46,143),(68,'S003','2024','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:31:57.342694','2026-03-31 23:31:57.342729',NULL,NULL,2,47,144),(69,'S004','2023','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:31:59.897934','2026-03-31 23:31:59.897964',NULL,NULL,2,46,145),(70,'S005','2023','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:32:02.413463','2026-03-31 23:32:02.413486',NULL,NULL,2,47,146),(71,'S006','2022','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:32:05.268553','2026-03-31 23:32:05.268593',NULL,NULL,2,46,147),(72,'S007','2022','',NULL,'','','','','','',NULL,NULL,'active',0.00,3.50,'2026-03-31 23:32:07.627446','2026-03-31 23:32:07.627475',NULL,NULL,2,47,148);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_editable` tinyint(1) NOT NULL,
  `category` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `teacher_no` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialization` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `office_location` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `office_hours` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `join_date` date NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `awards_and_honors` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `education_background` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `linkedin` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `professional_experience` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `publications` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `research_abilities` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `research_interests` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `teaching_interests` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `website` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_no` (`teacher_no`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `teachers_department_id_3458aa5b_fk_departments_id` (`department_id`),
  CONSTRAINT `teachers_department_id_3458aa5b_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `teachers_user_id_6fdcda53_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (66,'T001','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:31.107486','2026-04-08 12:03:47.003405',2,135,'','','','','','','','',''),(67,'T002','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:33.906076','2026-03-31 23:31:33.906104',2,136,'','','','','','','','',''),(68,'T003','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:36.968187','2026-03-31 23:31:36.968215',51,137,'','','','','','','','',''),(69,'T004','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:39.665552','2026-03-31 23:31:39.665580',51,138,'','','','','','','','',''),(70,'T005','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:43.285974','2026-03-31 23:31:43.286004',52,139,'','','','','','','','',''),(71,'T006','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:46.097108','2026-03-31 23:31:46.097139',2,140,'','','','','','','','',''),(72,'T007','lecturer','General','','','','2020-01-01','active','2026-03-31 23:31:48.528706','2026-03-31 23:31:48.528732',51,141,'','','','','','','','','');
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `uuid` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name_en` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name_zh` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `last_login_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `email` (`email`),
  KEY `users_role_id_1900a745_fk_roles_id` (`role_id`),
  CONSTRAINT `users_role_id_1900a745_fk_roles_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (4,'pbkdf2_sha256$1200000$oaZNfZSmiHUXkl3bo18ZDL$7zfF+JE4TKNG5sySz4JU/tCZ5thtnvdFnWxDVDmrPO4=','2026-04-08 16:42:57.381665','b911b4905e4849d49e514faa91ce65b4','omer','孟勇','abbasal@gmail.com','12221036386','','active',0,0,1,'2026-04-08 16:42:57.385696','2026-03-28 13:57:28.612528','2026-03-28 14:16:28.744552',3),(7,'pbkdf2_sha256$1200000$NftfTfFGZlXWpX56f3ntvv$THmm4pFGgi8aWulJocPbmngPbB9pkCrb9JVzTiSVPqU=','2026-04-08 17:16:47.307034','939ca299239149ff94d3183e015fd975','ABBAS','孟勇','admin@university.edu','15551036386','avatars/2026/04/made-some-anime-profile-pictures-to-use-which-is-your-v0-r814ufs8drrc1.png','active',1,1,1,'2026-04-08 17:16:47.311427','2026-03-30 07:22:23.668268','2026-04-01 12:29:03.860912',1),(135,'pbkdf2_sha256$1200000$ofpC004sYUNzP2pLqOovDa$RwBud1bKxMbQC0jXXTGGlJlxj5OBqc/FZiEkmyWe/ag=','2026-04-08 16:58:05.310896','776337cb738341e589edd593469a0ecb','John Smith','约翰·史密斯','teacher1@university.edu','','','active',1,0,1,'2026-04-08 16:58:05.315719','2026-03-31 23:31:28.082777','2026-04-08 12:03:47.009273',2),(136,'pbkdf2_sha256$1200000$GWfmute0KrvjagWXBAaYkB$khOw1AECmS81DqHcjs0pSKToo2K6o+/ifW8ldpvGjG4=',NULL,'c341916336da446eb0acf3215e391966','Sarah Johnson','莎拉·约翰逊','teacher2@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:31.113724','2026-03-31 23:31:33.902260',2),(137,'pbkdf2_sha256$1200000$ndFBy8JA4hPy51PaqiBc6C$cpBqzbTvg2cr/bVcChcYp7ytXn4UnTFcds2Kp00eWEs=',NULL,'5b28501dc2a542f998d4340334787294','Michael Chen','迈克尔·陈','teacher3@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:33.915261','2026-03-31 23:31:36.960808',2),(138,'pbkdf2_sha256$1200000$FPYrVwS8eZ1veYIXv9JMdn$ceH2Jqf5pRdsBtllh0VTrAdRHNYNO663wwmXdifGq9s=',NULL,'ca94718a8bbb478986ee7f012daeab05','Emily Davis','艾米丽·戴维斯','teacher4@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:36.977425','2026-03-31 23:31:39.661729',2),(139,'pbkdf2_sha256$1200000$E7oqREnwrOMxdyM4YSb6CL$GToiLzd8mEPTxRaKxssJHRCij/qC8f3WW2D2kSY1joA=',NULL,'3a38952f16bc439094d0a4ee0cd7d7ed','Robert Wilson','罗伯特·威尔逊','teacher5@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:39.669507','2026-03-31 23:31:43.282140',2),(140,'pbkdf2_sha256$1200000$NAzI7dKrFZnlRhTwKXxUn6$r1dJXMDcpsqRRw9XudO18nZHnLu+ly4qtm8oeV3SI9I=',NULL,'e0c99559001d437f85892a833ca53729','Lisa Brown','丽莎·布朗','teacher6@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:43.294804','2026-03-31 23:31:46.092644',2),(141,'pbkdf2_sha256$1200000$bTaxSdOXoTQ6MsIqulLN08$d+cM3GPWg+bCcCH+dY8YoLrex0ZRNNqLRY/2z/wplhs=',NULL,'f2583b25835243538dcb327807c946ac','David Lee','大卫·李','teacher7@university.edu','','','pending',1,0,1,NULL,'2026-03-31 23:31:46.102201','2026-03-31 23:31:48.522235',2),(142,'pbkdf2_sha256$1200000$Z5K2hnls88XumD4VmVlXMw$9B0No2dtYucg1Omn9moHnmZJgp0P4HxKYi6oBXTY/Mg=',NULL,'df459fa6950d4764a20e81d3cd346d94','Alice Wang','爱丽丝·王','student1@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:31:48.536836','2026-03-31 23:31:51.158838',3),(143,'pbkdf2_sha256$1200000$j9P00ah4e6pRe5n4UFhobE$3elTaieQlATCql/5aPJZmBuvU8ANLf/kX1LFXCO7aiQ=',NULL,'71426c5d833a4aaeba7c5ecf07be81d3','Bob Zhang','鲍勃·张','student2@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:31:51.167169','2026-03-31 23:31:54.559215',3),(144,'pbkdf2_sha256$1200000$sKHh6QDJxh12QX3GRHyXIY$sh5nbmhoTSqoZpwZxFzVR6Rr9p3cB7kMvbhvKPZMKw0=',NULL,'8f808c757956469f888d96622ba5e6c7','Carol Liu','卡罗尔·刘','student3@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:31:54.569798','2026-03-31 23:31:57.338288',3),(145,'pbkdf2_sha256$1200000$s61SixtCT0FBOfM9C2mM2J$PL2FKJsJc3KN8PNhqJM/yoT47l2OMgAbasZJpZ7m1+s=',NULL,'d0b72133939d49af9597ec012721eeb4','David Kim','大卫·金','student4@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:31:57.346292','2026-03-31 23:31:59.894572',3),(146,'pbkdf2_sha256$1200000$hRLbfRxcEt2mOj8nnP4u0R$fxq7smiyNtfOwiMGWk3klIqq8zEqIZ5cXDndDOdHoRU=',NULL,'52e626a8ccb3469c826b9f2781c8b192','Eva Martinez','伊娃·马丁内斯','student5@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:31:59.901708','2026-03-31 23:32:02.410187',3),(147,'pbkdf2_sha256$1200000$PMwr586DeAaR8FQbmG80xe$Woh1LE93+QG11G/uIwJyHTe1D5yfvDZ1itgsTcvzuOs=',NULL,'8b1f668e92634519a3a75bfe524ff827','Frank Huang','弗兰克·黄','student6@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:32:02.416521','2026-03-31 23:32:05.263412',3),(148,'pbkdf2_sha256$1200000$IADShozLLjIty1NrEQyQV3$LTy1YFVcXx3RPBacGXNEJ7b8bBq3RFOFKMuPsbAMes8=',NULL,'883a93ca21994ab39109e88ab0dc9896','Grace Chen','格蕾丝·陈','student7@university.edu','','','pending',0,0,1,NULL,'2026-03-31 23:32:05.271399','2026-03-31 23:32:07.623360',3);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_permissions`
--

DROP TABLE IF EXISTS `users_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_permissions`
--

LOCK TABLES `users_user_permissions` WRITE;
/*!40000 ALTER TABLE `users_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warning_escalation_rules`
--

DROP TABLE IF EXISTS `warning_escalation_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warning_escalation_rules` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `to_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `days_without_improvement` int unsigned NOT NULL,
  `requires_intervention_attempt` tinyint(1) NOT NULL,
  `auto_notify_parents` tinyint(1) NOT NULL,
  `auto_notify_advisor` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `warning_escalation_rules_chk_1` CHECK ((`days_without_improvement` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warning_escalation_rules`
--

LOCK TABLES `warning_escalation_rules` WRITE;
/*!40000 ALTER TABLE `warning_escalation_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `warning_escalation_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warning_evidence`
--

DROP TABLE IF EXISTS `warning_evidence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warning_evidence` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `evidence_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_attachment` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_snapshot` json NOT NULL,
  `captured_at` datetime(6) NOT NULL,
  `captured_by_id` bigint DEFAULT NULL,
  `warning_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `warning_evidence_captured_by_id_a6acf814_fk_users_id` (`captured_by_id`),
  KEY `warning_evidence_warning_id_819aada3_fk_early_warning_results_id` (`warning_id`),
  CONSTRAINT `warning_evidence_captured_by_id_a6acf814_fk_users_id` FOREIGN KEY (`captured_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `warning_evidence_warning_id_819aada3_fk_early_warning_results_id` FOREIGN KEY (`warning_id`) REFERENCES `early_warning_results` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warning_evidence`
--

LOCK TABLES `warning_evidence` WRITE;
/*!40000 ALTER TABLE `warning_evidence` DISABLE KEYS */;
/*!40000 ALTER TABLE `warning_evidence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warning_history`
--

DROP TABLE IF EXISTS `warning_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warning_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `change_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `previous_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `new_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `previous_risk_score` decimal(5,2) DEFAULT NULL,
  `new_risk_score` decimal(5,2) DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `triggered_by_id` bigint DEFAULT NULL,
  `warning_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `warning_history_triggered_by_id_81c3c02c_fk_users_id` (`triggered_by_id`),
  KEY `warning_history_warning_id_d7bd17a7_fk_early_warning_results_id` (`warning_id`),
  CONSTRAINT `warning_history_triggered_by_id_81c3c02c_fk_users_id` FOREIGN KEY (`triggered_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `warning_history_warning_id_d7bd17a7_fk_early_warning_results_id` FOREIGN KEY (`warning_id`) REFERENCES `early_warning_results` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warning_history`
--

LOCK TABLES `warning_history` WRITE;
/*!40000 ALTER TABLE `warning_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `warning_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warning_interventions`
--

DROP TABLE IF EXISTS `warning_interventions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warning_interventions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `intervention_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scheduled_date` datetime(6) DEFAULT NULL,
  `completed_date` datetime(6) DEFAULT NULL,
  `outcome_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `follow_up_date` datetime(6) DEFAULT NULL,
  `is_effective` tinyint(1) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assigned_to_id` bigint DEFAULT NULL,
  `initiated_by_id` bigint DEFAULT NULL,
  `warning_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `warning_interventions_assigned_to_id_e073a93e_fk_teachers_id` (`assigned_to_id`),
  KEY `warning_interventions_initiated_by_id_396ef2ac_fk_users_id` (`initiated_by_id`),
  KEY `warning_intervention_warning_id_8a28be48_fk_early_war` (`warning_id`),
  CONSTRAINT `warning_intervention_warning_id_8a28be48_fk_early_war` FOREIGN KEY (`warning_id`) REFERENCES `early_warning_results` (`id`),
  CONSTRAINT `warning_interventions_assigned_to_id_e073a93e_fk_teachers_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `warning_interventions_initiated_by_id_396ef2ac_fk_users_id` FOREIGN KEY (`initiated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warning_interventions`
--

LOCK TABLES `warning_interventions` WRITE;
/*!40000 ALTER TABLE `warning_interventions` DISABLE KEYS */;
/*!40000 ALTER TABLE `warning_interventions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warning_resolutions`
--

DROP TABLE IF EXISTS `warning_resolutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warning_resolutions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `resolution_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resolution_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `final_risk_score` decimal(5,2) DEFAULT NULL,
  `improvement_metrics` json NOT NULL,
  `requires_monitoring` tinyint(1) NOT NULL,
  `monitoring_end_date` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `resolved_by_id` bigint DEFAULT NULL,
  `warning_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `warning_id` (`warning_id`),
  KEY `warning_resolutions_resolved_by_id_df8edd7e_fk_users_id` (`resolved_by_id`),
  CONSTRAINT `warning_resolutions_resolved_by_id_df8edd7e_fk_users_id` FOREIGN KEY (`resolved_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `warning_resolutions_warning_id_f6bdcd3f_fk_early_war` FOREIGN KEY (`warning_id`) REFERENCES `early_warning_results` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warning_resolutions`
--

LOCK TABLES `warning_resolutions` WRITE;
/*!40000 ALTER TABLE `warning_resolutions` DISABLE KEYS */;
/*!40000 ALTER TABLE `warning_resolutions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-09  1:34:09
