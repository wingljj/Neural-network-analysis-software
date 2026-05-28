"""业务异常定义。"""


class NNQtError(Exception):
    """应用业务异常基类。"""


class DataValidationError(NNQtError):
    """数据校验失败。"""


class ModelPackageError(NNQtError):
    """模型包加载或格式错误。"""
