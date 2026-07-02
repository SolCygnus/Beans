#!/usr/bin/env python3

import argparse
import hashlib
import sys


HASH_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def detect_hash_algorithm(known_hash: str) -> str | None:
    return {
        32: "md5",
        40: "sha1",
        56: "sha224",
        64: "sha256",
        96: "sha384",
        128: "sha512",
    }.get(len(known_hash))


def calculate_hash(file_path: str, algorithm: str) -> str:
    try:
        hash_func = HASH_ALGORITHMS[algorithm]()
    except KeyError as exc:
        raise SystemExit(f"Unsupported hash algorithm: {algorithm}") from exc
    with open(file_path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            hash_func.update(chunk)
    return hash_func.hexdigest()


def calculate_all_hashes(file_path: str) -> dict[str, str]:
    with open(file_path, "rb") as handle:
        payload = handle.read()
    hashes: dict[str, str] = {}
    for name, hash_func in HASH_ALGORITHMS.items():
        digest = hash_func()
        digest.update(payload)
        hashes[name] = digest.hexdigest()
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify or print common file hashes.")
    parser.add_argument("file_path")
    parser.add_argument("--hash")
    args = parser.parse_args()

    if args.hash:
        algorithm = detect_hash_algorithm(args.hash)
        if not algorithm:
            print("Could not infer the hash algorithm from the supplied digest.")
            return 1
        actual = calculate_hash(args.file_path, algorithm)
        if actual == args.hash:
            print(f"[PASS] {algorithm} matched for {args.file_path}")
            return 0
        print(f"[FAIL] expected {args.hash} but got {actual}")
        return 1

    for name, value in calculate_all_hashes(args.file_path).items():
        print(f"{name.upper()}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
