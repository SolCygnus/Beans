# Hash Checking

A cryptographic hash is a fingerprint calculated from a file's contents. Hashes help confirm that a download was not corrupted or changed. Beans provides the `beans-hash-check` command.

> [!important]
> A matching hash verifies that two file contents are identical. It does not prove that a file is safe unless the expected hash came from a trusted source.

## Check That the Command Is Available

```bash
beans-hash-check --help
```

## Print a File's Hashes

```bash
beans-hash-check "download.iso"
```

Beans prints the file's MD5, SHA-1, SHA-224, SHA-256, SHA-384, and SHA-512 values.

For paths containing spaces, use quotation marks:

```bash
beans-hash-check "$HOME/Downloads/example file.zip"
```

## Verify a Published Hash

Copy the expected digest from a trusted source and provide it with `--hash`:

```bash
beans-hash-check "download.iso" --hash 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

Beans identifies the algorithm from the digest length and reports either `[PASS]` or `[FAIL]`.

Supported digest lengths:

| Algorithm | Characters |
|---|---:|
| MD5 | 32 |
| SHA-1 | 40 |
| SHA-224 | 56 |
| SHA-256 | 64 |
| SHA-384 | 96 |
| SHA-512 | 128 |

Use the digest exactly as published. Lowercase hexadecimal is recommended.

## Common Linux Hash Commands

The standard Linux utilities are useful when only one algorithm is needed:

```bash
sha256sum "download.iso"
sha512sum "download.iso"
md5sum "download.iso"
```

Verify a SHA-256 checksum file supplied by a publisher:

```bash
sha256sum --check SHA256SUMS
```

Verify one expected SHA-256 value without Beans:

```bash
echo "EXPECTED_SHA256  download.iso" | sha256sum --check
```

> [!warning]
> MD5 and SHA-1 are no longer considered collision-resistant. Use SHA-256 or SHA-512 when choosing an algorithm, while still using an older algorithm when a trusted publisher only supplies that value.

## A Safe Download-Verification Workflow

1. Download the file from the official source.
2. Obtain the expected SHA-256 or SHA-512 value through a trusted channel.
3. Run `beans-hash-check` with the expected value.
4. Use the file only if the result is `[PASS]`.
5. Recheck the filename and trusted source if the result is `[FAIL]`.

## Common Problems

- **File not found:** Confirm the path and quote paths containing spaces.
- **Could not infer the hash algorithm:** Check that the digest was copied completely without spaces or punctuation.
- **`[FAIL]` result:** Do not use the file until you determine why it differs.
- **Hash copied in uppercase:** Convert it to lowercase before using `beans-hash-check`.
