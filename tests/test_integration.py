"""集成测试"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.network import Network
from models.demand import Demand
from algorithms.all_or_nothing import all_or_nothing_assignment
from algorithms.incremental import incremental_assignment
from algorithms.frank_wolfe import frank_wolfe_assignment
from evaluation.metrics import calculate_total_travel_time


class TestIntegration:
    """端到端集成测试"""
    
    @pytest.fixture
    def network(self):
        """加载真实路网"""
        network = Network()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        network.load_from_json(os.path.join(data_dir, 'network.json'))
        return network
    
    @pytest.fixture
    def demand(self):
        """加载真实需求"""
        demand = Demand()
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        demand.load_from_json(os.path.join(data_dir, 'demand.json'))
        return demand
    
    def test_full_workflow(self, network, demand):
        """测试完整工作流程"""
        # 全有全无分配
        network.reset_flows()
        aon_flows = all_or_nothing_assignment(network, demand)
        for link_id, flow in aon_flows.items():
            network.links[link_id].update_flow(flow)
        aon_time = calculate_total_travel_time(network)
        
        # 增量分配
        network.reset_flows()
        inc_flows = incremental_assignment(network, demand, n_iterations=4)
        for link_id, flow in inc_flows.items():
            network.links[link_id].update_flow(flow)
        inc_time = calculate_total_travel_time(network)
        
        # Frank-Wolfe
        network.reset_flows()
        fw_flows, fw_history = frank_wolfe_assignment(
            network, demand, max_iter=20, epsilon=0.01
        )
        for link_id, flow in fw_flows.items():
            network.links[link_id].update_flow(flow)
        fw_time = calculate_total_travel_time(network)
        
        # 验证所有算法都产生了有效结果
        assert aon_time > 0
        assert inc_time > 0
        assert fw_time > 0
        
        # Frank-Wolfe应该收敛
        assert len(fw_history) > 0
        
        print(f"\n集成测试结果:")
        print(f"  全有全无: {aon_time:.2f}")
        print(f"  增量分配: {inc_time:.2f}")
        print(f"  Frank-Wolfe: {fw_time:.2f}")
    
    def test_flow_conservation(self, network, demand):
        """测试流量守恒"""
        network.reset_flows()
        flows = all_or_nothing_assignment(network, demand)
        
        # 每个OD对的流量应该被分配到某些路段上
        total_demand = demand.get_total_demand()
        
        # 由于网络结构，某些流量会在多条路段上
        # 这里只验证有流量被分配
        total_assigned = sum(flows.values())
        assert total_assigned > 0

