from safeagents import Dataset
# Point to a previous run
dataset = Dataset(
    name="ai-safety-institute/AgentHarm",
    config="harmful",
    framework="openai-agents",
    architecture="centralized",
    log_dir="./logs/ai-safety-institute_AgentHarm_20260106_152727_gpt5"  # Previous run
)

# No need to load() or run()!
dataset.print_summary()  # Loads results from disk