from safeagents import Dataset

# Load AgentHarm benchmark
dataset = Dataset(
    name="asb",
    config="financial_analyst_agent",  # Specific agent
    split="test",
    framework="openai-agents",
    architecture="centralized",
    indices=None,  # Run first 3 tasks
    max_turns=30
).load()

# Run with automatic safety assessment
results = dataset.run(

    assessment=["aria", "dharma"],
    progress_bar=True
)

# View summary with score distributions
dataset.print_summary()