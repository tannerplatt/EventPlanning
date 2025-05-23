-- MySQL dump 10.13  Distrib 9.2.0, for macos15 (x86_64)
--
-- Host: localhost    Database: event_manager
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Events`
--

DROP TABLE IF EXISTS `Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Events` (
  `EventID` int NOT NULL AUTO_INCREMENT,
  `UserID` int DEFAULT NULL,
  `VenueID` int DEFAULT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Description` text,
  `Theme` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`EventID`),
  KEY `UserID` (`UserID`),
  KEY `VenueID` (`VenueID`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`),
  CONSTRAINT `events_ibfk_2` FOREIGN KEY (`VenueID`) REFERENCES `Venues` (`VenueID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Events`
--

LOCK TABLES `Events` WRITE;
/*!40000 ALTER TABLE `Events` DISABLE KEYS */;
INSERT INTO `Events` VALUES (1,1,1,'Charity Gala','2025-05-10','Annual fundraising event.','Formal'),(2,2,2,'Beach Bonfire Night','2025-06-15','Relaxing night on the beach.','Casual'),(3,3,3,'Startup Pitch Fest','2025-07-20','Entrepreneurs pitch ideas.','Tech'),(4,4,1,'Test Event','2025-05-05','This is a test event','Formal');
/*!40000 ALTER TABLE `Events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Invites`
--

DROP TABLE IF EXISTS `Invites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Invites` (
  `InviteID` int NOT NULL AUTO_INCREMENT,
  `UserID` int DEFAULT NULL,
  `EventID` int DEFAULT NULL,
  `DateSent` date DEFAULT NULL,
  `Text` text,
  `RecipientStatus` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`InviteID`),
  KEY `UserID` (`UserID`),
  KEY `EventID` (`EventID`),
  CONSTRAINT `invites_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`),
  CONSTRAINT `invites_ibfk_2` FOREIGN KEY (`EventID`) REFERENCES `Events` (`EventID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Invites`
--

LOCK TABLES `Invites` WRITE;
/*!40000 ALTER TABLE `Invites` DISABLE KEYS */;
INSERT INTO `Invites` VALUES (1,2,1,'2025-04-01','Join us for the gala!','Attending'),(2,3,1,'2025-04-01','Hope you can make it!','Maybe'),(3,1,2,'2025-05-01','Bonfire party!','Declined'),(4,4,4,'2025-05-05','You\'re invited to Test Event','Accepted'),(6,2,4,'2025-05-05','You\'re invited to Test Event','Pending');
/*!40000 ALTER TABLE `Invites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Age` int DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Number` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'Alice Smith',25,'alice@example.com','123-456-7890'),(2,'Bob Johnson',30,'bob@example.com','987-654-3210'),(3,'Charlie Davis',22,'charlie@example.com','555-111-2222'),(4,'Brady Fisher',21,'bmf1418@gmail.com','3128486916');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Vendor_Event`
--

DROP TABLE IF EXISTS `Vendor_Event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Vendor_Event` (
  `VendorID` int NOT NULL,
  `EventID` int NOT NULL,
  `VendorCost` float DEFAULT NULL,
  PRIMARY KEY (`VendorID`,`EventID`),
  KEY `EventID` (`EventID`),
  CONSTRAINT `vendor_event_ibfk_1` FOREIGN KEY (`VendorID`) REFERENCES `Vendors` (`VendorID`),
  CONSTRAINT `vendor_event_ibfk_2` FOREIGN KEY (`EventID`) REFERENCES `Events` (`EventID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Vendor_Event`
--

LOCK TABLES `Vendor_Event` WRITE;
/*!40000 ALTER TABLE `Vendor_Event` DISABLE KEYS */;
INSERT INTO `Vendor_Event` VALUES (1,1,300),(2,1,500),(3,3,1000);
/*!40000 ALTER TABLE `Vendor_Event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Vendors`
--

DROP TABLE IF EXISTS `Vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Vendors` (
  `VendorID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `ServiceType` varchar(100) DEFAULT NULL,
  `Owner` varchar(100) DEFAULT NULL,
  `StaffCount` int DEFAULT NULL,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`VendorID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Vendors`
--

LOCK TABLES `Vendors` WRITE;
/*!40000 ALTER TABLE `Vendors` DISABLE KEYS */;
INSERT INTO `Vendors` VALUES (1,'Elite Catering','Catering','John Chef',15,'555-123-4567'),(2,'AV Pros','Audio/Visual','Mike Sound',10,'555-234-5678'),(3,'PhotoTime','Photography','Sarah Click',5,'555-345-6789'),(4,'Brew Hawg','Catering','Bob',10,'(123) 456-7890'),(5,'Brew Hawg','Catering','Bob',10,'(123) 456-7890');
/*!40000 ALTER TABLE `Vendors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Venues`
--

DROP TABLE IF EXISTS `Venues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Venues` (
  `VenueID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Location` varchar(100) DEFAULT NULL,
  `Capacity` int DEFAULT NULL,
  `Type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`VenueID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Venues`
--

LOCK TABLES `Venues` WRITE;
/*!40000 ALTER TABLE `Venues` DISABLE KEYS */;
INSERT INTO `Venues` VALUES (1,'Grand Hall','Newport Beach',300,'Indoor'),(2,'Oceanview Terrace','Laguna Beach',150,'Outdoor'),(3,'Rooftop Lounge','Irvine',200,'Rooftop');
/*!40000 ALTER TABLE `Venues` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-22 18:17:33
