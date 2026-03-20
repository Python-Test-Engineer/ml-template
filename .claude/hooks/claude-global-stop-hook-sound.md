# Claude Code Stop Hook — Sound Notification

> *Last amended by Claude: 2026-03-20*

Plays a WAV file every time Claude finishes responding (the `Stop` event fires).

---

## How It Works

The hook is configured in `~/.claude/settings.json` under the `hooks.Stop` key:

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "powershell -c \"(New-Object Media.SoundPlayer 'C:\\Windows\\Media\\chimes.wav').PlaySync()\""
        }
      ]
    }
  ]
}
```

### What each part does

| Part | Purpose |
|------|---------|
| `"Stop"` | Hook event — fires when Claude finishes a response |
| `type: "command"` | Runs a shell command |
| `Media.SoundPlayer` | .NET class built into Windows — no extra tools needed |
| `PlaySync()` | Plays the file synchronously (waits for it to finish) |

---

## Changing the Sound

Open `~/.claude/settings.json` and replace the WAV path in the command.

### Windows system sounds

Located in `C:\Windows\Media\` — common options:

| File | Sound |
|------|-------|
| `chimes.wav` | Chimes (current) |
| `chord.wav` | Chord |
| `ding.wav` | Ding |
| `notify.wav` | Notification |
| `Windows Notify.wav` | Windows notification |
| `Windows Ding.wav` | Windows ding |

**Example** — switch to `ding.wav`:

```json
"command": "powershell -c \"(New-Object Media.SoundPlayer 'C:\\Windows\\Media\\ding.wav').PlaySync()\""
```

### Custom WAV file

Use any absolute path to a `.wav` file:

```json
"command": "powershell -c \"(New-Object Media.SoundPlayer 'C:\\Users\\mrcra\\sounds\\done.wav').PlaySync()\""
```

> **Note:** `Media.SoundPlayer` only supports uncompressed PCM `.wav` files. MP3 and other formats will not play.

---

## Disabling the Hook

Remove the `Stop` key from `hooks` in `~/.claude/settings.json`, or delete the entire `hooks` block if it's the only hook.

---

## Applying Changes

After editing `settings.json`, either:
- Open the `/hooks` menu in Claude Code (reloads config immediately), or
- Restart your Claude Code session
