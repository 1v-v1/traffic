"""Dijkstra最短路径算法"""
import heapq
from typing import List, Optional, Tuple, Dict
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network
from models.link import Link


def shortest_path(
    network: Network,
    origin: str,
    destination: str
) -> Tuple[Optional[List[str]], float]:
    """
    使用Dijkstra算法计算最短路径
    
    基于当前路段流量计算的travel_time作为权重
    
    Args:
        network: 路网对象
        origin: 起点节点
        destination: 终点节点
    
    Returns:
        (路径节点列表, 总时间)
        如果路径不存在，返回(None, inf)
        如果起点==终点，返回([起点], 0)
    """
    # 起点等于终点
    if origin == destination:
        return ([origin], 0.0)
    
    # 检查节点是否存在
    if origin not in network.nodes or destination not in network.nodes:
        return (None, float('inf'))
    
    # 初始化
    distances: Dict[str, float] = {node: float('inf') for node in network.nodes}
    distances[origin] = 0.0
    
    previous: Dict[str, Optional[str]] = {node: None for node in network.nodes}
    
    # 优先队列：(距离, 节点)
    pq = [(0.0, origin)]
    visited = set()
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        # 已访问过，跳过
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # 到达目标节点
        if current_node == destination:
            break
        
        # 当前距离已不是最优，跳过
        if current_dist > distances[current_node]:
            continue
        
        # 遍历邻居节点
        for neighbor, link_id in network.get_neighbors(current_node):
            if neighbor in visited:
                continue
            
            link = network.links[link_id]
            # 使用当前流量计算行程时间作为权重
            travel_time = link.get_travel_time()
            new_dist = current_dist + travel_time
            
            # 找到更短路径
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
    
    # 重建路径
    if distances[destination] == float('inf'):
        # 路径不存在
        return (None, float('inf'))
    
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    
    return (path, distances[destination])


def get_path_links(network: Network, path: List[str]) -> List[Link]:
    """
    将节点路径转换为路段列表
    
    Args:
        network: 路网对象
        path: 节点路径列表
    
    Returns:
        路段对象列表
    """
    links = []
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]
        link = network.get_link(from_node, to_node)
        if link:
            links.append(link)
    return links

