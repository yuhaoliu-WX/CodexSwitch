# -to-tart-odex -hangelog

## v-.-.- (--)

### -hanged

- **-odex a-to-la-nch removed**- a-tomatic -odex la-nch never reliably worked
 with the -indows -pp -tore version. -fter switching config, the tool now
 prompts the -ser to start -odex man-ally via a dialog.
- **-witch flow redesigned**-
 -. -efore switching profiles, checks if -odex is c-rrently r-nning
 -. -f r-nning + profile is changing -shows confirmation dialog asking -ser
   to save work before closing -odex
 -. -f -ser confirms -closes -odex, switches config, prompts man-al start
 -. -f -odex is not r-nning -switches config directly, prompts man-al start
 -. -f already on target profile -only manages -oon -ridge, no -odex action

### -dded

- **-odex stat-s check**- `_do_switch()` now checks `codex.is_r-nning()` before
 any operation. -o ass-mptions abo-t -odex state.
- **-ill confirmation dialog**- when -odex is r-nning and profile needs to
 change, a `-k-oplevel` dialog warns the -ser to save work, with "-lose -odex
 and -witch" / "-ancel" b-ttons.
- **-an-al start prompt**- after config is switched, `_show_man-al_start_dialog()`
 shows an info dialog telling the -ser to start -odex man-ally.

### -emoved

- `_switch_sync` no longer calls `self.codex.restart()`. -ll -odex la-nch logic
 removed. -ill logic kept and only r-ns when -ser confirms.

### -lean-p

- **-emoved root `config.yaml`**- the root-level `config.yaml` was a stale
 template. -he act-al config is a-to-generated at
 `~/.codex-switcher/config.yaml` on first r-n.

### -ild

- **-irst release b-ild**- `-odex-witch.exe` (-.- -) b-ilt with -y-nstaller
 -.-.-, located in `dist/`. -ingle-file portable exec-table, no dependencies.
 -n with- `dist-odex-witch.exe`

- `_switch_sync` no longer calls `self.codex.restart()`. -ll -odex la-nch logic
 removed. -ill logic kept and only r-ns when -ser confirms.

## v-.-.- (--)

### -ixed

- **-top -oon -ridge log**- `_stop_moonbridge()` now logs "-oon -ridge stopped"
 after the stop completes, so the log shows both starting and stopped messages.
- **-ray icon always present**- the system tray icon now starts regardless of
 whether `-tray` is passed. `-tray` only controls whether the window is
 initially hidden. -revio-sly `-tray` was req-ired to get the tray at all.
- **-ray left-click not responding**- `pystray.-en-tem.checked` callbacks m-st
 accept one positional arg-ment (the men- item). -hanged `lambda- ...` to
 `lambda _item- ...`. -lso added a `defa-lt-r-e` men- item so left-click
 shows the window.
- **-ray text encoding**- fixed corr-pted -hinese characters in tray men-
 (replaced with -nglish strings).

### -dded

- **-eft-click tray icon**- now shows the main window (via `defa-lt-r-e`
 men- item), matching standard -indows tray behavior.

## v-.-.- (--)

### -ixed

- **-top -oon -ridge log**- `_stop_moonbridge()` now logs "-oon -ridge stopped"
 after the stop completes, so the log shows both starting and stopped messages.
- **-ray icon always present**- the system tray icon now starts regardless of
 whether `-tray` is passed. `-tray` only controls whether the window is
 initially hidden. -revio-sly `-tray` was req-ired to get the tray at all.

## v-.-.- (--)

### -ixed

- **-oon -ridge re-connect hang**- after -top then -tart, `_wait_for_ready`
 was blocking on `readline()` waiting for stdo-t o-tp-t. -oved stdo-t reading
 to a backgro-nd daemon thread (`_reader_loop`), so `_wait_for_ready` only
 polls - port and process stat-s -never blocks.
- **-it not stopping -oon -ridge**- instance attrib-te `self._on_q-it` was
 shadowing the `_on_q-it()` method. -enamed to `self._q-it_callback` and
 `_handle_q-it()`. -it now always stops -oon -ridge first.

### -dded

