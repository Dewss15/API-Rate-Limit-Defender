# 🎯 How to Increase Agent Accuracy

## 📊 **Current Baseline Performance**

Your heuristic agent (RPS > 50 + suspicious):
- Easy: F1 = 0.95+ ✅
- Medium: F1 = 0.70-0.80 ⚠️
- Winning: F1 = 0.65-0.75 ❌

**Goal: F1 > 0.80 on ALL levels**

---

## 🚀 **Strategy 1: Better Features (Feature Engineering)**

### Current Features (What Agent Sees)
```python
{
    "rps": 50,
    "is_suspicious_pattern": True,
    "tier": "premium"
}
```

### 🔧 **Add Derived Features**

```python
def extract_features(user, observation):
    """Extract better features from raw observation."""
    
    # Raw features
    rps = user["rps"]
    suspicious = int(user["is_suspicious_pattern"])
    is_premium = int(user["tier"] == "premium")
    
    # Normalized features (helps NN learn)
    rps_normalized = min(rps / 100.0, 1.0)  # Scale to [0, 1]
    
    # Interaction features (capture relationships)
    suspicious_high_rps = int(suspicious and rps > 50)
    safe_premium = int(is_premium and not suspicious)
    danger_score = rps_normalized * suspicious
    
    # Context features (from environment state)
    system_health = observation["system_health"]
    num_blocked = len(observation["blocked_users"])
    total_users = len(observation["users"])
    block_rate = num_blocked / total_users if total_users > 0 else 0
    
    # RPS bands (categorical features)
    rps_very_low = int(rps < 10)
    rps_low = int(10 <= rps < 30)
    rps_medium = int(30 <= rps < 50)
    rps_high = int(50 <= rps < 100)
    rps_very_high = int(rps >= 100)
    
    # Risk score (composite)
    risk_score = 0.0
    if rps > 100:
        risk_score += 0.5
    elif rps > 50:
        risk_score += 0.3
    
    if suspicious:
        risk_score += 0.3
    
    if is_premium:
        risk_score -= 0.4  # Lower risk (protected)
    
    return {
        # Raw
        "rps": rps,
        "suspicious": suspicious,
        "is_premium": is_premium,
        
        # Normalized
        "rps_norm": rps_normalized,
        
        # Interactions
        "suspicious_high_rps": suspicious_high_rps,
        "safe_premium": safe_premium,
        "danger_score": danger_score,
        
        # Context
        "system_health": system_health,
        "block_rate": block_rate,
        
        # Bands
        "rps_very_low": rps_very_low,
        "rps_low": rps_low,
        "rps_medium": rps_medium,
        "rps_high": rps_high,
        "rps_very_high": rps_very_high,
        
        # Composite
        "risk_score": risk_score
    }
```

**Why this helps:**
- Neural networks learn better with normalized inputs
- Interaction features capture relationships
- Context features provide situational awareness
- Risk score gives pre-computed signal

---

## 🧠 **Strategy 2: Progressive Training (Curriculum Learning)**

### ❌ **Don't Do This:**
```python
# Training on hardest data from start
for episode in range(1000):
    train_on(get_winning_data())  # Too hard! Won't learn!
```

### ✅ **Do This Instead:**
```python
# Curriculum Learning (Easy → Hard)

# Phase 1: Master the basics (500 episodes)
print("Phase 1: Learning basics on easy data...")
for episode in range(500):
    train_on(get_easy_data())
    
print(f"Easy F1: {evaluate_on(get_easy_data())}")  # Should be 0.95+

# Phase 2: Handle ambiguity (1000 episodes)
print("Phase 2: Learning overlap on medium data...")
for episode in range(1000):
    train_on(get_medium_data())
    
print(f"Medium F1: {evaluate_on(get_medium_data())}")  # Should be 0.80+

# Phase 3: Master edge cases (1500 episodes)
print("Phase 3: Mastering winning data...")
for episode in range(1500):
    train_on(get_winning_data())
    
print(f"Winning F1: {evaluate_on(get_winning_data())}")  # Should be 0.80+

# Phase 4: Mixed training (1000 episodes)
print("Phase 4: Mixed practice...")
for episode in range(1000):
    # Randomly pick dataset (80% winning, 20% medium/easy)
    import random
    if random.random() < 0.8:
        train_on(get_winning_data())
    elif random.random() < 0.5:
        train_on(get_medium_data())
    else:
        train_on(get_easy_data())
```

**Why this helps:**
- Agent learns simple patterns first
- Gradually increases difficulty
- Prevents overwhelming the agent early
- Final mixed training prevents forgetting

