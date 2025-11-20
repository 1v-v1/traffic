"""评估指标计算"""
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network


def calculate_total_travel_time(network: Network) -> float:
    """
    计算路网总出行时间
    
    总出行时间 = Σ(flow × travel_time)
    
    Args:
        network: 路网对象
    
    Returns:
        总出行时间
    """
    return network.get_total_travel_time()


def calculate_relative_gap(
    network: Network,
    auxiliary_flows: Dict[str, float]
) -> float:
    """
    计算Frank-Wolfe算法的相对间隙
    
    相对间隙 = |Σ(x_a * t_a(x)) - Σ(y_a * t_a(x))| / Σ(x_a * t_a(x))
    
    其中：
    - x_a: 当前流量
    - y_a: 辅助流量（全有全无分配结果）
    - t_a(x): 基于当前流量的行程时间
    
    Args:
        network: 路网对象（包含当前流量）
        auxiliary_flows: 辅助流量字典 {link_id: flow}
    
    Returns:
        相对间隙（0到1之间的值）
    """
    # 计算分子和分母
    numerator = 0.0  # Σ(x_a * t_a(x))
    denominator = 0.0  # Σ(y_a * t_a(x))
    
    for link_id, link in network.links.items():
        # 基于当前流量计算行程时间
        travel_time = link.get_travel_time()
        
        # 当前流量的贡献
        numerator += link.flow * travel_time
        
        # 辅助流量的贡献
        auxiliary_flow = auxiliary_flows.get(link_id, 0.0)
        denominator += auxiliary_flow * travel_time
    
    # 避免除零
    if numerator < 1e-10:
        return 0.0
    
    # 相对间隙
    relative_gap = abs(numerator - denominator) / numerator
    
    return relative_gap


def calculate_link_performance(network: Network) -> Dict[str, Dict[str, float]]:
    """
    计算各路段的性能指标
    
    Args:
        network: 路网对象
    
    Returns:
        路段性能字典 {link_id: {'flow': x, 'capacity': c, 'ratio': x/c, 'travel_time': t}}
    """
    performance = {}
    
    for link_id, link in network.links.items():
        ratio = link.flow / link.capacity if link.capacity > 0 else 0.0
        performance[link_id] = {
            'flow': link.flow,
            'capacity': link.capacity,
            'ratio': ratio,
            'travel_time': link.get_travel_time(),
            'free_flow_time': link.get_free_flow_time()
        }
    
    return performance

