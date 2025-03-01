-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 01, 2025 at 06:39 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `skripsi_original_dari_bapak`
--

-- --------------------------------------------------------

--
-- Table structure for table `grobid_references`
--

CREATE TABLE `grobid_references` (
  `article_id` bigint(20) NOT NULL,
  `journal_id` bigint(20) NOT NULL,
  `location_file` mediumtext NOT NULL,
  `pdf_downloaded` tinyint(4) NOT NULL DEFAULT 0 COMMENT '-2: unknown error, -1: not found, 0: not yet, 1: yes',
  `pdf_processed` tinyint(4) NOT NULL DEFAULT 0 COMMENT '-2: unknown error, -1: grobid error, 0: not yet, 1: yes',
  `log` text DEFAULT NULL,
  `last_activity` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `grobid_references`
--
ALTER TABLE `grobid_references`
  ADD PRIMARY KEY (`article_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