---

## 🎛️ **Strategy 3: Hyperparameter Tuning**

### For Q-Learning / DQN

```python
class ImprovedAgent:
    def __init__(self):
        # Learning rate (how fast to update)
        self.learning_rate = 0.001  # Start: 0.001, try: [0.0001, 0.0005, 0.001, 0.005]
        
        # Discount factor (how much to value future rewards)
        self.gamma = 0.95  # Start: 0.95, try: [0.90, 0.95, 0.99]
        
        # Exploration vs exploitation
        self.epsilon_start = 1.0    # Start with full exploration
        self.epsilon_end = 0.01     # End with 1% exploration
        self.epsilon_decay = 0.995  # Decay rate
        
        # Experience replay (for DQN)
        self.buffer_size = 10000    # Try: [5000, 10000, 50000]
        self.batch_size = 64        # Try: [32, 64, 128]
        
        # Network architecture (for DQN)
        self.hidden_layers = [128, 64]  # Try: [64], [128, 64], [256, 128, 64]
        
        # Update frequency
        self.target_update_freq = 100  # Update target network every N episodes
```

### For Policy Gradient (PPO)

```python
class PPOAgent:
    def __init__(self):
        # Learning rate
        self.lr = 0.0003  # Try: [0.0001, 0.0003, 0.001]
        
        # PPO clipping
        self.clip_epsilon = 0.2  # Try: [0.1, 0.2, 0.3]
        
        # Entropy coefficient (exploration)
        self.entropy_coef = 0.01  # Try: [0.0, 0.01, 0.1]
        
        # Value function coefficient
        self.value_coef = 0.5
        
        # GAE lambda (advantage estimation)
        self.gae_lambda = 0.95
        
        # Mini-batch size
        self.batch_size = 64
        
        # Epochs per update
        self.n_epochs = 10
```

---

## 🎯 **Strategy 4: Smarter Decision Rules**

### Level 1: Simple Threshold
```python
def select_action_v1(user):
    """Too simple - fails on hard data."""
    if user["rps"] > 50 and user["is_suspicious_pattern"]:
        return "block"
    return "skip"
```

### Level 2: Tier-Aware
```python
def select_action_v2(user):
    """Better - protects premium."""
    if user["tier"] == "premium":
        return "skip"  # NEVER block premium
    
    if user["rps"] > 50 and user["is_suspicious_pattern"]:
        return "block"
    return "skip"
```

### Level 3: Multi-Threshold
```python
def select_action_v3(user):
    """Better - handles edge cases."""
    # Never block premium
    if user["tier"] == "premium":
        return "skip"
    
    # Very confident
    if user["rps"] > 100 and user["is_suspicious_pattern"]:
        return "block"
    
    # Medium confidence
    if user["rps"] > 50 and user["is_suspicious_pattern"]:
        return "block"
    
    # Stealth bot detection
    if user["rps"] > 30 and user["is_suspicious_pattern"]:
        return "block"
    
    return "skip"
```

### Level 4: Confidence-Based (RL Agent)
```python
def select_action_v4(user, observation):
    """Best - uses ML to learn optimal threshold."""
    features = extract_features(user, observation)
    
    # Get Q-values or policy probabilities
    block_confidence = model.predict(features)
    
    # Never block premium (hard constraint)
    if user["tier"] == "premium":
        return "skip"
    
    # Adaptive threshold based on system state
    if observation["system_health"] < 0.8:
        threshold = 0.6  # More conservative
    else:
        threshold = 0.7  # Normal
    
    if block_confidence > threshold:
        return "block"
    return "skip"
```

---

## 📈 **Strategy 5: Evaluation-Driven Improvement**

### Track Multiple Metrics

```python
def evaluate_agent(agent, dataset):
    """Comprehensive evaluation."""
    from environment import make_env
    from grader import Grader
    
    env = make_env()
    obs = env.reset(dataset)
    done = False
    
    while not done:
        action = agent.select_action(obs)
        obs, reward, done, info = env.step(action)
    
    # Get grader results
    grader = Grader()
    results = grader.grade(info["blocked_ids"], dataset)
    
    # Print detailed breakdown
    print(f"TP: {results['TP']}, FP: {results['FP']}, FN: {results['FN']}, TN: {results['TN']}")
    print(f"Precision: {results['precision']:.3f}")
    print(f"Recall: {results['recall']:.3f}")
    print(f"F1: {results['f1']:.3f}")
    print(f"System Health: {results['system_health']:.3f}")
    print(f"Premium Penalties: {results['premium_penalty']}")
    print(f"Score: {results['score']:.3f}")
    
    # Identify weaknesses
    if results['FP'] > results['FN']:
        print("⚠️  Too aggressive - blocking too many humans")
    elif results['FN'] > results['FP']:
        print("⚠️  Too conservative - missing too many bots")
    
    if results['premium_penalty'] > 0:
        print(f"❌ CRITICAL: Blocked {results['premium_penalty']} premium users!")
    
    return results
```

