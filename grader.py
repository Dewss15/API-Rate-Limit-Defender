"""
grader.py - OpenEnv Compliance Grader

CRITICAL: This grader MUST match evaluator.py EXACTLY.
Formula and metrics must be identical for hackathon submission.
"""

from typing import Dict, List, Any


class Grader:
    """
    Official grader that mirrors Anchal's evaluator.py logic.
    
    This ensures consistency between environment training and final evaluation.
    DO NOT modify the formula - it must match the evaluator exactly.
    """
    
    def __init__(self):
        """Initialize the grader."""
        pass
    
    def grade(self, blocked_users: List[str], users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grade agent performance using EXACT evaluator.py formula.
        
        Args:
            blocked_users: List of user IDs that were blocked
            users: Complete user dataset including is_bot ground truth
            
        Returns:
            Dict with metrics matching evaluator.py output
        """
        # Initialize counters
        TP = 0  # True Positives: bots correctly blocked
        FP = 0  # False Positives: humans incorrectly blocked
        FN = 0  # False Negatives: bots not blocked
        TN = 0  # True Negatives: humans not blocked
        
        total_users = len(users)
        premium_penalty = 0
        
        # Filter invalid IDs (match evaluator.py behavior)
        valid_ids = {user["id"] for user in users}
        blocked_users = [uid for uid in blocked_users if uid in valid_ids]
        
        # Calculate TP, FP, FN, TN
        for user in users:
            is_blocked = user["id"] in blocked_users
            
            if user["is_bot"]:
                if is_blocked:
                    TP += 1
                else:
                    FN += 1
            else:
                if is_blocked:
                    FP += 1
                    # Track premium penalty (matches evaluator.py)
                    if user["tier"] == "premium":
                        premium_penalty += 1
                else:
                    TN += 1
        
        # Calculate precision, recall, F1 (EXACT evaluator.py logic)
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        # Calculate system health (EXACT evaluator.py formula)
        system_health = 1.0 - ((FN + FP) / total_users)
        
        # Calculate final score (EXACT evaluator.py formula)
        # score = (0.6 * f1) + (0.3 * system_health) - (0.1 * (premium_penalty / total_users))
        premium_penalty_rate = premium_penalty / total_users if total_users > 0 else 0.0
        score = (0.6 * f1) + (0.3 * system_health) - (0.1 * premium_penalty_rate)
        
        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        
        # Return results matching evaluator.py format
        return {
            "TP": TP,
            "FP": FP,
            "FN": FN,
            "TN": TN,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "system_health": system_health,
            "premium_penalty": premium_penalty,
            "score": score,
            "total_users": total_users
        }
    
    def validate_against_evaluator(self, blocked_users: List[str], users: List[Dict[str, Any]]) -> bool:
        """
        Validate that grader output matches evaluator.py.
        
        Args:
            blocked_users: List of blocked user IDs
            users: Complete user dataset
            
        Returns:
            True if results match within floating point tolerance
        """
        try:
            from evaluator import evaluate
            
            grader_result = self.grade(blocked_users, users)
            evaluator_result = evaluate(blocked_users, users)
            
            # Compare key metrics
            tolerance = 1e-6
            
            checks = [
                ("TP", grader_result["TP"] == evaluator_result["TP"]),
                ("FP", grader_result["FP"] == evaluator_result["FP"]),
                ("FN", grader_result["FN"] == evaluator_result["FN"]),
                ("precision", abs(grader_result["precision"] - evaluator_result["precision"]) < tolerance),
                ("recall", abs(grader_result["recall"] - evaluator_result["recall"]) < tolerance),
                ("f1", abs(grader_result["f1"] - evaluator_result["f1"]) < tolerance),
                ("system_health", abs(grader_result["system_health"] - evaluator_result["system_health"]) < tolerance),
                ("score", abs(grader_result["score"] - evaluator_result["score"]) < tolerance),
            ]
            
            all_passed = all(result for _, result in checks)
            
            if not all_passed:
                print("❌ Grader validation FAILED:")
                for name, passed in checks:
                    status = "✅" if passed else "❌"
                    print(f"  {status} {name}")
                    if not passed:
                        print(f"     Grader: {grader_result.get(name)}")
                        print(f"     Evaluator: {evaluator_result.get(name)}")
            
            return all_passed
            
        except ImportError:
            print("⚠️  Cannot validate: evaluator.py not found")
            return False


def verify_grader():
    """Verify grader matches evaluator.py on sample data."""
    from data import get_easy_data
    
    grader = Grader()
    data = get_easy_data()
    
    # Test case: Block all users with RPS > 100
    blocked = [u["id"] for u in data if u["rps"] > 100]
    
    result = grader.grade(blocked, data)
    
    print("=== Grader Verification ===")
    print(f"Blocked: {len(blocked)} users")
    print(f"TP={result['TP']}, FP={result['FP']}, FN={result['FN']}, TN={result['TN']}")
    print(f"F1={result['f1']:.4f}, Health={result['system_health']:.4f}")
    print(f"Score={result['score']:.4f}")
    
    # Validate against evaluator
    if grader.validate_against_evaluator(blocked, data):
        print("✅ Grader matches evaluator.py EXACTLY")
    else:
        print("❌ Grader MISMATCH - fix required!")


if __name__ == "__main__":
    verify_grader()
