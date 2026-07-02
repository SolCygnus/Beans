# Whisper AI - Transcription

Whisper converts speech in audio or video files into text. Beans installs OpenAI Whisper in its own Python environment and provides the `beans-whisper` command. Beans uses NVIDIA GPU acceleration when it is available and falls back to the CPU when it is not.

> [!note]
> The first use of a model downloads its model files. Larger models require more disk space, memory, and processing time.

## Check That Whisper Is Available

```bash
beans-whisper --help
```

## Basic Transcription

Transcribe one file using Whisper's default model:

```bash
beans-whisper "interview.mp3"
```

Choose a model explicitly:

```bash
beans-whisper "interview.mp3" --model base
```

Transcribe multiple files:

```bash
beans-whisper "part-1.mp3" "part-2.wav" --model base
```

Whisper normally writes the results to the current directory. Common output files include plain text (`.txt`), subtitles (`.srt` and `.vtt`), and structured data (`.json` and `.tsv`).

## Useful Options

| Option | Purpose |
|---|---|
| `--model base` | Select the model to use |
| `--language English` | Specify the spoken language instead of detecting it |
| `--task transcribe` | Write speech in its original language |
| `--task translate` | Translate supported non-English speech into English |
| `--output_dir PATH` | Save results in a chosen directory |
| `--output_format txt` | Produce one output format instead of all formats |
| `--device cpu` | Force CPU processing |
| `--help` | Display every available option |

## Practical Examples

Save a plain-text transcript in a `transcripts` directory:

```bash
mkdir -p transcripts
beans-whisper "meeting.m4a" --model base --output_format txt --output_dir transcripts
```

Transcribe known English audio with an English-only model:

```bash
beans-whisper "lecture.mp3" --model base.en --language English
```

Create subtitles:

```bash
beans-whisper "video.mp4" --model base --output_format srt --output_dir transcripts
```

==Translate Spanish speech into English:==

```bash
beans-whisper "spanish-int.mp3" --model medium --language Spanish --task translate

beans-whisper japanese.wav --model medium --language Japanese --task translate
```

> [!warning]
> The `turbo` model is intended for fast transcription, not translation. Use a multilingual model such as `base`, `small`, `medium`, or `large` with `--task translate`.

## Choosing a Model

| Model | General Use |
|---|---|
| `tiny` / `tiny.en` | Fastest and least accurate |
| `base` / `base.en` | Good starting point for most computers |
| `small` / `small.en` | Better accuracy with more processing time |
| `medium` / `medium.en` | Higher accuracy with much greater resource use |
| `large` | Highest resource use among the standard models |
| `turbo` | Fast multilingual transcription |

Models ending in `.en` are English-only. CPU transcription can take considerably longer than GPU transcription, especially with larger models.

## Common Problems

- **Command not found:** Whisper may not have installed successfully. Review the Beans installation summary.
- **File not found:** Put quotes around paths containing spaces.
- **Out of memory:** Select a smaller model such as `tiny` or `base`.
- **Slow processing:** Use a smaller model or a working NVIDIA GPU configuration.
- **No transcript appears:** Check the current directory or the directory supplied with `--output_dir`.

## Reference

- [OpenAI Whisper documentation](https://github.com/openai/whisper)
