/*
 Navicat Premium Data Transfer

 Source Server         : ao-test
 Source Server Type    : MySQL
 Source Server Version : 90001
 Source Host           : 45.120.216.242:3306
 Source Schema         : ao

 Target Server Type    : MySQL
 Target Server Version : 90001
 File Encoding         : 65001

 Date: 10/08/2024 21:28:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for llama_war_exchange
-- ----------------------------
DROP TABLE IF EXISTS `llama_war_exchange`;
CREATE TABLE `llama_war_exchange`  (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `player_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `x_amount` bigint(0) NULL DEFAULT NULL,
  `y_amount` bigint(0) NULL DEFAULT NULL,
  `created_time` datetime(0) NOT NULL,
  `sell_flag` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_l_w_ctime`(`created_time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for trunk_war_exchange
-- ----------------------------
DROP TABLE IF EXISTS `trunk_war_exchange`;
CREATE TABLE `trunk_war_exchange`  (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `player_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `x_amount` bigint(0) NULL DEFAULT NULL,
  `y_amount` bigint(0) NULL DEFAULT NULL,
  `created_time` datetime(0) NOT NULL,
  `sell_flag` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_l_t_ctime`(`created_time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
