"""可视化工具"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import networkx as nx
from typing import List, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.network import Network

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False


def plot_network(
    network: Network,
    title: str = "Road Network",
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    绘制路网结构图
    
    Args:
        network: 路网对象
        title: 图标题
        save_path: 保存路径（可选）
        show: 是否显示图形
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 创建NetworkX图
    G = nx.DiGraph()
    
    # 添加节点
    for node, (x, y) in network.nodes.items():
        G.add_node(node, pos=(x, y))
    
    # 添加边
    for link_id, link in network.links.items():
        G.add_edge(
            link.from_node,
            link.to_node,
            capacity=link.capacity,
            speed=link.speed_max,
            length=link.length
        )
    
    # 获取节点位置
    pos = nx.get_node_attributes(G, 'pos')
    
    # 绘制节点
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightblue',
        node_size=800,
        edgecolors='black',
        linewidths=2,
        ax=ax
    )
    
    # 绘制节点标签
    nx.draw_networkx_labels(
        G, pos,
        font_size=14,
        font_weight='bold',
        ax=ax
    )
    
    # 绘制边
    nx.draw_networkx_edges(
        G, pos,
        edge_color='gray',
        width=2,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # 添加边的标签（cap和spd）
    edge_labels = {}
    for link_id, link in network.links.items():
        edge_labels[(link.from_node, link.to_node)] = (
            f"cap={link.capacity}, spd={link.speed_max}"
        )
    
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
        ax=ax
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"路网图已保存到: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_flow_assignment(
    network: Network,
    title: str = "Traffic Assignment Result",
    save_path: Optional[str] = None,
    show: bool = True,
    highlight_congested: bool = True
) -> None:
    """
    绘制流量分配结果
    
    Args:
        network: 路网对象（包含流量信息）
        title: 图标题
        save_path: 保存路径（可选）
        show: 是否显示图形
        highlight_congested: 是否高亮拥堵路段
    """
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 创建NetworkX图
    G = nx.DiGraph()
    
    # 添加节点
    for node, (x, y) in network.nodes.items():
        G.add_node(node, pos=(x, y))
    
    # 计算流量范围用于归一化
    max_flow = max([link.flow for link in network.links.values()]) if network.links else 1
    
    # 添加边和流量信息
    edge_colors = []
    edge_widths = []
    
    for link_id, link in network.links.items():
        G.add_edge(link.from_node, link.to_node, flow=link.flow)
        
        # 边宽度根据流量大小
        width = 1 + (link.flow / max_flow) * 5 if max_flow > 0 else 1
        edge_widths.append(width)
        
        # 边颜色根据拥堵程度 (flow/capacity)
        ratio = link.flow / link.capacity if link.capacity > 0 else 0
        if ratio < 0.5:
            color = 'green'
        elif ratio < 0.8:
            color = 'orange'
        else:
            color = 'red'
        edge_colors.append(color)
    
    # 获取节点位置
    pos = nx.get_node_attributes(G, 'pos')
    
    # 绘制节点
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightblue',
        node_size=1000,
        edgecolors='black',
        linewidths=2,
        ax=ax
    )
    
    # 绘制节点标签
    nx.draw_networkx_labels(
        G, pos,
        font_size=14,
        font_weight='bold',
        ax=ax
    )
    
    # 绘制边
    nx.draw_networkx_edges(
        G, pos,
        edge_color=edge_colors,
        width=edge_widths,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )
    
    # 添加边的流量标签
    edge_labels = {}
    for link_id, link in network.links.items():
        ratio = link.flow / link.capacity if link.capacity > 0 else 0
        edge_labels[(link.from_node, link.to_node)] = (
            f"flow={link.flow:.0f}\nratio={ratio:.2f}"
        )
    
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9),
        ax=ax
    )
    
    # 添加图例
    if highlight_congested:
        green_patch = mpatches.Patch(color='green', label='畅通 (ratio<0.5)')
        orange_patch = mpatches.Patch(color='orange', label='拥挤 (0.5≤ratio<0.8)')
        red_patch = mpatches.Patch(color='red', label='拥堵 (ratio≥0.8)')
        ax.legend(handles=[green_patch, orange_patch, red_patch], loc='upper right')
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"流量分配图已保存到: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_convergence(
    history: List[Dict],
    title: str = "Frank-Wolfe Convergence",
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    绘制Frank-Wolfe收敛曲线
    
    Args:
        history: 收敛历史记录
        title: 图标题
        save_path: 保存路径（可选）
        show: 是否显示图形
    """
    if not history:
        print("警告: 没有收敛历史记录")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    iterations = [h['iteration'] for h in history]
    gaps = [h['relative_gap'] for h in history]
    times = [h['total_travel_time'] for h in history]
    
    # 绘制相对间隙
    ax1.plot(iterations, gaps, 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('迭代次数', fontsize=12)
    ax1.set_ylabel('相对间隙', fontsize=12)
    ax1.set_title('相对间隙收敛曲线', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # 绘制总出行时间
    ax2.plot(iterations, times, 'r-s', linewidth=2, markersize=6)
    ax2.set_xlabel('迭代次数', fontsize=12)
    ax2.set_ylabel('总出行时间', fontsize=12)
    ax2.set_title('总出行时间变化曲线', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"收敛图已保存到: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_comparison(
    results: Dict[str, float],
    title: str = "Algorithm Comparison",
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    绘制不同算法的比较图
    
    Args:
        results: 结果字典 {算法名称: 总出行时间}
        title: 图标题
        save_path: 保存路径（可选）
        show: 是否显示图形
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    algorithms = list(results.keys())
    times = list(results.values())
    
    colors = ['skyblue', 'lightcoral', 'lightgreen'][:len(algorithms)]
    bars = ax.bar(algorithms, times, color=colors, edgecolor='black', linewidth=1.5)
    
    # 在柱子上添加数值标签
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{time:.1f}',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold'
        )
    
    # 添加差异百分比标注
    if len(times) > 1:
        min_time = min(times)
        for i, (bar, time) in enumerate(zip(bars, times)):
            if time > min_time:
                diff_percent = ((time - min_time) / min_time) * 100
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height * 0.5,
                    f'+{diff_percent:.2f}%',
                    ha='center',
                    va='center',
                    fontsize=10,
                    color='red',
                    fontweight='bold'
                )
    
    ax.set_ylabel('总出行时间', fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"比较图已保存到: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_flow_difference(
    network1: Network,
    network2: Network,
    label1: str = "算法1",
    label2: str = "算法2",
    title: str = "流量差异对比",
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    绘制两种算法的流量差异对比图
    
    Args:
        network1: 第一个路网（含流量）
        network2: 第二个路网（含流量）
        label1: 算法1名称
        label2: 算法2名称
        title: 图标题
        save_path: 保存路径
        show: 是否显示
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 收集数据
    link_ids = []
    flows1 = []
    flows2 = []
    
    for link_id in sorted(network1.links.keys()):
        link_ids.append(link_id)
        flows1.append(network1.links[link_id].flow)
        flows2.append(network2.links[link_id].flow)
    
    x = range(len(link_ids))
    width = 0.35
    
    # 绘制柱状图
    bars1 = ax.bar([i - width/2 for i in x], flows1, width, 
                    label=label1, color='skyblue', edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], flows2, width,
                    label=label2, color='lightcoral', edgecolor='black')
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('路段', fontsize=12)
    ax.set_ylabel('流量', fontsize=12)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(link_ids, rotation=45, ha='right')
    ax.legend(fontsize=12)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"流量差异图已保存到: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()

