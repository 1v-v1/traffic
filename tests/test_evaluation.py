"""测试评估指标"""
import pytest
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.network import Network
from models.link import Link
from evaluation.metrics import calculate_total_travel_time, calculate_relative_gap


class TestMetrics:
    """测试评估指标"""
    
    @pytest.fixture
    def simple_network(self):
        """创建简单测试网络"""
        network = Network()
        network.nodes = {
            'A': (0, 0),
            'B': (10, 0)
        }
        
        link = Link('A', 'B', 10.0, 1800, 30, 0)
        network.links = {'AB': link}
        network.adjacency = {'A': [('B', 'AB')], 'B': []}
        
        return network
    
    def test_calculate_total_travel_time_zero_flow(self, simple_network):
        """测试零流量时的总出行时间"""
        total_time = calculate_total_travel_time(simple_network)
        assert total_time == 0.0
    
    def test_calculate_total_travel_time_with_flow(self, simple_network):
        """测试有流量时的总出行时间"""
        # 设置流量为900
        simple_network.links['AB'].update_flow(900)
        
        # t = 1.125, total = 900 * 1.125 = 1012.5
        total_time = calculate_total_travel_time(simple_network)
        assert abs(total_time - 1012.5) < 1.0
    
    def test_calculate_relative_gap(self, simple_network):
        """测试相对间隙计算"""
        # 设置当前流量
        simple_network.links['AB'].update_flow(1000)
        
        # 辅助流量
        auxiliary_flows = {'AB': 800}
        
        gap = calculate_relative_gap(simple_network, auxiliary_flows)
        
        # 相对间隙应该是非负数
        assert gap >= 0