### Compare Strategies

```python
from easy_defender_agent import EasyDefenderAgent
from medium_defender_agent import MediumDefenderAgent
from hard_defender_agent import HardDefenderAgent

# Test different agents
agents = {
    "Easy-Agent": EasyDefenderAgent(),
    "Medium-Agent": MediumDefenderAgent(),
    "Hard-Agent": HardDefenderAgent(),
}

for name, agent in agents.items():
    print(f"\n=== {name} ===")
    results = evaluate_agent(agent, get_winning_data())
```

---

## 🔧 **Strategy 6: Debugging & Error Analysis**

### Identify Failure Cases

```python
def analyze_mistakes(agent, dataset):
    """Find which users the agent gets wrong."""
    from environment import make_env
    
    env = make_env()
    obs = env.reset(dataset)
    done = False
    
    actions_taken = []
    while not done:
        action = agent.select_action(obs)
        actions_taken.append(action)
        obs, reward, done, info = env.step(action)
    
    blocked_ids = set(info["blocked_ids"])
    
    # Analyze each user
    false_positives = []  # Humans we blocked
    false_negatives = []  # Bots we missed
    
    for user in dataset:
        is_blocked = user["id"] in blocked_ids
        is_bot = user["is_bot"]
        
        if is_blocked and not is_bot:
            false_positives.append(user)
        elif not is_blocked and is_bot:
            false_negatives.append(user)
    
    # Print analysis
    print(f"\n❌ False Positives ({len(false_positives)}):")
    for user in false_positives:
        print(f"   {user['id']}: RPS={user['rps']}, suspicious={user['is_suspicious_pattern']}, tier={user['tier']}")
        if user['tier'] == 'premium':
            print(f"      ⚠️  PREMIUM - very expensive mistake!")
    
    print(f"\n❌ False Negatives ({len(false_negatives)}):")
    for user in false_negatives:
        print(f"   {user['id']}: RPS={user['rps']}, suspicious={user['is_suspicious_pattern']}")
    
    # Find patterns
    print(f"\n📊 Pattern Analysis:")
    if false_positives:
        fp_rps = [u['rps'] for u in false_positives]
        print(f"   FP RPS range: {min(fp_rps)}-{max(fp_rps)}, avg={sum(fp_rps)/len(fp_rps):.1f}")
    
    if false_negatives:
        fn_rps = [u['rps'] for u in false_negatives]
        print(f"   FN RPS range: {min(fn_rps)}-{max(fn_rps)}, avg={sum(fn_rps)/len(fn_rps):.1f}")
```

**Usage:**
```python
from data import get_winning_data
from hard_defender_agent import HardDefenderAgent

agent = HardDefenderAgent()
analyze_mistakes(agent, get_winning_data())
```

---

## 🎓 **Strategy 7: Algorithm Selection**

### Option 1: Q-Learning (Simple, Good Start)
```python
class QLearningAgent:
    """Learn Q-values for state-action pairs."""
    
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.1   # Learning rate
        self.gamma = 0.95  # Discount factor
        self.epsilon = 0.1 # Exploration
    
    def get_state_key(self, user):
        """Discretize continuous features."""
        rps_band = "low" if user["rps"] < 30 else "medium" if user["rps"] < 50 else "high"
        return (rps_band, user["is_suspicious_pattern"], user["tier"])
    
    def select_action(self, obs):
        import random
        for user in obs["users"]:
            if user["id"] in obs["blocked_users"]:
                continue
            
            state = self.get_state_key(user)
            
            # Epsilon-greedy
            if random.random() < self.epsilon:
                action = random.choice(["block", "skip"])
            else:
                q_block = self.q_table.get((state, "block"), 0)
                q_skip = self.q_table.get((state, "skip"), 0)
                action = "block" if q_block > q_skip else "skip"
            
            if action == "block":
                return {"type": "block", "user_id": user["id"]}
        
        return {"type": "noop"}
    
    def update(self, state, action, reward, next_state):
        """Update Q-value."""
        old_q = self.q_table.get((state, action), 0)
        next_max_q = max(
            self.q_table.get((next_state, "block"), 0),
            self.q_table.get((next_state, "skip"), 0)
        )
        new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
        self.q_table[(state, action)] = new_q
```

