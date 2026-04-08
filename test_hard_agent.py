"""
test_hard_agent.py - Comprehensive Test Suite for HardDefenderAgent

Tests all aspects of the risk-based defender:
1. Risk scoring logic
2. Premium protection
3. Performance on all datasets
4. Edge cases and boundary conditions
5. Adversarial robustness
6. Deterministic behavior
"""

import sys
from typing import List, Dict, Any
from hard_defender_agent import HardDefenderAgent
from environment import make_env
from grader import Grader
from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data


class TestHardDefenderAgent:
    """Comprehensive test suite for HardDefenderAgent"""
    
    def __init__(self):
        self.agent = HardDefenderAgent(block_threshold=2.5)
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def assert_equal(self, actual, expected, test_name: str):
        """Assert equality with detailed output"""
        self.total += 1
        if actual == expected:
            print(f"  ✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name}")
            print(f"     Expected: {expected}")
            print(f"     Got:      {actual}")
            self.failed += 1
            return False
    
    def assert_true(self, condition: bool, test_name: str):
        """Assert condition is true"""
        self.total += 1
        if condition:
            print(f"  ✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name}")
            self.failed += 1
            return False
    
    def assert_greater_equal(self, actual, threshold, test_name: str):
        """Assert value is greater than or equal to threshold"""
        self.total += 1
        if actual >= threshold:
            print(f"  ✅ {test_name} ({actual:.3f} >= {threshold})")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name} ({actual:.3f} < {threshold})")
            self.failed += 1
            return False
    
    def assert_less_equal(self, actual, threshold, test_name: str):
        """Assert value is less than or equal to threshold"""
        self.total += 1
        if actual <= threshold:
            print(f"  ✅ {test_name} ({actual} <= {threshold})")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name} ({actual} > {threshold})")
            self.failed += 1
            return False
    
    # ========================================================================
    # TEST 1: Risk Scoring Logic
    # ========================================================================
    
    def test_risk_scoring(self):
        """Test the risk scoring calculation"""
        print("\n" + "="*80)
        print("TEST 1: Risk Scoring Logic")
        print("="*80)
        
        # Test Case 1.1: High RPS + Suspicious = High Risk
        user1 = {"id": "T1", "rps": 200, "is_suspicious_pattern": True, "tier": "normal"}
        risk1 = self.agent._risk_score(user1)
        self.assert_equal(risk1, 4.0, "High RPS (>90) + Suspicious = 4.0 risk")
        
        # Test Case 1.2: Medium RPS + Suspicious = Medium-High Risk
        user2 = {"id": "T2", "rps": 70, "is_suspicious_pattern": True, "tier": "normal"}
        risk2 = self.agent._risk_score(user2)
        self.assert_equal(risk2, 3.0, "Medium RPS (50-90) + Suspicious = 3.0 risk")
        
        # Test Case 1.3: Low RPS + Suspicious = Medium Risk
        user3 = {"id": "T3", "rps": 30, "is_suspicious_pattern": True, "tier": "normal"}
        risk3 = self.agent._risk_score(user3)
        self.assert_equal(risk3, 2.5, "Low RPS (20-50) + Suspicious = 2.5 risk")
        
        # Test Case 1.4: High RPS + Not Suspicious = Medium Risk
        user4 = {"id": "T4", "rps": 150, "is_suspicious_pattern": False, "tier": "normal"}
        risk4 = self.agent._risk_score(user4)
        self.assert_equal(risk4, 2.0, "High RPS (>90) + Not Suspicious = 2.0 risk")
        
        # Test Case 1.5: Low RPS + Not Suspicious = Low Risk
        user5 = {"id": "T5", "rps": 10, "is_suspicious_pattern": False, "tier": "normal"}
        risk5 = self.agent._risk_score(user5)
        self.assert_equal(risk5, 0.5, "Very low RPS (<15) + Not Suspicious = 0.5 risk")
        
        # Test Case 1.6: Normal activity = No Risk
        user6 = {"id": "T6", "rps": 15, "is_suspicious_pattern": False, "tier": "normal"}
        risk6 = self.agent._risk_score(user6)
        self.assert_equal(risk6, 0.0, "Normal RPS (15-20) + Not Suspicious = 0.0 risk")
        
        # Test Case 1.7: Premium user gets protection (-2.0)
        user7 = {"id": "T7", "rps": 200, "is_suspicious_pattern": True, "tier": "premium"}
        risk7 = self.agent._risk_score(user7)
        self.assert_equal(risk7, 2.0, "Premium gets -2.0 protection (4.0 - 2.0 = 2.0)")
        
        # Test Case 1.8: Premium with normal activity = Negative risk
        user8 = {"id": "T8", "rps": 10, "is_suspicious_pattern": False, "tier": "premium"}
        risk8 = self.agent._risk_score(user8)
        self.assert_equal(risk8, -1.5, "Premium + low activity = -1.5 (0.5 - 2.0)")
    
    # ========================================================================
    # TEST 2: Premium Protection
    # ========================================================================
    
    def test_premium_protection(self):
        """Test that premium users are protected"""
        print("\n" + "="*80)
        print("TEST 2: Premium Protection")
        print("="*80)
        
        premium_users = [
            # High risk premium (should NOT block due to protection)
            {"id": "P1", "rps": 500, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
            {"id": "P2", "rps": 300, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
            {"id": "P3", "rps": 200, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
            # Normal premium
            {"id": "P4", "rps": 50, "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
            {"id": "P5", "rps": 20, "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
            # Some normal users as control
            {"id": "N1", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        ]
        
        # Run episode
        env = make_env()
        observation = env.reset(premium_users)
        blocked = []
        
        for _ in range(20):
            action = self.agent.select_action(observation)
            if action.get("type") == "block":
                blocked.append(action.get("user_id"))
            observation, _, done, _ = env.step(action)
            if done:
                break
        
        # Check no premium users were blocked
        premium_blocked = [uid for uid in blocked if uid.startswith("P")]
        
        self.assert_equal(len(premium_blocked), 0, "No premium users blocked")
        self.assert_true(len(blocked) >= 0, "Agent can still block normal users")
    
    # ========================================================================
    # TEST 3: Performance on All Datasets
    # ========================================================================
    
    def test_all_datasets(self):
        """Test performance on all difficulty levels"""
        print("\n" + "="*80)
        print("TEST 3: Performance on All Datasets")
        print("="*80)
        
        grader = Grader()
        
        # Test 3.1: Easy Dataset
        easy_blocked = self._run_episode(get_easy_data())
        easy_results = grader.grade(easy_blocked, get_easy_data())
        self.assert_greater_equal(easy_results['f1'], 0.90, "Easy F1 >= 0.90")
        self.assert_equal(easy_results['premium_penalty'], 0, "Easy: No premium violations")
        
        # Test 3.2: Medium Dataset
        medium_blocked = self._run_episode(get_medium_data())
        medium_results = grader.grade(medium_blocked, get_medium_data())
        self.assert_greater_equal(medium_results['f1'], 0.80, "Medium F1 >= 0.80")
        self.assert_equal(medium_results['premium_penalty'], 0, "Medium: No premium violations")
        
        # Test 3.3: Extreme Dataset
        extreme_blocked = self._run_episode(get_extreme_data())
        extreme_results = grader.grade(extreme_blocked, get_extreme_data())
        self.assert_greater_equal(extreme_results['f1'], 0.60, "Extreme F1 >= 0.60")
        self.assert_equal(extreme_results['premium_penalty'], 0, "Extreme: No premium violations")
        
        # Test 3.4: Winning Dataset (MOST IMPORTANT)
        winning_blocked = self._run_episode(get_winning_data())
        winning_results = grader.grade(winning_blocked, get_winning_data())
        self.assert_greater_equal(winning_results['f1'], 0.70, "Winning F1 >= 0.70 (PASS THRESHOLD)")
        self.assert_equal(winning_results['premium_penalty'], 0, "Winning: No premium violations")
        
        print(f"\n  📊 Performance Summary:")
        print(f"     Easy:    F1={easy_results['f1']:.3f}, Premium={easy_results['premium_penalty']}")
        print(f"     Medium:  F1={medium_results['f1']:.3f}, Premium={medium_results['premium_penalty']}")
        print(f"     Extreme: F1={extreme_results['f1']:.3f}, Premium={extreme_results['premium_penalty']}")
        print(f"     Winning: F1={winning_results['f1']:.3f}, Premium={winning_results['premium_penalty']}")
    
    # ========================================================================
    # TEST 4: Edge Cases
    # ========================================================================
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n" + "="*80)
        print("TEST 4: Edge Cases and Boundary Conditions")
        print("="*80)
        
        edge_cases = [
            # Zero RPS
            {"id": "E1", "rps": 0, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
            # Maximum RPS
            {"id": "E2", "rps": 10000, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            # Exactly at threshold boundaries
            {"id": "E3", "rps": 90, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            {"id": "E4", "rps": 50, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            {"id": "E5", "rps": 20, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            # Stealth bot (low RPS, no suspicious)
            {"id": "E6", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": True},
            # Active human (high RPS, not suspicious)
            {"id": "E7", "rps": 150, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
            # Premium bot (should NOT block)
            {"id": "E8", "rps": 500, "is_suspicious_pattern": True, "tier": "premium", "is_bot": True},
        ]
        
        grader = Grader()
        blocked = self._run_episode(edge_cases)
        results = grader.grade(blocked, edge_cases)
        
        # Verify premium not blocked
        self.assert_equal(results['premium_penalty'], 0, "Edge: No premium violations")
        
        # Verify high RPS bots blocked
        self.assert_true("E2" in blocked, "Max RPS bot blocked")
        
        # Check specific edge cases
        print(f"\n  📋 Edge Case Results:")
        for user in edge_cases:
            was_blocked = user['id'] in blocked
            print(f"     {user['id']}: RPS={user['rps']:5d}, Susp={str(user['is_suspicious_pattern']):5s}, "
                  f"Tier={user['tier']:7s}, Bot={str(user['is_bot']):5s} → {'BLOCKED' if was_blocked else 'ALLOWED'}")
        
        print(f"\n     F1 Score: {results['f1']:.3f}")
        print(f"     TP={results['TP']}, FP={results['FP']}, FN={results['FN']}")
    
    # ========================================================================
    # TEST 5: Deterministic Behavior
    # ========================================================================
    
    def test_deterministic(self):
        """Test that agent produces same results on repeated runs"""
        print("\n" + "="*80)
        print("TEST 5: Deterministic Behavior")
        print("="*80)
        
        dataset = get_winning_data()
        
        # Run 3 times
        run1 = self._run_episode(dataset)
        run2 = self._run_episode(dataset)
        run3 = self._run_episode(dataset)
        
        # All runs should produce identical results
        self.assert_equal(run1, run2, "Run 1 == Run 2")
        self.assert_equal(run2, run3, "Run 2 == Run 3")
        self.assert_equal(run1, run3, "Run 1 == Run 3")
        
        print(f"     Blocked users: {len(run1)} (consistent across all runs)")
    
    # ========================================================================
    # TEST 6: Block Threshold Sensitivity
    # ========================================================================
    
    def test_threshold_sensitivity(self):
        """Test different block thresholds"""
        print("\n" + "="*80)
        print("TEST 6: Block Threshold Sensitivity")
        print("="*80)
        
        dataset = get_winning_data()
        grader = Grader()
        
        thresholds = [1.5, 2.0, 2.5, 3.0, 3.5]
        
        print(f"\n  {'Threshold':>10} | {'F1':>6} | {'Precision':>9} | {'Recall':>6} | {'Blocked':>7} | Premium")
        print(f"  {'-'*10}-+-{'-'*6}-+-{'-'*9}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}")
        
        for threshold in thresholds:
            agent = HardDefenderAgent(block_threshold=threshold)
            blocked = self._run_episode(dataset, agent)
            results = grader.grade(blocked, dataset)
            
            print(f"  {threshold:>10.1f} | {results['f1']:>6.3f} | {results['precision']:>9.3f} | "
                  f"{results['recall']:>6.3f} | {len(blocked):>7d} | {results['premium_penalty']:>7d}")
        
        # Default threshold (2.5) should work well
        agent_default = HardDefenderAgent(block_threshold=2.5)
        blocked_default = self._run_episode(dataset, agent_default)
        results_default = grader.grade(blocked_default, dataset)
        
        self.assert_greater_equal(results_default['f1'], 0.70, "Default threshold F1 >= 0.70")
    
    # ========================================================================
    # TEST 7: Adversarial Robustness
    # ========================================================================
    
    def test_adversarial(self):
        """Test robustness against adversarial examples"""
        print("\n" + "="*80)
        print("TEST 7: Adversarial Robustness")
        print("="*80)
        
        adversarial = [
            # Stealth bot (low RPS but suspicious)
            {"id": "A1", "rps": 20, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            # Active human (high RPS, not suspicious)
            {"id": "A2", "rps": 180, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
            # Premium bot (critical - must NOT block)
            {"id": "A3", "rps": 500, "is_suspicious_pattern": True, "tier": "premium", "is_bot": True},
            # False positive trap (suspicious human)
            {"id": "A4", "rps": 45, "is_suspicious_pattern": True, "tier": "normal", "is_bot": False},
            # Stealth bot (no suspicious pattern)
            {"id": "A5", "rps": 350, "is_suspicious_pattern": False, "tier": "normal", "is_bot": True},
            # Extreme high RPS bot
            {"id": "A6", "rps": 2000, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
            # Zero RPS human
            {"id": "A7", "rps": 0, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
            # Premium human (critical - must NOT block)
            {"id": "A8", "rps": 200, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
        ]
        
        blocked = self._run_episode(adversarial)
        
        print(f"\n  {'ID':>4} | {'RPS':>4} | {'Suspicious':>10} | {'Tier':>7} | {'Bot':>5} | {'Action':>7} | Result")
        print(f"  {'-'*4}-+-{'-'*4}-+-{'-'*10}-+-{'-'*7}-+-{'-'*5}-+-{'-'*7}-+-{'-'*10}")
        
        correct = 0
        for user in adversarial:
            was_blocked = user['id'] in blocked
            should_block = user['is_bot'] and user['tier'] != 'premium'
            is_correct = (was_blocked == should_block)
            
            if is_correct:
                correct += 1
            
            result = "✅ CORRECT" if is_correct else "❌ WRONG"
            action = "BLOCKED" if was_blocked else "ALLOWED"
            
            print(f"  {user['id']:>4} | {user['rps']:>4d} | {str(user['is_suspicious_pattern']):>10} | "
                  f"{user['tier']:>7} | {str(user['is_bot']):>5} | {action:>7} | {result}")
        
        accuracy = correct / len(adversarial)
        self.assert_greater_equal(accuracy, 0.625, f"Adversarial accuracy >= 62.5% ({correct}/{len(adversarial)})")
        
        # Premium protection must be perfect
        premium_blocked = [u['id'] for u in adversarial if u['tier'] == 'premium' and u['id'] in blocked]
        self.assert_equal(len(premium_blocked), 0, "No premium users blocked (adversarial)")
    
    # ========================================================================
    # TEST 8: Empty and Single User Cases
    # ========================================================================
    
    def test_special_cases(self):
        """Test special cases like empty dataset, single user, etc."""
        print("\n" + "="*80)
        print("TEST 8: Special Cases")
        print("="*80)
        
        # Test 8.1: Single bot
        single_bot = [{"id": "S1", "rps": 500, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True}]
        blocked1 = self._run_episode(single_bot)
        self.assert_true("S1" in blocked1, "Single bot blocked")
        
        # Test 8.2: Single human
        single_human = [{"id": "S2", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False}]
        blocked2 = self._run_episode(single_human)
        self.assert_true("S2" not in blocked2, "Single human NOT blocked")
        
        # Test 8.3: Single premium (should NOT block)
        single_premium = [{"id": "S3", "rps": 500, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False}]
        blocked3 = self._run_episode(single_premium)
        self.assert_true("S3" not in blocked3, "Single premium NOT blocked")
        
        # Test 8.4: All bots
        all_bots = [
            {"id": f"B{i}", "rps": 100 + i*50, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True}
            for i in range(5)
        ]
        blocked4 = self._run_episode(all_bots)
        self.assert_true(len(blocked4) >= 4, "Most bots blocked (all bots scenario)")
        
        # Test 8.5: All humans
        all_humans = [
            {"id": f"H{i}", "rps": 5 + i, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False}
            for i in range(5)
        ]
        blocked5 = self._run_episode(all_humans)
        self.assert_less_equal(len(blocked5), 1, "Almost no humans blocked (all humans scenario)")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _run_episode(self, dataset: List[Dict], agent=None) -> List[str]:
        """Run one episode and return blocked user IDs"""
        if agent is None:
            agent = self.agent
        
        env = make_env()
        observation = env.reset(dataset)
        blocked = []
        
        for _ in range(20):
            action = agent.select_action(observation)
            if action.get("type") == "block":
                user_id = action.get("user_id")
                if user_id and user_id not in blocked:
                    blocked.append(user_id)
            observation, _, done, _ = env.step(action)
            if done:
                break
        
        return blocked
    
    # ========================================================================
    # Run All Tests
    # ========================================================================
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("HARD DEFENDER AGENT - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print("\nTesting HardDefenderAgent with block_threshold=2.5")
        
        # Run all test suites
        self.test_risk_scoring()
        self.test_premium_protection()
        self.test_all_datasets()
        self.test_edge_cases()
        self.test_deterministic()
        self.test_threshold_sensitivity()
        self.test_adversarial()
        self.test_special_cases()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\n  Total Tests:  {self.total}")
        print(f"  Passed:       {self.passed} ✅")
        print(f"  Failed:       {self.failed} ❌")
        print(f"  Pass Rate:    {(self.passed/self.total*100):.1f}%")
        
        if self.failed == 0:
            print("\n  🎉 ALL TESTS PASSED! Agent is ready for submission!")
            return 0
        else:
            print(f"\n  ⚠️  {self.failed} test(s) failed. Review and fix before submission.")
            return 1


if __name__ == "__main__":
    tester = TestHardDefenderAgent()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
