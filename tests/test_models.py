"""测试数据模型"""
import pytest
import json
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.link import Link
from models.network import Network
from models.demand import Demand


class TestLink:
    """测试Link类"""
    
    def test_link_initialization(self):
        """测试Link初始化"""
        link = Link(
            from_node='A',
            to_node='B',
            length=10.0,
            capacity=1800,
            speed_max=30,
            flow=0
        )
        assert link.from_node == 'A'
        assert link.to_node == 'B'
        assert link.length == 10.0
        assert link.capacity == 1800
        assert link.speed_max == 30
        assert link.flow == 0
    
    def test_get_free_flow_time(self):
        """测试自由流行程时间计算"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        # t0 = length / speed_max = 15 / 30 = 0.5
        assert link.get_free_flow_time() == 0.5
    
    def test_get_travel_time_no_congestion(self):
        """测试无拥堵时的行程时间（流量=0）"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        # 流量为0时，travel_time = t0
        travel_time = link.get_travel_time(0)
        assert travel_time == 0.5
    
    def test_get_travel_time_with_congestion(self):
        """测试有拥堵时的BPR函数"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        # t(q) = t0 * (1 + q/cap)^2
        # t0 = 0.5, q = 900, cap = 1800
        # t = 0.5 * (1 + 900/1800)^2 = 0.5 * (1.5)^2 = 0.5 * 2.25 = 1.125
        travel_time = link.get_travel_time(900)
        assert abs(travel_time - 1.125) < 0.001
    
    def test_get_travel_time_full_capacity(self):
        """测试满容量时的行程时间"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        # q = cap时，t = t0 * (1 + 1)^2 = t0 * 4 = 2.0
        travel_time = link.get_travel_time(1800)
        assert abs(travel_time - 2.0) < 0.001
    
    def test_update_flow(self):
        """测试更新流量"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        assert link.flow == 0
        link.update_flow(500)
        assert link.flow == 500
        link.update_flow(1000)
        assert link.flow == 1000
    
    def test_get_id(self):
        """测试获取链路ID"""
        link = Link('A', 'B', length=15.0, capacity=1800, speed_max=30, flow=0)
        assert link.get_id() == 'AB'


class TestNetwork:
    """测试Network类"""
    
    @pytest.fixture
    def temp_network_json(self, tmp_path):
        """创建临时的network.json文件"""
        network_data = {
            "nodes": {
                "name": ["A", "B", "C"],
                "x": [0, 10, 20],
                "y": [0, 0, 0]
            },
            "links": {
                "between": ["AB", "BC"],
                "capacity": [1800, 3600],
                "speedmax": [30, 60]
            }
        }
        json_file = tmp_path / "network.json"
        with open(json_file, 'w') as f:
            json.dump(network_data, f)
        return json_file
    
    def test_load_from_json(self, temp_network_json):
        """测试从JSON加载网络数据"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        assert len(network.nodes) == 3
        assert 'A' in network.nodes
        assert 'B' in network.nodes
        assert 'C' in network.nodes
        
        assert len(network.links) == 2
        assert 'AB' in network.links
        assert 'BC' in network.links
    
    def test_calculate_link_length(self, temp_network_json):
        """测试路段长度计算"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        # A(0,0) -> B(10,0): 距离 = 10
        link_ab = network.get_link('A', 'B')
        assert abs(link_ab.length - 10.0) < 0.001
        
        # B(10,0) -> C(20,0): 距离 = 10
        link_bc = network.get_link('A', 'B')
        assert abs(link_bc.length - 10.0) < 0.001
    
    def test_get_link(self, temp_network_json):
        """测试获取指定路段"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        link = network.get_link('A', 'B')
        assert link is not None
        assert link.from_node == 'A'
        assert link.to_node == 'B'
        
        # 测试不存在的路段
        non_link = network.get_link('A', 'C')
        assert non_link is None
    
    def test_get_all_links(self, temp_network_json):
        """测试获取所有路段"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        links = network.get_all_links()
        assert len(links) == 2
    
    def test_reset_flows(self, temp_network_json):
        """测试重置所有路段流量"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        # 设置流量
        network.get_link('A', 'B').update_flow(1000)
        network.get_link('B', 'C').update_flow(500)
        
        # 重置流量
        network.reset_flows()
        
        assert network.get_link('A', 'B').flow == 0
        assert network.get_link('B', 'C').flow == 0
    
    def test_get_total_travel_time(self, temp_network_json):
        """测试计算总出行时间"""
        network = Network()
        network.load_from_json(str(temp_network_json))
        
        # 设置流量
        network.get_link('A', 'B').update_flow(900)  # t = 1.125
        network.get_link('B', 'C').update_flow(1800)  # t = 0.5 * 4 = 2.0
        
        # 总出行时间 = 900 * 1.125 + 1800 * 2.0 = 1012.5 + 3600 = 4612.5
        total_time = network.get_total_travel_time()
        assert abs(total_time - 4612.5) < 1.0


class TestDemand:
    """测试Demand类"""
    
    @pytest.fixture
    def temp_demand_json(self, tmp_path):
        """创建临时的demand.json文件"""
        demand_data = {
            "from": ["A", "B"],
            "to": ["C", "A"],
            "amount": [1000, 500]
        }
        json_file = tmp_path / "demand.json"
        with open(json_file, 'w') as f:
            json.dump(demand_data, f)
        return json_file
    
    def test_load_from_json(self, temp_demand_json):
        """测试从JSON加载需求数据"""
        demand = Demand()
        demand.load_from_json(str(temp_demand_json))
        
        od_pairs = demand.get_od_pairs()
        assert len(od_pairs) == 2
        assert od_pairs[0] == ('A', 'C', 1000)
        assert od_pairs[1] == ('B', 'A', 500)
    
    def test_get_od_pairs(self, temp_demand_json):
        """测试获取OD对列表"""
        demand = Demand()
        demand.load_from_json(str(temp_demand_json))
        
        od_pairs = demand.get_od_pairs()
        assert isinstance(od_pairs, list)
        assert len(od_pairs) == 2

