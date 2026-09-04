import subprocess
import time
import sys

def main():
    print("🚀 Starting Global Algo Bot (Day & Night Autonomous System)...")
    
    # 1. Web Dashboard Server
    server_proc = subprocess.Popen([sys.executable, "server.py"])
    time.sleep(1)
    
    # 2. Day Trading Bot (main.py)
    bot_proc = subprocess.Popen([sys.executable, "main.py"])
    time.sleep(1)
    
    # 3. Night Learner & Strategy Optimizer (night_learner.py)
    learner_proc = subprocess.Popen([sys.executable, "night_learner.py"])
    
    try:
        server_proc.wait()
        bot_proc.wait()
        learner_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping all autonomous services...")
        server_proc.terminate()
        bot_proc.terminate()
        learner_proc.terminate()

if __name__ == "__main__":
    main()
