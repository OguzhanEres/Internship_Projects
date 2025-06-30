#!/usr/bin/env python3
import sys, subprocess,argparse,logging
from datetime import datetime


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Project1/log/btrfs_snapshot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def run(cmd:list):
    logging.debug("Çalışıyor: %s", ' '.join(cmd))
    p=subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        logging.error("Komut başarısız: %s", ' '.join(cmd))
        logging.error("Hata mesajı: %s", p.stderr.strip())
        sys.exit(1)
    logging.info("Komut başarılı: %s", ' '.join(cmd))
    return p.stdout.strip() 


def create_snapshot(source,dest_dir):
    ts=datetime.now().strftime("%Y%m%d-%H%M%S")
    snap=f"{dest_dir}/snapshot-{ts}"
    run(["sudo","btrfs", "subvolume", "snapshot", source, snap])
    logging.info("Anlık görüntü oluşturuldu: %s", snap)
    
def rollback_snapshot(snap,target):
    run(["sudo","btrfs","subvolume","delete",target])
    run(["sudo","btrfs","subvolume","delete",snap,target])
    logging.info("Anlık görüntü geri yüklendi: %s", snap,target)
    
    
def parse_args():
    parser = argparse.ArgumentParser(description="Btrfs anlık görüntü yönetimi")
    sub=parser.add_subparsers(dest='cmd', required=True)
    p1=sub.add_parser("snap")
    p1.add_argument("source", help="Anlık görüntü alınacak kaynak dizin")
    p1.add_argument("dest_dir", help="Anlık görüntünün kaydedileceği dizin")
    p2=sub.add_parser("rollback")
    p2.add_argument("snap", help="Geri yüklenecek anlık görüntü")
    p2.add_argument("target", help="Geri yüklenecek hedef dizin")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.cmd == "snap":
        create_snapshot(args.source, args.dest_dir)
    elif args.cmd == "rollback":
        rollback_snapshot(args.snap, args.target)

if __name__ == "__main__":
    main()