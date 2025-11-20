"""Frank-Wolfe用户均衡分配算法"""
from typing import Dict, List, Tuple
import sys
import os
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network
from models.demand import Demand
from .all_or_nothing import all_or_nothing_assignment
from evaluation.metrics import calculate_relative_gap, calculate_total_travel_time
from utils.logger import setup_logger

logger = setup_logger(__name__)


def frank_wolfe_assignment(
    network: Network,
    demand: Demand,
    max_iter: int = 100,
    epsilon: float = 0.001
) -> Tuple[Dict[str, float], List[Dict]]:
    """
    Frank-Wolfe用户均衡分配算法
    
    迭代过程：
    1. 初始化：全有全无分配得到初始流量
    2. 迭代：
       a. 基于当前流量计算最短路径
       b. 全有全无分配得到辅助流量y
       c. 线搜索：找最优步长α
       d. 更新流量：x_new = x_old + α(y - x_old)
       e. 检查收敛：相对间隙 < 阈值
    
    Args:
        network: 路网对象
        demand: 需求对象
        max_iter: 最大迭代次数
        epsilon: 收敛阈值（相对间隙）
    
    Returns:
        (各路段流量字典, 收敛历史记录列表)
    """
    logger.info(f"开始Frank-Wolfe分配，最大迭代: {max_iter}, 收敛阈值: {epsilon}")
    
    # 步骤1: 初始化 - 全有全无分配
    network.reset_flows()
    initial_flows = all_or_nothing_assignment(network, demand)
    
    # 更新路网流量
    for link_id, flow in initial_flows.items():
        network.links[link_id].update_flow(flow)
    
    current_flows = copy.deepcopy(initial_flows)
    
    # 收敛历史
    history = []
    
    # 迭代
    for iteration in range(1, max_iter + 1):
        logger.info(f"Frank-Wolfe 迭代 {iteration}/{max_iter}")
        
        # 步骤2a: 基于当前流量，全有全无分配得到辅助流量
        auxiliary_flows = all_or_nothing_assignment(network, demand)
        
        # 步骤2b: 计算相对间隙
        relative_gap = calculate_relative_gap(network, auxiliary_flows)
        
        # 计算当前总出行时间
        total_time = calculate_total_travel_time(network)
        
        # 记录历史
        history.append({
            'iteration': iteration,
            'relative_gap': relative_gap,
            'total_travel_time': total_time
        })
        
        logger.info(f"迭代 {iteration}: 相对间隙={relative_gap:.6f}, 总出行时间={total_time:.2f}")
        
        # 步骤2e: 检查收敛
        if relative_gap < epsilon:
            logger.info(f"算法收敛！相对间隙 {relative_gap:.6f} < {epsilon}")
            break
        
        # 步骤2c: 线搜索找最优步长α
        alpha = line_search(network, current_flows, auxiliary_flows)
        
        logger.debug(f"线搜索步长: α={alpha:.6f}")
        
        # 步骤2d: 更新流量
        for link_id in network.links:
            old_flow = current_flows.get(link_id, 0.0)
            aux_flow = auxiliary_flows.get(link_id, 0.0)
            new_flow = old_flow + alpha * (aux_flow - old_flow)
            
            current_flows[link_id] = new_flow
            network.links[link_id].update_flow(new_flow)
    
    logger.info("Frank-Wolfe分配完成")
    
    return current_flows, history


def line_search(
    network: Network,
    current_flows: Dict[str, float],
    auxiliary_flows: Dict[str, float],
    n_samples: int = 20
) -> float:
    """
    线搜索找最优步长α
    
    寻找使目标函数最小的α ∈ [0, 1]
    目标函数: Z(α) = Σ ∫[0 to x_a(α)] t_a(w) dw
    
    近似方法：在[0, 1]之间采样，选择使总出行时间最小的α
    
    Args:
        network: 路网对象
        current_flows: 当前流量字典
        auxiliary_flows: 辅助流量字典
        n_samples: 采样点数量
    
    Returns:
        最优步长α
    """
    best_alpha = 0.0
    best_objective = float('inf')
    
    # 在[0, 1]之间采样
    alphas = [i / n_samples for i in range(n_samples + 1)]
    
    for alpha in alphas:
        # 计算该α下的流量
        test_flows = {}
        for link_id in network.links:
            old_flow = current_flows.get(link_id, 0.0)
            aux_flow = auxiliary_flows.get(link_id, 0.0)
            test_flows[link_id] = old_flow + alpha * (aux_flow - old_flow)
        
        # 计算目标函数值（近似为总出行时间）
        objective = calculate_objective(network, test_flows)
        
        if objective < best_objective:
            best_objective = objective
            best_alpha = alpha
    
    return best_alpha


def calculate_objective(
    network: Network,
    flows: Dict[str, float]
) -> float:
    """
    计算目标函数值
    
    目标函数: Z = Σ ∫[0 to x_a] t_a(w) dw
    
    对于BPR函数 t(x) = t0 * (1 + x/cap)^2
    积分结果: ∫ t(x) dx = t0 * [x + x^2/(2*cap) + x^3/(3*cap^2)]
    
    简化计算：使用 Z ≈ Σ x_a * t_a(x_a)
    
    Args:
        network: 路网对象
        flows: 流量字典
    
    Returns:
        目标函数值
    """
    objective = 0.0
    
    for link_id, link in network.links.items():
        flow = flows.get(link_id, 0.0)
        if flow > 0:
            # 计算该流量下的行程时间
            travel_time = link.get_travel_time(flow)
            
            # BPR积分的精确计算
            t0 = link.get_free_flow_time()
            cap = link.capacity
            
            # ∫[0 to x] t0*(1+w/cap)^2 dw = t0*[w + w^2/(2*cap) + w^3/(3*cap^2)]
            integral = t0 * (
                flow +
                flow**2 / (2 * cap) +
                flow**3 / (3 * cap**2)
            )
            
            objective += integral
    
    return objective

