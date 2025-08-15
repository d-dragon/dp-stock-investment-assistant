# powershell: run with python .\test_agent.py
from core.data_manager import DataManager
from core.agent import StockAgent
from utils.config_loader import ConfigLoader

cfg = ConfigLoader.load_config(load_env=True)
dm = DataManager(cfg)
agent = StockAgent(cfg, dm)

print("=== Non-stream response ===")
print(agent._process_query("What is the current price of AAPL?"))

print("\n=== Streaming response ===")
for chunk in agent.process_query_streaming("Summarize recent news about AAPL"):
    print(chunk, end="", flush=True)
print()