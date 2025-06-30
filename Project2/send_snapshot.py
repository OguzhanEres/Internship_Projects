import subprocess
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / "Config.env")

SOURCE_DIR=os.getenv("SOURCE_DIR")
SNAPSHOT_DIR=os.getenv("SNAPSHOT_DIR")
REMOTE_USER = os.getenv("REMOTE_USER")
REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_DIR = os.getenv("REMOTE_DIR")
LOG_FILE = os.getenv("LOG_FILE")

def run(cmd, shell=False):
    try:
        result= subprocess.run(cmd,capture_output=True, text=True, shell=True)
        with open(LOG_FILE,'a') as f:
            if shell:
                f.write(f"$ {cmd}\n")
            else:
                f.write(f"$ {' '.join(cmd)}\n")
            f.write(f"{result.stdout}")
            if result.stderr and result.returncode != 0:
                f.write(f"Error: {result.stderr}\n")
            elif result.stderr:
                f.write(f"Stderr: {result.stderr}\n")

        return result
    except Exception as e:
        with open(LOG_FILE, 'a') as f:
            f.write(f"Hata: {str(e)}\n")
        raise
    
def create_snapshot():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_path = f"{SNAPSHOT_DIR}/snapshot-{ts}"
    
    
    cmd = f"sudo btrfs subvolume snapshot -r {SOURCE_DIR} {snapshot_path}"
    run(cmd, shell=True)

    return snapshot_path


def send_snapshot(snapshot_path):
    cmd = (
    f"sudo btrfs send {snapshot_path} | "
    f"ssh {REMOTE_USER}@{REMOTE_HOST} "
    f"'sudo btrfs receive {REMOTE_DIR}'"
    )
    run(cmd, shell=True)

    
    
def main():
    
    try:
        variables={
            "SOURCE_DIR": SOURCE_DIR,
            "SNAPSHOT_DIR": SNAPSHOT_DIR,
            "REMOTE_USER": REMOTE_USER,
            "REMOTE_HOST": REMOTE_HOST,
            "REMOTE_DIR": REMOTE_DIR,
            "LOG_FILE": LOG_FILE
        }
        for var in variables:
            if not variables[var]:
                raise ValueError(f"{var} tanımlı değil")
        
        start_time =datetime.now()
        with open(LOG_FILE, "a") as f:
            f.write(f"\n Yedekleme başladı : {start_time.strftime('%Y-%m-%d %H:%M:%S')})\n")
        snapshot_path = create_snapshot()
        send_snapshot(snapshot_path)
        
        
        
        end_time = datetime.now()
        duration = end_time - start_time
        with open(LOG_FILE, "a") as f:
            f.write(f"Yedekleme bitti {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Süre: {duration}\n")
            f.write(f"Snapshot oluşturuldu: {snapshot_path}\n")
            f.write("Yedekleme başarılı.\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"HATA: {str(e)}\n")
        raise
    
if __name__ == "__main__":
    main()          