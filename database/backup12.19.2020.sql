-- MariaDB dump 10.17  Distrib 10.5.4-MariaDB, for Win64 (AMD64)
--
-- Host: 192.168.50.173    Database: smart_home
-- ------------------------------------------------------
-- Server version	10.1.47-MariaDB-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `commands`
--

DROP TABLE IF EXISTS `commands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `commands` (
  `command_record_id` int(11) NOT NULL AUTO_INCREMENT,
  `info_level` int(2) NOT NULL,
  `info_id` int(11) DEFAULT NULL,
  `command_type` varchar(50) DEFAULT NULL,
  `command_sensor` varchar(50) NOT NULL,
  `command_name` varchar(50) NOT NULL,
  `command_value` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`command_record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commands`
--

LOCK TABLES `commands` WRITE;
/*!40000 ALTER TABLE `commands` DISABLE KEYS */;
INSERT INTO `commands` (`command_record_id`, `info_level`, `info_id`, `command_type`, `command_sensor`, `command_name`, `command_value`) VALUES (1,3,1,'write','HVAC_cool','AC_off','1'),(2,3,1,'write','HVAC_cool','AC_on','0'),(4,2,1,'broadcast','group','lights_off','lights_off'),(5,2,1,'broadcast','group','lights_on','lights_on'),(6,2,1,'broadcast','group','status','status'),(7,3,1,'write','HVAC_fan','fan_off','1'),(8,3,1,'write','HVAC_fan','fan_on','0'),(9,3,1,'write','HVAC_heat','heat_off','1'),(10,3,1,'write','HVAC_heat','heat_on','0'),(11,2,1,'hue','group','hue_lights_dim','{\"bri\": 50, \"on\": true}'),(12,2,1,'hue','group','hue_lights_off','{\"on\": false}'),(13,2,1,'hue','group','hue_lights_on','{\"bri\": 255, \"on\": true}'),(14,3,1,'write','light','lights_off','1'),(15,3,1,'write','light','lights_on','0'),(17,3,1,'read','all','status','None'),(18,2,1,'broadcast','thing1','AC_off','AC_off'),(19,2,1,'broadcast','thing1','heat_on','heat_on'),(20,2,1,'broadcast','thing1','heat_off','heat_off'),(21,2,1,'broadcast','thing1','fan_off','fan_off'),(22,2,1,'broadcast','thing1','fan_on','fan_on'),(23,2,1,'broadcast','thing1','AC_on','AC_on'),(24,2,1,'app','room','get_room_status','25'),(25,2,1,'broadcast','room','status','status'),(26,2,1,'app','room','hue_lights_dim','11'),(27,2,1,'app','room','hue_lights_on','13'),(28,2,1,'app','room','hue_lights_off','12'),(29,2,1,'app','room','lights_on','5'),(30,2,1,'app','room','lights_off','4'),(31,2,1,'hue','Kitchen_backlight','hue_kitchen_backlight','{\"bri\": 255, \"on\": true}'),(32,2,1,'app','room','hue_backlight','31'),(33,3,2,'read','all','status','None'),(34,3,2,'write','light','lights_on','0'),(35,3,2,'write','light','lights_off','1'),(36,3,2,'write','fan','fan_off','1'),(37,3,2,'write','fan','fan_on','0'),(38,2,2,'broadcast','group','status','status'),(41,2,2,'broadcast','room','status','status'),(50,2,2,'app','room','get_room_status','41'),(54,2,2,'hue','group','hue_off','{\"on\": false}'),(55,2,2,'hue','group','hue_dim','{\"bri\": 50, \"on\": true}'),(56,2,2,'hue','group','hue_on','{\"bri\": 255, \"on\": true}'),(57,2,2,'app','room','hue_lights_on','56'),(58,2,2,'app','room','hue_lights_dim','55'),(59,2,2,'app','room','hue_lights_off','54'),(60,2,2,'app','room','lights_on','63'),(61,2,2,'app','room','lights_off','62'),(62,2,2,'broadcast','group','lights_off','lights_off'),(63,2,2,'broadcast','group','lights_on','lights_on'),(64,2,2,'broadcast','group','fan_on','fan_on'),(65,2,2,'broadcast','group','fan_off','fan_off'),(66,2,2,'app','room','fan_on','64'),(67,2,2,'app','room','fan_off','65');
/*!40000 ALTER TABLE `commands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conditions`
--

DROP TABLE IF EXISTS `conditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conditions` (
  `condition_record_id` int(11) NOT NULL AUTO_INCREMENT,
  `condition_rule_id` int(11) NOT NULL,
  `condition_type` varchar(50) NOT NULL,
  `condition_check` varchar(50) DEFAULT NULL,
  `condition_logic` varchar(5) NOT NULL,
  `condition_value` varchar(50) NOT NULL,
  PRIMARY KEY (`condition_record_id`),
  KEY `conditions_rules_rule_id_fk` (`condition_rule_id`),
  KEY `conditions_sensor_types_sensor_type_fk` (`condition_check`),
  CONSTRAINT `conditions_rules_rule_id_fk` FOREIGN KEY (`condition_rule_id`) REFERENCES `rules` (`rule_id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conditions`
--

LOCK TABLES `conditions` WRITE;
/*!40000 ALTER TABLE `conditions` DISABLE KEYS */;
INSERT INTO `conditions` (`condition_record_id`, `condition_rule_id`, `condition_type`, `condition_check`, `condition_logic`, `condition_value`) VALUES (65,15,'time','none','>','04:00'),(66,15,'time','none','<=','23:00'),(69,16,'time','none','>','23:00'),(71,17,'time','none','<=','04:00'),(73,18,'time','none','>','04:00'),(74,18,'time','none','<=','23:00'),(75,15,'average','LDR','<=','3000'),(76,18,'average','LDR','>','3000'),(77,19,'time','none','>','04:00'),(78,19,'time','none','<=','23:00'),(83,20,'time','none','>','23:00'),(84,21,'time','none','<=','04:00');
/*!40000 ALTER TABLE `conditions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups_rooms_things`
--

DROP TABLE IF EXISTS `groups_rooms_things`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups_rooms_things` (
  `group_record_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) DEFAULT NULL,
  `info_id` int(11) DEFAULT NULL,
  `info_level` int(11) DEFAULT NULL,
  PRIMARY KEY (`group_record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups_rooms_things`
--

LOCK TABLES `groups_rooms_things` WRITE;
/*!40000 ALTER TABLE `groups_rooms_things` DISABLE KEYS */;
INSERT INTO `groups_rooms_things` (`group_record_id`, `group_id`, `info_id`, `info_level`) VALUES (4,1,1,3),(5,2,1,2),(6,3,2,3),(7,2,2,2);
/*!40000 ALTER TABLE `groups_rooms_things` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `home_groups`
--

DROP TABLE IF EXISTS `home_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `home_groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(100) DEFAULT NULL,
  `group_description` longtext NOT NULL,
  `info_level` int(11) DEFAULT NULL,
  `info_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `home_groups`
--

LOCK TABLES `home_groups` WRITE;
/*!40000 ALTER TABLE `home_groups` DISABLE KEYS */;
INSERT INTO `home_groups` (`group_id`, `group_name`, `group_description`, `info_level`, `info_id`) VALUES (1,'kitchen_things','All things related to the Kitchen',2,1),(2,'all_rooms','All Rooms related to the house',1,1),(3,'lab_things','All the things related to the Lab',2,2);
/*!40000 ALTER TABLE `home_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `home_rooms`
--

DROP TABLE IF EXISTS `home_rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `home_rooms` (
  `room_id` int(11) NOT NULL AUTO_INCREMENT,
  `room_name` varchar(100) DEFAULT NULL,
  `room_description` longtext,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `home_rooms`
--

LOCK TABLES `home_rooms` WRITE;
/*!40000 ALTER TABLE `home_rooms` DISABLE KEYS */;
INSERT INTO `home_rooms` (`room_id`, `room_name`, `room_description`) VALUES (1,'Kitchen','The room where we eat'),(2,'Lab','Where the magic happens');
/*!40000 ALTER TABLE `home_rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `home_things`
--

DROP TABLE IF EXISTS `home_things`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `home_things` (
  `thing_id` int(11) NOT NULL,
  `thing_level` int(11) NOT NULL,
  `thing_name` varchar(50) DEFAULT NULL,
  `thing_description` longtext,
  PRIMARY KEY (`thing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='IoT information';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `home_things`
--

LOCK TABLES `home_things` WRITE;
/*!40000 ALTER TABLE `home_things` DISABLE KEYS */;
INSERT INTO `home_things` (`thing_id`, `thing_level`, `thing_name`, `thing_description`) VALUES (1,2,'Kitchen1','Raspberry Pi Next to fridge'),(2,2,'Lab1','Raspberry Pi Next to front door');
/*!40000 ALTER TABLE `home_things` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hue_groups`
--

DROP TABLE IF EXISTS `hue_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hue_groups` (
  `group_id` text,
  `lights` text,
  `name` text,
  `state` text,
  `action` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hue_groups`
--

LOCK TABLES `hue_groups` WRITE;
/*!40000 ALTER TABLE `hue_groups` DISABLE KEYS */;
INSERT INTO `hue_groups` (`group_id`, `lights`, `name`, `state`, `action`) VALUES ('1','[\'4\', \'5\', \'6\', \'7\', \'8\', \'9\', \'10\', \'11\']','Kitchen','{\'all_on\': True, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 8402, \'sat\': 140, \'effect\': \'none\', \'xy\': [0.4575, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\'}'),('2','[\'13\', \'14\', \'15\', \'2\', \'3\']','Lab','{\'all_on\': False, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\'}'),('3','[\'1\', \'12\', \'18\', \'21\']','Hallway','{\'all_on\': False, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\'}'),('4','[\'23\', \'22\']','Guest Bedroom','{\'all_on\': True, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\'}'),('5','[\'26\', \'24\']','Master Bedroom','{\'all_on\': True, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\'}'),('7','[\'9\', \'10\', \'11\']','Kitchen_backlight','{\'all_on\': True, \'any_on\': True}','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\'}');
/*!40000 ALTER TABLE `hue_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hue_lights`
--

DROP TABLE IF EXISTS `hue_lights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hue_lights` (
  `light_id` text,
  `state` text,
  `name` text,
  `uniqueid` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hue_lights`
--

LOCK TABLES `hue_lights` WRITE;
/*!40000 ALTER TABLE `hue_lights` DISABLE KEYS */;
INSERT INTO `hue_lights` (`light_id`, `state`, `name`, `uniqueid`) VALUES ('1','{\'on\': False, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.2677, 0.2388], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 1','00:17:88:01:00:3f:b5:8e-0b'),('2','{\'on\': False, \'bri\': 77, \'hue\': 0, \'sat\': 0, \'effect\': \'none\', \'xy\': [0.4578, 0.41], \'ct\': 367, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 2','00:17:88:01:10:5a:b7:99-0b'),('3','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 3','00:17:88:01:10:41:14:a2-0b'),('4','{\'on\': True, \'bri\': 254, \'hue\': 14957, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4576, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color spot 1','00:17:88:01:00:f1:f7:74-0b'),('5','{\'on\': True, \'bri\': 254, \'hue\': 14957, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4576, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color spot 2','00:17:88:01:00:e8:09:c5-0b'),('6','{\'on\': True, \'bri\': 254, \'hue\': 14957, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4576, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color spot 3','00:17:88:01:00:f1:a2:5d-0b'),('7','{\'on\': True, \'bri\': 254, \'hue\': 14957, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4576, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color spot 4','00:17:88:01:00:f1:99:b0-0b'),('8','{\'on\': True, \'bri\': 254, \'hue\': 14957, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4576, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color spot 5','00:17:88:01:00:f1:b3:6c-0b'),('9','{\'on\': True, \'bri\': 254, \'hue\': 8402, \'sat\': 140, \'effect\': \'none\', \'xy\': [0.4575, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue lightstrip plus 1','00:17:88:01:01:1a:cc:80-0b'),('10','{\'on\': True, \'bri\': 254, \'hue\': 8402, \'sat\': 140, \'effect\': \'none\', \'xy\': [0.4575, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue lightstrip plus 2','00:17:88:01:01:1a:d1:b0-0b'),('11','{\'on\': True, \'bri\': 254, \'hue\': 8402, \'sat\': 140, \'effect\': \'none\', \'xy\': [0.4575, 0.4099], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue lightstrip plus 3','00:17:88:01:01:1a:d1:a6-0b'),('12','{\'on\': False, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.2677, 0.2388], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'xy\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 4','00:17:88:01:00:f7:11:bd-0b'),('13','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 5','00:17:88:01:00:f6:0a:f0-0b'),('14','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 6','00:17:88:01:00:f6:10:72-0b'),('15','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 7','00:17:88:01:10:26:90:18-0b'),('18','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 10','00:17:88:01:10:4b:6e:c5-0b'),('21','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 13','00:17:88:01:00:e2:d2:97-0b'),('22','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color lamp 14','00:17:88:01:00:ed:82:ec-0b'),('23','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': True}','Hue color lamp 15','00:17:88:01:00:ed:b9:be-0b'),('24','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 16','00:17:88:01:10:5d:3e:81-0b'),('26','{\'on\': True, \'bri\': 254, \'hue\': 14988, \'sat\': 141, \'effect\': \'none\', \'xy\': [0.4575, 0.4101], \'ct\': 366, \'alert\': \'none\', \'colormode\': \'ct\', \'mode\': \'homeautomation\', \'reachable\': False}','Hue color lamp 17','00:17:88:01:10:4b:91:e2-0b');
/*!40000 ALTER TABLE `hue_lights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `info_levels`
--

DROP TABLE IF EXISTS `info_levels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `info_levels` (
  `info_id` int(11) NOT NULL AUTO_INCREMENT,
  `info_level` int(11) NOT NULL,
  `info_description` longtext NOT NULL,
  PRIMARY KEY (`info_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `info_levels`
--

LOCK TABLES `info_levels` WRITE;
/*!40000 ALTER TABLE `info_levels` DISABLE KEYS */;
INSERT INTO `info_levels` (`info_id`, `info_level`, `info_description`) VALUES (1,1,'Home '),(2,2,'Room'),(3,3,'Thing');
/*!40000 ALTER TABLE `info_levels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mosquitto_channels`
--

DROP TABLE IF EXISTS `mosquitto_channels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mosquitto_channels` (
  `channel_id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_level` int(11) NOT NULL DEFAULT '0',
  `channel_name` varchar(50) NOT NULL,
  `channel_broadcast` text,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8 COMMENT='Define MQTT channel structure';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mosquitto_channels`
--

LOCK TABLES `mosquitto_channels` WRITE;
/*!40000 ALTER TABLE `mosquitto_channels` DISABLE KEYS */;
INSERT INTO `mosquitto_channels` (`channel_id`, `channel_level`, `channel_name`, `channel_broadcast`) VALUES (1,2,'room_commands','home/rooms/room_name/commands'),(2,2,'room_info','home/rooms/room_name/info'),(3,3,'thing_commands','home/rooms/room_name/things/thing_name/commands'),(4,1,'group_commands','home/groups/group_name/commands'),(9,3,'thing_info','home/rooms/room_name/things/thing_name/info'),(27,3,'thing_interrupt','home/rooms/room_name/things/thing_name/interrupt'),(28,1,'home_commands','home/commands'),(29,1,'home_info','home/info');
/*!40000 ALTER TABLE `mosquitto_channels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mosquitto_configuration`
--

DROP TABLE IF EXISTS `mosquitto_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mosquitto_configuration` (
  `mqtt_id` varchar(255) NOT NULL,
  `mqtt_value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`mqtt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='MQTT client and server configurations';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mosquitto_configuration`
--

LOCK TABLES `mosquitto_configuration` WRITE;
/*!40000 ALTER TABLE `mosquitto_configuration` DISABLE KEYS */;
INSERT INTO `mosquitto_configuration` (`mqtt_id`, `mqtt_value`) VALUES ('broker_address','192.168.50.173');
/*!40000 ALTER TABLE `mosquitto_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pins_configurations`
--

DROP TABLE IF EXISTS `pins_configurations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pins_configurations` (
  `pin_record_id` int(11) NOT NULL AUTO_INCREMENT,
  `thing_id` int(11) DEFAULT NULL,
  `pin_id` int(11) NOT NULL,
  `pin_type` varchar(50) NOT NULL,
  `pin_sensor` varchar(50) DEFAULT NULL,
  `pin_name` varchar(50) NOT NULL,
  `pin_up_down` varchar(10) DEFAULT 'none',
  `pin_interrupt_on` varchar(10) NOT NULL DEFAULT 'none',
  PRIMARY KEY (`pin_record_id`),
  KEY `pins_pin_types_type_name_fk` (`pin_type`),
  KEY `pins_sensor_types_sensor_type_name_fk` (`pin_sensor`),
  CONSTRAINT `pins_pin_types_type_name_fk` FOREIGN KEY (`pin_type`) REFERENCES `pins_types` (`pin_type`),
  CONSTRAINT `pins_sensor_types_sensor_type_name_fk` FOREIGN KEY (`pin_sensor`) REFERENCES `sensor_types` (`sensor_type`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8 COMMENT='Actively Used PINS on thing';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pins_configurations`
--

LOCK TABLES `pins_configurations` WRITE;
/*!40000 ALTER TABLE `pins_configurations` DISABLE KEYS */;
INSERT INTO `pins_configurations` (`pin_record_id`, `thing_id`, `pin_id`, `pin_type`, `pin_sensor`, `pin_name`, `pin_up_down`, `pin_interrupt_on`) VALUES (1,1,23,'input','motion','motion1','down','rising'),(2,1,19,'output','light','light1','none','none'),(3,1,24,'input','window','window1','none','none'),(13,1,26,'output','HVAC_fan','fan1','none','none'),(14,1,20,'output','HVAC_heat','heat1','none','none'),(15,1,21,'output','HVAC_cool','cool1','none','none'),(17,1,25,'dht','temp_humidity','temp1','none','none'),(18,1,0,'adc','LDR','LDR1','none','none'),(19,1,16,'input','motion','motion2','down','rising'),(22,2,24,'output','light','light2','none','none'),(23,2,23,'input','motion','motion2','down','rising'),(24,2,26,'input','door','door1','up','rising'),(27,2,0,'adc','LDR','LDR2','none','none'),(28,2,18,'output','fan','fan2','none','none');
/*!40000 ALTER TABLE `pins_configurations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pins_types`
--

DROP TABLE IF EXISTS `pins_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pins_types` (
  `pin_type` varchar(50) NOT NULL,
  PRIMARY KEY (`pin_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Actively used PIN types (Input | Output | adc)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pins_types`
--

LOCK TABLES `pins_types` WRITE;
/*!40000 ALTER TABLE `pins_types` DISABLE KEYS */;
INSERT INTO `pins_types` (`pin_type`) VALUES ('adc'),('dht'),('input'),('output');
/*!40000 ALTER TABLE `pins_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms_things`
--

DROP TABLE IF EXISTS `rooms_things`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rooms_things` (
  `rooms_record_id` int(11) NOT NULL AUTO_INCREMENT,
  `rooms_room_id` int(11) DEFAULT NULL,
  `rooms_thing_id` int(11) NOT NULL,
  PRIMARY KEY (`rooms_record_id`),
  KEY `rooms_things_home_things_thing_id_fk` (`rooms_thing_id`),
  CONSTRAINT `rooms_things_home_things_thing_id_fk` FOREIGN KEY (`rooms_thing_id`) REFERENCES `home_things` (`thing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms_things`
--

LOCK TABLES `rooms_things` WRITE;
/*!40000 ALTER TABLE `rooms_things` DISABLE KEYS */;
INSERT INTO `rooms_things` (`rooms_record_id`, `rooms_room_id`, `rooms_thing_id`) VALUES (1,1,1),(2,2,2);
/*!40000 ALTER TABLE `rooms_things` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rules`
--

DROP TABLE IF EXISTS `rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rules` (
  `rule_id` int(11) NOT NULL AUTO_INCREMENT,
  `info_id` int(11) DEFAULT NULL,
  `info_level` int(2) NOT NULL,
  `rule_name` varchar(255) NOT NULL,
  `rule_command` varchar(50) NOT NULL,
  `rule_timer` float NOT NULL DEFAULT '30',
  `rule_function` varchar(100) DEFAULT NULL,
  `rule_sensor` varchar(25) NOT NULL DEFAULT 'none',
  PRIMARY KEY (`rule_id`),
  KEY `rules_commands_command_name_fk` (`rule_command`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rules`
--

LOCK TABLES `rules` WRITE;
/*!40000 ALTER TABLE `rules` DISABLE KEYS */;
INSERT INTO `rules` (`rule_id`, `info_id`, `info_level`, `rule_name`, `rule_command`, `rule_timer`, `rule_function`, `rule_sensor`) VALUES (15,1,2,'Turn on lights if motion is detected','hue_lights_on',1800,'hue_lights_off','motion'),(16,1,2,'Dim lights if motion is detected at night','hue_lights_dim',1800,'hue_lights_off','motion'),(17,1,2,'Dim lights if motion is detected early morning','hue_lights_dim',1800,'hue_lights_off','motion'),(18,1,2,'Turn on backlights if motion is detected','hue_kitchen_backlight',1800,'hue_lights_off','motion'),(19,2,2,'Turn on lights if motion is detected','hue_on',1800,'hue_off','motion'),(20,2,2,'Dim lights if motion is detected at night','hue_dim',1800,'hue_off','motion'),(21,2,2,'Dim lights if motion is detected early morning','hue_dim',1800,'hue_off','motion');
/*!40000 ALTER TABLE `rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_types`
--

DROP TABLE IF EXISTS `sensor_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sensor_types` (
  `sensor_type` varchar(50) NOT NULL,
  PRIMARY KEY (`sensor_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Types of Available Sensors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_types`
--

LOCK TABLES `sensor_types` WRITE;
/*!40000 ALTER TABLE `sensor_types` DISABLE KEYS */;
INSERT INTO `sensor_types` (`sensor_type`) VALUES ('door'),('fan'),('HVAC_cool'),('HVAC_fan'),('HVAC_heat'),('LDR'),('light'),('motion'),('temp_humidity'),('time'),('window');
/*!40000 ALTER TABLE `sensor_types` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-12-19 17:15:49
