import matplotlib.pyplot as plt
from environment import ChakravyuhaEnvironment
from agent import random_agent, SmartChakravyuhaAgent

def evaluate_agents(episodes=100):
    information_levels = ["LOW", "MEDIUM", "HIGH"]
    
    # Store success rates for both agents
    random_success_rates = []
    smart_success_rates = []

    print(f"Running Final Experiment: {episodes} episodes per Information Level\n" + "-"*50)

    for info in information_levels:
        random_successes = 0
        smart_successes = 0

        # --- Test Random Agent ---
        for _ in range(episodes):
            env = ChakravyuhaEnvironment(information=info)
            obs = env.reset()
            while not obs["terminal"]:
                action = random_agent(obs)
                obs = env.step(action)
            if obs["success"]:
                random_successes += 1
                
        # --- Test Smart AI Agent ---
        smart_agent = SmartChakravyuhaAgent()
        for _ in range(episodes):
            env = ChakravyuhaEnvironment(information=info)
            obs = env.reset()
            smart_agent.reset() # Clear memory for new episode
            while not obs["terminal"]:
                action, _ = smart_agent.choose_action(obs)
                obs = env.step(action)
            if obs["success"]:
                smart_successes += 1

        # Calculate averages for this information level
        random_rate = (random_successes / episodes) * 100
        smart_rate = (smart_successes / episodes) * 100
        
        random_success_rates.append(random_rate)
        smart_success_rates.append(smart_rate)

        print(f"Information Level: {info}")
        print(f"Random Agent Success: {random_rate}%")
        print(f"Smart AI Success:     {smart_rate}%\n")

    # --- Generate final comparison chart ---
    x = range(len(information_levels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    bars1 = plt.bar([i - width/2 for i in x], random_success_rates, width, label='Random Agent', color='#e74c3c')
    bars2 = plt.bar([i + width/2 for i in x], smart_success_rates, width, label='Smart AI', color='#2ecc71')

    plt.title('AI Performance Under Incomplete Information', fontsize=14)
    plt.xlabel('Information Access Level', fontsize=12)
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.xticks(x, information_levels)
    plt.legend()
    plt.ylim(0, 100)

    # Add percentages on top of bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    # Saving directly to your desktop like last time
    plt.savefig('/Users/tara/Desktop/final_comparison_chart.png')
    
    print("-" * 50)
    print("✅ Final experiment complete! Chart saved as 'final_comparison_chart.png' on your Desktop.")

if __name__ == "__main__":
    evaluate_agents(episodes=100)