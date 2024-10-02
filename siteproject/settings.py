try:
    from .my_settings import *  # 모든 설정을 가져와 현재 네임스페이스에 적용
except ImportError:
    raise ImportError("Could not import settings from 'my_settings'. Ensure it exists and is readable.")