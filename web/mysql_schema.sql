-- ==============================================================
-- SupeRR Selector - Rajasthan Royals Hackathon
-- MySQL Database Schema and Setup Script
-- ==============================================================

CREATE DATABASE IF NOT EXISTS `superr_selector_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `superr_selector_db`;

-- --------------------------------------------------------------
-- Table structure for table `batter_rankings`
-- --------------------------------------------------------------
DROP TABLE IF EXISTS `batter_rankings`;
CREATE TABLE `batter_rankings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `striker_id` int NOT NULL,
  `striker_name` varchar(150) NOT NULL,
  `season_category` varchar(50) NOT NULL,
  `is_ipl_eligible` tinyint(1) NOT NULL DEFAULT '1',
  `rank` int NOT NULL,
  `balls_press` int NOT NULL,
  `runs_press` int NOT NULL,
  `sr_press` double NOT NULL,
  `avg_press` double NOT NULL,
  `delta_sr` double NOT NULL,
  `boundary_pct_press` double NOT NULL,
  `dot_pct_press` double NOT NULL DEFAULT '0',
  `rsaa_bat_per_100` double NOT NULL DEFAULT '0',
  `impact_rate` double NOT NULL DEFAULT '0',
  `pri_bat_score` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_bat_season_eligible` (`season_category`, `is_ipl_eligible`),
  KEY `idx_bat_rank` (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------
-- Table structure for table `bowler_rankings`
-- --------------------------------------------------------------
DROP TABLE IF EXISTS `bowler_rankings`;
CREATE TABLE `bowler_rankings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bowler_id` int NOT NULL,
  `bowler_name` varchar(150) NOT NULL,
  `season_category` varchar(50) NOT NULL,
  `is_ipl_eligible` tinyint(1) NOT NULL DEFAULT '1',
  `rank` int NOT NULL,
  `balls_press` int NOT NULL,
  `wickets_press` int NOT NULL,
  `econ_press` double NOT NULL,
  `sr_press` double NOT NULL,
  `dot_pct_press` double NOT NULL DEFAULT '0',
  `boundary_pct_press` double NOT NULL DEFAULT '0',
  `runs_saved_per_6` double NOT NULL DEFAULT '0',
  `impact_rate` double NOT NULL DEFAULT '0',
  `pri_bowl_score` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_bowl_season_eligible` (`season_category`, `is_ipl_eligible`),
  KEY `idx_bowl_rank` (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------
-- Table structure for table `matches_summary`
-- --------------------------------------------------------------
DROP TABLE IF EXISTS `matches_summary`;
CREATE TABLE `matches_summary` (
  `match_id` int NOT NULL,
  `comp_id` int NOT NULL,
  `comp_name` varchar(200) NOT NULL,
  `match_date` varchar(50) NOT NULL,
  `stage` varchar(100) NOT NULL,
  `home_team` varchar(100) NOT NULL,
  `away_team` varchar(100) NOT NULL,
  `result` varchar(250) NOT NULL,
  `knock_out` tinyint(1) NOT NULL DEFAULT '0',
  `is_ipl` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`match_id`),
  KEY `idx_match_date` (`match_date`),
  KEY `idx_match_format` (`is_ipl`, `knock_out`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

