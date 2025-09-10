from src.core.data_manager import DataManager
from src.utils.config_loader import ConfigLoader

cfg = ConfigLoader.load_config(load_env=True)
dm = DataManager(cfg)
print(dm.get_stock_info("AAPL"))
df = dm.get_stock_data("AAPL", period="1mo", interval="1d")
print(df.head() if df is not None else "No data")