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

 Date: 10/08/2024 21:28:09
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for exchange_price_config
-- ----------------------------
DROP TABLE IF EXISTS `exchange_price_config`;
CREATE TABLE `exchange_price_config`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT 'PK',
  `code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '{token1}_{token2}_exchange',
  `process_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '交易对的ao process的id',
  `token_x` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主交易货币：llama',
  `token_x_pid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主交易货币的 token process 的 id',
  `token_y` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '被锚定交易对的货币：wAR',
  `ratio` int(0) NOT NULL COMMENT '为了显示的转化比例',
  `dimension_x` int(0) NOT NULL COMMENT 'token_x有几位小数，比如12位',
  `dimension_y` int(0) NOT NULL COMMENT 'token_y的小数位数',
  `del_flag` tinyint(1) NOT NULL DEFAULT 0 COMMENT '软删',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of exchange_price_config
-- ----------------------------
INSERT INTO `exchange_price_config` VALUES (1, 'llama_war_exchange', 'aGF7BWB_9B924sBXoirHy4KOceoCX72B77yh1nllMPA', 'llama', 'pazXumQI-HPH7iFGfTC-4_7biSnqz_U67oFAGry5zUY', 'wAR', 1000, 12, 12, 0);
INSERT INTO `exchange_price_config` VALUES (2, 'trunk_war_exchange', 'ii73EP8PXGTvfn6xIEDrnRhqBI8_JEfCVmsXKMHNwXw', 'trunk', 'OT9qTE2467gcozb2g8R6D6N3nQS94ENcaAIJfUzHCww', 'wAR', 1, 3, 12, 0);

SET FOREIGN_KEY_CHECKS = 1;
