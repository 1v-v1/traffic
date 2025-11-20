"""全有全无分配算法（All-or-Nothing Assignment）"""
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network
from models.demand import Demand
from .dijkstra import shortest_path, get_path_links
from utils.logger import setup_logger

logger = setup_logger(__name__)


def all_or_nothing_assignment(
    network: Network,
    demand: Demand
) -> Dict[str, float]:
    """
    全有全无分配算法
    
    对每个OD需求，基于当前路网状态计算最短路径，
    将全部需求量分配到最短路径上
    
    Args:
        network: 路网对象
        demand: 需求对象
    
    Returns:
        各路段流量字典 {link_id: flow}
    """
    logger.info("开始全有全无分配")
    
    # 初始化流量字典
    flows: Dict[str, float] = {link_id: 0.0 for link_id in network.links}
    
    # 统计成功和失败的OD对
    success_count = 0
    fail_count = 0
    
    # 对每个OD对进行分配
    for origin, destination, amount in demand.get_od_pairs():
        # 计算最短路径
        path, cost = shortest_path(network, origin, destination)
        
        if path is None:
            logger.warning(f"未找到路径: {origin} -> {destination}")
            fail_count += 1
            continue
        
        # 将需求分配到路径上的每条路段
        path_links = get_path_links(network, path)
        for link in path_links:
            link_id = link.get_id()
            flows[link_id] += amount
        
        success_count += 1
        logger.debug(f"分配 {origin}->{destination}: {amount:.1f} 到路径 {' -> '.join(path)}")
    
    logger.info(f"全有全无分配完成: 成功 {success_count} 个OD对, 失败 {fail_count} 个")
    
    return flows

