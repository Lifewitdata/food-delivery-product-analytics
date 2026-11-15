"""Run additive local product analytics outputs in dependency order."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=[
 [sys.executable,"-m","scripts.build_product_sessions"],
 [sys.executable,"-m","scripts.analyze_product_funnel"],
 [sys.executable,"-m","scripts.build_unit_economics"],
 [sys.executable,"-m","scripts.build_customer_lifecycle"],
 [sys.executable,"-m","scripts.build_delivery_risk"],
]
def main():
    for command in COMMANDS:
        print("\\n>>>"," ".join(command),flush=True)
        subprocess.run(command,cwd=ROOT,check=True)
    print("\\nAll additive product analytics outputs generated.")
if __name__=="__main__":main()
