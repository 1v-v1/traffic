"""增量分配算法（Incremental Assignment）"""
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network
from models.demand import Demand
from .all_or_nothing import all_or_nothing_assignment
from utils.logger import setup_logger

logger = setup_logger(__name__)


def incremental_assignment(
    network: Network,
    demand: Demand,
    n_iterations: int = 4
) -> Dict[str, float]:
    """
    增量分配算法
    
    将需求分成N份，每次分配一份需求，使用全有全无方法，
    更新路段流量后重新计算行程时间
    
    Args:
        network: 路网对象
        demand: 需求对象
        n_iterations: 迭代次数（需求分割份数）
    
    Returns:
        各路段流量字典 {link_id: flow}
    """
    logger.info(f"开始增量分配，迭代次数: {n_iterations}")
    
    # 重置路网流量
    network.reset_flows()
    
    # 计算每次迭代的需求比例
    # 常用策略：40%, 30%, 20%, 10% 或均匀分配
    if n_iterations == 4:
        fractions = [0.4, 0.3, 0.2, 0.1]
    else:
        # 均匀分配
        fractions = [1.0 / n_iterations] * n_iterations
    
    # 累积流量
    total_flows: Dict[str, float] = {link_id: 0.0 for link_id in network.links}
    
    # 迭代分配
    for iteration, fraction in enumerate(fractions, 1):
        logger.info(f"增量分配迭代 {iteration}/{n_iterations}, 需求比例: {fraction*100:.1f}%")
        
        # 创建当前迭代的需求
        current_demand = Demand()
        for origin, destination, amount in demand.get_od_pairs():
            current_demand.od_pairs.append((origin, destination, amount * fraction))
        
        # 全有全无分配
        iteration_flows = all_or_nothing_assignment(network, current_demand)
        
        # 累加流量
        for link_id, flow in iteration_flows.items():
            total_flows[link_id] += flow
        
        # 更新路网流量（用于下一次迭代的最短路径计算）
        for link_id, flow in total_flows.items():
            network.links[link_id].update_flow(flow)
        
        # 记录当前路网总出行时间
        total_time = network.get_total_travel_time()
        logger.info(f"迭代 {iteration} 完成，当前总出行时间: {total_time:.2f}")
    
    logger.info("增量分配完成")
    
    return total_flows

