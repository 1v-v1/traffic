"""交通分配系统主程序"""
import os
import sys
import time
import logging

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.network import Network
from models.demand import Demand
from algorithms.all_or_nothing import all_or_nothing_assignment
from algorithms.incremental import incremental_assignment
from algorithms.frank_wolfe import frank_wolfe_assignment
from evaluation.metrics import calculate_total_travel_time, calculate_link_performance
from visualization.plotter import (
    plot_network,
    plot_flow_assignment,
    plot_convergence,
    plot_comparison,
    plot_flow_difference
)
from utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger("traffic_assignment", level=logging.INFO)
    
    logger.info("=" * 60)
    logger.info("交通分配系统 - Traffic Assignment System")
    logger.info("=" * 60)
    
    # 数据文件路径
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    network_file = os.path.join(data_dir, 'network.json')
    demand_file = os.path.join(data_dir, 'demand.json')
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # ========== 1. 加载数据 ==========
        logger.info("\n[步骤1] 加载数据...")
        
        network = Network()
        network.load_from_json(network_file)
        logger.info(f"  路网加载成功: {network}")
        
        demand = Demand()
        demand.load_from_json(demand_file)
        logger.info(f"  需求加载成功: {demand}")
        
        # 可视化原始路网
        logger.info("  生成路网结构图...")
        plot_network(
            network,
            title="交通路网结构 (Traffic Network)",
            save_path=os.path.join(output_dir, '01_network.png'),
            show=False
        )
        
        # ========== 2. 全有全无分配 ==========
        logger.info("\n[步骤2] 执行全有全无分配...")
        start_time = time.time()
        
        network.reset_flows()
        aon_flows = all_or_nothing_assignment(network, demand)
        
        # 更新路网流量
        for link_id, flow in aon_flows.items():
            network.links[link_id].update_flow(flow)
        
        aon_time = calculate_total_travel_time(network)
        aon_duration = time.time() - start_time
        
        logger.info(f"  全有全无分配完成:")
        logger.info(f"    总出行时间: {aon_time:.2f}")
        logger.info(f"    执行时间: {aon_duration:.3f}秒")
        
        # 可视化全有全无分配结果
        plot_flow_assignment(
            network,
            title="全有全无分配结果 (All-or-Nothing)",
            save_path=os.path.join(output_dir, '02_all_or_nothing.png'),
            show=False
        )
        
        # ========== 3. 增量分配 ==========
        logger.info("\n[步骤3] 执行增量分配...")
        start_time = time.time()
        
        network.reset_flows()
        inc_flows = incremental_assignment(network, demand, n_iterations=4)
        
        # 更新路网流量
        for link_id, flow in inc_flows.items():
            network.links[link_id].update_flow(flow)
        
        inc_time = calculate_total_travel_time(network)
        inc_duration = time.time() - start_time
        
        logger.info(f"  增量分配完成:")
        logger.info(f"    总出行时间: {inc_time:.2f}")
        logger.info(f"    执行时间: {inc_duration:.3f}秒")
        
        # 可视化增量分配结果
        plot_flow_assignment(
            network,
            title="增量分配结果 (Incremental)",
            save_path=os.path.join(output_dir, '03_incremental.png'),
            show=False
        )
        
        # ========== 4. Frank-Wolfe用户均衡分配 ==========
        logger.info("\n[步骤4] 执行Frank-Wolfe用户均衡分配...")
        start_time = time.time()
        
        network.reset_flows()
        fw_flows, fw_history = frank_wolfe_assignment(
            network,
            demand,
            max_iter=50,
            epsilon=0.001
        )
        
        # 更新路网流量
        for link_id, flow in fw_flows.items():
            network.links[link_id].update_flow(flow)
        
        fw_time = calculate_total_travel_time(network)
        fw_duration = time.time() - start_time
        
        logger.info(f"  Frank-Wolfe分配完成:")
        logger.info(f"    总出行时间: {fw_time:.2f}")
        logger.info(f"    迭代次数: {len(fw_history)}")
        logger.info(f"    最终相对间隙: {fw_history[-1]['relative_gap']:.6f}")
        logger.info(f"    执行时间: {fw_duration:.3f}秒")
        
        # 可视化Frank-Wolfe分配结果
        plot_flow_assignment(
            network,
            title="Frank-Wolfe用户均衡分配结果 (User Equilibrium)",
            save_path=os.path.join(output_dir, '04_frank_wolfe.png'),
            show=False
        )
        
        # 可视化收敛曲线
        plot_convergence(
            fw_history,
            title="Frank-Wolfe收敛曲线",
            save_path=os.path.join(output_dir, '05_convergence.png'),
            show=False
        )
        
        # ========== 5. 结果对比 ==========
        logger.info("\n[步骤5] 算法结果对比...")
        
        results = {
            '全有全无分配': aon_time,
            '增量分配': inc_time,
            'Frank-Wolfe': fw_time
        }
        
        plot_comparison(
            results,
            title="交通分配算法对比 (总出行时间)",
            save_path=os.path.join(output_dir, '06_comparison.png'),
            show=False
        )
        
        # 绘制增量分配与Frank-Wolfe的流量差异
        logger.info("  生成增量分配与Frank-Wolfe流量差异图...")
        
        # 使用两个独立的网络对象保存流量状态
        network_inc_copy = Network()
        network_inc_copy.load_from_json(network_file)
        for link_id, flow in inc_flows.items():
            network_inc_copy.links[link_id].update_flow(flow)
        
        network_fw_copy = Network()
        network_fw_copy.load_from_json(network_file)
        for link_id, flow in fw_flows.items():
            network_fw_copy.links[link_id].update_flow(flow)
        
        plot_flow_difference(
            network_inc_copy,
            network_fw_copy,
            label1="增量分配",
            label2="Frank-Wolfe",
            title="增量分配 vs Frank-Wolfe 流量差异对比",
            save_path=os.path.join(output_dir, '07_flow_difference.png'),
            show=False
        )
        
        # 打印详细对比
        logger.info("\n" + "=" * 60)
        logger.info("算法对比结果:")
        logger.info("-" * 60)
        logger.info(f"{'算法':<20} {'总出行时间':<15} {'执行时间(秒)':<15}")
        logger.info("-" * 60)
        logger.info(f"{'全有全无分配':<20} {aon_time:<15.2f} {aon_duration:<15.3f}")
        logger.info(f"{'增量分配':<20} {inc_time:<15.2f} {inc_duration:<15.3f}")
        logger.info(f"{'Frank-Wolfe':<20} {fw_time:<15.2f} {fw_duration:<15.3f}")
        logger.info("=" * 60)
        
        # ========== 6. 路段性能分析 ==========
        logger.info("\n[步骤6] 路段性能分析...")
        
        # 使用Frank-Wolfe结果进行分析
        network.reset_flows()
        for link_id, flow in fw_flows.items():
            network.links[link_id].update_flow(flow)
        
        performance = calculate_link_performance(network)
        
        logger.info("\n路段详细信息:")
        logger.info("-" * 80)
        logger.info(f"{'路段':<8} {'流量':<10} {'容量':<10} {'流量比':<10} {'行程时间':<12} {'自由流时间':<12}")
        logger.info("-" * 80)
        
        for link_id, perf in sorted(performance.items()):
            logger.info(
                f"{link_id:<8} "
                f"{perf['flow']:<10.1f} "
                f"{perf['capacity']:<10.0f} "
                f"{perf['ratio']:<10.2f} "
                f"{perf['travel_time']:<12.3f} "
                f"{perf['free_flow_time']:<12.3f}"
            )
        logger.info("-" * 80)
        
        logger.info(f"\n所有结果已保存到目录: {output_dir}")
        logger.info("\n交通分配系统运行完成！")
        
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        return 1
    except ValueError as e:
        logger.error(f"数据格式错误: {e}")
        return 1
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

