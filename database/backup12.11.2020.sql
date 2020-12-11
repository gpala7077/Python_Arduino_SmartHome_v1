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
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commands`
--

LOCK TABLES `commands` WRITE;
/*!40000 ALTER TABLE `commands` DISABLE KEYS */;
INSERT INTO `commands` (`command_record_id`, `info_level`, `info_id`, `command_type`, `command_sensor`, `command_name`, `command_value`) VALUES (1,3,1,'write','HVAC_cool','AC_off','1'),(2,3,1,'write','HVAC_cool','AC_on','0'),(4,2,1,'broadcast','group','lights_off','lights_off'),(5,2,1,'broadcast','group','lights_on','lights_on'),(6,2,1,'broadcast','group','status','status'),(7,3,1,'write','HVAC_fan','fan_off','1'),(8,3,1,'write','HVAC_fan','fan_on','0'),(9,3,1,'write','HVAC_heat','heat_off','1'),(10,3,1,'write','HVAC_heat','heat_on','0'),(11,2,1,'hue','group','hue_lights_dim','{\"bri\": 50, \"on\": true}'),(12,2,1,'hue','group','hue_lights_off','{\"on\": false}'),(13,2,1,'hue','group','hue_lights_on','{\"bri\": 255, \"on\": true}'),(14,3,1,'write','light','lights_off','1'),(15,3,1,'write','light','lights_on','0'),(17,3,1,'read','all','status','None'),(18,2,1,'broadcast','thing1','AC_off','AC_off'),(19,2,1,'broadcast','thing1','heat_on','heat_on'),(20,2,1,'broadcast','thing1','heat_off','heat_off'),(21,2,1,'broadcast','thing1','fan_off','fan_off'),(22,2,1,'broadcast','thing1','fan_on','fan_on'),(23,2,1,'broadcast','thing1','AC_on','AC_on'),(24,2,1,'app','room','get_room_status','25'),(25,2,1,'broadcast','room','status','status'),(26,2,1,'app','room','hue_lights_dim','11'),(27,2,1,'app','room','hue_lights_on','13'),(28,2,1,'app','room','hue_lights_off','12'),(29,2,1,'app','room','lights_on','5'),(30,2,1,'app','room','lights_off','4');
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
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conditions`
--

LOCK TABLES `conditions` WRITE;
/*!40000 ALTER TABLE `conditions` DISABLE KEYS */;
INSERT INTO `conditions` (`condition_record_id`, `condition_rule_id`, `condition_type`, `condition_check`, `condition_logic`, `condition_value`) VALUES (64,15,'average','LDR','<=','50000'),(65,15,'time','none','>','04:00'),(66,15,'time','none','<=','22:00');
/*!40000 ALTER TABLE `conditions` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `home_rooms`
--

LOCK TABLES `home_rooms` WRITE;
/*!40000 ALTER TABLE `home_rooms` DISABLE KEYS */;
INSERT INTO `home_rooms` (`room_id`, `room_name`, `room_description`) VALUES (1,'Kitchen','The room where we eat');
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
INSERT INTO `home_things` (`thing_id`, `thing_level`, `thing_name`, `thing_description`) VALUES (1,2,'Kitchen1','Raspberry Pi Next to fridge');
/*!40000 ALTER TABLE `home_things` ENABLE KEYS */;
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
INSERT INTO `mosquitto_configuration` (`mqtt_id`, `mqtt_value`) VALUES ('broker_address','192.168.50.90');
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8 COMMENT='Actively Used PINS on thing';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pins_configurations`
--

LOCK TABLES `pins_configurations` WRITE;
/*!40000 ALTER TABLE `pins_configurations` DISABLE KEYS */;
INSERT INTO `pins_configurations` (`pin_record_id`, `thing_id`, `pin_id`, `pin_type`, `pin_sensor`, `pin_name`, `pin_up_down`, `pin_interrupt_on`) VALUES (1,1,23,'input','motion','motion1','down','rising'),(2,1,19,'output','light','light1','none','none'),(3,1,24,'input','window','window1','none','none'),(4,1,1,'adc','LDR','LDR1','none','none'),(13,1,26,'output','HVAC_fan','fan1','none','none'),(14,1,20,'output','HVAC_heat','heat1','none','none'),(15,1,21,'output','HVAC_cool','cool1','none','none'),(17,1,25,'dht','temp_humidity','temp1','none','none');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms_things`
--

LOCK TABLES `rooms_things` WRITE;
/*!40000 ALTER TABLE `rooms_things` DISABLE KEYS */;
INSERT INTO `rooms_things` (`rooms_record_id`, `rooms_room_id`, `rooms_thing_id`) VALUES (1,1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rules`
--

LOCK TABLES `rules` WRITE;
/*!40000 ALTER TABLE `rules` DISABLE KEYS */;
INSERT INTO `rules` (`rule_id`, `info_id`, `info_level`, `rule_name`, `rule_command`, `rule_timer`, `rule_function`, `rule_sensor`) VALUES (15,1,2,'Turn on lights if motion is detected','hue_lights_on',1800,'hue_lights_off','motion');
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
INSERT INTO `sensor_types` (`sensor_type`) VALUES ('HVAC_cool'),('HVAC_fan'),('HVAC_heat'),('LDR'),('light'),('motion'),('temp_humidity'),('time'),('window');
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

-- Dump completed on 2020-12-11 17:03:44
