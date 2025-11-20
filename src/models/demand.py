"""交通需求（Demand）数据模型"""
import json
from typing import List, Tuple


class Demand:
    """
    交通需求类，管理OD需求对
    
    Attributes:
        od_pairs: OD对列表 [(起点, 终点, 需求量), ...]
    """
    
    def __init__(self):
        """初始化空需求"""
        self.od_pairs: List[Tuple[str, str, float]] = []
    
    def load_from_json(self, filepath: str) -> None:
        """
        从JSON文件加载需求数据
        
        Args:
            filepath: JSON文件路径
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 数据格式错误
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Demand file not found: {filepath}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {filepath}") from e
        
        # 加载OD对
        try:
            origins = data['from']
            destinations = data['to']
            amounts = data['amount']
            
            if not (len(origins) == len(destinations) == len(amounts)):
                raise ValueError("Length mismatch in demand data")
            
            self.od_pairs = []
            for origin, destination, amount in zip(origins, destinations, amounts):
                if amount < 0:
                    raise ValueError(f"Negative demand amount: {amount}")
                self.od_pairs.append((origin, destination, amount))
        
        except KeyError as e:
            raise ValueError(f"Missing required field in demand data: {e}") from e
    
    def get_od_pairs(self) -> List[Tuple[str, str, float]]:
        """
        获取所有OD对
        
        Returns:
            OD对列表 [(起点, 终点, 需求量), ...]
        """
        return self.od_pairs
    
    def get_total_demand(self) -> float:
        """
        获取总需求量
        
        Returns:
            总需求量
        """
        return sum(amount for _, _, amount in self.od_pairs)
    
    def __repr__(self) -> str:
        """字符串表示"""
        total = self.get_total_demand()
        return f"Demand(od_pairs={len(self.od_pairs)}, total={total:.1f})"