### Option 2: DQN (Deep Q-Network, Better for Complex Features)
```python
import torch
import torch.nn as nn

class DQNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, x):
        return self.fc(x)

class DQNAgent:
    """Use neural network to approximate Q-values."""
    
    def __init__(self, state_dim=10, action_dim=2):
        self.model = DQNetwork(state_dim, action_dim)
        self.target_model = DQNetwork(state_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = []
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
    
    def select_action(self, obs):
        # Extract features and predict
        # ... implementation
        pass
```

### Option 3: Imitation Learning (Learn from Expert)
```python
def collect_expert_demonstrations():
    """Collect data from optimal heuristic."""
    from environment import make_env
    from data import get_easy_data, get_medium_data, get_winning_data
    
    # Use your best heuristic as expert
    class ExpertAgent:
        def select_action(self, obs):
            for user in obs["users"]:
                if user["id"] in obs["blocked_users"]:
                    continue
                
                # Never block premium
                if user["tier"] == "premium":
                    continue
                
                # Expert rules
                if user["rps"] > 60 and user["is_suspicious_pattern"]:
                    return {"type": "block", "user_id": user["id"]}
            
            return {"type": "noop"}
    
    expert = ExpertAgent()
    demonstrations = []
    
    for dataset_fn in [get_easy_data, get_medium_data, get_winning_data]:
        data = dataset_fn()
        env = make_env()
        obs = env.reset(data)
        done = False
        
        while not done:
            action = expert.select_action(obs)
            next_obs, reward, done, info = env.step(action)
            
            # Store (state, action) pairs
            demonstrations.append((obs, action))
            obs = next_obs
    
    return demonstrations
```

---

## 🎯 **Strategy 8: Specific Improvements for Each Metric**

### To Increase Precision (Reduce False Positives)
```python
# Be more conservative
✅ Increase RPS threshold (50 → 60 → 70)
✅ Require BOTH high RPS AND suspicious pattern
✅ Add confidence threshold
✅ NEVER block premium (already doing this)
```

### To Increase Recall (Reduce False Negatives)
```python
# Be more aggressive
✅ Decrease RPS threshold (50 → 40 → 30)
✅ Block on suspicious pattern even with medium RPS
✅ Look for stealth bots (low RPS but suspicious)
```

### To Increase F1 (Balance Both)
```python
# Find optimal threshold
✅ Use validation set to tune threshold
✅ Try multiple thresholds: [30, 40, 50, 60, 70]
✅ Pick one with best F1
```

### To Increase System Health
```python
# Minimize FP + FN
✅ Focus on high-confidence decisions
✅ Skip ambiguous cases
✅ Prioritize precision over recall slightly
```

---

## 🚀 **Complete Training Recipe**

```python
# agent_training.py

from environment import make_env
from data import get_easy_data, get_medium_data, get_winning_data
from grader import Grader

def train_curriculum():
    """Complete training pipeline."""
    
    # 1. Initialize agent
    agent = QLearningAgent()  # or DQNAgent()
    
    # 2. Phase 1: Easy (500 episodes)
    print("=== Phase 1: Easy ===")
    for episode in range(500):
        data = get_easy_data()
        env = make_env()
        obs = env.reset(data)
        done = False
        
        while not done:
            action = agent.select_action(obs)
            next_obs, reward, done, info = env.step(action)
            agent.update(obs, action, reward, next_obs)
            obs = next_obs
        
        if episode % 100 == 0:
            results = evaluate(agent, get_easy_data())
            print(f"Episode {episode}: F1 = {results['f1']:.3f}")
    
    # 3. Phase 2: Medium (1000 episodes)
    print("\n=== Phase 2: Medium ===")
    for episode in range(1000):
        data = get_medium_data()
        env = make_env()
        obs = env.reset(data)
        done = False
        
        while not done:
            action = agent.select_action(obs)
            next_obs, reward, done, info = env.step(action)
            agent.update(obs, action, reward, next_obs)
            obs = next_obs
        
        if episode % 200 == 0:
            results = evaluate(agent, get_medium_data())
            print(f"Episode {episode}: F1 = {results['f1']:.3f}")
    
    # 4. Phase 3: Winning (1500 episodes)
    print("\n=== Phase 3: Winning ===")
    for episode in range(1500):
        data = get_winning_data()
        env = make_env()
        obs = env.reset(data)
        done = False
        
        while not done:
            action = agent.select_action(obs)
            next_obs, reward, done, info = env.step(action)
            agent.update(obs, action, reward, next_obs)
            obs = next_obs
        
        if episode % 300 == 0:
            results = evaluate(agent, get_winning_data())
            print(f"Episode {episode}: F1 = {results['f1']:.3f}")
    
    # 5. Final evaluation
    print("\n=== Final Evaluation ===")
    for name, data_fn in [("Easy", get_easy_data), ("Medium", get_medium_data), ("Winning", get_winning_data)]:
        results = evaluate(agent, data_fn())
        print(f"{name}: F1 = {results['f1']:.3f}, Score = {results['score']:.3f}")
    
    return agent

def evaluate(agent, dataset):
    """Evaluate agent on dataset."""
    from grader import Grader
    env = make_env()
    obs = env.reset(dataset)
    done = False
    
    while not done:
        action = agent.select_action(obs)
        obs, reward, done, info = env.step(action)
    
    grader = Grader()
    return grader.grade(info["blocked_ids"], dataset)

if __name__ == "__main__":
    agent = train_curriculum()
    print("Training complete!")
```

