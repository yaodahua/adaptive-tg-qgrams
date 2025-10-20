"""
全局日志记录模块
功能: 提供统一的日志记录接口, 支持不同级别的日志输出
"""

import logging
import sys

from config_variables import LOGGING_LEVEL

# 设置matplotlib日志级别为WARNING, 避免过多调试信息
logging.getLogger("matplotlib").setLevel(logging.WARNING)


class GlobalLog:
    """全局日志记录类"""
    
    def __init__(self, logger_prefix: str, verbose: bool = True):
        """
        初始化日志记录器
        
        参数:
            logger_prefix: 日志记录器前缀
            verbose: 是否启用详细日志模式, 当verbose=False时, 级别低于INFO的日志将被忽略
        """
        self.logger = logging.getLogger(logger_prefix)
        self.verbose = verbose
        
        # 避免重复创建日志处理器
        if len(self.logger.handlers) == 0:
            self.logger = logging.getLogger(logger_prefix)
            self.logger.setLevel(level=LOGGING_LEVEL)

            # FIXME: 似乎不需要将日志流式传输到标准输出
            formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            ch.setLevel(level=logging.DEBUG)

            self.logger.addHandler(ch)

    def debug(self, message):
        """记录调试级别日志"""
        if self.verbose:
            self.logger.debug(message)

    def info(self, message):
        """记录信息级别日志"""
        self.logger.info(message)

    def warn(self, message):
        """记录警告级别日志"""
        self.logger.warn(message)

    def error(self, message):
        """记录错误级别日志"""
        self.logger.error(message)

    def critical(self, message):
        """记录严重级别日志"""
        self.logger.critical(message)
