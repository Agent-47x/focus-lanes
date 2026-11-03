# Scheduling the daily build

The build is a plain Python script, so it can run without Claude.

## Windows — Task Scheduler

Create a basic task that runs daily at the time you want, with:

- **Program:** `py` (or the full path to `python.exe`)
- **Arguments:** `"C:\path\to\projects\00 Command Center\build_dashboard.py" "C:\path\to\projects" --tz Europe/London`

## macOS / Linux — cron

```
0 22 * * *  python3 "/path/to/projects/00 Command Center/build_dashboard.py" "/path/to/projects" --tz Europe/London
```

## Claude scheduled task (to also publish the page and get a notification)

If your Claude app offers scheduled tasks (Cowork does), create one that runs daily with a prompt such as:

> Run the daily brief for the Focus Lanes workspace at `<path>` using the focus-lanes
> `daily-brief` skill. The final message is the notification: Today's tasks, the Focus and Test progress, then the flags.

A task that works on files on your computer needs the computer to be on and the Claude app running at that time.
Pick an hour when your computer is usually on; if a run is missed, "run the daily brief" by hand gives the same result.
