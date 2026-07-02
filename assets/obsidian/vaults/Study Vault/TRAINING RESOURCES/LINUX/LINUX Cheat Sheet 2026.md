

## Paths: Absolute vs Relative & Home (~)
- **Absolute Path**: Specifies the full path from the root (`/`) directory.
  - Example: `/home/user/Documents/file.txt`
- **Relative Path**: Specifies the path from the current directory.
  - Example: `cd ../../Documents/file.txt`
- **Home Shortcut (~)**: Represents the home directory of the user.
  - Example: `cd ~/Downloads`

## Navigating Directories
| Command                   | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `pwd`                     | Print current working directory                           |
| `whoami`                  | Show the current user                                     |
| `ls`                      | List directory contents                                   |
| `ls -l`                   | Long format listing                                       |
| `ls -a`                   | Show hidden files                                         |
| ls -alh                   | multiple options - list, long, all files, humand-readable |
| `ls /home/user/Documents` | show a specific folder                                    |
| `cd <dir>`                | Change directory to `<dir>`                               |
| `cd ..`                   | Move up one directory                                     |
| `cd -`                    | Switch to previous directory                              |
| ~ (tilda)                 | represents /home/user                                     |
| `cd ~` OR `cd`            | Go to home directory                                      |
| `cd ~/Desktop`            | shortcut to folder                                        |

## Getting Help
| Command                    | Description                         |
| -------------------------- | ----------------------------------- |
| `history`                  | Show command history                |
| `clear` OR ctrl + L        | clears the terminal screen          |
| Up Arrow                   | go back through history             |
| ctrl + R                   | reverse-search history              |
| echo                       | repeat input back to screen         |
| `whatis <command>`         | One-line description of `<command>` |
| `<command> --help` OR `-h` | Show command usage and options      |
| `man <command>`            | Show manual page for `<command>`    |
| `Google`                   | Search online for additional help   |

## Help ##
+ Terminal history is temporarily stored in RAM during terminal use. If not cleared, when session is closed will store to .bash_history file.

## Administrative Commands
| Command                                | Description                                                                                                          |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `sudo <command>`                       | Run `<command>` as superuser                                                                                         |
| sudo !!                                | run previous command with sudo                                                                                       |
| `apt install <package_name>`           | Install a package                                                                                                    |
| `apt update`                           | Refresh package list                                                                                                 |
| `apt upgrade`                          | Upgrade installed packages                                                                                           |
| sudo apt update && sudo apt upgrade -y | update and upgrade the system                                                                                        |
| `sudo shutdown`                        | shutdown VM from command line. Adding `now` at the end will immediately do so without graceful process terminations. |
| sudo reboot                            | reboot VM from command line                                                                                          |


## ==Chaining Commands==

| **`<command> ; <command>`** | ==Run multiple commands sequentially==        |
| --------------------------- | --------------------------------------------- |
| `<command> && <command>`    | ==Run second command only if first succeeds== |

## Managing Files
| Command                       | Description                                            |
| ----------------------------- | ------------------------------------------------------ |
| `nano <file>`                 | Open `<file>` in nano editor                           |
| `touch <file>`                | Create an empty file                                   |
| `cat <file>`                  | Show file contents                                     |
| `cat -n <file>`               | Show file contents and line numbers                    |
| `tac <file>`                  | Show file contents in reverse                          |
| `echo "text" > <file>`        | Write text to a file (overwrite)                       |
| `echo "text" >> <file>`       | Append text to a file                                  |
| `mkdir <dir>`                 | Create a directory                                     |
| `mkdir -p <dir/dir>`          | Create parent directories if they do not exist already |
| `rm <file>`                   | Remove a file                                          |
| `rm -rf <dir>`                | Remove a directory recursively                         |
| `cp <sourc> <destination>`    | Copy file                                              |
| `cp -r <sourc> <destination>` | Copy directory and its contents                        |
| `cp -i <sourc> <destination>` | interactive copy - will ensure you do not overwrite    |
| `mv <file>`                   | move files and directories                             |

+ If creating a file with nano - you will need to save it and exit. Your toolbar for options is at the bottom of the terminal where ^ = Ctrl Key. So Ctrl + X will exit the file and ask if you would like to save changes.
+ when operating within the nano program: Alt-Shift-3 will turn on line numbers


## File Content Operations
| Command                       | Description                                                                                                |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `file <file>`                 | Identify file type by looking at file header information. Does not care about file extensions              |
| `wc <file>`                   | Count words, lines, characters                                                                             |
| `less <file>`                 | View file contents with navigation                                                                         |
| `head -n <num> <file>`        | Display first 10 lines of file or specified number with -n option <br>(`head <file>` OR `head -n5 <file>`) |
| `tail -n <num> <file>`        | Display last 10 lines of file or specified number with -n option<br>(`tail <file>` OR `tail -n5 <file>`)   |
| `find <path> -name "pattern"` | Search for files by name                                                                                   |

