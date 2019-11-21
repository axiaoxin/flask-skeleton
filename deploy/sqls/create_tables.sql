-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';
-- +goose StatementEnd

CREATE TABLE `metric_set` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `appid` int(11) NOT NULL DEFAULT 0 COMMENT 'Appid',
  `uin` varchar(64) NOT NULL DEFAULT '' COMMENT 'Uin',
  `region` varchar(16) NOT NULL DEFAULT '' COMMENT '地域名称',
  `logset_id` int(11) NOT NULL DEFAULT 0 COMMENT '日志集ID',
  `logset_name` varchar(128) NOT NULL DEFAULT '' COMMENT '日志集名称',
  `logtopic_id` int(11) NOT NULL DEFAULT 0 COMMENT '日志主题ID',
  `logtopic_name` varchar(128) NOT NULL DEFAULT '' COMMENT '日志主题名称',
  `name` varchar(128) NOT NULL DEFAULT '' COMMENT '指标集名称',
  `calc_cycle` int(11) NOT NULL DEFAULT 0 COMMENT '计算周期（秒数）',
  `time_field` varchar(64) NOT NULL DEFAULT '' COMMENT '日志内容的时间字段',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `i_appid` (`appid`),
  INDEX `i_uin` (`uin`),
  INDEX `i_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指标集表';


CREATE TABLE `metric_item` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `metric_set_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '关联的指标集ID',
  `type` tinyint(4) NOT NULL DEFAULT 0 COMMENT '指标类型（1=普通指标，2=复合指标）',
  `field` varchar(64) NOT NULL DEFAULT '' COMMENT '日志原始字段名（复合指标为空）',
  `operating` varchar(128) NOT NULL DEFAULT '' COMMENT '操作符（复合指标整个存这里）',
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '指标名称',
  `desc` varchar(64) NOT NULL DEFAULT '' COMMENT '指标描述',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `i_metric_set_id` (`metric_set_id`),
  INDEX `i_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指标表';


CREATE TABLE `log_filter_rule` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `metric_set_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '关联的指标集ID',
  `relation` tinyint(4) NOT NULL DEFAULT 0 COMMENT '与或关系（1=与，2=或）',
  `field` varchar(64) NOT NULL DEFAULT '' COMMENT '日志原始字段名',
  `operating` varchar(8) NOT NULL DEFAULT '' COMMENT '操作符',
  `value` varchar(64) NOT NULL DEFAULT '' COMMENT '筛选值',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `i_metric_set_id` (`metric_set_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='日志筛选规则表';


CREATE TABLE `statistic_filter_rule` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `metric_item_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '关联的指标ID',
  `relation` tinyint(4) NOT NULL DEFAULT 0 COMMENT '与或关系（1=与，2=或）',
  `field` varchar(64) NOT NULL DEFAULT '' COMMENT '日志原始字段名',
  `operating` varchar(8) NOT NULL DEFAULT '' COMMENT '操作符',
  `value` varchar(64) NOT NULL DEFAULT '' COMMENT '筛选值',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `i_metric_item_id` (`metric_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='统计筛选规则表';

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';
-- +goose StatementEnd

DROP TABLE `metric_set`;
DROP TABLE `metric_item`;
DROP TABLE `log_filter_rule`;
DROP TABLE `statistic_filter_rule`;
