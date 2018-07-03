import logging

# 配置日志文件
logger = logging.getLogger('time_line')

# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(thread)d %(funcName)s %(levelname)-8s: %(message)s')

# 文件日志
file_handler = logging.FileHandler("time_line.log")
file_handler.setFormatter(formatter)

# 为logger添加的日志处理器
logger.addHandler(file_handler)

# 指定日志的最低输出级别，默认为WARN级别
logger.setLevel(logging.INFO)