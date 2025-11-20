"""路段（Link）数据模型"""
from typing import Optional


class Link:
    """
    路段类，封装路段属性和BPR行程时间函数
    
    Attributes:
        from_node: 起点节点
        to_node: 终点节点
        length: 路段长度
        capacity: 路段通行能力
        speed_max: 最大速度（限速）
        flow: 当前流量
    """
    
    def __init__(
        self,
        from_node: str,
        to_node: str,
        length: float,
        capacity: int,
        speed_max: int,
        flow: float = 0
    ):
        """
        初始化路段
        
        Args:
            from_node: 起点节点名称
            to_node: 终点节点名称
            length: 路段长度
            capacity: 路段通行能力（cap）
            speed_max: 最大速度/限速（spd）
            flow: 初始流量，默认为0
        """
        self.from_node = from_node
        self.to_node = to_node
        self.length = length
        self.capacity = capacity
        self.speed_max = speed_max
        self.flow = flow
    
    def get_free_flow_time(self) -> float:
        """
        计算自由流行程时间 t0
        
        t0 = length / speed_max
        
        Returns:
            自由流行程时间
        """
        return self.length / self.speed_max
    
    def get_travel_time(self, flow: Optional[float] = None) -> float:
        """
        计算行程时间（BPR函数）
        
        t(q) = t0 * (1 + q/cap)^2
        
        Args:
            flow: 流量，如果为None则使用当前流量
        
        Returns:
            行程时间
        """
        if flow is None:
            flow = self.flow
        
        t0 = self.get_free_flow_time()
        congestion_factor = (1 + flow / self.capacity) ** 2
        return t0 * congestion_factor
    
    def update_flow(self, flow: float) -> None:
        """
        更新路段流量
        
        Args:
            flow: 新的流量值
        """
        self.flow = flow
    
    def get_id(self) -> str:
        """
        获取路段标识符
        
        Returns:
            路段ID（格式：起点+终点，如'AB'）
        """
        return f"{self.from_node}{self.to_node}"
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (f"Link({self.from_node}->{self.to_node}, "
                f"length={self.length:.1f}, "
                f"cap={self.capacity}, "
                f"spd={self.speed_max}, "
                f"flow={self.flow:.1f})")

