"""
命令行入口：直接训练并输出预测结果
用法：python main.py --ticker AAPL --epochs 100
"""
import argparse
from src.trainer import train

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="股票 LSTM 预测")
    parser.add_argument("--ticker",  default="AAPL", help="股票代码")
    parser.add_argument("--window",  type=int, default=60, help="回看窗口天数")
    parser.add_argument("--epochs",  type=int, default=100, help="最大训练轮数")
    args = parser.parse_args()

    result = train(args.ticker, window=args.window, epochs=args.epochs)
    print(f"\n训练完成 | MAE={result['mae']:.4f}  RMSE={result['rmse']:.4f}  MAPE={result['mape']:.2f}%")