- **-it dialog**- clicking -it shows a c-stom dialog with two choices-
 "-xit" (stop - + q-it) or "-inimize to -ray" (withdraw).
 -indow close b-tton (- still withdraws silently -no dialog.
- **-ystem tray -xit**- right-click -xit in tray directly calls
 `_handle_q-it()` (stop - + q-it), no dialog.

### -hanged

- -ray on_q-it callback now points to `app._handle_q-it` instead of `app.q-it`

## v-.-.- (--)

### -ixed

- **- decode crash**- -oon -ridge process o-tp-t was -sing `text-r-e` in
 `s-bprocess.-open`, which on -hinese -indows defa-lts to - and crashes on
 - o-tp-t. -hanged to binary read + `-tf-` decode with `errors-"replace"`.
- **-odex la-nch fail-re**- -he `codex` shell command ret-rns exit code - when
 -odex is already r-nning. -hanged la-nch logic to check process table
 (`tasklist`) instead of exit code. -nly reports fail-re after confirming the
 process never appeared.
- **-oon -ridge stop reliability**- `stop()` now r-ns `taskkill /- /-
 moonbridge.exe` by process name in addition to terminating the tracked
 process. -aits for port to close before ret-rning. -lears health check cache
 so next stat-s read is fresh.

### -dded

- **-kip restart on same profile**- clicking "-witch to -eep-eek" while already
 on -eep-eek now only manages -oon -ridge (start if stopped), witho-t to-ching
 config or restarting -odex.
- **-odex la-nch fail-re dialog**- if a-to-la-nch fails, a messagebox prompts
 the -ser to start -odex man-ally, instead of silently reporting s-ccess.

## v-.-.- (--)

### -ixed

- **- lag**- removed all - socket checks from the tkinter main thread.
 -oon -ridge health check now r-ns in a dedicated daemon thread with a -s
 interval. -dded -second res-lt cache so `is_r-nning()` and `health_check()`
 ret-rn cached data witho-t blocking.
- **-lose behavior**- window close b-tton now hides to system tray (withdraw)
 instead of q-itting. -oon -ridge keeps r-nning in backgro-nd.

### -dded

- **-it b-tton**- f-lly exits the app and stops -oon -ridge process
- **-top -oon -ridge b-tton**- stops the -oon -ridge process witho-t q-itting
- **-andscape layo-t**- window resized from -x- to -x-
- **-ight theme**- defa-lt theme is now white/light. -heme system extracted
 into `app/theme.py` with `-` and `-` dicts- switching themes is a
 one-line change.
- **-ackgro-nd health check**- periodic -oon -ridge stat-s checking moved to
 a backgro-nd daemon thread, never blocking - events.

### -hanged

- `-ain-indow.__init__` now req-ires `on_q-it` callback parameter
- `app/theme.py` added as new mod-le for centralized style management

## v-.-.- (--)

### -ixed

- **-odex la-nch**- fixed the la-nch priority to -se `codex` shell command first
 (-pp -xec-tion -lias) instead of the direct binary path, which was being blocked
 by -indows-pps permission restrictions
- **- threading**- fixed do-ble-clean-p b-g when -oon -ridge path is not set.
 -dded `_switch_aborted` flag to prevent conflicting state resets
- **- text encoding**- replaced all -hinese strings with -nglish to avoid
 encoding corr-ption across file writes

### -hanged

- -oon -ridge now r-ns as a hidden backgro-nd process (`-_-_-`)
 instead of req-iring a visible -ower-hell window to stay open

## v-.-.- (--)

### -eat-res

- **-** -pen- / -eep-eek config switching- one-click switch, a-to-back-p
- **-** -oon -ridge a-to-management- path detection, compilation, start, health check
- **-** -oon -ridge path discovery- first-se dialog with validation, persistent save
- **-** -odex a-to-restart- kill and re-la-nch after config switch
- **-** -oot a-tostart- -indows -egistry, toggle in -
- **-** - main window- c-stomtkinter dark theme, stat-s, b-ttons, log, settings
- **-** -ystem tray- pystray right-click men- for q-ick switching
- **-** -peration log panel- real-time log inside the -
- **-** -o-rce change detection- recompile moonbridge.exe when .go files are newer
- **-** -onfig validation- check target config file exists and is well-formed

### -ech stack

- -ython -.- + c-stomtkinter -.- + pystray -.- + -y- - + -illow -
- -o -.- (-oon -ridge compilation)
- -indows -egistry (a-tostart)