---

## ✅ **Checklist for High Accuracy**

- [ ] **Feature engineering** (normalized RPS, interaction features)
- [ ] **Progressive training** (easy → medium → winning)
- [ ] **Hyperparameter tuning** (learning rate, epsilon, thresholds)
- [ ] **Error analysis** (identify failure cases)
- [ ] **Premium protection** (NEVER block premium)
- [ ] **Confidence-based decisions** (not binary)
- [ ] **Multiple evaluation runs** (ensure consistency)
- [ ] **Target: F1 > 0.80 on all datasets**

---

## 🏆 **Expected Improvement Timeline**

| Week | Improvement | F1 (Winning) |
|------|-------------|--------------|
| **Week 1** | Baseline heuristic | 0.70 |
| **Week 2** | Feature engineering | 0.75 |
| **Week 3** | Curriculum learning | 0.78 |
| **Week 4** | Hyperparameter tuning | 0.82 ✅ |
| **Week 5** | Error analysis & refinement | 0.85 🎯 |

---

## 🎬 **Quick Start: Run Error Analysis**

```bash
# Create analysis script
python analyze_mistakes.py

# Output will show:
# - Which users you got wrong
# - Patterns in false positives/negatives
# - Suggestions for threshold tuning
```

---

## 📚 **Key Insights**

### 1. **Premium Users are CRITICAL**
- Blocking 1 premium = -1.5 reward
- Blocking 3 premiums = equivalent to missing 11 bots
- **Rule: NEVER block premium users under any circumstance**

### 2. **RPS Threshold Matters**
- Too low (30): High recall, low precision → many FP
- Too high (70): Low recall, high precision → many FN
- Sweet spot: 50-60 depending on suspicious pattern

### 3. **Suspicious Pattern is Key**
- High RPS alone is not enough
- Suspicious pattern alone is not enough
- Best: BOTH together (85%+ confidence bot)

### 4. **System Health Drives Score**
- system_health = 1 - ((FP + FN) / total_users)
- Every mistake (FP or FN) reduces health
- Health < 0.8 loses the +0.1 bonus

---

## 🐛 **Common Mistakes to Avoid**

❌ **Training only on winning data** → Agent never learns basics  
✅ **Use curriculum learning** → Easy → Medium → Winning

❌ **Ignoring premium users** → Huge penalty  
✅ **Hard constraint: Never block premium**

❌ **Binary decisions (always block or never block)** → Misses nuance  
✅ **Confidence-based thresholds** → Block only when confident

❌ **Not tracking metrics during training** → Flying blind  
✅ **Log F1, precision, recall every N episodes**

❌ **Overfitting to one dataset** → Fails on others  
✅ **Validate on all 3 datasets** → Easy, Medium, Winning

---

## 💡 **Pro Tips**

1. **Start with heuristics, then add ML**
   - Get baseline with smart rules
   - Use ML to optimize thresholds
   
2. **Use error analysis to guide improvement**
   - Find common patterns in failures
   - Add features to capture those patterns
   
3. **Ensemble multiple agents**
   - Conservative agent (high precision)
   - Aggressive agent (high recall)
   - Combine predictions
   
4. **Save checkpoints**
   - Save agent every 100 episodes
   - Keep best performing version
   - Can always roll back if performance drops

---

**Remember:** Start simple, iterate, measure, improve! 🚀

**Questions?** Run `analyze_mistakes.py` to see exactly what your agent is doing wrong!
