"""路网（Network）数据模型"""
import json
import math
from typing import Dict, List, Optional, Tuple
from .link import Link


class Network:
    """
    路网类，管理节点和路段
    
    Attributes:
        nodes: 节点字典 {节点名: (x坐标, y坐标)}
        links: 路段字典 {路段ID: Link对象}
        adjacency: 邻接表 {节点名: [(邻居节点, 路段ID), ...]}
    """
    
    def __init__(self):
        """初始化空路网"""
        self.nodes: Dict[str, Tuple[float, float]] = {}
        self.links: Dict[str, Link] = {}
        self.adjacency: Dict[str, List[Tuple[str, str]]] = {}
    
    def load_from_json(self, filepath: str) -> None:
        """
        从JSON文件加载路网数据
        
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
            raise FileNotFoundError(f"Network file not found: {filepath}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {filepath}") from e
        
        # 加载节点
        try:
            node_names = data['nodes']['name']
            node_x = data['nodes']['x']
            node_y = data['nodes']['y']
            
            for name, x, y in zip(node_names, node_x, node_y):
                self.nodes[name] = (x, y)
                self.adjacency[name] = []
        except KeyError as e:
            raise ValueError(f"Missing required field in network data: {e}") from e
        
        # 加载路段
        try:
            link_betweens = data['links']['between']
            link_capacities = data['links']['capacity']
            link_speedmax = data['links']['speedmax']
            
            for between, capacity, speed_max in zip(link_betweens, link_capacities, link_speedmax):
                if len(between) < 2:
                    raise ValueError(f"Invalid link format: {between}")
                
                from_node = between[0]
                to_node = between[1]
                
                # 计算路段长度
                length = self._calculate_distance(from_node, to_node)
                
                # 创建路段对象
                link = Link(
                    from_node=from_node,
                    to_node=to_node,
                    length=length,
                    capacity=capacity,
                    speed_max=speed_max,
                    flow=0
                )
                
                link_id = link.get_id()
                self.links[link_id] = link
                
                # 更新邻接表
                self.adjacency[from_node].append((to_node, link_id))
        
        except KeyError as e:
            raise ValueError(f"Missing required field in link data: {e}") from e
    
    def _calculate_distance(self, from_node: str, to_node: str) -> float:
        """
        计算两节点之间的欧几里得距离
        
        Args:
            from_node: 起点节点名称
            to_node: 终点节点名称
        
        Returns:
            距离
        
        Raises:
            KeyError: 节点不存在
        """
        if from_node not in self.nodes:
            raise KeyError(f"Node not found: {from_node}")
        if to_node not in self.nodes:
            raise KeyError(f"Node not found: {to_node}")
        
        x1, y1 = self.nodes[from_node]
        x2, y2 = self.nodes[to_node]
        
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance
    
    def get_link(self, from_node: str, to_node: str) -> Optional[Link]:
        """
        获取指定的路段
        
        Args:
            from_node: 起点节点
            to_node: 终点节点
        
        Returns:
            Link对象，如果不存在则返回None
        """
        link_id = f"{from_node}{to_node}"
        return self.links.get(link_id)
    
    def get_all_links(self) -> List[Link]:
        """
        获取所有路段
        
        Returns:
            Link对象列表
        """
        return list(self.links.values())
    
    def reset_flows(self) -> None:
        """重置所有路段的流量为0"""
        for link in self.links.values():
            link.update_flow(0)
    
    def get_total_travel_time(self) -> float:
        """
        计算路网总出行时间
        
        总出行时间 = Σ(flow × travel_time)
        
        Returns:
            总出行时间
        """
        total_time = 0.0
        for link in self.links.values():
            if link.flow > 0:
                travel_time = link.get_travel_time()
                total_time += link.flow * travel_time
        return total_time
    
    def get_neighbors(self, node: str) -> List[Tuple[str, str]]:
        """
        获取节点的邻居节点
        
        Args:
            node: 节点名称
        
        Returns:
            邻居列表 [(邻居节点, 路段ID), ...]
        """
        return self.adjacency.get(node, [])
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Network(nodes={len(self.nodes)}, links={len(self.links)})"

