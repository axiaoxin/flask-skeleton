-- 创建数据库 zhiyun_notifer
CREATE DATABASE IF NOT EXISTS zhiyun_notifer;

USE zhiyun_notifer;

-- 创建message表
CREATE TABLE `message` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `message_id` CHAR(32) NOT NULL COMMENT 'MD5 message_id',
  `send_status` TINYINT NOT NULL DEFAULT 0 COMMENT '发送状态：0等待发送，1发送成功，2发送失败',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '是否删除: 0未删除, 1已删除',
  `created_at` DATETIME NOT NULL DEFAULT NOW() COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW() COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uidx_message_id` (`message_id`)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8
COMMENT = '消息表';
