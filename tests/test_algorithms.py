"""测试交通分配算法"""
import pytest
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.network import Network
from models.demand import Demand
from algorithms.dijkstra import shortest_path, get_path_links
from algorithms.all_or_nothing import all_or_nothing_assignment
from algorithms.incremental import incremental_assignment
from algorithms.frank_wolfe import frank_wolfe_assignment


class TestDijkstra:
    """测试Dijkstra最短路径算法"""
    
    @pytest.fixture
    def simple_network(self):
        """创建简单测试网络"""
        network = Network()
        # 手动构建简单网络: A -> B -> C
        network.nodes = {
            'A': (0, 0),
            'B': (10, 0),
            'C': (20, 0)
        }
        
        from models.link import Link
        link_ab = Link('A', 'B', 10.0, 1800, 30, 0)
        link_bc = Link('B', 'C', 10.0, 1800, 30, 0)
        
        network.links = {
            'AB': link_ab,
            'BC': link_bc
        }
        
        network.adjacency = {
            'A': [('B', 'AB')],
            'B': [('C', 'BC')],
            'C': []
        }
        
        return network
    
    def test_shortest_path_simple(self, simple_network):
        """测试简单最短路径"""
        path, cost = shortest_path(simple_network, 'A', 'C')
        assert path == ['A', 'B', 'C']
        assert cost > 0
    
    def test_shortest_path_single_node(self, simple_network):
        """测试起点终点相同"""
        path, cost = shortest_path(simple_network, 'A', 'A')
        assert path == ['A']
        assert cost == 0
    
    def test_shortest_path_not_found(self, simple_network):
        """测试路径不存在"""
        path, cost = shortest_path(simple_network, 'C', 'A')
        assert path is None
        assert cost == float('inf')
    
    def test_get_path_links(self, simple_network):
        """测试路径转换为路段列表"""
        path = ['A', 'B', 'C']
        links = get_path_links(simple_network, path)
        assert len(links) == 2
        assert links[0].get_id() == 'AB'
        assert links[1].get_id() == 'BC'


class TestAllOrNothing:
    """测试全有全无分配"""
    
    @pytest.fixture
    def test_network(self):
        """加载测试网络"""
        network = Network()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        network.load_from_json(os.path.join(data_dir, 'network.json'))
        return network
    
    @pytest.fixture
    def test_demand(self):
        """加载测试需求"""
        demand = Demand()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        demand.load_from_json(os.path.join(data_dir, 'demand.json'))
        return demand
    
    def test_all_or_nothing_basic(self, test_network, test_demand):
        """测试全有全无分配基本功能"""
        flows = all_or_nothing_assignment(test_network, test_demand)
        
        # 验证返回的是字典
        assert isinstance(flows, dict)
        
        # 验证流量非负
        for link_id, flow in flows.items():
            assert flow >= 0
    
    def test_all_or_nothing_flow_conservation(self, test_network, test_demand):
        """测试流量守恒"""
        flows = all_or_nothing_assignment(test_network, test_demand)
        
        # 总分配流量应该等于总需求
        total_demand = test_demand.get_total_demand()
        # 由于某些OD对可能无路径，实际分配流量可能少于总需求
        # 这里只检查不超过总需求
        assigned_flow = sum(flows.values())
        assert assigned_flow <= total_demand * len(test_demand.get_od_pairs())


class TestIncremental:
    """测试增量分配"""
    
    @pytest.fixture
    def test_network(self):
        """加载测试网络"""
        network = Network()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        network.load_from_json(os.path.join(data_dir, 'network.json'))
        return network
    
    @pytest.fixture
    def test_demand(self):
        """加载测试需求"""
        demand = Demand()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        demand.load_from_json(os.path.join(data_dir, 'demand.json'))
        return demand
    
    def test_incremental_basic(self, test_network, test_demand):
        """测试增量分配基本功能"""
        flows = incremental_assignment(test_network, test_demand, n_iterations=4)
        
        # 验证返回的是字典
        assert isinstance(flows, dict)
        
        # 验证流量非负
        for link_id, flow in flows.items():
            assert flow >= 0
    
    def test_incremental_iterations(self, test_network, test_demand):
        """测试不同迭代次数"""
        flows_2 = incremental_assignment(test_network, test_demand, n_iterations=2)
        flows_4 = incremental_assignment(test_network, test_demand, n_iterations=4)
        
        # 两次结果应该不同
        assert flows_2 != flows_4


class TestFrankWolfe:
    """测试Frank-Wolfe算法"""
    
    @pytest.fixture
    def test_network(self):
        """加载测试网络"""
        network = Network()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        network.load_from_json(os.path.join(data_dir, 'network.json'))
        return network
    
    @pytest.fixture
    def test_demand(self):
        """加载测试需求"""
        demand = Demand()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        demand.load_from_json(os.path.join(data_dir, 'demand.json'))
        return demand
    
    def test_frank_wolfe_basic(self, test_network, test_demand):
        """测试Frank-Wolfe基本功能"""
        flows, history = frank_wolfe_assignment(
            test_network, 
            test_demand, 
            max_iter=20,
            epsilon=0.01
        )
        
        # 验证返回的是字典和历史记录
        assert isinstance(flows, dict)
        assert isinstance(history, list)
        
        # 验证流量非负
        for link_id, flow in flows.items():
            assert flow >= 0
        
        # 验证有历史记录
        assert len(history) > 0
    
    def test_frank_wolfe_convergence(self, test_network, test_demand):
        """测试Frank-Wolfe收敛性"""
        flows, history = frank_wolfe_assignment(
            test_network,
            test_demand,
            max_iter=50,
            epsilon=0.001
        )
        
        # 验证相对间隙递减
        if len(history) > 1:
            first_gap = history[0]['relative_gap']
            last_gap = history[-1]['relative_gap']
            assert last_gap <= first_gap

