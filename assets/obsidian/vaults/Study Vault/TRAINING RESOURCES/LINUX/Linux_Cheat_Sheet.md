# Linux Field Cheat Sheet

**OSR Linux Block | Chapman Challenge | Ashfall**

This is a working reference, not a list to memorize. Start with **Choose a command**, look up an example when you need one, and add your own notes as you solve problems. You can use your notes, the terminal help system, and your research skills.

> [!tip] When you're stuck
> 1. **Orient:** Where am I? Run `pwd` and `ls`.
> 2. **Identify:** Am I looking for a **file**, text **inside** a file, or something I need to **change**?
> 3. **Choose:** Find a command below. Check its help if necessary.
> 4. **Verify:** Read the output. Did it do what you expected?

## Choose a command

Use this section like the **right side of the old one-page cheat sheet**: scan for what you need to accomplish, then look below for examples.

| I need to...                                            | Command to consider                                                     |          |
| ------------------------------------------------------- | ----------------------------------------------------------------------- | -------- |
| Know **where I am** or **who I am**                     | `pwd` (location), `whoami` (user)                                       |          |
| See what's here or **change directories**               | `ls` (list), `cd` (move), `clear` (clear screen)                        |          |
| Recall a command or find **help**                       | `history`, `--help`, `man`, `whatis`, `↑`, `Ctrl+R`                     |          |
| Create or edit a file                                   | `touch` (empty file), `nano` (edit text), `echo` (output text)          |          |
| Organize files and folders                              | `mkdir` (create folder), `cp` (copy), `mv` (move/rename), `rm` (remove) |          |
| Read or inspect file contents                           | `cat`, `less`, `head`, `tail`, `file`, `wc`                             |          |
| **Find a file/folder** by its name                      | `find`                                                                  |          |
| **Search inside files** for text                        | `grep`                                                                  |          |
| Open a file with its regular app                        | `xdg-open`                                                              |          |
| Perform an administrative task                          | `sudo`, `apt`                                                           |          |
| **⭐ Chain commands**: control the next action           | `;` (run next), `&&` (run next only after success)                      |          |
| **⭐ Redirect output**: save what a command produces     | `>` (replace), `>>` (append)                                            |          |
| **⭐ Feed commands**: use one result in the next command |    \|                                                                   | ` (pipe) |

The **three stars** are worth understanding especially well. They work with many different commands.

---

## 1. Navigation: head, space, and timing

**A command runs from your current location unless you give it another path.** Keep checking where you are.

| Command | What it does |
|---|---|
| `pwd` | Print my current location (absolute path) |
| `ls` | List what's in the current directory |
| `ls -l` | Long listing (details about files and folders) |
| `ls -a` | Include hidden entries (names beginning with `.`) |
| `ls -lh` | Long listing with human-readable sizes |
| `cd Documents` | Move into `Documents` **from the current directory** |
| `cd ..` | Move up one directory |
| `cd` or `cd ~` | Return to my home directory |
| `cd /` | Move to the filesystem root |
| `clear` | Clear the terminal display (not the files or command history) |

**Paths in plain language**

- **Absolute:** starts at `/` and works from anywhere, e.g. `/home/boris/Documents`. Use your own username rather than copying `boris`.
- **Relative:** starts from **where you are now**, e.g. `Documents`, `../Downloads`, `./file.txt`.
- `~` means **your home directory**. `~/Documents` expands to a home-based absolute path.
- `.` means **here**; `..` means **parent directory**.
- Linux filenames are generally **case-sensitive**: `Documents` and `documents` are different names.
- Filenames **can contain spaces**, but you must quote or escape them: `cat "case notes.txt"`.

```bash
cd ~
pwd
ls
cd Documents
pwd
ls -la
cd ..
```

> [!note]- My notes: navigation and paths
> - A path I used today:
> - A command I want to remember:
> - A mistake I made and how I fixed it:

## 2. Help and command recall

| Try            | Use it for                                        |
| -------------- | ------------------------------------------------- |
| `history`      | See commands used in this shell                   |
| `↑` (up arrow) | Recall previous commands                          |
| `Ctrl+R`       | Search command history (press `Ctrl+C` to cancel) |
| `ls --help`    | See command syntax and options                    |
| `man ls`       | Open the manual (`q` to quit)                     |
| `whatis ls`    | Get a short description                           |

> [!tip] Help is part of the skill
> You do not need to memorize every option. Recognize the task, choose a likely command, and look up the details.

> [!note]- My notes: useful help or history tricks
> - What I looked up:
> - What I learned:

## 3. Create, read, and manage files

| Command | Main job | Example |
|---|---|---|
| `mkdir` | Make a directory | `mkdir CaseFiles` |
| `mkdir -p` | Make a directory and missing parents | `mkdir -p CaseFiles/Reports` |
| `touch` | Create an empty file (or update its timestamp) | `touch leads.txt` |
| `nano` | Create or edit text in an editor | `nano leads.txt` |
| `echo` | Print text to output | `echo "Lead confirmed"` |
| `cat` | Display or concatenate file contents | `cat leads.txt` |
| `cp` | Copy a file | `cp leads.txt leads_backup.txt` |
| `mv` | Move or rename | `mv leads_backup.txt old_leads.txt` |
| `rm` | Remove a file | `rm old_leads.txt` |

**Useful `nano` keys:** `Ctrl+O` saves, `Enter` confirms, and `Ctrl+X` exits.

> [!warning] Deletion and overwriting
> `rm` does not send files to a recycle bin. `rm -r` removes directories and their contents. Check your target **before** you run a destructive command. `>` can also overwrite a file (see the stars below).

> [!note]- My notes: file management
> - A command I used:
> - What changed in the filesystem:
> - An error and how I recovered:

## 4. Inspect files and search for information

### Look at a file

| Command | Main job |
|---|---|
| `file sample.jpg` | Identify the file's type from its contents (not merely its extension) |
| `less records.txt` | Read a large file a screen at a time (`q` to quit) |
| `head -n 5 records.txt` | Show the first 5 lines |
| `tail -n 5 records.txt` | Show the last 5 lines |
| `wc -l records.txt` | Count lines (newline characters) |
| `wc -w records.txt` | Count words |

### Find **names**: `find`

```bash
find ~/Documents -name 'leads.txt'
find ~/Documents -iname '*.csv'
find ~/Documents -type d
```

- `-name` matches names with case sensitivity.
- `-iname` ignores case; `*.csv` means names ending in `.csv`.
- `-type f` selects files; `-type d` selects directories.
- Quote patterns such as `'*.csv'` so the shell doesn't expand them before `find` sees them.

### Search **inside** files: `grep`

Build on the **same search** before adding another capability:

```bash
grep -i 'SJM' victory.csv        # Find matching lines, ignoring case
grep -in 'SJM' victory.csv       # Include line numbers
grep -iw 'SJM' victory.csv       # Match whole words
grep -ri 'Special Forces' ~/Documents/DATASETS  # Search through a directory
```

| Option | Meaning |
|---|---|
| `-i` | Ignore case |
| `-n` | Show line numbers |
| `-w` | Match whole words |
| `-r` | Search recursively through directories |
| `-o` | Show only matched text, not entire lines |

> [!tip] One important distinction
> `grep -i 'SJM' victory.csv | wc -l` counts **matching lines**. A line containing `SJM` twice still counts as one line. To count each matching occurrence, use `grep -io 'SJM' victory.csv | wc -l`.

> [!note]- My notes: `find` and `grep`
> - I needed to locate:
> - My working command:
> - Why that command worked:

## 5. ⭐ The three gold stars

These symbols change **how commands work together**. Practice with commands you already understand.

### ⭐ 1 — Chaining: `;` and `&&`

| Operator | Meaning | Example |
|---|---|---|
| `;` | Run the next command regardless of the first command's result | `pwd; ls` |
| `&&` | Run the next command **only if** the previous one succeeded | `cd ~/Documents && ls -l` |

**Think:** *Should the second command run even if the first fails?*

### ⭐ 2 — Redirecting: `>` and `>>`

| Operator | Meaning | Example |
|---|---|---|
| `>` | Send standard output to a file, **replacing** its contents | `echo "First lead" > leads.txt` |
| `>>` | Send standard output to a file, **appending** to it | `echo "Second lead" >> leads.txt` |

**Think:** *Where should this output go, and should I keep what was already there?*

### ⭐ 3 — Feeding: `|` (pipe)

The output of the command on the **left** becomes input for the command on the **right**.

```bash
grep -i 'SJM' victory.csv | wc -l
```

**Think:** *The first command finds something. What should the next command do with it?*

> [!important] The distinction
> - `;` / `&&` control **execution**.
> - `>` / `>>` send output **to a file**.
> - `|` sends output **to another command**.
>
> Redirects and pipes normally carry **standard output**. Error output is separate.

> [!note]- My notes: the three gold stars
> **Chaining**
> - Command I tried:
> - What happened:
>
> **Redirecting**
> - Command I tried:
> - What happened:
>
> **Feeding**
> - Command I tried:
> - What happened:

## 6. Administrative tools and extras

These are references for when your task calls for them. Use administrative privileges thoughtfully.

| Command | Purpose |
|---|---|
| `sudo command` | Run a permitted command with elevated privileges |
| `sudo !!` | In Bash, repeat the previous command with `sudo` (check it first) |
| `sudo apt update` | Refresh available package information |
| `sudo apt install tree` | Install a package (when authorized and online) |
| `chmod +x script.sh` | Add execute permission |
| `chmod 644 notes.txt` | Set owner read/write, group read, others read |
| `tree -d` | Show a directory tree (directories only) |
| `xdg-open image.jpg` | Open a file using its default desktop application |

> [!note]- My notes: administrative or optional commands
> - Command:
> - When I would use it:
> - A safety consideration:

---
