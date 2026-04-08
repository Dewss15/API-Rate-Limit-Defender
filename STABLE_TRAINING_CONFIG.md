# Stable Training Configuration

This configuration is more conservative and should train stably.

## Changes to make in train_dqn.py

```python
# Line 577-587: Create agent with MORE STABLE settings
agent = DQNAgent(
    input_dim=3,
    hidden_dim=128,           # ← Increased from 64 (more capacity)
    learning_rate=0.0003,     # ← Lower (was 0.001) for stability
    gamma=0.95,
    epsilon_start=1.0,
    epsilon_end=0.05,         # ← Higher (was 0.01) for more exploration
    epsilon_decay=0.998,      # ← Slower (was 0.995) for gradual learning
    buffer_capacity=10000,
    batch_size=32,            # ← Smaller (was 64) for stability
    device=None
)

# Line 594-602: Use curriculum with better pacing
train_curriculum(
    agent,
    easy_episodes=200,        # ← Double (was 100) for better foundation
    medium_episodes=300,      # ← Balanced (was 400)
    winning_episodes=300,     # ← Shorter (was 500) to prevent overfitting
    target_update_freq=20,    # ← Slower (was 10) for stability
    validation_freq=50,
    save_path="best_model.pt"
)
```

## Why These Changes Help

1. **Lower learning rate (0.0003):** Smaller steps = more stable
2. **Larger network (128):** More capacity to learn subtle patterns
3. **Slower epsilon decay (0.998):** More exploration = better generalization
4. **Smaller batch size (32):** Less variance in gradient updates
5. **More easy episodes (200):** Better foundation before hard cases
6. **Slower target updates (20):** More stable Q-learning

## Expected Results

With these settings:
- Training should be STABLE (no collapse)
- Loss should DECREASE steadily
- F1 should IMPROVE gradually
- Final F1: 0.75-0.80 (better than 0.711)

## Time Cost

- GPU: ~45 minutes (800 episodes total)
- CPU: ~2 hours

## When to Use This

Only if you have time and want to try for better performance.
If deadline is soon, use your original model (it already passes!).
