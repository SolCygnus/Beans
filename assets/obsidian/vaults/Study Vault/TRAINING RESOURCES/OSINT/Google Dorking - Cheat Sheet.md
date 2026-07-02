

Google Dorking (or Google Hacking) is a technique used to find sensitive information using advanced search queries. Below are some useful Google search operators to refine your searches.

## Basic Operators

| Operator    | Description                            | Example                         |
| ----------- | -------------------------------------- | ------------------------------- |
| `site:`     | Search within a specific site          | `site:example.com`              |
| `filetype:` | Search for specific file types         | `filetype:pdf site:example.com` |
| `intitle:`  | Search for words in the page title     | `intitle:"index of"`            |
| `inurl:`    | Search for words in the URL            | `inurl:admin`                   |
| `intext:`   | Search for words in the page content   | `intext:"password"`             |
| `related:`  | Find similar sites                     | `related:example.com`           |

## Advanced Dorking Techniques

### Finding Login Pages
```
inurl:login
intitle:"login" site:example.com
```

### Discovering Exposed Directories
```
intitle:"index of" "parent directory"
```

### Finding Exposed Databases
```
intext:"phpMyAdmin" "Welcome to phpMyAdmin"
inurl:phpmyadmin
```

### Searching for Sensitive Documents
```
filetype:xls intext:"username" | intext:"password"
filetype:pdf intext:"confidential"
```

## Combining Operators
You can combine multiple operators to refine your searches.
```
site:example.com filetype:pdf intext:"confidential"
inurl:admin intitle:login
```

## Warnings and Ethical Considerations
Google Dorking can expose sensitive information, but unauthorized access to data or systems is illegal and unethical. Always obtain permission before probing websites, and use this knowledge responsibly.

---

This cheat sheet is for educational and ethical cybersecurity research 