## ==Redirection==

| `>`  | ==Used for output redirection. A single `>` overwrites specified destination==  |
| ---- | ------------------------------------------------------------------------------- |
| `>>` | ==Used for output redirection. A double `>>` appends to specified destination== |
|      | `echo this is a test > test.txt`                                                |
|      | `cat <file> >> text.txt`                                                        |

## ==Pipes==

| \|                                           | ==Use to combine two or more commands with output from first command being used for input of next command== |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `cat [filename]`                             | wc -l`: cats file and feeds into word count                                                                 |
| cat [filename] \| grep -i "victory" \| wc -w |                                                                                                             |

## Advanced Commands
| Command                             | Description                                                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `grep "pattern" <file>`             | Global regular expression print (grep) - Search files for given pattern or word and see lines containing it |
| `grep -i "search term" [filename]`  | ignore case                                                                                                 |
|                                     | `-w`: whole words                                                                                           |
|                                     | `-o`: only prints the matching parts of a line                                                              |
|                                     | `-E`: extended regex                                                                                        |
| `grep -r "search term" ~/Documents` | `-r`: recursive through a directory                                                                         |
|                                     | `-c`: count of lines found per filename                                                                     |
|                                     | `-n`: print lines containing keywords                                                                       |
|                                     |                                                                                                             |


## Extras
| Command              | Description                          |
| -------------------- | ------------------------------------ |
| `tree`               | Show directory tree structure        |
| `xdg-open <file>`    | Open file with default application   |
| `alias ll='ls -lah'` | Create temporary alias for `ls -lah` |
| `terminator`         | Launch Terminator terminal emulator  |
+ you can make permanent alias associations by editing the alias section of your .bashrc file in your home folder.


## Terminator Command Line Interface (CLI)

+ enhanced command line interface with more options than built-in
+ sudo apt install terminator

| Command        | Description                          |
| -------------- | ------------------------------------ |
| `Ctrl-Shirt-E` | Split the view vertically            |
| `Ctrl-Shift-O` | Split the view horizontally.         |
| `Ctrl-Shift-W` | Close the view where the focus is on |
| `Ctrl-Shift-Q` | Exit Terminator                      |
| `Ctrl-Alt-W`   | Edit window title                    |


## File Permissions
cdcd
- `chmod`: change modification command 
  - `chmod +x [filename]`: add executable function
  - `chmod -x [filename]`: remove executable function
  - `chmod 777 [filename]`: change to read, write, execute for user, group, and others
  - `sudo chown -R $USER: [filename]`: change owner of specified file


## Other

- `2>/dev/null`: Device on Linux systems considered a vacuum/blackhole where standard error output can be directed to de-clutter a command's use
  - `find / -name [filename] 2>/dev/null`
- `xargs`: Extended Argument deals with STDIN STDOUT issues. commonly seen in piped commands
  - `find -iname '*.log' | xargs rm`: remove all files that end in .log

## Linux File Structure

- `/`: The main or “root” directory contains the following directories/folders:
  - `/bin`: binary files used by the system
  - `/boot`: bootloader, kernel and other files needed for booting
  - `/dev`: device files
  - `/etc`: configuration files
  - `/home`: user home directories
  - `/lib`: shared libraries
  - `/media`: directory for external device mounts
  - `/mnt`: old directory for external device mounts
  - `/opt`: optional software
  - `/proc`: virtual directory used by the kernel for process management.
  - `/root`: root user’s home directory
  - `/sbin`: shared binary files
  - `/sys`: virtual directory used by kernel for data structures
  - `/tmp`: temporary directory
  - `/usr`: read-only user-specific files and binaries
  - `/var`: variable files, including logs and printer spool


## Create Shared Folder 
+ Virtual Box System Settings - Shared Folder:
	+ Folder Path: Select Path to Folder on your Host Machine
	+ Folder Name: I prefer to keep it the same as name on Host
	+ Mount Point: /mnt/<Folder_Name>
	+ Select Auto-mount
+ On the Virtual Machine Command line:
	+ Create a symbolic link to the folder on your desktop (create a shortcut)
		+ `ln -s /mnt/<Folder_Name> ~/Desktop`
	+ Add the current user to the `vboxsf` group
		+ `sudo usermod -aG vboxsf <your_username>`
	+ reboot OR run `newgrp vboxsf`
